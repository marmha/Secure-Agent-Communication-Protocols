import json
import os
from agents.base_client import BaseClient

CONFIG_FILE = os.path.join("agents", "config.json")

def load_token(agent_name):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
            return data.get(agent_name)
    return None

class AuditAgentClient(BaseClient):
    def __init__(self, token: str | None = None):
        super().__init__(server_url="http://127.0.0.1:8000", token=token)
