# 🚀 언어교환 프로그램 백엔드 API 문서

## 📋 **API 엔드포인트 목록**

### 🔐 **인증 관련**

- `POST /api/auth/login` - 로그인
- `POST /api/auth/signup` - 회원가입

### 👤 **사용자 관련**

- `GET /api/users/profile` - 프로필 조회
- `PUT /api/users/profile` - 프로필 수정
- `PUT /api/users/change-password` - 비밀번호 변경
- `DELETE /api/users/delete` - 계정 삭제

### 🤝 **매칭 관련**

- `GET /api/matching/partners` - 파트너 목록 조회
- `POST /api/matching/request` - 친구찾기 신청
- `GET /api/matching/status` - 매칭 상태 확인
- `POST /api/matching/simulate` - 매칭 시뮬레이션 (관리자용)

### 💬 **채팅 관련**

- `GET /api/chat/rooms` - 채팅방 목록
- `GET /api/chat/rooms/{id}/partner` - 파트너 정보
- `GET /api/chat/rooms/{id}/messages` - 메시지 목록
- `POST /api/chat/rooms/{id}/messages/send` - 메시지 전송
- `POST /api/chat/rooms/{id}/messages/read` - 메시지 읽음 처리

---

## 🔐 **인증 관련 API**

### 1. **로그인** - `POST /api/auth/login`

**요청:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "user123",
    "profile_image": "👨‍🎓",
    "phone": "010-1234-5678",
    "gender": "female",
    "birth_date": "2000-03-15",
    "student_name": "홍길동",
    "school": "서강대학교",
    "department": "국제통상학과",
    "student_id": "2024001",
    "university": "seoul_area",
    "teaching_languages": ["한국어", "영어"],
    "learning_languages": ["일본어", "중국어"],
    "interests": ["언어교환", "문화교류", "여행"],
    "created_at": "2024-01-15T09:00:00Z",
    "updated_at": "2024-01-15T09:00:00Z"
  }
}
```

**실패 응답 (401):**

```json
{
  "success": false,
  "message": {
    "non_field_errors": ["이메일 또는 비밀번호가 올바르지 않습니다."]
  }
}
```

### 2. **회원가입** - `POST /api/auth/signup`

**요청 (FormData):**

```
email: user@example.com
password: password123
password_confirm: password123
nickname: user123
phone: 010-1234-5678
gender: female
birth_date: 2000-03-15
student_name: 홍길동
school: 서강대학교
department: 국제통상학과
student_id: 2024001
university: seoul_area
student_card: [파일]
teaching_languages: ["한국어", "영어"]
learning_languages: ["일본어", "중국어"]
interests: ["언어교환", "문화교류"]
```

**성공 응답 (201):**

```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    // 로그인 응답과 동일한 user 객체
  }
}
```

---

## 👤 **사용자 관련 API**

### 1. **프로필 조회** - `GET /api/users/profile`

**요청 헤더:**

```
Authorization: Bearer {token}
```

**성공 응답 (200):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "nickname": "user123",
  "profile_image": "👨‍🎓",
  "phone": "010-1234-5678",
  "gender": "female",
  "birth_date": "2000-03-15",
  "student_name": "홍길동",
  "school": "서강대학교",
  "department": "국제통상학과",
  "student_id": "2024001",
  "university": "seoul_area",
  "teaching_languages": ["한국어", "영어"],
  "learning_languages": ["일본어", "중국어"],
  "interests": ["언어교환", "문화교류"],
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T09:00:00Z"
}
```

### 2. **프로필 수정** - `PUT /api/users/profile`

**요청 (FormData):**

```
nickname: new_nickname
phone: 010-9876-5432
gender: female
birth_date: 2000-03-15
student_name: 홍길동
school: 서강대학교
department: 국제통상학과
student_id: 2024001
university: seoul_area
profile_image: [파일]
teaching_languages: ["한국어", "영어"]
learning_languages: ["일본어", "중국어"]
interests: ["언어교환", "문화교류"]
```

**성공 응답 (200):**

```json
{
  "success": true,
  "message": "프로필이 성공적으로 업데이트되었습니다."
}
```

### 3. **비밀번호 변경** - `PUT /api/users/change-password`

**요청:**

```json
{
  "current_password": "old_password",
  "new_password": "new_password",
  "new_password_confirm": "new_password"
}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "message": "비밀번호가 성공적으로 변경되었습니다."
}
```

### 4. **계정 삭제** - `DELETE /api/users/delete`

**요청:**

```json
{
  "password": "user_password"
}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "message": "계정이 성공적으로 삭제되었습니다."
}
```

---

## 🤝 **매칭 관련 API**

### 1. **파트너 목록 조회** - `GET /api/matching/partners`

**요청 헤더:**

```
Authorization: Bearer {token}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "partners": [
    {
      "id": 2,
      "nickname": "partner1",
      "profile_image": "👨‍🎓",
      "gender": "male",
      "university": "연세대학교",
      "teaching_languages": ["영어", "일본어"],
      "learning_languages": ["한국어", "중국어"],
      "interests": ["언어교환", "스포츠"],
      "age": 22
    }
  ]
}
```

### 2. **친구찾기 신청** - `POST /api/matching/request`

**요청:**

```json
{
  "gender_preference": "male",
  "university_preference": "seoul_area",
  "specific_university": "서강대학교",
  "teaching_languages": ["한국어", "영어"],
  "learning_languages": ["일본어", "중국어"],
  "interests": ["언어교환", "문화교류"]
}
```

**성공 응답 (201):**

```json
{
  "success": true,
  "message": "친구찾기 신청이 완료되었습니다.",
  "requestId": 123
}
```

### 3. **매칭 상태 확인** - `GET /api/matching/status`

**요청 헤더:**

```
Authorization: Bearer {token}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "status": "pending",
  "partner": null,
  "requestId": 123
}
```

### 4. **매칭 시뮬레이션** - `POST /api/matching/simulate`

**요청:**

```json
{
  "user_id": 1
}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "message": "매칭이 성공적으로 완료되었습니다.",
  "partner": {
    "id": 2,
    "nickname": "partner1",
    "profile_image": "👨‍🎓",
    "gender": "male",
    "university": "연세대학교",
    "teaching_languages": ["영어", "일본어"],
    "learning_languages": ["한국어", "중국어"],
    "interests": ["언어교환", "스포츠"]
  }
}
```

---

## 💬 **채팅 관련 API**

### 1. **채팅방 목록** - `GET /api/chat/rooms`

**요청 헤더:**

```
Authorization: Bearer {token}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "rooms": [
    {
      "id": 1,
      "partner": {
        "id": 2,
        "nickname": "partner1",
        "profile_image": "👨‍🎓"
      },
      "last_message": {
        "content": "안녕하세요!",
        "timestamp": "2024-01-15T10:30:00Z",
        "is_from_me": false
      },
      "unread_count": 2,
      "created_at": "2024-01-15T09:00:00Z"
    }
  ]
}
```

### 2. **파트너 정보** - `GET /api/chat/rooms/{id}/partner`

**요청 헤더:**

```
Authorization: Bearer {token}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "partner": {
    "id": 2,
    "nickname": "partner1",
    "profile_image": "👨‍🎓",
    "gender": "male",
    "university": "연세대학교",
    "teaching_languages": ["영어", "일본어"],
    "learning_languages": ["한국어", "중국어"],
    "interests": ["언어교환", "스포츠"]
  }
}
```

### 3. **메시지 목록** - `GET /api/chat/rooms/{id}/messages`

**요청 헤더:**

```
Authorization: Bearer {token}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "content": "안녕하세요!",
      "timestamp": "2024-01-15T10:30:00Z",
      "is_from_me": false,
      "sender_id": 2
    },
    {
      "id": 2,
      "content": "안녕하세요! 반갑습니다.",
      "timestamp": "2024-01-15T10:31:00Z",
      "is_from_me": true,
      "sender_id": 1
    }
  ]
}
```

### 4. **메시지 전송** - `POST /api/chat/rooms/{id}/messages/send`

**요청:**

```json
{
  "content": "안녕하세요! 반갑습니다."
}
```

**성공 응답 (201):**

```json
{
  "success": true,
  "message": {
    "id": 123,
    "content": "안녕하세요! 반갑습니다.",
    "timestamp": "2024-01-15T10:31:00Z",
    "is_from_me": true,
    "sender_id": 1
  }
}
```

### 5. **메시지 읽음 처리** - `POST /api/chat/rooms/{id}/messages/read`

**요청 헤더:**

```
Authorization: Bearer {token}
```

**성공 응답 (200):**

```json
{
  "success": true,
  "message": "3개의 메시지를 읽음 처리했습니다."
}
```

---

## 🗄️ **데이터베이스 모델**

### **User 모델**

- 기본 사용자 정보 (이메일, 닉네임, 프로필 이미지 등)
- 학생 정보 (학교, 학과, 학번, 학생증 등)
- 언어 및 관심사는 별도 모델로 관리

### **UserLanguage 모델**

- 사용자가 가르치거나 배우는 언어 정보

### **UserInterest 모델**

- 사용자의 관심사 정보

### **MatchingRequest 모델**

- 매칭 요청 정보 (성별 선호도, 대학교 선호도 등)

### **MatchingPreference 모델**

- 매칭 시 선호하는 언어 및 관심사

### **ChatRoom 모델**

- 채팅방 정보 (두 사용자 간의 채팅방)

### **Message 모델**

- 메시지 정보 (내용, 송신자, 시간 등)

### **MessageReadStatus 모델**

- 메시지 읽음 상태 관리

---

## 🔧 **설정 및 보안**

### **JWT 토큰**

- 액세스 토큰: 24시간 유효
- 리프레시 토큰: 7일 유효
- 자동 토큰 갱신 지원

### **CORS 설정**

- 개발 환경에서 모든 도메인 허용
- 프로덕션에서는 특정 도메인만 허용 필요

### **파일 업로드**

- 프로필 이미지: `media/` 디렉토리에 저장
- 학생증: `media/student_cards/` 디렉토리에 저장

### **비밀번호 보안**

- Django 기본 비밀번호 검증 사용
- 비밀번호 해싱 자동 처리

---

## 🚀 **서버 실행 방법**

1. **가상환경 활성화:**

   ```bash
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **서버 실행:**

   ```bash
   python manage.py runserver
   ```

3. **서버 접속:**
   - API: `http://127.0.0.1:8000/api/`
   - 관리자: `http://127.0.0.1:8000/admin/`

---

## 📝 **테스트 방법**

### **Postman 또는 curl 사용**

1. **회원가입 테스트:**

   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123", "password_confirm": "test123", "nickname": "testuser"}'
   ```

2. **로그인 테스트:**

   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123"}'
   ```

3. **프로필 조회 테스트:**
   ```bash
   curl -X GET http://127.0.0.1:8000/api/users/profile/ \
     -H "Authorization: Bearer {token}"
   ```

---

## ✅ **구현 완료 사항**

- ✅ Django 프로젝트 설정
- ✅ 데이터베이스 모델 설계 및 구현
- ✅ JWT 인증 시스템
- ✅ 사용자 관리 API (회원가입, 로그인, 프로필 관리)
- ✅ 매칭 시스템 API (파트너 검색, 매칭 요청)
- ✅ 채팅 시스템 API (채팅방, 메시지 관리)
- ✅ 파일 업로드 지원
- ✅ CORS 설정
- ✅ API 문서화

이제 프론트엔드에서 이 API들을 사용하여 언어교환 프로그램을 완성할 수 있습니다! 🎉

