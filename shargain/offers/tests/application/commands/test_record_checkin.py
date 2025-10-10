import pytest
from django.core.exceptions import ObjectDoesNotExist

from shargain.offers.application.commands.record_checkin import record_checkin
from shargain.offers.models import ScrapingCheckin
from shargain.offers.tests.factories import ScrapingUrlFactory


@pytest.mark.django_db
class TestRecordCheckin:
    def test_record_checkin_success(self):
        scraping_url = ScrapingUrlFactory.create()
        offers_count = 5
        new_offers_count = 3

        record_checkin(scraping_url.id, offers_count, new_offers_count)

        checkin = ScrapingCheckin.objects.get(scraping_url=scraping_url)
        assert checkin.offers_count == offers_count
        assert checkin.new_offers_count == new_offers_count

    def test_record_checkin_with_nonexistent_scraping_url(self):
        nonexistent_id = 99999
        offers_count = 5
        new_offers_count = 3

        with pytest.raises(ObjectDoesNotExist):
            record_checkin(nonexistent_id, offers_count, new_offers_count)
