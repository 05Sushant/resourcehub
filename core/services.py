from django.db import transaction

from core.models import Reservation, Resource


@transaction.atomic
def create_reservation(user, resource, start_time, end_time):
    if start_time >= end_time:
        raise ValueError("End time must be after start time.")

    resource = Resource.objects.select_for_update().get(
        pk=resource.pk
    )

    if resource.status != resource.Status.ACTIVE:
        raise ValueError("Resource is not active.")

    overlapping_reservations = Reservation.objects.filter(
        resource=resource,
        status=Reservation.Status.ACTIVE,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).count()

    if overlapping_reservations >= resource.capacity:
        raise ValueError(
            "Resource capacity is full for this time."
        )

    return Reservation.objects.create(
        user=user,
        resource=resource,
        start_time=start_time,
        end_time=end_time,
    )

@transaction.atomic
def cancel_reservation(user, reservation):
    if reservation.user != user:
        raise PermissionError("You cannot cancel this reservation.")

    if reservation.status != Reservation.Status.ACTIVE:
        raise ValueError("Only active reservations can be cancelled.")

    reservation.status = Reservation.Status.CANCELLED
    reservation.save(update_fields=["status"])

    return reservation