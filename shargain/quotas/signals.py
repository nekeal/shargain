from django.dispatch import receiver

from shargain.offers.signals import offers_batch_created
from shargain.quotas.services.quota import QuotaService


@receiver(offers_batch_created)
def handle_offers_created(sender, user_id: int, target_id: int, count: int, **kwargs):
    QuotaService.record_offers_created(user_id=user_id, target_id=target_id, count=count)
