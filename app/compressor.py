from typing import Iterable
import tarfile
import os


class Compressor:
    def __init__(self, root_path: str):
        self.root_path = root_path if root_path.endswith('/') else root_path + '/'

    def compress(self, files: Iterable[str], output_file_name: str):
        cur_dir = os.getcwd()
        try:
            os.chdir(self.root_path)
            with tarfile.open(output_file_name, 'w:xz') as archive:
                for file in files:
                    archive.add(file)
        finally:
            os.chdir(cur_dir)
