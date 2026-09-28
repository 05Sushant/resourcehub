from django.db import transaction

from core.models import Job, Reservation, Resource
from core.operations import validate_operation


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

def validate_parameters(operation, parameters):
    if operation == "RESIZE":
        return (
            isinstance(parameters.get("width"), int)
            and isinstance(parameters.get("height"), int)
            and parameters["width"] > 0
            and parameters["height"] > 0
        )

    if operation == "VALIDATE":
        columns = parameters.get("columns")

        return (
            isinstance(columns, dict)
            and len(columns) > 0
            and all(
                column_type in {"string", "integer", "float"}
                for column_type in columns.values()
            )
        )

    return parameters == {}


def create_job(
    user,
    resource,
    operation,
    parameters,
    input_file,
):
    if resource.status != resource.Status.ACTIVE:
        raise ValueError("Resource is not active.")

    if not validate_operation(
        resource.resource_type,
        operation,
    ):
        raise ValueError(
            "Operation is not supported by this resource."
        )

    if not validate_parameters(
        operation,
        parameters,
    ):
        raise ValueError(
            "Invalid parameters for this operation."
        )

    return Job.objects.create(
        user=user,
        resource=resource,
        operation=operation,
        parameters=parameters,
        input_file=input_file,
    )
