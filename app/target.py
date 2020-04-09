from typing import List
from errors import ParseError
import os


class BuildTarget:
    def __init__(self, target_file: str = None, dependencies_files: list = None,
                 bash_commands: list = None, ready: bool = False, up_to_date: bool = False):
        self.target_file = target_file
        self.dependencies_files = dependencies_files.copy() if dependencies_files else []
        self.bash_commands = bash_commands.copy() if bash_commands else []
        self.ready = ready
        self.up_to_date = False
        self.dependencies_targets = []
        self.root = True
        self.local_only = False

    def __repr__(self):
        return f"(Target: {self.target_file}, file dependencies: {self.dependencies_files}, target_depedencies: " \
               f"{[t.target_file for t in self.dependencies_targets]} commands: {self.bash_commands})\n"

    @staticmethod
    def build_targets_dependencies(targets: List['BuildTarget']):
        # Modifies the input data, be careful
        target_by_name = {target.target_file: target for target in targets}
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
    def get_build_order(targets: List['BuildTarget']) -> List['BuildTarget']:
        targets_order = []

        # Mark root elements
        for build_target in targets:
            for target_dep in build_target.dependencies_targets:
                target_dep.root = False

        # Iterate through targets and find out which should be re-compiled
        def dfs(target: 'BuildTarget'):
            newest_time = 0
            up_to_date = True
            target_file_time = os.path.getmtime(target.target_file) if os.path.exists(target.target_file) else 0
            os.path.exists(target.target_file)
            for file in target.dependencies_files:
                if not os.path.exists(file):
                    raise ParseError(f"Error! The file {file} does not exist but is in dependencies "
                                     f"of a target {target.target_file}")
                if os.path.getmtime(file) > target_file_time:
                    up_to_date = False

            for dep_target in target.dependencies_targets:
                dfs(dep_target)
                if os.path.exists(dep_target.target_file):
                    newest_time = max(newest_time, os.path.getmtime(dep_target.target_file))
                else:
                    newest_time = float('inf')
                up_to_date &= dep_target.up_to_date
            if up_to_date and os.path.exists(target.target_file) and newest_time < os.path.getmtime(target.target_file):
                target.ready = True
                target.up_to_date = True
            else:
                targets_order.append(target)

        for build_target in targets:
            if build_target.root:
                dfs(build_target)
        return targets_order

    @staticmethod
    def target_by_filename(name: str, targets: List['BuildTarget']) -> 'BuildTarget' or None:
        for target in targets:
            if target.target_file == name:
                return target
        return None

    def create_commands_file(self, filename):
        with open(filename, 'w') as f:
            f.write('\n'.join(self.bash_commands))

    def build_archive(self, compressor, filename=''):
        if not filename:
            filename = self.target_file
        files_to_compress = [target.target_file for target in self.dependencies_targets] + [file for file in
                                                                                            self.dependencies_files]
        commands_filename = self.target_file.split('/')[-1] + '.sh'
        self.create_commands_file(commands_filename)

        compressor.compress(files_to_compress + [commands_filename], filename)
