from target import BuildTarget
import aiohttp
from compressor import Compressor
import os
import tempfile
import asyncio
from errors import ParseError, ExecutionError
import config
from parser import Parser
from host import Host


class RequestsManager:
    @classmethod
    async def create(cls, default_target: BuildTarget, hosts_filename: str, compressor: Compressor,
                     parser: Parser) -> 'RequestsManager':
        new_manager = RequestsManager(default_target, hosts_filename, compressor, parser)
        await new_manager.check_active_hosts()
        return new_manager

    def __init__(self, default_target: BuildTarget, hosts_filename: str, compressor: Compressor, parser: Parser):
        self.compressor = compressor
        self.root_target = default_target
        self.hosts = []
        try:
            hosts_file_lines = open(hosts_filename).readlines()
            for line in hosts_file_lines:
                try:
                    self.hosts.append(Host(line.split()[0], line.split()[1]))
                except KeyError:
                    pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Error! Hosts file cannot be found")
        self.active_hosts = []
        self.available_hosts = []
        self.busy_hosts = []
        self.lock = asyncio.Lock()
        self.host_cond_var = asyncio.Condition()
        self.parser = parser

    async def check_active_hosts(self):
        for host in self.hosts:
            if await host.is_available():
                self.active_hosts.append(host)
                self.available_hosts.append(host)

    async def get_available_host(self) -> Host:
        async with self.host_cond_var:
            if len(self.available_hosts) == 0:
                await self.host_cond_var.wait()
            host = self.available_hosts.pop()
            self.busy_hosts.append(host)
            return host

    async def release_host(self, host: Host):
        async with self.host_cond_var:
            self.available_hosts.append(host)
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
        result = await host.get_archive(data, session)
        await self.release_host(host)

        async with self.lock:
            await Compressor.extract_files(result)
        return result

    async def build_targets(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            await self.build_target(self.root_target, session)

    async def build_target(self, target: BuildTarget, session: aiohttp.ClientSession):
        # Simple DFS here
        async with self.lock:
            if target.up_to_date:
                return
            target.up_to_date = True
            await target.replace_all_variables(self.parser)
            await target.process_dependencies(self.parser)

        target.replace_special_vars()
        dependency_builds = []
        for dependency in target.dependencies_targets:
            dependency_builds.append(self.build_target(dependency, session))

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
