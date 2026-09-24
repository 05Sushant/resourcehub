from django.db.migrations import serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Resource, Reservation
from .serializers import ResourceSerializer, ReservationSerializer
from .services import cancel_reservation, create_reservation
from django.shortcuts import get_object_or_404


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
    