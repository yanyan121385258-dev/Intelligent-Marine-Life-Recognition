"""
Django URL配置模板
"""
<%!
from datetime import datetime
%>
<%
# 生成操作列表
operations_list = operations or ['create', 'get', 'update', 'delete', 'list']
snake_model_name = model_name.lower()
resource_name = snake_model_name
%>
from django.urls import path
from . import views

app_name = '${app_name or snake_model_name}'

urlpatterns = [
    % if 'create' in operations_list:
    # 创建${model_name}
    path('', views.create_${snake_model_name}, name='create_${snake_model_name}'),
    % endif
    
    % if 'list' in operations_list:
    # 获取${model_name}列表
    path('list/', views.list_${snake_model_name}, name='list_${snake_model_name}'),
    % endif
    
    % if 'get' in operations_list:
    # 获取${model_name}详情
    path('<int:${snake_model_name}_id>/', views.get_${snake_model_name}, name='get_${snake_model_name}'),
    % endif
    
    % if 'update' in operations_list:
    # 更新${model_name}
    path('<int:${snake_model_name}_id>/update/', views.update_${snake_model_name}, name='update_${snake_model_name}'),
    % endif
    
    % if 'delete' in operations_list:
    # 删除${model_name}
    path('<int:${snake_model_name}_id>/delete/', views.delete_${snake_model_name}, name='delete_${snake_model_name}'),
    % endif
]

# RESTful风格的URL配置（可选）
restful_urlpatterns = [
    % if 'create' in operations_list or 'list' in operations_list:
    # POST: 创建${model_name}, GET: 获取${model_name}列表
    path('${prefix}${resource_name}/', views.${'create_' + snake_model_name if 'create' in operations_list else 'list_' + snake_model_name}, name='${snake_model_name}_collection'),
    % endif
    
    % if 'get' in operations_list or 'update' in operations_list or 'delete' in operations_list:
    # GET: 获取详情, PUT/PATCH: 更新, DELETE: 删除
    path('${prefix}${resource_name}/<int:${snake_model_name}_id>/', views.update_${snake_model_name}, name='${snake_model_name}_detail'),
    % endif
]