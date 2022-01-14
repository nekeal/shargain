import asyncio
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shargain.settings.local")

app = Celery("shargain")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check_for_closed_offers": {
        "task": "shargain.offers.tasks.get_offer_source_html",
        "schedule": 5,
    }
}


async def wait(t):
    await asyncio.sleep(t)
    print(f"{t} done")


@app.task(bind=True)
def debug_task(self):
    loop = asyncio.get_event_loop()
    coros = [wait(i) for i in range(10, 1, -1)]
    loop.run_until_complete(asyncio.gather(*coros))
