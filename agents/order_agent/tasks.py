# agents/order_agent/tasks.py
async def validate_order(data: dict):
    """Validate order fields or structure."""
    return {"status": "order_validated", "order": data}
