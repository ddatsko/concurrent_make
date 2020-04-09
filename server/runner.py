import os


class CommandRunner:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def run_commands(self, commands_file: str) -> str:
        """
        :return the name of created file (target)
        """
        cur_dir = os.getcwd()
        try:
            os.chdir(self.root_dir)
            os.system(f'chmod +x {commands_file}')
            os.system(f'./{commands_file}')
        finally:
            os.chdir(cur_dir)
        output_filename = commands_file[:-10]
        if os.path.exists(output_filename):
            return output_filename
