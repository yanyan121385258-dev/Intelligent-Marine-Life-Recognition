"""
基础代码生成器类

提供代码生成的基础功能和通用方法
"""

import os
import re
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from .template_engine import TemplateEngine


class BaseGenerator(ABC):
    """
    基础代码生成器抽象类
    """
    
    def __init__(self, template_dir: str = None):
        """
        初始化基础生成器
        
        Args:
            template_dir: 模板目录路径
        """
        self.template_vars = {}
        self.template_engine = TemplateEngine(template_dir)
    
    def render_template(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板文件名
            context: 模板上下文变量
            
        Returns:
            str: 渲染后的代码字符串
        """
        if context is None:
            context = {}
        
        # 合并模板变量和上下文
        merged_context = {**self.template_vars, **context}
        
        return self.template_engine.render_template(template_name, merged_context)
    
    def create_template_context(self, **kwargs) -> Dict[str, Any]:
        """
        创建模板上下文
        
        Args:
            **kwargs: 上下文变量
            
        Returns:
            Dict[str, Any]: 模板上下文
        """
        context = {**self.template_vars, **kwargs}
        
        # 添加常用的辅助函数到上下文
        context.update({
            'snake_to_camel': self.snake_to_camel,
            'camel_to_snake': self.camel_to_snake,
            'format_field_name': self.format_field_name,
            'format_class_name': self.format_class_name,
            'format_verbose_name': self.format_verbose_name,
            'get_django_field_type': self.get_django_field_type,
        })
        
        return context
    
    @abstractmethod
    def generate(self, **kwargs) -> str:
        """
        生成代码的抽象方法
        
        Returns:
            str: 生成的代码字符串
        """
        pass
    
    def set_template_var(self, key: str, value: Any) -> None:
        """
        设置模板变量
        
        Args:
            key: 变量名
            value: 变量值
        """
        self.template_vars[key] = value
    
    def get_template_var(self, key: str, default: Any = None) -> Any:
        """
        获取模板变量
        
        Args:
            key: 变量名
            default: 默认值
            
        Returns:
            Any: 变量值
        """
        return self.template_vars.get(key, default)
    
    def snake_to_camel(self, snake_str: str) -> str:
        """
        将蛇形命名转换为驼峰命名
        
        Args:
            snake_str: 蛇形命名字符串
            
        Returns:
            str: 驼峰命名字符串
        """
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
    
    def camel_to_snake(self, camel_str: str) -> str:
        """
        将驼峰命名转换为蛇形命名
        
        Args:
            camel_str: 驼峰命名字符串
            
        Returns:
            str: 蛇形命名字符串
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def format_field_name(self, field_name: str) -> str:
        """
        格式化字段名称
        
        Args:
            field_name: 原始字段名
            
        Returns:
            str: 格式化后的字段名
        """
        return field_name.lower().replace(' ', '_').replace('-', '_')
    
    def format_class_name(self, name: str) -> str:
        """
        格式化类名
        
        Args:
            name: 原始名称
            
        Returns:
            str: 格式化后的类名
        """
        return self.snake_to_camel(self.format_field_name(name))
    
    def format_verbose_name(self, field_name: str) -> str:
        """
        格式化verbose_name
        
        Args:
            field_name: 字段名
            
        Returns:
            str: 格式化后的verbose_name
        """
        return field_name.replace('_', ' ').title()
    
    def generate_imports(self, imports: List[str]) -> str:
        """
        生成导入语句
        
        Args:
            imports: 导入列表
            
        Returns:
            str: 导入语句字符串
        """
        if not imports:
            return ''
        
        return '\n'.join(imports) + '\n\n'
    
    def indent_code(self, code: str, indent_level: int = 1) -> str:
        """
        为代码添加缩进
        
        Args:
            code: 代码字符串
            indent_level: 缩进级别
            
        Returns:
            str: 缩进后的代码
        """
        indent = '    ' * indent_level
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
    
    def write_to_file(self, file_path: str, content: str) -> bool:
        """
        将内容写入文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            bool: 是否写入成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败: {e}")
            return False
    
    def validate_field_config(self, field_config: Dict[str, Any]) -> bool:
        """
        验证字段配置
        
        Args:
            field_config: 字段配置字典
            
        Returns:
            bool: 配置是否有效
        """
        required_keys = ['name', 'type']
        return all(key in field_config for key in required_keys)
    
    def get_django_field_type(self, field_type: str) -> str:
        """
        获取Django字段类型
        
        Args:
            field_type: 字段类型
            
        Returns:
            str: Django字段类型
        """
        field_mapping = {
            'string': 'CharField',
            'text': 'TextField', 
            'integer': 'IntegerField',
            'float': 'FloatField',
            'decimal': 'DecimalField',
            'boolean': 'BooleanField',
            'date': 'DateField',
            'datetime': 'DateTimeField',
            'time': 'TimeField',
            'email': 'EmailField',
            'url': 'URLField',
            'file': 'FileField',
            'image': 'ImageField',
            'json': 'JSONField',
            'uuid': 'UUIDField',
            'foreign_key': 'ForeignKey',
            'many_to_many': 'ManyToManyField',
            'one_to_one': 'OneToOneField'
        }
        return field_mapping.get(field_type.lower(), 'CharField')