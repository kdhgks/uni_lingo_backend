from rest_framework import serializers
from users.models import User
from .models import ChatRoom, Message, MessageReadStatus


class PartnerInfoSerializer(serializers.ModelSerializer):
    """파트너 정보 시리얼라이저"""
    teaching_languages = serializers.SerializerMethodField()
    learning_languages = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'nickname', 'profile_image', 'gender', 'university', 'school',
            'teaching_languages', 'learning_languages', 'interests'
        ]
    
    def get_teaching_languages(self, obj):
        """가르치는 언어들 반환"""
        return [lang.language for lang in obj.languages.filter(language_type='teaching')]
    
    def get_learning_languages(self, obj):
        """배우는 언어들 반환"""
        return [lang.language for lang in obj.languages.filter(language_type='learning')]
    
    def get_interests(self, obj):
        """관심사들 반환"""
        return [interest.interest for interest in obj.interests.all()]


class MessageSerializer(serializers.ModelSerializer):
    """메시지 시리얼라이저"""
    is_from_me = serializers.SerializerMethodField()
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'is_from_me', 'sender_id']
        read_only_fields = ['id', 'timestamp']
    
    def get_is_from_me(self, obj):
        """메시지가 현재 사용자로부터 온 것인지 확인"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False


class ChatRoomSerializer(serializers.ModelSerializer):
    """채팅방 시리얼라이저"""
    partner = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'partner', 'last_message', 'unread_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_partner(self, obj):
        """상대방 정보 반환"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            partner = obj.get_partner(request.user)
            if partner:
                return {
                    'id': partner.id,
                    'nickname': partner.nickname,
                    'profile_image': partner.profile_image
                }
        return None
    
    def get_last_message(self, obj):
        """마지막 메시지 반환"""
        last_message = obj.messages.last()
        if last_message:
            request = self.context.get('request')
            is_from_me = False
            if request and hasattr(request, 'user'):
                is_from_me = last_message.sender == request.user
            
            return {
                'content': last_message.content,
                'timestamp': last_message.created_at,
                'is_from_me': is_from_me
            }
        return None
    
    def get_unread_count(self, obj):
        """읽지 않은 메시지 수 반환"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # 현재 사용자가 읽지 않은 메시지 수 계산
            unread_messages = obj.messages.exclude(sender=request.user)
            read_message_ids = MessageReadStatus.objects.filter(
                user=request.user,
                message__in=unread_messages
            ).values_list('message_id', flat=True)
            
            return unread_messages.exclude(id__in=read_message_ids).count()
        return 0


class SendMessageSerializer(serializers.ModelSerializer):
    """메시지 전송 시리얼라이저"""
    class Meta:
        model = Message
        fields = ['content']
    
    def create(self, validated_data):
        """메시지 생성"""
        room = self.context['room']
        sender = self.context['sender']
        return Message.objects.create(
            room=room,
            sender=sender,
            **validated_data
        )

