"""
Django模型代码生成器

该模块负责根据配置生成Django模型代码
"""

import os
from typing import Dict, List, Any, Optional
from .base_generator import BaseGenerator


class ModelGenerator(BaseGenerator):
    """Django模型代码生成器"""
    
    def __init__(self):
        """初始化模型生成器"""
        super().__init__()
    
    def generate(self, model_name: str = None, fields: List[Dict[str, Any]] = None, **kwargs) -> str:
        """
        生成Django模型代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表
            **kwargs: 其他参数
            
        Returns:
            str: 生成的模型代码
        """
        # 处理参数，支持位置参数和关键字参数
        if model_name is None:
            model_name = kwargs.get('model_name', 'DefaultModel')
        if fields is None:
            fields = kwargs.get('fields', [])
            
        table_name = kwargs.get('table_name')
        verbose_name = kwargs.get('verbose_name')
        verbose_name_plural = kwargs.get('verbose_name_plural')
        ordering = kwargs.get('ordering', ['-created_at'])
        status_choices = kwargs.get('status_choices', [
            ('active', '激活'),
            ('inactive', '未激活'),
            ('deleted', '已删除')
        ])
        
        # 确保verbose_name不为None
        if verbose_name is None:
            verbose_name = model_name
        
        # 确保verbose_name_plural不为None
        if verbose_name_plural is None:
            verbose_name_plural = verbose_name + '列表'
        
        # 处理字段列表，确保每个字段都有必要的属性
        processed_fields = []
        for field in fields:
            if isinstance(field, dict):
                # 字段已经在YAML解析器中处理过类型转换，这里不再重复处理
                processed_fields.append(field)
            elif isinstance(field, str):
                # 如果字段是字符串，转换为字典格式
                processed_fields.append({
                    'name': field,
                    'type': 'CharField',  # 直接使用Django字段类型
                    'django_field_type': 'CharField',
                    'max_length': 100,
                    'verbose_name': field,
                    'help_text': f'{field}字段'
                })
        
        # 添加默认的时间戳字段（如果不存在）
        has_created_at = any(field.get('name') == 'created_at' for field in processed_fields)
        has_updated_at = any(field.get('name') == 'updated_at' for field in processed_fields)
        
        if not has_created_at:
            processed_fields.append({
                'name': 'created_at',
                'type': 'DateTimeField',
                'auto_now_add': True,
                'verbose_name': '创建时间',
                'help_text': '记录创建时间'
            })
            
        if not has_updated_at:
            processed_fields.append({
                'name': 'updated_at',
                'type': 'DateTimeField',
                'auto_now': True,
                'verbose_name': '更新时间',
                'help_text': '记录最后更新时间'
            })
        
        # 准备模板上下文
        context = {
            'model_name': model_name,
            'fields': processed_fields,
            'table_name': table_name or self.camel_to_snake(model_name),
            'verbose_name': verbose_name,
            'verbose_name_plural': verbose_name_plural,
            'ordering': ordering,
            'status_choices': status_choices,
            'has_status_field': any(field.get('name') == 'status' for field in processed_fields)
        }
        
        # 渲染模板
        return self.render_template('django/models.mako', context)
    
    def generate_model_with_relationships(
        self,
        model_name: str,
        fields: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        生成包含关系字段的模型代码
        
        Args:
            model_name: 模型名称
            fields: 字段配置列表
            relationships: 关系字段配置列表
            
        Returns:
            str: 生成的模型代码
        """
        if relationships:
            # 将关系字段添加到字段列表中
            for rel in relationships:
                fields.append(rel)
        
        return self.generate(
            model_name=model_name,
            fields=fields,
            **kwargs
        )
    
    def generate_abstract_model(
        self,
        model_name: str,
        fields: List[Dict[str, Any]],
        **kwargs
    ) -> str:
        """
        生成抽象模型代码
        
        Args:
            model_name: 模型名称
            fields: 字段配置列表
            
        Returns:
            str: 生成的抽象模型代码
        """
        kwargs['abstract'] = True
        return self.generate(
            model_name=model_name,
            fields=fields,
            **kwargs
        )
    
    def generate_proxy_model(
        self,
        model_name: str,
        base_model: str,
        **kwargs
    ) -> str:
        """
        生成代理模型代码
        
        Args:
            model_name: 模型名称
            base_model: 基础模型名称
            
        Returns:
            str: 生成的代理模型代码
        """
        kwargs['proxy'] = True
        kwargs['base_model'] = base_model
        return self.generate(
            model_name=model_name,
            fields=[],
            **kwargs
        )
    
    def validate_field_config(self, field_config: Dict[str, Any]) -> bool:
        """
        验证字段配置
        
        Args:
            field_config: 字段配置字典
            
        Returns:
            bool: 验证是否通过
        """
        required_keys = ['name', 'type']
        for key in required_keys:
            if key not in field_config:
                return False
        
        # 验证字段类型
        valid_types = {
            'CharField', 'TextField', 'IntegerField', 'FloatField',
            'DecimalField', 'BooleanField', 'DateField', 'DateTimeField',
            'EmailField', 'URLField', 'ImageField', 'FileField',
            'ForeignKey', 'ManyToManyField', 'OneToOneField', 'JSONField',
            'SlugField', 'PositiveIntegerField', 'BigIntegerField',
            'SmallIntegerField', 'UUIDField', 'TimeField'
        }
        
        if field_config['type'] not in valid_types:
            return False
        
        return True
    
    def add_timestamp_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        添加时间戳字段
        
        Args:
            fields: 原字段列表
            
        Returns:
            List[Dict[str, Any]]: 包含时间戳字段的字段列表
        """
        timestamp_fields = [
            {
                'name': 'created_at',
                'type': 'DateTimeField',
                'auto_now_add': True,
                'verbose_name': '创建时间',
                'help_text': '记录创建时间'
            },
            {
                'name': 'updated_at',
                'type': 'DateTimeField',
                'auto_now': True,
                'verbose_name': '更新时间',
                'help_text': '记录最后更新时间'
            }
        ]
        
        return fields + timestamp_fields
    
    def add_status_field(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        添加状态字段
        
        Args:
            fields: 原字段列表
            
        Returns:
            List[Dict[str, Any]]: 包含状态字段的字段列表
        """
        status_field = {
            'name': 'status',
            'type': 'IntegerField',
            'choices': 'StatusChoices.choices',
            'default': 'StatusChoices.ENABLED',
            'verbose_name': '状态'
        }
        
        return fields + [status_field]