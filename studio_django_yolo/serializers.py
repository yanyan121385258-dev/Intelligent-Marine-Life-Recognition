from rest_framework import serializers
from .models import YoloModel, DetectionRecord, Alert, ModelCategory, Dataset


class YoloModelSerializer(serializers.ModelSerializer):
    """YOLO模型序列化器"""
    model_path = serializers.ReadOnlyField()
    weights_folder_path = serializers.ReadOnlyField()
    
    class Meta:
        model = YoloModel
        fields = [
            'id', 'name', 'version', 'model_file', 'model_folder_path', 
            'model_path', 'weights_folder_path', 'categories', 'is_enabled', 
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'model_path', 'weights_folder_path']

    def validate_model_file(self, value):
        """验证模型文件格式"""
        if value and not value.name.endswith('.pt'):
            raise serializers.ValidationError("模型文件必须是 .pt 格式")
        return value

    def create(self, validated_data):
        """创建模型时，如果是第一个模型则自动启用"""
        if not YoloModel.objects.exists():
            validated_data['is_enabled'] = True
        return super().create(validated_data)


class YoloModelListSerializer(serializers.ModelSerializer):
    """YOLO模型列表序列化器（简化版）"""
    
    class Meta:
        model = YoloModel
        fields = ['id', 'name', 'version', 'is_enabled', 'created_at']


class DetectionRecordSerializer(serializers.ModelSerializer):
    """检测记录序列化器"""
    original_filename = serializers.ReadOnlyField()
    result_filename = serializers.ReadOnlyField()
    model_info = serializers.SerializerMethodField()
    
    class Meta:
        model = DetectionRecord
        fields = [
            'id', 'original_file', 'result_file', 'original_filename', 'result_filename',
            'detection_type', 'model_name', 'model_info', 'object_count', 
            'detected_categories', 'confidence_threshold', 'confidence_scores', 'avg_confidence',
            'processing_time', 'created_at'
        ]
        read_only_fields = [
            'id', 'result_file', 'original_filename', 'result_filename',
            'model_name', 'object_count', 'detected_categories', 'confidence_scores', 'avg_confidence',
            'processing_time', 'created_at'
        ]

    def get_model_info(self, obj):
        """获取模型信息"""
        if obj.model:
            return {
                'id': obj.model.id,
                'name': obj.model.name,
                'version': obj.model.version
            }
        return None


class DetectionRequestSerializer(serializers.Serializer):
    """检测请求序列化器"""
    file = serializers.FileField(help_text="要检测的图片或视频文件")
    model_id = serializers.IntegerField(required=False, help_text="指定使用的模型ID，不指定则使用当前启用的模型")
    confidence_threshold = serializers.FloatField(
        default=0.5, 
        min_value=0.1, 
        max_value=1.0,
        help_text="置信度阈值，范围0.1-1.0"
    )

    def validate_file(self, value):
        """验证上传的文件格式"""
        allowed_image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        allowed_video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
        file_name = value.name.lower()
        
        # 检查是否是支持的格式
        is_image = any(file_name.endswith(ext) for ext in allowed_image_extensions)
        is_video = any(file_name.endswith(ext) for ext in allowed_video_extensions)
        
        if not (is_image or is_video):
            raise serializers.ValidationError(
                f"不支持的文件格式。支持的图片格式: {', '.join(allowed_image_extensions)}，"
                f"支持的视频格式: {', '.join(allowed_video_extensions)}"
            )
        
        # 检查文件大小（图片最大50MB，视频最大500MB）
        max_size = 500 * 1024 * 1024 if is_video else 50 * 1024 * 1024  # 500MB for video, 50MB for image
        if value.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise serializers.ValidationError(f"文件大小不能超过 {max_size_mb}MB")
        
        return value

    def validate_model_id(self, value):
        """验证模型ID"""
        if value is not None:
            try:
                model = YoloModel.objects.get(id=value)
                if not model.is_enabled:
                    raise serializers.ValidationError("指定的模型未启用")
            except YoloModel.DoesNotExist:
                raise serializers.ValidationError("指定的模型不存在")
        return value


class DetectionResponseSerializer(serializers.Serializer):
    """检测响应序列化器"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(required=False)
    detection_id = serializers.IntegerField(required=False)
    result_file_url = serializers.URLField(required=False)
    object_count = serializers.IntegerField(required=False)
    detected_categories = serializers.ListField(required=False)
    processing_time = serializers.FloatField(required=False)


class ModelEnableSerializer(serializers.Serializer):
    """模型启用序列化器"""
    pass  # 只需要模型ID，通过URL传递


class ModelCategorySerializer(serializers.ModelSerializer):
    """模型类别序列化器"""
    alert_level_display = serializers.CharField(source='get_alert_level_display', read_only=True)
    model_info = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = ModelCategory
        fields = [
            'id', 'model', 'model_info', 'name', 'alias', 'display_name', 'category_id', 'description', 
            'alert_level', 'alert_level_display', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'display_name', 'model', 'name', 'category_id', 'description']

    def get_model_info(self, obj):
        """获取关联模型信息"""
        if obj.model:
            return {
                'id': obj.model.id,
                'name': obj.model.name,
                'version': obj.model.version,
                'is_enabled': obj.model.is_enabled
            }
        return None

    def validate(self, data):
        """验证模型和类别ID的唯一性"""
        model = data.get('model')
        category_id = data.get('category_id')
        
        if model and category_id is not None:
            # 检查同一模型中类别ID的唯一性
            queryset = ModelCategory.objects.filter(model=model, category_id=category_id)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'category_id': f'模型 {model.name} 中已存在类别ID {category_id}'
                })
        
        return data


class ModelCategoryListSerializer(serializers.ModelSerializer):
    """模型类别列表序列化器（简化版）"""
    alert_level_display = serializers.CharField(source='get_alert_level_display', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = ModelCategory
        fields = ['id', 'model', 'model_name', 'name', 'alias', 'display_name', 'category_id', 'alert_level', 'alert_level_display', 'is_active']


class AlertSerializer(serializers.ModelSerializer):
    """告警记录序列化器"""
    detection_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    alert_level_display = serializers.CharField(source='get_alert_level_display', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'detection_record', 'detection_info', 'user', 'user_name', 
            'alert_level', 'alert_level_display', 'alert_category', 'category', 'category_info', 
            'status', 'created_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'deleted_at', 'alert_level_display']
    
    def get_detection_info(self, obj):
        """获取检测记录信息"""
        if obj.detection_record:
            return {
                'id': obj.detection_record.id,
                'detection_type': obj.detection_record.detection_type,
                'original_filename': f"/media/detection/original/{obj.detection_record.original_filename}",
                'result_filename': f"/media/detection/result/{obj.detection_record.result_filename}",
                'object_count': obj.detection_record.object_count,
                'avg_confidence': obj.detection_record.avg_confidence,
            }
        return None
    
    def get_category_info(self, obj):
        """获取类别信息"""
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'alert_level': obj.category.alert_level,
                'alert_level_display': obj.category.get_alert_level_display(),
            }
        return None


class AlertStatusUpdateSerializer(serializers.ModelSerializer):
    """告警状态更新序列化器"""
    
    class Meta:
        model = Alert
        fields = ['status']
    
    def validate_status(self, value):
        """验证状态值"""
        valid_statuses = [choice[0] for choice in Alert.ALERT_STATUS]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"无效的状态值。可选值: {', '.join(valid_statuses)}")
        return value


class ModelUploadSerializer(serializers.Serializer):
    """模型压缩包上传序列化器"""
    zip_file = serializers.FileField(help_text="YOLO模型压缩包文件 (.zip)")
    name = serializers.CharField(max_length=100, help_text="模型名称")
    version = serializers.CharField(max_length=20, default="1.0", help_text="模型版本")
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, help_text="模型描述")

    def validate_zip_file(self, value):
        """验证压缩包文件"""
        if not value.name.lower().endswith('.zip'):
            raise serializers.ValidationError("只支持 ZIP 格式的压缩包")
        
        # 检查文件大小 (限制为100MB)
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("压缩包文件大小不能超过 100MB")
        
        return value

    def validate_name(self, value):
        """验证模型名称"""
        if not value.strip():
            raise serializers.ValidationError("模型名称不能为空")
        return value.strip()


class ModelUploadResponseSerializer(serializers.Serializer):
    """模型上传响应序列化器"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(required=False)


class DatasetUploadSerializer(serializers.Serializer):
    zip_file = serializers.FileField()
    name = serializers.CharField(max_length=100)
    version = serializers.CharField(max_length=50, default='1.0')
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_zip_file(self, value):
        if not value.name.lower().endswith('.zip'):
            raise serializers.ValidationError('只支持 ZIP 格式的压缩包')
        if value.size > 500 * 1024 * 1024:
            raise serializers.ValidationError('压缩包文件大小不能超过 500MB')
        return value

    def validate_name(self, value):
        v = value.strip()
        if not v:
            raise serializers.ValidationError('数据集名称不能为空')
        return v


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'version', 'zip_file', 'root_folder_path', 'data_yaml_path',
            'names', 'nc',
            'train_images_count', 'train_labels_count',
            'val_images_count', 'val_labels_count',
            'test_images_count', 'test_labels_count',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DatasetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'name', 'version', 'nc', 'train_images_count', 'val_images_count', 'test_images_count', 'created_at']