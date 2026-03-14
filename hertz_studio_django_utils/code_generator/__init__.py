"""
Django代码生成器模块

该模块提供了Django应用代码自动生成功能，包括：
- 模型(ORM)代码生成
- 序列化器代码生成  
- 视图(CRUD)代码生成
- URL路由代码生成

使用示例:
    from hertz_studio_django_utils.code_generator import DjangoCodeGenerator
    
    generator = DjangoCodeGenerator()
    generator.generate_full_module(
        model_name='User',
        fields=[
            {'name': 'username', 'type': 'CharField', 'max_length': 150},
            {'name': 'email', 'type': 'EmailField'}
        ]
    )
"""

from .base_generator import BaseGenerator
from .django_code_generator import DjangoCodeGenerator
from .model_generator import ModelGenerator
from .serializer_generator import SerializerGenerator
from .view_generator import ViewGenerator
from .url_generator import URLGenerator
from .menu_generator import MenuGenerator

__all__ = [
    'BaseGenerator',
    'DjangoCodeGenerator',
    'ModelGenerator', 
    'SerializerGenerator',
    'ViewGenerator',
    'URLGenerator',
    'MenuGenerator'
]