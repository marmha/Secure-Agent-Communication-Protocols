import secrets
from .models import Agent, AuditLog


def generate_token() -> str:
    """Generate a random token for agents."""
    return secrets.token_hex(16)


def authenticate_agent(request):
    """
    Read Authorization header: "Token <value>"
    Return Agent instance or None.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Token "):
        return None

    token = auth.replace("Token ", "").strip()
    try:
        return Agent.objects.get(token=token)
    except Agent.DoesNotExist:
        return None


def audit_log(agent, endpoint: str, request_data, response_data, correlation_id=None, trace="OK"):
    """
    Safe wrapper around AuditLog.objects.create
    Uses the actual model fields: endpoint, request_data, response_data, trace, correlation_id.
    """
    try:
        AuditLog.objects.create(
            agent=agent,
            endpoint=endpoint,
            request_data=request_data,
            response_data=response_data,
            correlation_id=correlation_id,
            trace=trace,
        )
    except Exception as e:
        # Do NOT crash pipeline if logging fails.
        print("⚠ Failed to create AuditLog:", e)
