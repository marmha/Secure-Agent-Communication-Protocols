import requests
import json
import os

API_URL = "http://127.0.0.1:8000/api/register/"
CONFIG_PATH = os.path.join("agents", "config.json")

AGENTS = [
    {"name": "OrderAgent", "capabilities": ["validate_order"]},
    {"name": "PreparationAgent", "capabilities": ["check_inventory"]},
    {"name": "BillingAgent", "capabilities": ["generate_invoice"]},
    {"name": "NotificationAgent", "capabilities": ["send_notification"]},
    {"name": "AuditAgent", "capabilities": ["record_audit_event"]},
]


def register_agent(agent):
    response = requests.post(
        API_URL,
        json=agent,
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Registered {agent['name']} successfully!")
        print(f"  Token: {data['token']}")
        return agent['name'], data['token']
    else:
        print(f"Failed to register {agent['name']}: {response.text}")
        return agent['name'], None


def save_config(tokens: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(tokens, f, indent=4)
    print(f"\nSaved tokens to: {CONFIG_PATH}")


def main():
    print("=== Agent Registration Starting ===")
    tokens = {}

    for agent in AGENTS:
        name, token = register_agent(agent)
        if token:
            tokens[name] = token

    save_config(tokens)
    print("\n=== All Done! ===")


if __name__ == "__main__":
    main()
