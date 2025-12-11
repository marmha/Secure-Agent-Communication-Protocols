from agents.base_agent import BaseAgent
from .mcp_tools import email_tool
from agents.audit_agent.client import AuditAgentClient

class NotificationAgent(BaseAgent):
    async def execute_task(self, task_name: str, **kwargs):
        if task_name != "send_notification":
            raise ValueError(f"Unknown task {task_name}")

        data = kwargs.get("data", {})

        # ✅ Correct extraction of 'user' email
        recipient = (
            data.get("order", {})
                .get("items", {})
                .get("order", {})
                .get("user")
        )

        result_notification = {"notified": True, "recipient": recipient}

        # Call MCP email tool
        mcp_result = await email_tool(
            to_email=recipient,
            subject="Order Completed",
            body="Your order has been successfully processed!"
        )

        result = {
            "notification": result_notification,
            "mcp_email": mcp_result,
            "correlation_id": data.get("correlation_id")
        }

        # forward to audit agent
        audit_client = AuditAgentClient()
        await audit_client.acp_call("audit", result)

        return result
