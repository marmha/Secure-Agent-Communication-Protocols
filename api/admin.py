#api/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
import json

from .models import Agent, Task, AuditLog


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("name", "last_seen", "active")
    list_filter = ("active",)
    search_fields = ("name", "token")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "task_type", "status", "agent", "created_at")
    list_filter = ("status", "task_type", "agent")
    search_fields = ("id", "task_type", "agent__name")


@admin.register(AuditLog)
class AuditAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "agent_name",
        "endpoint",
        "short_request",
        "short_response",
    )
    list_filter = ("endpoint", "agent")
    search_fields = ("endpoint", "agent__name")
    readonly_fields = (
        "timestamp",
        "agent",
        "endpoint",
        "pretty_request",
        "pretty_response",
        "trace",
    )

    fieldsets = (
        (None, {"fields": ("timestamp", "agent", "endpoint", "trace")}),
        ("Request", {"fields": ("pretty_request",)}),
        ("Response", {"fields": ("pretty_response",)}),
    )

    def agent_name(self, obj):
        return obj.agent.name if obj.agent else "system"
    agent_name.short_description = "Agent"

    def short_request(self, obj):
        if not obj.request_data:
            return "-"
        raw = json.dumps(obj.request_data, ensure_ascii=False)
        return Truncator(raw).chars(60)
    short_request.short_description = "Request"

    def short_response(self, obj):
        if not obj.response_data:
            return "-"
        raw = json.dumps(obj.response_data, ensure_ascii=False)
        return Truncator(raw).chars(60)
    short_response.short_description = "Response"

    def pretty_request(self, obj):
        if not obj.request_data:
            return "-"
        pretty = json.dumps(obj.request_data, indent=2, ensure_ascii=False)
        return format_html("<pre style='white-space: pre-wrap'>{}</pre>", pretty)

    def pretty_response(self, obj):
        if not obj.response_data:
            return "-"
        pretty = json.dumps(obj.response_data, indent=2, ensure_ascii=False)
        return format_html("<pre style='white-space: pre-wrap'>{}</pre>", pretty)

