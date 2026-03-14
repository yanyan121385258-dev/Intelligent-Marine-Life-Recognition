"""
模板引擎类

基于Mako模板引擎的代码生成模板管理器
"""

import os
from typing import Dict, Any, Optional
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import TemplateLookupException, CompileException


class TemplateEngine:
    """
    模板引擎类
    
    负责管理和渲染Mako模板
    """
    
    def __init__(self, template_dir: str = None):
        """
        初始化模板引擎
        
        Args:
            template_dir: 模板目录路径
        """
        if template_dir is None:
            # 默认模板目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(current_dir, 'templates')
        
        self.template_dir = template_dir
        self.lookup = TemplateLookup(
            directories=[template_dir],
            module_directory=os.path.join(template_dir, '.mako_modules'),
            input_encoding='utf-8',
            output_encoding='utf-8',
            encoding_errors='replace'
        )
        
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template_name: 模板文件名
            context: 模板上下文变量
            
        Returns:
            str: 渲染后的代码字符串
            
        Raises:
            TemplateLookupException: 模板不存在
            CompileException: 模板编译错误
        """
        try:
            template = self.lookup.get_template(template_name)
            rendered = template.render(**context)
            # 确保返回字符串而不是bytes
            if isinstance(rendered, bytes):
                return rendered.decode('utf-8')
            return rendered
        except TemplateLookupException as e:
            raise TemplateLookupException(f"模板 '{template_name}' 不存在: {str(e)}")
        except CompileException as e:
            raise CompileException(f"模板 '{template_name}' 编译错误: {str(e)}")
        except Exception as e:
            raise Exception(f"渲染模板 '{template_name}' 时发生错误: {str(e)}")
    
    def render_django_model(self, context: Dict[str, Any]) -> str:
        """
        渲染Django模型模板
        
        Args:
            context: 模板上下文
            
        Returns:
            str: 生成的模型代码
        """
        return self.render_template('django/models.mako', context)
    
    def render_django_serializer(self, context: Dict[str, Any]) -> str:
        """
        渲染Django序列化器模板
        
        Args:
            context: 模板上下文
            
        Returns:
            str: 生成的序列化器代码
        """
        return self.render_template('django/serializers.mako', context)
    
    def render_django_view(self, context: Dict[str, Any]) -> str:
        """
        渲染Django视图模板
        
        Args:
            context: 模板上下文
            
        Returns:
            str: 生成的视图代码
        """
        return self.render_template('django/views.mako', context)
    
    def render_django_url(self, context: Dict[str, Any]) -> str:
        """
        渲染Django URL配置模板
        
        Args:
            context: 模板上下文
            
        Returns:
            str: 生成的URL配置代码
        """
        return self.render_template('django/urls.mako', context)
    
    def render_django_app(self, context: Dict[str, Any]) -> str:
        """
        渲染Django应用配置模板
        
        Args:
            context: 模板上下文
            
        Returns:
            str: 生成的应用配置代码
        """
        return self.render_template('django/apps.mako', context)
    
    def get_available_templates(self) -> list:
        """
        获取可用的模板列表
        
        Returns:
            list: 模板文件列表
        """
        templates = []
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith('.mako'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.template_dir)
                    templates.append(rel_path.replace('\\', '/'))
        return templates
    
    def template_exists(self, template_name: str) -> bool:
        """
        检查模板是否存在
        
        Args:
            template_name: 模板名称
            
        Returns:
            bool: 模板是否存在
        """
        try:
            self.lookup.get_template(template_name)
            return True
        except TemplateLookupException:
            return False
    
    def validate_template(self, template_name: str) -> tuple:
        """
        验证模板语法
        
        Args:
            template_name: 模板名称
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        try:
            template = self.lookup.get_template(template_name)
            # 尝试编译模板
            template.code
            return True, None
        except CompileException as e:
            return False, f"模板编译错误: {str(e)}"
        except TemplateLookupException as e:
            return False, f"模板不存在: {str(e)}"
        except Exception as e:
            return False, f"未知错误: {str(e)}"
    
    def create_context(self, **kwargs) -> Dict[str, Any]:
        """
        创建模板上下文
        
        Args:
            **kwargs: 上下文变量
            
        Returns:
            Dict[str, Any]: 模板上下文
        """
        return kwargs
    
    def add_template_directory(self, directory: str) -> None:
        """
        添加模板目录
        
        Args:
            directory: 模板目录路径
        """
        if os.path.exists(directory):
            self.lookup.directories.append(directory)
        else:
            raise FileNotFoundError(f"模板目录不存在: {directory}")
    
    def clear_cache(self) -> None:
        """
        清除模板缓存
        """
        self.lookup._collection.clear()
        
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        获取模板信息
        
        Args:
            template_name: 模板名称
            
        Returns:
            Dict[str, Any]: 模板信息
        """
        try:
            template = self.lookup.get_template(template_name)
            template_path = template.filename
            
            info = {
                'name': template_name,
                'path': template_path,
                'exists': True,
                'size': os.path.getsize(template_path) if template_path else 0,
                'modified_time': os.path.getmtime(template_path) if template_path else None
            }
            
            # 验证模板
            is_valid, error = self.validate_template(template_name)
            info['valid'] = is_valid
            info['error'] = error
            
            return info
        except TemplateLookupException:
            return {
                'name': template_name,
                'exists': False,
                'valid': False,
                'error': '模板不存在'
            }