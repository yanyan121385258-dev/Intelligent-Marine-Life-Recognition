"""
Django代码生成器主入口类

该模块提供了一个统一的Django代码生成器入口，
整合了模型、序列化器、视图、URL路由等所有生成器功能。

使用示例:
    generator = DjangoCodeGenerator()
    
    # 生成完整的CRUD模块
    generator.generate_full_module(
        model_name='User',
        fields=[
            {'name': 'username', 'type': 'CharField', 'max_length': 150},
            {'name': 'email', 'type': 'EmailField'},
            {'name': 'phone', 'type': 'CharField', 'max_length': 20}
        ],
        output_dir='./generated_code'
    )
"""

import os
from typing import Dict, List, Optional, Any
from .base_generator import BaseGenerator
from .model_generator import ModelGenerator
from .serializer_generator import SerializerGenerator
from .view_generator import ViewGenerator
from .url_generator import URLGenerator
from .yaml_parser import YAMLParser


class DjangoCodeGenerator(BaseGenerator):
    """Django代码生成器主入口类"""
    
    def __init__(self):
        """初始化Django代码生成器"""
        super().__init__()
        self.model_generator = ModelGenerator()
        self.serializer_generator = SerializerGenerator()
        self.view_generator = ViewGenerator()
        self.url_generator = URLGenerator()
        self.yaml_parser = YAMLParser()
    
    def generate(self, **kwargs) -> str:
        """
        实现抽象方法generate
        
        Returns:
            str: 生成的代码字符串
        """
        return "Django代码生成器"
    
    def generate_full_module(
        self,
        model_name: str,
        fields: List[Dict[str, Any]],
        output_dir: str = './generated_code',
        app_name: str = None,
        operations: List[str] = None,
        permissions: List[str] = None,
        validators: Optional[Dict[str, str]] = None,
        table_name: str = None,
        verbose_name: str = None,
        ordering: List[str] = None
    ) -> Dict[str, str]:
        """
        生成完整的Django模块代码（模型、序列化器、视图、URL）
        
        Args:
            model_name: 模型名称
            fields: 字段配置列表
            output_dir: 输出目录
            app_name: 应用名称
            operations: 支持的操作列表
            permissions: 权限装饰器列表
            validators: 字段验证器映射
            table_name: 数据库表名
            verbose_name: 模型显示名称
            ordering: 默认排序字段
            
        Returns:
            Dict[str, str]: 生成的代码文件映射
        """
        if operations is None:
            operations = ['create', 'read', 'update', 'delete', 'list']
        
        if not app_name:
            app_name = self.to_snake_case(model_name)
        
        generated_files = {}
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成模型代码
        model_code = self.generate_model(
            model_name=model_name,
            fields=fields,
            table_name=table_name,
            verbose_name=verbose_name,
            ordering=ordering
        )
        generated_files['models.py'] = model_code
        
        # 生成序列化器代码
        serializer_code = self.generate_serializers(
            model_name=model_name,
            fields=[field['name'] for field in fields],
            validators=validators
        )
        generated_files['serializers.py'] = serializer_code
        
        # 生成视图代码
        view_code = self.generate_views(
            model_name=model_name,
            operations=operations,
            permissions=permissions
        )
        generated_files['views.py'] = view_code
        
        # 生成URL路由代码
        url_code = self.generate_urls(
            model_name=model_name,
            operations=operations,
            app_name=app_name
        )
        generated_files['urls.py'] = url_code
        
        # 写入文件
        for filename, code in generated_files.items():
            file_path = os.path.join(output_dir, filename)
            self.write_to_file(file_path, code)
        
        return generated_files
    
    def generate_model(
        self,
        model_name: str,
        fields: List[Dict[str, Any]],
        table_name: str = None,
        verbose_name: str = None,
        ordering: List[str] = None,
        status_choices: List[tuple] = None
    ) -> str:
        """
        生成模型代码
        
        Args:
            model_name: 模型名称
            fields: 字段配置列表
            table_name: 数据库表名
            verbose_name: 模型显示名称
            ordering: 默认排序字段
            status_choices: 状态选择项
            
        Returns:
            str: 生成的模型代码
        """
        return self.model_generator.generate(
            model_name=model_name,
            fields=fields,
            table_name=table_name,
            verbose_name=verbose_name,
            ordering=ordering,
            status_choices=status_choices
        )
    
    def generate_serializers(
        self,
        model_name: str,
        fields: List[str],
        validators: Optional[Dict[str, str]] = None,
        create_fields: Optional[List[str]] = None,
        update_fields: Optional[List[str]] = None,
        list_fields: Optional[List[str]] = None
    ) -> str:
        """
        生成序列化器代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表
            validators: 字段验证器映射
            create_fields: 创建时使用的字段
            update_fields: 更新时使用的字段
            list_fields: 列表时显示的字段
            
        Returns:
            str: 生成的序列化器代码
        """
        return self.serializer_generator.generate(
            model_name=model_name,
            fields=fields,
            create_fields=create_fields,
            update_fields=update_fields,
            list_fields=list_fields,
            validators=validators
        )
    
    def generate_views(
        self,
        model_name: str,
        operations: List[str] = None,
        permissions: List[str] = None,
        filters: Optional[List[str]] = None,
        ordering: Optional[List[str]] = None,
        search_fields: Optional[List[str]] = None,
        pagination: bool = True
    ) -> str:
        """
        生成视图代码
        
        Args:
            model_name: 模型名称
            operations: 支持的操作列表
            permissions: 权限装饰器列表
            filters: 过滤字段列表
            ordering: 排序字段列表
            search_fields: 搜索字段列表
            pagination: 是否启用分页
            
        Returns:
            str: 生成的视图代码
        """
        if operations is None:
            operations = ['create', 'read', 'update', 'delete', 'list']
        
        return self.view_generator.generate(
            model_name=model_name,
            operations=operations,
            permissions=permissions,
            filters=filters,
            ordering=ordering,
            search_fields=search_fields,
            pagination=pagination
        )
    
    def generate_urls(
        self,
        model_name: str,
        operations: List[str] = None,
        prefix: str = '',
        app_name: str = '',
        namespace: str = ''
    ) -> str:
        """
        生成URL路由代码
        
        Args:
            model_name: 模型名称
            operations: 支持的操作列表
            prefix: URL前缀
            app_name: 应用名称
            namespace: 命名空间
            
        Returns:
            str: 生成的URL路由代码
        """
        if operations is None:
            operations = ['create', 'read', 'update', 'delete', 'list']
        
        return self.url_generator.generate(
            model_name=model_name,
            operations=operations,
            prefix=prefix,
            app_name=app_name,
            namespace=namespace
        )
    
    def generate_api_module(
        self,
        model_name: str,
        fields: List[Dict[str, Any]],
        output_dir: str = './generated_api',
        version: str = 'v1',
        permissions: List[str] = None
    ) -> Dict[str, str]:
        """
        生成RESTful API模块代码
        
        Args:
            model_name: 模型名称
            fields: 字段配置列表
            output_dir: 输出目录
            version: API版本
            permissions: 权限装饰器列表
            
        Returns:
            Dict[str, str]: 生成的代码文件映射
        """
        generated_files = {}
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成模型代码
        model_code = self.generate_model(
            model_name=model_name,
            fields=fields
        )
        generated_files['models.py'] = model_code
        
        # 生成序列化器代码
        serializer_code = self.generate_serializers(
            model_name=model_name,
            fields=[field['name'] for field in fields]
        )
        generated_files['serializers.py'] = serializer_code
        
        # 生成API视图代码
        view_code = self.generate_views(
            model_name=model_name,
            permissions=permissions
        )
        generated_files['views.py'] = view_code
        
        # 生成API URL路由代码
        url_code = self.url_generator.generate_api_urls(
            model_name=model_name,
            version=version
        )
        generated_files['urls.py'] = url_code
        
        # 写入文件
        for filename, code in generated_files.items():
            file_path = os.path.join(output_dir, filename)
            self.write_to_file(file_path, code)
        
        return generated_files
    
    def generate_nested_module(
        self,
        parent_model: str,
        child_model: str,
        parent_fields: List[Dict[str, Any]],
        child_fields: List[Dict[str, Any]],
        output_dir: str = './generated_nested',
        relationship_type: str = 'foreign_key'
    ) -> Dict[str, str]:
        """
        生成嵌套资源模块代码
        
        Args:
            parent_model: 父模型名称
            child_model: 子模型名称
            parent_fields: 父模型字段配置
            child_fields: 子模型字段配置
            output_dir: 输出目录
            relationship_type: 关系类型 ('foreign_key', 'one_to_one', 'many_to_many')
            
        Returns:
            Dict[str, str]: 生成的代码文件映射
        """
        generated_files = {}
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 在子模型字段中添加父模型关系
        if relationship_type == 'foreign_key':
            child_fields.append({
                'name': self.to_snake_case(parent_model),
                'type': 'ForeignKey',
                'to': parent_model,
                'on_delete': 'models.CASCADE',
                'verbose_name': f'{parent_model}',
                'help_text': f'关联的{parent_model}'
            })
        
        # 生成父模型代码
        parent_model_code = self.generate_model(
            model_name=parent_model,
            fields=parent_fields
        )
        generated_files[f'{self.to_snake_case(parent_model)}_models.py'] = parent_model_code
        
        # 生成子模型代码
        child_model_code = self.generate_model(
            model_name=child_model,
            fields=child_fields
        )
        generated_files[f'{self.to_snake_case(child_model)}_models.py'] = child_model_code
        
        # 生成嵌套URL路由
        nested_url_code = self.url_generator.generate_nested_urls(
            parent_model=parent_model,
            child_model=child_model
        )
        generated_files['nested_urls.py'] = nested_url_code
        
        # 写入文件
        for filename, code in generated_files.items():
            file_path = os.path.join(output_dir, filename)
            self.write_to_file(file_path, code)
        
        return generated_files
    
    def generate_app_structure(
        self,
        app_name: str,
        models: List[Dict[str, Any]],
        output_dir: str = None
    ) -> Dict[str, str]:
        """
        生成完整的Django应用结构
        
        Args:
            app_name: 应用名称
            models: 模型配置列表
            output_dir: 输出目录
            
        Returns:
            Dict[str, str]: 生成的代码文件映射
        """
        if not output_dir:
            output_dir = f'./generated_{app_name}'
        
        generated_files = {}
        
        # 创建应用目录结构
        app_dir = os.path.join(output_dir, app_name)
        os.makedirs(app_dir, exist_ok=True)
        os.makedirs(os.path.join(app_dir, 'serializers'), exist_ok=True)
        os.makedirs(os.path.join(app_dir, 'views'), exist_ok=True)
        os.makedirs(os.path.join(app_dir, 'urls'), exist_ok=True)
        
        # 生成应用配置文件
        apps_code = self._generate_apps_config(app_name)
        generated_files['apps.py'] = apps_code
        
        # 生成__init__.py文件
        generated_files['__init__.py'] = ''
        generated_files['serializers/__init__.py'] = ''
        generated_files['views/__init__.py'] = ''
        generated_files['urls/__init__.py'] = ''
        
        # 为每个模型生成代码
        all_models_code = []
        all_serializers_code = []
        all_views_code = []
        all_urls_code = []
        
        for model_config in models:
            model_name = model_config['name']
            fields = model_config['fields']
            
            # 生成模型代码
            model_code = self.generate_model(
                model_name=model_name,
                fields=fields,
                verbose_name=model_config.get('verbose_name', model_name),
                table_name=model_config.get('table_name'),
                ordering=model_config.get('ordering', ['-created_at'])
            )
            all_models_code.append(model_code)
            
            # 生成序列化器代码
            serializer_code = self.generate_serializers(
                model_name=model_name,
                fields=[field['name'] for field in fields],
                validators=model_config.get('validators', {})
            )
            all_serializers_code.append(serializer_code)
            
            # 生成视图代码
            view_code = self.generate_views(
                model_name=model_name,
                operations=model_config.get('operations', ['create', 'read', 'update', 'delete', 'list']),
                permissions=model_config.get('permissions', [])
            )
            all_views_code.append(view_code)
            
            # 生成URL代码
            url_code = self.generate_urls(
                model_name=model_name,
                app_name=app_name,
                operations=model_config.get('operations', ['create', 'read', 'update', 'delete', 'list'])
            )
            all_urls_code.append(url_code)
        
        # 合并所有代码
        generated_files['models.py'] = '\n\n'.join(all_models_code)
        generated_files['serializers.py'] = '\n\n'.join(all_serializers_code)
        generated_files['views.py'] = '\n\n'.join(all_views_code)
        generated_files['urls.py'] = '\n\n'.join(all_urls_code)
        
        # 写入文件
        for filename, code in generated_files.items():
            file_path = os.path.join(app_dir, filename)
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.write_to_file(file_path, code)
        
        return generated_files
    
    def _generate_apps_config(self, app_name: str) -> str:
        """生成Django应用配置代码"""
        class_name = self.snake_to_camel(app_name) + 'Config'
        
        code_parts = [
            'from django.apps import AppConfig',
            '',
            f'class {class_name}(AppConfig):',
            '    """',
            f'    {app_name}应用配置',
            '    """',
            "    default_auto_field = 'django.db.models.BigAutoField'",
            f"    name = '{app_name}'",
            f"    verbose_name = '{app_name.title()}'"
        ]
        
        return '\n'.join(code_parts)
    
    def generate_from_yaml_file(self, yaml_file_path: str) -> Dict[str, str]:
        """
        从YAML配置文件生成Django应用代码
        
        Args:
            yaml_file_path: YAML配置文件路径
            
        Returns:
            Dict[str, str]: 生成的文件路径和内容映射
            
        Raises:
            FileNotFoundError: 当YAML文件不存在时
            ValueError: 当配置验证失败时
        """
        # 解析YAML配置
        config = self.yaml_parser.parse_yaml_file(yaml_file_path)
        
        # 从配置生成代码
        return self.generate_from_yaml_config(config)
    
    def generate_from_yaml_config(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        从YAML配置字典生成Django应用代码
        
        Args:
            config: YAML配置字典
            
        Returns:
            Dict[str, str]: 生成的文件路径和内容映射
        """
        app_name = config['app_name']
        models = config['models']
        output_dir = config.get('output_dir', '.')  # 默认输出到当前目录
        
        all_generated_files = {}
        
        # 为每个模型生成代码
        if isinstance(models, dict):
            # 如果models是字典格式
            models_items = models.items()
        else:
            # 如果models是列表格式，转换为字典格式
            models_items = [(model['name'], model) for model in models]
            
        for model_name, model_config in models_items:
            # 获取模型字段配置
            fields = model_config.get('fields', [])
            operations = model_config.get('operations', ['create', 'get', 'update', 'delete', 'list'])
            permissions = model_config.get('permissions', {})
            api_config = model_config.get('api', {})
            
            # 转换字段格式
            processed_fields = {}
            for field in fields:
                field_name = field['name']
                processed_fields[field_name] = {
                    'type': field['type'],
                    'verbose_name': field.get('verbose_name', field_name),
                    'help_text': field.get('help_text', f'{field_name}字段'),
                }
                
                # 添加其他字段属性
                for attr in ['max_length', 'null', 'blank', 'default', 'unique', 'choices']:
                    if attr in field:
                        processed_fields[field_name][attr] = field[attr]
            
            # 创建应用目录
            app_dir = os.path.join(output_dir, app_name)
            print(f"📁 创建应用目录: {app_dir}")
            os.makedirs(app_dir, exist_ok=True)
            
            # 创建migrations子目录
            migrations_dir = os.path.join(app_dir, 'migrations')
            print(f"📁 创建子目录: {migrations_dir}")
            os.makedirs(migrations_dir, exist_ok=True)
            # 创建migrations/__init__.py文件
            migrations_init_file = os.path.join(migrations_dir, '__init__.py')
            with open(migrations_init_file, 'w', encoding='utf-8') as f:
                f.write('')
            all_generated_files[migrations_init_file] = ''
            
            # 生成模型代码
            print(f"📝 生成模型代码...")
            model_code = self.model_generator.generate(model_name, processed_fields)
            model_file = os.path.join(app_dir, 'models.py')
            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(model_code)
            all_generated_files[model_file] = model_code
            print(f"✅ 已生成: {model_file}")
            
            # 生成序列化器代码
            print(f"📝 生成序列化器代码...")
            serializer_code = self.serializer_generator.generate(model_name, processed_fields)
            serializer_file = os.path.join(app_dir, 'serializers.py')
            with open(serializer_file, 'w', encoding='utf-8') as f:
                f.write(serializer_code)
            all_generated_files[serializer_file] = serializer_code
            print(f"✅ 已生成: {serializer_file}")
            
            # 生成视图代码
            print(f"📝 生成视图代码...")
            view_code = self.view_generator.generate(model_name, operations)
            view_file = os.path.join(app_dir, 'views.py')
            with open(view_file, 'w', encoding='utf-8') as f:
                f.write(view_code)
            all_generated_files[view_file] = view_code
            print(f"✅ 已生成: {view_file}")
            
            # 生成URL代码
            print(f"📝 生成URL代码...")
            url_code = self.url_generator.generate(model_name, operations)
            url_file = os.path.join(app_dir, 'urls.py')
            with open(url_file, 'w', encoding='utf-8') as f:
                f.write(url_code)
            all_generated_files[url_file] = url_code
            print(f"✅ 已生成: {url_file}")
            
            # 生成应用配置文件
            print(f"📝 生成应用配置文件...")
            apps_code = self._generate_apps_config(app_name)
            apps_file = os.path.join(app_dir, 'apps.py')
            with open(apps_file, 'w', encoding='utf-8') as f:
                f.write(apps_code)
            all_generated_files[apps_file] = apps_code
            print(f"✅ 已生成: {apps_file}")
            
            # 生成__init__.py文件
            init_file = os.path.join(app_dir, '__init__.py')
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('')
            all_generated_files[init_file] = ''
            print(f"✅ 已生成: {init_file}")
            
            # 生成migrations的__init__.py
            migrations_init = os.path.join(app_dir, 'migrations', '__init__.py')
            with open(migrations_init, 'w', encoding='utf-8') as f:
                f.write('')
            all_generated_files[migrations_init] = ''
            print(f"✅ 已生成: {migrations_init}")
        
        print(f"\n🎉 Django应用 '{app_name}' 生成完成!")
        print(f"📁 输出目录: {os.path.abspath(output_dir)}")
        print(f"📄 生成文件数量: {len(all_generated_files)}")
        
        return all_generated_files
    
    def generate_yaml_template(self, output_path: str = 'app_template.yaml') -> str:
        """
        生成YAML配置文件模板
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            str: 生成的模板内容
        """
        return self.yaml_parser.generate_yaml_template(output_path)
    
    def validate_yaml_config(self, yaml_file_path: str) -> bool:
        """
        验证YAML配置文件格式
        
        Args:
            yaml_file_path: YAML配置文件路径
            
        Returns:
            bool: 验证是否通过
        """
        try:
            self.yaml_parser.parse_yaml_file(yaml_file_path)
            return True
        except Exception as e:
            print(f"YAML配置验证失败: {e}")
            return False