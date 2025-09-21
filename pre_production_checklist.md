# UniLingo 실서비스 오픈 직전 점검 체크리스트

## ✅ Django/환경 점검

### 기본 설정

- [ ] `DEBUG=False` 확인
- [ ] `ALLOWED_HOSTS`에 실제 도메인 반영
- [ ] `CSRF_TRUSTED_ORIGINS=["https://your-domain.com"]` 설정
- [ ] `SECRET_KEY` 환경변수에서 주입 확인
- [ ] `DATABASE_URL`, `REDIS_URL`, `S3_BUCKET` 등 모든 키 환경변수로 관리
- [ ] `ASGI_APPLICATION = 'language_exchange.asgi.application'` 설정 확인

### 보안 설정

- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SECURE_PROXY_SSL_HEADER` 설정
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000`

## ✅ Nginx/WebSocket 점검

### WebSocket 설정

- [ ] `map $http_upgrade $connection_upgrade` 적용됨
- [ ] `/ws/` 블록에 `proxy_set_header Upgrade $http_upgrade` 설정
- [ ] `/ws/` 블록에 `proxy_set_header Connection $connection_upgrade` 설정
- [ ] `proxy_read_timeout 75s` 설정 (ALB 호환)
- [ ] `proxy_buffering off` 설정 (실시간 통신)

### SSL/TLS 설정

- [ ] 80→443 리다이렉트 설정
- [ ] SSL 인증서 유효성 확인
- [ ] `ssl_protocols TLSv1.2 TLSv1.3` 설정
- [ ] 보안 헤더 설정 완료

## ✅ Channels/Redis 점검

### Redis 연결

- [ ] `CHANNEL_LAYERS` → Redis 엔드포인트 연결 성공
- [ ] Redis 인증 설정 (패스워드)
- [ ] Redis 메모리 사용량 모니터링
- [ ] 헬스체크 `/health/redis/` 200 OK 응답

### Channels 설정

- [ ] `channels-redis` 패키지 설치
- [ ] WebSocket 라우팅 설정 완료
- [ ] JWT 인증 WebSocket 연결 테스트

## ✅ PostgreSQL 점검

### 인덱스 생성

```sql
-- 필수 인덱스 확인
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chat_message_room_timestamp
ON chat_message (room_id, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chat_message_room_sender
ON chat_message (room_id, sender_id, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chat_room_users
ON chat_room (user1_id, user2_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_language_teaching
ON user_language (user_id, language_type) WHERE language_type = 'teaching';
```

### 성능 설정

- [ ] `CONN_MAX_AGE=300` 적용
- [ ] `shared_buffers`, `effective_cache_size` 최적화
- [ ] `max_connections = 200` 설정
- [ ] 슬로우 쿼리 로깅 활성화

## ✅ 서비스 상태 점검

### systemd 서비스

- [ ] `systemctl status gunicorn` - Active (running)
- [ ] `systemctl status uvicorn` - Active (running)
- [ ] `systemctl status nginx` - Active (running)
- [ ] `systemctl status redis` - Active (running)
- [ ] `systemctl status postgresql` - Active (running)

### 로그 확인

- [ ] Django 로그: `/var/log/unilingo/django.log`
- [ ] Nginx 로그: `/var/log/nginx/unilingo_error.log`
- [ ] Gunicorn 로그: `/var/log/unilingo/gunicorn_error.log`
- [ ] Uvicorn 로그: 시스템 로그 확인

## ✅ 파일 권한 점검

### 디렉토리 권한

- [ ] `/var/www/unilingo` - ubuntu:www-data
- [ ] `/var/log/unilingo` - ubuntu:ubuntu
- [ ] 정적 파일 디렉토리 권한 확인
- [ ] 미디어 파일 디렉토리 권한 확인

## ✅ 백업 및 복구

### 데이터베이스 백업

- [ ] RDS 자동 백업 설정
- [ ] 수동 백업 스크립트 준비
- [ ] 백업 복구 테스트 완료

### 코드 백업

- [ ] Git 태그 생성 (릴리즈 버전)
- [ ] 배포 패키지 백업
- [ ] 환경 변수 스냅샷 백업

## ✅ 모니터링 설정

### 기본 모니터링

- [ ] Sentry DSN 연결
- [ ] CloudWatch 로그 그룹 설정
- [ ] 헬스체크 엔드포인트 동작 확인
- [ ] 기본 알람 설정 완료

### 성능 모니터링

- [ ] Nginx 응답시간 모니터링
- [ ] 데이터베이스 연결 수 모니터링
- [ ] Redis 메모리 사용량 모니터링
- [ ] WebSocket 연결 수 모니터링


