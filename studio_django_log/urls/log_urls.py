from django.urls import path
from ..views import operation_log_list, operation_log_detail

urlpatterns = [
    # 操作日志列表
    path('list/', operation_log_list, name='operation_log_list'),
    
    # 操作日志详情
    path('detail/<int:log_id>/', operation_log_detail, name='operation_log_detail'),
]