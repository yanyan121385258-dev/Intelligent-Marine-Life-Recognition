from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from studio_django_utils.responses.HertzResponse import HertzResponse
from .captcha_generator import HertzCaptchaGenerator
from .serializers import (
    CaptchaGenerateSerializer,
    CaptchaVerifyRequestSerializer,
    CaptchaVerifyResponseSerializer,
    CaptchaRefreshRequestSerializer,
    HertzResponseSerializer
)


class CaptchaGenerateAPIView(APIView):
    """验证码生成接口"""
    permission_classes = [AllowAny]
    serializer_class = CaptchaGenerateSerializer
    
    @extend_schema(
        operation_id='captcha_generate',
        summary='生成验证码',
        description='生成新的验证码图片和ID',
        responses={
            200: OpenApiResponse(
                response=HertzResponseSerializer,
                description='验证码生成成功',

            ),
            500: OpenApiResponse(
                response=HertzResponseSerializer,
                description='验证码生成失败'
            )
        },
        tags=['验证码']
    )
    def post(self, request):
        try:
            generator = HertzCaptchaGenerator()
            captcha_data = generator.generate_captcha()
            
            return HertzResponse.success(
                data=captcha_data,
                message='验证码生成成功'
            )
        except Exception as e:
            return HertzResponse.error(
                message='验证码生成失败',
                error=str(e)
            )


# CaptchaVerifyAPIView 接口已删除
# 验证码验证功能已集成到具体的业务接口中，不再提供独立的验证接口


class CaptchaRefreshAPIView(APIView):
    """验证码刷新接口"""
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id='captcha_refresh',
        summary='刷新验证码',
        description='刷新验证码，生成新的验证码图片',
        request=CaptchaRefreshRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=HertzResponseSerializer,
                description='验证码刷新成功',

            ),
            400: OpenApiResponse(
                response=HertzResponseSerializer,
                description='参数错误'
            ),
            500: OpenApiResponse(
                response=HertzResponseSerializer,
                description='验证码刷新失败'
            )
        },
        tags=['验证码']
    )
    def post(self, request):
        try:
            serializer = CaptchaRefreshRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return HertzResponse.fail(
                    message='参数不完整',
                    code=400
                )
            
            old_captcha_id = serializer.validated_data['captcha_id']
            
            generator = HertzCaptchaGenerator()
            captcha_data = generator.refresh_captcha(old_captcha_id)
            
            return HertzResponse.success(
                data=captcha_data,
                message='验证码刷新成功'
            )
        except Exception as e:
            return HertzResponse.error(
                message='验证码刷新失败',
                error=str(e)
            )