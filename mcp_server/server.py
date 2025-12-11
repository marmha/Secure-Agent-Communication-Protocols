# mcp_server/server.py
import sys
import json
import traceback
from tools import send_email_tool

TOOLS = {
    "send_email": send_email_tool,
}

def send_json(data):
    sys.stdout.write(json.dumps(data) + "\n")
    sys.stdout.flush()

def main():
    send_json({"mcp_version": "1.0", "status": "ready", "tools": list(TOOLS.keys())})

    for line in sys.stdin:
        try:
            request = json.loads(line)
            tool_name = request.get("tool")
            params = request.get("params", {})

            if tool_name not in TOOLS:
                send_json({"error": "Unknown tool"})
                continue

            result = TOOLS[tool_name](params)
            send_json({"result": result})

        except Exception as e:
            traceback.print_exc()
            send_json({"error": str(e)})

if __name__ == "__main__":
    main()
