from rest_framework import serializers
from ..models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    """
    操作日志序列化器
    用于API响应的数据序列化
    """
    
    username = serializers.CharField(read_only=True, help_text="操作用户名")
    action_type_display = serializers.CharField(
        source='get_action_type_display', 
        read_only=True, 
        help_text="操作类型显示名称"
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True, 
        help_text="状态显示名称"
    )
    is_success = serializers.BooleanField(read_only=True, help_text="是否成功")
    formatted_request_data = serializers.CharField(
        read_only=True, 
        help_text="格式化的请求数据"
    )
    
    class Meta:
        model = OperationLog
        fields = [
            'log_id',
            'user',
            'username',
            'action_type',
            'action_type_display',
            'module',
            'description',
            'target_model',
            'target_id',
            'ip_address',
            'user_agent',
            'request_data',
            'formatted_request_data',
            'response_status',
            'status',
            'status_display',
            'is_success',
            'created_at',
        ]
        read_only_fields = [
            'log_id',
            'user',
            'username',
            'action_type_display',
            'status_display',
            'is_success',
            'formatted_request_data',
            'created_at',
        ]


class OperationLogListSerializer(serializers.ModelSerializer):
    """
    操作日志列表序列化器
    用于列表页面的简化数据展示
    """
    
    username = serializers.CharField(read_only=True, help_text="操作用户名")
    action_type_display = serializers.CharField(
        source='get_action_type_display', 
        read_only=True, 
        help_text="操作类型显示名称"
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True, 
        help_text="状态显示名称"
    )
    is_success = serializers.BooleanField(read_only=True, help_text="是否成功")
    
    class Meta:
        model = OperationLog
        fields = [
            'log_id',
            'username',
            'action_type',
            'action_type_display',
            'module',
            'description',
            'ip_address',
            'response_status',
            'status',
            'status_display',
            'is_success',
            'created_at',
        ]
        read_only_fields = [
            'log_id',
            'username',
            'action_type_display',
            'status_display',
            'is_success',
            'created_at',
        ]


class OperationLogFilterSerializer(serializers.Serializer):
    """
    操作日志过滤参数序列化器
    用于API查询参数验证
    """
    
    user_id = serializers.IntegerField(
        required=False, 
        help_text="用户ID"
    )
    username = serializers.CharField(
        required=False, 
        max_length=150, 
        help_text="用户名"
    )
    action_type = serializers.ChoiceField(
        choices=OperationLog.ACTION_TYPE_CHOICES,
        required=False,
        help_text="操作类型"
    )
    module = serializers.CharField(
        required=False, 
        max_length=50, 
        help_text="操作模块"
    )
    status = serializers.ChoiceField(
        choices=OperationLog.STATUS_CHOICES,
        required=False,
        help_text="操作状态"
    )
    ip_address = serializers.CharField(
        max_length=45,
        required=False,
        help_text="IP地址"
    )
    start_date = serializers.DateTimeField(
        required=False,
        help_text="开始时间"
    )
    end_date = serializers.DateTimeField(
        required=False,
        help_text="结束时间"
    )
    page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
        help_text="页码"
    )
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
        default=20,
        help_text="每页数量"
    )
    
    def validate(self, attrs):
        """
        验证过滤参数
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始时间不能大于结束时间")
        
        return attrs