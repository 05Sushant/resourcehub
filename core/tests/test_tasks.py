from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.models import Job, Resource
from core.tasks import process_job


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