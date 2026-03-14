"""
Django应用配置模板
"""
<%!
from datetime import datetime
%>
<%
# 生成应用配置类名
app_class_name = ''.join(word.capitalize() for word in app_name.split('_')) + 'Config'
%>
from django.apps import AppConfig


class ${app_class_name}(AppConfig):
    """
    ${app_name}应用配置
    
    创建时间: ${datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = '${app_name}'
    verbose_name = '${verbose_name or app_name}'
    
