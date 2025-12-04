from agents.base_agent import BaseAgent
from .tasks import validate_order


class OrderAgent(BaseAgent):
    async def execute_task(self, task_name: str, **kwargs):
        if task_name == "validate_order":
            data = kwargs.get("data", {})
            return await validate_order(data)

        raise ValueError(f"Unknown task: {task_name}")
