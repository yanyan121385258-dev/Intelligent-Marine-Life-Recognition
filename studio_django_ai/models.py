from django.db import models
from django.conf import settings


class AIChat(models.Model):
    """
    AI聊天会话模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    title = models.CharField(max_length=255, verbose_name="标题")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'hertz_ai_ai_chat'
        verbose_name = "AI聊天"
        verbose_name_plural = "AI聊天"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class AIChatMessage(models.Model):
    """
    AI聊天消息模型
    """
    ROLE_CHOICES = (
        ('user', '用户'),
        ('assistant', 'AI助手'),
        ('system', '系统'),
    )
    
    chat = models.ForeignKey(AIChat, on_delete=models.CASCADE, related_name='messages', verbose_name="聊天")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="角色")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'hertz_ai_ai_chat_message'
        verbose_name = "聊天消息"
        verbose_name_plural = "聊天消息"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.chat.title} - {self.role} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"