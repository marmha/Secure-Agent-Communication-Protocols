# agents/order_agent/client.py



from agents.base_client import BaseClient


class OrderAgentClient(BaseClient):
    """
    Not used for ACP hops inside this demo (OrderAgent is local),
    but kept for symmetry / future use.
    """
    def __init__(self, token: str = None):
        super().__init__(server_url="http://127.0.0.1:8000", token=token)
