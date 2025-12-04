# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import Agent, AuditLog
from .utils import generate_token, authenticate_agent, audit_log
from asgiref.sync import async_to_sync
import uuid
from django.utils.timezone import localtime

# REGISTER AGENT
@api_view(["POST"])
def register_agent(request):
    name = request.data.get("name")
    if not name:
        return Response({"error": "name required"}, status=400)

    token = generate_token()
    agent, created = Agent.objects.get_or_create(name=name, defaults={"token": token})

    if not created:
        token = agent.token

    audit_log(agent, "/register", request.data, {"token": token}, correlation_id=None)
    return Response({"token": token})


# ORDER AGENT
@api_view(["POST"])
def acp_order(request):
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    if not msg:
        return Response({"error": "content missing"}, status=400)

    print("\n📩 [OrderAgent] Received:", msg)

    correlation_id = str(uuid.uuid4())  # start workflow
    msg["correlation_id"] = correlation_id

    from agents.order_agent.agent import OrderAgent
    from agents.order_agent.client import OrderAgentClient
    from agents.preparation_agent.client import PreparationAgentClient

    order_agent = OrderAgent("OrderAgent", OrderAgentClient())
    result = async_to_sync(order_agent.execute_task)("validate_order", data=msg)
    result["correlation_id"] = correlation_id

    audit_log(agent, "/acp/order", {"content": msg}, result, correlation_id)

    print("✔ Order Validated:", result)

    if result.get("status") == "order_validated":
        prep = Agent.objects.get(name="PreparationAgent")
        print(f"➡ Forwarding to PreparationAgent :: token={prep.token}")
        async_to_sync(PreparationAgentClient(token=prep.token).acp_call)(
            "preparation", result
        )

    return Response(result)


@api_view(["POST"])
def acp_preparation(request):
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    print("📦 [PreparationAgent] Received:", msg)

    correlation_id = msg.get("correlation_id")  # 🔥 Keep workflow trace

    from agents.preparation_agent.agent import PreparationAgent
    from agents.billing_agent.client import BillingAgentClient

    result = async_to_sync(PreparationAgent("PreparationAgent", None).execute_task)(
        "check_inventory", data=msg
    )
    result["correlation_id"] = correlation_id

    audit_log(agent, "/acp/preparation", {"content": msg}, result, correlation_id)
    print("✔ Inventory checked:", result)

    if result.get("inventory_ok"):
        bill = Agent.objects.get(name="BillingAgent")
        print("➡ Forwarding to BillingAgent using token:", bill.token)

        async_to_sync(BillingAgentClient(token=bill.token).acp_call)(
            "billing", result
        )

    return Response(result)



# BILLING AGENT
@api_view(["POST"])
def acp_billing(request):
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    print("💰 [BillingAgent] Received:", msg)

    correlation_id = msg.get("correlation_id")  # 🔥 Keep trace alive

    from agents.billing_agent.agent import BillingAgent
    from agents.notification_agent.client import NotificationAgentClient

    result = async_to_sync(BillingAgent("BillingAgent", None).execute_task)(
        "generate_invoice", order=msg
    )
    result["correlation_id"] = correlation_id

    audit_log(agent, "/acp/billing", {"content": msg}, result, correlation_id)
    print("✔ Invoice created:", result)

    notif = Agent.objects.get(name="NotificationAgent")
    print("➡ Forwarding to NotificationAgent using token:", notif.token)

    async_to_sync(NotificationAgentClient(token=notif.token).acp_call)(
        "notification", result
    )

    return Response(result)


# NOTIFICATION AGENT
@api_view(["POST"])
def acp_notification(request):
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    print("📣 [NotificationAgent] Received:", msg)

    correlation_id = msg.get("correlation_id")  # 🔥 Continue workflow

    from agents.notification_agent.agent import NotificationAgent
    from agents.audit_agent.client import AuditAgentClient

    result = async_to_sync(NotificationAgent("NotificationAgent", None).execute_task)(
        "send_notification", data=msg
    )
    result["correlation_id"] = correlation_id

    audit_log(agent, "/acp/notification", {"content": msg}, result, correlation_id)
    print("✔ Notification sent:", result)

    audit = Agent.objects.get(name="AuditAgent")
    print("➡ Forwarding to AuditAgent using token:", audit.token)

    async_to_sync(AuditAgentClient(token=audit.token).acp_call)(
        "audit", result
    )

    return Response(result)



# AUDIT AGENT
@api_view(["POST"])
def acp_audit(request):
    agent = authenticate_agent(request)
    if not agent:
        return Response({"error": "unauthorized"}, status=401)

    msg = request.data.get("content")
    print("📝 [AuditAgent] Final Event:", msg)

    correlation_id = msg.get("correlation_id")

    from agents.audit_agent.agent import AuditAgent
    audit_agent = AuditAgent("AuditAgent", None)

    result = async_to_sync(audit_agent.execute_task)(
        "record_audit_event", data=msg
    )
    result["correlation_id"] = correlation_id

    audit_log(agent, "/acp/audit", {"content": msg}, result, correlation_id)

    print("🎯 WORKFLOW COMPLETE")

    return Response(result)


# TIMELINE VIEW
def workflow_timeline(request):
    logs = list(
        AuditLog.objects.select_related("agent")
        .order_by("-timestamp")[:50]
    )
    logs.reverse()
    return render(request, "api/workflow_timeline.html", {"logs": logs})


# PIPELINE VIEW
@api_view(["GET"])
def workflow_pipelines(request):
    pipelines = []
    for cid in AuditLog.objects.values_list("correlation_id", flat=True).distinct():
        if not cid:
            continue

        logs = AuditLog.objects.filter(correlation_id=cid) \
            .select_related("agent") \
            .order_by("timestamp")

        steps = [
            {"agent": l.agent.name, "status": "done"}
            for l in logs
        ]

        pipelines.append({
            "correlation_id": cid,
            "steps": steps,
            "started": logs.first().timestamp,
            "updated": logs.last().timestamp,
        })

    return render(request, "api/workflow_pipelines.html", {"pipelines": pipelines})


def dashboard(request):
    """
    Simple dashboard for workflows:
    - totals
    - per-pipeline status
    """
    # Get all logs with a correlation_id
    logs = (
        AuditLog.objects
        .exclude(correlation_id__isnull=True)
        .select_related("agent")
        .order_by("timestamp")
    )

    pipelines = {}

    for log in logs:
        cid = log.correlation_id
        if cid not in pipelines:
            pipelines[cid] = {
                "correlation_id": cid,
                "started": log.timestamp,
                "updated": log.timestamp,
                "agents": set(),
                "completed": False,
            }

        p = pipelines[cid]
        p["updated"] = log.timestamp
        if log.agent:
            p["agents"].add(log.agent.name)
            if log.agent.name == "AuditAgent":
                p["completed"] = True

    pipeline_list = []
    for p in pipelines.values():
        pipeline_list.append({
            "correlation_id": p["correlation_id"],
            "started": localtime(p["started"]),
            "updated": localtime(p["updated"]),
            "agents": sorted(p["agents"]),
            "completed": p["completed"],
        })

    # Sort by last updated desc
    pipeline_list.sort(key=lambda x: x["updated"], reverse=True)

    total = len(pipeline_list)
    completed = sum(1 for p in pipeline_list if p["completed"])
    running = total - completed

    context = {
        "total": total,
        "completed": completed,
        "running": running,
        "pipelines": pipeline_list[:20],  # last 20 pipelines
    }
    return render(request, "api/dashboard.html", context)
