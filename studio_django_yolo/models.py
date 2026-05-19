from django.db import models
import json
import os
from django.utils import timezone


class Dataset(models.Model):
    name = models.CharField(max_length=100, verbose_name="数据集名称")
    version = models.CharField(max_length=50, verbose_name="版本", default="1.0")
    zip_file = models.FileField(upload_to='yolo/datasets/', verbose_name="数据集压缩包", null=True, blank=True)
    root_folder_path = models.CharField(max_length=500, verbose_name="数据集根路径")
    data_yaml_path = models.CharField(max_length=500, verbose_name="配置文件路径", null=True, blank=True)
    names = models.JSONField(default=list, verbose_name="类别名称")
    nc = models.IntegerField(default=0, verbose_name="类别数量")
    train_images_count = models.IntegerField(default=0, verbose_name="训练集图片数")
    train_labels_count = models.IntegerField(default=0, verbose_name="训练集标注数")
    val_images_count = models.IntegerField(default=0, verbose_name="验证集图片数")
    val_labels_count = models.IntegerField(default=0, verbose_name="验证集标注数")
    test_images_count = models.IntegerField(default=0, verbose_name="测试集图片数")
    test_labels_count = models.IntegerField(default=0, verbose_name="测试集标注数")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'hertz_yolo_dataset'
        verbose_name = '数据集'
        verbose_name_plural = '数据集'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"

    @property
    def root_path(self):
        """获取数据集根目录的绝对路径"""
        if not self.root_folder_path:
            return None
        # 如果已经是绝对路径，直接返回
        if os.path.isabs(self.root_folder_path):
            return self.root_folder_path
        # 否则，拼接 MEDIA_ROOT
        from django.conf import settings
        return os.path.join(settings.MEDIA_ROOT, self.root_folder_path)


class YoloModel(models.Model):
    """YOLO模型管理"""
    name = models.CharField(max_length=100, verbose_name="模型名称")
    version = models.CharField(max_length=50, verbose_name="版本", default="1.0")
    model_file = models.FileField(upload_to='yolo/models/', verbose_name="模型文件", null=True, blank=True)
    model_folder_path = models.CharField(max_length=500, verbose_name="模型文件夹路径", null=True, blank=True,
                                         help_text="解压后的模型文件夹路径")
    best_model_path = models.CharField(max_length=500, verbose_name="最佳模型路径", null=True, blank=True,
                                       help_text="best.pt文件的完整路径")
    last_model_path = models.CharField(max_length=500, verbose_name="最后模型路径", null=True, blank=True,
                                       help_text="last.pt文件的完整路径")
    categories = models.JSONField(default=dict, verbose_name="类别信息", help_text="JSON格式的类别信息")
    is_enabled = models.BooleanField(default=False, verbose_name="是否启用")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'hertz_yolo_yolo_model'
        verbose_name = 'YOLO模型'
        verbose_name_plural = 'YOLO模型'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"

    def save(self, *args, **kwargs):
        # 如果设置为启用，则禁用其他所有模型
        if self.is_enabled:
            YoloModel.objects.exclude(pk=self.pk).update(is_enabled=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_enabled_model(cls):
        """获取当前启用的模型"""
        return cls.objects.filter(is_enabled=True).first()

    def _get_absolute_path(self, relative_path):
        """将相对路径转换为绝对路径"""
        if not relative_path:
            return None
        # 如果已经是绝对路径，直接返回
        if os.path.isabs(relative_path):
            return relative_path
        # 否则，拼接 MEDIA_ROOT
        from django.conf import settings
        return os.path.join(settings.MEDIA_ROOT, relative_path)

    @property
    def model_path(self):
        """获取模型文件的完整绝对路径"""
        if self.best_model_path:
            # 优先使用 best_model_path
            return self._get_absolute_path(self.best_model_path)
        elif self.last_model_path:
            # 其次使用 last_model_path
            return self._get_absolute_path(self.last_model_path)
        elif self.model_folder_path:
            # 如果有文件夹路径，尝试查找 weights/best.pt 或 weights/last.pt
            folder_abs = self._get_absolute_path(self.model_folder_path)
            if folder_abs:
                best_pt_path = os.path.join(folder_abs, 'weights', 'best.pt')
                if os.path.exists(best_pt_path):
                    return best_pt_path
                last_pt_path = os.path.join(folder_abs, 'weights', 'last.pt')
                if os.path.exists(last_pt_path):
                    return last_pt_path
        elif self.model_file:
            return self.model_file.path
        return None

    @property
    def weights_folder_path(self):
        """获取权重文件夹绝对路径"""
        if self.model_folder_path:
            folder_abs = self._get_absolute_path(self.model_folder_path)
            if folder_abs:
                return os.path.join(folder_abs, 'weights')
        return None


class DetectionRecord(models.Model):
    """检测记录"""
    DETECTION_TYPES = [
        ('image', '图片检测'),
        ('video', '视频检测'),
    ]

    original_file = models.FileField(upload_to='detection/original/', verbose_name="原始文件")
    result_file = models.FileField(upload_to='detection/result/', verbose_name="检测结果文件")
    detection_type = models.CharField(max_length=10, choices=DETECTION_TYPES, verbose_name="检测类型")
    model_name = models.CharField(max_length=100, verbose_name="使用的模型名称")
    model = models.ForeignKey(YoloModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="使用的模型")
    user = models.ForeignKey('studio_django_auth.HertzUser', on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="检测用户", related_name="detection_records")
    user_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="用户名称")
    object_count = models.IntegerField(default=0, verbose_name="检测到的对象数量")
    detected_categories = models.JSONField(default=list, verbose_name="检测到的类别列表")
    confidence_threshold = models.FloatField(default=0.5, verbose_name="置信度阈值")
    confidence_scores = models.JSONField(default=list, verbose_name="真实置信度列表",
                                         help_text="检测到的每个对象的置信度分数")
    avg_confidence = models.FloatField(null=True, blank=True, verbose_name="平均置信度",
                                       help_text="所有检测对象的平均置信度")
    processing_time = models.FloatField(null=True, blank=True, verbose_name="处理时间(秒)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="检测时间")

    class Meta:
        db_table = 'hertz_yolo_detection_record'
        verbose_name = '检测记录'
        verbose_name_plural = '检测记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.detection_type} - {self.model_name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def original_filename(self):
        """获取原始文件名"""
        if self.original_file:
            return os.path.basename(self.original_file.name)

    @property
    def result_filename(self):
        """获取结果文件名"""
        if self.result_file:
            return os.path.basename(self.result_file.name)
        return ""


class ModelCategory(models.Model):
    """模型类别管理"""
    ALERT_LEVELS = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
        ('none', '无'),
    ]

    model = models.ForeignKey(YoloModel, on_delete=models.CASCADE, related_name='model_categories',
                              verbose_name="关联模型")
    name = models.CharField(max_length=100, verbose_name="类别名称")
    alias = models.CharField(max_length=100, blank=True, verbose_name="类别别名",
                             help_text="用于显示的别名，如果为空则使用类别名称")
    category_id = models.IntegerField(default=0, verbose_name="类别ID", help_text="模型中的类别索引")
    description = models.TextField(blank=True, verbose_name="类别描述")
    alert_level = models.CharField(max_length=30, choices=ALERT_LEVELS, default='medium', verbose_name="告警等级")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'hertz_yolo_model_category'
        verbose_name = '模型类别'
        verbose_name_plural = '模型类别'
        ordering = ['model', 'category_id']
        unique_together = ['model', 'category_id']  # 确保同一模型中的类别ID唯一

    def __str__(self):
        return f"{self.model.name} - {self.display_name} ({self.get_alert_level_display()})"

    @property
    def display_name(self):
        """获取显示名称，优先使用别名"""
        return self.alias if self.alias else self.name


class Alert(models.Model):
    """告警记录"""
    ALERT_LEVELS = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
        ('none', '无'),
    ]

    ALERT_STATUS = [
        ('pending', '待处理'),
        ('is_confirm', '已处理'),
        ('false_positive', '误报'),
    ]

    detection_record = models.OneToOneField(DetectionRecord, on_delete=models.CASCADE, related_name='alert',
                                            verbose_name="关联的检测记录")
    user = models.ForeignKey('studio_django_auth.HertzUser', on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="用户", related_name="alerts")
    user_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="用户名称")
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS, default='medium', verbose_name="告警等级")
    alert_category = models.CharField(max_length=100, verbose_name="告警类别", help_text="检测到的对象类别")
    category = models.ForeignKey(ModelCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="关联类别")
    status = models.CharField(max_length=30, choices=ALERT_STATUS, default='pending', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="删除时间")

    class Meta:
        db_table = 'hertz_yolo_alert_record'
        verbose_name = '告警记录'
        verbose_name_plural = '告警记录'
        ordering = ['alert_level', '-created_at']

    def __str__(self):
        return f"告警-{self.alert_category}-等级{self.get_alert_level_display()}-{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def delete(self, *args, **kwargs):
        """软删除，保留历史记录"""
        self.status = 'deleted'
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        """硬删除，完全从数据库中删除"""
        super().delete(*args, **kwargs)

    @property
    def result_filename(self):
        """获取结果文件名"""
        if self.result_file:
            return os.path.basename(self.result_file.name)
        return ""

    def get_detection_summary(self):
        """获取检测摘要信息"""
        return {
            'id': self.id,
            'type': self.detection_type,
            'model': self.model_name,
            'object_count': self.object_count,
            'categories': self.detected_categories,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat(),
            'original_file': self.original_file.url if self.original_file else None,
            'result_file': self.result_file.url if self.result_file else None,
        }
