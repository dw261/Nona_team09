import json
import urllib.parse  # 💡 한글 방 이름 ASCII 인코딩을 위해 내장 라이브러리 추가
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message  # 💡 NameError가 나지 않도록 임포트 위치 고정
from asgiref.sync import sync_to_async

MAX_MESSAGE_LENGTH = 1000


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 1. DB 조회에 사용할 원본 방 이름 (한글 포함)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        # 2. 💡 Channels Group Name 규칙에 맞게 한글 및 공백을 언더바(_)로 안전하게 변환
        safe_name = urllib.parse.quote(self.room_name).replace('%', '_').replace(' ', '_')
        
        # 3. 💡 변환된 안전한 이름으로 그룹 이름 지정 (100자 미만 제한)
        self.room_group_name = f'chat_{safe_name}'[:99]
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close(code=4401)
            return

        # 4. DB 조회할 때는 인코딩되지 않은 원래 한글 방 이름(self.room_name)을 그대로 사용
        self.room = await self.get_room_for_user(user, self.room_name)
        if self.room is None:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 5. 💡 안전한 그룹 이름을 사용해 채널 레이어에서 제거
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = str(data.get('message', '')).strip()
        if not message:
            return

        if len(message) > MAX_MESSAGE_LENGTH:
            message = message[:MAX_MESSAGE_LENGTH]

        user = self.scope['user']
        await sync_to_async(Message.objects.create)(room=self.room, user=user, content=message)

        # 6. 💡 메시지를 브로드캐스팅할 때도 안전한 그룹 이름을 사용
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @sync_to_async
    def get_room_for_user(self, user, room_name):
        try:
            room = ChatRoom.objects.select_related('group_post', 'sharing_post').get(name=room_name)
        except ChatRoom.DoesNotExist:
            return None

        if room.group_post_id:
            if room.group_post.host_id == user.id:
                return room
            if room.group_post.groupsParticipants.filter(
                user=user,
                status__in=['pending', 'approved'],
            ).exists():
                return room

        if room.sharing_post_id:
            if room.sharing_post.host_id == user.id:
                return room
            if room.sharing_post.participants.filter(
                user=user,
                status__in=['pending', 'approved'],
            ).exists():
                return room

        return None