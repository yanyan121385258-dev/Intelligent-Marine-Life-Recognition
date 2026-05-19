# URL路由模块
from django.urls import path, include
from . import auth_urls, management_urls

# 合并所有URL模式，添加auth/前缀
urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include(management_urls)),
]

__all__ = ['urlpatterns']