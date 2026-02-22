from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shargain.accounts.models import CustomUser
from shargain.commons.models import TimeStampedModel
from shargain.subscriptions.querysets import PlanQuerySet, UserSubscriptionQuerySet


class Plan(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    max_urls = models.PositiveIntegerField()
    max_offers_per_target = models.PositiveIntegerField()
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    objects = PlanQuerySet.as_manager()

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")
        ordering = ("display_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("is_default",),
                condition=Q(is_default=True),
                name="subscriptions_single_default_plan",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"


class UserSubscription(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="user_subscriptions")
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = UserSubscriptionQuerySet.as_manager()

    class Meta:
        verbose_name = _("User subscription")
        verbose_name_plural = _("User subscriptions")
        ordering = ("-started_at", "-id")
        indexes = [
            models.Index(fields=("user", "is_active"), name="subscriptions_user_active_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("user",),
                condition=Q(is_active=True),
                name="subscriptions_single_active_subscription_per_user",
            ),
        ]

    def __str__(self) -> str:
        return f"UserSubscription(user={self.user_id}, plan={self.plan_id}, active={self.is_active})"
