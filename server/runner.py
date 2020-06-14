import os
import re
import subprocess as sp
from Library import Library
from typing import List


class CommandRunner:
    def __init__(self, root_dir: str, present_libraries: List[Library]):
        self.root_dir = root_dir
        self.present_libraries = present_libraries

    def run_commands(self, commands_file: str, abs_paths_root: str, logger) -> (str, int):
        """
        :return the name of created file (target)
        """
        cur_dir = os.getcwd()
        res = []
        try:
            logger.debug("HERE")
            os.chdir(self.root_dir)

            # Considering that all the paths were substitute for the absolute ones
            lines = [re.sub(r'\s/', f' {abs_paths_root}', line) for line in open(commands_file).readlines()]
            logger.debug("Lines Before: " + '\n'.join(lines))
            for i in range(len(lines)):
                for library in re.findall(r'\${(.*?)}', lines[i]):
                    lines[i] = re.sub(r'\${' + library + '}',
                                      Library.find_library_in_list(library, self.present_libraries).abs_path, lines[i])

            logger.debug("Lines After: " + '\n'.join(lines))
            for command in lines:
                r = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
                out, err = r.communicate()
                output = f"Command: {command}" + f"\nSTDOUT: {out.decode('utf-8')}\n" + \
                         f"STDERR: {err.decode('utf-8')}"

                print(output)
                res.append(output)
                if r.returncode != 0:
                    return '\n'.join(res), r.returncode
        except Exception as e:
            logger.debug(e)
            return '\n'.join(res), -1
        finally:
            os.chdir(cur_dir)
        return '\n'.join(res), 0

    @staticmethod
    def run_one_command(command: str):
        check_result = sp.Popen(command, stdout=sp.PIPE, shell=True)
        output = check_result.communicate()[0].decode('utf-8')
        if check_result.returncode != 0:
            print("Command seems to be wrong")
            print(str(output))
            return ''
        return output
