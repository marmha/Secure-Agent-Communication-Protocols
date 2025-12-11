import requests
import json
import time
import os

API_URL = "http://127.0.0.1:8000/api/acp/order/"
AUDIT_URL = "http://127.0.0.1:8000/api/workflow/"

# Load tokens
CONFIG_PATH = os.path.join("agents", "config.json")

with open(CONFIG_PATH, "r") as f:
    token_data = json.load(f)

ORDER_TOKEN = token_data.get("OrderAgent")

print("\n==============================")
print("🚀 SECURE AGENTS WORKFLOW TEST")
print("==============================\n")

print(f"🔑 Using OrderAgent Token: {ORDER_TOKEN}\n")

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

# ------------------------------
#  STEP 1: Send to OrderAgent
# ------------------------------
print("📤 Sending Order to OrderAgent...\n")
resp = requests.post(API_URL, json=order_payload, headers=headers)

try:
    json_response = resp.json()
except Exception:
    print("❌ ERROR: Server did not return valid JSON!")
    print(resp.text)
    exit()

# Basic validation
correlation_id = json_response.get("correlation_id")
print(f"🆔 Correlation ID: {correlation_id}")

status = json_response.get("status", "")
print(f"➡ OrderAgent returned status: {status}")

if status != "order_validated":
    print("❌ OrderAgent failed — stopping.\n")
    exit()

print("✓ OrderAgent completed successfully.\n")
time.sleep(1)


# ---------------------------------------------------
#  STEP 2: Poll Audit Logs to see workflow progression
# ---------------------------------------------------
print("📡 Monitoring workflow...\n")

expected_steps = [
    "OrderAgent",
    "PreparationAgent",
    "BillingAgent",
    "NotificationAgent",
    "AuditAgent"
]

completed_steps = []

# Poll up to 10 seconds
for i in range(10):
    logs = requests.get("http://127.0.0.1:8000/api/workflow/json/").json()

    # Filter logs belonging to workflow
    workflow_logs = [log for log in logs if log.get("correlation_id") == correlation_id]

    for log in workflow_logs:
        agent_name = log.get("agent_name")
        if agent_name not in completed_steps:
            completed_steps.append(agent_name)
            print(f"✓ Step completed: {agent_name}")

    if set(completed_steps) == set(expected_steps):
        break

    time.sleep(1)

print("\n📌 Workflow steps completed:")
for step in completed_steps:
    print(f"   - {step}")

missing = set(expected_steps) - set(completed_steps)
if missing:
    print("\n⚠ Missing steps:", missing)

# ---------------------------------------------------
#   Detect MCP Email Result
# ---------------------------------------------------

print("\n🔍 Checking for MCP Email Action...")

email_logs = [
    log for log in workflow_logs
    if "mcp_email" in str(log.get("response", "")).lower()
]

if email_logs:
    print("📧 MCP Email Tool was called!")
    print("➡ Email event log:")
    print(json.dumps(email_logs[-1], indent=4))
else:
    print("⚠ No MCP email activity found in logs.")


# ---------------------------------------------------
#   Final Summary
# ---------------------------------------------------

print("\n==============================")
print("🎯 WORKFLOW EXECUTION FINISHED")
print("==============================\n")

print("Response from OrderAgent:")
print(json.dumps(json_response, indent=4))
