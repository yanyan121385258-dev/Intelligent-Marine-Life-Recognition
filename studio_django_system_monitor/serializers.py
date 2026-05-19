from rest_framework import serializers


class SystemInfoSerializer(serializers.Serializer):
    """
    系统信息序列化器
    """
    hostname = serializers.CharField(help_text="主机名")
    platform = serializers.CharField(help_text="操作系统平台")
    architecture = serializers.CharField(help_text="系统架构")
    boot_time = serializers.DateTimeField(help_text="系统启动时间")
    uptime = serializers.CharField(help_text="系统运行时间")


class CPUInfoSerializer(serializers.Serializer):
    """
    CPU信息序列化器
    """
    cpu_count = serializers.IntegerField(help_text="CPU核心数")
    cpu_percent = serializers.FloatField(help_text="CPU使用率百分比")
    cpu_freq = serializers.DictField(help_text="CPU频率信息")
    load_avg = serializers.ListField(
        child=serializers.FloatField(),
        help_text="系统负载平均值"
    )


class MemoryInfoSerializer(serializers.Serializer):
    """
    内存信息序列化器
    """
    total = serializers.IntegerField(help_text="总内存(字节)")
    available = serializers.IntegerField(help_text="可用内存(字节)")
    used = serializers.IntegerField(help_text="已用内存(字节)")
    percent = serializers.FloatField(help_text="内存使用率百分比")
    free = serializers.IntegerField(help_text="空闲内存(字节)")


class DiskInfoSerializer(serializers.Serializer):
    """
    磁盘信息序列化器
    """
    device = serializers.CharField(help_text="设备名")
    mountpoint = serializers.CharField(help_text="挂载点")
    fstype = serializers.CharField(help_text="文件系统类型")
    total = serializers.IntegerField(help_text="总容量(字节)")
    used = serializers.IntegerField(help_text="已用容量(字节)")
    free = serializers.IntegerField(help_text="空闲容量(字节)")
    percent = serializers.FloatField(help_text="磁盘使用率百分比")


class NetworkInfoSerializer(serializers.Serializer):
    """
    网络信息序列化器
    """
    interface = serializers.CharField(help_text="网络接口名")
    bytes_sent = serializers.IntegerField(help_text="发送字节数")
    bytes_recv = serializers.IntegerField(help_text="接收字节数")
    packets_sent = serializers.IntegerField(help_text="发送包数")
    packets_recv = serializers.IntegerField(help_text="接收包数")


class ProcessInfoSerializer(serializers.Serializer):
    """
    进程信息序列化器
    """
    pid = serializers.IntegerField(help_text="进程ID")
    name = serializers.CharField(help_text="进程名")
    status = serializers.CharField(help_text="进程状态")
    cpu_percent = serializers.FloatField(help_text="CPU使用率")
    memory_percent = serializers.FloatField(help_text="内存使用率")
    memory_info = serializers.DictField(help_text="内存详细信息")
    create_time = serializers.DateTimeField(help_text="进程创建时间")
    cmdline = serializers.ListField(
        child=serializers.CharField(),
        help_text="命令行参数"
    )


class GPUInfoSerializer(serializers.Serializer):
    """
    GPU信息序列化器
    """
    index = serializers.IntegerField(help_text="GPU索引")
    name = serializers.CharField(help_text="GPU名称")
    driver_version = serializers.CharField(help_text="驱动版本", allow_null=True)
    memory_total = serializers.IntegerField(help_text="总显存(MB)", allow_null=True)
    memory_used = serializers.IntegerField(help_text="已用显存(MB)", allow_null=True)
    memory_free = serializers.IntegerField(help_text="空闲显存(MB)", allow_null=True)
    gpu_utilization = serializers.FloatField(help_text="GPU使用率", allow_null=True)
    memory_utilization = serializers.FloatField(help_text="显存使用率", allow_null=True)
    temperature = serializers.FloatField(help_text="GPU温度", allow_null=True)
    power_draw = serializers.FloatField(help_text="功耗(W)", allow_null=True)


class SystemMonitorSerializer(serializers.Serializer):
    """
    系统监测综合信息序列化器
    """
    system = SystemInfoSerializer(help_text="系统信息")
    cpu = CPUInfoSerializer(help_text="CPU信息")
    memory = MemoryInfoSerializer(help_text="内存信息")
    disks = DiskInfoSerializer(many=True, help_text="磁盘信息列表")
    network = NetworkInfoSerializer(many=True, help_text="网络信息列表")
    processes = ProcessInfoSerializer(many=True, help_text="进程信息列表")
    gpus = GPUInfoSerializer(many=True, help_text="GPU信息列表", allow_empty=True)