"""
Django序列化器代码生成器

该模块负责根据配置生成Django REST Framework序列化器代码
"""

import os
from typing import Dict, List, Any, Optional
from .base_generator import BaseGenerator


class SerializerGenerator(BaseGenerator):
    """Django序列化器代码生成器"""
    
    def __init__(self):
        """初始化序列化器生成器"""
        super().__init__()
    
    def generate(self, model_name: str = None, fields: List[Any] = None, **kwargs) -> str:
        """
        生成Django序列化器代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表（可以是字符串列表或字典列表）
            **kwargs: 其他参数
            
        Returns:
            str: 生成的序列化器代码
        """
        # 处理参数，支持位置参数和关键字参数
        if model_name is None:
            model_name = kwargs.get('model_name', 'DefaultModel')
        if fields is None:
            fields = kwargs.get('fields', [])
        
        # 处理字段列表，统一转换为字典格式
        processed_fields = []
        
        for field in fields:
            if isinstance(field, str):
                # 字符串字段转换为字典格式
                field_config = {
                    'name': field,
                    'type': 'CharField',
                    'create': True,
                    'update': True,
                    'list': True,
                    'required': True,
                    'read_only': False
                }
                processed_fields.append(field_config)
            elif isinstance(field, dict):
                # 字典字段，确保有必要的属性
                field_config = {
                    'name': field.get('name', 'unknown_field'),
                    'type': field.get('type', 'CharField'),
                    'create': field.get('create', True),
                    'update': field.get('update', True),
                    'list': field.get('list', True),
                    'required': field.get('required', True),
                    'read_only': field.get('read_only', False)
                }
                processed_fields.append(field_config)
        
        # 添加默认字段（如果不存在）
        field_names = [f['name'] for f in processed_fields]
        
        if 'id' not in field_names:
            processed_fields.insert(0, {
                'name': 'id',
                'type': 'IntegerField',
                'create': False,
                'update': False,
                'list': True,
                'required': False,
                'read_only': True
            })
        
        if 'created_at' not in field_names:
            processed_fields.append({
                'name': 'created_at',
                'type': 'DateTimeField',
                'create': False,
                'update': False,
                'list': True,
                'required': False,
                'read_only': True
            })
            
        if 'updated_at' not in field_names:
            processed_fields.append({
                'name': 'updated_at',
                'type': 'DateTimeField',
                'create': False,
                'update': False,
                'list': True,
                'required': False,
                'read_only': True
            })
        
        # 生成字段列表
        create_fields_list = [f['name'] for f in processed_fields if f.get('create', False)]
        update_fields_list = [f['name'] for f in processed_fields if f.get('update', False)]
        list_fields_list = [f['name'] for f in processed_fields if f.get('list', False)]
        
        # 准备模板上下文
        context = {
            'model_name': model_name,
            'model_name_lower': model_name.lower(),
            'fields': processed_fields,
            'create_fields_list': create_fields_list,
            'update_fields_list': update_fields_list,
            'list_fields_list': list_fields_list,
            'has_create_serializer': bool(create_fields_list),
            'has_update_serializer': bool(update_fields_list),
            'has_list_serializer': bool(list_fields_list)
        }
        
        # 渲染模板
        return self.render_template('django/serializers.mako', context)
    
    def generate_crud_serializers(
        self,
        model_name: str,
        fields: List[str],
        create_fields: Optional[List[str]] = None,
        update_fields: Optional[List[str]] = None,
        list_fields: Optional[List[str]] = None,
        validators: Optional[Dict[str, str]] = None
    ) -> str:
        """
        生成CRUD序列化器代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表
            create_fields: 创建时使用的字段
            update_fields: 更新时使用的字段
            list_fields: 列表时显示的字段
            validators: 字段验证器映射
            
        Returns:
            str: 生成的序列化器代码
        """
        # 默认字段配置
        if create_fields is None:
            create_fields = [f for f in fields if f not in ['id', 'created_at', 'updated_at']]
        if update_fields is None:
            update_fields = [f for f in fields if f not in ['id', 'created_at', 'updated_at']]
        if list_fields is None:
            list_fields = fields
        
        # 构建字段配置
        field_configs = []
        for field_name in fields:
            field_config = {
                'name': field_name,
                'create': field_name in create_fields,
                'update': field_name in update_fields,
                'list': field_name in list_fields,
                'validators': validators.get(field_name, {}) if validators else {}
            }
            field_configs.append(field_config)
        
        return self.generate(
            model_name=model_name,
            fields=field_configs
        )
    
    def generate_nested_serializer(
        self,
        model_name: str,
        fields: List[str],
        nested_fields: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        生成嵌套序列化器代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表
            nested_fields: 嵌套字段配置
            
        Returns:
            str: 生成的嵌套序列化器代码
        """
        # 构建字段配置，包含嵌套字段信息
        field_configs = []
        for field_name in fields:
            field_config = {
                'name': field_name,
                'nested': field_name in nested_fields,
                'nested_config': nested_fields.get(field_name, {})
            }
            field_configs.append(field_config)
        
        return self.generate(
            model_name=model_name,
            fields=field_configs,
            has_nested=True
        )
    
    def generate_read_only_serializer(
        self,
        model_name: str,
        fields: List[str]
    ) -> str:
        """
        生成只读序列化器代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表
            
        Returns:
            str: 生成的只读序列化器代码
        """
        field_configs = []
        for field_name in fields:
            field_config = {
                'name': field_name,
                'read_only': True
            }
            field_configs.append(field_config)
        
        return self.generate(
            model_name=model_name,
            fields=field_configs,
            read_only=True
        )
    
    def generate_create_serializer(
        self,
        model_name: str,
        fields: List[str],
        validators: Optional[Dict[str, str]] = None
    ) -> str:
        """
        生成创建序列化器代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表
            validators: 字段验证器映射
            
        Returns:
            str: 生成的创建序列化器代码
        """
        field_configs = []
        for field_name in fields:
            field_config = {
                'name': field_name,
                'validators': validators.get(field_name, {}) if validators else {}
            }
            field_configs.append(field_config)
        
        return self.generate(
            model_name=model_name,
            fields=field_configs,
            serializer_type='create'
        )
    
    def generate_update_serializer(
        self,
        model_name: str,
        fields: List[str],
        validators: Optional[Dict[str, str]] = None
    ) -> str:
        """
        生成更新序列化器代码
        
        Args:
            model_name: 模型名称
            fields: 字段列表
            validators: 字段验证器映射
            
        Returns:
            str: 生成的更新序列化器代码
        """
        field_configs = []
        for field_name in fields:
            field_config = {
                'name': field_name,
                'validators': validators.get(field_name, {}) if validators else {}
            }
            field_configs.append(field_config)
        
        return self.generate(
            model_name=model_name,
            fields=field_configs,
            serializer_type='update'
        )
    
    def add_custom_validation(
        self,
        serializer_code: str,
        field_name: str,
        validation_code: str
    ) -> str:
        """
        添加自定义验证方法
        
        Args:
            serializer_code: 原序列化器代码
            field_name: 字段名称
            validation_code: 验证代码
            
        Returns:
            str: 包含自定义验证的序列化器代码
        """
        validation_method = f"""
    def validate_{field_name}(self, value):
        \"\"\"
        验证{field_name}字段
        \"\"\"
        {validation_code}
        return value
"""
        
        # 在类定义结束前插入验证方法
        lines = serializer_code.split('\n')
        insert_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and 'Serializer' in line:
                # 找到类定义结束的位置
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('    '):
                        insert_index = j
                        break
                break
        
        if insert_index > 0:
            lines.insert(insert_index, validation_method)
        
        return '\n'.join(lines)