import aiohttp

class Public():
    """about public"""

    def __init__(self, url: str, port: int = None):
        if port:
            self.url = f"{url}:{port}"
        else:
            self.url = url


    async def ping(self) -> dict:
        """
        description: Ping the server
        params: None
        return: dict
        """

        path = "/api/ping"

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.url}{path}") as resp:
                resp.raise_for_status()
                return await resp.json()
            

    async def get_version(self) -> dict:
        """
        description: Get the server version
        params: None
        return: dict
        """

        path = "/api/version"

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.url}{path}") as resp:
                resp.raise_for_status()
                return await resp.json()


        