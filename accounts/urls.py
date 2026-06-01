from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('phone/', views.phone_start, name='phone'),
    path('code/', views.code, name='code'),
    path('verify/', views.code, name='verify'),
    path('send-code/', views.send_code_api, name='send_code'),
    path('verify-code/', views.verify_code_api, name='verify_code'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mypage/', views.mypage, name='mypage'),
    path('location/', views.location, name='location'),
    path('complete/', views.complete, name='complete'),
    path('verify-region/', views.verify_region, name='verify_region'),
]
