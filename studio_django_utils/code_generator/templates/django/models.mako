"""
Django模型模板
"""
<%!
from datetime import datetime
%>
<%
# 导入必要的模块
imports = []
if any(field.get('type') == 'ForeignKey' for field in fields):
    imports.append('from django.contrib.auth import get_user_model')
if any(field.get('type') in ['DateTimeField', 'DateField', 'TimeField'] for field in fields):
    imports.append('from django.utils import timezone')
if any(field.get('choices') for field in fields):
    imports.append('from django.core.validators import validate_email')

# 生成状态选择项
status_choices_code = ""
if status_choices:
    choices_list = []
    for choice in status_choices:
        if isinstance(choice, tuple) and len(choice) == 2:
            choices_list.append(f"        ('{choice[0]}', '{choice[1]}')")
        else:
            choices_list.append(f"        ('{choice}', '{choice}')")
    status_choices_code = f"""    STATUS_CHOICES = [
{',{}'.format(chr(10)).join(choices_list)},
    ]"""
%>\
from django.db import models
% for import_line in imports:
${import_line}
% endfor

class ${model_name}(models.Model):
    """
    ${verbose_name or model_name}模型
    % if table_name:
    
    数据表名: ${table_name}
    % endif
    创建时间: ${datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
% if status_choices_code:
${status_choices_code}

% endif
% for field in fields:
<%
field_name = field['name']
# 使用转换后的Django字段类型
field_type = field.get('type', 'CharField')
field_options = []

# 处理字段选项
if field.get('verbose_name'):
    field_options.append(f"verbose_name='{field['verbose_name']}'")
if field.get('help_text'):
    field_options.append(f"help_text='{field['help_text']}'")
if field.get('max_length'):
    field_options.append(f"max_length={field['max_length']}")
if field.get('null'):
    field_options.append(f"null={field['null']}")
if field.get('blank'):
    field_options.append(f"blank={field['blank']}")
if field.get('default') is not None:
    if isinstance(field['default'], str):
        field_options.append(f"default='{field['default']}'")
    else:
        field_options.append(f"default={field['default']}")
if field.get('unique'):
    field_options.append(f"unique={field['unique']}")
if field.get('db_index'):
    field_options.append(f"db_index={field['db_index']}")

# 处理特殊字段类型
if field_type == 'ForeignKey':
    if field.get('to'):
        field_options.insert(0, f"'{field['to']}'")
    else:
        field_options.insert(0, "get_user_model()")
    if field.get('on_delete'):
        field_options.append(f"on_delete=models.{field['on_delete']}")
    else:
        field_options.append("on_delete=models.CASCADE")
elif field_type == 'ManyToManyField':
    if field.get('to'):
        field_options.insert(0, f"'{field['to']}'")
elif field_type == 'OneToOneField':
    if field.get('to'):
        field_options.insert(0, f"'{field['to']}'")
    if field.get('on_delete'):
        field_options.append(f"on_delete=models.{field['on_delete']}")
    else:
        field_options.append("on_delete=models.CASCADE")

# 处理选择项
if field.get('choices'):
    if field_name == 'status' and status_choices:
        field_options.append("choices=STATUS_CHOICES")
    else:
        choices_list = []
        for choice in field['choices']:
            if isinstance(choice, tuple) and len(choice) == 2:
                choices_list.append(f"('{choice[0]}', '{choice[1]}')")
            else:
                choices_list.append(f"('{choice}', '{choice}')")
        field_options.append(f"choices=[{', '.join(choices_list)}]")

# 处理特殊字段类型的额外参数
if field_type == 'DecimalField':
    if not any('max_digits' in opt for opt in field_options):
        field_options.append('max_digits=10')
    if not any('decimal_places' in opt for opt in field_options):
        field_options.append('decimal_places=2')
elif field_type == 'DateTimeField':
    if field_name == 'created_at' and not any('auto_now_add' in opt for opt in field_options):
        field_options.append('auto_now_add=True')
    elif field_name == 'updated_at' and not any('auto_now' in opt for opt in field_options):
        field_options.append('auto_now=True')

options_str = ', '.join(field_options) if field_options else ''
%>
    ${field_name} = models.${field_type}(${options_str})
% endfor

    class Meta:
        % if table_name:
        db_table = '${table_name}'
        % endif
        verbose_name = '${verbose_name or model_name}'
        verbose_name_plural = '${verbose_name or model_name}'
        % if ordering:
        ordering = [${', '.join([f"'{field}'" for field in ordering])}]
        % else:
        ordering = ['-created_at']
        % endif

    def __str__(self):
        """字符串表示"""
        % if fields:
        <%
        # 寻找合适的字段作为字符串表示
        str_field = None
        for field in fields:
            if field['name'] in ['name', 'title', 'username', 'email']:
                str_field = field['name']
                break
        if not str_field:
            # 如果没有找到合适的字段，使用第一个字符串字段
            for field in fields:
                if field['type'] in ['CharField', 'TextField', 'EmailField']:
                    str_field = field['name']
                    break
        if not str_field:
            str_field = 'id'
        %>
        return str(self.${str_field})
        % else:
        return f"${model_name}({self.id})"
        % endif

    def save(self, *args, **kwargs):
        """保存方法"""
        super().save(*args, **kwargs)

    @classmethod
    def get_by_id(cls, obj_id):
        """根据ID获取对象"""
        try:
            return cls.objects.get(id=obj_id)
        except cls.DoesNotExist:
            return None