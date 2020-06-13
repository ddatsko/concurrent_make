from hashlib import sha256
from typing import List
from Library import Library
from runner import CommandRunner
import os
import subprocess as sp


def check_password(password: str):
    pass


def find_libraries() -> List[Library]:
    res = []
    # There may be some errors and exit code not 0, but output in stdout will be correct
    check_result = sp.Popen('ldconfig -v', stdout=sp.PIPE, stderr=open('/dev/null', 'w'), shell=True)
    ld_output = check_result.communicate()[0].decode('utf-8')
    current_prefix = ''
    for line in ld_output.splitlines():
        if line.startswith('\t'):
            res.append(Library(current_prefix + line.split(' -> ')[1]))
        else:
            current_prefix = line.strip().strip(':') + '/'
    return res

