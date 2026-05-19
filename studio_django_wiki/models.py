from django.db import models
from django.utils import timezone
from django.conf import settings
from studio_django_auth.models import HertzUser
import os

class Wiki(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(null=True, blank=True, verbose_name='分类描述')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父分类')
    sort_order = models.IntegerField(default=0, verbose_name='排序顺序')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'hertz_wiki_wiki_category'
        verbose_name = '知识分类'
        verbose_name_plural = '知识分类'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name
    
    def get_full_path(self):
        if self.parent:
            return f'{self.parent.get_full_path()} > {self.name}'
        return self.name


class WikiArticle(models.Model):
    """
    知识文章模型
    """
    STATUS_CHOICES=(
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    )

    title = models.CharField(max_length=200, verbose_name='文章标题')
    content = models.TextField(verbose_name='文章内容')
    summary = models.TextField(max_length=500, null=True, blank=True, verbose_name='文章摘要')
    image = models.CharField(max_length=255, null=True, blank=True, verbose_name='文章图片')
    category = models.ForeignKey(Wiki, on_delete=models.CASCADE, related_name='articles', verbose_name='知识分类')
    author = models.ForeignKey(HertzUser, on_delete=models.CASCADE, related_name='wiki_articles', verbose_name='作者')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='文章状态')
    tags = models.CharField(max_length=200, null=True, blank=True, verbose_name='文章标签')
    view_count = models.IntegerField(default=0, verbose_name='阅读量')
    sort_order = models.IntegerField(default=0, verbose_name='排序顺序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')

    class Meta:
        verbose_name = '知识文章'
        verbose_name_plural = '知识文章'
        db_table = 'hertz_wiki_wiki_article'
        ordering = ['sort_order', 'title']
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])