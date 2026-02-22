from django.db.models import QuerySet


class PlanQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def default(self):
        return self.filter(is_default=True)


class UserSubscriptionQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)
