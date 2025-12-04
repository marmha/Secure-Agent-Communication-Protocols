import aiohttp

class BaseClient:
    def __init__(self, server_url: str, token: str = None):
        self.server_url = server_url
        self.token = token  # 🔥 Explicitly required now

    async def _headers(self):
        return {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

    async def acp_call(self, endpoint: str, content: dict):
        url = f"{self.server_url}/api/acp/{endpoint}/"
        payload = {"content": content}

        print(f"📡 POST → {url}")
        print(f"   🔸 Token: {self.token}")
        print(f"   📦 Payload: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=await self._headers()) as resp:
                try:
                    return await resp.json()
                except:
                    print("❌ ACP invalid JSON:", await resp.text())
                    return {"error": "invalid-response"}
