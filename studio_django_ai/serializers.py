from rest_framework import serializers
from .models import AIChat, AIChatMessage


class AIChatSerializer(serializers.ModelSerializer):
    """
    AI聊天序列化器
    """
    class Meta:
        model = AIChat
        fields = ['id', 'title', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AIChatMessageSerializer(serializers.ModelSerializer):
    """
    AI聊天消息序列化器
    """
    class Meta:
        model = AIChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatRequestSerializer(serializers.Serializer):
    """
    聊天请求序列化器
    """
    content = serializers.CharField(required=True, help_text="消息内容")
    
    def validate_content(self, value):
        """
        验证消息内容不为空
        """
        if not value.strip():
            raise serializers.ValidationError("消息内容不能为空")
        return value


class AIChatDeleteSerializer(serializers.Serializer):
    """
    AI聊天删除序列化器
    """
    chat_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        min_length=1, 
        help_text="要删除的聊天ID列表"
    )