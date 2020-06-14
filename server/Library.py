from typing import Iterable, Dict, Set, List
import os
import re
from errors import InvalidLibraryFileName


class Library:
    def __init__(self, path_to_file: str):
        if '.so.' in path_to_file.split('/')[-1] or path_to_file.endswith('.so'):
            ext = '.so'
        elif '.a.' in path_to_file.split('/')[-1] or path_to_file.endswith('.a'):
            ext = '.a'
        else:
            raise InvalidLibraryFileName(f"File {path_to_file} seems to be not a library")
        match = re.match(rf".*?/?([^/]+{ext})(.*)", path_to_file)
        if not match:
            raise InvalidLibraryFileName(f"Errors while parsing {path_to_file}")
        self.name = match.groups('0')[0]

        try:
            version_numbers = match.groups('0')[1].strip('.').split('.')
            if version_numbers[0]:
                self.version = tuple(map(int, version_numbers))
            else:
                self.version = (0,)
        except Exception as e:
            self.version = (0,)
        self.abs_path = os.path.abspath(path_to_file)

    def __ge__(self, other: 'Library'):
        if self.name != other.name:
            return False
        if len(self.version) > len(other.version):
            version2 = list(other.version) + [0] * (len(self.version) - len(other.version))
            version1 = list(self.version)
        else:
            version1 = list(self.version) + [0] * (len(other.version) - len(self.version))
            version2 = list(other.version)
        for i in range(len(version1)):
            if version1[i] < version2[i]:
                return False
        return True

    def __repr__(self):
        return f"Library(name={self.name}, path={self.abs_path}, version={'.'.join(map(str, self.version))})\n"

    @staticmethod
    def find_library_in_list(library_name: str, libraries: List['Library'], exact_versions: bool) -> 'Library' or None:
        looked_library = Library(library_name)
        for library in libraries:
            if (not exact_versions and library >= looked_library) or library == looked_library:
                return library
