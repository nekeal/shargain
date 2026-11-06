import pytest

from shargain.jobs.models import Job
from shargain.jobs.processor import JobProcessor
from shargain.jobs.registry import clear_registry, job_handler


@pytest.fixture(autouse=True)
def _registry():
    clear_registry()

    @job_handler("test.echo")
    def handler(job):
        job.payload["handled"] = True

    yield
    clear_registry()


@pytest.mark.django_db
def test_claim_and_process():
    Job.objects.create(type="test.echo", stream_key="s1", payload={"msg": "hi"})
    Job.objects.create(type="test.echo", stream_key="s2", payload={"msg": "ho"})

    processor = JobProcessor(worker_id="w1", job_types=["test.echo"])
    processed = processor.run_once()
    assert processed == 2
    assert Job.objects.filter(status=Job.Status.SUCCEEDED).count() == 2


@pytest.mark.django_db
def test_per_stream_ordering():
    # two jobs same stream
    j1 = Job.objects.create(type="test.echo", stream_key="s1", payload={"n": 1})
    Job.objects.create(type="test.echo", stream_key="s1", payload={"n": 2})

    processor = JobProcessor(worker_id="w1", job_types=["test.echo"], batch_size=10)
    # first run should claim only first per stream
    claimed = processor.claim_batch()
    assert len(claimed) == 1
    assert claimed[0].id == j1.id


@pytest.mark.django_db
def test_rate_limit_blocks_scope():

    from django.utils import timezone

    from shargain.jobs.exceptions import RateLimited
    from shargain.jobs.models import RateLimit

    clear_registry()

    @job_handler("test.rl")
    def handler(job):
        raise RateLimited(retry_after=60)

    Job.objects.create(type="test.rl", stream_key="s1", payload={})
    processor = JobProcessor(worker_id="w1", job_types=["test.rl"])
    processor.run_once()

    job = Job.objects.get()
    assert job.status == Job.Status.PENDING
    rl = RateLimit.objects.get(key="test:test.rl")
    assert rl.blocked_until is not None
    assert rl.blocked_until > timezone.now()


@pytest.mark.django_db
def test_sweep_expired_lease():
    from datetime import timedelta

    from django.utils import timezone

    job = Job.objects.create(type="test.echo", stream_key="s1", payload={}, status=Job.Status.PROCESSING)
    job.lease_expires_at = timezone.now() - timedelta(minutes=1)
    job.lease_owner = "w1"
    job.save()

    processor = JobProcessor(worker_id="w2", job_types=["test.echo"])
    swept = processor.sweep_expired_leases()
    assert swept == 1
    job.refresh_from_db()
    assert job.status == Job.Status.PENDING
