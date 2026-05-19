from studio_django_captcha.serializers import HertzResponseSerializer

from ..serializers import (
    UserLoginSerializer, UserRegisterSerializer, ChangePasswordSerializer,
    ResetPasswordSerializer, UserInfoSerializer, UpdateUserInfoSerializer,
    SendEmailCodeSerializer, RefreshTokenSerializer
)
from ..models import HertzUser, HertzMenu
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_captcha import HertzCaptchaGenerator
from studio_django_utils.email import EmailService
from studio_django_utils.validators import EmailValidator
from django.conf import settings
from studio_django_auth.utils.auth import TokenUtils
from studio_django_auth.utils.decorators import login_required, no_login_required
from studio_django_utils.log.log_decorator import operation_log
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
import os
import uuid


@extend_schema(
    operation_id='user_login',
    summary='用户登录',
    description='用户通过用户名/邮箱/手机号和密码登录系统',
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='登录成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户名或密码错误'
        )
    },
    tags=['用户认证']
)
@api_view(['POST'])
@no_login_required
@operation_log(action_type='LOGIN', module='认证', description='用户登录')
def user_login(request):
    """用户登录"""
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    user = serializer.validated_data['user']
    
    # 更新登录信息
    user.last_login_time = timezone.now()
    user.last_login_ip = request.META.get('REMOTE_ADDR', '')
    user.save(update_fields=['last_login_time', 'last_login_ip'])
    
    # 获取用户角色和权限
    roles = user.roles.filter(status=1)
    permissions = []
    role_codes = []
    for role in roles:
        role_codes.append(role.role_code)
        role_permissions = role.menus.filter(
            status=1, 
            menu_type__in=[2, 3]
        ).exclude(
            permission__isnull=True
        ).exclude(
            permission=''
        ).values_list('permission', flat=True)
        permissions.extend(role_permissions)
    
    # 生成JWT token（包含权限信息）
    token_data = {
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'roles': role_codes,
        'permissions': list(set(permissions))  # 去重
    }
    access_token = TokenUtils.generate_token(token_data)
    refresh_token = TokenUtils.generate_refresh_token(token_data)
    
    user_info = {
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'real_name': user.real_name,
        'avatar': user.avatar,
        'roles': [{'role_id': role.role_id, 'role_name': role.role_name, 'role_code': role.role_code} for role in roles],
        'permissions': list(set(permissions))
    }
    
    return HertzResponse.success(
        message='登录成功',
        data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_info': user_info
        }
    )


@extend_schema(
    operation_id='user_register',
    summary='用户注册',
    description='用户注册新账户，需要提供用户名、邮箱、密码等信息',
    request=UserRegisterSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='注册成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        409: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户名或邮箱已存在'
        )
    },
    tags=['用户认证']
)
@api_view(['POST'])
@no_login_required
@operation_log(action_type='REGISTER', module='认证', description='用户注册')
def user_register(request):
    """用户注册"""
    serializer = UserRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    # 根据开关验证邮箱验证码
    require_verification = getattr(settings, 'REGISTER_EMAIL_VERIFICATION', 0) == 1
    email = serializer.validated_data['email']
    if require_verification:
        email_code = serializer.validated_data.get('email_code')
        if not email_code:
            return HertzResponse.error(message='邮箱验证码不能为空')
        cache_key = f'email_code_{email}_register'
        cached_code = cache.get(cache_key)
        if not cached_code or cached_code != email_code:
            return HertzResponse.error(message='邮箱验证码错误或已过期')
    
    try:
        with transaction.atomic():
            user = serializer.save()
            # 删除验证码缓存
            if require_verification:
                cache.delete(cache_key)
            
        return HertzResponse.success(
            message='注册成功',
            data={'user_id': user.user_id, 'username': user.username}
        )
    except Exception as e:
        return HertzResponse.error(message=f'注册失败: {str(e)}')


@extend_schema(
    operation_id='user_logout',
    summary='用户登出',
    description='用户登出系统，清除登录状态',
    request=None,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='登出成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户认证']
)
@api_view(['POST'])
@login_required
@operation_log(action_type='LOGOUT', module='认证', description='用户登出')
def user_logout(request):
    """用户登出"""
    # 这里可以将token加入黑名单，暂时简单返回成功
    return HertzResponse.success(message='登出成功')


@extend_schema(
    operation_id='change_password',
    summary='修改密码',
    description='用户修改登录密码，需要提供旧密码和新密码',
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='密码修改成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败或旧密码错误'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户认证']
)
@api_view(['POST'])
@login_required
@operation_log(action_type='UPDATE', module='认证', description='修改密码')
def change_password(request):
    """修改密码"""
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    user = request.user
    old_password = serializer.validated_data['old_password']
    new_password = serializer.validated_data['new_password']
    
    # 验证原密码
    if not user.check_password(old_password):
        return HertzResponse.error(message='原密码错误')
    
    # 更新密码
    user.set_password(new_password)
    user.save()
    
    return HertzResponse.success(message='密码修改成功')


@extend_schema(
    operation_id='reset_password',
    summary='重置密码',
    description='通过邮箱验证码重置用户密码',
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='密码重置成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败或验证码错误'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户不存在'
        )
    },
    tags=['用户认证']
)
@api_view(['POST'])
@no_login_required
@operation_log(action_type='RESET', module='认证', description='重置密码')
def reset_password(request):
    """重置密码"""
    serializer = ResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    email = serializer.validated_data['email']
    email_code = serializer.validated_data['email_code']
    new_password = serializer.validated_data['new_password']
    
    # 验证邮箱验证码
    cache_key = f'email_code_{email}_reset_password'
    cached_code = cache.get(cache_key)
    
    if not cached_code or cached_code != email_code:
        return HertzResponse.error(message='邮箱验证码错误或已过期')
    
    try:
        user = HertzUser.objects.get(email=email, status=1)
        user.set_password(new_password)
        user.save()
        
        # 删除验证码缓存
        cache.delete(cache_key)
        
        return HertzResponse.success(message='密码重置成功')
    except HertzUser.DoesNotExist:
        return HertzResponse.error(message='用户不存在')
    except Exception as e:
        return HertzResponse.error(message=f'密码重置失败: {str(e)}')


@extend_schema(
    operation_id='get_user_info',
    summary='获取用户信息',
    description='获取当前登录用户的详细信息',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取用户信息成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户管理']
)
@api_view(['GET'])
@login_required
def get_user_info(request):
    """获取用户信息"""
    serializer = UserInfoSerializer(request.user)
    return HertzResponse.success(data=serializer.data)


@extend_schema(
    operation_id='update_user_info',
    summary='更新用户信息',
    description='更新当前登录用户的个人信息',
    request=UpdateUserInfoSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户信息更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户管理']
)
@api_view(['PUT'])
@login_required
@operation_log(action_type='UPDATE', module='用户管理', description='更新用户信息')
def update_user_info(request):
    """更新用户信息"""
    serializer = UpdateUserInfoSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    serializer.save()
    return HertzResponse.success(message='用户信息更新成功', data=serializer.data)


@extend_schema(
    operation_id='get_user_menus',
    summary='获取用户菜单',
    description='获取当前登录用户有权限访问的菜单列表',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取用户菜单成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户管理']
)
@api_view(['GET'])
@login_required
def get_user_menus(request):
    """获取用户菜单"""
    user = request.user
    
    # 获取用户所有角色的菜单
    user_roles = user.roles.filter(status=1)
    menu_ids = []
    for role in user_roles:
        role_menu_ids = role.menus.filter(status=1).values_list('menu_id', flat=True)
        menu_ids.extend(role_menu_ids)
    
    # 去重并获取菜单
    menu_ids = list(set(menu_ids))
    menus = HertzMenu.objects.filter(
        menu_id__in=menu_ids,
        status=1,
        is_visible=True
    ).order_by('sort_order')
    
    # 构建菜单树
    def build_menu_tree(menus, parent_id=None):
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = build_menu_tree(menus, menu.menu_id)
                menu_data = {
                    'menu_id': menu.menu_id,
                    'menu_name': menu.menu_name,
                    'menu_code': menu.menu_code,
                    'menu_type': menu.menu_type,
                    'path': menu.path,
                    'component': menu.component,
                    'icon': menu.icon,
                    'permission': menu.permission,
                    'is_external': menu.is_external,
                    'is_cache': menu.is_cache,
                    'sort_order': menu.sort_order,
                    'children': children
                }
                tree.append(menu_data)
        return tree
    
    menu_tree = build_menu_tree(menus)
    return HertzResponse.success(data=menu_tree)


@extend_schema(
    operation_id='upload_avatar',
    summary='上传用户头像',
    description='上传当前登录用户的头像图片，文件将保存到 media/auth/avatar，并更新用户头像URL',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='头像上传成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户管理']
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@login_required
@operation_log(action_type='UPDATE', module='用户管理', description='上传头像')
def upload_avatar(request):
    f = request.FILES.get('file') or request.FILES.get('avatar')
    if not f:
        return HertzResponse.validation_error(message='请上传头像文件，字段名为 file 或 avatar')

    name = f.name.lower()
    exts = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif']
    if not any(name.endswith(e) for e in exts):
        return HertzResponse.validation_error(message='仅支持图片格式：jpg/jpeg/png/bmp/webp/gif')

    rel_dir = os.path.join('auth', 'avatar')
    os.makedirs(os.path.join(settings.MEDIA_ROOT, rel_dir), exist_ok=True)
    ext = os.path.splitext(name)[1]
    filename = f"u{request.user.user_id}_{uuid.uuid4().hex}{ext}"
    rel_path = os.path.join(rel_dir, filename)
    saved_path = default_storage.save(rel_path, f)

    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    relative_url = (media_url.rstrip('/') + '/' + saved_path).replace('\\', '/')

    try:
        request.user.avatar = relative_url
        request.user.save(update_fields=['avatar'])
    except Exception as e:
        return HertzResponse.error(message=f'头像更新失败: {str(e)}')

    return HertzResponse.success(data={'avatar_url': relative_url}, message='头像上传成功')


@extend_schema(
    operation_id='send_email_code',
    summary='发送邮箱验证码',
    description='向指定邮箱发送验证码，用于注册、重置密码等操作',
    request=SendEmailCodeSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='验证码发送成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        429: OpenApiResponse(
            response=HertzResponseSerializer,
            description='发送频率过快，请稍后再试'
        ),
        500: OpenApiResponse(
            response=HertzResponseSerializer,
            description='邮件发送失败'
        )
    },
    tags=['邮箱服务']
)
@api_view(['POST'])
@no_login_required
def send_email_code(request):
    """
    发送邮箱验证码
    """
    serializer = SendEmailCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(
            message="参数验证失败",
            errors=serializer.errors,
            code=status.HTTP_400_BAD_REQUEST
        )
    
    email = serializer.validated_data['email']
    code_type = serializer.validated_data['code_type']
    
    # 验证邮箱格式
    if not EmailValidator.is_valid_email(email):
        return HertzResponse.error(
            message="邮箱格式不正确",
            code=status.HTTP_400_BAD_REQUEST
        )
    
    # 检查发送频率限制（60秒内只能发送一次）
    cache_key = f"email_code_limit_{email}"
    if cache.get(cache_key):
        return HertzResponse.error(
            message="发送过于频繁，请60秒后再试",
            code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # 生成6位数字验证码
    verification_code = HertzCaptchaGenerator.generate_numeric_code(6)
    
    # 将验证码存储到缓存中，有效期5分钟
    code_cache_key = f"email_code_{email}_{code_type}"
    cache.set(code_cache_key, verification_code, 300)  # 5分钟
    
    # 设置发送频率限制
    cache.set(cache_key, True, 60)  # 60秒
    
    # 发送邮件验证码
    try:
        # 获取用户名（如果用户已存在）
        recipient_name = '用户'
        try:
            user = HertzUser.objects.get(email=email)
            recipient_name = user.username or user.email.split('@')[0]
        except HertzUser.DoesNotExist:
            recipient_name = email.split('@')[0]
        
        # 发送邮件
        email_sent = EmailService.send_verification_code(
            recipient_email=email,
            recipient_name=recipient_name,
            verification_code=verification_code,
            code_type=code_type
        )
        
        if not email_sent:
            return HertzResponse.error(
                message="邮件发送失败，请稍后重试",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return HertzResponse.success(
            message="验证码发送成功，请查收邮件",
            data={
                "email": email,
                "code_type": code_type,
                "expires_in": 300  # 5分钟有效期
            }
        )
        
    except Exception as e:
        return HertzResponse.error(
            message=f"发送失败：{str(e)}",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id='refresh_token',
    summary='刷新访问令牌',
    description='使用刷新令牌获取新的访问令牌',
    request=RefreshTokenSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='令牌刷新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='刷新令牌无效或已过期'
        )
    },
    tags=['用户认证']
)
@api_view(['POST'])
@login_required
@operation_log(action_type='REFRESH', module='认证', description='刷新访问令牌')
def refresh_token(request):
    """刷新token"""
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return HertzResponse.error(message='refresh_token不能为空')
    
    try:
        # 验证refresh_token
        payload = TokenUtils.verify_token(refresh_token)
        user_id = payload.get('user_id')
        
        # 获取用户信息
        user = HertzUser.objects.get(user_id=user_id, status=1)
        
        # 获取用户角色和权限
        user_roles = user.roles.all()
        roles = [role.role_name for role in user_roles]
        
        # 获取所有权限（去重）
        permissions = set()
        for role in user_roles:
            role_permissions = role.permissions.all()
            for perm in role_permissions:
                permissions.add(perm.permission_code)
        
        # 生成新的access_token
        token_data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'roles': roles,
            'permissions': list(permissions)
        }
        new_access_token = TokenUtils.generate_token(token_data)
        
        return HertzResponse.success(
            message='token刷新成功',
            data={'access_token': new_access_token}
        )
    except Exception as e:
        return HertzResponse.error(message='token刷新失败', error=str(e))
