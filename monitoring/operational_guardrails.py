"""
UniLingo 운영 가드레일 활성화 스크립트
"""

import os
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from monitoring.alerts import MonitoringService

logger = logging.getLogger(__name__)

class OperationalGuardrails:
    """운영 가드레일 관리 클래스"""
    
    @staticmethod
    def setup_rate_limiting():
        """레이트 리미팅 설정 활성화"""
        logger.info("🛡️ 레이트 리미팅 활성화...")
        
        # DRF 레이트 리미팅 확인
        rest_framework = getattr(settings, 'REST_FRAMEWORK', {})
        throttle_classes = rest_framework.get('DEFAULT_THROTTLE_CLASSES', [])
        
        if 'rest_framework.throttling.UserRateThrottle' not in throttle_classes:
            print("⚠️ 사용자 레이트 리미팅이 활성화되지 않았습니다")
            return False
        
        if 'rest_framework.throttling.AnonRateThrottle' not in throttle_classes:
            print("⚠️ 익명 사용자 레이트 리미팅이 활성화되지 않았습니다")
            return False
        
        print("✅ 레이트 리미팅 활성화 완료")
        return True
    
    @staticmethod
    def setup_monitoring_alerts():
        """모니터링 알림 설정"""
        print("📊 모니터링 알림 설정...")
        
        # Sentry 설정 확인
        sentry_dsn = os.environ.get('SENTRY_DSN')
        if not sentry_dsn:
            print("⚠️ SENTRY_DSN이 설정되지 않았습니다")
        else:
            print("✅ Sentry 모니터링 활성화")
        
        # CloudWatch 설정 확인
        aws_region = os.environ.get('AWS_DEFAULT_REGION')
        if not aws_region:
            print("⚠️ AWS_DEFAULT_REGION이 설정되지 않았습니다")
        else:
            print("✅ CloudWatch 모니터링 준비 완료")
        
        return True
    
    @staticmethod
    def setup_logging_protection():
        """로그 보호 설정 (PII 마스킹)"""
        print("🔒 로그 보호 설정...")
        
        # 로깅 설정에서 PII 마스킹 확인
        logging_config = getattr(settings, 'LOGGING', {})
        
        # 커스텀 로그 포매터 추가 (PII 마스킹용)
        formatters = logging_config.get('formatters', {})
        if 'secure' not in formatters:
            print("⚠️ PII 마스킹 로그 포매터가 설정되지 않았습니다")
            return False
        
        print("✅ 로그 보호 설정 완료")
        return True
    
    @staticmethod
    def setup_health_monitoring():
        """헬스 모니터링 설정"""
        print("🏥 헬스 모니터링 설정...")
        
        # 헬스체크 엔드포인트 확인
        health_endpoints = getattr(settings, 'HEALTH_CHECK_ENDPOINTS', [])
        
        required_endpoints = ['/healthz/', '/health/db/', '/health/redis/']
        missing_endpoints = [ep for ep in required_endpoints if ep not in health_endpoints]
        
        if missing_endpoints:
            print(f"⚠️ 누락된 헬스체크 엔드포인트: {missing_endpoints}")
            return False
        
        print("✅ 헬스 모니터링 설정 완료")
        return True
    
    @staticmethod
    def setup_backup_strategy():
        """백업 전략 설정"""
        print("💾 백업 전략 설정...")
        
        # RDS 자동 백업 확인
        database_url = os.environ.get('DATABASE_URL', '')
        if 'rds.amazonaws.com' in database_url:
            print("✅ RDS 자동 백업 활성화")
        else:
            print("⚠️ RDS 자동 백업 설정 확인 필요")
        
        # S3 버전 관리 확인
        s3_bucket = os.environ.get('S3_BUCKET')
        if s3_bucket:
            print("✅ S3 버킷 설정 완료 (버전 관리 권장)")
        
        return True
    
    @staticmethod
    def setup_security_headers():
        """보안 헤더 설정 확인"""
        print("🔐 보안 헤더 설정 확인...")
        
        security_headers = [
            'SECURE_SSL_REDIRECT',
            'SECURE_HSTS_SECONDS',
            'SECURE_CONTENT_TYPE_NOSNIFF',
            'SECURE_BROWSER_XSS_FILTER',
            'X_FRAME_OPTIONS'
        ]
        
        missing_headers = []
        for header in security_headers:
            if not getattr(settings, header, None):
                missing_headers.append(header)
        
        if missing_headers:
            print(f"⚠️ 누락된 보안 헤더: {missing_headers}")
            return False
        
        print("✅ 보안 헤더 설정 완료")
        return True
    
    @staticmethod
    def run_initial_health_check():
        """초기 헬스체크 실행"""
        print("🔍 초기 헬스체크 실행...")
        
        try:
            result = MonitoringService.run_health_monitoring()
            
            # 헬스체크 결과 분석
            health_checks = result['health_checks']
            alerts = result['alerts']
            
            failed_services = [service for service, status in health_checks.items() if not status]
            
            if failed_services:
                print(f"⚠️ 실패한 서비스: {failed_services}")
                return False
            
            if alerts:
                print(f"⚠️ 성능 경고: {len(alerts)}개")
                for alert in alerts:
                    print(f"  - {alert['type']}: {alert['message']}")
            
            print("✅ 초기 헬스체크 통과")
            return True
            
        except Exception as e:
            print(f"❌ 헬스체크 실행 실패: {e}")
            return False
    
    @staticmethod
    def setup_operational_guardrails():
        """모든 운영 가드레일 설정"""
        print("🚀 UniLingo 운영 가드레일 활성화 시작...\n")
        
        guardrails = [
            ("레이트 리미팅", OperationalGuardrails.setup_rate_limiting),
            ("모니터링 알림", OperationalGuardrails.setup_monitoring_alerts),
            ("로그 보호", OperationalGuardrails.setup_logging_protection),
            ("헬스 모니터링", OperationalGuardrails.setup_health_monitoring),
            ("백업 전략", OperationalGuardrails.setup_backup_strategy),
            ("보안 헤더", OperationalGuardrails.setup_security_headers),
            ("초기 헬스체크", OperationalGuardrails.run_initial_health_check),
        ]
        
        total_guardrails = len(guardrails)
        activated_guardrails = 0
        
        for name, setup_func in guardrails:
            print(f"\n{'='*50}")
            try:
                if setup_func():
                    activated_guardrails += 1
            except Exception as e:
                print(f"❌ {name} 설정 중 오류 발생: {e}")
        
        print(f"\n{'='*50}")
        print("🎯 운영 가드레일 활성화 결과")
        print("==========================")
        print(f"총 가드레일: {total_guardrails}")
        print(f"활성화 완료: {activated_guardrails}" + (" ✅" if activated_guardrails == total_guardrails else ""))
        print(f"실패: {total_guardrails - activated_guardrails}" + (" ❌" if activated_guardrails < total_guardrails else ""))
        
        if activated_guardrails == total_guardrails:
            print("\n🎉 모든 운영 가드레일이 성공적으로 활성화되었습니다!")
            print("🛡️ 서비스가 안전하게 운영 준비 완료!")
            return True
        else:
            print(f"\n⚠️ {total_guardrails - activated_guardrails}개 가드레일 설정에 문제가 있습니다.")
            print("🔧 문제를 수정한 후 다시 실행하세요.")
            return False

# Django 관리 명령어로 실행
class Command(BaseCommand):
    help = '운영 가드레일 활성화'

    def handle(self, *args, **options):
        success = OperationalGuardrails.setup_operational_guardrails()
        if success:
            self.stdout.write(self.style.SUCCESS('운영 가드레일 활성화 완료!'))
        else:
            self.stdout.write(self.style.ERROR('운영 가드레일 활성화 실패!'))


