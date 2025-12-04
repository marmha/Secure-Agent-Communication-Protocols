import requests
import time

# === CONFIGURATION ===
DJANGO_BASE = "http://127.0.0.1:8000/api"
AGENT_NAME = "agent-demo-1"
CAPABILITIES = ["process_file"]
POLL_INTERVAL = 5  # seconds between task polls

# === 3.2 — Register Agent ===
def register_agent():
    url = f"{DJANGO_BASE}/register/"
    payload = {"name": AGENT_NAME, "capabilities": CAPABILITIES}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        token = data["token"]
        agent_id = data["agent_id"]
        print(f"[INFO] Registered Agent {AGENT_NAME} (ID: {agent_id})")
        return token
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return None

# === 3.4 — Get Next Task ===
def get_next_task(token):
    url = f"{DJANGO_BASE}/tasks/next/"
    headers = {"Authorization": f"Token {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        task = response.json().get("task")
        return task
    except Exception as e:
        print(f"[ERROR] Getting next task failed: {e}")
        return None

# === 3.5 — Execute Task ===
def execute_task(task):
    print(f"[INFO] Executing task {task['id']} - payload: {task['payload']}")
    # Simulate processing
    result = f"processed {task['payload']}"
    time.sleep(2)  # simulate work
    return result

# === 3.6 — Submit Result ===
def submit_result(token, task_id, result):
    url = f"{DJANGO_BASE}/tasks/result/"
    headers = {"Authorization": f"Token {token}"}
    payload = {"task_id": task_id, "result": result}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"[INFO] Result submitted for task {task_id}")
    except Exception as e:
        print(f"[ERROR] Submitting result failed: {e}")

# === 3.7 — Main Agent Loop ===
def run_agent():
    token = register_agent()
    if not token:
        print("[FATAL] Cannot start agent without token.")
        return

    while True:
        task = get_next_task(token)
        if task:
            result = execute_task(task)
            submit_result(token, task["id"], result)
        else:
            print("[INFO] No task available. Waiting...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_agent()
