[![PyPI version](https://badge.fury.io/py/plinux.svg)](https://badge.fury.io/py/plinux)
[![Python application](https://github.com/c-pher/plinux/actions/workflows/pythonapp.yml/badge.svg?branch=master)](https://github.com/c-pher/plinux/actions/workflows/pythonapp.yml)

# Plinux

Cross-platform tool to work with remote Linux OS.

Plinux based on paramiko project. It can establish ssh connection to a remote server, execute command as user or with sudo rights. Plinux returns object with exit code, sent command, stdout/sdtderr response.

## Installation
For most users, the recommended method to install is via pip:
```cmd
pip install plinux
```
## Import
```python
from plinux import Plinux
```
---
## Usage
#### The most recommended usage way:
```python
from plinux import Plinux

client = Plinux(host="172.16.0.124", username="bobby", password="qawsedrf")
response = client.run_cmd("hostname")
print(response.stdout)  # WebServer
print(response.ok)  # True
```
```python
from plinux import Plinux

client = Plinux()
response = client.run_cmd_local("hostname")
print(response.stdout)  # WebServer
print(response.ok)  # True
```

#### Command using sudo:
```python
from plinux import Plinux

client = Plinux(host="172.16.0.124", username="bobby", password="qawsedrf", logger_enabled=True)
response = client.run_cmd("systemctl stop myservicename.service", sudo=True)

print(response)  # SSHResponse(response=(0, None, None, "sudo -S -p '' -- sh -c 'systemctl stop myservicename.service'"))
print(response.command)  # sudo -S -p '' -- sh -c 'systemctl stop myservicename.service'
print(response.exited)  # 0
```

#### SFTP usage:
```python
from plinux import Plinux

tool = Plinux(host="ftp.test.local", username="bobby", password="qawsedrf")
sftp = tool.sftp
print(sftp.listdir())
```

#### SQLite3 usage:
```python
from plinux import Plinux

client = Plinux(host="cdn1.test.local", username="bobby", password="qawsedrf")

db_path = '/opt/ProductName/rxdb/StorageConfig.db'
sql = 'select Data from DtoDataContainer'
db = client.sqlite3(db_path, sql).json()
print(db)  # {"Settings1": 1, "Settings2": 2...,"Settings10": 10}
print(db['Setting1'])  # {"Settings1": 1}
```

#### Aliases

Some methods have "human commands" and aliases:

* client.run_cmd("cat /home/bobby/text")
* client.cat("/home/bobby/text")
