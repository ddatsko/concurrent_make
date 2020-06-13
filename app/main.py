from parser import Parser
from compressor import Compressor
from requests_manager import RequestsManager
import asyncio
import subprocess as sp
from errors import ExecutionError
import os.path

file = 'concurrent_makefile'
hosts_file = os.path.join(os.path.dirname(__file__), 'hosts')


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
    rm = await RequestsManager.create(p.default_target, hosts_file, Compressor(), p)
    try:
        await rm.build_targets()
    except ExecutionError as e:
        print(e.commands_output, e.message)


if __name__ == "__main__":
    asyncio.run(main())
