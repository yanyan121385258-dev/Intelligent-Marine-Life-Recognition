import platform
import psutil
import datetime
from django.utils import timezone
from django.views.decorators.cache import cache_page
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    SystemInfoSerializer, CPUInfoSerializer, MemoryInfoSerializer,
    DiskInfoSerializer, NetworkInfoSerializer, ProcessInfoSerializer,
    GPUInfoSerializer, SystemMonitorSerializer
)
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_utils.log.log_decorator import operation_log

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# 缓存时间配置（秒）
SYSTEM_INFO_CACHE_TIMEOUT = 60  # 1分钟
CPU_CACHE_TIMEOUT = 5  # 5秒
MEMORY_CACHE_TIMEOUT = 5  # 5秒
DISK_CACHE_TIMEOUT = 60  # 1分钟
NETWORK_CACHE_TIMEOUT = 10  # 10秒
PROCESS_CACHE_TIMEOUT = 30  # 30秒
GPU_CACHE_TIMEOUT = 5  # 5秒
MONITOR_CACHE_TIMEOUT = 5  # 5秒


class SystemInfoView(GenericAPIView):
    """
    系统信息接口
    获取系统基本信息
    """
    
    @extend_schema(
        operation_id='system_info',
        summary='获取系统信息',
        description='获取系统基本信息，包括主机名、平台、架构等',
        responses={
            200: OpenApiResponse(response=SystemInfoSerializer, description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取系统信息")
    def get(self, request, *args, **kwargs):
        """
        获取系统基本信息
        """
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        
        system_info = {
            'hostname': platform.node(),
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'boot_time': timezone.make_aware(boot_time),
            'uptime': str(uptime).split('.')[0]  # 去掉微秒
        }
        
        return HertzResponse.success(data=system_info)


class CPUInfoView(GenericAPIView):
    """
    CPU信息接口
    获取CPU使用情况
    """
    
    @extend_schema(
        operation_id='cpu_info',
        summary='获取CPU信息',
        description='获取CPU使用率、核心数、频率等信息',
        responses={
            200: OpenApiResponse(response=CPUInfoSerializer, description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取CPU信息")
    def get(self, request, *args, **kwargs):
        """
        获取CPU信息
        """
        cpu_info = {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            'load_avg': list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else []
        }
        
        return HertzResponse.success(data=cpu_info)


class MemoryInfoView(GenericAPIView):
    """
    内存信息接口
    获取内存使用情况
    """
    
    @extend_schema(
        operation_id='memory_info',
        summary='获取内存信息',
        description='获取内存使用率、总量、可用量等信息',
        responses={
            200: OpenApiResponse(response=MemoryInfoSerializer, description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取内存信息")
    def get(self, request, *args, **kwargs):
        """
        获取内存信息
        """
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'free': memory.free
        }
        
        return HertzResponse.success(data=memory_info)


class DiskInfoView(GenericAPIView):
    """
    磁盘信息接口
    获取磁盘使用情况
    """
    
    @extend_schema(
        operation_id='disk_info',
        summary='获取磁盘信息',
        description='获取所有磁盘分区的使用情况',
        responses={
            200: OpenApiResponse(response=DiskInfoSerializer(many=True), description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取磁盘信息")
    def get(self, request, *args, **kwargs):
        """
        获取磁盘信息
        """
        disk_info = []
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                # 处理Windows路径编码问题
                mountpoint = partition.mountpoint
                if isinstance(mountpoint, bytes):
                    mountpoint = mountpoint.decode('utf-8', errors='replace')
                
                usage = psutil.disk_usage(mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': round((usage.used / usage.total) * 100, 2)
                })
            except PermissionError:
                # 某些分区可能没有权限访问
                continue
            except Exception:
                # 处理其他错误，如路径编码问题
                continue
        
        return HertzResponse.success(data=disk_info)


class NetworkInfoView(GenericAPIView):
    """
    网络信息接口
    获取网络接口统计信息
    """
    
    @extend_schema(
        operation_id='network_info',
        summary='获取网络信息',
        description='获取网络接口的流量统计信息',
        responses={
            200: OpenApiResponse(response=NetworkInfoSerializer(many=True), description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取网络信息")
    def get(self, request, *args, **kwargs):
        """
        获取网络信息
        """
        network_info = []
        net_io = psutil.net_io_counters(pernic=True)
        
        for interface, stats in net_io.items():
            network_info.append({
                'interface': interface,
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv
            })
        
        return HertzResponse.success(data=network_info)


class ProcessInfoView(GenericAPIView):
    """
    进程信息接口
    获取系统进程信息
    """
    
    @extend_schema(
        operation_id='process_info',
        summary='获取进程信息',
        description='获取系统运行进程的详细信息',
        responses={
            200: OpenApiResponse(response=ProcessInfoSerializer(many=True), description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取进程信息")
    def get(self, request, *args, **kwargs):
        """
        获取进程信息
        """
        # 获取查询参数
        limit = int(request.GET.get('limit', 20))  # 默认返回前20个进程
        sort_by = request.GET.get('sort_by', 'cpu_percent')  # 默认按CPU使用率排序
        
        process_info = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 
                                       'memory_percent', 'memory_info', 'create_time', 'cmdline']):
            try:
                pinfo = proc.info
                process_info.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'status': pinfo['status'],
                    'cpu_percent': pinfo['cpu_percent'] or 0.0,
                    'memory_percent': pinfo['memory_percent'] or 0.0,
                    'memory_info': pinfo['memory_info']._asdict() if pinfo['memory_info'] else {},
                    'create_time': timezone.make_aware(datetime.datetime.fromtimestamp(pinfo['create_time'])),
                    'cmdline': pinfo['cmdline'] or []
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 进程可能已经结束或没有权限访问
                continue
        
        # 排序
        if sort_by in ['cpu_percent', 'memory_percent']:
            process_info.sort(key=lambda x: x[sort_by], reverse=True)
        
        # 限制返回数量
        process_info = process_info[:limit]
        
        return HertzResponse.success(data=process_info)


class GPUInfoView(GenericAPIView):
    """
    GPU信息接口
    获取GPU使用情况
    """
    
    @extend_schema(
        operation_id='gpu_info',
        summary='获取GPU信息',
        description='获取GPU使用率、显存、温度等信息',
        responses={
            200: OpenApiResponse(response=GPUInfoSerializer(many=True), description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取GPU信息")
    def get(self, request, *args, **kwargs):
        """
        获取GPU信息
        """
        try:
            if not GPU_AVAILABLE:
                return HertzResponse.success(data={
                    'gpu_available': False,
                    'message': 'GPU监控不可用，请安装GPUtil库',
                    'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # 获取GPU信息
            gpus = GPUtil.getGPUs()
            
            if not gpus:
                return HertzResponse.success(data={
                    'gpu_available': False,
                    'message': '未检测到GPU设备',
                    'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            gpu_info = []
            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': round(gpu.load * 100, 2),  # 转换为百分比
                    'memory_total': gpu.memoryTotal,
                    'memory_used': gpu.memoryUsed,
                    'memory_util': round((gpu.memoryUsed / gpu.memoryTotal * 100), 2),
                    'temperature': gpu.temperature
                })
            
            data = {
                'gpu_available': True,
                'gpu_info': gpu_info,
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return HertzResponse.success(data=data)
        except Exception as e:
            return HertzResponse.success(data={
                'gpu_available': False,
                'message': f'获取GPU信息失败: {str(e)}',
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            })


class SystemMonitorView(GenericAPIView):
    """
    系统监测综合信息接口
    获取所有系统监测信息
    """
    
    @extend_schema(
        operation_id='system_monitor',
        summary='获取系统监测综合信息',
        description='获取系统、CPU、内存、磁盘、网络、进程、GPU等所有监测信息',
        responses={
            200: OpenApiResponse(response=SystemMonitorSerializer, description='成功'),
        },
        tags=['系统监测']
    )
    
    @operation_log('view', '系统监测', description="获取系统监测综合信息")
    def get(self, request, *args, **kwargs):
        """
        获取系统监测综合信息
        """
        # 获取系统信息
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        
        system_info = {
            'hostname': platform.node(),
            'platform': platform.platform(),
            'architecture': platform.architecture()[0],
            'boot_time': timezone.make_aware(boot_time),
            'uptime': str(uptime).split('.')[0]
        }
        
        # 获取CPU信息
        cpu_info = {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            'load_avg': list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else []
        }
        
        # 获取内存信息
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'free': memory.free
        }
        
        # 获取磁盘信息
        disk_info = []
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                # 处理Windows路径编码问题
                mountpoint = partition.mountpoint
                if isinstance(mountpoint, bytes):
                    mountpoint = mountpoint.decode('utf-8', errors='replace')
                
                usage = psutil.disk_usage(mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': round((usage.used / usage.total) * 100, 2)
                })
            except PermissionError:
                continue
            except Exception:
                continue
        
        # 获取网络信息
        network_info = []
        net_io = psutil.net_io_counters(pernic=True)
        for interface, stats in net_io.items():
            network_info.append({
                'interface': interface,
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv
            })
        
        # 获取进程信息（限制前10个）
        process_info = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 
                                       'memory_percent', 'memory_info', 'create_time', 'cmdline']):
            try:
                pinfo = proc.info
                process_info.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'status': pinfo['status'],
                    'cpu_percent': pinfo['cpu_percent'] or 0.0,
                    'memory_percent': pinfo['memory_percent'] or 0.0,
                    'memory_info': pinfo['memory_info']._asdict() if pinfo['memory_info'] else {},
                    'create_time': timezone.make_aware(datetime.datetime.fromtimestamp(pinfo['create_time'])),
                    'cmdline': pinfo['cmdline'] or []
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # 按CPU使用率排序，取前10个
        process_info.sort(key=lambda x: x['cpu_percent'], reverse=True)
        process_info = process_info[:10]
        
        # 获取GPU信息
        gpu_info = []
        try:
            if not GPU_AVAILABLE:
                gpu_info = [{
                    'gpu_available': False,
                    'message': 'GPU监控不可用，请安装GPUtil库',
                    'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                }]
            else:
                # 获取GPU信息
                gpus = GPUtil.getGPUs()
                
                if not gpus:
                    gpu_info = [{
                        'gpu_available': False,
                        'message': '未检测到GPU设备',
                        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                    }]
                else:
                    for gpu in gpus:
                        gpu_info.append({
                            'id': gpu.id,
                            'name': gpu.name,
                            'load': round(gpu.load * 100, 2),  # 转换为百分比
                            'memory_total': gpu.memoryTotal,
                            'memory_used': gpu.memoryUsed,
                            'memory_util': round((gpu.memoryUsed / gpu.memoryTotal * 100), 2),
                            'temperature': gpu.temperature
                        })
        except Exception as e:
            gpu_info = [{
                'gpu_available': False,
                'message': f'获取GPU信息失败: {str(e)}',
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }]
        
        # 构建综合数据
        monitor_data = {
            'system': system_info,
            'cpu': cpu_info,
            'memory': memory_info,
            'disks': disk_info,
            'network': network_info,
            'processes': process_info,
            'gpus': gpu_info
        }
        
        return HertzResponse.success(data=monitor_data)
