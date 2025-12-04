import aiohttp
import json


class BaseClient:
    """
    Shared async client for ACP (and MCP if you extend it).
    Token is ALWAYS passed explicitly from Django DB.
    """

    def __init__(self, server_url: str = "http://127.0.0.1:8000", token: str = None):
        self.server_url = server_url.rstrip("/")
        self.token = token  # no auto-load from config.json anymore

    async def _headers(self):
        return {
            "Authorization": f"Token {self.token}" if self.token else "",
            "Content-Type": "application/json",
        }

    async def acp_call(self, endpoint: str, content: dict):
        """
        Call another agent via Django ACP endpoint.
        endpoint: 'preparation', 'billing', 'notification', 'audit'
        """
        url = f"{self.server_url}/api/acp/{endpoint}/"
        payload = {"content": content}

        print(f"📡 POST → {url}")
        print(f"   🔸 Token: {self.token}")
        print(f"   📦 Payload: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=await self._headers()) as resp:
                text = await resp.text()
                try:
                    data = json.loads(text)
                except Exception:
                    print(f"❌ Server did not return valid JSON: {text}")
                    return {"error": "invalid-json", "status": resp.status, "body": text}

                if resp.status >= 400:
                    print(f"❌ Server Error {resp.status}: {data}")
                return data
