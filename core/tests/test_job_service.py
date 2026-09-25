from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from core.models import Job, Resource
from core.services import create_job, validate_parameters

class JobParameterValidationTest(TestCase):

    def test_resize_accepts_valid_parameters(self):
        self.assertTrue(
            validate_parameters(
                "RESIZE",
                {
                    "width": 800,
                    "height": 600,
                },
            )
        )

    def test_resize_rejects_missing_width(self):
        self.assertFalse(
            validate_parameters(
                "RESIZE",
                {
                    "height": 600,
                },
            )
        )

    def test_resize_rejects_missing_height(self):
        self.assertFalse(
            validate_parameters(
                "RESIZE",
                {
                    "width": 800,
                },
            )
        )

    def test_resize_rejects_zero_width(self):
        self.assertFalse(
            validate_parameters(
                "RESIZE",
                {
                    "width": 0,
                    "height": 600,
                },
            )
        )

    def test_resize_rejects_negative_height(self):
        self.assertFalse(
            validate_parameters(
                "RESIZE",
                {
                    "width": 800,
                    "height": -1,
                },
            )
        )

    def test_analyze_accepts_empty_parameters(self):
        self.assertTrue(
            validate_parameters("ANALYZE", {})
        )

    def test_profile_accepts_empty_parameters(self):
        self.assertTrue(
            validate_parameters("PROFILE", {})
        )

    def test_grayscale_rejects_unexpected_parameters(self):
        self.assertFalse(
            validate_parameters(
                "GRAYSCALE",
                {"width": 800},
            )
        )

    def test_create_job_creates_pending_job(self):
        user = User.objects.create_user(
            username="jobuser",
            password="testpass123",
        )

        resource = Resource.objects.create(
            name="CSV Worker",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            capacity=1,
        )

        input_file = SimpleUploadedFile(
            "sales.csv",
            b"name,amount\nAlice,100\nBob,200\n",
            content_type="text/csv",
        )

        job = create_job(
            user=user,
            resource=resource,
            operation="ANALYZE",
            parameters={},
            input_file=input_file,
        )

        self.assertEqual(job.user, user)
        self.assertEqual(job.resource, resource)
        self.assertEqual(job.operation, "ANALYZE")
        self.assertEqual(job.parameters, {})
        self.assertEqual(job.status, Job.Status.PENDING)

class JobCreationTest(TestCase):

    def test_create_job_rejects_inactive_resource(self):
        user = User.objects.create_user(
            username="jobuser",
            password="testpass123",
        )

        resource = Resource.objects.create(
            name="CSV Worker",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            capacity=1,
            status=Resource.Status.DISABLED,
        )

        input_file = SimpleUploadedFile(
            "sales.csv",
            b"name,amount\nAlice,100\n",
            content_type="text/csv",
        )

        with self.assertRaisesMessage(
            ValueError,
            "Resource is not active.",
        ):
            create_job(
                user=user,
                resource=resource,
                operation="ANALYZE",
                parameters={},
                input_file=input_file,
            )

    def test_create_job_rejects_unsupported_operation(self):
        user = User.objects.create_user(
            username="jobuser",
            password="testpass123",
        )

        resource = Resource.objects.create(
            name="CSV Worker",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            capacity=1,
        )

        input_file = SimpleUploadedFile(
            "sales.csv",
            b"name,amount\nAlice,100\n",
            content_type="text/csv",
        )

        with self.assertRaisesMessage(
            ValueError,
            "Operation is not supported by this resource.",
        ):
            create_job(
                user=user,
                resource=resource,
                operation="GRAYSCALE",
                parameters={},
                input_file=input_file,
            )

    def test_create_job_rejects_invalid_parameters(self):
        user = User.objects.create_user(
            username="jobuser",
            password="testpass123",
        )

        resource = Resource.objects.create(
            name="Image Worker",
            resource_type=Resource.ResourceType.IMAGE_PROCESSING,
            capacity=1,
        )

        input_file = SimpleUploadedFile(
            "photo.jpg",
            b"fake-image-data",
            content_type="image/jpeg",
        )

        with self.assertRaisesMessage(
            ValueError,
            "Invalid parameters for this operation.",
        ):
            create_job(
                user=user,
                resource=resource,
                operation="RESIZE",
                parameters={
                    "width": 0,
                    "height": 600,
                },
                input_file=input_file,
            )