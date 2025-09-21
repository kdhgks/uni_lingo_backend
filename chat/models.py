from django.db import models
from users.models import User


class ChatRoom(models.Model):
    """채팅방"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        unique_together = ['user1', 'user2']
        verbose_name = '채팅방'
        verbose_name_plural = '채팅방들'
    
    def __str__(self):
        return f"{self.user1.nickname} - {self.user2.nickname}"
    
    @property
    def participants(self):
        """채팅방 참여자들 반환"""
        return [self.user1, self.user2]
    
    def get_partner(self, user):
        """특정 사용자의 상대방 반환"""
        if user == self.user1:
            return self.user2
        elif user == self.user2:
            return self.user1
        return None


class Message(models.Model):
    """메시지"""
    MESSAGE_TYPE_CHOICES = [
        ('text', '일반 메시지'),
        ('system_join', '시스템 메시지 - 입장'),
        ('system_leave', '시스템 메시지 - 퇴장'),
        ('system_info', '시스템 메시지 - 정보'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        verbose_name = '메시지'
        verbose_name_plural = '메시지들'
    
    def save(self, *args, **kwargs):
        """메시지 저장 시 채팅방의 updated_at 업데이트"""
        super().save(*args, **kwargs)
        # 채팅방의 updated_at을 현재 시간으로 업데이트
        from django.utils import timezone
        ChatRoom.objects.filter(id=self.room.id).update(updated_at=timezone.now())
    
    def __str__(self):
        return f"{self.sender.nickname}: {self.content[:50]}..."


class MessageReadStatus(models.Model):
    """메시지 읽음 상태"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_read_statuses')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_read_statuses'
        unique_together = ['message', 'user']
        verbose_name = '메시지 읽음 상태'
        verbose_name_plural = '메시지 읽음 상태들'
    
    def __str__(self):
        return f"{self.user.nickname} - {self.message.content[:30]}..."


class HeartReaction(models.Model):
    """하트 반응"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='heart_reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='heart_reactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'heart_reactions'
        unique_together = ['message', 'user']  # 한 메시지에 한 사용자는 하나의 하트만
        verbose_name = '하트 반응'
        verbose_name_plural = '하트 반응들'
    
    def __str__(self):
        return f"{self.user.nickname} ❤️ {self.message.content[:30]}..."


class Report(models.Model):
    """신고"""
    REPORT_STATUS_CHOICES = [
        ('pending', '대기중'),
        ('reviewing', '검토중'),
        ('resolved', '해결됨'),
        ('rejected', '거부됨'),
    ]
    
    REPORT_TYPE_CHOICES = [
        ('user', '사용자 신고'),
        ('message', '메시지 신고'),
        ('room', '채팅방 신고'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made', verbose_name='신고자')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received', null=True, blank=True, verbose_name='신고당한 사용자')
    reported_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='reports', verbose_name='신고된 메시지')
    reported_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True, related_name='reports', verbose_name='신고된 채팅방')
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name='신고 유형')
    reason = models.TextField(verbose_name='신고 사유')
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='pending', verbose_name='처리 상태')
    
    admin_notes = models.TextField(blank=True, null=True, verbose_name='관리자 메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='신고일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        db_table = 'reports'
        verbose_name = '신고'
        verbose_name_plural = '신고들'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.reported_user:
            return f"{self.reporter.nickname} → {self.reported_user.nickname} ({self.report_type})"
        elif self.reported_message:
            return f"{self.reporter.nickname} → 메시지 신고"
        elif self.reported_room:
            return f"{self.reporter.nickname} → 채팅방 신고"
        return f"{self.reporter.nickname} → 신고"


class ChatRoomParticipant(models.Model):
    """채팅방 참여자 관리 (나가기 기능용)"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_room_participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_room_participants'
        unique_together = ['room', 'user']
        verbose_name = '채팅방 참여자'
        verbose_name_plural = '채팅방 참여자들'
    
    def __str__(self):
        status = "활성" if self.is_active else "나감"
        return f"{self.user.nickname} - {self.room} ({status})"