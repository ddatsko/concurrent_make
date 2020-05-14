from target import BuildTarget
import urllib3
import aiohttp
from compressor import Compressor
import os
import tempfile
import asyncio
from errors import ParseError, ExecutionError
import config


class RequestsManager:
    def __init__(self, default_target: BuildTarget, hosts_filename, compressor: Compressor):
        self.compressor = compressor
        self.root_target = default_target
        try:
            self.hosts = open(hosts_filename).readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error! Hosts file cannot be found")
        self.active_hosts = []
        self.available_hosts = set()
        self.busy_hosts = set()
        self.http = urllib3.PoolManager()
        self.check_active_hosts()
        self.lock = asyncio.Lock()
        self.host_cond_var = asyncio.Condition()

    def check_active_hosts(self):
        for host in self.hosts:
            try:
                response = self.http.request('get', host + config.check_host_path)
                if response.data.decode('utf-8') == 'OK':
                    self.active_hosts.append(host)
                    print(host)
            except urllib3.exceptions.MaxRetryError:
                pass
            except Exception as e:
                print(f'Error in checking host {host}: {e}')

        self.available_hosts = set(self.active_hosts)

    async def get_available_host(self):
        async with self.host_cond_var:
            if len(self.available_hosts) == 0:
                await self.host_cond_var.wait()
            host = self.available_hosts.pop()
            self.busy_hosts.add(host)
            return host

    async def release_host(self, host: str):
        async with self.host_cond_var:
            self.available_hosts.add(host)
            self.busy_hosts.remove(host)
            self.host_cond_var.notify(n=1)

    async def get_compiled_file(self, session: aiohttp.ClientSession, target: BuildTarget) -> bytes:

        # Acquire the lock to get a temporary file
        async with self.lock:
            data = aiohttp.FormData()
            archive_file = tempfile.NamedTemporaryFile(suffix='tar.xz')
            commands_file = tempfile.NamedTemporaryFile(suffix='.sh')
            target.substitute_for_absolute_paths('/')
            data.add_field('workdir', os.getcwd())
            data.add_field('targets', ', '.join(target.target_files))
            data.add_field('commands_file', commands_file.name)

        host = await self.get_available_host()
        response = await session.post(url=f'{host}{config.libraries_host_path}',
                                      json=f'{{"needed_libraries": {[file for file in target.all_dependency_files if file.startswith(config.substitutable_lib_dirs)]}}}')
        present_libraries = (await response.json())['present_libraries']

        async with self.lock:
            for library in present_libraries:
                await target.replace_in_commands(library, f'${{{library.split("/")[-1]}}}')
            await target.create_commands_file(commands_file.name)

            self.compressor.compress([file for file in target.all_dependency_files if file not in present_libraries]
                                     + [commands_file.name], archive_file.name)
            data.add_field('file',
                           open(archive_file.name, 'rb'),
                           filename=archive_file.name.split('/')[-1])
            archive_file.close()
            commands_file.close()

        # Lock is released
        result = await self.get_archive(host, data, session)
        await self.release_host(host)

        async with self.lock:
            await Compressor.extract_files(result)

        return result

    async def get_archive(self, host: str, data: aiohttp.FormData, session: aiohttp.ClientSession) -> bytes:
        try:
            resp = await session.post(url=host + config.build_host_path, data=data)
            if resp.status != 200:
                raise ExecutionError("", str(await resp.read()))
        except ExecutionError as e:
            print(e)
            raise e
        data = await resp.content.read()
        return data

    async def build_targets(self):
        async with aiohttp.ClientSession() as session:
            await self.build_target(self.root_target, session)

    async def build_target(self, target: BuildTarget, session: aiohttp.ClientSession):
        # Simple DFS here
        async with self.lock:
            if target.up_to_date:
                return
            target.up_to_date = True

        dependency_builds = []
        for dependency in target.dependencies_targets:
            dependency_builds.append(self.build_target(dependency, session))

        print("Waiting for dependencies to build")

        await asyncio.gather(*dependency_builds)

        newest_time = 0
        target_files_time = target.get_latest_modification_time()
        up_to_date = True

        for file in target.dependencies_files_only:
            if not os.path.exists(file):
                raise ParseError(f"Error! The file {file} does not exist but is in dependencies "
                                 f"of a target {', '.join(target.target_files)}")
            if os.path.getmtime(file) > target_files_time:
                up_to_date = False

        for dep_target in target.dependencies_targets:
            newest_time = max(newest_time, dep_target.get_latest_modification_time())

        if up_to_date and newest_time < target.get_latest_modification_time() and target.targets_exist():
            target.up_to_date = True
        else:
            print("Waiting for a compiled file...")
            await self.get_compiled_file(session, target)
