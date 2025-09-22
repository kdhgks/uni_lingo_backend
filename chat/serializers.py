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
    
    def to_representation(self, instance):
        """시리얼라이저 출력 시 프로필 이미지 URL 추가"""
        data = super().to_representation(instance)
        if instance.profile_image:
            request = self.context.get('request')
            if request:
                data['profile_image_url'] = request.build_absolute_uri(instance.profile_image.url)
        return data
    
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
        fields = ['id', 'content', 'timestamp', 'is_from_me', 'sender_id', 'message_type']
        read_only_fields = ['id', 'timestamp']
    
    def get_is_from_me(self, obj):
        """메시지가 현재 사용자로부터 온 것인지 확인"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # 시스템 메시지는 항상 상대방 메시지로 표시
            if obj.message_type and obj.message_type != 'text':
                return False
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
                partner_data = {
                    'id': partner.id,
                    'nickname': partner.nickname,
                    'profile_image': partner.profile_image
                }
                # 프로필 이미지 URL 추가
                if partner.profile_image:
                    partner_data['profile_image_url'] = request.build_absolute_uri(partner.profile_image.url)
                return partner_data
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
        else:
            # 메시지가 없는 경우 채팅방 생성 시간 반환
            return {
                'content': None,
                'timestamp': obj.created_at,
                'is_from_me': False
            }
    
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

