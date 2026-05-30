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
    path('groups/<int:group_id>/wish/',  group_wish_toggle,   name='group_wish_toggle'),

    # 나눔
    path('shares/', shares_list, name='share_list'),
    path('shares/create/', shares_create, name='share_create'),
    path('shares/<int:share_id>/', shares_detail, name='share_detail'),
    path('shares/<int:share_id>/update/', shares_update, name='share_update'),
    path('shares/<int:share_id>/delete/', shares_delete, name='share_delete'),
    path('shares/<int:share_id>/participate/', shares_participate, name='share_participate'),
    path('shares/<int:share_id>/wish/', sharing_wish_toggle, name='sharing_wish_toggle'),

]