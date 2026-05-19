from django.db import models
from django.utils import timezone
from studio_django_auth.models import HertzUser


class HertzNotice(models.Model):
    """
    通知表
    """
    NOTICE_TYPE_CHOICES = [
        (1, '系统通知'),
        (2, '公告通知'),
        (3, '活动通知'),
        (4, '维护通知'),
    ]
    
    PRIORITY_CHOICES = [
        (1, '低'),
        (2, '中'),
        (3, '高'),
        (4, '紧急'),
    ]
    
    STATUS_CHOICES = [
        (0, '草稿'),
        (1, '已发布'),
        (2, '已撤回'),
    ]
    
    notice_id = models.AutoField(primary_key=True, verbose_name='通知ID')
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    notice_type = models.IntegerField(choices=NOTICE_TYPE_CHOICES, default=1, verbose_name='通知类型')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name='优先级')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='状态')
    is_top = models.BooleanField(default=False, verbose_name='是否置顶')
    publish_time = models.DateTimeField(default=timezone.now, verbose_name='发布时间')
    expire_time = models.DateTimeField(blank=True, null=True, verbose_name='过期时间')
    publisher = models.ForeignKey(HertzUser, on_delete=models.SET_NULL, null=True, verbose_name='发布者')
    attachment_url = models.URLField(blank=True, null=True, verbose_name='附件链接')
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hertz_notice_notice'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-is_top', '-priority', '-publish_time']
        indexes = [
            models.Index(fields=['status', 'publish_time']),
            models.Index(fields=['notice_type', 'status']),
            models.Index(fields=['is_top', 'priority']),
        ]
    
    def __str__(self):
        return f'{self.title} - {self.get_notice_type_display()}'
    
    @property
    def is_expired(self):
        """检查通知是否已过期"""
        if self.expire_time:
            return timezone.now() > self.expire_time
        return False
    
    @property
    def read_count(self):
        """获取已读用户数量"""
        return self.user_notices.filter(is_read=True).count()
    
    @property
    def unread_count(self):
        """获取未读用户数量"""
        return self.user_notices.filter(is_read=False).count()


class HertzUserNotice(models.Model):
    """
    用户通知状态表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(HertzUser, on_delete=models.CASCADE, verbose_name='用户', related_name='user_notices')
    notice = models.ForeignKey(HertzNotice, on_delete=models.CASCADE, verbose_name='通知', related_name='user_notices')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    read_time = models.DateTimeField(blank=True, null=True, verbose_name='阅读时间')
    is_starred = models.BooleanField(default=False, verbose_name='是否收藏')
    starred_time = models.DateTimeField(blank=True, null=True, verbose_name='收藏时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'hertz_notice_user_notice'
        verbose_name = '用户通知状态'
        verbose_name_plural = '用户通知状态'
        unique_together = ['user', 'notice']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'is_starred']),
            models.Index(fields=['notice', 'is_read']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.notice.title} - {"已读" if self.is_read else "未读"}'
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_time = timezone.now()
            self.save(update_fields=['is_read', 'read_time', 'updated_at'])
    
    def mark_as_starred(self):
        """标记为收藏"""
        if not self.is_starred:
            self.is_starred = True
            self.starred_time = timezone.now()
            self.save(update_fields=['is_starred', 'starred_time', 'updated_at'])
    
    def unmark_starred(self):
        """取消收藏"""
        if self.is_starred:
            self.is_starred = False
            self.starred_time = None
            self.save(update_fields=['is_starred', 'starred_time', 'updated_at'])
    
    def toggle_star(self):
        """切换收藏状态"""
        if self.is_starred:
            self.unmark_starred()
        else:
            self.mark_as_starred()
