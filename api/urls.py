from django.urls import path
from .views import (
    register_agent,
    acp_order,
    acp_preparation,
    acp_billing,
    acp_notification,
    acp_audit,
    workflow_timeline,
    workflow_pipelines,
    dashboard,
)


urlpatterns = [
    path("register/", register_agent, name="register_agent"),

    # ACP Secure Endpoints
    path("acp/order/", acp_order, name="acp_order"),
    path("acp/preparation/", acp_preparation, name="acp_preparation"),
    path("acp/billing/", acp_billing, name="acp_billing"),
    path("acp/notification/", acp_notification, name="acp_notification"),
    path("acp/audit/", acp_audit, name="acp_audit"),
]

urlpatterns += [
    path("workflow/", workflow_timeline, name="workflow_timeline"),
]

urlpatterns += [
    path("pipelines/", workflow_pipelines, name="workflow_pipelines"),
]

urlpatterns += [
    path("dashboard/", dashboard, name="dashboard"),
]