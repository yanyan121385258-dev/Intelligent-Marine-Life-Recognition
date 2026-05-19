from django.urls import path, include

app_name = 'studio_django_auth'

urlpatterns = [
    # 认证相关API
    path('auth/', include('studio_django_auth.urls.auth_urls')),
    
    # 管理相关API
    path('', include('studio_django_auth.urls.management_urls')),
]