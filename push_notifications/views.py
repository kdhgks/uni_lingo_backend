from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import DeviceToken
from .services import PushNotificationService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device_token(request):
    """디바이스 토큰 등록 (FCM/APNs)"""
    try:
        device_type = request.data.get('device_type')  # 'ios', 'android'
        token = request.data.get('token')
        device_id = request.data.get('device_id')
        
        if not all([device_type, token, device_id]):
            return Response({
                'error': 'device_type, token, device_id가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 기존 토큰 업데이트 또는 새로 생성
        device_token, created = DeviceToken.objects.update_or_create(
            user=request.user,
            device_id=device_id,
            defaults={
                'device_type': device_type,
                'token': token,
                'is_active': True
            }
        )
        
        logger.info(f"디바이스 토큰 {'등록' if created else '업데이트'}: {request.user.username}")
        
        return Response({
            'message': '디바이스 토큰이 등록되었습니다.',
            'created': created
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"디바이스 토큰 등록 오류: {e}")
        return Response({
            'error': '디바이스 토큰 등록에 실패했습니다.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unregister_device_token(request):
    """디바이스 토큰 삭제"""
    try:
        device_id = request.data.get('device_id')
        
        if not device_id:
            return Response({
                'error': 'device_id가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        DeviceToken.objects.filter(
            user=request.user,
            device_id=device_id
        ).delete()
        
        logger.info(f"디바이스 토큰 삭제: {request.user.username}")
        
        return Response({
            'message': '디바이스 토큰이 삭제되었습니다.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"디바이스 토큰 삭제 오류: {e}")
        return Response({
            'error': '디바이스 토큰 삭제에 실패했습니다.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_notification(request):
    """테스트 푸시 알림 전송"""
    try:
        push_service = PushNotificationService()
        
        # 사용자의 모든 활성 디바이스에 테스트 알림 전송
        devices = DeviceToken.objects.filter(
            user=request.user,
            is_active=True
        )
        
        if not devices.exists():
            return Response({
                'error': '등록된 디바이스가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success_count = 0
        for device in devices:
            try:
                result = push_service.send_notification(
                    device_token=device.token,
                    title="UniLingo 테스트",
                    body="푸시 알림 테스트입니다.",
                    data={
                        'type': 'test',
                        'room_id': '0'
                    }
                )
                if result:
                    success_count += 1
            except Exception as e:
                logger.error(f"푸시 알림 전송 실패 ({device.device_id}): {e}")
        
        return Response({
            'message': f'{success_count}개 디바이스에 테스트 알림을 전송했습니다.',
            'success_count': success_count,
            'total_devices': devices.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"테스트 알림 전송 오류: {e}")
        return Response({
            'error': '테스트 알림 전송에 실패했습니다.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


