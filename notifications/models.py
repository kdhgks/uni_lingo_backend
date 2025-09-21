from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    """알림 모델"""
    NOTIFICATION_TYPES = [
        ('matching', '매칭 완료'),
        ('message', '새 메시지'),
        ('friend_request', '친구 요청'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 관련 데이터
    related_user_id = models.IntegerField(null=True, blank=True)  # 매칭된 상대방 ID
    related_request_id = models.IntegerField(null=True, blank=True)  # 매칭 요청 ID
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '알림'
        verbose_name_plural = '알림들'
    
    def __str__(self):
        return f"{self.user.nickname} - {self.title}"


