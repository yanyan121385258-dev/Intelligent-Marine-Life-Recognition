"""
Django主项目URL配置模板
用于自动添加新app的URL路由
"""
<%!
from datetime import datetime
%>
<%
# 获取现有的URL配置
existing_urls = url_patterns or []
new_app_config = {
    'app_name': app_name,
    'url_path': url_path or f'api/{app_name.replace("hertz_studio_django_", "").replace("_", "/")}/',
    'comment': comment or f'{verbose_name or app_name} routes'
}

# 检查URL是否已存在
url_exists = any(config.get('app_name') == new_app_config['app_name'] for config in existing_urls)
if not url_exists:
    existing_urls.append(new_app_config)
%>
"""
URL configuration for hertz_server_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views

urlpatterns = [
    # 首页路由
    path('', views.index, name='index'),
    
% for url_config in existing_urls:
    # ${url_config['comment']}
    path('${url_config['url_path']}', include('${url_config['app_name']}.urls')),
    
% endfor
    # API documentation routes
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]

# 在开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])