from django.db import models
from django.contrib.auth import get_user_model

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    group_post = models.ForeignKey(
        'posts.groupsPost',
        related_name='chat_rooms',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    sharing_post = models.ForeignKey(
        'posts.sharingPost',
        related_name='chat_rooms',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'
