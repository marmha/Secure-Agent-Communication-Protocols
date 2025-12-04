# agents/billing_agent/tasks.py
import asyncio

async def generate_invoice(order: dict):
    """Produce an invoice number and summary."""
    await asyncio.sleep(1.0)
    return {
        "invoice_id": "INV-001",
        "amount": 100.0,
        "order": order,
    }

