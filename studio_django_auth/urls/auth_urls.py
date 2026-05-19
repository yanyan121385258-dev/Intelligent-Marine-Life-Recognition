from django.urls import path
from ..views.auth_views import (
    user_login, user_register, user_logout, change_password, reset_password,
    get_user_info, update_user_info, get_user_menus, send_email_code, refresh_token,
    upload_avatar
)

urlpatterns = [
    # 用户认证
    path('login/', user_login, name='user_login'),
    path('register/', user_register, name='user_register'),
    path('logout/', user_logout, name='user_logout'),
    
    # 密码管理
    path('password/change/', change_password, name='change_password'),
    path('password/reset/', reset_password, name='reset_password'),
    
    # 用户信息
    path('user/info/', get_user_info, name='get_user_info'),
    path('user/info/update/', update_user_info, name='update_user_info'),
    path('user/avatar/upload/', upload_avatar, name='upload_avatar'),
    path('user/menus/', get_user_menus, name='get_user_menus'),
    
    # 验证码
    path('email/code/', send_email_code, name='send_email_code'),
    
    # Token刷新
    path('token/refresh/', refresh_token, name='refresh_token'),
]
