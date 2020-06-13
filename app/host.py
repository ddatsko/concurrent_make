import aiohttp
import json
from errors import ConnectionError
import asyncio


class Host:
    OK_ANSWER = 'OK'
    FAIL_ANSWER = 'NOT OK'
    CHECK_ENDPOINT = '/api/v1/check'
    INFO_ENDPOINT = '/api/v1/get_info'
    BUILD_ENDPOINT = '/api/v1/build'

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
                if self.architecture == '':
                    await self.get_server_info()
                return (await response.text()) == self.OK_ANSWER
            except Exception as e:
                print(e)
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

    def __str__(self):
        return self.address

    def __eq__(self, other: 'Host'):
        return self.address == other.address
