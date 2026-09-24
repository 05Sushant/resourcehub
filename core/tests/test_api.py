from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from core.models import Resource, Reservation


class ReservationAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_reservation_list_requires_authentication(self):
        response = self.client.get("/api/reservations/")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_list_reservations(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/reservations/")

        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_reservation(self):
            resource = Resource.objects.create(
                name="Test CSV Worker",
                resource_type=Resource.ResourceType.CSV_ANALYTICS,
                capacity=1,
                status=Resource.Status.ACTIVE,
            )

            self.client.force_authenticate(user=self.user)

            response = self.client.post(
                "/api/reservations/",
                data={
                    "resource": resource.id,
                    "start_time": "2026-09-25T10:00:00Z",
                    "end_time": "2026-09-25T11:00:00Z",
                },
                format="json",
            )

            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data["resource"], resource.id)
            self.assertEqual(response.data["status"], "ACTIVE")

    def test_user_cannot_cancel_another_users_reservation(self):
            resource = Resource.objects.create(
                name="Test CSV Worker",
                resource_type=Resource.ResourceType.CSV_ANALYTICS,
                capacity=1,
                status=Resource.Status.ACTIVE,
            )

            reservation = Reservation.objects.create(
                user=self.user,
                resource=resource,
                start_time="2026-09-25T10:00:00Z",
                end_time="2026-09-25T11:00:00Z",
            )

            another_user = User.objects.create_user(
                username="anotheruser",
                password="testpass123",
            )

            self.client.force_authenticate(user=another_user)

            response = self.client.post(
                f"/api/reservations/{reservation.id}/cancel/"
            )

            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.data["detail"],
                "You cannot cancel this reservation.",
            )

    def test_user_can_cancel_own_reservation(self):
            resource = Resource.objects.create(
                name="Test CSV Worker",
                resource_type=Resource.ResourceType.CSV_ANALYTICS,
                capacity=1,
                status=Resource.Status.ACTIVE,
            )

            reservation = Reservation.objects.create(
                user=self.user,
                resource=resource,
                start_time="2026-09-25T10:00:00Z",
                end_time="2026-09-25T11:00:00Z",
            )

            self.client.force_authenticate(user=self.user)

            response = self.client.post(
                f"/api/reservations/{reservation.id}/cancel/"
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["status"], "CANCELLED")