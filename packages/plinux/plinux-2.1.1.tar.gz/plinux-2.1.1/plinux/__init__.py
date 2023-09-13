import configparser
import datetime
import io
import json
import os
import re
import shlex
import socket
import subprocess
import time
from json import JSONDecodeError

import plogger
from paramiko import SSHClient, ssh_exception, AutoAddPolicy
from paramiko.sftp_client import SFTPClient

from plinux.exceptions import RemoteCommandExecutionError


class SSHResponse:
    """Response parser"""

    def __init__(self,
                 out, err, exited: int, command: str = None,
                 logger_enabled: bool = True, log_level: str | int = 'DEBUG'):
        self.__out = out
        self.__err = err
        self.__exited = exited
        self.command = command
        self.logger = plogger.logger('SSHResponse', enabled=logger_enabled, level=log_level)

    def __str__(self):
        return json.dumps(self._dict, indent=4)

    @property
    def stdout(self):
        """STDOUT

        Can be:
            - None
            - str
            - dict
            - list
        """

        out = self.__out
        if not out:
            self.logger.debug('Empty file. String will be returned.')
            return out

        # Try to convert into Dict
        try:
            out = json.loads(out)
            self.logger.debug('JSON file detected. Dict will be returned.')
            return out
        except JSONDecodeError:
            pass

        self.logger.debug('Common file detected. File content wil be returned.')
        return out

    @property
    def stderr(self) -> None | str:
        return self.__err if self.__err else None

    @property
    def exited(self) -> int:
        """Get exit code"""
        return self.__exited

    @property
    def ok(self) -> bool:
        return self.exited == 0

    @property
    def _dict(self):
        """Get raw response from WinRM and return result dict"""

        result = {
            'exit_code': self.exited,
            'ok': self.ok,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'cmd': self.command,
        }

        return result


class Plinux:
    """Base class to work with linux OS"""

    def __init__(self,
                 host: str = '127.0.0.1',
                 username: str = None,
                 password: str = None,
                 port: int = 22,
                 logger_enabled: bool = True,
                 log_level: str | int = 'INFO'):
        """Create a client object to work with linux host"""

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.log_enabled = logger_enabled
        self.log_level = log_level
        self.logger = plogger.logger('Plinux', enabled=self.log_enabled, level=self.log_level)

    def __str__(self):
        str_msg = (f'==========================\n'
                   f'Remote IP: {self.host}\n'
                   f'Username: {self.username}\n'
                   f'Password: {self.password}\n'
                   f'Host available: {self.is_host_available()}\n'
                   f'==========================')
        return str_msg

    def is_host_available(self, port: int = 0, timeout: int = 5):
        """Check remote host is available using specified port"""

        port_ = port or self.port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((self.host, port_))
            return False if result else True

    def list_all_methods(self):
        """Returns all available public methods"""

        return [method for method in dir(self) if not method.startswith('_')]

    def run_cmd_local(self, cmd: str, timeout: int = 60):
        """Main function to send commands using subprocess

        :param cmd: string, command
        :param timeout: timeout for command
        :return: Decoded response

        """

        try:
            self.logger.info(f'COMMAND: "{cmd}"')
            cmd_divided = shlex.split(cmd)
            result = subprocess.run(cmd_divided, capture_output=True, timeout=timeout)

            out = result.stdout.decode().strip()
            err = result.stderr.decode().strip()

            response_cfg = {
                'out': out,
                'err': err,
                'exited': result.returncode,
                'command': cmd,
                'logger_enabled': self.log_enabled,
                'log_level': self.log_level,
            }
            return SSHResponse(**response_cfg)
        except subprocess.TimeoutExpired as err:
            self.logger.exception('Connection timeout')
            raise err

    def run_cmd_local_native(self, *popenargs,
                             stdin_input=None,
                             capture_output: bool = False,
                             timeout: int = 60,
                             check: bool = False,
                             **kwargs):
        """It's just native subprocess' .run invocation.

        The returned instance will have attributes args, returncode, stdout and
        stderr. By default, stdout and stderr are not captured, and those attributes
        will be None. Pass stdout=PIPE and/or stderr=PIPE in order to capture them.

        If check is True and the exit code was non-zero, it raises a
        CalledProcessError. The CalledProcessError object will have the return code
        in the returncode attribute, and output & stderr attributes if those streams
        were captured.

        If timeout is given, and the process takes too long, a TimeoutExpired
        exception will be raised.

        There is an optional argument "stdin_input", allowing you to
        pass bytes or a string to the subprocess's stdin.  If you use this argument
        you may not also use the Popen constructor's "stdin" argument, as
        it will be used internally.

        By default, all communication is in bytes, and therefore any "stdin_input" should
        be bytes, and the stdout and stderr will be bytes. If in text mode, any
        "stdin_input" should be a string, and stdout and stderr will be strings decoded
        according to locale encoding, or by "encoding" if set. Text mode is
        triggered by setting any of text, encoding, errors or universal_newlines.

        The other arguments are the same as for the Popen constructor.

        :param popenargs:
        :param stdin_input:
        :param capture_output:
        :param timeout:
        :param check:
        :param kwargs:
        :return:
        """

        cmd = shlex.split(*popenargs)
        cmd_to_log = ' '.join(cmd)
        self.logger.info(f'{self.host:<14} | {cmd_to_log}')

        result = subprocess.run(cmd, input=stdin_input, capture_output=capture_output, timeout=timeout, check=check,
                                **kwargs)

        self.logger.info(f'{self.host:<14} | {result.returncode}:\n\t{result}')
        return result

    def _client(self, sftp: bool = False, connect_timeout: int = 15) -> SFTPClient | SSHClient:
        """Create SSHClient or SFTPClient instance

        https://www.paramiko.org/

        Authentication will be validated.

        :param sftp: Is this sFTP client?
        :param connect_timeout: 15 sec. Timeout (in seconds) for the TCP connect.
        :return:
        """

        client = SSHClient()
        policy = AutoAddPolicy()
        client.set_missing_host_key_policy(policy)

        try:
            client.connect(self.host, username=self.username, password=self.password, timeout=connect_timeout)

            if sftp:
                return client.open_sftp()
            return client
        except ssh_exception.AuthenticationException as err:
            msg = f'{self.host:<14}| Invalid credentials: {self.username}@{self.password}:\n{err}.'
            self.logger.exception(msg)
            raise err
        except ssh_exception.NoValidConnectionsError as err:
            msg = f'{self.host:<14}| There is no valid connection. Try to use "_local" or vice versa method.'
            self.logger.exception(msg)
            raise err
        except TimeoutError as err:
            self.logger.exception(f'{self.host:<14}| Timeout exceeded.')
            raise err
        except Exception as err:
            self.logger.exception(f'{self.host:<14}| Something went wrong:\n{err}.')
            raise err

    # noinspection GrazieInspection
    def run_cmd(self,
                cmd: str,
                sudo: bool = False,
                exec_timeout: int = None,
                connect_timeout: int = 15,
                ignore_errors: bool = False) -> SSHResponse:
        """Base method to execute SSH command on remote server

        Exit codes: https://tldp.org/LDP/abs/html/exitcodes.html

        :param cmd: SSH command
        :param sudo: Execute specified command as sudo user
        :param exec_timeout: Execution timeout. Unlimited by default
        :param connect_timeout: Timeout (in seconds) for the TCP connect.
        :param ignore_errors: Ignore errors
        :return: SSHResponse class
        """

        data_to_log = locals()
        params_msg = f'Parameters:\n{self._dict_to_log(data_to_log)}'
        self.logger.debug(params_msg)

        client = self._client(connect_timeout=connect_timeout)

        try:
            command = f"sudo -S -p '' -- sh -c '{cmd}'" if sudo else cmd
            self.logger.info(f'{self.host:<14} | {command}')

            stdin, out, err = client.exec_command(command, timeout=exec_timeout)

            if sudo:
                stdin.write(self.password + '\n')
                stdin.flush()

            # recv_exit_status - socket blocking operation. To add command timeout we use exit_status_ready
            if exec_timeout is not None:
                timer = 0
                while exit_status_ready := not out.channel.exit_status_ready():
                    self.logger.debug(f'{not exit_status_ready = }')
                    time.sleep(1)

                    timer += 1
                    if timer > exec_timeout:
                        error_msg = f'The command ({command}) was not completed within {exec_timeout} seconds.'
                        self.logger.error(error_msg)
                        raise TimeoutError(error_msg)

            exited = out.channel.recv_exit_status()
            out_ = out.read().decode()  # .strip()
            err_ = err.read().decode()  # .strip()

            response_cfg = {
                'out': out_,
                'err': err_,
                'exited': exited,
                'command': cmd,
                'logger_enabled': self.log_enabled,
                'log_level': self.log_level,
            }
            parsed = SSHResponse(**response_cfg)

            # Log ERROR / Exit code != 0 (operation is failed)
            def_log = f'{self.host:<14} | {parsed.exited}:'
            err_to_log = f'{def_log} STDERR:\n\t{parsed.stderr}' if parsed.stderr else def_log

            if parsed.exited:
                self.logger.error(err_to_log)

                if not ignore_errors:  # Exit code != 0 and ignore_errors=True
                    raise RemoteCommandExecutionError(parsed.stderr)

            # Log INFO / Exit code == 0 (operation is success)
            else:
                # Log WARNING
                if parsed.stderr:  # Exit code != 0 and stderr contains message
                    self.logger.warning(err_to_log)

                out_to_log = parsed.stdout
                match out_to_log:
                    case dict():
                        out_to_log = json.dumps(out_to_log, indent=4)
                    case configparser.ConfigParser():
                        out_to_log = configparser.ConfigParser
                    case _:
                        pass

                msg_to_log = f'{parsed.exited}:\n\t{out_to_log}' if out_to_log else f'{parsed.exited}:'
                self.logger.info(f'{self.host:<14} | {msg_to_log}')

            return parsed
        finally:
            client.close()

    def sqlite3(self, db: str, sql: str, sudo: bool = False, params: str = '', timeout: int = 1000):
        """Simple work with the SQLite.

        - sqlite3 -cmd ".timeout {timeout}" {db} "{sql}" {params}

        :param db: DB path
        :param sql: SQL request
        :param params: i.e. "-line -header", "-csv"
        :param sudo:
        :param timeout: ms. 1000 by default
        """

        cmd = f'sqlite3 -cmd ".timeout {timeout}" {db} "{sql}" {params}'
        result = self.run_cmd(cmd, sudo=sudo)
        return result

    def is_credentials_valid(self) -> bool:
        """Verify credentials using "whoami" request """

        try:
            self.run_cmd('whoami')
            return True
        except ssh_exception.AuthenticationException:
            self.logger.exception(f'Invalid credentials ({self.username, self.password})')
            return False

    def exists(self, path: str, sudo: bool = False) -> bool:
        r"""Check file and directory exists.

        For windows path: specify network path in row format or use escape symbol.
        You must be connected to the remote host.

        Usage::

            exists('\\\\172.16.0.25\\d$\\New Text Document.txt')

        For linux path: linux style path.

        Usage::

            exists('/home/user/test.txt')

        :param path: Full path to file/directory
        :param sudo:
        :return:
        """

        self.logger.info(f'-> Verify entity ({path}) existence')

        # Linux
        if '/' in path:
            cmd = f'test -e {path}'
            response = self.run_cmd(cmd, sudo=sudo, ignore_errors=True)
            result = response.ok
            self.logger.info(f'<- {result}')
            return result
        # Windows
        elif '\\' in path:
            return os.path.exists(path)
        raise SyntaxError('Incorrect method usage. Check specified path.')

    def cat(self, path: str, sudo: bool = False) -> str | dict:
        """Get file content

        :param path: /opt/test/file.conf
        :param sudo: Use sudo rights
        :return:
        """

        cmd = f'cat {path}'
        result = self.run_cmd(cmd, sudo=sudo)

        return result.stdout

    def cat_ini(self, path: str, sudo: bool = False, raw: bool = False) -> str | configparser.ConfigParser:
        """Get ini file and return ConfigParser

        :param path: /etc/pip.conf
        :param sudo: True / False
        :param raw: Return raw config. Environment vars will be skipped
        :return:
        """

        self.logger.info(f'Reading file ({path}) as ini-config. Parser: {raw = }')

        content = self.cat(path, sudo=sudo)
        if not content:
            return content

        buffer = io.StringIO(content)
        config = configparser.RawConfigParser() if raw else configparser.ConfigParser()
        config.read_file(buffer)

        self.logger.info('Completed')
        return config

    def stat_file(self, path: str, sudo: bool = False) -> dict:
        """Get file information

        Parameters used::

            - %a access rights in octal
            - %A access rights in human-readable form
            - %g group ID of owner
            - %G group name of owner
            - %u user ID of owner
            - %U username of owner
            - %F file type
            - %i inode number
            - %s total size, in bytes
            - %m mount point
            - %w time of file birth, human-readable; - if unknown
            - %X time of last access, seconds since Epoch
            - %Y time of last data modification, seconds since Epoch
            - %Z time of last status change, seconds since Epoch
            - executable: True if there are 3 "x" in access right. Otherwise, False

        Response::

            {
              'access_rights': 775,
              'access_rights_human': '-rwxrwxr-x',
              'executable': True,
              'group': 1000,
              'group_human': 'objectfirst',
              'user': 1000,
              'user_human': 'objectfirst',
              'file_type': 'regular file',
              'inode': 927734,
              'size': 13325572,
              'mount_point': '/',
              'time_birth': '-',
              'datetime_last_access': datetime.datetime(2021,  11,10,11,27,29),
              'datetime_data_modification': datetime.datetime(2021,11,1,17,59,55),
              'datetime_status_modification': datetime.datetime(2021,11,1,18,0,26)
            }

        :param path: File path. /home/username/just_file
        :param sudo: Use sudo
        :returns: dict
        """

        params = ('access_rights:%a|'
                  'access_rights_human:%A|'
                  'group:%g|'
                  'group_human:%G|'
                  'user:%u|'
                  'user_human:%U|'
                  'file_type:%F|'
                  'inode:%i|'
                  'size:%s|'
                  'mount_point:%m|'
                  'time_birth:%w|'
                  'datetime_last_access:%X|'
                  'datetime_data_modification:%Y|'
                  'datetime_status_modification:%Z'
                  )

        cmd = f'stat -c "{params}" {path}'
        result = self.run_cmd(cmd, sudo=sudo)
        res_dict = {}

        for i in result.stdout.split('|'):
            k, v = i.split(':', maxsplit=1)

            if k == 'access_rights_human':  # Check executable or not
                count_x = v.count('x')
                res_dict[k] = v
                res_dict['executable'] = True if count_x == 3 else False

            elif 'datetime' in k:
                epoch_time = int(v)
                date_time = datetime.datetime.fromtimestamp(epoch_time)
                res_dict[k] = date_time
            else:
                try:
                    res_dict[k] = int(v)
                except ValueError:
                    res_dict[k] = v

        return res_dict

    def grep(self, path: str, string: str, directory: bool = False, sudo: bool = True):
        """Grep line in file or directory

        :param sudo:
        :param path: File/directory path
        :param string: string pattern to grep
        :param directory: If True - grep in directory with files
        :return:
        """

        self.logger.info(f'-> Grep line in file or directory')

        cmd = f'grep -rn "{string}" {path}' if directory else f'grep -n "{string}" {path}'

        result = self.run_cmd(cmd, sudo=sudo, ignore_errors=True)

        match result.exited:
            case 0:
                self.logger.info(f'<- Pattern "{string}" found in {path}')
            case 1:
                self.logger.info(f'<- Pattern "{string}" not found')
            case _:
                self.logger.error(f'<- {result.stderr}')
                raise RemoteCommandExecutionError

        return result

    @property
    def sftp(self):
        return self._client(sftp=True)

    def upload(self, local: str, remote: str):
        r"""Upload file/dir to the host and check exists after.

        Usage::

            tool.upload(r'd:\python_tutorial.pdf', '/home/user/python_tutorial.pdf'')

        :param local: Source full path
        :param remote: Destination full path
        :return: bool
        """

        self.sftp.put(local, remote, confirm=True)
        self.logger.info(f'Uploaded {local} to {remote}')
        return self.exists(remote)

    def download(self, remote: str, local: str, callback=None) -> bool:
        r"""Download a file from the current connection to the local filesystem and check exists after.

        Usage::

            tool.download("/home/user/python_tutorial.pdf", "d:\dust\python_tutorial.pdf")

        :param remote: Remote file to download. May be absolute, or relative to the remote working directory.
        :param local: Local path to store downloaded file in, or a file-like object
        :param callback: func(int, int)). Accepts the bytes transferred so far and the total bytes to be transferred
        :return: bool
        """

        self.sftp.get(remote, local, callback=callback)
        self.logger.info(f'Downloaded {remote} to {local}')
        return self.exists(local)

    def get_ip_addresses_show(self, name: str = None) -> dict:
        """Show IP addresses info.

        - ip --json addr show

        Note:
            - If name is specified, return only info about this interface.
            - If name is not specified, return all interfaces info.

        :param name: Interface name. Returns for specific iface info if used. For example: ens160, enp0s10f0
        :return:
        """

        cmd = 'ip --json addr show'
        result = self.run_cmd(cmd).stdout

        result_dict = {iface.get('ifname'): iface for iface in result}

        for key, value in result_dict.items():
            # Set IP address as keys in addr_info dict
            addr_info_dict = {addr['local']: addr for addr in value['addr_info']}
            result_dict[key]['addr_info'] = addr_info_dict
            result_dict[key]['ipv4_addresses'] = [k for k, v in addr_info_dict.items() if v['family'] == 'inet']
            result_dict[key]['ipv6_addresses'] = [k for k, v in addr_info_dict.items() if v['family'] == 'inet6']

        result_dict['entities_quantity'] = len(result)

        return result_dict if name is None else result_dict[name]

    def get_ntp_servers(self) -> list:
        """Get NTP servers list

        - grep "NTP" /etc/systemd/timesyncd.conf | grep -v "#"

        :return: List of NTP servers. {'172.16.0.1', '192.168.12.1'}
        """

        cmd = 'grep "NTP" /etc/systemd/timesyncd.conf | grep -v "#"'
        response = self.run_cmd(cmd).stdout
        values = re.findall(r'NTP=(.+)', response)  # ['172.16.0.3 ntp.com'] or ['172.16.0.3', '172.16.0.4']

        if len(values) > 1:
            # NTP=172.16.0.3
            # FallbackNTP=172.16.0.4
            return values

        # For NTP=172.16.0.3 ntp.com
        try:
            return values[0].split()
        except IndexError:
            return []

    @staticmethod
    def _dict_to_log(data: dict | list, sort: bool = False, ensure_ascii: bool = False) -> str:
        """Pretty dict data to log"""

        def convert_data_to_log(obj):
            """Convert datetime, IPv4Address, requests Response...

            :param obj: Object to convert
            :return:
            """

            match obj:
                case Plinux():
                    return obj.__repr__()

        json_data = json.dumps(data, sort_keys=sort, ensure_ascii=ensure_ascii, indent=4, default=convert_data_to_log)

        return json_data


def to_known_type(value: str):
    """Convert string data into known Python's data types.

    - date/time => datetime.datetime
    - "yes"/"no"/"true"/"false" => True/False
    - "none", "empty", ""  => True/False
    - "123"  => int
    - "000000"  => "000000"

    :param value:
    :return:
    """

    from dateutil import parser
    from dateutil.parser import ParserError

    try:
        value_lower = value.lower()
    except AttributeError:
        value_lower = value

    try:
        return int(value_lower)
    except (TypeError, ValueError):
        ...

    if value_lower in ('yes', 'true'):
        return True
    if value_lower in ('no', 'false'):
        return False
    if value_lower in ('none', 'empty', ''):
        return None
    if value_lower.startswith('00'):
        return value

    try:
        return parser.parse(value)
    except ParserError:
        ...

    return value
