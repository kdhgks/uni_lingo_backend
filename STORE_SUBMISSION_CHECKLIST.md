# UniLingo 스토어 제출 준비 체크리스트

## 🍎 iOS App Store 제출 준비

### 필수 준비사항

- [ ] **Bundle ID 최종 확정**: `com.unilingo.app` (예시)
- [ ] **개인정보처리방침 URL**: `https://your-domain.com/privacy-policy`
- [ ] **이용약관 URL**: `https://your-domain.com/terms-of-service`
- [ ] **앱 설명**: 언어교환 서비스, 주요 기능 설명
- [ ] **키워드**: 언어교환, 영어, 한국어, 대학생, 매칭
- [ ] **앱 아이콘**: 1024x1024px (모든 크기 준비)
- [ ] **스크린샷**: iPhone, iPad (필요시) 각각 3-5장

### 프라이버시 답변 (스토어 심사용)

- [ ] **수집하는 데이터**:
  - 이메일 주소 (계정 생성용)
  - 대학명, 학과명, 학번 (신원 확인용)
  - 프로필 사진 (선택사항)
  - 디바이스 토큰 (푸시 알림용)
  - 채팅 메시지 (서비스 제공용)
- [ ] **데이터 사용 목적**: 언어교환 매칭 및 채팅 서비스 제공
- [ ] **데이터 공유**: 제3자와 공유하지 않음
- [ ] **데이터 보관**: 계정 삭제 시 모든 데이터 삭제

### 심사용 테스트 계정

- [ ] **테스트 계정 1**: `testuser1@example.com` / `TestPassword123!`
- [ ] **테스트 계정 2**: `testuser2@example.com` / `TestPassword123!`
- [ ] **관리자 계정**: `admin@unilingo.com` / `AdminPassword123!`

## 🤖 Google Play Store 제출 준비

### 필수 준비사항

- [ ] **패키지명 최종 확정**: `com.unilingo.app` (예시)
- [ ] **개인정보처리방침 URL**: `https://your-domain.com/privacy-policy`
- [ ] **앱 설명**: 언어교환 서비스, 주요 기능 설명
- [ ] **키워드**: 언어교환, 영어, 한국어, 대학생, 매칭
- [ ] **앱 아이콘**: 512x512px
- [ ] **스크린샷**: Phone, Tablet (필요시) 각각 2-8장
- [ ] **Feature Graphic**: 1024x500px

### Google Play Console 설정

- [ ] **콘텐츠 등급**: 모든 연령 (또는 12+)
- [ ] **앱 카테고리**: 교육 또는 소셜
- [ ] **타겟 연령대**: 18-25세 (대학생)
- [ ] **데이터 보안**: 개인정보 수집 및 처리 방식 명시

## 🔗 딥링크 설정

### iOS 딥링크 설정

```xml
<!-- Info.plist -->
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>com.unilingo.app</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>unilingo</string>
        </array>
    </dict>
</array>
```

### Android 딥링크 설정

```xml
<!-- AndroidManifest.xml -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="unilingo" />
</intent-filter>
```

### 딥링크 URL 형식

- **채팅방 진입**: `unilingo://chat/123`
- **프로필 보기**: `unilingo://profile/456`
- **알림 확인**: `unilingo://notifications`

## 📱 푸시 알림 설정

### iOS 푸시 알림

- [ ] **APNs 인증서**: 개발/프로덕션 인증서 준비
- [ ] **푸시 권한 요청**: "새 메시지 알림을 위해 필요합니다"
- [ ] **알림 사운드**: 기본 사운드 또는 커스텀 사운드
- [ ] **배지 카운트**: 읽지 않은 메시지 수 표시

### Android 푸시 알림

- [ ] **FCM 서버 키**: Firebase Console에서 발급
- [ ] **푸시 권한 요청**: "새 메시지 알림을 위해 필요합니다"
- [ ] **알림 채널**: 중요도별 채널 설정
- [ ] **알림 아이콘**: 투명 배경 PNG 24x24px

## 🛡️ 보안 및 프라이버시

### 개인정보처리방침 필수 내용

- [ ] **수집하는 개인정보 항목**
- [ ] **개인정보 수집 및 이용 목적**
- [ ] **개인정보 보유 및 이용 기간**
- [ ] **개인정보 제3자 제공**
- [ ] **개인정보 처리 위탁**
- [ ] **개인정보의 안전성 확보 조치**
- [ ] **개인정보 보호책임자**

### 이용약관 필수 내용

- [ ] **서비스 이용 조건**
- [ ] **회원가입 및 탈퇴**
- [ ] **서비스 이용 제한**
- [ ] **면책 조항**
- [ ] **분쟁 해결**

## 🧪 최종 테스트 체크리스트

### 기능 테스트

- [ ] **회원가입/로그인**: 정상 동작
- [ ] **프로필 설정**: 모든 필드 저장
- [ ] **언어 설정**: 가르칠 언어/배울 언어 선택
- [ ] **매칭 시스템**: 요청/승인/거절
- [ ] **채팅 기능**: 실시간 메시지 송수신
- [ ] **이미지 전송**: 업로드/다운로드
- [ ] **푸시 알림**: 백그라운드에서 수신
- [ ] **딥링크**: 알림 터치 시 해당 화면 이동

### 성능 테스트

- [ ] **앱 시작 시간**: 3초 이내
- [ ] **메시지 전송**: 1초 이내
- [ ] **이미지 로딩**: 5초 이내
- [ ] **배터리 사용량**: 정상 범위
- [ ] **메모리 사용량**: 정상 범위

### 호환성 테스트

- [ ] **iOS 14.0 이상**: 모든 기능 정상
- [ ] **Android 8.0 이상**: 모든 기능 정상
- [ ] **다양한 화면 크기**: 레이아웃 정상
- [ ] **다양한 해상도**: 이미지 품질 정상

## 📋 제출 전 최종 점검

### iOS App Store

- [ ] **앱 버전**: 1.0.0
- [ ] **빌드 번호**: 1
- [ ] **최소 iOS 버전**: 14.0
- [ ] **지원 기기**: iPhone, iPad
- [ ] **언어**: 한국어, 영어
- [ ] **연령 등급**: 4+ (모든 연령)

### Google Play Store

- [ ] **앱 버전**: 1.0.0
- [ ] **버전 코드**: 1
- [ ] **최소 Android 버전**: API 26 (Android 8.0)
- [ ] **타겟 Android 버전**: API 33 (Android 13)
- [ ] **권한**: 인터넷, 카메라, 저장소, 알림
- [ ] **언어**: 한국어, 영어

## 🚀 제출 후 모니터링

### 심사 기간 중

- [ ] **심사 상태 확인**: 매일 체크
- [ ] **심사 피드백 대응**: 24시간 이내 응답
- [ ] **테스트 계정 유지**: 심사 기간 중 활성 상태

### 출시 후

- [ ] **사용자 리뷰 모니터링**: 매일 체크
- [ ] **앱 크래시 모니터링**: 실시간 알림
- [ ] **성능 지표 모니터링**: 일일 리포트
- [ ] **업데이트 준비**: 버그 수정 및 기능 개선

---

## 📞 지원 연락처

### 개발팀

- **기술 지원**: dev@unilingo.com
- **긴급 상황**: +82-10-0000-0000

### 스토어 관련

- **iOS App Store**: https://appstoreconnect.apple.com
- **Google Play Console**: https://play.google.com/console

---

**✅ 모든 체크리스트를 완료한 후 스토어 제출을 진행하세요!** 🎉


