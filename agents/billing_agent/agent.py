from agents.base_agent import BaseAgent
from .tasks import generate_invoice
from agents.notification_agent.client import NotificationAgentClient

class BillingAgent(BaseAgent):
    async def execute_task(self, task_name: str, **kwargs):
        if task_name == "generate_invoice":
            result = await generate_invoice(kwargs.get("order", {}))

            # Forward to NotificationAgent
            notif_client = NotificationAgentClient()
            await notif_client.acp_call("notification", result)

            return result

        raise ValueError(f"Unknown task {task_name}")

