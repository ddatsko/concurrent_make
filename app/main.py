from parser import Parser
from target import BuildTarget
from compressor import Compressor
import os
from requests_manager import RequestsManager
import asyncio
import aiohttp

file = 'concurrent_makefile'
hosts_file = 'hosts'


def main():
    lines = open(file, 'r').readlines()
    p = Parser(lines)
    p.parse()
    targets = p.get_build_targets()
    locally = BuildTarget.target_by_filename('LOCALLY', targets)
    if locally:
        for target in locally.dependencies_targets:
            target.local_only = True
        targets.remove(locally)
    targets_order = BuildTarget.get_build_order(targets)
    print(targets_order)

    rm = RequestsManager(targets_order, 'hosts', Compressor())
    asyncio.run(rm.build_targets())


if __name__ == "__main__":
    main()
