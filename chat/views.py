from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import ChatRoom, Message, MessageReadStatus
from .serializers import (
    ChatRoomSerializer, MessageSerializer, 
    PartnerInfoSerializer, SendMessageSerializer
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_rooms(request):
    """채팅방 목록 조회 API"""
    user = request.user
    
    # 사용자가 참여한 채팅방들 조회
    chat_rooms = ChatRoom.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).order_by('-updated_at')
    
    serializer = ChatRoomSerializer(chat_rooms, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'rooms': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_room_partner(request, room_id):
    """채팅방 파트너 정보 조회 API"""
    user = request.user
    
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인
        if user not in chat_room.participants:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        partner = chat_room.get_partner(user)
        if partner:
            serializer = PartnerInfoSerializer(partner)
            return Response({
                'success': True,
                'partner': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': '파트너를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except ChatRoom.DoesNotExist:
        return Response({
            'success': False,
            'message': '채팅방을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_chat_messages(request, room_id):
    """채팅방 메시지 목록 조회 API"""
    user = request.user
    
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인
        if user not in chat_room.participants:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 메시지 목록 조회 (최신순)
        messages = chat_room.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'messages': serializer.data
        }, status=status.HTTP_200_OK)
        
    except ChatRoom.DoesNotExist:
        return Response({
            'success': False,
            'message': '채팅방을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_as_read(request, room_id):
    """채팅방 메시지 읽음 처리 API"""
    user = request.user
    
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인
        if user not in chat_room.participants:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 현재 사용자가 보낸 메시지가 아닌 모든 메시지를 읽음 처리
        unread_messages = chat_room.messages.exclude(sender=user)
        
        for message in unread_messages:
            # 이미 읽음 처리된 메시지는 건너뛰기
            if not MessageReadStatus.objects.filter(user=user, message=message).exists():
                MessageReadStatus.objects.create(user=user, message=message)
        
        return Response({
            'success': True,
            'message': '메시지가 읽음 처리되었습니다.'
        }, status=status.HTTP_200_OK)
        
    except ChatRoom.DoesNotExist:
        return Response({
            'success': False,
            'message': '채팅방을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request, room_id):
    """메시지 전송 API"""
    user = request.user
    
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인
        if user not in chat_room.participants:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SendMessageSerializer(
            data=request.data, 
            context={'room': chat_room, 'sender': user}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            
            # 메시지 읽음 상태 초기화 (송신자는 자동으로 읽음 처리)
            MessageReadStatus.objects.create(message=message, user=user)
            
            response_serializer = MessageSerializer(message, context={'request': request})
            
            return Response({
                'success': True,
                'message': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': '메시지 전송 중 오류가 발생했습니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except ChatRoom.DoesNotExist:
        return Response({
            'success': False,
            'message': '채팅방을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_as_read(request, room_id):
    """메시지 읽음 처리 API"""
    user = request.user
    
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인
        if user not in chat_room.participants:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 사용자가 보내지 않은 메시지들을 읽음 처리
        unread_messages = chat_room.messages.exclude(sender=user)
        read_message_ids = MessageReadStatus.objects.filter(
            user=user,
            message__in=unread_messages
        ).values_list('message_id', flat=True)
        
        new_read_messages = unread_messages.exclude(id__in=read_message_ids)
        
        for message in new_read_messages:
            MessageReadStatus.objects.create(message=message, user=user)
        
        return Response({
            'success': True,
            'message': f'{new_read_messages.count()}개의 메시지를 읽음 처리했습니다.'
        }, status=status.HTTP_200_OK)
        
    except ChatRoom.DoesNotExist:
        return Response({
            'success': False,
            'message': '채팅방을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)