from django.urls import path
from .views.admin_views import (
    admin_create_notice,
    admin_update_notice,
    admin_delete_notice,
    admin_get_notice_list,
    admin_get_notice_detail,
    admin_publish_notice,
    admin_withdraw_notice
)
from .views.user_views import (
    user_get_notice_list,
    user_get_notice_detail,
    user_mark_notice_read,
    user_batch_mark_read,
    user_mark_all_read,
    user_toggle_notice_star,
    user_get_notice_statistics
)

urlpatterns = [
    # 管理员通知接口
    path('admin/create/', admin_create_notice, name='admin_create_notice'),
    path('admin/update/<str:notice_id>/', admin_update_notice, name='admin_update_notice'),
    path('admin/delete/<str:notice_id>/', admin_delete_notice, name='admin_delete_notice'),
    path('admin/list/', admin_get_notice_list, name='admin_get_notice_list'),
    path('admin/detail/<str:notice_id>/', admin_get_notice_detail, name='admin_get_notice_detail'),
    path('admin/publish/<str:notice_id>/', admin_publish_notice, name='admin_publish_notice'),
    path('admin/withdraw/<str:notice_id>/', admin_withdraw_notice, name='admin_withdraw_notice'),
    
    # 用户通知接口
    path('user/list/', user_get_notice_list, name='user_get_notice_list'),
    path('user/detail/<str:notice_id>/', user_get_notice_detail, name='user_get_notice_detail'),
    path('user/mark-read/', user_mark_notice_read, name='user_mark_notice_read'),
    path('user/batch-mark-read/', user_batch_mark_read, name='user_batch_mark_read'),
    path('user/mark-all-read/', user_mark_all_read, name='user_mark_all_read'),
    path('user/toggle-star/', user_toggle_notice_star, name='user_toggle_notice_star'),
    path('user/statistics/', user_get_notice_statistics, name='user_get_notice_statistics'),
]