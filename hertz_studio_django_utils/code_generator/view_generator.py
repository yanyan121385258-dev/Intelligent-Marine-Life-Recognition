"""
Django视图代码生成器

该模块负责根据配置生成Django REST Framework视图代码
"""

import os
from typing import Dict, List, Any, Optional
from .base_generator import BaseGenerator


class ViewGenerator(BaseGenerator):
    """Django视图代码生成器"""
    
    def __init__(self):
        """初始化视图生成器"""
        super().__init__()
    
    def generate(self, model_name: str = None, operations: List[str] = None, **kwargs) -> str:
        """
        生成Django视图代码
        
        Args:
            model_name: 模型名称
            operations: 支持的操作列表
            **kwargs: 其他参数
            
        Returns:
            str: 生成的视图代码
        """
        # 处理参数，支持位置参数和关键字参数
        if model_name is None:
            model_name = kwargs.get('model_name', 'DefaultModel')
        if operations is None:
            operations = kwargs.get('operations', ['list', 'create', 'retrieve', 'update', 'delete'])
            
        permissions = kwargs.get('permissions', {})
        authentication = kwargs.get('authentication', ['IsAuthenticated'])
        pagination = kwargs.get('pagination', True)
        filters = kwargs.get('filters', {})
        permission_type = kwargs.get('permission_type', 'standard')  # 'standard' 或 'system'
        
        # 确保operations是列表
        if isinstance(operations, str):
            operations = [operations]
        
        # 自动生成权限配置
        if not permissions and permission_type:
            if permission_type == 'system':
                permissions = self.generate_system_permission_config(model_name, operations)
            else:
                permissions = self.generate_permission_config(model_name, operations)
        
        # 准备模板上下文
        context = {
            'model_name': model_name,
            'model_name_lower': model_name.lower(),
            'operations': operations,
            'permissions': permissions,
            'permissions_list': permissions,  # 为了兼容模板
            'authentication': authentication,
            'pagination': pagination,
            'filters': filters,
            'has_create': 'create' in operations,
            'has_list': 'list' in operations,
            'has_retrieve': 'retrieve' in operations,
            'has_update': 'update' in operations,
            'has_delete': 'delete' in operations,
            'viewset_name': f'{model_name}ViewSet',
            'serializer_name': f'{model_name}Serializer',
            'queryset_name': f'{model_name}.objects.all()',
            'view_classes': []
        }
        
        # 生成视图类列表
        for operation in operations:
            if operation == 'list':
                context['view_classes'].append({
                    'name': f'{model_name}ListView',
                    'base_class': 'ListAPIView',
                    'operation': 'list'
                })
            elif operation == 'create':
                context['view_classes'].append({
                    'name': f'{model_name}CreateView',
                    'base_class': 'CreateAPIView',
                    'operation': 'create'
                })
            elif operation == 'retrieve' or operation == 'get':
                context['view_classes'].append({
                    'name': f'{model_name}DetailView',
                    'base_class': 'RetrieveAPIView',
                    'operation': 'retrieve'
                })
            elif operation == 'update':
                context['view_classes'].append({
                    'name': f'{model_name}UpdateView',
                    'base_class': 'UpdateAPIView',
                    'operation': 'update'
                })
            elif operation == 'delete':
                context['view_classes'].append({
                    'name': f'{model_name}DeleteView',
                    'base_class': 'DestroyAPIView',
                    'operation': 'delete'
                })
        
        # 渲染模板
        return self.render_template('django/views.mako', context)
    
    def generate_api_view(
        self,
        model_name: str,
        view_name: str,
        http_methods: List[str],
        permissions: Optional[List[str]] = None,
        authentication: Optional[List[str]] = None
    ) -> str:
        """
        生成API视图代码
        
        Args:
            model_name: 模型名称
            view_name: 视图名称
            http_methods: HTTP方法列表
            permissions: 权限列表
            authentication: 认证方式列表
            
        Returns:
            str: 生成的API视图代码
        """
        context = {
            'model_name': model_name,
            'view_name': view_name,
            'http_methods': http_methods,
            'permissions': permissions or [],
            'authentication': authentication or [],
            'view_type': 'api_view'
        }
        
        return self.render_template('django/views.mako', context)
    
    def generate_viewset(
        self,
        model_name: str,
        viewset_type: str = 'ModelViewSet',
        operations: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成ViewSet代码
        
        Args:
            model_name: 模型名称
            viewset_type: ViewSet类型
            operations: 支持的操作列表
            permissions: 权限列表
            filters: 过滤器配置
            
        Returns:
            str: 生成的ViewSet代码
        """
        if operations is None:
            operations = ['list', 'create', 'retrieve', 'update', 'destroy']
        
        context = {
            'model_name': model_name,
            'viewset_type': viewset_type,
            'operations': operations,
            'permissions': permissions or [],
            'filters': filters or {},
            'view_type': 'viewset'
        }
        
        return self.render_template('django/views.mako', context)
    
    def generate_generic_view(
        self,
        model_name: str,
        view_type: str,
        permissions: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成通用视图代码
        
        Args:
            model_name: 模型名称
            view_type: 视图类型 (ListAPIView, CreateAPIView等)
            permissions: 权限列表
            filters: 过滤器配置
            
        Returns:
            str: 生成的通用视图代码
        """
        context = {
            'model_name': model_name,
            'view_type': view_type,
            'permissions': permissions or [],
            'filters': filters or {},
            'generic_view': True
        }
        
        return self.render_template('django/views.mako', context)
    
    def generate_crud_views(
        self,
        model_name: str,
        operations: List[str],
        permissions: Optional[Dict[str, List[str]]] = None,
        pagination: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成CRUD视图代码
        
        Args:
            model_name: 模型名称
            operations: 支持的操作列表
            permissions: 每个操作的权限配置
            pagination: 是否启用分页
            filters: 过滤器配置
            
        Returns:
            str: 生成的CRUD视图代码
        """
        context = {
            'model_name': model_name,
            'operations': operations,
            'permissions': permissions or {},
            'pagination': pagination,
            'filters': filters or {},
            'crud_views': True
        }
        
        return self.render_template('django/views.mako', context)
    
    def generate_custom_action(
        self,
        action_name: str,
        http_methods: List[str],
        detail: bool = False,
        permissions: Optional[List[str]] = None,
        serializer_class: Optional[str] = None
    ) -> str:
        """
        生成自定义动作代码
        
        Args:
            action_name: 动作名称
            http_methods: HTTP方法列表
            detail: 是否为详情动作
            permissions: 权限列表
            serializer_class: 序列化器类名
            
        Returns:
            str: 生成的自定义动作代码
        """
        context = {
            'action_name': action_name,
            'http_methods': http_methods,
            'detail': detail,
            'permissions': permissions or [],
            'serializer_class': serializer_class,
            'custom_action': True
        }
        
        return self.render_template('django/views.mako', context)
    
    def add_permission_decorator(
        self,
        view_code: str,
        permissions: List[str]
    ) -> str:
        """
        添加权限装饰器
        
        Args:
            view_code: 原视图代码
            permissions: 权限列表
            
        Returns:
            str: 包含权限装饰器的视图代码
        """
        decorators = []
        for permission in permissions:
            if permission == 'login_required':
                decorators.append('@login_required')
            elif permission == 'no_login_required':
                decorators.append('@no_login_required')
            else:
                decorators.append(f'@permission_required("{permission}")')
        
        # 在函数定义前添加装饰器
        lines = view_code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                # 在函数或类定义前插入装饰器
                for j, decorator in enumerate(decorators):
                    lines.insert(i + j, decorator)
                break
        
        return '\n'.join(lines)
    
    def generate_permission_config(
        self,
        model_name: str,
        operations: List[str],
        permission_prefix: str = None
    ) -> Dict[str, str]:
        """
        生成权限配置字典
        
        Args:
            model_name: 模型名称
            operations: 操作列表
            permission_prefix: 权限前缀，默认使用模型名称小写
            
        Returns:
            Dict[str, str]: 权限配置字典
        """
        if permission_prefix is None:
            permission_prefix = model_name.lower()
        
        # 统一权限映射规则，与菜单生成器保持一致
        permission_mapping = {
            'list': f'{permission_prefix}:list',
            'create': f'{permission_prefix}:add',      # 改为add，与菜单一致
            'retrieve': f'{permission_prefix}:list',   # 改为list，与菜单一致
            'get': f'{permission_prefix}:list',        # 改为list，与菜单一致
            'update': f'{permission_prefix}:edit',     # 改为edit，与菜单一致
            'delete': f'{permission_prefix}:remove',   # 改为remove，与菜单一致
            'partial_update': f'{permission_prefix}:edit'  # 改为edit，与菜单一致
        }
        
        return {op: permission_mapping.get(op, f'{permission_prefix}:{op}') for op in operations}
    
    def generate_system_permission_config(
        self,
        model_name: str,
        operations: List[str],
        module_prefix: str = 'system'
    ) -> Dict[str, str]:
        """
        生成系统级权限配置字典
        
        Args:
            model_name: 模型名称
            operations: 操作列表
            module_prefix: 模块前缀，默认为'system'
            
        Returns:
            Dict[str, str]: 系统级权限配置字典
        """
        model_lower = model_name.lower()
        
        permission_mapping = {
            'list': f'{module_prefix}:{model_lower}:list',
            'create': f'{model_lower}:create',
            'retrieve': f'{module_prefix}:{model_lower}:query',
            'get': f'{module_prefix}:{model_lower}:query',
            'update': f'{model_lower}:update',
            'delete': f'{model_lower}:delete',
            'partial_update': f'{model_lower}:update'
        }
        
        return {op: permission_mapping.get(op, f'{module_prefix}:{model_lower}:{op}') for op in operations}
    
    def add_swagger_documentation(
        self,
        view_code: str,
        operation_id: str,
        summary: str,
        description: str,
        tags: List[str],
        request_schema: Optional[str] = None,
        response_schema: Optional[str] = None
    ) -> str:
        """
        添加Swagger文档注解
        
        Args:
            view_code: 原视图代码
            operation_id: 操作ID
            summary: 摘要
            description: 描述
            tags: 标签列表
            request_schema: 请求模式
            response_schema: 响应模式
            
        Returns:
            str: 包含Swagger文档的视图代码
        """
        swagger_decorator = f"""@extend_schema(
    operation_id='{operation_id}',
    summary='{summary}',
    description='{description}',
    tags={tags}"""
        
        if request_schema:
            swagger_decorator += f",\n    request={request_schema}"
        
        if response_schema:
            swagger_decorator += f",\n    responses={{200: {response_schema}}}"
        
        swagger_decorator += "\n)"
        
        # 在函数定义前添加装饰器
        lines = view_code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                lines.insert(i, swagger_decorator)
                break
        
        return '\n'.join(lines)