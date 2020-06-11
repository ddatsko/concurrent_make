from parser import Parser
from compressor import Compressor
from requests_manager import RequestsManager
import asyncio
import subprocess as sp

file = 'concurrent_makefile'
hosts_file = 'hosts'


async def main():
    # Check the file with GNU make
    check_result = sp.Popen(f'make -n -f {file}', stderr=sp.PIPE, shell=True)
    output = check_result.communicate()[1]
    if check_result.returncode != 0:
        print("File seems to be of bad format")
        print(str(output))
        exit(1)
        
    lines = open(file, 'r').readlines()
    p = Parser(lines)
    p.replace_all_variables()
    p.get_build_targets()

    rm = RequestsManager(p.default_target, hosts_file, Compressor(), p)
    await rm.build_targets()


if __name__ == "__main__":
    asyncio.run(main())
