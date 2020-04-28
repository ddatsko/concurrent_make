from typing import List
from target import BuildTarget
import urllib3
import aiohttp
from compressor import Compressor
import os
import tempfile
import asyncio
from errors import ParseError


class RequestsManager:
    def __init__(self, ordered_targets: List[BuildTarget], hosts_filename, compressor: Compressor):
        self.compressor = compressor
        self.targets = ordered_targets
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
        self.host_cond_var = asyncio.Condition(self.lock)

    def check_active_hosts(self):
        for host in self.hosts:
            try:
                response = self.http.request('get', host + '/api/v1/check')
                if response.data.decode('utf-8') == 'OK':
                    self.active_hosts.append(host)
                    print(host)
            except urllib3.exceptions.MaxRetryError:
                pass
            except Exception as e:
                print(f'Error in checking host {host}: {e}')

        # TODO: uncomment this
        # self.available_hosts = set(self.active_hosts)
        self.available_hosts = {"127.0.0.1:2000"}

    async def get_available_host(self):
        if len(self.available_hosts) == 0:
            await self.host_cond_var.wait()
        host = self.available_hosts.pop()
        self.busy_hosts.add(host)
        return host

    async def release_host(self, host: str):
        self.available_hosts.add(host)
        self.busy_hosts.remove(host)
        self.host_cond_var.notify()

    async def get_compiled_file(self, session: aiohttp.ClientSession, target: BuildTarget) -> bytes:
        async with self.lock:
            with tempfile.NamedTemporaryFile('w') as file:
                data = aiohttp.FormData()
                data.add_field('targets', str(target.target_files))

                archive_filename = file.name + '.tar.xz'
                commands_filename = file.name + '.sh'

                target.substitute_for_absolute_paths('/')

                # determine files that should be compressed
                files_to_compress = []
                for tgt in target.dependencies_targets:
                    for f in tgt.target_files:
                        files_to_compress.append(f)
                files_to_compress += [file for file in target.dependencies_files]

                await target.create_commands_file(commands_filename)

                self.compressor.compress(files_to_compress + [commands_filename], archive_filename)

    async def build_targets(self, root_target: BuildTarget):
        async with aiohttp.ClientSession() as session:
            await self.build_target(root_target, session)

    async def build_target(self, target: BuildTarget, session: aiohttp.ClientSession):
        # Simple DFS here

        dependency_builds = []
        for dependency in target.dependencies_targets:
            dependency_builds.append(self.build_target(dependency, session))
        await asyncio.gather(*dependency_builds)

        newest_time = 0
        target_files_time = target.get_latest_modification_time()
        up_to_date = True

        for file in target.dependencies_files:
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
