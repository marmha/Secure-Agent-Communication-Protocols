# agents/orchestrator_agent/client.py
import httpx
import asyncio
from typing import Any, Dict, Optional

class OrchestratorClient:
    """
    HTTP ACP client for OrchestratorAgent.
    It posts to the Django ACP endpoints, using Bearer token auth when provided.
    """

    def __init__(self, server_url: str = "http://127.0.0.1:8000", token: Optional[str] = None, timeout: float = 10.0):
        self.server_url = server_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def acp_call(self, agent_endpoint: str, content: dict) -> dict:
        """
        agent_endpoint: one of "order", "preparation", "billing", "notification", "audit"
        content: dict payload to send as { "performative": "...", "content": {...} } (we send content directly)
        """
        url = f"{self.server_url}/api/acp/{agent_endpoint}/"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json={"content": content}, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    # helper wrappers for explicit calls
    async def order_validate(self, order_payload: dict) -> dict:
        return await self.acp_call("order", order_payload)

    async def check_inventory(self, content: dict) -> dict:
        return await self.acp_call("preparation", content)

    async def generate_invoice(self, order: dict) -> dict:
        return await self.acp_call("billing", order)

    async def send_notification(self, data: dict) -> dict:
        return await self.acp_call("notification", data)

    async def push_audit(self, payload: dict) -> dict:
        return await self.acp_call("audit", payload)
