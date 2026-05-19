from rest_framework import serializers
from django.utils import timezone
from django.core.validators import RegexValidator
from ..models import HertzNotice, HertzUserNotice
from studio_django_auth.models import HertzUser


class NoticeCreateSerializer(serializers.ModelSerializer):
    """管理员创建通知序列化器"""
    
    class Meta:
        model = HertzNotice
        fields = [
            'title', 'content', 'notice_type', 'priority', 'is_top',
            'publish_time', 'expire_time', 'attachment_url'
        ]
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'required': '通知标题不能为空',
                    'blank': '通知标题不能为空',
                    'max_length': '通知标题长度不能超过200个字符'
                }
            },
            'content': {
                'error_messages': {
                    'required': '通知内容不能为空',
                    'blank': '通知内容不能为空'
                }
            },
            'publish_time': {
                'help_text': '发布时间，格式：YYYY-MM-DD HH:MM:SS'
            },
            'expire_time': {
                'help_text': '过期时间，格式：YYYY-MM-DD HH:MM:SS，可为空'
            }
        }
    
    def validate_title(self, value):
        """验证标题"""
        if not value or not value.strip():
            raise serializers.ValidationError('通知标题不能为空')
        return value.strip()
    
    def validate_content(self, value):
        """验证内容"""
        if not value or not value.strip():
            raise serializers.ValidationError('通知内容不能为空')
        return value.strip()
    
    def validate_expire_time(self, value):
        """验证过期时间"""
        if value and value <= timezone.now():
            raise serializers.ValidationError('过期时间必须大于当前时间')
        return value
    
    def validate(self, attrs):
        """整体验证"""
        publish_time = attrs.get('publish_time', timezone.now())
        expire_time = attrs.get('expire_time')
        
        if expire_time and publish_time >= expire_time:
            raise serializers.ValidationError('过期时间必须大于发布时间')
        
        return attrs


class NoticeUpdateSerializer(serializers.ModelSerializer):
    """管理员更新通知序列化器"""
    
    class Meta:
        model = HertzNotice
        fields = [
            'title', 'content', 'notice_type', 'priority', 'is_top',
            'publish_time', 'expire_time', 'attachment_url', 'status'
        ]
        extra_kwargs = {
            'title': {
                'error_messages': {
                    'required': '通知标题不能为空',
                    'blank': '通知标题不能为空',
                    'max_length': '通知标题长度不能超过200个字符'
                }
            },
            'content': {
                'error_messages': {
                    'required': '通知内容不能为空',
                    'blank': '通知内容不能为空'
                }
            }
        }
    
    def validate_title(self, value):
        """验证标题"""
        if not value or not value.strip():
            raise serializers.ValidationError('通知标题不能为空')
        return value.strip()
    
    def validate_content(self, value):
        """验证内容"""
        if not value or not value.strip():
            raise serializers.ValidationError('通知内容不能为空')
        return value.strip()
    
    def validate_expire_time(self, value):
        """验证过期时间"""
        if value and value <= timezone.now():
            raise serializers.ValidationError('过期时间必须大于当前时间')
        return value


class NoticeListSerializer(serializers.ModelSerializer):
    """管理员通知列表序列化器"""
    publisher_name = serializers.CharField(source='publisher.real_name', read_only=True)
    notice_type_display = serializers.CharField(source='get_notice_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    read_count = serializers.IntegerField(read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = HertzNotice
        fields = [
            'notice_id', 'title', 'notice_type', 'notice_type_display',
            'priority', 'priority_display', 'status', 'status_display',
            'is_top', 'publish_time', 'expire_time', 'publisher_name',
            'view_count', 'is_expired', 'read_count', 'unread_count',
            'created_at', 'updated_at'
        ]


class NoticeDetailSerializer(serializers.ModelSerializer):
    """管理员通知详情序列化器"""
    publisher_name = serializers.CharField(source='publisher.real_name', read_only=True)
    publisher_username = serializers.CharField(source='publisher.username', read_only=True)
    notice_type_display = serializers.CharField(source='get_notice_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    read_count = serializers.IntegerField(read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = HertzNotice
        fields = [
            'notice_id', 'title', 'content', 'notice_type', 'notice_type_display',
            'priority', 'priority_display', 'status', 'status_display',
            'is_top', 'publish_time', 'expire_time', 'attachment_url',
            'publisher_name', 'publisher_username', 'view_count',
            'is_expired', 'read_count', 'unread_count',
            'created_at', 'updated_at'
        ]


class UserNoticeListSerializer(serializers.ModelSerializer):
    """用户通知列表序列化器"""
    notice_type_display = serializers.CharField(source='notice.get_notice_type_display', read_only=True)
    priority_display = serializers.CharField(source='notice.get_priority_display', read_only=True)
    title = serializers.CharField(source='notice.title', read_only=True)
    publish_time = serializers.DateTimeField(source='notice.publish_time', read_only=True)
    is_top = serializers.BooleanField(source='notice.is_top', read_only=True)
    is_expired = serializers.BooleanField(source='notice.is_expired', read_only=True)
    
    class Meta:
        model = HertzUserNotice
        fields = [
            'notice', 'title', 'notice_type_display', 'priority_display',
            'is_top', 'publish_time', 'is_read', 'read_time',
            'is_starred', 'starred_time', 'is_expired', 'created_at'
        ]


class UserNoticeDetailSerializer(serializers.ModelSerializer):
    """用户通知详情序列化器"""
    title = serializers.CharField(source='notice.title', read_only=True)
    content = serializers.CharField(source='notice.content', read_only=True)
    notice_type_display = serializers.CharField(source='notice.get_notice_type_display', read_only=True)
    priority_display = serializers.CharField(source='notice.get_priority_display', read_only=True)
    attachment_url = serializers.URLField(source='notice.attachment_url', read_only=True)
    publish_time = serializers.DateTimeField(source='notice.publish_time', read_only=True)
    expire_time = serializers.DateTimeField(source='notice.expire_time', read_only=True)
    is_top = serializers.BooleanField(source='notice.is_top', read_only=True)
    is_expired = serializers.BooleanField(source='notice.is_expired', read_only=True)
    publisher_name = serializers.CharField(source='notice.publisher.real_name', read_only=True)
    
    class Meta:
        model = HertzUserNotice
        fields = [
            'notice', 'title', 'content', 'notice_type_display',
            'priority_display', 'attachment_url', 'publish_time',
            'expire_time', 'is_top', 'is_expired', 'publisher_name',
            'is_read', 'read_time', 'is_starred', 'starred_time',
            'created_at', 'updated_at'
        ]


class NoticeReadStatusSerializer(serializers.Serializer):
    """通知已读状态序列化器"""
    notice_id = serializers.IntegerField(
        help_text="通知ID",
        error_messages={
            'required': '通知ID不能为空',
            'invalid': '通知ID必须为整数'
        }
    )
    
    def validate_notice_id(self, value):
        """验证通知ID"""
        try:
            notice = HertzNotice.objects.get(notice_id=value, status=1)
            if notice.is_expired:
                raise serializers.ValidationError('该通知已过期')
            return value
        except HertzNotice.DoesNotExist:
            raise serializers.ValidationError('通知不存在或已下线')


class NoticeStarStatusSerializer(serializers.Serializer):
    """通知收藏状态序列化器"""
    notice_id = serializers.IntegerField(
        help_text="通知ID",
        error_messages={
            'required': '通知ID不能为空',
            'invalid': '通知ID必须为整数'
        }
    )
    is_starred = serializers.BooleanField(
        help_text="是否收藏",
        error_messages={
            'required': '收藏状态不能为空',
            'invalid': '收藏状态必须为布尔值'
        }
    )
    
    def validate_notice_id(self, value):
        """验证通知ID"""
        try:
            notice = HertzNotice.objects.get(notice_id=value, status=1)
            return value
        except HertzNotice.DoesNotExist:
            raise serializers.ValidationError('通知不存在或已下线')


class BatchNoticeReadSerializer(serializers.Serializer):
    """批量标记已读序列化器"""
    notice_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="通知ID列表",
        error_messages={
            'required': '通知ID列表不能为空',
            'empty': '通知ID列表不能为空'
        }
    )
    
    def validate_notice_ids(self, value):
        """验证通知ID列表"""
        if not value:
            raise serializers.ValidationError('通知ID列表不能为空')
        
        # 验证所有通知是否存在且有效
        valid_notices = HertzNotice.objects.filter(
            notice_id__in=value,
            status=1
        ).values_list('notice_id', flat=True)
        
        invalid_ids = set(value) - set(valid_notices)
        if invalid_ids:
            raise serializers.ValidationError(f'以下通知ID无效：{list(invalid_ids)}')
        
        return value