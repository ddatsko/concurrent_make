import os
import subprocess as sp
from errors import ExecutionError


class CommandRunner:
    def __init__(self, root_dir):
        self.root_dir = root_dir + ('/' if not root_dir.endswith('/') else '')

    def run_one_command(self, command: str) -> str:
        cur_dir = os.getcwd()
        try:
            os.chdir(self.root_dir)
            check_result = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
            output = check_result.communicate()[0].decode('utf-8')
            if check_result.returncode != 0:
                print("Command seems to be wrong")
                raise ExecutionError(f'Command: {command}', f"STDOUT: {check_result.communicate()[0].decode('utf-8')}\n"
                                                            f"STDERR: {check_result.communicate()[1].decode('utf-8')}")
            return output
        finally:
            os.chdir(cur_dir)
