from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_notifications(request):
    """사용자의 알림 목록 조회"""
    user = request.user
    
    # 읽지 않은 알림 개수
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    # 최근 알림 50개
    notifications = Notification.objects.filter(user=user)[:50]
    serializer = NotificationListSerializer(notifications, many=True)
    
    return Response({
        'success': True,
        'unread_count': unread_count,
        'notifications': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_as_read(request):
    """알림을 읽음으로 표시"""
    user = request.user
    
    # 모든 알림을 읽음으로 표시
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    
    return Response({
        'success': True,
        'message': '알림이 읽음으로 표시되었습니다.'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    """특정 알림을 읽음으로 표시"""
    user = request.user
    
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.save()
        
        return Response({
            'success': True,
            'message': '알림이 읽음으로 표시되었습니다.'
        }, status=status.HTTP_200_OK)
        
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': '알림을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


