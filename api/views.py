# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.db.models import Count, Min, Max
from asgiref.sync import async_to_sync
from django.utils.timezone import localtime
import uuid

from .models import Agent, AuditLog
from .utils import generate_token, authenticate_agent, audit_log


# ========================= AGENT REGISTRATION =========================

@api_view(["POST"])
def register_agent(request):
    """
    POST /api/register/
    Body: { "name": "OrderAgent", "capabilities": [...] }
    """
    name = request.data.get("name")
    if not name:
        return Response({"error": "name required"}, status=400)

    token = generate_token()
    agent, created = Agent.objects.get_or_create(name=name, defaults={"token": token})
    if not created:
        token = agent.token

    audit_log(agent, "/register", request.data, {"token": token})
    return Response({"token": token})


# ============================= ORDER AGENT ============================

@api_view(["POST"])
def acp_order(request):
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    if not msg:
        return Response({"error": "content missing"}, status=400)

    print("\n📩 [OrderAgent] Received:", msg)

    # 🔥 ALWAYS CREATE correlation_id
    correlation_id = str(uuid.uuid4())
    msg["correlation_id"] = correlation_id

    from agents.order_agent.agent import OrderAgent
    from agents.preparation_agent.client import PreparationAgentClient

    # Run local task
    order_agent = OrderAgent("OrderAgent", None)
    result = async_to_sync(order_agent.execute_task)(
        "validate_order",
        data=msg,
    )

    # 🔥 ALWAYS RETURN correlation_id
    result["correlation_id"] = correlation_id

    # Save audit
    audit_log(agent, "/acp/order", {"content": msg}, result, correlation_id)

    print("✔ Order Validated:", result)

    # Continue pipeline
    if result.get("status") == "order_validated":
        prep = Agent.objects.get(name="PreparationAgent")
        print(f"➡ Forwarding to PreparationAgent :: token={prep.token}")

        prep_client = PreparationAgentClient(token=prep.token)
        async_to_sync(prep_client.acp_call)("preparation", result)

    # 🔥 Critical: ALWAYS return correlation_id to demo_order.py
    return Response(result)


# =========================== PREPARATION AGENT ========================

@api_view(["POST"])
def acp_preparation(request):
    """
    Step 2: PreparationAgent
    - Checks inventory
    - Forwards to BillingAgent if ok
    """
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    if not msg:
        return Response({"error": "content missing"}, status=400)

    print("📦 [PreparationAgent] Received:", msg)

    correlation_id = msg.get("correlation_id")

    from agents.preparation_agent.agent import PreparationAgent
    from agents.billing_agent.client import BillingAgentClient

    prep_agent = PreparationAgent("PreparationAgent", None)
    result = async_to_sync(prep_agent.execute_task)(
        "check_inventory",
        data=msg,
    )
    result["correlation_id"] = correlation_id

    audit_log(
        agent,
        "/acp/preparation",
        {"content": msg},
        result,
        correlation_id=correlation_id,
    )
    print("✔ Inventory checked:", result)

    if result.get("inventory_ok"):
        bill = Agent.objects.get(name="BillingAgent")
        print(f"➡ Forwarding to BillingAgent :: token={bill.token}")

        bill_client = BillingAgentClient(token=bill.token)
        async_to_sync(bill_client.acp_call)("billing", result)

    return Response(result)


# ============================= BILLING AGENT ==========================

@api_view(["POST"])
def acp_billing(request):
    """
    Step 3: BillingAgent
    - Generates invoice
    - Forwards to NotificationAgent
    """
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    if not msg:
        return Response({"error": "content missing"}, status=400)

    print("💰 [BillingAgent] Received:", msg)

    correlation_id = msg.get("correlation_id")

    from agents.billing_agent.agent import BillingAgent
    from agents.notification_agent.client import NotificationAgentClient

    bill_agent = BillingAgent("BillingAgent", None)
    result = async_to_sync(bill_agent.execute_task)(
        "generate_invoice",
        order=msg,
    )
    result["correlation_id"] = correlation_id

    audit_log(
        agent,
        "/acp/billing",
        {"content": msg},
        result,
        correlation_id=correlation_id,
    )
    print("✔ Invoice created:", result)

    notif = Agent.objects.get(name="NotificationAgent")
    print(f"➡ Forwarding to NotificationAgent :: token={notif.token}")

    notif_client = NotificationAgentClient(token=notif.token)
    async_to_sync(notif_client.acp_call)("notification", result)

    return Response(result)


# =========================== NOTIFICATION AGENT =======================

@api_view(["POST"])
def acp_notification(request):
    """
    Step 4: NotificationAgent
    - Sends notification
    - Forwards to AuditAgent
    """
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    if not msg:
        return Response({"error": "content missing"}, status=400)

    print("📣 [NotificationAgent] Received:", msg)

    correlation_id = msg.get("correlation_id")

    from agents.notification_agent.agent import NotificationAgent
    from agents.audit_agent.client import AuditAgentClient

    notif_agent = NotificationAgent("NotificationAgent", None)
    result = async_to_sync(notif_agent.execute_task)(
        "send_notification",
        data=msg,
    )
    result["correlation_id"] = correlation_id

    audit_log(
        agent,
        "/acp/notification",
        {"content": msg},
        result,
        correlation_id=correlation_id,
    )
    print("✔ Notification sent:", result)

    audit = Agent.objects.get(name="AuditAgent")
    print(f"➡ Forwarding to AuditAgent :: token={audit.token}")

    audit_client = AuditAgentClient(token=audit.token)
    async_to_sync(audit_client.acp_call)("audit", result)

    return Response(result)


# =============================== AUDIT AGENT ==========================

@api_view(["POST"])
def acp_audit(request):
    """
    Final step: AuditAgent
    - Receives end-of-pipeline event
    """
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    if not msg:
        return Response({"error": "content missing"}, status=400)

    print("📝 [AuditAgent] Final Event:", msg)

    correlation_id = msg.get("correlation_id")

    from agents.audit_agent.agent import AuditAgent

    audit_agent = AuditAgent("AuditAgent", None)
    result = async_to_sync(audit_agent.execute_task)(
        "record_audit_event",
        data=msg,
    )
    result["correlation_id"] = correlation_id

    audit_log(
        agent,
        "/acp/audit",
        {"content": msg},
        result,
        correlation_id=correlation_id,
    )
    print("🎯 WORKFLOW COMPLETE")

    return Response(result)


# ============================= TIMELINE VIEW ==========================

def workflow_timeline(request):
    logs_qs = AuditLog.objects.select_related("agent").order_by("-timestamp")[:50]
    logs = list(reversed(list(logs_qs)))
    return render(request, "api/workflow_timeline.html", {"logs": logs})


# ============================ PIPELINE DASHBOARD ======================

@api_view(["GET"])
def workflow_pipelines(request):
    pipelines = []

    workflows = (
        AuditLog.objects.exclude(correlation_id__isnull=True)
        .exclude(correlation_id="")
        .values("correlation_id")
        .annotate(
            step_count=Count("id"),
            started=Min("timestamp"),
            updated=Max("timestamp"),
        )
        .order_by("-started")[:20]
    )

    for wf in workflows:
        cid = wf["correlation_id"]
        logs = (
            AuditLog.objects
            .filter(correlation_id=cid)
            .select_related("agent")
            .order_by("timestamp")
        )

        steps = [
            {
                "agent": log.agent.name if log.agent else "Unknown",
                "timestamp": localtime(log.timestamp),
                "endpoint": log.endpoint,
            }
            for log in logs
        ]

        pipelines.append({
            "correlation_id": cid,
            "steps": steps,
            "step_count": len(steps),
            "started": wf["started"],
            "updated": wf["updated"],
        })

    return render(request, "api/workflow_pipelines.html", {"pipelines": pipelines})


# ============================== DASHBOARD =============================

@api_view(["GET"])
def workflow_dashboard(request):
    workflow_count = (
        AuditLog.objects.exclude(correlation_id__isnull=True)
        .exclude(correlation_id="")
        .values("correlation_id")
        .distinct()
        .count()
    )

    events_count = AuditLog.objects.count()
    recent_logs = AuditLog.objects.select_related("agent").order_by("-timestamp")[:5]

    context = {
        "workflow_count": workflow_count,
        "events_count": events_count,
        "recent_logs": recent_logs,
    }

    return render(request, "api/workflow_dashboard.html", context)


# ============================= WORKFLOW JSON API =============================

@api_view(["GET"])
def workflow_logs_json(request):
    """
    Pure JSON feed of audit logs for polling by demo_order.py
    """
    logs = (
        AuditLog.objects
        .select_related("agent")
        .order_by("-timestamp")[:200]
    )

    data = []
    for log in logs:
        data.append({
            "agent_name": log.agent.name if log.agent else None,
            "timestamp": str(log.timestamp),
            "endpoint": log.endpoint,
            "correlation_id": log.correlation_id,
            "request": log.request_data,
            "response": log.response_data,
        })

    return Response(data)
