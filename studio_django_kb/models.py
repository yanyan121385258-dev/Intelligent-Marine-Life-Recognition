"""
知识库与知识图谱模型定义

- KBItem: 知识库条目（多模态内容的原始承载）
- KBChunk: 条目分块及其向量嵌入（用于向量检索）
- KBEntity: 知识图谱实体（节点）
- KBRelation: 知识图谱关系（边），可关联来源片段
"""

from django.db import models
from django.conf import settings


class KBItem(models.Model):
    """知识库条目

    存储用户导入的原始内容（文本/代码/媒体文件）。
    当 `source_type=text` 时使用 `content` 字段；当 `source_type=file` 时使用 `file` 字段。
    """
    MODALITY_CHOICES = (
        ('text', 'text'),
        ('code', 'code'),
        ('image', 'image'),
        ('audio', 'audio'),
        ('video', 'video'),
    )
    SOURCE_CHOICES = (
        ('text', 'text'),
        ('file', 'file'),
        ('url', 'url'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 所属用户
    title = models.CharField(max_length=255)  # 条目标题
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, default='text')  # 内容模态类型
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='text')  # 内容来源类型
    content = models.TextField(null=True, blank=True)  # 文本内容（source_type=text）
    file = models.FileField(upload_to='kb/', null=True, blank=True)  # 文件内容（source_type=file）
    metadata = models.JSONField(default=dict, blank=True)  # 任意附加元数据
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    class Meta:
        db_table = 'hertz_kb_item'
        ordering = ['-updated_at']


class KBChunk(models.Model):
    """知识片段与嵌入

    将 `KBItem` 的内容进行分块，每块生成并存储一个向量嵌入，用于近似语义检索。
    """
    item = models.ForeignKey(KBItem, on_delete=models.CASCADE, related_name='chunks')
    index = models.IntegerField(default=0)  # 片段序号（从0开始）
    text = models.TextField()  # 片段文本内容
    embedding = models.JSONField(default=list)  # 片段向量（浮点列表，通常归一化）
    created_at = models.DateTimeField(auto_now_add=True)  # 片段创建时间

    class Meta:
        db_table = 'hertz_kb_chunk'
        ordering = ['item_id', 'index']


class KBEntity(models.Model):
    """知识图谱实体

    代表领域中的一个对象/概念，例如语言、框架、库、API 等。
    """
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)  # 实体类型（例如 Language/Framework/Library 等）
    properties = models.JSONField(default=dict, blank=True)  # 额外属性字典
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    class Meta:
        db_table = 'hertz_kb_entity'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['type']),
        ]


class KBRelation(models.Model):
    """知识图谱关系

    表示两个实体之间的连接，例如 depends_on/uses/implements 等，
    可可选关联来源片段以便溯源。
    """
    source = models.ForeignKey(KBEntity, on_delete=models.CASCADE, related_name='outgoing_relations')
    target = models.ForeignKey(KBEntity, on_delete=models.CASCADE, related_name='incoming_relations')
    relation_type = models.CharField(max_length=100)  # 关系类型（例如 depends_on/uses 等）
    properties = models.JSONField(default=dict, blank=True)  # 关系的附加属性
    source_chunk = models.ForeignKey(KBChunk, on_delete=models.SET_NULL, null=True, blank=True)  # 来源片段（可为空）
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    class Meta:
        db_table = 'hertz_kb_relation'
        indexes = [
            models.Index(fields=['relation_type']),
        ]
