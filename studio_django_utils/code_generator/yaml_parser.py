"""
YAML配置文件解析器

该模块负责解析YAML配置文件，将其转换为Django代码生成器可以使用的数据结构。

使用示例:
    parser = YAMLParser()
    config = parser.parse_yaml_file('app_config.yaml')
    generator = DjangoCodeGenerator()
    generator.generate_from_yaml_config(config)
"""

import yaml
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class YAMLParser:
    """YAML配置文件解析器"""
    
    def __init__(self):
        """初始化YAML解析器"""
        # 支持Django字段类型
        self.supported_field_types = {
            'CharField', 'TextField', 'IntegerField', 'FloatField',
            'DecimalField', 'BooleanField', 'DateField', 'DateTimeField',
            'EmailField', 'URLField', 'ImageField', 'FileField',
            'ForeignKey', 'ManyToManyField', 'OneToOneField', 'JSONField',
            'SlugField', 'PositiveIntegerField', 'BigIntegerField',
            'SmallIntegerField', 'UUIDField', 'TimeField',
            'GenericIPAddressField', 'BinaryField', 'DurationField',
            # 支持通用字段类型
            'string', 'text', 'integer', 'float', 'decimal', 'boolean',
            'date', 'datetime', 'email', 'url', 'image', 'file', 'json',
            'slug', 'uuid', 'time', 'ip', 'binary', 'duration'
        }
        
        # 通用字段类型到Django字段类型的映射
        self.field_type_mapping = {
            'string': 'CharField',
            'text': 'TextField',
            'integer': 'IntegerField',
            'float': 'FloatField',
            'decimal': 'DecimalField',
            'boolean': 'BooleanField',
            'date': 'DateField',
            'datetime': 'DateTimeField',
            'email': 'EmailField',
            'url': 'URLField',
            'image': 'ImageField',
            'file': 'FileField',
            'json': 'JSONField',
            'slug': 'SlugField',
            'uuid': 'UUIDField',
            'time': 'TimeField',
            'ip': 'GenericIPAddressField',
            'binary': 'BinaryField',
            'duration': 'DurationField'
        }
        
        self.supported_operations = {
            'create', 'read', 'update', 'delete', 'list', 'search', 'filter', 'get', 'retrieve'
        }
    
    def parse_yaml_file(self, yaml_file_path: str) -> Dict[str, Any]:
        """
        解析YAML配置文件
        
        Args:
            yaml_file_path: YAML文件路径
            
        Returns:
            Dict[str, Any]: 解析后的配置字典
            
        Raises:
            FileNotFoundError: 当文件不存在时
            yaml.YAMLError: 当YAML格式错误时
            ValueError: 当配置验证失败时
        """
        if not os.path.exists(yaml_file_path):
            raise FileNotFoundError(f"YAML配置文件不存在: {yaml_file_path}")
        
        try:
            with open(yaml_file_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML文件格式错误: {e}")
        
        # 验证配置结构
        validated_config = self._validate_config(config)
        return validated_config
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证YAML配置结构
        
        Args:
            config: 原始配置字典
            
        Returns:
            Dict[str, Any]: 验证后的配置字典
            
        Raises:
            ValueError: 当配置验证失败时
        """
        if not isinstance(config, dict):
            raise ValueError("YAML配置必须是字典格式")
        
        # 验证必需的顶级字段
        required_fields = ['app_name', 'models']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 验证应用名称
        app_name = config['app_name']
        if not isinstance(app_name, str) or not app_name.strip():
            raise ValueError("app_name必须是非空字符串")
        
        # 验证模型配置
        models = config['models']
        if isinstance(models, dict):
            # 如果models是字典格式，转换为列表格式
            models_list = []
            for model_name, model_config in models.items():
                model_config['name'] = model_name
                models_list.append(model_config)
            models = models_list
        elif not isinstance(models, list) or len(models) == 0:
            raise ValueError("models必须是非空列表或字典")
        
        validated_models = []
        for i, model in enumerate(models):
            validated_model = self._validate_model_config(model, i)
            validated_models.append(validated_model)
        
        # 构建验证后的配置
        validated_config = {
            'app_name': app_name.strip(),
            'models': validated_models,
            'output_dir': config.get('output_dir', './generated_code'),
            'version': config.get('version', '1.0.0'),
            'description': config.get('description', ''),
            'author': config.get('author', ''),
            'global_settings': config.get('global_settings', {})
        }
        
        return validated_config
    
    def _validate_model_config(self, model: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        验证单个模型配置
        
        Args:
            model: 模型配置字典
            index: 模型在列表中的索引
            
        Returns:
            Dict[str, Any]: 验证后的模型配置
            
        Raises:
            ValueError: 当模型配置验证失败时
        """
        if not isinstance(model, dict):
            raise ValueError(f"模型配置[{index}]必须是字典格式")
        
        # 验证必需字段
        if 'name' not in model:
            raise ValueError(f"模型配置[{index}]缺少必需字段: name")
        
        if 'fields' not in model:
            raise ValueError(f"模型配置[{index}]缺少必需字段: fields")
        
        model_name = model['name']
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError(f"模型配置[{index}]的name必须是非空字符串")
        
        # 验证字段配置
        fields = model['fields']
        if not isinstance(fields, list) or len(fields) == 0:
            raise ValueError(f"模型{model_name}的fields必须是非空列表")
        
        validated_fields = []
        for j, field in enumerate(fields):
            validated_field = self._validate_field_config(field, model_name, j)
            validated_fields.append(validated_field)
        
        # 验证操作配置
        operations = model.get('operations', ['create', 'read', 'update', 'delete', 'list'])
        if not isinstance(operations, list):
            raise ValueError(f"模型{model_name}的operations必须是列表")
        
        for op in operations:
            if op not in self.supported_operations:
                raise ValueError(f"模型{model_name}包含不支持的操作: {op}")
        
        # 构建验证后的模型配置
        validated_model = {
            'name': model_name.strip(),
            'fields': validated_fields,
            'operations': operations,
            'table_name': model.get('table_name'),
            'verbose_name': model.get('verbose_name', model_name),
            'verbose_name_plural': model.get('verbose_name_plural'),
            'ordering': model.get('ordering', []),
            'permissions': model.get('permissions', []),
            'validators': model.get('validators', {}),
            'meta_options': model.get('meta_options', {}),
            'admin_config': model.get('admin_config', {}),
            'api_config': model.get('api_config', {})
        }
        
        return validated_model
    
    def _validate_field_config(self, field: Dict[str, Any], model_name: str, index: int) -> Dict[str, Any]:
        """
        验证单个字段配置
        
        Args:
            field: 字段配置字典
            model_name: 所属模型名称
            index: 字段在列表中的索引
            
        Returns:
            Dict[str, Any]: 验证后的字段配置
            
        Raises:
            ValueError: 当字段配置验证失败时
        """
        if not isinstance(field, dict):
            raise ValueError(f"模型{model_name}的字段配置[{index}]必须是字典格式")
        
        # 验证必需字段
        if 'name' not in field:
            raise ValueError(f"模型{model_name}的字段配置[{index}]缺少必需字段: name")
        
        if 'type' not in field:
            raise ValueError(f"模型{model_name}的字段配置[{index}]缺少必需字段: type")
        
        field_name = field['name']
        field_type = field['type']
        
        if not isinstance(field_name, str) or not field_name.strip():
            raise ValueError(f"模型{model_name}的字段配置[{index}]的name必须是非空字符串")
        
        # 检查字段类型是否支持（包括通用类型和Django类型）
        if field_type not in self.supported_field_types and field_type not in self.field_type_mapping:
            raise ValueError(f"模型{model_name}的字段{field_name}使用了不支持的类型: {field_type}")
        
        # 如果是通用类型，转换为Django字段类型
        django_field_type = self.field_type_mapping.get(field_type, field_type)
        # 移除调试输出
        print(f"字段类型转换: {field_type} -> {django_field_type}")
        
        # 构建验证后的字段配置
        validated_field = {
            'name': field['name'],
            'type': django_field_type,  # 使用转换后的Django字段类型
            'verbose_name': field.get('verbose_name', field['name']),
            'help_text': field.get('help_text', f"{field['name']}字段"),
            'required': field.get('required', False),
            'null': not field.get('required', False),
            'blank': not field.get('required', False)
        }
        
        # 添加其他字段属性
        for key in ['max_length', 'default', 'unique', 'choices', 'max_digits', 'decimal_places', 'upload_to']:
            if key in field:
                validated_field[key] = field[key]
        
        # 移除None值
        validated_field = {k: v for k, v in validated_field.items() if v is not None}
        
        return validated_field
    
    def generate_yaml_template(self, output_path: str = 'app_template.yaml') -> str:
        """
        生成YAML配置文件模板
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            str: 生成的模板内容
        """
        template = {
            'app_name': 'studio_django_example',
            'version': '1.0.0',
            'description': 'Django应用示例',
            'author': 'Hertz Studio',
            'output_dir': './generated_code',
            'global_settings': {
                'use_uuid_primary_key': False,
                'add_created_updated_fields': True,
                'add_status_field': True,
                'default_permissions': ['add', 'change', 'delete', 'view']
            },
            'models': [
                {
                    'name': 'User',
                    'verbose_name': '用户',
                    'verbose_name_plural': '用户列表',
                    'table_name': 'example_user',
                    'ordering': ['-created_at'],
                    'fields': [
                        {
                            'name': 'username',
                            'type': 'CharField',
                            'max_length': 150,
                            'unique': True,
                            'verbose_name': '用户名',
                            'help_text': '用户登录名'
                        },
                        {
                            'name': 'email',
                            'type': 'EmailField',
                            'unique': True,
                            'verbose_name': '邮箱',
                            'help_text': '用户邮箱地址'
                        },
                        {
                            'name': 'phone',
                            'type': 'CharField',
                            'max_length': 20,
                            'blank': True,
                            'null': True,
                            'verbose_name': '手机号',
                            'help_text': '用户手机号码'
                        },
                        {
                            'name': 'avatar',
                            'type': 'ImageField',
                            'upload_to': 'avatars/',
                            'blank': True,
                            'null': True,
                            'verbose_name': '头像',
                            'help_text': '用户头像图片'
                        },
                        {
                            'name': 'is_active',
                            'type': 'BooleanField',
                            'default': True,
                            'verbose_name': '是否激活',
                            'help_text': '用户账户是否激活'
                        }
                    ],
                    'operations': ['create', 'read', 'update', 'delete', 'list', 'search'],
                    'permissions': ['add_user', 'change_user', 'delete_user', 'view_user'],
                    'validators': {
                        'username': 'validate_username',
                        'email': 'validate_email'
                    },
                    'admin_config': {
                        'list_display': ['username', 'email', 'is_active', 'created_at'],
                        'list_filter': ['is_active', 'created_at'],
                        'search_fields': ['username', 'email']
                    },
                    'api_config': {
                        'pagination': True,
                        'filters': ['is_active'],
                        'search_fields': ['username', 'email'],
                        'ordering_fields': ['username', 'created_at']
                    }
                }
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as file:
            yaml.dump(template, file, default_flow_style=False, allow_unicode=True, indent=2)
        
        return yaml.dump(template, default_flow_style=False, allow_unicode=True, indent=2)