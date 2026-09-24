from rest_framework import serializers

from core.models import Resource, Reservation


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "resource_type",
            "description",
            "capacity",
            "status",
            "created_at",
            "updated_at",
        ]

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            "id",
            "resource",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]