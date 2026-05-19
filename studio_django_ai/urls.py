from django.urls import path
from .views import (
    AIChatListView,
    AIChatCreateView,
    AIChatDetailView,
    AIChatUpdateView,
    AIChatDeleteView,
    AIChatSendMessageView
)

app_name = 'studio_django_ai'

urlpatterns = [
    # AI聊天列表
    path('chats/', AIChatListView.as_view(), name='chat_list'),
    # 创建AI聊天
    path('chats/create/', AIChatCreateView.as_view(), name='chat_create'),
    # 聊天详情
    path('chats/<int:chat_id>/', AIChatDetailView.as_view(), name='chat_detail'),
    # 更新聊天
    path('chats/<int:chat_id>/update/', AIChatUpdateView.as_view(), name='chat_update'),
    # 删除聊天
    path('chats/delete/', AIChatDeleteView.as_view(), name='chat_delete'),
    # 发送消息
    path('chats/<int:chat_id>/send/', AIChatSendMessageView.as_view(), name='chat_send_message'),
]