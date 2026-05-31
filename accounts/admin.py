from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nickname', 'phone_number', 'reliability', 'created_at')
    search_fields = ('user__username', 'nickname', 'phone_number')
