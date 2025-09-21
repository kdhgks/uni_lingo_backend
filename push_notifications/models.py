from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DeviceToken(models.Model):
    """디바이스 토큰 모델 (FCM/APNs)"""
    
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='device_tokens',
        verbose_name='사용자'
    )
    device_type = models.CharField(
        max_length=10,
        choices=DEVICE_TYPES,
        verbose_name='디바이스 타입'
    )
    device_id = models.CharField(
        max_length=255,
        verbose_name='디바이스 ID'
    )
    token = models.TextField(
        verbose_name='푸시 토큰'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성 상태'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='등록일'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일'
    )
    last_notification_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='마지막 알림 시간'
    )
    
    class Meta:
        verbose_name = '디바이스 토큰'
        verbose_name_plural = '디바이스 토큰'
        unique_together = ['user', 'device_id']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type} ({self.device_id[:8]}...)"

class NotificationLog(models.Model):
    """푸시 알림 전송 로그"""
    
    STATUS_CHOICES = [
        ('sent', '전송됨'),
        ('failed', '실패'),
        ('pending', '대기중'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_logs',
        verbose_name='사용자'
    )
    device_token = models.ForeignKey(
        DeviceToken,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='디바이스 토큰'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='제목'
    )
    body = models.TextField(
        verbose_name='내용'
    )
    data = models.JSONField(
        default=dict,
        verbose_name='추가 데이터'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='상태'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='오류 메시지'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='전송 시간'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='생성일'
    )
    
    class Meta:
        verbose_name = '알림 로그'
        verbose_name_plural = '알림 로그'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.status})"


