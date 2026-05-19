from django.db import models


class TrainingJob(models.Model):
    STATUS_CHOICES = [
        ('queued', '排队中'),
        ('running', '训练中'),
        ('canceling', '取消中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('canceled', '已取消'),
    ]

    dataset = models.ForeignKey('studio_django_yolo.Dataset', on_delete=models.CASCADE, related_name='training_jobs')
    model_family = models.CharField(max_length=20, verbose_name='YOLO版本')
    model_size = models.CharField(max_length=5, verbose_name='模型大小', blank=True)
    weight_path = models.CharField(max_length=500, verbose_name='预训练权重路径', blank=True)
    config_path = models.CharField(max_length=500, verbose_name='模型配置路径')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued', verbose_name='状态')
    logs_path = models.CharField(max_length=500, verbose_name='日志文件路径', blank=True)
    runs_path = models.CharField(max_length=500, verbose_name='训练输出目录', blank=True)
    best_model_path = models.CharField(max_length=500, verbose_name='best.pt路径', blank=True)
    last_model_path = models.CharField(max_length=500, verbose_name='last.pt路径', blank=True)
    progress = models.IntegerField(default=0, verbose_name='进度百分比')
    epochs = models.IntegerField(default=100, verbose_name='轮次')
    imgsz = models.IntegerField(default=640, verbose_name='图像尺寸')
    batch = models.IntegerField(default=16, verbose_name='批大小')
    device = models.CharField(max_length=50, default='0', verbose_name='设备')
    optimizer = models.CharField(max_length=50, default='SGD', verbose_name='优化器')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')

    class Meta:
        db_table = 'hertz_yolo_train_train_job'
        ordering = ['-created_at']
        verbose_name = '训练任务'
        verbose_name_plural = '训练任务'