import os
import re


class CommandRunner:
    def __init__(self, root_dir: str = '/'):
        self.root_dir = root_dir

    def run_commands(self, commands_file: str, abs_paths_root: str) -> str:
        """
        :return the name of created file (target)
        """
        cur_dir = os.getcwd()
        res = []
        try:
            os.chdir(self.root_dir)

            # Considering that all the paths were substitute for the absolute ones
            lines = [re.sub(r'\s/', f' {abs_paths_root}', line) for line in open(commands_file).readlines()]
            input()
            for command in lines:
                print(command)
                res.append(os.popen(command).read())
        finally:
            os.chdir(cur_dir)
        return '\n'.join(res)
