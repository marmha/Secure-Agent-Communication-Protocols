# api/utils.py
import uuid
from .models import Agent, AuditLog

def authenticate_agent(request):
    auth = request.headers.get("Authorization", "")
    if not auth:
        return None

    token = None

    # Accept both Token and Bearer formats ✔
    if auth.startswith("Token "):
        token = auth.replace("Token ", "").strip()
    elif auth.startswith("Bearer "):
        token = auth.replace("Bearer ", "").strip()

    if not token:
        return None

    try:
        return Agent.objects.get(token=token)
    except Agent.DoesNotExist:
        return None

def generate_token():
    return uuid.uuid4().hex



# api/utils.py
from django.utils.timezone import now

'''
def audit_log(agent, endpoint, request_data, response_data, correlation_id=None):
    try:
        AuditLog.objects.create(
            agent=agent,
            endpoint=endpoint,
            request=request_data,
            response=response_data,
            correlation_id=correlation_id,
            timestamp=now(),
        )
    except Exception as e:
        print("⚠ Failed to create AuditLog:", e)
'''
def audit_log(agent, path, request_data, response_data, correlation_id=None):
    try:
        AuditLog.objects.create(
            agent=agent,
            path=path,
            request_data=request_data,
            response_data=response_data,
            correlation_id=correlation_id
        )
    except Exception as e:
        print("⚠ Failed to create AuditLog:", e)
