from agents.base_agent import BaseAgent
from .tasks import record_audit_event


class AuditAgent(BaseAgent):
    async def execute_task(self, task_name: str, **kwargs):
        if task_name == "record_audit_event":
            data = kwargs.get("data", {})
            return await record_audit_event(data)

        raise ValueError(f"Unknown task: {task_name}")
