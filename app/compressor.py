from typing import Iterable
import tarfile
import os
import tempfile


class Compressor:
    def __init__(self, root_path: str = '.'):
        self.root_path = root_path if root_path.endswith('/') else root_path + '/'

    def compress(self, files: Iterable[str], output_file_name: str):
        print(f"Compressing files {files}")
        if not output_file_name.endswith('tar.xz'):
            output_file_name += '.tar.xz'
        cur_dir = os.getcwd()
        try:
            os.chdir(self.root_path)
            with tarfile.open(output_file_name, 'w:xz') as archive:
                for file in files:
                    archive.add(file)
        finally:
            os.chdir(cur_dir)

    @staticmethod
    async def extract_files(buffer: bytes):
        tmp_archive = tempfile.NamedTemporaryFile(suffix='tar.xz', prefix=os.getcwd())
        archive_name = tmp_archive.name
        with open(archive_name, 'wb') as file:
            file.write(buffer)

        with tarfile.open(archive_name, 'r:xz') as file:
            file.extractall(f"/")
        tmp_archive.close()
