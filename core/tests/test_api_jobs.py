from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from unittest.mock import patch

from core.models import Resource, Job

class JobAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass")
        self.resource_profile = Resource.objects.create(
            name="Profile Resource",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            status=Resource.Status.ACTIVE
        )
        self.resource_resize = Resource.objects.create(
            name="Resize Resource",
            resource_type=Resource.ResourceType.IMAGE_PROCESSING,
            status=Resource.Status.ACTIVE
        )
        self.resource_inactive = Resource.objects.create(
            name="Inactive Resource",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            status=Resource.Status.DISABLED
        )

    def test_job_list_requires_authentication(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_list_own_jobs(self):
        Job.objects.create(user=self.user, resource=self.resource_profile, operation="PROFILE")
        Job.objects.create(user=self.other_user, resource=self.resource_profile, operation="PROFILE")
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @patch('core.tasks.process_job.delay')
    def test_valid_profile_job_creation(self, mock_delay):
        mock_delay.return_value.id = "fake-task-id"
        self.client.force_authenticate(user=self.user)
        file_obj = SimpleUploadedFile("test.csv", b"col1,col2\n1,2", content_type="text/csv")
        response = self.client.post('/api/jobs/', {
            'resource': self.resource_profile.id,
            'operation': 'PROFILE',
            'input_file': file_obj,
        }, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertTrue(mock_delay.called)

    @patch('core.tasks.process_job.delay')
    def test_valid_resize_job_creation(self, mock_delay):
        mock_delay.return_value.id = "fake-task-id"
        self.client.force_authenticate(user=self.user)
        file_obj = SimpleUploadedFile("img.png", b"fakeimgbytes", content_type="image/png")
        response = self.client.post('/api/jobs/', {
            'resource': self.resource_resize.id,
            'operation': 'RESIZE',
            'parameters': '{"width": 800, "height": 600}',
            'input_file': file_obj,
        }, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'PENDING')

    def test_inactive_resource_rejected(self):
        self.client.force_authenticate(user=self.user)
        file_obj = SimpleUploadedFile("test.csv", b"col1,col2\n1,2", content_type="text/csv")
        response = self.client.post('/api/jobs/', {
            'resource': self.resource_inactive.id,
            'operation': 'PROFILE',
            'input_file': file_obj,
        }, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_unsupported_operation_rejected(self):
        self.client.force_authenticate(user=self.user)
        file_obj = SimpleUploadedFile("test.csv", b"col1,col2\n1,2", content_type="text/csv")
        response = self.client.post('/api/jobs/', {
            'resource': self.resource_profile.id,
            'operation': 'RESIZE',
            'input_file': file_obj,
        }, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_invalid_parameters_rejected(self):
        self.client.force_authenticate(user=self.user)
        file_obj = SimpleUploadedFile("img.png", b"fakeimgbytes", content_type="image/png")
        response = self.client.post('/api/jobs/', {
            'resource': self.resource_resize.id,
            'operation': 'RESIZE',
            'parameters': '{"width": -100, "height": 600}',
            'input_file': file_obj,
        }, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_missing_file_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/jobs/', {
            'resource': self.resource_profile.id,
            'operation': 'PROFILE',
        }, format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_job_detail_owner_can_retrieve(self):
        job = Job.objects.create(user=self.user, resource=self.resource_profile, operation="PROFILE")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/jobs/{job.id}/')
        self.assertEqual(response.status_code, 200)

    def test_job_detail_another_user_gets_404(self):
        job = Job.objects.create(user=self.other_user, resource=self.resource_profile, operation="PROFILE")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/jobs/{job.id}/')
        self.assertEqual(response.status_code, 404)

    def test_job_detail_unauthenticated_gets_401(self):
        job = Job.objects.create(user=self.user, resource=self.resource_profile, operation="PROFILE")
        response = self.client.get(f'/api/jobs/{job.id}/')
        self.assertEqual(response.status_code, 401)
