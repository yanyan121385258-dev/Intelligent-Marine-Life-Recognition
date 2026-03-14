"""
Django URL配置代码生成器

该模块负责根据配置生成Django URL路由代码
"""

import os
from typing import Dict, List, Any, Optional
from .base_generator import BaseGenerator


class URLGenerator(BaseGenerator):
    """Django URL配置代码生成器"""
    
    def __init__(self):
        """初始化URL生成器"""
        super().__init__()
    
    def generate(self, model_name: str = None, operations: List[str] = None, app_name: str = None, **kwargs) -> str:
        """
        生成Django URL配置代码
        
        Args:
            model_name: 模型名称
            operations: 支持的操作列表
            app_name: 应用名称
            **kwargs: 其他参数
            
        Returns:
            str: 生成的URL配置代码
        """
        # 处理参数，支持位置参数和关键字参数
        if model_name is None:
            model_name = kwargs.get('model_name', 'DefaultModel')
        if operations is None:
            operations = kwargs.get('operations', ['list', 'create', 'retrieve', 'update', 'delete'])
        if app_name is None:
            app_name = kwargs.get('app_name', 'default_app')
            
        api_version = kwargs.get('api_version', 'v1')
        prefix = kwargs.get('prefix', '')
        namespace = kwargs.get('namespace', app_name)
        
        # 确保operations是列表
        if isinstance(operations, str):
            operations = [operations]
        
        # 准备模板上下文
        context = {
            'app_name': app_name,
            'model_name': model_name,
            'model_name_lower': model_name.lower(),
            'snake_model_name': model_name.lower(),  # 添加snake_model_name变量
            'operations': operations,
            'api_version': api_version,
            'prefix': prefix,
            'namespace': namespace,
            'has_create': 'create' in operations,
            'has_list': 'list' in operations,
            'has_retrieve': 'retrieve' in operations,
            'has_update': 'update' in operations,
            'has_delete': 'delete' in operations,
            'url_patterns': []
        }
        
        # 生成URL模式
        for operation in operations:
            if operation == 'list':
                context['url_patterns'].append({
                    'pattern': f'{model_name.lower()}/',
                    'view': f'list_{model_name.lower()}',
                    'name': f'{model_name.lower()}_list'
                })
            elif operation == 'create':
                context['url_patterns'].append({
                    'pattern': f'{model_name.lower()}/create/',
                    'view': f'create_{model_name.lower()}',
                    'name': f'{model_name.lower()}_create'
                })
            elif operation == 'retrieve' or operation == 'get':
                context['url_patterns'].append({
                    'pattern': f'{model_name.lower()}/<int:pk>/',
                    'view': f'get_{model_name.lower()}',
                    'name': f'{model_name.lower()}_detail'
                })
            elif operation == 'update':
                context['url_patterns'].append({
                    'pattern': f'{model_name.lower()}/<int:pk>/update/',
                    'view': f'update_{model_name.lower()}',
                    'name': f'{model_name.lower()}_update'
                })
            elif operation == 'delete':
                context['url_patterns'].append({
                    'pattern': f'{model_name.lower()}/<int:pk>/delete/',
                    'view': f'delete_{model_name.lower()}',
                    'name': f'{model_name.lower()}_delete'
                })
        
        # 渲染模板
        return self.render_template('django/urls.mako', context)
    
    def generate_rest_urls(
        self,
        app_name: str,
        model_name: str,
        viewset_name: Optional[str] = None,
        api_version: str = 'v1',
        namespace: Optional[str] = None
    ) -> str:
        """
        生成REST风格的URL配置
        
        Args:
            app_name: 应用名称
            model_name: 模型名称
            viewset_name: ViewSet名称
            api_version: API版本
            namespace: 命名空间
            
        Returns:
            str: 生成的REST URL配置代码
        """
        if viewset_name is None:
            viewset_name = f'{model_name}ViewSet'
        
        context = {
            'app_name': app_name,
            'model_name': model_name,
            'viewset_name': viewset_name,
            'api_version': api_version,
            'namespace': namespace,
            'url_type': 'rest'
        }
        
        return self.render_template('django/urls.mako', context)
    
    def generate_router_urls(
        self,
        app_name: str,
        viewsets: List[Dict[str, str]],
        api_version: str = 'v1',
        router_type: str = 'DefaultRouter'
    ) -> str:
        """
        生成使用Router的URL配置
        
        Args:
            app_name: 应用名称
            viewsets: ViewSet配置列表
            api_version: API版本
            router_type: Router类型
            
        Returns:
            str: 生成的Router URL配置代码
        """
        context = {
            'app_name': app_name,
            'viewsets': viewsets,
            'api_version': api_version,
            'router_type': router_type,
            'url_type': 'router'
        }
        
        return self.render_template('django/urls.mako', context)
    
    def generate_function_based_urls(
        self,
        app_name: str,
        views: List[Dict[str, Any]],
        api_version: str = 'v1'
    ) -> str:
        """
        生成基于函数视图的URL配置
        
        Args:
            app_name: 应用名称
            views: 视图配置列表
            api_version: API版本
            
        Returns:
            str: 生成的函数视图URL配置代码
        """
        context = {
            'app_name': app_name,
            'views': views,
            'api_version': api_version,
            'url_type': 'function_based'
        }
        
        return self.render_template('django/urls.mako', context)
    
    def generate_nested_urls(
        self,
        app_name: str,
        parent_model: str,
        child_model: str,
        operations: List[str],
        api_version: str = 'v1'
    ) -> str:
        """
        生成嵌套资源的URL配置
        
        Args:
            app_name: 应用名称
            parent_model: 父模型名称
            child_model: 子模型名称
            operations: 支持的操作列表
            api_version: API版本
            
        Returns:
            str: 生成的嵌套URL配置代码
        """
        context = {
            'app_name': app_name,
            'parent_model': parent_model,
            'child_model': child_model,
            'operations': operations,
            'api_version': api_version,
            'url_type': 'nested'
        }
        
        return self.render_template('django/urls.mako', context)
    
    def generate_custom_action_urls(
        self,
        app_name: str,
        model_name: str,
        actions: List[Dict[str, Any]],
        api_version: str = 'v1'
    ) -> str:
        """
        生成自定义动作的URL配置
        
        Args:
            app_name: 应用名称
            model_name: 模型名称
            actions: 自定义动作配置列表
            api_version: API版本
            
        Returns:
            str: 生成的自定义动作URL配置代码
        """
        context = {
            'app_name': app_name,
            'model_name': model_name,
            'actions': actions,
            'api_version': api_version,
            'url_type': 'custom_actions'
        }
        
        return self.render_template('django/urls.mako', context)
    
    def generate_app_urls(
        self,
        app_name: str,
        models: List[str],
        api_version: str = 'v1',
        include_admin: bool = False
    ) -> str:
        """
        生成应用级别的URL配置
        
        Args:
            app_name: 应用名称
            models: 模型名称列表
            api_version: API版本
            include_admin: 是否包含管理后台URL
            
        Returns:
            str: 生成的应用URL配置代码
        """
        context = {
            'app_name': app_name,
            'models': models,
            'api_version': api_version,
            'include_admin': include_admin,
            'url_type': 'app_level'
        }
        
        return self.render_template('django/urls.mako', context)
    
    def add_url_pattern(
        self,
        url_code: str,
        pattern: str,
        view: str,
        name: str,
        methods: Optional[List[str]] = None
    ) -> str:
        """
        添加URL模式
        
        Args:
            url_code: 原URL配置代码
            pattern: URL模式
            view: 视图名称
            name: URL名称
            methods: HTTP方法列表
            
        Returns:
            str: 包含新URL模式的配置代码
        """
        if methods:
            method_str = f", methods={methods}"
        else:
            method_str = ""
        
        new_pattern = f"    path('{pattern}', {view}, name='{name}'{method_str}),"
        
        # 在urlpatterns列表中添加新模式
        lines = url_code.split('\n')
        for i, line in enumerate(lines):
            if 'urlpatterns = [' in line:
                # 找到列表结束位置
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == ']':
                        lines.insert(j, new_pattern)
                        break
                break
        
        return '\n'.join(lines)
    
    def generate_api_documentation_urls(
        self,
        app_name: str,
        api_version: str = 'v1',
        include_swagger: bool = True,
        include_redoc: bool = True
    ) -> str:
        """
        生成API文档的URL配置
        
        Args:
            app_name: 应用名称
            api_version: API版本
            include_swagger: 是否包含Swagger UI
            include_redoc: 是否包含ReDoc
            
        Returns:
            str: 生成的API文档URL配置代码
        """
        context = {
            'app_name': app_name,
            'api_version': api_version,
            'include_swagger': include_swagger,
            'include_redoc': include_redoc,
            'url_type': 'api_docs'
        }
        
        return self.render_template('django/urls.mako', context)