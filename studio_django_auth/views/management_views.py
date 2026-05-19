from studio_django_captcha.serializers import HertzResponseSerializer
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db import transaction
from studio_django_auth.utils.decorators import permission_required
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_utils.log.log_decorator import operation_log
from ..models import HertzUser, HertzRole, HertzMenu, HertzDepartment, HertzUserRole, HertzRoleMenu
from ..serializers import (
    UserManagementSerializer, UserRoleAssignSerializer, RoleManagementSerializer,
    RoleMenuAssignSerializer, MenuManagementSerializer, DepartmentManagementSerializer,
    MenuTreeSerializer, DepartmentTreeSerializer
)


# ==================== 用户管理 ====================

@extend_schema(
    operation_id='user_list',
    summary='获取用户列表',
    description='分页获取系统用户列表，支持按用户名、邮箱、真实姓名等条件筛选',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取用户列表成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['用户管理']
)
@api_view(['GET'])
@permission_required('system:user:list')
def user_list(request):
    """用户列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    username = request.GET.get('username', '')
    email = request.GET.get('email', '')
    real_name = request.GET.get('real_name', '')
    department_id = request.GET.get('department_id', '')
    status_filter = request.GET.get('status', '')
    
    # 构建查询条件
    queryset = HertzUser.objects.all()
    
    if username:
        queryset = queryset.filter(username__icontains=username)
    if email:
        queryset = queryset.filter(email__icontains=email)
    if real_name:
        queryset = queryset.filter(real_name__icontains=real_name)
    if department_id:
        queryset = queryset.filter(department_id=department_id)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    users = queryset.order_by('-created_at')[start:end]
    
    serializer = UserManagementSerializer(users, many=True)
    
    return HertzResponse.success(data={
        'list': serializer.data,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@extend_schema(
    operation_id='user_create',
    summary='创建用户',
    description='创建新的系统用户',
    request=UserManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户创建成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['用户管理']
)
@api_view(['POST'])
@permission_required('system:user:add')
@operation_log(action_type='CREATE', module='用户管理', description='创建用户')
def user_create(request):
    """创建用户"""
    serializer = UserManagementSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    try:
        user = serializer.save()
        return HertzResponse.success(
            message='用户创建成功',
            data=UserManagementSerializer(user).data
        )
    except Exception as e:
        return HertzResponse.error(message=f'用户创建失败: {str(e)}')


@extend_schema(
    operation_id='user_detail',
    summary='获取用户详情',
    description='根据用户ID获取用户详细信息',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取用户详情成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['用户管理']
)
@api_view(['GET'])
@permission_required('system:user:query')
def user_detail(request, user_id):
    """用户详情"""
    try:
        user = HertzUser.objects.get(user_id=user_id)
        serializer = UserManagementSerializer(user)
        return HertzResponse.success(data=serializer.data)
    except HertzUser.DoesNotExist:
        return HertzResponse.error(message='用户不存在')


@extend_schema(
    operation_id='user_update',
    summary='更新用户信息',
    description='根据用户ID更新用户信息',
    request=UserManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['用户管理']
)
@api_view(['PUT'])
@permission_required('system:user:edit')
@operation_log(action_type='UPDATE', module='用户管理', description='更新用户')
def user_update(request, user_id):
    """更新用户"""
    try:
        user = HertzUser.objects.get(user_id=user_id)
        serializer = UserManagementSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        serializer.save()
        return HertzResponse.success(
            message='用户更新成功',
            data=serializer.data
        )
    except HertzUser.DoesNotExist:
        return HertzResponse.error(message='用户不存在')
    except Exception as e:
        return HertzResponse.error(message=f'用户更新失败: {str(e)}')


@extend_schema(
    operation_id='user_delete',
    summary='删除用户',
    description='根据用户ID删除用户（软删除）',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户删除成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='用户不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['用户管理']
)
@api_view(['DELETE'])
@permission_required('system:user:remove')
@operation_log(action_type='DELETE', module='用户管理', description='删除用户')
def user_delete(request, user_id):
    """删除用户"""
    try:
        user = HertzUser.objects.get(user_id=user_id)
        user.status = 0  # 软删除
        user.save(update_fields=['status'])
        return HertzResponse.success(message='用户删除成功')
    except HertzUser.DoesNotExist:
        return HertzResponse.error(message='用户不存在')
    except Exception as e:
        return HertzResponse.error(message=f'用户删除失败: {str(e)}')


@extend_schema(
    operation_id='user_assign_roles',
    summary='分配用户角色',
    description='为指定用户分配角色',
    request=UserRoleAssignSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色分配成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['用户管理']
)

@api_view(['POST'])
@permission_required('system:user:role')
@operation_log(action_type='ASSIGN', module='用户管理', description='分配用户角色')
def user_assign_roles(request):
    """分配用户角色"""
    serializer = UserRoleAssignSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    user_id = serializer.validated_data['user_id']
    role_ids = serializer.validated_data['role_ids']
    
    try:
        with transaction.atomic():
            # 删除用户现有角色
            HertzUserRole.objects.filter(user_id=user_id).delete()
            
            # 分配新角色
            user_roles = []
            for role_id in role_ids:
                user_roles.append(HertzUserRole(user_id=user_id, role_id=role_id))
            HertzUserRole.objects.bulk_create(user_roles)
            
        return HertzResponse.success(message='角色分配成功')
    except Exception as e:
        return HertzResponse.error(message=f'角色分配失败: {str(e)}')


# ==================== 角色管理 ====================

@extend_schema(
    operation_id='role_list',
    summary='获取角色列表',
    description='分页获取系统角色列表，支持按角色名称、角色编码等条件筛选',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取角色列表成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['角色管理']
)
@api_view(['GET'])
@permission_required('system:role:list')
def role_list(request):
    """角色列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    role_name = request.GET.get('role_name', '')
    role_code = request.GET.get('role_code', '')
    status_filter = request.GET.get('status', '')
    
    # 构建查询条件
    queryset = HertzRole.objects.all()
    
    if role_name:
        queryset = queryset.filter(role_name__icontains=role_name)
    if role_code:
        queryset = queryset.filter(role_code__icontains=role_code)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    else:
        # 默认只显示未删除的角色
        queryset = queryset.filter(status=1)
    
    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    roles = queryset.order_by('sort_order', '-created_at')[start:end]
    
    serializer = RoleManagementSerializer(roles, many=True)
    
    return HertzResponse.success(data={
        'list': serializer.data,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@extend_schema(
    operation_id='role_create',
    summary='创建角色',
    description='创建新的系统角色',
    request=RoleManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色创建成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['角色管理']
)
@api_view(['POST'])
@permission_required('system:role:add')
@operation_log(action_type='CREATE', module='角色管理', description='创建角色')
def role_create(request):
    """创建角色"""
    serializer = RoleManagementSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    try:
        role = serializer.save()
        return HertzResponse.success(
            message='角色创建成功',
            data=RoleManagementSerializer(role).data
        )
    except Exception as e:
        return HertzResponse.error(message=f'角色创建失败: {str(e)}')


@extend_schema(
    operation_id='role_detail',
    summary='获取角色详情',
    description='根据角色ID获取角色详细信息',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取角色详情成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['角色管理']
)
@api_view(['GET'])
@permission_required('system:role:query')
def role_detail(request, role_id):
    """角色详情"""
    try:
        role = HertzRole.objects.get(role_id=role_id)
        serializer = RoleManagementSerializer(role)
        return HertzResponse.success(data=serializer.data)
    except HertzRole.DoesNotExist:
        return HertzResponse.error(message='角色不存在')


@extend_schema(
    operation_id='role_update',
    summary='更新角色信息',
    description='根据角色ID更新角色信息',
    request=RoleManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['角色管理']
)
@api_view(['PUT'])
@permission_required('system:role:edit')
@operation_log(action_type='UPDATE', module='角色管理', description='更新角色')
def role_update(request, role_id):
    """更新角色"""
    try:
        role = HertzRole.objects.get(role_id=role_id)
        serializer = RoleManagementSerializer(role, data=request.data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        serializer.save()
        return HertzResponse.success(
            message='角色更新成功',
            data=serializer.data
        )
    except HertzRole.DoesNotExist:
        return HertzResponse.error(message='角色不存在')
    except Exception as e:
        return HertzResponse.error(message=f'角色更新失败: {str(e)}')


@extend_schema(
    operation_id='role_delete',
    summary='删除角色',
    description='根据角色ID删除角色（软删除）',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色删除成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='该角色下还有用户，无法删除'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['角色管理']
)
@api_view(['DELETE'])
@permission_required('system:role:remove')
@operation_log(action_type='DELETE', module='角色管理', description='删除角色')
def role_delete(request, role_id):
    """删除角色"""
    try:
        role = HertzRole.objects.get(role_id=role_id)
        
        # 检查是否有用户使用该角色
        user_count = HertzUser.objects.filter(hertzuserrole__role=role, status=1).count()
        if user_count > 0:
            return HertzResponse.error(message='该角色下还有用户，无法删除')
        
        role.status = 0  # 软删除
        role.save(update_fields=['status'])
        return HertzResponse.success(message='角色删除成功')
    except HertzRole.DoesNotExist:
        return HertzResponse.error(message='角色不存在')
    except Exception as e:
        return HertzResponse.error(message=f'角色删除失败: {str(e)}')


@extend_schema(
    operation_id='role_assign_menus',
    summary='分配角色菜单权限',
    description='为指定角色分配菜单权限',
    request=RoleMenuAssignSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色菜单权限分配成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['角色管理']
)
@api_view(['POST'])
@permission_required('system:role:menu')
@operation_log(action_type='ASSIGN', module='角色管理', description='分配角色菜单权限')
def role_assign_menus(request):
    """分配角色菜单"""
    serializer = RoleMenuAssignSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    role_id = serializer.validated_data['role_id']
    menu_ids = serializer.validated_data['menu_ids']
    
    try:
        with transaction.atomic():
            # 删除角色现有菜单
            HertzRoleMenu.objects.filter(role_id=role_id).delete()
            
            # 分配新菜单
            if menu_ids:
                role_menus = []
                for menu_id in menu_ids:
                    role_menus.append(HertzRoleMenu(role_id=role_id, menu_id=menu_id))
                HertzRoleMenu.objects.bulk_create(role_menus)
            
        return HertzResponse.success(message='菜单分配成功')
    except Exception as e:
        return HertzResponse.error(message=f'菜单分配失败: {str(e)}')


@extend_schema(
    operation_id='role_menus',
    summary='获取角色菜单权限',
    description='获取指定角色的菜单权限列表',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取角色菜单权限成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='角色不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['角色管理']
)
@api_view(['GET'])
@permission_required('system:role:menu')
def role_menus(request, role_id):
    """获取角色菜单"""
    try:
        role = HertzRole.objects.get(role_id=role_id, status=1)
        menu_ids = role.menus.filter(status=1).values_list('menu_id', flat=True)
        return HertzResponse.success(data=list(menu_ids))
    except HertzRole.DoesNotExist:
        return HertzResponse.error(message='角色不存在')


# ==================== 菜单管理 ====================

@extend_schema(
    operation_id='menu_list',
    summary='获取菜单列表',
    description='获取系统菜单树形结构列表，支持按菜单名称、类型等条件筛选',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取菜单列表成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['菜单管理']
)
@api_view(['GET'])
@permission_required('system:menu:list')
def menu_list(request):
    """菜单列表"""
    menu_name = request.GET.get('menu_name', '')
    menu_type = request.GET.get('menu_type', '')
    status_filter = request.GET.get('status', '')
    
    # 构建查询条件
    queryset = HertzMenu.objects.all()
    
    if menu_name:
        queryset = queryset.filter(menu_name__icontains=menu_name)
    if menu_type:
        queryset = queryset.filter(menu_type=menu_type)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # 获取顶级菜单
    top_menus = queryset.filter(parent_id__isnull=True).order_by('sort_order')
    serializer = MenuManagementSerializer(top_menus, many=True)
    
    return HertzResponse.success(data=serializer.data)


@extend_schema(
    operation_id='menu_tree',
    summary='获取菜单树',
    description='获取系统菜单树形结构，用于权限分配等场景',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取菜单树成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['菜单管理']
)
@api_view(['GET'])
@permission_required('system:menu:list')
def menu_tree(request):
    """菜单树"""
    menus = HertzMenu.objects.filter(status=1, parent_id__isnull=True).order_by('sort_order')
    serializer = MenuTreeSerializer(menus, many=True)
    return HertzResponse.success(data=serializer.data)


@extend_schema(
    operation_id='menu_create',
    summary='创建菜单',
    description='创建新的系统菜单',
    request=MenuManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='菜单创建成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['菜单管理']
)
@api_view(['POST'])
@permission_required('system:menu:add')
@operation_log(action_type='CREATE', module='菜单管理', description='创建菜单')
def menu_create(request):
    """创建菜单"""
    serializer = MenuManagementSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    try:
        menu = serializer.save()
        return HertzResponse.success(
            message='菜单创建成功',
            data=MenuManagementSerializer(menu).data
        )
    except Exception as e:
        return HertzResponse.error(message=f'菜单创建失败: {str(e)}')


@extend_schema(
    operation_id='menu_detail',
    summary='获取菜单详情',
    description='根据菜单ID获取菜单详细信息',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取菜单详情成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='菜单不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['菜单管理']
)
@api_view(['GET'])
@permission_required('system:menu:query')
def menu_detail(request, menu_id):
    """菜单详情"""
    try:
        menu = HertzMenu.objects.get(menu_id=menu_id)
        serializer = MenuManagementSerializer(menu)
        return HertzResponse.success(data=serializer.data)
    except HertzMenu.DoesNotExist:
        return HertzResponse.error(message='菜单不存在')


@extend_schema(
    operation_id='menu_update',
    summary='更新菜单信息',
    description='根据菜单ID更新菜单信息',
    request=MenuManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='菜单更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='菜单不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['菜单管理']
)
@api_view(['PUT'])
@permission_required('system:menu:edit')
@operation_log(action_type='UPDATE', module='菜单管理', description='更新菜单')
def menu_update(request, menu_id):
    """更新菜单"""
    try:
        menu = HertzMenu.objects.get(menu_id=menu_id)
        serializer = MenuManagementSerializer(menu, data=request.data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        serializer.save()
        return HertzResponse.success(
            message='菜单更新成功',
            data=serializer.data
        )
    except HertzMenu.DoesNotExist:
        return HertzResponse.error(message='菜单不存在')
    except Exception as e:
        return HertzResponse.error(message=f'菜单更新失败: {str(e)}')


@extend_schema(
    operation_id='menu_delete',
    summary='删除菜单',
    description='根据菜单ID删除菜单（软删除）',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='菜单删除成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='该菜单下还有子菜单，无法删除'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='菜单不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['菜单管理']
)
@api_view(['DELETE'])
@permission_required('system:menu:remove')
@operation_log(action_type='DELETE', module='菜单管理', description='删除菜单')
def menu_delete(request, menu_id):
    """删除菜单"""
    try:
        menu = HertzMenu.objects.get(menu_id=menu_id)
        
        # 检查是否有子菜单
        if HertzMenu.objects.filter(parent_id=menu.menu_id, status=1).exists():
            return HertzResponse.error(message='该菜单下还有子菜单，无法删除')
        
        menu.status = 0  # 软删除
        menu.save(update_fields=['status'])
        return HertzResponse.success(message='菜单删除成功')
    except HertzMenu.DoesNotExist:
        return HertzResponse.error(message='菜单不存在')
    except Exception as e:
        return HertzResponse.error(message=f'菜单删除失败: {str(e)}')


# ==================== 部门管理 ====================

@extend_schema(
    operation_id='department_list',
    summary='获取部门列表',
    description='获取系统部门树形结构列表，支持按部门名称等条件筛选',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取部门列表成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['部门管理']
)
@api_view(['GET'])
@permission_required('system:dept:list')
def department_list(request):
    """部门列表"""
    dept_name = request.GET.get('dept_name', '')
    status_filter = request.GET.get('status', '')
    
    # 构建查询条件
    queryset = HertzDepartment.objects.all()
    
    if dept_name:
        queryset = queryset.filter(dept_name__icontains=dept_name)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # 获取顶级部门
    top_departments = queryset.filter(parent_id__isnull=True).order_by('sort_order')
    serializer = DepartmentManagementSerializer(top_departments, many=True)
    
    return HertzResponse.success(data=serializer.data)


@extend_schema(
    operation_id='department_tree',
    summary='获取部门树',
    description='获取系统部门树形结构，用于部门选择等场景',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取部门树成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['部门管理']
)
@api_view(['GET'])
@permission_required('system:dept:list')
def department_tree(request):
    """部门树"""
    departments = HertzDepartment.objects.filter(status=1, parent_id__isnull=True).order_by('sort_order')
    serializer = DepartmentTreeSerializer(departments, many=True)
    return HertzResponse.success(data=serializer.data)


@extend_schema(
    operation_id='department_create',
    summary='创建部门',
    description='创建新的系统部门',
    request=DepartmentManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='部门创建成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['部门管理']
)
@api_view(['POST'])
@permission_required('system:dept:add')
@operation_log(action_type='CREATE', module='部门管理', description='创建部门')
def department_create(request):
    """创建部门"""
    serializer = DepartmentManagementSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    try:
        department = serializer.save()
        return HertzResponse.success(
            message='部门创建成功',
            data=DepartmentManagementSerializer(department).data
        )
    except Exception as e:
        return HertzResponse.error(message=f'部门创建失败: {str(e)}')


@extend_schema(
    operation_id='department_detail',
    summary='获取部门详情',
    description='根据部门ID获取部门详细信息',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取部门详情成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='部门不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['部门管理']
)
@api_view(['GET'])
@permission_required('system:dept:query')
def department_detail(request, dept_id):
    """部门详情"""
    try:
        department = HertzDepartment.objects.get(dept_id=dept_id)
        serializer = DepartmentManagementSerializer(department)
        return HertzResponse.success(data=serializer.data)
    except HertzDepartment.DoesNotExist:
        return HertzResponse.error(message='部门不存在')


@extend_schema(
    operation_id='department_update',
    summary='更新部门信息',
    description='根据部门ID更新部门信息',
    request=DepartmentManagementSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='部门更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='部门不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['部门管理']
)
@api_view(['PUT'])
@permission_required('system:dept:edit')
@operation_log(action_type='UPDATE', module='部门管理', description='更新部门')
def department_update(request, dept_id):
    """更新部门"""
    try:
        department = HertzDepartment.objects.get(dept_id=dept_id)
        serializer = DepartmentManagementSerializer(department, data=request.data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        serializer.save()
        return HertzResponse.success(
            message='部门更新成功',
            data=serializer.data
        )
    except HertzDepartment.DoesNotExist:
        return HertzResponse.error(message='部门不存在')
    except Exception as e:
        return HertzResponse.error(message=f'部门更新失败: {str(e)}')


@extend_schema(
    operation_id='department_delete',
    summary='删除部门',
    description='根据部门ID删除部门（软删除）',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='部门删除成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='该部门下还有子部门或用户，无法删除'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='部门不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        )
    },
    tags=['部门管理']
)
@api_view(['DELETE'])
@permission_required('system:dept:remove')
@operation_log(action_type='DELETE', module='部门管理', description='删除部门')
def department_delete(request, dept_id):
    """删除部门"""
    try:
        department = HertzDepartment.objects.get(dept_id=dept_id)
        
        # 检查是否有子部门
        if HertzDepartment.objects.filter(parent_id=department.dept_id, status=1).exists():
            return HertzResponse.error(message='该部门下还有子部门，无法删除')
        
        # 检查是否有用户
        if HertzUser.objects.filter(department_id=department.dept_id, status=1).exists():
            return HertzResponse.error(message='该部门下还有用户，无法删除')
        
        department.status = 0  # 软删除
        department.save(update_fields=['status'])
        return HertzResponse.success(message='部门删除成功')
    except HertzDepartment.DoesNotExist:
        return HertzResponse.error(message='部门不存在')
    except Exception as e:
        return HertzResponse.error(message=f'部门删除失败: {str(e)}')