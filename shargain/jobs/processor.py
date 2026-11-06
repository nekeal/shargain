"""Core job processing logic: claim, execute, sweep."""

import logging
import time
from collections.abc import Iterable
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from shargain.jobs.exceptions import (
    NonRetryableError,
    RateLimited,
    UnknownJobType,
)
from shargain.jobs.models import Job, RateLimit
from shargain.jobs.registry import get_handler

logger = logging.getLogger(__name__)

DEFAULT_LEASE_DURATION = timedelta(minutes=5)
DEFAULT_BATCH_SIZE = 50
DEFAULT_POLL_INTERVAL = 1.0
DEFAULT_MIN_DELAY_BETWEEN_JOBS = 0.05


def compute_backoff(attempts: int) -> timedelta:
    # exponential backoff with jitter, capped
    base = min(2 ** attempts, 300)
    jitter = base * 0.25
    import random  # noqa: S311

    return timedelta(seconds=base + random.uniform(-jitter, jitter))  # noqa: S311


class JobProcessor:
    def __init__(
        self,
        *,
        worker_id: str,
        job_types: Iterable[str] | None = None,
        lease_duration: timedelta = DEFAULT_LEASE_DURATION,
        batch_size: int = DEFAULT_BATCH_SIZE,
        min_delay_between_jobs: float = DEFAULT_MIN_DELAY_BETWEEN_JOBS,
    ):
        self.worker_id = worker_id
        self.job_types = list(job_types) if job_types is not None else None
        self.lease_duration = lease_duration
        self.batch_size = batch_size
        self.min_delay_between_jobs = min_delay_between_jobs

    # ---------- claim ----------
    def claim_batch(self) -> list[Job]:
        """Claim up to ``batch_size`` jobs, at most one per stream_key."""
        with transaction.atomic():
            qs = Job.objects.filter(status=Job.Status.PENDING, visible_at__lte=timezone.now())
            if self.job_types is not None:
                qs = qs.filter(type__in=self.job_types)

            # DISTINCT ON (stream_key) -> at most one job per stream, oldest first
            claimed_qs = qs.order_by("stream_key", "created_at", "id").distinct("stream_key")[: self.batch_size]

            # Lock rows
            ids = list(claimed_qs.values_list("id", flat=True))
            if not ids:
                return []

            # Re-fetch with select_for_update to lock, then update status
            locked = (
                Job.objects.select_for_update(skip_locked=True)
                .filter(id__in=ids, status=Job.Status.PENDING)
            )
            locked_ids = [j.id for j in locked]
            if not locked_ids:
                return []

            for jid in locked_ids:
                Job.objects.filter(id=jid).update(
                    status=Job.Status.PROCESSING,
                    lease_owner=self.worker_id,
                    lease_expires_at=timezone.now() + self.lease_duration,
                    attempts=F("attempts") + 1,
                )

            return list(Job.objects.filter(id__in=locked_ids))

    def sweep_expired_leases(self) -> int:
        count = 0
        with transaction.atomic():
            expired = (
                Job.objects.select_for_update(skip_locked=True)
                .filter(status=Job.Status.PROCESSING, lease_expires_at__lt=timezone.now())
            )
            for job in expired:
                if job.attempts >= job.max_attempts:
                    job.status = Job.Status.DEAD
                else:
                    job.status = Job.Status.PENDING
                    job.lease_owner = ""
                    job.lease_expires_at = None
                    job.visible_at = timezone.now() + compute_backoff(job.attempts)
                job.save(update_fields=["status", "lease_owner", "lease_expires_at", "visible_at", "updated_at"])
                count += 1
        return count

    # ---------- rate limiting ----------
    def _check_rate_limit(self, scope: str) -> RateLimit | None:
        rl = RateLimit.objects.filter(key=scope).first()
        if rl is None:
            return None
        if rl.blocked_until and rl.blocked_until > timezone.now():
            return rl
        return None

    def _block_scope(self, scope: str, retry_after_seconds: float) -> None:
        from django.utils import timezone as tz

        blocked_until = tz.now() + timedelta(seconds=retry_after_seconds)
        RateLimit.objects.update_or_create(
            key=scope,
            defaults={"blocked_until": blocked_until, "updated_at": tz.now()},
        )

    # ---------- process ----------
    def process_job(self, job: Job) -> None:
        handler = get_handler(job.type)
        if handler is None:
            raise UnknownJobType(job.type)

        scope = self._scope_for(job)

        # rate limit check
        rl = self._check_rate_limit(scope)
        if rl is not None:
            # put back to pending with visible_at = blocked_until
            job.status = Job.Status.PENDING
            job.lease_owner = ""
            job.lease_expires_at = None
            job.visible_at = rl.blocked_until
            job.save(update_fields=["status", "lease_owner", "lease_expires_at", "visible_at", "updated_at"])
            return

        try:
            handler(job)
        except RateLimited as exc:
            retry_after = getattr(exc, "retry_after", 60)
            self._block_scope(scope, retry_after)
            job.status = Job.Status.PENDING
            job.lease_owner = ""
            job.lease_expires_at = None
            job.visible_at = timezone.now() + timedelta(seconds=retry_after)
            job.last_error = str(exc)
            job.save(
                update_fields=["status", "lease_owner", "lease_expires_at", "visible_at", "last_error", "updated_at"]
            )
            return
        except NonRetryableError as exc:
            job.status = Job.Status.DEAD
            job.lease_owner = ""
            job.lease_expires_at = None
            job.last_error = str(exc)
            job.save(update_fields=["status", "lease_owner", "lease_expires_at", "last_error", "updated_at"])
            return
        except Exception as exc:  # noqa: BLE001
            logger.exception("Job %s failed", job.id)
            job.last_error = str(exc)
            if job.attempts >= job.max_attempts:
                job.status = Job.Status.DEAD
            else:
                job.status = Job.Status.PENDING
                job.visible_at = timezone.now() + compute_backoff(job.attempts)
            job.lease_owner = ""
            job.lease_expires_at = None
            job.save(
                update_fields=["status", "lease_owner", "lease_expires_at", "visible_at", "last_error", "updated_at"]
            )
            return

        # success
        job.status = Job.Status.SUCCEEDED
        job.lease_owner = ""
        job.lease_expires_at = None
        job.save(update_fields=["status", "lease_owner", "lease_expires_at", "payload", "updated_at"])

    def _scope_for(self, job: Job) -> str:
        # default scope derived from job type; handlers may override via payload
        return job.payload.get("rate_limit_scope") or f"{job.type.split('.')[0]}:{job.type}"

    def run_once(self) -> int:
        self.sweep_expired_leases()
        jobs = self.claim_batch()
        processed = 0
        for job in jobs:
            # re-fetch fresh
            job.refresh_from_db()
            self.process_job(job)
            processed += 1
            if self.min_delay_between_jobs:
                time.sleep(self.min_delay_between_jobs)
        return processed



