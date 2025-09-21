import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = int(self.scope['url_route']['kwargs']['room_id'])
            self.room_group_name = f'chat_{self.room_id}'
            
            # JWT 토큰에서 사용자 인증
            user = await self.get_user_from_token()
            if not user:
                await self.close(code=4401, reason="Authentication failed")
                return
            else:
                self.user = user
            
            # 채팅방에 참여
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # 사용자가 온라인 상태임을 알림
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_online',
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
            
        except (ValueError, KeyError) as e:
            await self.close(code=4000)
        except Exception as e:
            await self.close(code=4000)

    async def disconnect(self, close_code):
        # 채팅방에서 나가기
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # 사용자가 오프라인 상태임을 알림
        if hasattr(self, 'user'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_offline',
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )

    @database_sync_to_async
    def get_participant_status(self):
        """현재 사용자의 채팅방 참여 상태 조회"""
        try:
            from .models import ChatRoom
            room = ChatRoom.objects.get(id=self.room_id)
            participant = ChatRoomParticipant.objects.get(room=room, user=self.user)
            return participant
        except:
            return None

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'chat_message':
                message = text_data_json.get('message', '')
                if not message.strip():
                    return
                    
                # 메시지 저장 (비동기로)
                await self.save_message(message)
                
                # 보낸 사람에게는 ACK만 전송 (메시지 전송 성공 확인)
                await self.send(text_data=json.dumps({
                    'type': 'message_ack',
                    'client_id': text_data_json.get('client_id'),
                    'message_id': text_data_json.get('id'),  # 서버에서 생성된 실제 ID
                    'status': 'delivered',
                    'server_ts': int(time.time()),  # 서버 타임스탬프
                    'timestamp': text_data_json.get('timestamp'),
                }))
                
                # 다른 사용자들에게만 메시지 전송 (보낸 사람 제외)
                # 나간 사용자들은 자동으로 제외됨 (WebSocket 연결이 끊어져 있음)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'timestamp': text_data_json.get('timestamp'),
                        'id': text_data_json.get('id'),
                        'exclude_user': self.user.id,  # 보낸 사람 제외
                    }
                )
                
            elif message_type == 'typing':
                # 타이핑 상태 전송
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'is_typing': text_data_json.get('is_typing', False),
                    }
                )
            elif message_type == 'ping':
                # Ping 메시지에 대한 Pong 응답
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp'),
                }))
            elif message_type == 'heart_reaction':
                # 하트 반응을 데이터베이스에 저장하고 모든 사용자에게 브로드캐스트
                action = text_data_json.get('action')
                messageId = text_data_json.get('messageId')
                timestamp = text_data_json.get('timestamp')
                
                # 데이터베이스에 하트 반응 저장/삭제
                await self.save_heart_reaction(action, messageId)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'heart_reaction',
                        'action': action,
                        'messageId': messageId,
                        'timestamp': timestamp,
                        'user_id': self.user.id,
                        'username': self.user.username,
                    }
                )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def chat_message(self, event):
        # 보낸 사람은 제외하고 다른 사용자에게만 메시지 전송
        if event.get('exclude_user') != self.user.id:
            # 나간 사용자인지 확인
            from .models import ChatRoomParticipant
            try:
                participant = await self.get_participant_status()
                if participant and not participant.is_active:
                    # 나간 사용자에게는 메시지 전송하지 않음
                    return
            except:
                # 참여자 정보를 가져올 수 없는 경우 기본적으로 전송
                pass
            
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': event['message'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp'],
                'id': event.get('id'),
            }))

    async def typing(self, event):
        # 타이핑 상태 전송 (본인 제외)
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    async def heart_reaction(self, event):
        # 하트 반응 전송 (본인 제외)
        if event['user_id'] != self.user.id:
            heart_message = {
                'type': 'heart_reaction',
                'action': event['action'],
                'messageId': event['messageId'],
                'timestamp': event['timestamp'],
                'user_id': event['user_id'],
                'username': event['username'],
            }
            await self.send(text_data=json.dumps(heart_message))

    async def user_online(self, event):
        # 사용자 온라인 상태 전송 (본인 제외)
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_online',
                'user_id': event['user_id'],
                'username': event['username'],
            }))

    async def user_offline(self, event):
        # 사용자 오프라인 상태 전송 (본인 제외)
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_offline',
                'user_id': event['user_id'],
                'username': event['username'],
            }))

    async def room_event(self, event):
        # 룸 이벤트 전송 (나간 사용자 제외)
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'room_event',
                'event_type': event['event_type'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp'],
            }))


    @database_sync_to_async
    def get_user_from_token(self):
        """토큰에서 사용자 정보 추출"""
        try:
            token = None
            
            # 1. 쿼리 파라미터에서 토큰 추출
            query_string = self.scope.get('query_string', b'').decode()
            
            if query_string:
                params = {}
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value
                token = params.get('token')
            
            # 2. Authorization 헤더에서 토큰 추출
            if not token:
                headers = dict(self.scope.get('headers', []))
                auth_header = headers.get(b'authorization', b'').decode()
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
            
            if not token:
                return None
            
            
            # JWT 토큰 검증
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            if user_id:
                # get_user_model()을 사용하여 현재 활성화된 User 모델 가져오기
                User = get_user_model()
                user = User.objects.get(id=user_id)
                return user
            return None
            
        except Exception as e:
            return None

    @database_sync_to_async
    def save_heart_reaction(self, action, message_id):
        """하트 반응을 데이터베이스에 저장/삭제"""
        try:
            from .models import Message, HeartReaction
            
            # 메시지 찾기
            message = Message.objects.get(id=message_id)
            
            if action == 'add':
                # 하트 반응 추가 (이미 있으면 무시)
                heart_reaction, created = HeartReaction.objects.get_or_create(
                    message=message,
                    user=self.user
                )
                if created:
                    pass  # 새로 생성된 경우의 처리
                else:
                    pass  # 이미 존재하는 경우의 처리
                    
            elif action == 'remove':
                # 하트 반응 삭제
                deleted_count, _ = HeartReaction.objects.filter(
                    message=message,
                    user=self.user
                ).delete()
                if deleted_count > 0:
                    pass  # 하트 반응 삭제됨
                else:
                    pass  # 삭제할 하트 반응 없음
                    
        except Message.DoesNotExist:
            pass  # 메시지를 찾을 수 없음
        except Exception as e:
            pass  # 하트 반응 저장 오류

    @database_sync_to_async
    def save_message(self, message_text):
        """메시지를 데이터베이스에 저장"""
        try:
            # User 모델을 안전하게 가져오기
            User = get_user_model()
            room = ChatRoom.objects.get(id=self.room_id)
            
            # 실제 사용자 객체 가져오기
            user = User.objects.get(id=self.user.id)
            
            Message.objects.create(
                room=room,
                sender=user,
                content=message_text
            )
        except Exception as e:
            # 메시지 저장 실패해도 웹소켓 연결은 유지
            pass