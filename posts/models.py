from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

# TimeStampedModel
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# upload_to
def upload_to_groups(instance, filename):
    ext = filename.split('.')[-1]
    return f"groups/{uuid.uuid4()}.{ext}"

def upload_to_sharing(instance, filename):
    ext = filename.split('.')[-1]
    return f"sharing/{uuid.uuid4()}.{ext}"

class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리 목록"

# =================================================
# 공구
# =================================================

class groupsPost(TimeStampedModel):
    STATUS_CHOICES = [
        ('recruiting', '모집중'),
        ('closed', '마감'),
        ('done', '완료'),
    ]

    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hosted_groups',  
        verbose_name="호스트"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='groups',         
        verbose_name="카테고리"
    )

    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    min_members = models.PositiveIntegerField(verbose_name="최소 모집인원")
    current_members = models.PositiveIntegerField(default=0, verbose_name="현재 참여인원")
    price_per = models.PositiveIntegerField(verbose_name="1/n 금액")
    location = models.CharField(max_length=100, verbose_name="거래 장소")
    deadline = models.DateTimeField(verbose_name="모집 마감일")
    link = models.URLField(blank=True, verbose_name="실제 판매 링크")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recruiting', verbose_name="상태")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '공구'
        verbose_name_plural = '공구 목록'
        ordering = ['deadline']  # 기본 정렬 마감임박순

class groupImage(models.Model):
    group = models.ForeignKey(
        groupsPost, 
        on_delete=models.CASCADE, 
        related_name='groupImages'
        )
    photo = models.ImageField(upload_to=upload_to_groups, verbose_name="공구 이미지")
    order = models.PositiveIntegerField(default=0, verbose_name="이미지 순서")

    class Meta:
        ordering = ['order']
        verbose_name = '공구 이미지'
        verbose_name_plural = '공구 이미지 목록'

class groupsParticipant(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('approved', '승인'),
        ('cancelled', '취소'),
    ]

    group = models.ForeignKey(
        groupsPost, 
        on_delete=models.CASCADE, 
        related_name='groupsParticipants'
        )
    user = models.ForeignKey(
        # Django 기본 User 모델을 참조, 필요에 따라 커스텀 User 모델로 변경 가능
        User, 
        on_delete=models.CASCADE, 
        related_name='groupsParticipants'
        )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="참여 상태")

    def __str__(self):
        return f'{self.group.title} - {self.user}'

    class Meta:
        verbose_name = '공구 참여'
        unique_together = ('group', 'user')  # 중복 참여 방지


# =================================================
# 나눔
# =================================================

class sharingPost(TimeStampedModel):
    STATUS_CHOICES = [
        ('recruiting', '모집중'),
        ('closed', '마감'),
        ('done', '완료'),
    ]

    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hosted_sharings',  
        verbose_name="호스트"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='sharings',        
        verbose_name="카테고리"
    )

    title = models.CharField(max_length=100, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    quantity   = models.PositiveIntegerField(verbose_name='물건 개수')
    location   = models.CharField(max_length=200, verbose_name='거래 장소')
    trade_time = models.DateTimeField(verbose_name='거래 시간')
    deadline   = models.DateTimeField(verbose_name='모집 마감 시간')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    latitude   = models.FloatField(null=True, blank=True, verbose_name='위도')
    longitude  = models.FloatField(null=True, blank=True, verbose_name='경도')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '나눔'
        verbose_name_plural = '나눔 목록'
        ordering = ['deadline']  # 기본 정렬 마감임박순

class SharingImage(models.Model):             # 이미지 분리
    sharing = models.ForeignKey(sharingPost, on_delete=models.CASCADE, related_name='images')
    photo   = models.ImageField(upload_to=upload_to_sharing)
    order   = models.PositiveIntegerField(default=0, verbose_name='이미지 순서')

    class Meta:
        ordering = ['order']
        verbose_name = '나눔 이미지'


class SharingParticipant(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('approved', '승인'),
        ('rejected', '거절'),
    ]

    sharing = models.ForeignKey(sharingPost, on_delete=models.CASCADE, related_name='participants')
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sharingParticipants')
    status  = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'{self.sharing.title} - {self.user}'

    class Meta:
        verbose_name = '나눔 신청'
        unique_together = ('sharing', 'user')