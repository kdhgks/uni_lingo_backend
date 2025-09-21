# UniLingo 모니터링 및 알람 설정

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests

logger = logging.getLogger(__name__)

class MonitoringService:
    """모니터링 서비스"""
    
    @staticmethod
    def check_system_health():
        """시스템 헬스체크"""
        health_checks = {
            'database': False,
            'redis': False,
            'websocket': False,
            'storage': False
        }
        
        try:
            # 데이터베이스 체크
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_checks['database'] = True
        except Exception as e:
            logger.error(f"데이터베이스 헬스체크 실패: {e}")
        
        try:
            # Redis 체크
            from django.core.cache import cache
            cache.set('health_check', 'test', 10)
            result = cache.get('health_check')
            if result == 'test':
                cache.delete('health_check')
                health_checks['redis'] = True
        except Exception as e:
            logger.error(f"Redis 헬스체크 실패: {e}")
        
        try:
            # WebSocket 체크 (간단한 연결 테스트)
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 8001))  # Uvicorn 포트
            sock.close()
            health_checks['websocket'] = result == 0
        except Exception as e:
            logger.error(f"WebSocket 헬스체크 실패: {e}")
        
        try:
            # 스토리지 체크 (S3 또는 로컬)
            if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
                import boto3
                s3 = boto3.client('s3')
                s3.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
                health_checks['storage'] = True
            else:
                # 로컬 스토리지 체크
                import os
                if os.path.exists(settings.MEDIA_ROOT):
                    health_checks['storage'] = True
        except Exception as e:
            logger.error(f"스토리지 헬스체크 실패: {e}")
        
        return health_checks
    
    @staticmethod
    def send_alert(subject, message, severity='warning'):
        """알림 전송"""
        try:
            # Slack 웹훅 (선택사항)
            slack_webhook = getattr(settings, 'SLACK_WEBHOOK_URL', None)
            if slack_webhook:
                slack_data = {
                    'text': f'🚨 *{severity.upper()}*: {subject}',
                    'attachments': [
                        {
                            'color': 'danger' if severity == 'critical' else 'warning',
                            'fields': [
                                {
                                    'title': '메시지',
                                    'value': message,
                                    'short': False
                                },
                                {
                                    'title': '시간',
                                    'value': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'short': True
                                },
                                {
                                    'title': '서버',
                                    'value': getattr(settings, 'SERVER_NAME', 'Unknown'),
                                    'short': True
                                }
                            ]
                        }
                    ]
                }
                
                response = requests.post(slack_webhook, json=slack_data, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Slack 알림 전송 성공: {subject}")
                else:
                    logger.error(f"Slack 알림 전송 실패: {response.status_code}")
            
            # 이메일 알림 (선택사항)
            admin_email = getattr(settings, 'ADMIN_EMAIL', None)
            if admin_email:
                send_mail(
                    subject=f'[UniLingo] {subject}',
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@unilingo.com'),
                    recipient_list=[admin_email],
                    fail_silently=False
                )
                logger.info(f"이메일 알림 전송 성공: {subject}")
                
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
    
    @staticmethod
    def check_performance_metrics():
        """성능 메트릭 체크"""
        alerts = []
        
        try:
            # 데이터베이스 연결 수 체크
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                db_connections = cursor.fetchone()[0]
                
                if db_connections > 80:  # 80% 이상
                    alerts.append({
                        'type': 'database_connections',
                        'message': f'데이터베이스 연결 수 높음: {db_connections}',
                        'severity': 'warning'
                    })
            
            # Redis 메모리 사용량 체크
            from django.core.cache import cache
            try:
                import redis
                redis_client = redis.Redis.from_url(getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'))
                info = redis_client.info('memory')
                memory_usage = info.get('used_memory', 0)
                memory_peak = info.get('used_memory_peak', 0)
                
                if memory_usage > memory_peak * 0.8:  # 80% 이상
                    alerts.append({
                        'type': 'redis_memory',
                        'message': f'Redis 메모리 사용량 높음: {memory_usage} bytes',
                        'severity': 'warning'
                    })
            except Exception as e:
                logger.warning(f"Redis 메트릭 체크 실패: {e}")
            
            # 디스크 사용량 체크
            import shutil
            disk_usage = shutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            if disk_percent > 85:  # 85% 이상
                alerts.append({
                    'type': 'disk_usage',
                    'message': f'디스크 사용량 높음: {disk_percent:.1f}%',
                    'severity': 'critical'
                })
            
        except Exception as e:
            logger.error(f"성능 메트릭 체크 실패: {e}")
            alerts.append({
                'type': 'monitoring_error',
                'message': f'모니터링 체크 실패: {e}',
                'severity': 'critical'
            })
        
        return alerts
    
    @staticmethod
    def run_health_monitoring():
        """헬스 모니터링 실행"""
        health_checks = MonitoringService.check_system_health()
        performance_alerts = MonitoringService.check_performance_metrics()
        
        # 헬스체크 실패 알림
        failed_checks = [service for service, status in health_checks.items() if not status]
        if failed_checks:
            MonitoringService.send_alert(
                subject='시스템 헬스체크 실패',
                message=f'실패한 서비스: {", ".join(failed_checks)}',
                severity='critical'
            )
        
        # 성능 알림
        for alert in performance_alerts:
            MonitoringService.send_alert(
                subject=f'성능 경고: {alert["type"]}',
                message=alert['message'],
                severity=alert['severity']
            )
        
        return {
            'health_checks': health_checks,
            'alerts': performance_alerts
        }

# 관리 명령어용
def run_monitoring():
    """모니터링 실행 (Django 관리 명령어에서 호출)"""
    return MonitoringService.run_health_monitoring()


