# agents/notification_agent/mcp_tools.py

import smtplib
from email.mime.text import MIMEText

async def email_tool(to_email: str, subject: str, body: str):
    """
    Sends a real email using Gmail SMTP.
    """

    if not to_email:
        return {"error": "No email address provided"}

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "mhadhbima@gmail.com"
        msg["To"] = to_email

        # Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("mhadhbima@gmail.com", "udjx pdbl fnjh tsvg")
            server.send_message(msg)

        return {"success": True, "sent_to": to_email}

    except Exception as e:
        return {"error": str(e)}

