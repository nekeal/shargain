class RateLimited(Exception):
    """Raised by a job handler when the underlying provider asks us to slow down."""

    def __init__(self, message: str = "Rate limited", retry_after: int | float = 60):
        super().__init__(message)
        self.retry_after = retry_after


class RetryableError(Exception):
    """Error that should be retried with backoff."""


class NonRetryableError(Exception):
    """Error that should not be retried; job should go straight to dead."""


class UnknownJobType(Exception):
    def __init__(self, job_type: str):
        self.job_type = job_type
        super().__init__(f"Unknown job type: {job_type}")
