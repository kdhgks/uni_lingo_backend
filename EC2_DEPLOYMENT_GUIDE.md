# 🚀 UniLingo Django EC2 배포 가이드

## 📋 사전 준비사항

### 1. EC2 인스턴스 생성

- **AMI**: Ubuntu 22.04 LTS
- **인스턴스 타입**: t3.medium 이상 (2GB RAM 권장)
- **스토리지**: 20GB 이상
- **보안 그룹**: HTTP(80), HTTPS(443), SSH(22) 포트 허용

### 2. Neon PostgreSQL 데이터베이스

- [Neon Console](https://console.neon.tech)에서 데이터베이스 생성
- Connection String 복사 (나중에 .env 파일에 사용)

## 🛠️ 배포 단계

### 1단계: EC2에 접속

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2단계: 배포 스크립트 실행

```bash
# 프로젝트 코드를 EC2에 업로드 (GitHub에서 클론 또는 SCP로 전송)
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# 배포 스크립트 실행 권한 부여
chmod +x deploy_ec2.sh

# 배포 실행
./deploy_ec2.sh
```

### 3단계: 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp env_production_example.txt .env

# .env 파일 편집
nano .env
```

**중요한 설정값들:**

- `SECRET_KEY`: Django 시크릿 키 (랜덤한 긴 문자열)
- `DATABASE_URL`: Neon PostgreSQL 연결 문자열
- `ALLOWED_HOSTS`: EC2 퍼블릭 IP 추가

### 4단계: 서비스 상태 확인

```bash
# 서비스 상태 확인
sudo systemctl status unilingo-api
sudo systemctl status unilingo-websocket
sudo systemctl status nginx

# 로그 확인
sudo journalctl -u unilingo-api -f
sudo journalctl -u unilingo-websocket -f
```

### 5단계: 헬스체크

```bash
# API 헬스체크
curl http://your-ec2-ip/healthz/

# 응답 예시: {"status": "healthy", "service": "UniLingo API", "version": "1.0.0"}
```

## 🔧 서비스 관리 명령어

### 서비스 시작/중지/재시작

```bash
# API 서비스
sudo systemctl start unilingo-api
sudo systemctl stop unilingo-api
sudo systemctl restart unilingo-api

# WebSocket 서비스
sudo systemctl start unilingo-websocket
sudo systemctl stop unilingo-websocket
sudo systemctl restart unilingo-websocket

# Nginx
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
```

### 로그 확인

```bash
# 실시간 로그 보기
sudo journalctl -u unilingo-api -f
sudo journalctl -u unilingo-websocket -f

# Nginx 로그
sudo tail -f /var/log/nginx/unilingo_access.log
sudo tail -f /var/log/nginx/unilingo_error.log
```

## 🌐 프론트엔드 설정 변경

프론트엔드에서 API URL을 EC2 주소로 변경:

```javascript
// 기존 (로컬)
const API_BASE_URL = "http://127.0.0.1:8001/api/";
const WS_URL = "ws://127.0.0.1:8001/ws/";

// 변경 후 (EC2)
const API_BASE_URL = "http://your-ec2-ip/api/";
const WS_URL = "ws://your-ec2-ip/ws/";
```

## 🔒 보안 설정

### 1. 방화벽 설정

```bash
# UFW 상태 확인
sudo ufw status

# 필요한 포트만 허용
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

### 2. SSL 인증서 설정 (선택사항)

```bash
# Let's Encrypt 인증서 설치
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 모니터링

### 1. 시스템 리소스 모니터링

```bash
# CPU, 메모리 사용량
htop

# 디스크 사용량
df -h

# 네트워크 연결
netstat -tlnp
```

### 2. 애플리케이션 모니터링

```bash
# 프로세스 확인
ps aux | grep python

# 포트 사용 확인
sudo netstat -tlnp | grep -E ':(80|8000|8001)'
```

## 🚨 문제 해결

### 1. 서비스가 시작되지 않는 경우

```bash
# 서비스 상태 확인
sudo systemctl status unilingo-api

# 로그 확인
sudo journalctl -u unilingo-api --no-pager

# 수동으로 실행해서 오류 확인
cd /var/www/unilingo
source venv/bin/activate
python manage.py runserver --settings=language_exchange.settings_production
```

### 2. 데이터베이스 연결 오류

```bash
# .env 파일 확인
cat .env | grep DATABASE_URL

# 데이터베이스 연결 테스트
python manage.py dbshell --settings=language_exchange.settings_production
```

### 3. Nginx 오류

```bash
# Nginx 설정 테스트
sudo nginx -t

# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log
```

## 📝 업데이트 배포

코드가 업데이트된 경우:

```bash
cd /var/www/unilingo

# 코드 업데이트
git pull origin main

# 의존성 업데이트
source venv/bin/activate
pip install -r requirements_production.txt

# 데이터베이스 마이그레이션
python manage.py migrate --settings=language_exchange.settings_production

# 정적 파일 수집
python manage.py collectstatic --noinput --settings=language_exchange.settings_production

# 서비스 재시작
sudo systemctl restart unilingo-api
sudo systemctl restart unilingo-websocket
```

## 🎯 성능 최적화

### 1. Gunicorn 워커 수 조정

```bash
# /etc/systemd/system/unilingo-api.service 파일 수정
ExecStart=/var/www/unilingo/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 language_exchange.wsgi:application
```

### 2. Nginx 캐싱 설정

```nginx
# nginx.conf에 추가
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📞 지원

문제가 발생하면 다음 정보와 함께 문의하세요:

- EC2 인스턴스 타입
- 오류 로그
- 서비스 상태 (`sudo systemctl status unilingo-api`)
- 네트워크 설정 (`sudo netstat -tlnp`)



