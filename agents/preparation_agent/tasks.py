# agents/preparation_agent/tasks.py
import asyncio

async def check_inventory(data: dict):
    """Verify if items are available for preparation."""
    # Simulate I/O (DB, external API…)
    await asyncio.sleep(1.0)
    return {"inventory_ok": True, "items": data}