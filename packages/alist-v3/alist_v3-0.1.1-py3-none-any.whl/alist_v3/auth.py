import aiohttp

class Auth():
    """about auth"""

    def __init__(self, usr: str, pwd : str, url: str = "http://127.0.0.1", port: int = 5244):
        self.usr = usr
        self.pwd = pwd
        if port:
            self.url = f"{url}:{port}"
        else:
            self.url = url

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.auth = await self.login()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()


    async def login(self) -> str:
        """
        description: Get the auth token from the server
        params: None
        return: str
        """

        path = "/api/auth/login"

        async with self.session.post(url=f"{self.url}{path}", json={"username": self.usr, "password": self.pwd}) as resp:
            resp.raise_for_status()
            self.auth = await resp.json()
            self.auth = self.auth["data"]["token"]
            return self.auth


    async def post_generate_2fa(self) -> dict:
        """
        description: Generate a 2fa token
        params: None
        return: dict
        """

        path = "/api/auth/2fa/generate"
        headers = {"Authorization": self.auth}

        async with self.session.post(f"{self.url}{path}", headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
            

    async def post_verify_2fa(self, otp: str) -> dict:
        """
        description: Verify a 2fa token
        params: str
        return: dict
        """

        path = "/api/auth/2fa/verify"
        headers = {"Authorization": self.auth}
        body = {"otp": otp}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
            

    async def get_me(self) -> dict:
        """
        description: Get the user information
        params: None
        return: dict
        """

        path = "/api/me"
        headers = {"Authorization": self.auth}

        async with self.session.get(f"{self.url}{path}", headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

