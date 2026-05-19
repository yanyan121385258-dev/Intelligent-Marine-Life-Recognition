from rest_framework import serializers


class CaptchaGenerateSerializer(serializers.Serializer):
    """验证码生成响应序列化器"""
    captcha_id = serializers.CharField(help_text="验证码ID")
    image_data = serializers.CharField(help_text="Base64编码的验证码图片")
    expires_at = serializers.DateTimeField(help_text="过期时间")


class CaptchaVerifyRequestSerializer(serializers.Serializer):
    """验证码验证请求序列化器"""
    captcha_id = serializers.CharField(help_text="验证码ID")
    user_input = serializers.CharField(help_text="用户输入的验证码")


class CaptchaVerifyResponseSerializer(serializers.Serializer):
    """验证码验证响应序列化器"""
    valid = serializers.BooleanField(help_text="验证是否通过")


class CaptchaRefreshRequestSerializer(serializers.Serializer):
    """验证码刷新请求序列化器"""
    captcha_id = serializers.CharField(help_text="旧验证码ID")


class HertzResponseSerializer(serializers.Serializer):
    """统一响应格式序列化器"""
    success = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="响应消息")
    data = serializers.JSONField(help_text="响应数据", required=False)
    code = serializers.IntegerField(help_text="状态码", required=False)
    error = serializers.CharField(help_text="错误信息", required=False)