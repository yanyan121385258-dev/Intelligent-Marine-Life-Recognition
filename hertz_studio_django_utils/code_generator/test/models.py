from django.db import models
from hertz_studio_django_auth.models import HertzUser
import os

class Testmodels(models.Model):
    """
    测试模型
    """
    # 测试字段
    test_field = models.CharField(max_length=100, verbose_name='测试字段')
    name = models.CharField(max_length=50, unique=True, verbose_name='名称')
    test_path = models.CharField(max_length=100, verbose_name='测试路径')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='父项')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_at = models.DatetimeField(auto_now=True, verbose_name='更新时间')


    class Meta:
        db_table = test1
        verbose_name = '测试模型'
        verbose_name_plural = '测试模型'
    
    def __str__(self):
        return self.name

    def get_full_path(self):
        if self.parent:
            return f'{self.parent.get_full_path()} > {self.name}'
        return self.name