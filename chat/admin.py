from django.contrib import admin
from .models import ChatRoom, Message, MessageReadStatus

# Register your models here.

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user1__nickname', 'user1__email', 'user2__nickname', 'user2__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'content_preview', 'created_at')
    list_filter = ('created_at', 'room')
    search_fields = ('sender__nickname', 'sender__email', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = '내용 미리보기'

@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__nickname', 'user__email', 'message__content')
    ordering = ('-read_at',)
    readonly_fields = ('read_at',)
