from typing import Iterable, Dict, Set
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
            self.version = tuple(map(int, match.groups('0')[1].strip('.').split('.')))
        except:
            self.version = (0,)
        self.abs_path = os.path.abspath(path_to_file)

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other: 'Library'):
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


def find_libraries(directories: Iterable[str]) -> Set[Library]:
    res = set()
    for path in directories:
        if not path.endswith('/'):
            path += '/'
        if not os.path.isdir(path):
            continue
        for file in os.listdir(path):
            try:
                library = Library(path + file)
                res.add(library)
            except InvalidLibraryFileName:
                continue
    return res
