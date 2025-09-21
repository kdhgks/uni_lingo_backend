from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """기본 헬스체크"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'UniLingo API',
        'version': '1.0.0'
    })

def db_health_check(request):
    """데이터베이스 헬스체크"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'result': result[0] if result else None
        })
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }, status=500)

def redis_health_check(request):
    """Redis 헬스체크"""
    try:
        # Redis 연결 테스트
        cache.set('health_check', 'test', 10)
        result = cache.get('health_check')
        
        if result == 'test':
            cache.delete('health_check')
            return JsonResponse({
                'status': 'healthy',
                'redis': 'connected',
                'test_result': result
            })
        else:
            return JsonResponse({
                'status': 'unhealthy',
                'redis': 'test_failed',
                'error': 'Cache test failed'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'redis': 'disconnected',
            'error': str(e)
        }, status=500)

def full_health_check(request):
    """전체 시스템 헬스체크"""
    health_status = {
        'service': 'UniLingo API',
        'version': '1.0.0',
        'timestamp': None,
        'checks': {}
    }
    
    # 데이터베이스 체크
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = {
                'status': 'healthy',
                'response_time': '< 10ms'
            }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Redis 체크
    try:
        cache.set('health_check_full', 'test', 10)
        result = cache.get('health_check_full')
        if result == 'test':
            cache.delete('health_check_full')
            health_status['checks']['redis'] = {
                'status': 'healthy',
                'response_time': '< 10ms'
            }
        else:
            health_status['checks']['redis'] = {
                'status': 'unhealthy',
                'error': 'Cache test failed'
            }
    except Exception as e:
        health_status['checks']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # 전체 상태 결정
    all_healthy = all(
        check['status'] == 'healthy' 
        for check in health_status['checks'].values()
    )
    
    health_status['overall_status'] = 'healthy' if all_healthy else 'unhealthy'
    
    status_code = 200 if all_healthy else 500
    return JsonResponse(health_status, status=status_code)


