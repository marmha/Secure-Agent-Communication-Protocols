# agents/notification_agent/tasks.py
import asyncio

async def send_notification(data: dict):
    """Send email/SMS notifications."""
    await asyncio.sleep(0.8)
    return {"notified": True, "recipient": data.get("user")}
