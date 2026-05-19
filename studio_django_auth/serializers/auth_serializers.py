from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.validators import RegexValidator
from datetime import datetime
from studio_django_utils.validators import EmailValidator, PhoneValidator, PasswordValidator
from studio_django_utils.crypto import EncryptionUtils
from ..models import HertzUser, HertzRole, HertzDepartment


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(
        max_length=50,
        help_text="用户名/邮箱/手机号",
        error_messages={
            'required': '请输入用户名',
            'blank': '用户名不能为空',
            'max_length': '用户名长度不能超过50个字符'
        }
    )
    password = serializers.CharField(
        max_length=128,
        help_text="密码",
        error_messages={
            'required': '请输入密码',
            'blank': '密码不能为空',
            'max_length': '密码长度不能超过128个字符'
        }
    )
    captcha_code = serializers.CharField(
        max_length=6,
        required=True,
        help_text="验证码",
        error_messages={
            'required': '请输入验证码',
            'blank': '验证码不能为空',
            'max_length': '验证码长度不能超过6个字符'
        }
    )
    captcha_key = serializers.CharField(
        max_length=64,
        required=True,
        help_text="验证码key",
        error_messages={
            'required': '请提供验证码key',
            'blank': '验证码key不能为空',
            'max_length': '验证码key长度不能超过64个字符'
        }
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        captcha_code = attrs.get('captcha_code')
        captcha_key = attrs.get('captcha_key')
        
        if not username or not password:
            raise serializers.ValidationError('用户名和密码不能为空')
        
        # 严格验证码校验 - 必须验证通过才能继续
        if not captcha_code or not captcha_key:
            raise serializers.ValidationError('验证码和验证码key不能为空')
        
        # 导入验证码生成器进行验证
        from studio_django_captcha.captcha_generator import HertzCaptchaGenerator
        captcha_generator = HertzCaptchaGenerator()
        
        # 验证验证码
        is_captcha_valid = captcha_generator.verify_captcha(captcha_key, captcha_code)
        if not is_captcha_valid:
            raise serializers.ValidationError('验证码错误或已过期，请重新获取验证码')
        
        # 查找用户（支持用户名、邮箱、手机号登录）
        user = None
        try:
            if EmailValidator.is_valid_email(username):
                user = HertzUser.objects.get(email=username, status=1)
            elif PhoneValidator.is_valid_china_mobile(username):
                user = HertzUser.objects.get(phone=username, status=1)
            else:
                user = HertzUser.objects.get(username=username, status=1)
        except HertzUser.DoesNotExist:
            raise serializers.ValidationError('用户不存在或已被禁用')
        
        # 验证密码 - 支持Django哈希格式和旧的MD5格式
        if not self._check_password(password, user.password):
            raise serializers.ValidationError('密码错误')
        
        attrs['user'] = user
        return attrs
    
    def _check_password(self, raw_password, encoded_password):
        """检查密码，支持Django哈希格式和旧的MD5格式"""
        # 如果是Django哈希格式（包含$符号）
        if '$' in encoded_password:
            return check_password(raw_password, encoded_password)
        else:
            # 旧的MD5格式
            return encoded_password == EncryptionUtils.md5_hash(raw_password)


class UserRegisterSerializer(serializers.Serializer):
    """用户注册序列化器"""
    username = serializers.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]{3,50}$',
                message='用户名只能包含字母、数字和下划线，长度3-50个字符'
            )
        ],
        help_text="用户名"
    )
    password = serializers.CharField(
        max_length=128,
        help_text="密码"
    )
    confirm_password = serializers.CharField(
        max_length=128,
        help_text="确认密码"
    )
    email = serializers.EmailField(
        help_text="邮箱"
    )
    phone = serializers.CharField(
        max_length=20,
        help_text="手机号"
    )
    real_name = serializers.CharField(
        max_length=50,
        help_text="真实姓名"
    )
    email_code = serializers.CharField(
        max_length=6,
        required=False,
        help_text="邮箱验证码"
    )

    def validate_username(self, value):
        if HertzUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_email(self, value):
        if not EmailValidator.is_valid_email(value):
            raise serializers.ValidationError('邮箱格式不正确')
        if HertzUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已被注册')
        return value

    def validate_phone(self, value):
        if not PhoneValidator.is_valid_china_mobile(value):
            raise serializers.ValidationError('手机号格式不正确')
        if HertzUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError('手机号已被注册')
        return value

    def validate_password(self, value):
        is_valid, errors = PasswordValidator.validate_password_strength(value)
        if not is_valid:
            raise serializers.ValidationError('密码强度不够：' + '，'.join(errors))
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError('两次输入的密码不一致')
        
        # 按开关要求邮箱验证码
        require_verification = getattr(settings, 'REGISTER_EMAIL_VERIFICATION', 0) == 1
        if require_verification:
            email_code = attrs.get('email_code')
            if not email_code:
                raise serializers.ValidationError('邮箱验证码不能为空')
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('email_code', None)
        
        # 使用Django的密码哈希系统
        password = validated_data.pop('password')
        user = HertzUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(
        max_length=128,
        help_text="原密码"
    )
    new_password = serializers.CharField(
        max_length=128,
        help_text="新密码"
    )
    confirm_password = serializers.CharField(
        max_length=128,
        help_text="确认新密码"
    )

    def validate_new_password(self, value):
        is_valid, errors = PasswordValidator.validate_password_strength(value)
        if not is_valid:
            raise serializers.ValidationError('密码强度不够：' + '，'.join(errors))
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError('两次输入的新密码不一致')
        
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """重置密码序列化器"""
    email = serializers.EmailField(
        help_text="邮箱"
    )
    # email_code = serializers.CharField(
    #     max_length=6,
    #     help_text="邮箱验证码"
    # )
    new_password = serializers.CharField(
        max_length=128,
        help_text="新密码"
    )
    confirm_password = serializers.CharField(
        max_length=128,
        help_text="确认新密码"
    )

    def validate_email(self, value):
        if not EmailValidator.is_valid_email(value):
            raise serializers.ValidationError('邮箱格式不正确')
        if not HertzUser.objects.filter(email=value, status=1).exists():
            raise serializers.ValidationError('邮箱未注册或用户已被禁用')
        return value

    def validate_new_password(self, value):
        is_valid, errors = PasswordValidator.validate_password_strength(value)
        if not is_valid:
            raise serializers.ValidationError('密码强度不够：' + '，'.join(errors))
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError('两次输入的新密码不一致')
        
        return attrs


class UserInfoSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    department_name = serializers.CharField(source='department.dept_name', read_only=True)
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = HertzUser
        fields = [
            'user_id', 'username', 'email', 'phone', 'real_name', 'avatar',
            'gender', 'birthday', 'department_id', 'department_name', 'status',
            'last_login_time', 'last_login_ip', 'created_at', 'updated_at', 'roles'
        ]
        read_only_fields = [
            'user_id', 'username', 'last_login_time', 'last_login_ip',
            'created_at', 'updated_at'
        ]
    
    def get_roles(self, obj):
        """获取用户角色列表"""
        roles = obj.roles.filter(status=1)
        return [{
            'role_id': role.role_id,
            'role_name': role.role_name,
            'role_code': role.role_code
        } for role in roles]


class UpdateUserInfoSerializer(serializers.ModelSerializer):
    """更新用户信息序列化器"""
    
    class Meta:
        model = HertzUser
        fields = ['email', 'phone', 'real_name', 'avatar', 'gender', 'birthday']
    
    def validate_email(self, value):
        if not EmailValidator.is_valid_email(value):
            raise serializers.ValidationError('邮箱格式不正确')
        # 检查邮箱是否被其他用户使用
        if HertzUser.objects.filter(email=value).exclude(user_id=self.instance.user_id).exists():
            raise serializers.ValidationError('邮箱已被其他用户使用')
        return value
    
    def validate_phone(self, value):
        if not PhoneValidator.is_valid_phone(value):
            raise serializers.ValidationError('手机号格式不正确')
        # 检查手机号是否被其他用户使用
        if HertzUser.objects.filter(phone=value).exclude(user_id=self.instance.user_id).exists():
            raise serializers.ValidationError('手机号已被其他用户使用')
        return value
    
    def validate_birthday(self, value):
        """
        验证生日字段，支持多种日期格式
        """
        if value is None:
            return value
        
        # 如果是字符串，尝试解析多种格式
        if isinstance(value, str):
            # 支持的日期格式
            date_formats = [
                '%Y-%m-%d',      # 2023-12-25
                '%Y/%m/%d',      # 2023/12/25
                '%d/%m/%Y',      # 25/12/2023
                '%d-%m-%Y',      # 25-12-2023
                '%m/%d/%Y',      # 12/25/2023
                '%m-%d-%Y',      # 12-25-2023
            ]
            
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(value, date_format).date()
                    return parsed_date
                except ValueError:
                    continue
            
            # 如果所有格式都失败，抛出错误
            raise serializers.ValidationError(
                '日期格式不正确，请使用以下格式之一：YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY, DD-MM-YYYY, MM/DD/YYYY, MM-DD-YYYY'
            )
        
        return value


class SendEmailCodeSerializer(serializers.Serializer):
    """发送邮箱验证码序列化器"""
    email = serializers.EmailField(
        help_text="邮箱地址"
    )
    code_type = serializers.ChoiceField(
        choices=[('register', '注册'), ('reset_password', '重置密码')],
        help_text="验证码类型"
    )

    def validate_email(self, value):
        if not EmailValidator.is_valid_email(value):
            raise serializers.ValidationError('邮箱格式不正确')
        return value


class RefreshTokenSerializer(serializers.Serializer):
    """刷新Token序列化器"""
    refresh_token = serializers.CharField(
        max_length=500,
        help_text="刷新令牌"
    )

    def validate_refresh_token(self, value):
        if not value:
            raise serializers.ValidationError('refresh_token不能为空')
        return value