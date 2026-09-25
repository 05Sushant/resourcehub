from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.db.models.deletion import ProtectedError
from core.models import Job, Resource


class JobModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.resource = Resource.objects.create(
            name="CSV Analytics Worker",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            description="Test CSV resource",
            capacity=1,
        )

        self.input_file = SimpleUploadedFile(
            "test.csv",
            b"name,age\nAlice,25\nBob,30\n",
            content_type="text/csv",
        )

    def test_new_job_defaults_to_pending(self):
        job = Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="ANALYZE",
            input_file=self.input_file,
        )

        self.assertEqual(
            job.status,
            Job.Status.PENDING,
        )

    def test_new_job_has_empty_parameters(self):
        job = Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="ANALYZE",
            input_file=self.input_file,
        )

        self.assertEqual(job.parameters, {})

    def test_new_job_has_no_started_or_completed_time(self):
        job = Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="ANALYZE",
            input_file=self.input_file,
        )

        self.assertIsNone(job.started_at)
        self.assertIsNone(job.completed_at)

    def test_new_job_has_no_result_or_celery_task(self):
        job = Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="ANALYZE",
            input_file=self.input_file,
        )

        self.assertFalse(job.result_file)
        self.assertEqual(job.celery_task_id, "")

    def test_job_stores_operation_and_parameters(self):
        job = Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="RESIZE",
            parameters={
                "width": 800,
                "height": 600,
            },
            input_file=self.input_file,
        )

        self.assertEqual(job.user, self.user)
        self.assertEqual(job.resource, self.resource)
        self.assertEqual(job.operation, "RESIZE")
        self.assertEqual(
            job.parameters,
            {
                "width": 800,
                "height": 600,
            },
        )

    def test_resource_cannot_be_deleted_if_job_references_it(self):
        Job.objects.create(
            user=self.user,
            resource=self.resource,
            operation="ANALYZE",
            input_file=self.input_file,
        )

        with self.assertRaises(ProtectedError):
            self.resource.delete()