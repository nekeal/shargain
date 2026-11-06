"""Public API for enqueuing background jobs."""

from datetime import datetime, timedelta
from typing import Any

from django.utils import timezone

from shargain.jobs.models import Job


class Jobs:
    @staticmethod
    def enqueue(
        job_type: str,
        stream_key: str,
        payload: dict[str, Any],
        *,
        priority: int = 0,
        visible_at: datetime | None = None,
        dedup_key: str | None = None,
        max_attempts: int = 10,
    ) -> Job:
        return Job.objects.create(
            type=job_type,
            stream_key=stream_key,
            payload=payload,
            priority=priority,
            visible_at=visible_at or timezone.now(),
            dedup_key=dedup_key,
            max_attempts=max_attempts,
        )

    @staticmethod
    def enqueue_in(
        job_type: str,
        stream_key: str,
        payload: dict[str, Any],
        delay: timedelta,
        **kwargs,
    ) -> Job:
        return Jobs.enqueue(
            job_type,
            stream_key,
            payload,
            visible_at=timezone.now() + delay,
            **kwargs,
        )
