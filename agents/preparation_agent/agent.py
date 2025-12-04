# agents/preparation_agent/agent.py
from agents.base_agent import BaseAgent
from .tasks import check_inventory
from agents.billing_agent.client import BillingAgentClient

class PreparationAgent(BaseAgent):
    async def execute_task(self, task_name: str, **kwargs):
        if task_name == "check_inventory":
            result = await check_inventory(kwargs.get("data", {}))

            # Forward workflow if inventory OK
            if result.get("inventory_ok"):
                await BillingAgentClient().acp_call("billing", result)

            return result

        raise ValueError(f"Unknown task {task_name}")

