from typing import List
from errors import ParseError
import os
import re
import config
from runner import CommandRunner
import subprocess as sp


class BuildTarget:
    dependencies_targets: List['BuildTarget']

    def __init__(self, target_files: List[str], dependencies_files: list = None,
                 bash_commands: list = None, ready: bool = False, up_to_date: bool = False):
        self.target_files = target_files.copy()
        self.dependencies_files_only = dependencies_files.copy() if dependencies_files else []
        self.all_dependency_files = self.dependencies_files_only.copy()
        self.bash_commands = bash_commands.copy() if bash_commands else []
        self.initial_bash_commands = bash_commands.copy() if bash_commands else []
        self.ready = ready
        self.up_to_date = False
        self.dependencies_targets = []
        self.root = True
        self.local_only = False

    def __repr__(self):
        return f"(Targets: {', '.join(self.target_files)}, file dependencies: {self.dependencies_files_only}, target_depedencies: " \
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
        if len(root) > 0 and root[-1] == '/':
            root = root[:-1]

        replaces = {file: root + os.path.abspath(file) for file in self.all_dependency_files + self.target_files}
        self.dependencies_files_only = [replaces[file] for file in self.dependencies_files_only]
        self.target_files = [replaces[file] for file in self.target_files]
        self.all_dependency_files = [replaces[file] for file in self.all_dependency_files]

        new_bash_commands = []
        for command in self.bash_commands:
            updated_command = f' {command} '  # simple way to make all the words be surrounded by spaces
            for file in replaces:
                updated_command = re.sub(rf'\s{file}\s', f' {replaces[file]} ', updated_command)
            new_bash_commands.append(updated_command)
        self.bash_commands = new_bash_commands

    def replace_special_vars(self):
        replaces = {
            r'\$@': self.target_files[0],
            r'\$\*': os.path.splitext(self.target_files[0])[0].split('.')[0],
            r'\$\<': self.all_dependency_files[0] if self.all_dependency_files else '',
            r'\$\^': ' '.join(set(self.all_dependency_files)),
            r'\$\+': ' '.join(self.all_dependency_files),
            r'\$\(@D\)': os.path.dirname(self.target_files[0]),
            r'\$\(@F\)': self.target_files[0].split('/')[-1].split('.')[0]
        }
        for i in range(len(self.bash_commands)):
            for replace in replaces:
                self.bash_commands[i] = re.sub(fr'{replace}', replaces[replace], self.bash_commands[i])
        self.initial_bash_commands = self.bash_commands.copy()

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

    async def replace_in_commands(self, pattern: str, value: str):
        self.bash_commands = list(map(lambda x: f' {x} ', self.bash_commands))  # Wrap each command into spaces
        for i in range(len(self.bash_commands)):
            self.bash_commands[i] = re.sub(rf'\s{pattern}\s', f' {value} ', self.bash_commands[i])

    async def process_dependencies(self, parser):
        self.dependencies_targets = []
        self.dependencies_files_only = []
        for dependency in self.all_dependency_files:
            if target_dep := parser.get_target_by_filename(dependency):
                self.dependencies_targets.append(target_dep)
            else:
                self.dependencies_files_only.append(dependency)

    async def _replace_var_in_list(self, files_list: list, parser):
        updated_list = []
        for file in files_list:
            if match := re.match(r"\$[{(](.*?)[})]", file):
                # Take variable, calculate expression and add all the files to dependency files
                updated_list.append(parser.calculate_expression(file))
            else:
                updated_list.append(file)
        files_list.clear()
        files_list.extend(updated_list)

    async def replace_all_variables(self, parser):
        await self._replace_var_in_list(self.all_dependency_files, parser)
        await self.process_dependencies(parser)
        for i in range(len(self.bash_commands)):
            self.bash_commands[i] = parser.calculate_expression(self.bash_commands[i])
        self.initial_bash_commands = self.bash_commands.copy()

    async def get_libraries_dependencies(self):
        if not config.CHECK_MORE_DEPENDENCIES:
            return
        dependencies_libraries = {file for file in self.dependencies_files_only if file.endswith('.so') or '.so.' in file}
        added = len(dependencies_libraries) != 0
        while added:
            new_dependencies = set()
            added = False
            for library in dependencies_libraries:
                library_dir = os.path.dirname(library)
                library_filename = library.split('/')[-1]

                # check symlinks
                try:
                    result = CommandRunner(os.getcwd()).run_one_command(f'ls {library_dir} -la | grep {library_filename}')
                    if '->' in result:
                        lib = result.split(' -> ')[1].strip()
                        if not lib.startswith('/'):
                            lib = library_dir + '/' + result.split(' -> ')[1].strip()
                        if lib not in dependencies_libraries:
                            new_dependencies.add(lib)
                            added = True
                except:
                    pass

                try:
                    result = CommandRunner(os.getcwd()).run_one_command(f'ldd {library}')
                    for line in result.splitlines():
                        if match := re.match(r'.*\s(/.+?)\s', line):
                            if match.groups('0')[0] not in dependencies_libraries:
                                new_dependencies.add(match.groups('0')[0])
                                added = True
                except:
                    pass
            for library in new_dependencies:
                dependencies_libraries.add(library)
        self.dependencies_files_only = list(set(self.dependencies_files_only).union(dependencies_libraries))
        self.all_dependency_files = list(set(self.all_dependency_files).union(dependencies_libraries))
