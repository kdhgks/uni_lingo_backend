from django.db import models
from users.models import User


class MatchingRequest(models.Model):
    """매칭 요청"""
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('matched', '매칭됨'),
        ('rejected', '거절됨'),
    ]
    
    GENDER_PREFERENCE_CHOICES = [
        ('male', '남성'),
        ('female', '여성'),
        ('any', '상관없음'),
    ]
    
    UNIVERSITY_PREFERENCE_CHOICES = [
        ('seoul_area', '서울권'),
        ('gyeonggi_area', '경기권'),
        ('incheon_area', '인천권'),
        ('busan_area', '부산권'),
        ('daegu_area', '대구권'),
        ('gwangju_area', '광주권'),
        ('daejeon_area', '대전권'),
        ('ulsan_area', '울산권'),
        ('gangwon_area', '강원권'),
        ('chungcheong_area', '충청권'),
        ('jeolla_area', '전라권'),
        ('gyeongsang_area', '경상권'),
        ('jeju_area', '제주권'),
        ('same_university', '같은 대학교'),
        ('specific_university', '특정 대학교'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matching_requests')
    gender_preference = models.CharField(max_length=10, choices=GENDER_PREFERENCE_CHOICES, default='any')
    university_preference = models.CharField(max_length=20, choices=UNIVERSITY_PREFERENCE_CHOICES, blank=True, null=True)
    specific_university = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    matched_partner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='matched_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'matching_requests'
        verbose_name = '매칭 요청'
        verbose_name_plural = '매칭 요청들'
    
    def __str__(self):
        return f"{self.user.nickname}의 매칭 요청 ({self.status})"


class MatchingPreference(models.Model):
    """매칭 선호도 (요청 시 저장되는 선호 언어, 관심사 등)"""
    matching_request = models.OneToOneField(
        MatchingRequest, 
        on_delete=models.CASCADE, 
        related_name='preferences'
    )
    teaching_languages = models.JSONField(default=list)  # 가르칠 수 있는 언어들
    learning_languages = models.JSONField(default=list)  # 배우고 싶은 언어들
    interests = models.JSONField(default=list)  # 관심사들
    
    class Meta:
        db_table = 'matching_preferences'
        verbose_name = '매칭 선호도'
        verbose_name_plural = '매칭 선호도들'
    
    def __str__(self):
        return f"{self.matching_request.user.nickname}의 매칭 선호도"