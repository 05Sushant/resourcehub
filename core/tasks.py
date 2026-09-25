import json

from django.core.files.base import ContentFile
from django.utils import timezone

from celery import shared_task

from core.models import Job
from core.processors import execute_operation
@shared_task
def add_numbers(a, b):
    return a + b

@shared_task
def process_job(job_id):
    job = Job.objects.get(pk=job_id)

    job.status = Job.Status.RUNNING
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:
        input_bytes = job.input_file.read()

        # Image operations need raw bytes; text operations need a decoded string.
        if job.operation in ("RESIZE",):
            input_data = input_bytes
        else:
            input_data = input_bytes.decode("utf-8")

        result = execute_operation(
            job.operation,
            input_data,
            job.parameters,
        )

        # bytes result → binary file (.png); dict result → JSON file
        if isinstance(result, bytes):
            result_filename = f"job_{job.id}_result.png"
            job.result_file.save(
                result_filename,
                ContentFile(result),
                save=False,
            )
        else:
            result_content = json.dumps(result, indent=2)
            result_filename = f"job_{job.id}_result.json"
            job.result_file.save(
                result_filename,
                ContentFile(result_content.encode("utf-8")),
                save=False,
            )

        job.status = Job.Status.COMPLETED
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "result_file",
                "status",
                "completed_at",
            ]
        )

    except Exception as exc:
        job.status = Job.Status.FAILED
        job.error_message = str(exc)
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "error_message",
                "completed_at",
            ]
        )