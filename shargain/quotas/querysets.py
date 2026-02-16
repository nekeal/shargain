from django.db.models import QuerySet
from django.utils import timezone


class OfferQuotaQuerySet(QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(period_start__lte=now, period_end__gte=now)

    def for_user_target(self, user_id: int, target_id: int):
        return self.filter(user_id=user_id, target_id=target_id)
