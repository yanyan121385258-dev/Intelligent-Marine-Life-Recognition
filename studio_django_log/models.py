import json
from django.db import models
from django.conf import settings


class OperationLog(models.Model):
    """
    操作日志模型
    记录用户在系统中的各种操作行为
    """
    
    # 操作类型选择
    ACTION_TYPE_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('view', '查看'),
        ('list', '列表查看'),
        ('login', '登录'),
        ('logout', '登出'),
        ('export', '导出'),
        ('import', '导入'),
        ('other', '其他'),
    ]
    
    # 状态选择
    STATUS_CHOICES = [
        (0, '失败'),
        (1, '成功'),
    ]
    
    log_id = models.AutoField(primary_key=True, verbose_name='日志ID')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='操作用户'
    )
    action_type = models.CharField(
        max_length=20, 
        choices=ACTION_TYPE_CHOICES, 
        verbose_name='操作类型'
    )
    module = models.CharField(max_length=50, verbose_name='操作模块')
    description = models.CharField(max_length=255, verbose_name='操作描述')
    target_model = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name='目标模型'
    )
    target_id = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name='目标ID'
    )
    ip_address = models.GenericIPAddressField(
        blank=True, 
        null=True, 
        verbose_name='IP地址'
    )
    user_agent = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name='用户代理'
    )
    request_data = models.JSONField(
        blank=True, 
        null=True, 
        verbose_name='请求数据'
    )
    response_status = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name='响应状态码'
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES, 
        default=1, 
        verbose_name='操作状态'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='创建时间'
    )
    class Meta:
        db_table = 'hertz_log_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['module', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.module} - {self.created_at}"
    
    @property
    def username(self):
        """获取用户名"""
        return self.user.username if self.user else '匿名用户'
    
    @property
    def formatted_request_data(self):
        """格式化请求数据"""
        if self.request_data:
            try:
                return json.dumps(self.request_data, ensure_ascii=False, indent=2)
            except (TypeError, ValueError):
                return str(self.request_data)
        return ''
    
    @property
    def is_success(self):
        """判断操作是否成功"""
        return self.status == 1 and (
            self.response_status is None or 
            200 <= self.response_status < 400
        )
    
    @classmethod
    def create_log(cls, user=None, action_type='other', module='系统', 
                   description='', target_model=None, target_id=None,
                   ip_address=None, user_agent=None, request_data=None,
                   response_status=None):
        """
        创建操作日志的便捷方法
        
        Args:
            user: 操作用户
            action_type: 操作类型
            module: 操作模块
            description: 操作描述
            target_model: 目标模型
            target_id: 目标ID
            ip_address: IP地址
            user_agent: 用户代理
            request_data: 请求数据
            response_status: 响应状态码
            
        Returns:
            OperationLog: 创建的日志实例
        """
        # 限制数据长度避免数据库错误
        if user_agent and len(user_agent) > 500:
            user_agent = user_agent[:500]
        
        if description and len(description) > 255:
            description = description[:255]
        
        # 限制请求数据大小
        if request_data and len(str(request_data)) > 5000:
            request_data = {'message': '请求数据过大，已省略'}
        
        # 根据响应状态码判断操作状态
        status = 1  # 默认成功
        if response_status and response_status >= 400:
            status = 0  # 失败
        
        return cls.objects.create(
            user=user,
            action_type=action_type,
            module=module,
            description=description,
            target_model=target_model,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data=request_data,
            response_status=response_status,
            status=status
        )
