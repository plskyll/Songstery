from rest_framework import serializers

from core.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "type", "type_display", "is_read", "created_at", "object_id")
        read_only_fields = fields
