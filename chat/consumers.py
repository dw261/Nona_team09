import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from asgiref.sync import sync_to_async


MAX_MESSAGE_LENGTH = 1000


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close(code=4401)
            return

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
