from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Resource, Reservation, Job
from .serializers import ResourceSerializer, ReservationSerializer, UserRegistrationSerializer, JobSerializer
from .services import cancel_reservation, create_reservation, create_job
from django.shortcuts import get_object_or_404
from .tasks import process_job


class ResourceListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)

class ReservationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservations = Reservation.objects.filter(
            user=request.user
        )

        serializer = ReservationSerializer(
            reservations,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = ReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reservation = create_reservation(
                user=request.user,
                resource=serializer.validated_data["resource"],
                start_time=serializer.validated_data["start_time"],
                end_time=serializer.validated_data["end_time"],
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=400,
            )
        response_serializer = ReservationSerializer(reservation)
        return Response(response_serializer.data,status=201)

class ReservationCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, pk=reservation_id)
        try:
            reservation = cancel_reservation(
                user=request.user,
                reservation=reservation,
            )
        except PermissionError as error:
            return Response(
                {"detail":str(error)},
                status=403
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=400,
            )

        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            status=201,
        )

class JobListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobs = Job.objects.filter(user=request.user).order_by('-created_at')
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            job = create_job(
                user=request.user,
                resource=serializer.validated_data['resource'],
                operation=serializer.validated_data['operation'],
                parameters=serializer.validated_data.get('parameters', {}),
                input_file=serializer.validated_data['input_file'],
            )
        except ValueError as error:
            return Response({'detail': str(error)}, status=400)

        try:
            task = process_job.delay(job.id)
            job.celery_task_id = task.id
            job.save(update_fields=["celery_task_id"])

        except Exception:
            job.status = Job.Status.FAILED
            job.error_message = "Failed to submit task to Celery."
            job.save(update_fields=["status", "error_message"])

            return Response(
                {"detail": "Failed to submit job for processing."},
                status=500,
            )

        response_serializer = JobSerializer(job)
        return Response(response_serializer.data, status=201)

class JobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_object_or_404(Job, pk=job_id)
        if job.user != request.user:
            return Response({'detail': 'Not found.'}, status=404)

        serializer = JobSerializer(job)
        return Response(serializer.data)
