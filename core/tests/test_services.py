import threading
from django.db import close_old_connections
from datetime import timedelta
from django.test import TransactionTestCase
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from core.models import Reservation, Resource
from core.services import cancel_reservation, create_reservation


class ReservationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.resource = Resource.objects.create(
            name="CSV Analytics Worker 01",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            description="Test CSV worker",
            capacity=1,
        )

    def test_active_resource_can_be_reserved(self):
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        reservation = create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.resource, self.resource)
        self.assertEqual(
            reservation.status,
            Reservation.Status.ACTIVE,
        )

    def test_reservation_end_time_must_be_after_start_time(self):
        start_time = timezone.now()
        end_time = start_time - timedelta(hours=1)

        with self.assertRaises(ValueError):
            create_reservation(
                user=self.user,
                resource=self.resource,
                start_time=start_time,
                end_time=end_time,
            )

    def test_disabled_resource_cannot_be_reserved(self):
        self.resource.status = Resource.Status.DISABLED
        self.resource.save()

        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        with self.assertRaises(ValueError):
            create_reservation(
                user=self.user,
                resource=self.resource,
                start_time=start_time,
                end_time=end_time,
            )

    def test_overlapping_reservation_is_rejected(self):
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        overlapping_start = start_time + timedelta(minutes=30)
        overlapping_end = overlapping_start + timedelta(hours=1)

        with self.assertRaises(ValueError):
            create_reservation(
                user=self.user,
                resource=self.resource,
                start_time=overlapping_start,
                end_time=overlapping_end,
            )

    def test_adjacent_reservation_is_allowed(self):
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        next_start = end_time
        next_end = next_start + timedelta(hours=1)

        reservation = create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=next_start,
            end_time=next_end,
        )

        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.start_time, next_start)
        self.assertEqual(reservation.end_time, next_end)

    def test_reservations_are_allowed_until_capacity_is_reached(self):
        self.resource.capacity = 2
        self.resource.save()

        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        second_user = User.objects.create_user(
            username="seconduser",
            password="testpass123",
        )

        second_reservation = create_reservation(
            user=second_user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        self.assertIsNotNone(second_reservation)

    def test_reservation_is_rejected_when_capacity_is_full(self):
        self.resource.capacity = 2
        self.resource.save()

        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        second_user = User.objects.create_user(
            username="seconduser",
            password="testpass123",
        )

        create_reservation(
            user=second_user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        third_user = User.objects.create_user(
            username="thirduser",
            password="testpass123",
        )

        with self.assertRaises(ValueError):
            create_reservation(
                user=third_user,
                resource=self.resource,
                start_time=start_time,
                end_time=end_time,
            )

    def test_cancelled_reservation_does_not_block_new_reservation(self):
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        reservation = create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        reservation.status = Reservation.Status.CANCELLED
        reservation.save()

        new_reservation = create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        self.assertIsNotNone(new_reservation)
        self.assertEqual(
            new_reservation.status,
            Reservation.Status.ACTIVE,
        )

    def test_user_cannot_cancel_another_users_reservation(self):
        reservation = create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
        )

        another_user = User.objects.create_user(
            username="anotheruser",
            password="testpass123",
        )

        with self.assertRaises(PermissionError):
            cancel_reservation(
                user=another_user,
                reservation=reservation,
            )

    def test_user_can_cancel_own_reservation(self):
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        reservation = create_reservation(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
        )

        cancelled_reservation = cancel_reservation(
            user=self.user,
            reservation=reservation,
        )

        self.assertEqual(
            cancelled_reservation.status,
            Reservation.Status.CANCELLED,
        )

class ReservationConcurrencyTest(TransactionTestCase):

    reset_sequences = True

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="testpass123",
        )

        self.user2 = User.objects.create_user(
            username="user2",
            password="testpass123",
        )

        self.resource = Resource.objects.create(
            name="Concurrent Worker",
            resource_type=Resource.ResourceType.CSV_ANALYTICS,
            capacity=1,
        )

    def test_concurrent_reservations_do_not_both_succeed(self):
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        results = []

        def reserve(user):
            close_old_connections()

            try:
                reservation = create_reservation(
                    user=user,
                    resource=self.resource,
                    start_time=start_time,
                    end_time=end_time,
                )

                results.append(("success", reservation.id))

            except ValueError:
                results.append(("rejected", None))

            finally:
                close_old_connections()

        thread1 = threading.Thread(
            target=reserve,
            args=(self.user1,),
        )

        thread2 = threading.Thread(
            target=reserve,
            args=(self.user2,),
        )

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        successes = [
            result
            for result in results
            if result[0] == "success"
        ]

        self.assertEqual(len(successes), 1)