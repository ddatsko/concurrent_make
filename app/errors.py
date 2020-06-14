class ParseError(Exception):
    pass


class ExecutionError(Exception):
    def __init__(self, message: str, commands_output: str):
        self.message = message
        self.commands_output = commands_output

    def __repr__(self):
        return "Error in running command in remote host. OUTPUT: " + self.commands_output

    def __str__(self):
        return self.__repr__()


class ConnectionError(Exception):
    pass


class InvalidLibraryFileName(Exception):
    pass
