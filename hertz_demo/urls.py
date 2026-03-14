from django.urls import path
from . import views

app_name = 'hertz_demo'

urlpatterns = [
    path('demo/captcha/', views.captcha_demo, name='captcha_demo'),
    path('demo/websocket/', views.websocket_demo, name='websocket_demo'),
    path('websocket/test/', views.websocket_test, name='websocket_test'),
    path('demo/email/', views.email_demo, name='email_demo'),
]