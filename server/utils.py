from hashlib import sha256
from typing import List
from Library import Library
import subprocess as sp


def is_password_acceptable(password: str) -> bool:
    password = bytes(password, encoding='utf-8')
    hashed_password = sha256(password).hexdigest()
    return hashed_password in [line.strip() for line in open('allowed_passwords').readlines()]


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

