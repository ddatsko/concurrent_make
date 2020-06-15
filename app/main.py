from parser import Parser
from compressor import Compressor
from requests_manager import RequestsManager
import asyncio
import subprocess as sp
from errors import ExecutionError
import os.path
import config
import argparse

parser = argparse.ArgumentParser(description='Concurrent makefile v1.0')
parser.add_argument('--file', default='', dest='file', help='File with configuration (similar to Makefile)')
parser.add_argument('--hosts', default='', dest='hosts', help='File with hosts for building')
parser.add_argument('--max-timeout', type=float, default=None, dest='timeout', help='Maximum waiting time (in seconds)'
                                                                                    'for host to build a target')
parser.add_argument('-j', default=1, type=int, dest='cores', help='Max numbre of processes on local computer')


hosts_file = os.path.join(os.path.dirname(__file__), config.HOSTS_FILE)


async def main():
    # Check the file with GNU make
    check_result = sp.Popen(f'make -n -f {config.MAKEFILE}', stderr=sp.PIPE, shell=True)
    output = check_result.communicate()[1]
    if check_result.returncode != 0:
        print("File seems to be of bad format")
        print(str(output))
        exit(1)

    lines = open(config.MAKEFILE, 'r').readlines()
    p = Parser(lines)
    p.replace_all_variables()
    p.get_build_targets()
    rm = await RequestsManager.create(p.default_target, hosts_file, Compressor(), p)
    try:
        await rm.build_targets()
    except ExecutionError as e:
        print(e.commands_output, e.message)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.file:
        config.MAKEFILE = args.file
    if args.hosts:
        hosts_file = args.hosts
    if args.timeout:
        config.RECEIVE_TIMEOUT = args.timeout
    if args.cores:
        config.MAX_LOCAL_PROCESSES = args.cores
    asyncio.run(main())
