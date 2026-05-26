from django.urls import path
from posts.views import *

app_name = 'posts'

urlpatterns = [
    # 공구
    path('groups/', group_list, name='group_list'),
    path('groups/create/', group_create, name='group_create'),
    path('groups/<int:group_id>/', group_detail, name='group_detail'),
    path('groups/<int:group_id>/update/', group_update, name='group_update'),
    path('groups/<int:group_id>/delete/', group_delete, name='group_delete'),
    path('groups/<int:group_id>/participate/', group_participate, name='group_participate'),

    # 나눔
    
]