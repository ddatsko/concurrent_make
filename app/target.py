from typing import List
from errors import ParseError
import os
import re


class BuildTarget:
    dependencies_targets: List['BuildTarget'];

    def __init__(self, target_files: List[str], dependencies_files: list = None,
                 bash_commands: list = None, ready: bool = False, up_to_date: bool = False):
        self.target_files = target_files.copy()
        self.dependencies_files = dependencies_files.copy() if dependencies_files else []
        self.bash_commands = bash_commands.copy() if bash_commands else []
        self.ready = ready
        self.up_to_date = False
        self.dependencies_targets = []
        self.root = True
        self.local_only = False

    def __repr__(self):
        return f"(Targets: {', '.join(self.target_files)}, file dependencies: {self.dependencies_files}, target_depedencies: " \
               f"{[''.join(t.target_files) for t in self.dependencies_targets]} commands: {self.bash_commands})\n"

    @staticmethod
    def get_modification_time(filename: str) -> int or float:
        if os.path.exists(filename):
            return os.path.getmtime(filename)
        else:
            return float("inf")

    def targets_exist(self) -> bool:
        for file in self.target_files:
            if not os.path.exists(file):
                return False
        return True

    def get_latest_modification_time(self):
        modification_time = 0
        for file in self.target_files:
            modification_time = max(modification_time, BuildTarget.get_modification_time(file))
        return modification_time

    def substitute_for_absolute_paths(self, root: str):
        if root[-1] == '/':
            root = root[:-1]

        replaces = {file: root + os.path.abspath(file) for file in self.dependencies_files + self.target_files}
        self.dependencies_files = [replaces[file] for file in self.dependencies_files]
        self.target_files = [replaces[file] for file in self.target_files]

        new_bash_commands = []
        for command in self.bash_commands:
            updated_command = ' ' + command + ' '  # simple way to make all the words be surrounded by spaces
            for file in replaces:
                updated_command = re.sub(rf'\s{file}\s', replaces[file], updated_command)
            new_bash_commands.append(updated_command)
        self.bash_commands = new_bash_commands

    @staticmethod
    def build_targets_dependencies(targets: List['BuildTarget']):
        # Modifies the input data, be careful
        target_by_name = {file: target for target in targets for file in target.target_files}
        if len(target_by_name) != len(targets):
            raise ParseError("Error! Two targets have the same name...")
        for target in targets:
            dependencies_files = []
            for dependency in target.dependencies_files:
                if dependency in target_by_name:
                    target.dependencies_targets.append(target_by_name[dependency])
                else:
                    dependencies_files.append(dependency)
            target.dependencies_files = dependencies_files

    @staticmethod
    def target_by_filename(name: str, targets: List['BuildTarget']) -> 'BuildTarget' or None:
        for target in targets:
            for file in target.target_files:
                if file == name:
                    return target
        return None

    async def create_commands_file(self, filename):
        with open(filename, 'w') as f:
            f.write('\n'.join(self.bash_commands))
