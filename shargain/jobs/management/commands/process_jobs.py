import signal
import time

from django.core.management.base import BaseCommand

from shargain.jobs.processor import JobProcessor


class Command(BaseCommand):
    help = "Process background jobs from the jobs table."

    def add_arguments(self, parser):
        parser.add_argument("--worker-id", default="worker-1")
        parser.add_argument("--types", nargs="*", default=None, help="Job types to process (default: all)")
        parser.add_argument("--batch-size", type=int, default=50)
        parser.add_argument("--poll-interval", type=float, default=1.0)
        parser.add_argument("--once", action="store_true", help="Process one batch and exit")

    def handle(self, *args, **options):
        worker_id = options["worker_id"]
        job_types = options["types"]
        batch_size = options["batch_size"]
        poll_interval = options["poll_interval"]
        once = options["once"]

        processor = JobProcessor(
            worker_id=worker_id,
            job_types=job_types,
            batch_size=batch_size,
        )

        self.stdout.write(self.style.SUCCESS(f"Starting job processor {worker_id}"))

        running = {"value": True}

        def stop(signum, frame):
            running["value"] = False
            self.stdout.write("Stopping...")

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)

        while running["value"]:
            try:
                processed = processor.run_once()
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(f"Error in run_once: {exc}")
                processed = 0

            if once:
                break

            if processed == 0:
                time.sleep(poll_interval)
            else:
                # small delay to avoid tight loops
                time.sleep(0.1)

        self.stdout.write(self.style.SUCCESS("Job processor stopped."))
