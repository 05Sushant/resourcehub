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


# ---------------------------------------------------------------------------
# User registration tests
# ---------------------------------------------------------------------------

class UserRegistrationAPITest(APITestCase):

    URL = "/api/register/"

    VALID_PAYLOAD = {
        "username": "sushant",
        "email": "sushant@example.com",
        "password": "securepassword",
        "password_confirm": "securepassword",
    }

    def test_successful_registration_returns_201(self):
        response = self.client.post(self.URL, data=self.VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)

    def test_successful_registration_returns_id_username_email(self):
        response = self.client.post(self.URL, data=self.VALID_PAYLOAD, format="json")
        self.assertIn("id", response.data)
        self.assertEqual(response.data["username"], "sushant")
        self.assertEqual(response.data["email"], "sushant@example.com")

    def test_successful_registration_does_not_return_password(self):
        response = self.client.post(self.URL, data=self.VALID_PAYLOAD, format="json")
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)

    def test_successful_registration_creates_user_in_db(self):
        self.client.post(self.URL, data=self.VALID_PAYLOAD, format="json")
        self.assertTrue(User.objects.filter(username="sushant").exists())

    def test_password_is_hashed_in_db(self):
        self.client.post(self.URL, data=self.VALID_PAYLOAD, format="json")
        user = User.objects.get(username="sushant")
        self.assertNotEqual(user.password, "securepassword")
        self.assertTrue(user.check_password("securepassword"))

    def test_duplicate_username_returns_400(self):
        User.objects.create_user(username="sushant", email="x@x.com", password="p")
        response = self.client.post(self.URL, data=self.VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_password_mismatch_returns_400(self):
        payload = {**self.VALID_PAYLOAD, "password_confirm": "wrong"}
        response = self.client.post(self.URL, data=payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password_confirm", response.data)

    def test_missing_username_returns_400(self):
        payload = {k: v for k, v in self.VALID_PAYLOAD.items() if k != "username"}
        response = self.client.post(self.URL, data=payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_missing_email_returns_400(self):
        payload = {k: v for k, v in self.VALID_PAYLOAD.items() if k != "email"}
        response = self.client.post(self.URL, data=payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_missing_password_returns_400(self):
        payload = {k: v for k, v in self.VALID_PAYLOAD.items() if k != "password"}
        response = self.client.post(self.URL, data=payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_invalid_email_format_returns_400(self):
        payload = {**self.VALID_PAYLOAD, "email": "not-an-email"}
        response = self.client.post(self.URL, data=payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_unauthenticated_access_is_allowed(self):
        """No credentials — must get 201, not 401."""
        response = self.client.post(self.URL, data=self.VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)
