from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """알림 시리얼라이저"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'is_read', 
            'created_at', 'related_user_id', 'related_request_id'
        ]
        read_only_fields = ['id', 'created_at']

class NotificationListSerializer(serializers.ModelSerializer):
    """알림 목록용 시리얼라이저"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'is_read', 
            'created_at', 'related_user_id'
        ]


