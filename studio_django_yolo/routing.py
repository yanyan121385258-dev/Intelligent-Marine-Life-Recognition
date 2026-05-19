from django.urls import re_path
from .consumers import YoloLiveConsumer

websocket_urlpatterns = [
    re_path(r'^ws/yolo/live/$', YoloLiveConsumer.as_asgi()),
]