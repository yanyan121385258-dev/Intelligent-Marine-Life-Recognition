from django.contrib import admin
from .models import YoloModel, DetectionRecord, Dataset


@admin.register(YoloModel)
class YoloModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'is_enabled', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['name', 'version']
    readonly_fields = ['created_at', 'updated_at', 'model_path']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'version', 'description')
        }),
        ('模型文件', {
            'fields': ('model_file', 'model_path')
        }),
        ('配置', {
            'fields': ('categories', 'is_enabled')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DetectionRecord)
class DetectionRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'detection_type', 'model_name', 'object_count', 'created_at']
    list_filter = ['detection_type', 'model_name', 'created_at']
    search_fields = ['model_name']
    readonly_fields = ['created_at', 'original_filename', 'result_filename']
    
    fieldsets = (
        ('检测信息', {
            'fields': ('detection_type', 'model_name', 'model')
        }),
        ('文件信息', {
            'fields': ('original_file', 'original_filename', 'result_file', 'result_filename')
        }),
        ('检测结果', {
            'fields': ('object_count', 'detected_categories', 'confidence_threshold', 'processing_time')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        # 不允许手动添加检测记录
        return False


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'nc', 'train_images_count', 'val_images_count', 'test_images_count', 'created_at']
    search_fields = ['name', 'version']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']