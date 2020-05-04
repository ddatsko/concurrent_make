import os
import re


class CommandRunner:
    def __init__(self, root_dir: str = '/'):
        self.root_dir = root_dir

    def run_commands(self, commands_file: str, abs_paths_root: str) -> (str, int):
        """
        :return the name of created file (target)
        """
        cur_dir = os.getcwd()
        res = []
        try:
            os.chdir(self.root_dir)

            # Considering that all the paths were substitute for the absolute ones
            lines = [re.sub(r'\s/', f' {abs_paths_root}', line) for line in open(commands_file).readlines()]
            for command in lines:
                print(command)
                command_out = os.popen(command)
                command_res = command_out.read()
                exit_code = command_out.close()
                res.append(command_res)
                if exit_code:
                    return '\n'.join(res), command_res[1]
        except Exception as e:
            print(e)
            pass
        finally:
            os.chdir(cur_dir)
        return '\n'.join(res), 0
