from target import BuildTarget
import aiohttp
from compressor import Compressor
import os
import asyncio
from errors import ParseError, ExecutionError
from parser import Parser
from host import Host
from host_local import HostLocal
from typing import List
import config


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
                if line.strip().startswith('#'):
                    continue
                try:
                    line = line.strip()
                    self.hosts.append(Host(line.split()[0], line.split()[1]))
                except KeyError:
                    pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Error! Hosts file cannot be found")
        self.active_hosts: List[Host] = [HostLocal()]
        self.available_hosts: List[Host] = [HostLocal()]
        self.busy_hosts: List[Host] = []
        self.lock = asyncio.Lock()
        self.host_cond_var = asyncio.Condition()
        self.parser = parser

    async def check_active_hosts(self):
        for host in self.hosts:
            if await host.is_available():
                self.active_hosts.append(host)
                self.available_hosts.append(host)

    async def get_local_host(self) -> Host:
        async with self.host_cond_var:
            while len(self.available_hosts) == 0 or not isinstance(self.available_hosts[0], HostLocal):
                await self.host_cond_var.wait()
            host = self.available_hosts.pop(0)
            self.busy_hosts.append(host)
            return host

    async def get_available_host(self) -> Host:
        async with self.host_cond_var:
            if len(self.available_hosts) == 0:
                await self.host_cond_var.wait()
            host = self.available_hosts.pop()
            self.busy_hosts.append(host)
            return host

    async def release_host(self, host: Host):
        async with self.host_cond_var:
            if isinstance(host, HostLocal):
                self.available_hosts.insert(0, host)
            else:
                self.available_hosts.append(host)
            self.busy_hosts.remove(host)
            self.host_cond_var.notify(n=1)

    async def get_best_host(self, target: BuildTarget) -> Host:
        async with self.host_cond_var:
            if len(self.available_hosts) == 0:
                await self.host_cond_var.wait()
            if len(self.available_hosts) == 1:
                host = self.available_hosts.pop()
            else:
                best_host_index = 1
                i = 1
                max_libraries = 0
                for host in self.available_hosts[1:]:
                    found_libraries = len(await host.get_present_libraries(target))
                    if found_libraries > max_libraries:
                        max_libraries = found_libraries
                        best_host_index = i
                    i += 1
                host = self.available_hosts[best_host_index]
            self.busy_hosts.append(host)
            return host

    async def get_compiled_file(self, session: aiohttp.ClientSession, target: BuildTarget) -> None:
        # Acquire the lock to get a temporary file
        await target.get_libraries_dependencies()
        if config.CHOOSE_HOST_WITH_MORE_LIBS:
            host = await self.get_best_host(target)
        else:
            host = await self.get_available_host()
        try:
            await host.get_compiled_file(session, target, self.lock, self.compressor)
            await self.release_host(host)
        except ExecutionError as e:
            print(f"ERROR in running command at remote host '{host.address}. OUTPUT: \n'"
                  f"-------------------------------------------------------------------\n"
                  f"{e.commands_output}"
                  f"\n-------------------------------------------------------------------\n"
                  f"Trying to build the target locally...")
            localhost = await self.get_local_host()
            try:
                await localhost.get_compiled_file(session, target, self.lock, self.compressor)
                await self.release_host(localhost)
            except ExecutionError as e:
                print('Unable to build the target on local computer too...')
                raise e

        except Exception as e:
            print(f"Failed to build target... Reason: {str(e)}\n Trying to build on local computer")
            if await host.is_available():
                await self.release_host(host)
            localhost = await self.get_local_host()
            try:
                await localhost.get_compiled_file(session, target, self.lock, self.compressor)
                await self.release_host(localhost)
            except ExecutionError as e:
                print('Unable to build the target on local computer too...')
                raise e

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
            await self.get_compiled_file(session, target)
