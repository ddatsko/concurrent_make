import aiohttp
import json
from errors import ConnectionError
import asyncio
from target import BuildTarget
import tempfile
import os
from compressor import Compressor
from runner import CommandRunner


class Host:
    OK_ANSWER = 'OK'
    FAIL_ANSWER = 'NOT OK'
    CHECK_ENDPOINT = '/api/v1/check'
    INFO_ENDPOINT = '/api/v1/get_info'
    BUILD_ENDPOINT = '/api/v1/build'
    ALL_LIBRARIES_ENDPOINT = '/api/v1/all_libraries'
    CHECK_LIBRARIES_ENDPOINT = '/api/v1/libraries'

    def __init__(self, address: str, password: str):
        self.address = address.strip('/')
        self.password = password
        self.architecture = ''

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
                        print(f"Host {self.address} has architecture {self.architecture}, which is not te same as yours ({this_computer_architecture})")
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
            resp = await session.post(url=self.address + self.BUILD_ENDPOINT, data=data)
        except ConnectionError as e:
            print(e)
            raise e
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
            data.add_field('workdir', os.path.dirname(__file__))
            data.add_field('targets', ', '.join(target.target_files))
            data.add_field('commands_file', commands_file.name)
            data.add_field('password', self.password)

        print(target.all_dependency_files)
        response = await session.post(url=self.address + self.CHECK_LIBRARIES_ENDPOINT,
                                      json=f'{{"needed_libraries": {[file for file in target.all_dependency_files if ".so" in file]}, "password": "{self.password}"}}')
        present_libraries = (await response.json())['present_libraries']

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
