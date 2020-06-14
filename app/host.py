from errors import ConnectionError, ExecutionError
from compressor import Compressor
from runner import CommandRunner
from target import BuildTarget
from Library import Library
from typing import List
import tempfile
import aiohttp
import asyncio
import config
import json
import os


class Host:
    OK_ANSWER = 'OK'
    FAIL_ANSWER = 'NOT OK'
    CHECK_ENDPOINT = '/api/v1/check'
    INFO_ENDPOINT = '/api/v1/get_info'
    BUILD_ENDPOINT = '/api/v1/build'
    ALL_LIBRARIES_ENDPOINT = '/api/v1/all_libraries'

    def __init__(self, address: str, password: str):
        self.address = address.strip('/')
        self.password = password
        self.architecture = ''
        self.libraries: List[Library] or None = None

    async def is_available(self) -> bool:
        headers = {'content-type': 'application/json'}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            try:
                response = await session.post(self.address + self.CHECK_ENDPOINT,
                                              data=json.dumps({'password': self.password}).encode('utf-8'),
                                              headers=headers)
                if (await response.text()) != self.OK_ANSWER:
                    print(f"Seems that you specified wrong password for host {self.address}")
                    return False
                if self.architecture == '':
                    await self.get_server_info()
                    this_computer_architecture = CommandRunner('/').run_one_command('uname -m').strip()
                    if this_computer_architecture != self.architecture:
                        print(
                            f"Host {self.address} has architecture {self.architecture}, which is not te same as yours ({this_computer_architecture})")
                        return False
                return True
            except Exception as e:
                print(e)
                print(f"Seems that host {self.address} was unable to reach")
                return False

    async def get_server_info(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            try:
                response = await session.post(self.address + self.INFO_ENDPOINT,
                                              data=json.dumps({'password': self.password}).encode('utf-8'))
                data = await response.json()
                self.architecture = data['architecture']

            except Exception as e:
                print(e)
                raise ConnectionError()

    async def get_archive(self, data: aiohttp.FormData, session: aiohttp.ClientSession) -> bytes:
        try:
            resp = await asyncio.wait_for(session.post(url=self.address + self.BUILD_ENDPOINT, data=data),
                                          timeout=config.RECEIVE_TIMEOUT)
        except Exception:
            raise ConnectionError()
        if resp.status != 200:
            raise ExecutionError('', await resp.text())
        data = await resp.content.read()
        return data

    async def get_compiled_file(self, session: aiohttp.ClientSession, target: BuildTarget, lock: asyncio.Lock,
                                compressor: Compressor):
        print(f"Waiting for a compiled file from {self.address}")
        async with lock:
            data = aiohttp.FormData()
            archive_file = tempfile.NamedTemporaryFile(suffix='tar.xz')
            commands_file = tempfile.NamedTemporaryFile(suffix='.sh')
            target.substitute_for_absolute_paths('/')
            data.add_field('workdir', os.getcwd())
            data.add_field('targets', ', '.join(target.target_files))
            data.add_field('commands_file', commands_file.name)
            data.add_field('password', self.password)
            data.add_field('exact_lib_versions', 'true' if config.EXACT_LIB_VERSIONS else 'false')

        if self.libraries is None:
            self.libraries = []
            response = await session.post(url=self.address + self.ALL_LIBRARIES_ENDPOINT)
            libraries = (await response.json())
            for library in libraries:
                try:
                    self.libraries.append(Library(library))
                except:
                    continue

        present_libraries = []
        for file in target.all_dependency_files:
            if file.endswith('.so') or '.so.' in file:
                if Library.find_library_in_list(file, self.libraries):
                    present_libraries.append(file)

        async with lock:
            for library in present_libraries:
                await target.replace_in_commands(library, f'${{{library.split("/")[-1]}}}')
            await target.create_commands_file(commands_file.name)

            compressor.compress([file for file in target.all_dependency_files if file not in present_libraries]
                                + [commands_file.name], archive_file.name)
            data.add_field('file',
                           open(archive_file.name, 'rb'),
                           filename=archive_file.name.split('/')[-1])
            archive_file.close()
            commands_file.close()

        # Lock is released
        result = await self.get_archive(data, session)
        async with lock:
            await Compressor.extract_files(result)

    def __repr__(self):
        return self.address

    def __eq__(self, other: 'Host'):
        return self.address == other.address
