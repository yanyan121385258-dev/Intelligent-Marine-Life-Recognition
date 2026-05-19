from django.urls import path
from ..views.management_views import (
    # 用户管理
    user_list, user_create, user_detail, user_update, user_delete, user_assign_roles,
    # 角色管理
    role_list, role_create, role_detail, role_update, role_delete, role_assign_menus, role_menus,
    # 菜单管理
    menu_list, menu_tree, menu_create, menu_detail, menu_update, menu_delete,
    # 部门管理
    department_list, department_tree, department_create, department_detail, department_update, department_delete
)

urlpatterns = [
    # ==================== 用户管理 ====================
    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/assign-roles/', user_assign_roles, name='user_assign_roles'),
    path('users/<str:user_id>/', user_detail, name='user_detail'),
    path('users/<str:user_id>/update/', user_update, name='user_update'),
    path('users/<str:user_id>/delete/', user_delete, name='user_delete'),

    
    # ==================== 角色管理 ====================
    path('roles/', role_list, name='role_list'),
    path('roles/create/', role_create, name='role_create'),
    path('roles/assign-menus/', role_assign_menus, name='role_assign_menus'),
    path('roles/<str:role_id>/', role_detail, name='role_detail'),
    path('roles/<str:role_id>/update/', role_update, name='role_update'),
    path('roles/<str:role_id>/delete/', role_delete, name='role_delete'),
    path('roles/<str:role_id>/menus/', role_menus, name='role_menus'),
    
    # ==================== 菜单管理 ====================
    path('menus/', menu_list, name='menu_list'),
    path('menus/tree/', menu_tree, name='menu_tree'),
    path('menus/create/', menu_create, name='menu_create'),
    path('menus/<str:menu_id>/', menu_detail, name='menu_detail'),
    path('menus/<str:menu_id>/update/', menu_update, name='menu_update'),
    path('menus/<str:menu_id>/delete/', menu_delete, name='menu_delete'),
    
    # ==================== 部门管理 ====================
    path('departments/', department_list, name='department_list'),
    path('departments/tree/', department_tree, name='department_tree'),
    path('departments/create/', department_create, name='department_create'),
    path('departments/<str:dept_id>/', department_detail, name='department_detail'),
    path('departments/<str:dept_id>/update/', department_update, name='department_update'),
    path('departments/<str:dept_id>/delete/', department_delete, name='department_delete'),
]