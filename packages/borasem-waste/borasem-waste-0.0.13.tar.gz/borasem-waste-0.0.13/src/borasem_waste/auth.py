import aiohttp

class Auth:
    """Class to make requests."""

    def __init__(self, websession: aiohttp.ClientSession, host: str='https://kundportal.borasem.se/EDPFutureWeb'):
        """Initialize the auth."""
        self.websession = websession
        self.host = host

    async def request(self, method: str, path: str, **kwargs) -> aiohttp.ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        return await self.websession.request(
            method, f"{self.host}/{path}", **kwargs, headers=headers,
        )