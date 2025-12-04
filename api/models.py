#models/api
from django.db import models
import uuid

class Agent(models.Model):
    name = models.CharField(max_length=150, unique=True)
    token = models.CharField(max_length=256, unique=True)
    capabilities = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    last_seen = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS = [("pending", "Pending"), ("assigned", "Assigned"), ("completed", "Completed")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_type = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL)
    result = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_type} ({self.status})"


    
class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    agent = models.ForeignKey("Agent", on_delete=models.CASCADE, null=True)

    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)

    trace = models.CharField(max_length=255, default="OK")

    # ✅ NEW FIELD
    correlation_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp} - {self.endpoint}"