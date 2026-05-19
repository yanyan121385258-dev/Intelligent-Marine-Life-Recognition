"""
URL configuration for server_django project.

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
    
    # Hertz Captcha routes
    path('api/captcha/', include('studio_django_captcha.urls')),
    
    # Hertz Auth routes
    path('api/', include('studio_django_auth.urls')),
    
    # Demo app routes
    path('', include('demo.urls')),
    
    # Hertz AI routes
    path('api/ai/', include('studio_django_ai.urls')),
    
    # Hertz System Monitor routes
    path('api/system/', include('studio_django_system_monitor.urls')),
    
    # Hertz System Notification routes
    path('api/notice/', include('studio_django_notice.urls')),
    
    # Hertz Log routes
    path('api/log/', include('studio_django_log.urls')),
    
    # Hertz Wiki routes
    path('api/wiki/', include('studio_django_wiki.urls')),
    
 
    
    # OpenAPI documentation
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]

# 在开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
