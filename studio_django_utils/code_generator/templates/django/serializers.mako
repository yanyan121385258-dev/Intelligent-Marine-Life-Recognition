"""
Django序列化器模板
"""
<%!
from datetime import datetime
%>
<%
# 生成字段列表
all_fields = []
create_fields_list = []
update_fields_list = []
list_fields_list = []

# 处理字段列表
for field in fields:
    field_name = field['name']
    all_fields.append(field_name)
    
    # 排除自动生成的字段
    if field_name not in ['id', 'created_at', 'updated_at']:
        create_fields_list.append(field_name)
        update_fields_list.append(field_name)
    
    list_fields_list.append(field_name)

# 添加默认字段
if 'id' not in all_fields:
    all_fields.insert(0, 'id')
if 'created_at' not in all_fields:
    all_fields.append('created_at')
if 'updated_at' not in all_fields:
    all_fields.append('updated_at')

# 如果没有指定列表字段，使用所有字段
if not list_fields_list:
    list_fields_list = all_fields
%>
from rest_framework import serializers
from .models import ${model_name}


class ${model_name}Serializer(serializers.ModelSerializer):
    """
    ${model_name}序列化器
    
    用于${model_name}模型的序列化和反序列化
    创建时间: ${datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    class Meta:
        model = ${model_name}
        fields = [${', '.join([f"'{field}'" for field in all_fields])}]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    % for field in fields:
    % if field.get('validators'):
    def validate_${field['name']}(self, value):
        """
        验证${field['name']}字段
        """
        % for validator_name, validator_rule in field['validators'].items():
        # ${validator_name}验证: ${validator_rule}
        % endfor
        return value
        
    % endif
    % endfor
    def validate(self, attrs):
        """
        对象级别的验证
        """
        # 在这里添加跨字段验证逻辑
        return attrs
        
    def create(self, validated_data):
        """
        创建${model_name}实例
        """
        return ${model_name}.objects.create(**validated_data)
        
    def update(self, instance, validated_data):
        """
        更新${model_name}实例
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ${model_name}CreateSerializer(serializers.ModelSerializer):
    """
    ${model_name}创建序列化器
    
    用于创建${model_name}实例
    """
    
    class Meta:
        model = ${model_name}
        fields = [${', '.join([f"'{field}'" for field in create_fields_list])}]
        
    % for field in fields:
    % if field['name'] in create_fields_list and field.get('validators'):
    def validate_${field['name']}(self, value):
        """
        验证${field['name']}字段
        """
        % for validator_name, validator_rule in field['validators'].items():
        # ${validator_name}验证: ${validator_rule}
        % endfor
        return value
        
    % endif
    % endfor


class ${model_name}UpdateSerializer(serializers.ModelSerializer):
    """
    ${model_name}更新序列化器
    
    用于更新${model_name}实例
    """
    
    class Meta:
        model = ${model_name}
        fields = [${', '.join([f"'{field}'" for field in update_fields_list])}]
        
    % for field in fields:
    % if field['name'] in update_fields_list and field.get('validators'):
    def validate_${field['name']}(self, value):
        """
        验证${field['name']}字段
        """
        % for validator_name, validator_rule in field['validators'].items():
        # ${validator_name}验证: ${validator_rule}
        % endfor
        return value
        
    % endif
    % endfor


class ${model_name}ListSerializer(serializers.ModelSerializer):
    """
    ${model_name}列表序列化器
    
    用于列表显示${model_name}实例
    """
    
    class Meta:
        model = ${model_name}
        fields = [${', '.join([f"'{field}'" for field in list_fields_list])}]
        read_only_fields = [${', '.join([f"'{field}'" for field in list_fields_list])}]