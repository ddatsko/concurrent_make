import aiohttp
import asyncio
import async_timeout


def main():
    async def fetch(session, url):
        with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.text()

    async def m():
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, 'http://python.org')
            print(html)

    loop = asyncio.get_event_loop()
    print("Hello")
    loop.run_until_complete(m())


if __name__ == "__main__":
    main()
