from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.room_list, name='list'),
    path('<int:room_id>/', views.room_detail, name='room'),
    path('api/<int:room_id>/confirm/', views.confirm_purchase, name='confirm'),
    path('api/<int:room_id>/leave/', views.leave_room, name='leave'),
]
