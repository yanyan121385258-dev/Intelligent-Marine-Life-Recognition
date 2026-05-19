from django.db.models import Q
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_auth.utils.decorators import login_required, permission_required
from ..models import OperationLog
from ..serializers import (
    OperationLogSerializer,
    OperationLogListSerializer,
    OperationLogFilterSerializer
)
from studio_django_captcha.serializers import HertzResponseSerializer
from studio_django_auth.utils.decorators import login_required

@api_view(['GET'])
@permission_required('system:log:list')
@extend_schema(
    operation_id='operation_log_list',
    summary='获取操作日志列表',
    description='获取系统操作日志列表，支持多种过滤条件，仅管理员可访问',
    parameters=[
        OpenApiParameter(
            name='user_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='用户ID',
            required=False
        ),
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='用户名',
            required=False
        ),
        OpenApiParameter(
            name='action_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='操作类型',
            required=False
        ),
        OpenApiParameter(
            name='module',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='操作模块',
            required=False
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='操作状态',
            required=False
        ),
        OpenApiParameter(
            name='ip_address',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='IP地址',
            required=False
        ),
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            description='开始时间',
            required=False
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            description='结束时间',
            required=False
        ),
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='页码',
            required=False,
            default=1
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='每页数量',
            required=False,
            default=20
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数错误'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        ),
    },
    tags=['日志管理']
)
def operation_log_list(request):
    """
    获取操作日志列表
    
    支持多种过滤条件：
    - user_id: 用户ID
    - username: 用户名（模糊匹配）
    - action_type: 操作类型
    - module: 操作模块（模糊匹配）
    - status: 操作状态
    - ip_address: IP地址
    - start_date: 开始时间
    - end_date: 结束时间
    - page: 页码
    - page_size: 每页数量
    """
    try:
        # 验证查询参数
        filter_serializer = OperationLogFilterSerializer(data=request.GET)
        if not filter_serializer.is_valid():
            return HertzResponse.validation_error(
                message='查询参数错误',
                errors=filter_serializer.errors
            )
        
        validated_data = filter_serializer.validated_data
        
        # 构建查询条件
        queryset = OperationLog.objects.select_related('user').all()
        
        # 用户ID过滤
        if validated_data.get('user_id'):
            queryset = queryset.filter(user_id=validated_data['user_id'])
        
        # 用户名过滤（模糊匹配）
        if validated_data.get('username'):
            queryset = queryset.filter(
                user__username__icontains=validated_data['username']
            )
        
        # 操作类型过滤
        if validated_data.get('action_type'):
            queryset = queryset.filter(action_type=validated_data['action_type'])
        
        # 操作模块过滤（模糊匹配）
        if validated_data.get('module'):
            queryset = queryset.filter(
                module__icontains=validated_data['module']
            )
        
        # 操作状态过滤
        if validated_data.get('status') is not None:
            queryset = queryset.filter(status=validated_data['status'])
        
        # IP地址过滤
        if validated_data.get('ip_address'):
            queryset = queryset.filter(ip_address=validated_data['ip_address'])
        
        # 时间范围过滤
        if validated_data.get('start_date'):
            queryset = queryset.filter(
                created_at__gte=validated_data['start_date']
            )
        
        if validated_data.get('end_date'):
            queryset = queryset.filter(
                created_at__lte=validated_data['end_date']
            )
        
        # 分页处理
        page = validated_data.get('page', 1)
        page_size = validated_data.get('page_size', 20)
        
        total_count = queryset.count()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        logs = queryset[start_index:end_index]
        
        # 序列化数据
        serializer = OperationLogListSerializer(logs, many=True)
        
        # 构建响应数据
        response_data = {
            'logs': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size,
                'has_next': end_index < total_count,
                'has_previous': page > 1,
            }
        }
        
        return HertzResponse.success(
            data=response_data,
            message='获取操作日志列表成功'
        )
        
    except Exception as e:
        return HertzResponse.error(
            message='获取操作日志列表失败',
            error=str(e)
        )


@api_view(['GET'])
@permission_required('system:log:query')
@extend_schema(
    operation_id='operation_log_detail',
    summary='获取操作日志详情',
    description='根据日志ID获取操作日志的详细信息，仅管理员可访问',
    parameters=[
        OpenApiParameter(
            name='log_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='日志ID',
            required=True
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='日志不存在'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        403: OpenApiResponse(
            response=HertzResponseSerializer,
            description='权限不足'
        ),
    },
    tags=['日志管理']
)
def operation_log_detail(request, log_id):
    """
    获取操作日志详情
    
    Args:
        request: HTTP请求对象
        log_id: 日志ID
        
    Returns:
        HertzResponse: 包含日志详情的响应
    """
    try:
        # 查找日志记录
        try:
            log = OperationLog.objects.select_related('user').get(log_id=log_id)
        except OperationLog.DoesNotExist:
            return HertzResponse.not_found(message='操作日志不存在')
        
        # 序列化数据
        serializer = OperationLogSerializer(log)
        
        return HertzResponse.success(
            data=serializer.data,
            message='获取操作日志详情成功'
        )
        
    except Exception as e:
        return HertzResponse.error(
            message='获取操作日志详情失败',
            error=str(e)
        )