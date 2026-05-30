from django.contrib import admin
from .models import (
    Category,
    groupsPost, groupImage, groupsParticipant,
    sharingPost, SharingImage, SharingParticipant,
)


# ──────────────────────────────
# 인라인 (상세 페이지에서 같이 보여줄 것들)
# ──────────────────────────────

class groupImageInline(admin.TabularInline):
    model = groupImage
    extra = 1  # 빈 폼 1개 기본 표시


class groupsParticipantInline(admin.TabularInline):
    model = groupsParticipant
    extra = 0


class SharingImageInline(admin.TabularInline):
    model = SharingImage
    extra = 1


class SharingParticipantInline(admin.TabularInline):
    model = SharingParticipant
    extra = 0


# ──────────────────────────────
# 카테고리
# ──────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


# ──────────────────────────────
# 공구
# ──────────────────────────────

@admin.register(groupsPost)
class groupsPostAdmin(admin.ModelAdmin):
    list_display  = ('id', 'title', 'host', 'category', 'status', 'current_members', 'min_members', 'deadline', 'created_at')
    list_filter   = ('status', 'category')
    search_fields = ('title', 'host__username')
    ordering      = ('deadline',)
    inlines       = [groupImageInline, groupsParticipantInline]


# ──────────────────────────────
# 나눔
# ──────────────────────────────

@admin.register(sharingPost)
class sharingPostAdmin(admin.ModelAdmin):
    list_display  = ('id', 'title', 'host', 'category', 'status', 'quantity', 'deadline', 'created_at')
    list_filter   = ('status', 'category')
    search_fields = ('title', 'host__username')
    ordering      = ('deadline',)
    inlines       = [SharingImageInline, SharingParticipantInline]