from host import Host
import aiohttp
from target import BuildTarget
import asyncio
from compressor import Compressor
from runner import CommandRunner
import os


class HostLocal(Host):
    def __init__(self):
        super().__init__('', '')

    async def is_available(self) -> bool:
        return True

    async def get_compiled_file(self, session: aiohttp.ClientSession, target: BuildTarget, lock: asyncio.Lock,
                                compressor: Compressor):
        print(f"Building the target locally...")
        for command in target.initial_bash_commands:
            CommandRunner(os.getcwd()).run_one_command(command)

    def __repr__(self):
        return 'Local host'

    def __eq__(self, other: 'Host'):
        return self.address == other.address

