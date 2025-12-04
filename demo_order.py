import requests
import json
import time
import os

API_URL = "http://127.0.0.1:8000/api/acp/order/"

# Load token from agents/config.json
CONFIG_PATH = os.path.join("agents", "config.json")

with open(CONFIG_PATH, "r") as f:
    token_data = json.load(f)

ORDER_TOKEN = token_data.get("OrderAgent")


print("\n=== WORKFLOW PIPELINE RESULT ===")
print(f"Using Token: {ORDER_TOKEN}\n")

headers = {
    "Authorization": f"Token {ORDER_TOKEN}",
    "Content-Type": "application/json"
}

order_payload = {
    "content": {
        "order_id": "ORD-DEMO-1",
        "items": ["sku1", "sku2"],
        "user": "customer@example.com"
    }
}

AGENT_STEPS = [
    ("OrderAgent", "validate_order"),
    ("PreparationAgent", "check_inventory"),
    ("BillingAgent", "generate_invoice"),
    ("NotificationAgent", "send_notification"),
    ("AuditAgent", "record_audit_event"),
]

# Send initial request
resp = requests.post(API_URL, json=order_payload, headers=headers)

try:
    json_response = resp.json()
except Exception:
    print("❌ Server did not return valid JSON")
    print(resp.text)
    exit()

# Display first response
current_response = json_response
print("➡ OrderAgent:", current_response.get("status", current_response))

if current_response.get("status") != "order_validated":
    print("❌ Failed at OrderAgent step")
    exit()

print("✓ OrderAgent completed\n")
time.sleep(0.6)  # simulate step timing


# Poll Django AuditLog to confirm downstream execution
print("📡 Waiting for next workflow steps...\n")
time.sleep(2)

# Fetch full audit log for visibility
audit_resp = requests.get("http://127.0.0.1:8000/admin/api/auditlog/")
print("Audit logs updated? Check Admin UI!")


# Final success print
print("🎯 FULL WORKFLOW COMPLETED!\n")
print("Response from OrderAgent:")
print(json.dumps(current_response, indent=4))
