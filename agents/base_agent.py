# agents/base_agent.py
import logging
import uuid

class BaseAgent:
    """
    Base class for all agents.
    Provides ID, logging, and async task execution stub.
    """
    def __init__(self, name: str, client):
        self.name = name
        self.id = str(uuid.uuid4())
        self.client = client
        self.logger = logging.getLogger(name)

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    async def execute_task(self, task_name: str, **kwargs):
        raise NotImplementedError("Each agent must implement execute_task()")
