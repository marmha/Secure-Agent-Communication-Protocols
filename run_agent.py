# run_agent.py
import asyncio
import importlib
import json
import inspect
import sys
from pathlib import Path

# Simple mock client for tests (returns canned responses).
class MockClient:
    def __init__(self, server_url="http://localhost:8000", token=None):
        self.server_url = server_url
        self.token = token

    async def mcp_call(self, tool, payload):
        return {"mock": True, "tool": tool, "payload": payload}

    async def acp_call(self, agent, payload):
        return {"mock": True, "to_agent": agent, "payload": payload}

async def run_agent(agent_module_class: str, task_name: str, task_args: dict):
    """
    agent_module_class: "agents.order_agent.agent.OrderAgent"
    task_name: string name of task to call, e.g. "validate_order"
    task_args: dict with keyword args for execute_task
    """
    # split module and class
    module_path, class_name = agent_module_class.rsplit(".", 1)
    module = importlib.import_module(module_path)
    AgentClass = getattr(module, class_name)

    # instantiate agent with a mock client
    client = MockClient()
    agent = AgentClass(name=class_name, client=client)

    # call execute_task

    if inspect.iscoroutinefunction(agent.execute_task):
        result = await agent.execute_task(task_name, **task_args)
    else:
        result = agent.execute_task(task_name, **task_args)

    print("=== RESULT ===")
    print(json.dumps(result, indent=2))

def load_task_args(raw: str):
    """
    Accept either:
      - a JSON string
      - a filename (path) (we accept plain filename without @)
    Robustly strips UTF-8 BOM if present.
    """
    from pathlib import Path

    def _load_text(path: Path):
        text = path.read_text(encoding="utf-8")
        # Strip common BOMs and leading/trailing whitespace
        return text.lstrip("\ufeff").strip()

    if raw.startswith("@"):
        path = Path(raw[1:])
        if not path.exists():
            raise FileNotFoundError(f"Task file not found: {path}")
        text = _load_text(path)
        return json.loads(text)
    # if raw looks like a file path (exists), load it too
    p = Path(raw)
    if p.exists():
        text = _load_text(p)
        return json.loads(text)

    # otherwise treat as inline JSON string
    text = raw.lstrip("\ufeff").strip()
    return json.loads(text)


def usage_and_exit():
    print("Usage:")
    print("  python run_agent.py <agent_module_class> <task_name> <task_args_json_or_@file>")
    print("Example (file):")
    print("  python run_agent.py agents.order_agent.agent.OrderAgent validate_order @task.json")
    print("Example (inline JSON - PowerShell users may need to escape quotes):")
    print(r"  python run_agent.py agents.order_agent.agent.OrderAgent validate_order '{\"data\": {\"order_id\": \"ORD-1\", \"client_name\": \"Alice\"}}'")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage_and_exit()

    agent_module_class = sys.argv[1]
    task_name = sys.argv[2]
    raw_args = sys.argv[3]

    try:
        task_args = load_task_args(raw_args)
    except Exception as e:
        print(f"Error loading task_args: {e}")
        usage_and_exit()

    asyncio.run(run_agent(agent_module_class, task_name, task_args))
