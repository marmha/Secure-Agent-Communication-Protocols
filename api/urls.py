from django.urls import path
from .views import (
    register_agent,
    acp_order, acp_preparation, acp_billing,
    acp_notification, acp_audit,
    workflow_logs_json,
    workflow_timeline, workflow_pipelines,workflow_dashboard
)
urlpatterns = [
    path("register/", register_agent),

    # ACP Endpoints - Agent Communication Protocol
    path("acp/order/", acp_order),
    path("acp/preparation/", acp_preparation),
    path("acp/billing/", acp_billing),
    path("acp/notification/", acp_notification),
    path("acp/audit/", acp_audit),

    # UI Dashboard Pages
    path("workflow/", workflow_timeline, name="workflow_timeline"),
    path("pipelines/", workflow_pipelines, name="workflow_pipelines"),
    path("dashboard/", workflow_dashboard, name="workflow_dashboard"),
    path("workflow/json/", workflow_logs_json),

]
