# 序列化器模块
from .auth_serializers import (
    UserLoginSerializer,
    UserRegisterSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    UserInfoSerializer,
    UpdateUserInfoSerializer,
    SendEmailCodeSerializer,
    RefreshTokenSerializer
)
from .management_serializers import (
    UserManagementSerializer,
    UserRoleAssignSerializer,
    RoleManagementSerializer,
    RoleMenuAssignSerializer,
    MenuManagementSerializer,
    DepartmentManagementSerializer,
    MenuTreeSerializer,
    DepartmentTreeSerializer
)

__all__ = [
    # 认证相关序列化器
    'UserLoginSerializer',
    'UserRegisterSerializer',
    'ChangePasswordSerializer',
    'ResetPasswordSerializer',
    'UserInfoSerializer',
    'UpdateUserInfoSerializer',
    # 管理相关序列化器
    'UserManagementSerializer',
    'UserRoleAssignSerializer',
    'RoleManagementSerializer',
    'RoleMenuAssignSerializer',
    'MenuManagementSerializer',
    'DepartmentManagementSerializer',
    'MenuTreeSerializer',
    'DepartmentTreeSerializer',
]