from agents.base_client import BaseClient


class NotificationAgentClient(BaseClient):
    def __init__(self, token: str = None):
        super().__init__(server_url="http://127.0.0.1:8000", token=token)
