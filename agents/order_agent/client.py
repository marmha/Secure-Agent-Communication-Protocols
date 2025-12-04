# agents/order_agent/client.py
import aiohttp
from agents.base_client import BaseClient

class OrderAgentClient(BaseClient):
    def __init__(self):
        super().__init__(server_url="http://127.0.0.1:8000")

    async def send_order_validated(self, order_data):
        async with aiohttp.ClientSession() as session:
            payload = {
                "from": "order-agent",
                "content": order_data
            }

            # Must call correct endpoint!
            async with session.post(
                f"{self.server_url}/api/acp/preparation/",
                json=payload
            ) as resp:
                return await resp.json()


