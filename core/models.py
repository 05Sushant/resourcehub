from django.db import models


class Resource(models.Model):

    class ResourceType(models.TextChoices):
        CSV_ANALYTICS = "CSV_ANALYTICS", "CSV Analytics"
        IMAGE_PROCESSING = "IMAGE_PROCESSING", "Image Processing"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DISABLED = "DISABLED", "Disabled"

    name = models.CharField(max_length=100)
    resource_type = models.CharField(
        max_length=30,
        choices=ResourceType.choices,
    )
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.resource.name} - "
            f"{self.start_time:%Y-%m-%d %H:%M}"
        )

class Job(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    resource = models.ForeignKey(
        Resource,
        on_delete=models.PROTECT,
        related_name="jobs",
    )

    operation = models.CharField(max_length=30)

    parameters = models.JSONField(
        default=dict,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    input_file = models.FileField(
        upload_to="jobs/input/",
    )

    result_file = models.FileField(
        upload_to="jobs/results/",
        blank=True,
    )

    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
    )

    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )