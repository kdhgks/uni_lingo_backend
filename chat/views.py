from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from .models import ChatRoom, Message, MessageReadStatus, HeartReaction, Report, ChatRoomParticipant
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
    
    # 사용자가 참여한 채팅방들 조회 (최신순)
    chat_rooms = ChatRoom.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).order_by('-updated_at')
    
    # 나간 채팅방 제외 (ChatRoomParticipant에서 is_active=False인 경우)
    active_rooms = []
    for room in chat_rooms:
        try:
            participant = ChatRoomParticipant.objects.get(room=room, user=user)
            if participant.is_active:  # 활성 상태인 경우만 포함
                active_rooms.append(room)
        except ChatRoomParticipant.DoesNotExist:
            # 참여자 기록이 없으면 기본적으로 포함 (기존 채팅방)
            active_rooms.append(room)
    
    serializer = ChatRoomSerializer(active_rooms, many=True, context={'request': request})
    
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
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인 (user1 또는 user2인지 확인)
        if user != chat_room.user1 and user != chat_room.user2:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 사용자가 나간 채팅방인지 확인
        try:
            participant = ChatRoomParticipant.objects.get(room=chat_room, user=user)
            if not participant.is_active:
                return Response({
                    'success': False,
                    'message': '나간 채팅방입니다.'
                }, status=status.HTTP_403_FORBIDDEN)
        except ChatRoomParticipant.DoesNotExist:
            # 참여자 기록이 없으면 기본적으로 허용 (기존 채팅방)
            pass
        
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
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인 (user1 또는 user2인지 확인)
        if user != chat_room.user1 and user != chat_room.user2:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 사용자가 나간 채팅방인지 확인
        try:
            participant = ChatRoomParticipant.objects.get(room=chat_room, user=user)
            if not participant.is_active:
                return Response({
                    'success': False,
                    'message': '나간 채팅방입니다.'
                }, status=status.HTTP_403_FORBIDDEN)
        except ChatRoomParticipant.DoesNotExist:
            # 참여자 기록이 없으면 기본적으로 허용 (기존 채팅방)
            pass
        
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
def send_message(request, room_id):
    """메시지 전송 API"""
    user = request.user
    
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인 (user1 또는 user2인지 확인)
        if user != chat_room.user1 and user != chat_room.user2:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 사용자가 나간 채팅방인지 확인
        try:
            participant = ChatRoomParticipant.objects.get(room=chat_room, user=user)
            if not participant.is_active:
                return Response({
                    'success': False,
                    'message': '나간 채팅방에서는 메시지를 보낼 수 없습니다.'
                }, status=status.HTTP_403_FORBIDDEN)
        except ChatRoomParticipant.DoesNotExist:
            # 참여자 기록이 없으면 기본적으로 허용 (기존 채팅방)
            pass
        
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
        
        # 사용자가 해당 채팅방에 참여하고 있는지 확인 (user1 또는 user2인지 확인)
        if user != chat_room.user1 and user != chat_room.user2:
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_heart_reactions(request, room_id):
    """채팅방의 하트 반응들 조회 API"""
    try:
        user = request.user
        
        # 채팅방 확인
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # 사용자가 참여한 채팅방인지 확인
        if user not in [chat_room.user1, chat_room.user2]:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 채팅방의 모든 하트 반응 조회
        heart_reactions = HeartReaction.objects.filter(
            message__room=chat_room
        ).select_related('user', 'message')
        
        # 메시지별로 그룹화
        heart_reactions_by_message = {}
        for reaction in heart_reactions:
            message_id = reaction.message.id
            if message_id not in heart_reactions_by_message:
                heart_reactions_by_message[message_id] = []
            heart_reactions_by_message[message_id].append({
                'id': reaction.id,
                'user_id': reaction.user.id,
                'username': reaction.user.username,
                'timestamp': reaction.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'heart_reactions': heart_reactions_by_message
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'하트 반응 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def report_user(request, room_id):
    """사용자 신고 API"""
    try:
        user = request.user
        
        # 채팅방 확인
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # 사용자가 참여한 채팅방인지 확인
        if user not in [chat_room.user1, chat_room.user2]:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 신고할 사용자 확인
        reported_user = chat_room.user1 if user == chat_room.user2 else chat_room.user2
        
        # 자신을 신고하는 것 방지
        if user == reported_user:
            return Response({
                'success': False,
                'message': '자신을 신고할 수 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 신고 사유 확인
        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response({
                'success': False,
                'message': '신고 사유를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 중복 신고 방지 (24시간 내)
        from django.utils import timezone
        from datetime import timedelta
        recent_report = Report.objects.filter(
            reporter=user,
            reported_user=reported_user,
            reported_room=chat_room,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()
        
        if recent_report:
            return Response({
                'success': False,
                'message': '24시간 내에 이미 신고한 사용자입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 신고 생성
        report = Report.objects.create(
            reporter=user,
            reported_user=reported_user,
            reported_room=chat_room,
            report_type='user',
            reason=reason
        )
        
        return Response({
            'success': True,
            'message': '신고가 접수되었습니다. 검토 후 조치하겠습니다.',
            'report_id': report.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'신고 접수 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_chat_room(request, room_id):
    """채팅방 나가기 API"""
    try:
        user = request.user
        
        # 채팅방 확인
        chat_room = get_object_or_404(ChatRoom, id=room_id)
        
        # 사용자가 참여한 채팅방인지 확인
        if user not in [chat_room.user1, chat_room.user2]:
            return Response({
                'success': False,
                'message': '접근 권한이 없습니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 상대방에게 시스템 메시지 생성
        partner = chat_room.user2 if user == chat_room.user1 else chat_room.user1
        system_message = Message.objects.create(
            room=chat_room,
            sender=user,  # 나간 사용자가 보낸 것으로 표시
            content=f"{user.nickname}님이 채팅방을 나갔습니다.",
            message_type='system_leave'
        )
        
        # ChatRoomParticipant에서 사용자를 비활성화
        try:
            participant = ChatRoomParticipant.objects.get(room=chat_room, user=user)
            participant.is_active = False
            participant.left_at = timezone.now()
            participant.save()
        except ChatRoomParticipant.DoesNotExist:
            # 참여자 기록이 없으면 생성
            ChatRoomParticipant.objects.create(
                room=chat_room,
                user=user,
                is_active=False,
                left_at=timezone.now()
            )
        
        # WebSocket을 통해 상대방에게 room_event 브로드캐스트
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{room_id}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'room_event',
                'event_type': 'left',
                'user_id': user.id,
                'username': user.nickname,
                'timestamp': system_message.created_at.isoformat(),
            }
        )
        
        
        return Response({
            'success': True,
            'message': '채팅방을 나갔습니다.',
            'system_message_id': system_message.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'채팅방 나가기 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_reports(request):
    """신고 내역 조회 API (관리자용)"""
    try:
        user = request.user
        
        # 관리자 권한 확인 (is_staff 또는 is_superuser)
        if not (user.is_staff or user.is_superuser):
            return Response({
                'success': False,
                'message': '관리자 권한이 필요합니다.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 신고 내역 조회
        reports = Report.objects.select_related(
            'reporter', 'reported_user', 'reported_room', 'reported_message'
        ).order_by('-created_at')
        
        reports_data = []
        for report in reports:
            report_data = {
                'id': report.id,
                'reporter': {
                    'id': report.reporter.id,
                    'username': report.reporter.username,
                    'nickname': getattr(report.reporter, 'nickname', ''),
                },
                'reported_user': {
                    'id': report.reported_user.id,
                    'username': report.reported_user.username,
                    'nickname': getattr(report.reported_user, 'nickname', ''),
                } if report.reported_user else None,
                'report_type': report.get_report_type_display(),
                'reason': report.reason,
                'status': report.get_status_display(),
                'admin_notes': report.admin_notes,
                'created_at': report.created_at.isoformat(),
                'updated_at': report.updated_at.isoformat(),
            }
            reports_data.append(report_data)
        
        return Response({
            'success': True,
            'reports': reports_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'신고 내역 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)