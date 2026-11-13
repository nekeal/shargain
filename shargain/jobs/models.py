import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Job(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        SUCCEEDED = "succeeded", _("Succeeded")
        FAILED = "failed", _("Failed")
        DEAD = "dead", _("Dead")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(verbose_name=_("Type"), max_length=64, db_index=True)
    stream_key = models.CharField(verbose_name=_("Stream key"), max_length=128, db_index=True)
    payload = models.JSONField(verbose_name=_("Payload"), default=dict)
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    priority = models.IntegerField(verbose_name=_("Priority"), default=0)
    attempts = models.PositiveIntegerField(verbose_name=_("Attempts"), default=0)
    max_attempts = models.PositiveIntegerField(verbose_name=_("Max attempts"), default=10)
    visible_at = models.DateTimeField(verbose_name=_("Visible at"), default=timezone.now, db_index=True)
    lease_owner = models.CharField(verbose_name=_("Lease owner"), max_length=64, blank=True, default="")
    lease_expires_at = models.DateTimeField(verbose_name=_("Lease expires at"), null=True, blank=True)
    dedup_key = models.CharField(
        verbose_name=_("Dedup key"), max_length=128, unique=True, null=True, blank=True
    )
    last_error = models.TextField(verbose_name=_("Last error"), blank=True, default="")
    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")
        indexes = [
            models.Index(fields=["stream_key", "status", "created_at"], name="job_stream_status_created_idx"),
            models.Index(fields=["type", "status", "visible_at"], name="job_type_status_visible_idx"),
            models.Index(fields=["lease_expires_at"], name="job_lease_expires_idx"),
            models.Index(fields=["visible_at"], name="job_visible_idx"),
        ]
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.type} ({self.id})"


class RateLimit(models.Model):
    key = models.CharField(verbose_name=_("Key"), max_length=64, primary_key=True)
    capacity = models.DecimalField(verbose_name=_("Capacity"), max_digits=10, decimal_places=2, default=1)
    refill_rate_per_sec = models.DecimalField(
        verbose_name=_("Refill rate per sec"), max_digits=10, decimal_places=4, default=1
    )
    tokens = models.DecimalField(verbose_name=_("Tokens"), max_digits=10, decimal_places=2, default=1)
    last_refill_at = models.DateTimeField(verbose_name=_("Last refill at"), default=timezone.now)
    blocked_until = models.DateTimeField(verbose_name=_("Blocked until"), null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Rate limit")
        verbose_name_plural = _("Rate limits")

    def __str__(self):
        return self.key
