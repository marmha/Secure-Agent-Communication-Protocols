# agents/orchestrator_agent/agent.py  (only the run logic shown; keep class wrapper)
from agents.base_agent import BaseAgent
from agents.orchestrator_agent.client import OrchestratorClient
from typing import Dict, Any
import asyncio

class OrchestratorAgent(BaseAgent):
    def __init__(self, name: str = "OrchestratorAgent", client: OrchestratorClient | None = None):
        client = client or OrchestratorClient()
        super().__init__(name=name, client=client)

    async def run_pipeline(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        trace = {"order": order_payload, "steps": []}
        client: OrchestratorClient = self.client

        # 1) Validate order via ACP order endpoint
        step = {"name": "validate_order", "agent": "OrderAgent"}
        val_res = await client.order_validate(order_payload)
        step["result"] = val_res
        trace["steps"].append(step)

        # push audit
        await client.push_audit({"event": "order_validated", "order": order_payload, "result": val_res})

        if not val_res or val_res.get("status") != "order_validated":
            trace["error"] = "order_validation_failed"
            return trace

        # 2) Preparation
        prep_input = {"items": order_payload.get("items", []), "order_id": order_payload.get("order_id")}
        step = {"name": "check_inventory", "agent": "PreparationAgent"}
        prep_res = await client.check_inventory(prep_input)
        step["result"] = prep_res
        trace["steps"].append(step)
        await client.push_audit({"event": "preparation_checked", "order_id": order_payload.get("order_id"), "result": prep_res})

        if not prep_res or not prep_res.get("inventory_ok", False):
            trace["error"] = "inventory_check_failed"
            return trace

        # 3) Billing
        step = {"name": "generate_invoice", "agent": "BillingAgent"}
        bill_res = await client.generate_invoice(order_payload)
        step["result"] = bill_res
        trace["steps"].append(step)
        await client.push_audit({"event": "order_billed", "order_id": order_payload.get("order_id"), "invoice": bill_res.get("invoice_id")})

        if not bill_res or not bill_res.get("invoice_id"):
            trace["error"] = "billing_failed"
            return trace

        # 4) Notification
        notify_payload = {
            "user": order_payload.get("client_email") or order_payload.get("client_name"),
            "message": f"Your order {order_payload.get('order_id')} billed (invoice {bill_res.get('invoice_id')})."
        }
        step = {"name": "send_notification", "agent": "NotificationAgent"}
        notif_res = await client.send_notification(notify_payload)
        step["result"] = notif_res
        trace["steps"].append(step)
        await client.push_audit({"event": "client_notified", "order_id": order_payload.get("order_id")})

        trace["status"] = "completed"
        return trace

    async def execute_task(self, task_name: str, **kwargs):
        if task_name == "run_pipeline":
            return await self.run_pipeline(kwargs.get("order", {}))
        raise ValueError(f"Unknown task {task_name} for OrchestratorAgent")
