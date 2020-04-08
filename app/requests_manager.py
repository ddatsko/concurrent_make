from typing import List
from target import BuildTarget
import urllib3
import asyncio
import aiohttp
from compressor import Compressor


class RequestsManager:
    def __init__(self, ordered_targets: List[BuildTarget], hosts_filename, compressor: Compressor):
        self.compressor = compressor
        self.targets = ordered_targets
        try:
            self.hosts = open(hosts_filename).readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Error! Hosts file cannot be found")
        self.active_hosts = set()
        self.http = urllib3.PoolManager()
        self.check_active_hosts()

    def check_active_hosts(self):
        for host in self.hosts:
            try:
                response = self.http.request('get', host + '/api/v1/check')
                if response.data.decode('utf-8') == 'OK':
                    self.active_hosts.add(host)
                    print(host)
            except urllib3.exceptions.MaxRetryError as e:
                pass
            except Exception as e:
                print(f'Error in checking host: {e}')

    @staticmethod
    async def get_compiled_file(session: aiohttp.ClientSession, url: str, archive_filename: str) -> dict:
        print(f"Sending file to {url}")
        data = aiohttp.FormData()
        data.add_field('file',
                       open(archive_filename, 'rb'),
                       filename='output.tar.xz')
        resp = await session.post(url=url, data=data)
        # Note that this may raise an exception for non-2xx responses
        # You can either handle that here, or pass the exception through
        data = await resp.text()
        print(f"Received data for {url}")
        return data

    async def build_targets(self):
        # TODO: Implement asynchronous sending requests here
        async with aiohttp.ClientSession() as session:
            await RequestsManager.get_compiled_file(session, 'http://127.0.0.1:3000/api/v1/build', './output.tar.xz')
