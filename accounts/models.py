from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone_number = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_region_verified = models.BooleanField(default=False)
    region_verified_at = models.DateTimeField(null=True, blank=True)
    reliability = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname or self.user.username
