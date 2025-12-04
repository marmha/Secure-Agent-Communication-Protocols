from agents.base_agent import BaseAgent
from .tasks import send_notification
from agents.audit_agent.client import AuditAgentClient

class NotificationAgent(BaseAgent):
    async def execute_task(self, task_name: str, **kwargs):
        if task_name == "send_notification":
            result = await send_notification(kwargs.get("data", {}))

            # Forward to AuditAgent
            audit_client = AuditAgentClient()
            await audit_client.acp_call("audit", result)

            return result

        raise ValueError(f"Unknown task {task_name}")
