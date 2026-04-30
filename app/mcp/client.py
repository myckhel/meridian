import httpx


class MCPClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def get_tools(self) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url)
            response.raise_for_status()
            return response.json()