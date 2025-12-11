#api/utils.py
import secrets
from .models import Agent, AuditLog
#from oauth2_provider.models import AccessToken
#from django.utils.timezone import now

def generate_token() -> str:
    """Generate a random token for agents."""
    return secrets.token_hex(16)

def authenticate_agent(request):
    """
    Simple Token authentication ONLY.
    Authorization: Token <agent_token>
    """
    auth = request.headers.get("Authorization", "").strip()
    if not auth.startswith("Token "):
        return None

    raw = auth.replace("Token ", "").strip()

    try:
        return Agent.objects.get(token=raw)
    except Agent.DoesNotExist:
        return None

'''def authenticate_agent(request):
    """
    Hybrid auth:
    - Legacy:  Authorization: Token <agent.token>
    - OAuth2: Authorization: Bearer <access_token>
              (maps to Agent via AccessToken.application.name)
    """
    auth = request.headers.get("Authorization", "").strip()
    if not auth:
        return None

    # ---- 1) Legacy static token: "Token <value>" ----
    if auth.startswith("Token "):
        raw = auth.replace("Token ", "").strip()
        try:
            return Agent.objects.get(token=raw)
        except Agent.DoesNotExist:
            return None

    # ---- 2) OAuth2 Bearer token: "Bearer <access_token>" ----
    if auth.startswith("Bearer "):
        raw = auth.replace("Bearer ", "").strip()
        try:
            access_token = AccessToken.objects.select_related("application").get(
                token=raw
            )
        except AccessToken.DoesNotExist:
            return None

        # Expired?
        if access_token.expires < now():
            return None

        # Map Application -> Agent (we assume names match)
        app = access_token.application
        try:
            agent = Agent.objects.get(name=app.name)
        except Agent.DoesNotExist:
            return None
        return agent

    # Unknown scheme
    return None
'''


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
