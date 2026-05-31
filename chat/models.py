from django.db import models
from django.contrib.auth import get_user_model


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
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

    @staticmethod
    def group_room_name(group_post_id):
        return f'group-{group_post_id}'

    @staticmethod
    def sharing_room_name(sharing_post_id):
        return f'share-{sharing_post_id}'

    @classmethod
    def get_or_create_for_group(cls, group_post):
        return cls.objects.get_or_create(
            group_post=group_post,
            defaults={'name': cls.group_room_name(group_post.pk)},
        )

    @classmethod
    def get_or_create_for_share(cls, sharing_post):
        return cls.objects.get_or_create(
            sharing_post=sharing_post,
            defaults={'name': cls.sharing_room_name(sharing_post.pk)},
        )

    def save(self, *args, **kwargs):
        if not self.name:
            if self.group_post_id:
                self.name = self.group_room_name(self.group_post_id)
            elif self.sharing_post_id:
                self.name = self.sharing_room_name(self.sharing_post_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group_post'],
                condition=models.Q(group_post__isnull=False),
                name='unique_chat_room_group_post',
            ),
            models.UniqueConstraint(
                fields=['sharing_post'],
                condition=models.Q(sharing_post__isnull=False),
                name='unique_chat_room_sharing_post',
            ),
        ]


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'
