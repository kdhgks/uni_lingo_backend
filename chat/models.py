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
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        verbose_name = '메시지'
        verbose_name_plural = '메시지들'
    
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