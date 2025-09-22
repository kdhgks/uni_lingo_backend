from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """사용자 모델"""
    GENDER_CHOICES = [
        ('male', '남성'),
        ('female', '여성'),
    ]
    
    # related_name 충돌 방지
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    UNIVERSITY_CHOICES = [
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
    ]
    
    # 기본 정보
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # 프로필 이미지 파일
    phone = models.CharField(
        max_length=20, 
        validators=[RegexValidator(regex=r'^010\d{8}$', message='올바른 전화번호 형식이 아닙니다.')],
        blank=True, 
        null=True
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # 학생 정보
    student_name = models.CharField(max_length=100, blank=True, null=True)
    school = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    university = models.CharField(max_length=20, choices=UNIVERSITY_CHOICES, blank=True, null=True)
    student_card = models.ImageField(upload_to='student_cards/', blank=True, null=True)
    
    # 언어 설정
    LEVEL_CHOICES = [
        ('beginner', '초급'),
        ('intermediate', '중급'),
        ('advanced', '고급'),
        ('native', '원어민'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    
    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'username']
    
    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
    
    def __str__(self):
        return f"{self.nickname} ({self.email})"


class UserLanguage(models.Model):
    """사용자 언어 정보"""
    LANGUAGE_TYPE_CHOICES = [
        ('teaching', '가르치는 언어'),
        ('learning', '배우는 언어'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(max_length=50)
    language_type = models.CharField(max_length=10, choices=LANGUAGE_TYPE_CHOICES)
    
    class Meta:
        db_table = 'user_languages'
        unique_together = ['user', 'language', 'language_type']
        verbose_name = '사용자 언어'
        verbose_name_plural = '사용자 언어들'
    
    def __str__(self):
        return f"{self.user.nickname} - {self.language} ({self.get_language_type_display()})"


class UserInterest(models.Model):
    """사용자 관심사"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    interest = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'user_interests'
        unique_together = ['user', 'interest']
        verbose_name = '사용자 관심사'
        verbose_name_plural = '사용자 관심사들'
    
    def __str__(self):
        return f"{self.user.nickname} - {self.interest}"