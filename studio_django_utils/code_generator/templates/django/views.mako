"""
Django视图模板
"""
<%!
from datetime import datetime
%>
<%
# 生成操作列表
operations_list = operations or ['create', 'get', 'update', 'delete', 'list']
permissions_list = permissions or []
snake_model_name = model_name.lower()
%>
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core.paginator import Paginator
from django.db.models import Q

from .models import ${model_name}
from .serializers import (
    ${model_name}Serializer,
    ${model_name}CreateSerializer,
    ${model_name}UpdateSerializer,
    ${model_name}ListSerializer
)
from studio_django_utils.responses import HertzResponse
% if permissions_list:
from studio_django_auth.utils.decorators import login_required, permission_required
% endif


% if 'create' in operations_list:
@extend_schema(
    operation_id='create_${snake_model_name}',
    summary='创建${model_name}',
    description='创建新的${model_name}实例',
    request=${model_name}CreateSerializer,
    responses={
        201: OpenApiResponse(response=${model_name}Serializer, description='创建成功'),
        400: OpenApiResponse(description='参数错误'),
    },
    tags=['${model_name}']
)
@api_view(['POST'])
% if 'create' in permissions_list:
<%
    # 获取权限代码，如果permissions_list是字典，则获取对应的权限代码
    if isinstance(permissions_list, dict) and 'create' in permissions_list:
        permission_code = permissions_list['create']
    else:
        permission_code = f'{snake_model_name}:create'
%>
@permission_required('${permission_code}')
% endif
def create_${snake_model_name}(request):
    """
    创建${model_name}
    
    创建时间: ${datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    try:
        serializer = ${model_name}CreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            response_serializer = ${model_name}Serializer(instance)
            return HertzResponse.success(
                data=response_serializer.data,
                message='${model_name}创建成功'
            )
        return HertzResponse.validation_error(
            message='参数验证失败',
            errors=serializer.errors
        )
    except Exception as e:
        return HertzResponse.error(
            message='创建${model_name}失败',
            error=str(e)
        )


% endif
% if 'get' in operations_list or 'retrieve' in operations_list:
@extend_schema(
    operation_id='get_${snake_model_name}',
    summary='获取${model_name}详情',
    description='根据ID获取${model_name}详情',
    responses={
        200: OpenApiResponse(response=${model_name}Serializer, description='获取成功'),
        404: OpenApiResponse(description='${model_name}不存在'),
    },
    tags=['${model_name}']
)
@api_view(['GET'])
% if 'get' in permissions_list or 'retrieve' in permissions_list:
<%
    # 获取权限代码
    if isinstance(permissions_list, dict):
        permission_code = permissions_list.get('get') or permissions_list.get('retrieve') or f'{snake_model_name}:query'
    else:
        permission_code = f'{snake_model_name}:query'
%>
@permission_required('${permission_code}')
% endif
def get_${snake_model_name}(request, ${snake_model_name}_id):
    """
    获取${model_name}详情
    
    Args:
        ${snake_model_name}_id: ${model_name}ID
    """
    try:
        instance = ${model_name}.get_by_id(${snake_model_name}_id)
        if not instance:
            return HertzResponse.not_found(message='${model_name}不存在')
            
        serializer = ${model_name}Serializer(instance)
        return HertzResponse.success(
            data=serializer.data,
            message='获取${model_name}详情成功'
        )
    except Exception as e:
        return HertzResponse.error(
            message='获取${model_name}详情失败',
            error=str(e)
        )


% endif
% if 'update' in operations_list:
@extend_schema(
    operation_id='update_${snake_model_name}',
    summary='更新${model_name}',
    description='根据ID更新${model_name}信息',
    request=${model_name}UpdateSerializer,
    responses={
        200: OpenApiResponse(response=${model_name}Serializer, description='更新成功'),
        404: OpenApiResponse(description='${model_name}不存在'),
        400: OpenApiResponse(description='参数错误'),
    },
    tags=['${model_name}']
)
@api_view(['PUT', 'PATCH'])
% if 'update' in permissions_list:
<%
    # 获取权限代码
    if isinstance(permissions_list, dict) and 'update' in permissions_list:
        permission_code = permissions_list['update']
    else:
        permission_code = f'{snake_model_name}:update'
%>
@permission_required('${permission_code}')
% endif
def update_${snake_model_name}(request, ${snake_model_name}_id):
    """
    更新${model_name}
    
    Args:
        ${snake_model_name}_id: ${model_name}ID
    """
    try:
        instance = ${model_name}.get_by_id(${snake_model_name}_id)
        if not instance:
            return HertzResponse.not_found(message='${model_name}不存在')
            
        partial = request.method == 'PATCH'
        serializer = ${model_name}UpdateSerializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        
        if serializer.is_valid():
            updated_instance = serializer.save()
            response_serializer = ${model_name}Serializer(updated_instance)
            return HertzResponse.success(
                data=response_serializer.data,
                message='${model_name}更新成功'
            )
        return HertzResponse.validation_error(
            message='参数验证失败',
            errors=serializer.errors
        )
    except Exception as e:
        return HertzResponse.error(
            message='更新${model_name}失败',
            error=str(e)
        )


% endif
% if 'delete' in operations_list:
@extend_schema(
    operation_id='delete_${snake_model_name}',
    summary='删除${model_name}',
    description='根据ID删除${model_name}',
    responses={
        200: OpenApiResponse(description='删除成功'),
        404: OpenApiResponse(description='${model_name}不存在'),
    },
    tags=['${model_name}']
)
@api_view(['DELETE'])
% if 'delete' in permissions_list:
<%
    # 获取权限代码
    if isinstance(permissions_list, dict) and 'delete' in permissions_list:
        permission_code = permissions_list['delete']
    else:
        permission_code = f'{snake_model_name}:delete'
%>
@permission_required('${permission_code}')
% endif
def delete_${snake_model_name}(request, ${snake_model_name}_id):
    """
    删除${model_name}
    
    Args:
        ${snake_model_name}_id: ${model_name}ID
    """
    try:
        instance = ${model_name}.get_by_id(${snake_model_name}_id)
        if not instance:
            return HertzResponse.not_found(message='${model_name}不存在')
            
        instance.delete()
        return HertzResponse.success(message='${model_name}删除成功')
    except Exception as e:
        return HertzResponse.error(
            message='删除${model_name}失败',
            error=str(e)
        )


% endif
% if 'list' in operations_list:
@extend_schema(
    operation_id='list_${snake_model_name}',
    summary='获取${model_name}列表',
    description='分页获取${model_name}列表',
    responses={
        200: OpenApiResponse(response=${model_name}ListSerializer, description='获取成功'),
    },
    tags=['${model_name}']
)
@api_view(['GET'])
% if 'list' in permissions_list:
<%
    # 获取权限代码
    if isinstance(permissions_list, dict) and 'list' in permissions_list:
        permission_code = permissions_list['list']
    else:
        permission_code = f'{snake_model_name}:list'
%>
@permission_required('${permission_code}')
% endif
def list_${snake_model_name}(request):
    """
    获取${model_name}列表
    
    支持分页、搜索和排序
    """
    try:
        queryset = ${model_name}.objects.all()
        
        # 搜索功能
        search = request.GET.get('search', '')
        if search:
            % if search_fields:
            search_q = Q()
            % for field in search_fields:
            search_q |= Q(${field}__icontains=search)
            % endfor
            queryset = queryset.filter(search_q)
            % else:
            # 默认搜索字段，可根据需要调整
            queryset = queryset.filter(
                Q(id__icontains=search)
            )
            % endif
        
        # 排序功能
        ordering = request.GET.get('ordering', '-created_at')
        % if ordering:
        valid_orderings = [${', '.join([f"'{field}'" for field in ordering] + [f"'-{field}'" for field in ordering])}]
        % else:
        valid_orderings = ['created_at', '-created_at', 'updated_at', '-updated_at']
        % endif
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        
        # 分页功能
        % if pagination:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = ${model_name}ListSerializer(page_obj.object_list, many=True)
        
        return HertzResponse.success(
            data={
                'results': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                }
            },
            message='获取${model_name}列表成功'
        )
        % else:
        serializer = ${model_name}ListSerializer(queryset, many=True)
        return HertzResponse.success(
            data=serializer.data,
            message='获取${model_name}列表成功'
        )
        % endif
    except Exception as e:
        return HertzResponse.error(
            message='获取${model_name}列表失败',
            error=str(e)
        )


% endif