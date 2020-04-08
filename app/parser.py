import re
from target import BuildTarget
from typing import List


class Parser:
    def __init__(self, lines: list):
        self.lines = list(lines)
        self.variables = self.extract_variables()

    def parse(self):
        self.replace_variables()

    def extract_variables(self):
        variables = {}
        for line in self.lines:
            match = re.match(r"^\s*([\w_][0-9A-Za-z_]*)\s+=\s+(.*)$", line)
            if match:
                variables[match.groups('0')[0]] = match.groups('0')[1]
        return variables

    def replace_variables(self):
        for i in range(len(self.lines)):
            for variable in self.variables:
                self.lines[i] = re.sub(fr'\$\({variable}\)', self.variables[variable], self.lines[i])

    def get_build_targets(self) -> List[BuildTarget]:
        targets = []
        current_line = 0
        bash_command = False
        while current_line < len(self.lines):
            line = self.lines[current_line]
            if not Parser.is_valid_line(line):
                current_line += 1
                continue
            match = re.match(r"\s*(.*):\s*(.*)\s*", line)
            if match:
                new_target = BuildTarget(target_file=match.groups('0')[0])
                new_target.dependencies_files = match.groups('0')[1].split()
                targets.append(new_target)
                bash_command = True
            elif len(targets) > 0  and bash_command and line.startswith('\t'):
                targets[-1].bash_commands.append(line.strip())
            else:
                bash_command = False
            current_line += 1
        BuildTarget.build_targets_dependencies(targets)
        return targets

    @staticmethod
    def is_valid_line(line: str) -> bool:
        return line.strip() and (not re.match(r'\s*#.*', line))
