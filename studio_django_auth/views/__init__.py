# 视图模块
from .auth_views import (
    user_login, user_register, user_logout, change_password, reset_password,
    get_user_info, update_user_info, get_user_menus, send_email_code, refresh_token
)
from .management_views import (
    # 用户管理
    user_list, user_create, user_detail, user_update, user_delete, user_assign_roles,
    # 角色管理
    role_list, role_create, role_detail, role_update, role_delete, role_assign_menus, role_menus,
    # 菜单管理
    menu_list, menu_tree, menu_create, menu_detail, menu_update, menu_delete,
    # 部门管理
    department_list, department_tree, department_create, department_detail, department_update, department_delete
)

__all__ = [
    # 认证相关
    'user_login', 'user_register', 'user_logout', 'change_password', 'reset_password',
    'get_user_info', 'update_user_info', 'get_user_menus', 'send_email_code', 'refresh_token',
    # 用户管理
    'user_list', 'user_create', 'user_detail', 'user_update', 'user_delete', 'user_assign_roles',
    # 角色管理
    'role_list', 'role_create', 'role_detail', 'role_update', 'role_delete', 'role_assign_menus', 'role_menus',
    # 菜单管理
    'menu_list', 'menu_tree', 'menu_create', 'menu_detail', 'menu_update', 'menu_delete',
    # 部门管理
    'department_list', 'department_tree', 'department_create', 'department_detail', 'department_update', 'department_delete'
]