from django.urls import path
from .views import (
    SystemInfoView, CPUInfoView, MemoryInfoView,
    DiskInfoView, NetworkInfoView, ProcessInfoView,
    GPUInfoView, SystemMonitorView
)

app_name = 'studio_django_system_monitor'

urlpatterns = [
    # 系统信息
    path('system/', SystemInfoView.as_view(), name='system_info'),
    
    # CPU信息
    path('cpu/', CPUInfoView.as_view(), name='cpu_info'),
    
    # 内存信息
    path('memory/', MemoryInfoView.as_view(), name='memory_info'),
    
    # 磁盘信息
    path('disks/', DiskInfoView.as_view(), name='disk_info'),
    
    # 网络信息
    path('network/', NetworkInfoView.as_view(), name='network_info'),
    
    # 进程信息
    path('processes/', ProcessInfoView.as_view(), name='process_info'),
    
    # GPU信息
    path('gpu/', GPUInfoView.as_view(), name='gpu_info'),
    
    # 系统监测综合信息
    path('monitor/', SystemMonitorView.as_view(), name='system_monitor'),
]