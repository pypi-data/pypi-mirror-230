__author__ = 'Andrey Komissarov'
__date__ = '2022'


class RemoteCommandExecutionError(Exception):
    """RemoteCommandExecutionError"""

    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        return f'During handling remote command execution error occurred!\n\t{self.error}'


class LocalCommandExecutionError(Exception):
    """LocalCommandExecutionError"""

    def __init__(self, error: str = None):
        self.error = error

    def __str__(self):
        return f'During handling local command execution error occurred!\n\t{self.error}'
