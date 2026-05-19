"""
Django应用代码生成器

该模块负责根据配置生成完整的Django应用代码
"""

import os
from typing import Dict, List, Any, Optional
from .base_generator import BaseGenerator
from .model_generator import ModelGenerator
from .serializer_generator import SerializerGenerator
from .view_generator import ViewGenerator
from .url_generator import URLGenerator


class AppGenerator(BaseGenerator):
    """Django应用代码生成器"""
    
    def __init__(self):
        """初始化应用生成器"""
        super().__init__()
        self.model_generator = ModelGenerator()
        self.serializer_generator = SerializerGenerator()
        self.view_generator = ViewGenerator()
        self.url_generator = URLGenerator()
    
    def generate(self, app_name: str = None, models: List[Dict[str, Any]] = None, **kwargs) -> Dict[str, str]:
        """
        生成完整的Django应用代码
        
        Args:
            app_name: 应用名称
            models: 模型配置列表
            **kwargs: 其他参数
            
        Returns:
            Dict[str, str]: 生成的文件代码映射
        """
        # 处理参数
        if app_name is None:
            app_name = kwargs.get('app_name', 'default_app')
        if models is None:
            models = kwargs.get('models', [])
            
        api_version = kwargs.get('api_version', 'v1')
        include_admin = kwargs.get('include_admin', True)
        include_tests = kwargs.get('include_tests', True)
        
        generated_files = {}
        
        # 生成应用配置文件
        generated_files['apps.py'] = self.generate_apps_config(app_name)
        
        # 生成__init__.py文件
        generated_files['__init__.py'] = self.generate_init_file(app_name)
        
        # 生成模型、序列化器、视图和URL
        all_models = []
        for model_config in models:
            model_name = model_config.get('name', 'DefaultModel')
            fields = model_config.get('fields', [])
            operations = model_config.get('operations', ['list', 'create', 'retrieve', 'update', 'delete'])
            
            # 生成模型代码
            model_code = self.model_generator.generate(
                model_name=model_name,
                fields=fields,
                **model_config
            )
            
            # 生成序列化器代码
            serializer_code = self.serializer_generator.generate(
                model_name=model_name,
                fields=fields
            )
            
            # 生成视图代码
            view_code = self.view_generator.generate(
                model_name=model_name,
                operations=operations
            )
            
            # 生成URL代码
            url_code = self.url_generator.generate(
                model_name=model_name,
                operations=operations,
                app_name=app_name
            )
            
            # 添加到生成的文件中
            generated_files[f'models/{model_name.lower()}_models.py'] = model_code
            generated_files[f'serializers/{model_name.lower()}_serializers.py'] = serializer_code
            generated_files[f'views/{model_name.lower()}_views.py'] = view_code
            generated_files[f'urls/{model_name.lower()}_urls.py'] = url_code
            
            all_models.append(model_name)
        
        # 生成主要文件
        generated_files['models.py'] = self.generate_models_init(all_models)
        generated_files['serializers/__init__.py'] = self.generate_serializers_init(all_models)
        generated_files['views/__init__.py'] = self.generate_views_init(all_models)
        generated_files['urls.py'] = self.generate_main_urls(app_name, all_models, api_version)
        
        # 生成管理后台文件
        if include_admin:
            generated_files['admin.py'] = self.generate_admin_config(all_models)
        
        # 生成测试文件
        if include_tests:
            generated_files['tests.py'] = self.generate_tests(all_models)
        
        return generated_files
    
    def generate_apps_config(self, app_name: str) -> str:
        """生成应用配置文件"""
        context = {
            'app_name': app_name,
            'app_label': app_name.replace('studio_django_', ''),
            'verbose_name': app_name.replace('_', ' ').title()
        }
        return self.render_template('django/apps.mako', context)
    
    def generate_init_file(self, app_name: str) -> str:
        """生成__init__.py文件"""
        return f'"""\n{app_name} Django应用\n"""\n\ndefault_app_config = \'{app_name}.apps.{app_name.title().replace("_", "")}Config\'\n'
    
    def generate_models_init(self, models: List[str]) -> str:
        """生成models.py主文件"""
        imports = []
        for model in models:
            imports.append(f'from .models.{model.lower()}_models import {model}')
        
        context = {
            'imports': imports,
            'models': models
        }
        return self.render_template('django/models_init.mako', context)
    
    def generate_serializers_init(self, models: List[str]) -> str:
        """生成serializers/__init__.py文件"""
        imports = []
        for model in models:
            imports.append(f'from .{model.lower()}_serializers import {model}Serializer')
        
        return '\n'.join(imports) + '\n'
    
    def generate_views_init(self, models: List[str]) -> str:
        """生成views/__init__.py文件"""
        imports = []
        for model in models:
            imports.append(f'from .{model.lower()}_views import {model}ViewSet')
        
        return '\n'.join(imports) + '\n'
    
    def generate_main_urls(self, app_name: str, models: List[str], api_version: str) -> str:
        """生成主URL配置文件"""
        context = {
            'app_name': app_name,
            'models': models,
            'api_version': api_version,
            'url_includes': [f'path(\'{model.lower()}/\', include(\'{app_name}.urls.{model.lower()}_urls\'))' for model in models]
        }
        return self.render_template('django/main_urls.mako', context)
    
    def generate_admin_config(self, models: List[str]) -> str:
        """生成管理后台配置"""
        context = {
            'models': models
        }
        return self.render_template('django/admin.mako', context)
    
    def generate_tests(self, models: List[str]) -> str:
        """生成测试文件"""
        context = {
            'models': models
        }
        return self.render_template('django/tests.mako', context)
    
    def generate_full_app(
        self,
        app_name: str,
        models: List[Dict[str, Any]],
        output_dir: str = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        生成完整的Django应用并写入文件
        
        Args:
            app_name: 应用名称
            models: 模型配置列表
            output_dir: 输出目录
            **kwargs: 其他参数
            
        Returns:
            Dict[str, str]: 生成的文件路径映射
        """
        generated_files = self.generate(app_name, models, **kwargs)
        
        if output_dir:
            file_paths = {}
            for file_name, content in generated_files.items():
                file_path = os.path.join(output_dir, app_name, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                file_paths[file_name] = file_path
            
            return file_paths
        
        return generated_files
    
    def generate_django_project(
        self,
        project_name: str,
        apps: List[Dict[str, Any]],
        output_dir: str = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        生成完整的Django项目
        
        Args:
            project_name: 项目名称
            apps: 应用配置列表
            output_dir: 输出目录
            **kwargs: 其他参数
            
        Returns:
            Dict[str, str]: 生成的文件路径映射
        """
        generated_files = {}
        
        # 生成项目配置文件
        generated_files['manage.py'] = self.generate_manage_py(project_name)
        generated_files[f'{project_name}/settings.py'] = self.generate_settings(project_name, apps)
        generated_files[f'{project_name}/urls.py'] = self.generate_project_urls(project_name, apps)
        generated_files[f'{project_name}/wsgi.py'] = self.generate_wsgi(project_name)
        generated_files[f'{project_name}/asgi.py'] = self.generate_asgi(project_name)
        generated_files[f'{project_name}/__init__.py'] = ''
        
        # 生成每个应用
        for app_config in apps:
            app_name = app_config.get('name', 'default_app')
            models = app_config.get('models', [])
            
            app_files = self.generate(app_name, models, **app_config)
            for file_name, content in app_files.items():
                generated_files[f'{app_name}/{file_name}'] = content
        
        return generated_files
    
    def generate_manage_py(self, project_name: str) -> str:
        """生成manage.py文件"""
        context = {'project_name': project_name}
        return self.render_template('django/manage.mako', context)
    
    def generate_settings(self, project_name: str, apps: List[Dict[str, Any]]) -> str:
        """生成settings.py文件"""
        app_names = [app.get('name', 'default_app') for app in apps]
        context = {
            'project_name': project_name,
            'apps': app_names
        }
        return self.render_template('django/settings.mako', context)
    
    def generate_project_urls(self, project_name: str, apps: List[Dict[str, Any]]) -> str:
        """生成项目主URL配置"""
        app_names = [app.get('name', 'default_app') for app in apps]
        context = {
            'project_name': project_name,
            'apps': app_names
        }
        return self.render_template('django/project_urls.mako', context)
    
    def generate_wsgi(self, project_name: str) -> str:
        """生成WSGI配置"""
        context = {'project_name': project_name}
        return self.render_template('django/wsgi.mako', context)
    
    def generate_asgi(self, project_name: str) -> str:
        """生成ASGI配置"""
        context = {'project_name': project_name}
        return self.render_template('django/asgi.mako', context)