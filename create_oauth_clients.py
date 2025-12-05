# create_oauth_clients.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "secure_agents.settings")
django.setup()

from oauth2_provider.models import Application
from api.models import Agent


AGENT_NAMES = [
    "OrderAgent",
    "PreparationAgent",
    "BillingAgent",
    "NotificationAgent",
    "AuditAgent",
]


def main():
    print("=== Creating OAuth2 Applications for agents ===")
    for name in AGENT_NAMES:
        agent, _ = Agent.objects.get_or_create(name=name)
        app, created = Application.objects.get_or_create(
            name=name,
            defaults={
                "client_type": Application.CLIENT_CONFIDENTIAL,
                "authorization_grant_type": Application.GRANT_CLIENT_CREDENTIALS,
            },
        )
        print(f"\nAgent: {name}")
        print(f"  Agent.id: {agent.id}")
        print(f"  OAuth2 client_id: {app.client_id}")
        print(f"  OAuth2 client_secret: {app.client_secret}")
        print(f"  Grant type: {app.authorization_grant_type}")


if __name__ == "__main__":
    main()
