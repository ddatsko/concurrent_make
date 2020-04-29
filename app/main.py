from parser import Parser
from target import BuildTarget
from compressor import Compressor
import os
from requests_manager import RequestsManager
import asyncio
import aiohttp

file = 'concurrent_makefile'
hosts_file = 'hosts'


async def main():
    lines = open(file, 'r').readlines()
    p = Parser(lines)
    p.parse()
    targets = p.get_build_targets()

    rm = RequestsManager(p.default_target, hosts_file, Compressor())
    await rm.build_targets()


if __name__ == "__main__":
    asyncio.run(main())
