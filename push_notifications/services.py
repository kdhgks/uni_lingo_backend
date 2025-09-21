import os
import json
import logging
from typing import Dict, Any, Optional
from firebase_admin import messaging, credentials, initialize_app
from django.conf import settings
from .models import DeviceToken, NotificationLog

logger = logging.getLogger(__name__)

class PushNotificationService:
    """푸시 알림 서비스 (FCM)"""
    
    def __init__(self):
        self.fcm_initialized = False
        self._initialize_fcm()
    
    def _initialize_fcm(self):
        """FCM 초기화"""
        try:
            # Firebase Admin SDK 초기화
            if not self.fcm_initialized:
                # 서비스 계정 키 파일 또는 환경변수에서 인증 정보 로드
                service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
                
                if service_account_path and os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                else:
                    # 환경변수에서 직접 인증 정보 로드
                    firebase_config = {
                        "type": "service_account",
                        "project_id": os.environ.get('FCM_PROJECT_ID'),
                        "private_key_id": os.environ.get('FCM_PRIVATE_KEY_ID'),
                        "private_key": os.environ.get('FCM_PRIVATE_KEY', '').replace('\\n', '\n'),
                        "client_email": os.environ.get('FCM_CLIENT_EMAIL'),
                        "client_id": os.environ.get('FCM_CLIENT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    cred = credentials.Certificate(firebase_config)
                
                initialize_app(cred)
                self.fcm_initialized = True
                logger.info("FCM 초기화 완료")
                
        except Exception as e:
            logger.error(f"FCM 초기화 실패: {e}")
            self.fcm_initialized = False
    
    def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> bool:
        """단일 디바이스에 푸시 알림 전송"""
        if not self.fcm_initialized:
            logger.error("FCM이 초기화되지 않았습니다.")
            return False
        
        try:
            # 알림 데이터 준비
            notification_data = {
                'title': title,
                'body': body,
            }
            
            # 추가 데이터가 있으면 포함
            if data:
                notification_data.update(data)
            
            # FCM 메시지 생성
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=notification_data,
                token=device_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        click_action='FLUTTER_NOTIFICATION_CLICK'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body
                            )
                        )
                    )
                )
            )
            
            # 알림 전송
            response = messaging.send(message)
            logger.info(f"푸시 알림 전송 성공: {response}")
            
            # 로그 저장
            if user_id:
                user = User.objects.get(id=user_id)
                device = DeviceToken.objects.filter(
                    user=user,
                    token=device_token
                ).first()
                
                NotificationLog.objects.create(
                    user=user,
                    device_token=device,
                    title=title,
                    body=body,
                    data=data or {},
                    status='sent',
                    sent_at=timezone.now()
                )
            
            return True
            
        except messaging.UnregisteredError:
            logger.warning(f"등록되지 않은 토큰: {device_token}")
            # 비활성 토큰으로 표시
            DeviceToken.objects.filter(token=device_token).update(is_active=False)
            return False
            
        except Exception as e:
            logger.error(f"푸시 알림 전송 실패: {e}")
            
            # 로그 저장 (실패)
            if user_id:
                user = User.objects.get(id=user_id)
                device = DeviceToken.objects.filter(
                    user=user,
                    token=device_token
                ).first()
                
                NotificationLog.objects.create(
                    user=user,
                    device_token=device,
                    title=title,
                    body=body,
                    data=data or {},
                    status='failed',
                    error_message=str(e)
                )
            
            return False
    
    def send_multicast_notification(
        self,
        device_tokens: list,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """여러 디바이스에 푸시 알림 전송"""
        if not self.fcm_initialized:
            logger.error("FCM이 초기화되지 않았습니다.")
            return {'success': 0, 'failure': len(device_tokens)}
        
        try:
            # 알림 데이터 준비
            notification_data = {
                'title': title,
                'body': body,
            }
            
            if data:
                notification_data.update(data)
            
            # 멀티캐스트 메시지 생성
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=notification_data,
                tokens=device_tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        click_action='FLUTTER_NOTIFICATION_CLICK'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body
                            )
                        )
                    )
                )
            )
            
            # 멀티캐스트 전송
            response = messaging.send_multicast(message)
            logger.info(f"멀티캐스트 푸시 알림 전송: 성공 {response.success_count}, 실패 {response.failure_count}")
            
            # 실패한 토큰들 비활성화
            if response.failure_count > 0:
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        if resp.exception.code == 'UNREGISTERED':
                            DeviceToken.objects.filter(
                                token=device_tokens[idx]
                            ).update(is_active=False)
            
            return {
                'success': response.success_count,
                'failure': response.failure_count
            }
            
        except Exception as e:
            logger.error(f"멀티캐스트 푸시 알림 전송 실패: {e}")
            return {'success': 0, 'failure': len(device_tokens)}
    
    def send_to_user(
        self,
        user,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """특정 사용자의 모든 활성 디바이스에 푸시 알림 전송"""
        device_tokens = DeviceToken.objects.filter(
            user=user,
            is_active=True
        ).values_list('token', flat=True)
        
        if not device_tokens:
            logger.warning(f"사용자 {user.username}에게 활성 디바이스가 없습니다.")
            return False
        
        result = self.send_multicast_notification(
            device_tokens=list(device_tokens),
            title=title,
            body=body,
            data=data
        )
        
        return result['success'] > 0

# 전역 서비스 인스턴스
push_service = PushNotificationService()


