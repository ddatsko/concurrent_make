import re
from target import BuildTarget
import os


class Parser:
    available_functions = [""]

    def __init__(self, lines: list):
        self.lines = list(lines)
        self.variables = self.extract_variables()
        self.targets = []
        self.default_target = None

    def get_default_target(self):
        return self.default_target if self.default_target else self.targets[0]

    def set_default_target(self, target_name: str):
        for target in self.targets:
            if target_name in target.target_files:
                self.default_target = target

    def replace_all_variables(self):
        for i in range(len(self.lines)):
            for variable in self.variables:
                self.lines[i] = re.sub(r"^\s*\$[{(]" + variable + r"[})]:",
                                       f'{self.calculate_expression(self.variables[variable])}:',
                                       self.lines[i])
                self.lines[i] = re.sub(r"\$[{(]" + variable + r"[})]", self.variables[variable], self.lines[i])

    def get_target_by_filename(self, name: str) -> BuildTarget or None:
        for target in self.targets:
            for file in target.target_files:
                if file == name:
                    return target
        return None

    def normalize_text(self):
        self.lines = [re.sub(r"\\(.)", r'\g<1>', line) for line in self.lines]

    def extract_variables(self):
        variables = {}
        for line in self.lines:
            if line.startswith("\t"):
                continue
            match = re.match(r"^\s*([\w_][0-9A-Za-z_]*)\s+([?+:]?)=\s+(.*)$", line)
            if not match:
                continue
            var_name, assign_type, value = match.groups('0')
            if assign_type == '':
                # simple assignment with =
                variables[var_name] = value
            elif assign_type == ':':
                # in place
                variables[var_name] = self.calculate_expression(value)
            elif assign_type == '+':
                # add as simple
                if var_name in variables:
                    variables[var_name] += value
                else:
                    variables[var_name] = value
            elif assign_type == '?':
                # assign only if does not exist
                if var_name not in variables:
                    variables[var_name] = value

        return variables

    def calculate_expression(self, expression: str):
        # ${var:a=b}’) - replace each entry at the end of each word from a to b

        # replace all the variables with their values
        while values := re.findall(r"\$[{(](.*?)[})]", expression):
            if not any(map(lambda x: x in self.variables, values)):
                break
            for value in values:
                if value in self.variables:
                    expression = re.sub(r"\$[{(]" + str(value) + r"[})]", self.variables[value], expression)
        return expression

    def get_build_targets(self):
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
                new_target = BuildTarget(target_files=list(match.groups('0')[0].split()))
                new_target.dependencies_files_only = match.groups('0')[1].split()
                new_target.all_dependency_files.extend(new_target.dependencies_files_only)
                targets.append(new_target)
                bash_command = True
            elif len(targets) > 0 and bash_command and line.startswith('\t'):
                targets[-1].bash_commands.append(line.strip())
            else:
                bash_command = False
            current_line += 1

        if self.default_target is None:
            self.default_target = targets[0]
        self.targets = targets

    @staticmethod
    def is_valid_line(line: str) -> bool:
        return line.strip() and (not re.match(r'\s*#.*', line))

    @staticmethod
    def check_file_with_make(filename: str) -> (bool, str):
        make_out = os.popen("make")
        output = make_out.read()
        exit_code = make_out.close()
        if exit_code != 0:
            return False, output
        return True, output
