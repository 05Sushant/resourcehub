from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Job, Resource
from core.tasks import process_job


def _make_png_bytes(width=100, height=80):
    """Create a solid-colour PNG in memory and return its bytes."""
    from io import BytesIO
    from PIL import Image

    img = Image.new("RGB", (width, height), color=(0, 128, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class JobTaskTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="taskuser",
            password="testpass123",
        )

        self.resource = Resource.objects.create(
            name="CSV Worker",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            capacity=1,
        )

        self.input_file = SimpleUploadedFile(
            "sales.csv",
            b"name,amount\nAlice,100\nBob,200\n",
            content_type="text/csv",
        )

        self.job = Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="PROFILE",
            parameters={},
            input_file=self.input_file,
        )

    def test_process_job_completes_job(self):
        process_job(self.job.id)

        self.job.refresh_from_db()

        self.assertEqual(
            self.job.status,
            Job.Status.COMPLETED,
        )

    def test_process_job_records_start_and_completion_time(self):
        process_job(self.job.id)

        self.job.refresh_from_db()

        self.assertIsNotNone(self.job.started_at)
        self.assertIsNotNone(self.job.completed_at)
        self.assertLessEqual(
            self.job.started_at,
            self.job.completed_at,
        )

    def test_process_job_marks_job_failed_when_processing_fails(self):
        self.job.operation = "INVALID_OPERATION"
        self.job.save(update_fields=["operation"])

        process_job(self.job.id)

        self.job.refresh_from_db()

        self.assertEqual(
            self.job.status,
            Job.Status.FAILED,
        )
        self.assertIsNotNone(self.job.error_message)
        self.assertIsNotNone(self.job.completed_at)

    def test_process_job_profile_creates_result_file(self):
        self.job.operation = "PROFILE"
        self.job.save(update_fields=["operation"])

        process_job(self.job.id)

        self.job.refresh_from_db()

        self.assertEqual(
            self.job.status,
            Job.Status.COMPLETED,
        )
        self.assertTrue(self.job.result_file)

        result_content = self.job.result_file.read().decode("utf-8")

        self.assertIn('"rows": 2', result_content)
        self.assertIn('"columns": 2', result_content)


# ---------------------------------------------------------------------------
# IMAGE_PROCESSING → RESIZE Celery task tests
# ---------------------------------------------------------------------------

class ImageResizeTaskTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="imguser",
            password="testpass123",
        )

        self.resource = Resource.objects.create(
            name="Image Worker",
            resource_type=Resource.ResourceType.IMAGE_PROCESSING,
            capacity=1,
        )

        self.job = Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="RESIZE",
            parameters={"width": 50, "height": 40},
            input_file=SimpleUploadedFile(
                "test.png",
                _make_png_bytes(width=100, height=80),
                content_type="image/png",
            ),
        )

    def test_resize_job_reaches_completed_status(self):
        process_job(self.job.id)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.COMPLETED)

    def test_resize_job_saves_result_as_png_file(self):
        process_job(self.job.id)
        self.job.refresh_from_db()
        self.assertTrue(self.job.result_file)
        self.assertTrue(
            self.job.result_file.name.endswith(".png"),
            msg=f"Expected .png, got: {self.job.result_file.name}",
        )

    def test_resize_job_result_has_correct_pixel_dimensions(self):
        from io import BytesIO
        from PIL import Image

        process_job(self.job.id)
        self.job.refresh_from_db()

        img = Image.open(BytesIO(self.job.result_file.read()))
        self.assertEqual(img.size, (50, 40))

    def test_resize_job_records_timestamps(self):
        process_job(self.job.id)
        self.job.refresh_from_db()
        self.assertIsNotNone(self.job.started_at)
        self.assertIsNotNone(self.job.completed_at)
        self.assertLessEqual(self.job.started_at, self.job.completed_at)

    def test_resize_job_fails_on_invalid_parameters(self):
        self.job.parameters = {"width": 0, "height": 40}
        self.job.save(update_fields=["parameters"])

        process_job(self.job.id)
        self.job.refresh_from_db()

        self.assertEqual(self.job.status, Job.Status.FAILED)
        self.assertIn("positive", self.job.error_message)

    def test_resize_job_transitions_pending_to_completed(self):
        """Starts as PENDING; process_job must end with COMPLETED."""
        self.assertEqual(self.job.status, Job.Status.PENDING)
        process_job(self.job.id)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.COMPLETED)
        self.assertIsNotNone(self.job.started_at)
