from django.urls import path
from .api_views import CaptchaGenerateAPIView, CaptchaRefreshAPIView

app_name = 'hertz_captcha'

urlpatterns = [
    # API endpoints for documentation
    path('generate/', CaptchaGenerateAPIView.as_view(), name='api_generate'),
    # verify接口已删除，验证功能已集成到具体业务接口中
    path('refresh/', CaptchaRefreshAPIView.as_view(), name='api_refresh'),
]