from django.core.management.base import BaseCommand
from monitoring.alerts import MonitoringService

class Command(BaseCommand):
    help = '시스템 헬스체크 실행'

    def add_arguments(self, parser):
        parser.add_argument(
            '--alert',
            action='store_true',
            help='문제 발견 시 알림 전송',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔍 시스템 헬스체크 시작...')
        
        # 헬스체크 실행
        result = MonitoringService.run_health_monitoring()
        
        # 결과 출력
        self.stdout.write('\n📊 헬스체크 결과:')
        for service, status in result['health_checks'].items():
            status_icon = '✅' if status else '❌'
            self.stdout.write(f'  {status_icon} {service}')
        
        # 알림 출력
        if result['alerts']:
            self.stdout.write('\n⚠️ 경고사항:')
            for alert in result['alerts']:
                self.stdout.write(f'  - {alert["type"]}: {alert["message"]}')
        
        # 전체 상태
        all_healthy = all(result['health_checks'].values())
        if all_healthy and not result['alerts']:
            self.stdout.write(self.style.SUCCESS('\n🎉 모든 시스템이 정상 작동 중입니다!'))
        else:
            self.stdout.write(self.style.ERROR('\n⚠️ 일부 시스템에 문제가 있습니다.'))
            
            if options['alert']:
                self.stdout.write('📧 알림을 전송했습니다.')


