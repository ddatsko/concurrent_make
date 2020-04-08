from typing import List


class BuildTarget:
    target_file = None
    dependencies_files = []
    dependencies_targets = None
    bash_commands = []
    ready = False
    up_to_date = False

    def __init__(self, target_file: str = None, dependencies_files=None,
                 bash_commands=None, ready: bool = False, up_to_date: bool = False):
        self.target_file = target_file
        self.dependencies_files = dependencies_files if dependencies_files else []
        self.bash_commands = bash_commands if bash_commands else []
        self.ready = ready
        self.up_to_date = up_to_date
        self.dependencies_targets = []

    def __repr__(self):
        return f"(Target: {self.target_file}, file dependencies: {self.dependencies_files}, target_depedencies: " \
               f"{[t.target_file for t in self.dependencies_targets]} commands: {self.bash_commands})\n"

    @staticmethod
    def build_targets_dependencies(targets: List['BuildTarget']):
        # Modifies the input data, be careful
        target_by_name = {target.target_file: target for target in targets}
        for target in targets:
            for dependency in target.dependencies_files:
                if dependency in target_by_name:
                    target.dependencies_files.remove(dependency)
                    target.dependencies_targets.append(target_by_name[dependency])
