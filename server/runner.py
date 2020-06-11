import os
import re
import sys
import subprocess as sp


class CommandRunner:
    def __init__(self, root_dir: str, present_libraries: dict):
        self.root_dir = root_dir
        self.present_libraries = present_libraries

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
            for i in range(len(lines)):
                # TODO: reqrite this for thanging with regex
                # NOTE!!: THIS IS HARDCODED AS I HAVENT ENOUGH TIME
                lines[i] = re.sub(r'\${.*}', '/usr/local/lib/libboost_thread.so.1.72.0', lines[i])

            for command in lines:
                r = sp.Popen(command, shell=True, stderr=sp.PIPE)
                sys.stderr.write(str(r.communicate()[1]))

                sys.stderr.write(command)
                command_out = os.popen(command)
                command_res = command_out.read()
                exit_code = command_out.close()
                res.append(command_res)
                if exit_code:
                    return '\n'.join(res), exit_code
        except Exception as e:
            print(e)
            pass
        finally:
            os.chdir(cur_dir)
        return '\n'.join(res), 0
