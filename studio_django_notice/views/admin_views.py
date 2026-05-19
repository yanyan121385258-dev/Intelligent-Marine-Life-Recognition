from rest_framework.decorators import api_view
from rest_framework import status
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_captcha.serializers import HertzResponseSerializer
from studio_django_auth.utils.decorators import login_required
from ..models import HertzNotice, HertzUserNotice
from ..serializers.notice_serializers import (
    NoticeCreateSerializer, NoticeUpdateSerializer,
    NoticeListSerializer, NoticeDetailSerializer
)
from studio_django_auth.models import HertzUser


@extend_schema(
    operation_id='admin_create_notice',
    summary='管理员创建通知',
    description='管理员发布新的通知公告',
    request=NoticeCreateSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知创建成功'
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
    tags=['管理员-通知管理']
)
@api_view(['POST'])
@login_required
def admin_create_notice(request):
    """管理员创建通知"""
    try:
        serializer = NoticeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        # 创建通知
        notice = serializer.save(publisher=request.user)
        
        # 如果通知已发布，为所有用户创建通知状态记录
        if notice.status == 1:  # 已发布状态
            users = HertzUser.objects.filter(status=1, is_active=True)
            user_notices = [
                HertzUserNotice(user=user, notice=notice)
                for user in users
            ]
            HertzUserNotice.objects.bulk_create(user_notices, ignore_conflicts=True)
        
        return HertzResponse.success(
            message='通知创建成功',
            data={'notice_id': notice.notice_id}
        )
    
    except Exception as e:
        return HertzResponse.error(message='通知创建失败', error=str(e))


@extend_schema(
    operation_id='admin_update_notice',
    summary='管理员更新通知',
    description='管理员编辑已存在的通知',
    request=NoticeUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知不存在'
        )
    },
    tags=['管理员-通知管理']
)
@api_view(['PUT'])
@login_required
def admin_update_notice(request, notice_id):
    """管理员更新通知"""
    try:
        notice = HertzNotice.objects.get(notice_id=notice_id)
    except HertzNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在')
    
    try:
        serializer = NoticeUpdateSerializer(notice, data=request.data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        old_status = notice.status
        updated_notice = serializer.save()
        
        # 如果状态从草稿变为已发布，为所有用户创建通知状态记录
        if old_status == 0 and updated_notice.status == 1:
            users = HertzUser.objects.filter(status=1, is_active=True)
            user_notices = [
                HertzUserNotice(user=user, notice=updated_notice)
                for user in users
            ]
            HertzUserNotice.objects.bulk_create(user_notices, ignore_conflicts=True)
        
        return HertzResponse.success(message='通知更新成功')
    
    except Exception as e:
        return HertzResponse.error(message='通知更新失败', error=str(e))


@extend_schema(
    operation_id='admin_delete_notice',
    summary='管理员删除通知',
    description='管理员删除指定的通知',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知删除成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知不存在'
        )
    },
    tags=['管理员-通知管理']
)
@api_view(['DELETE'])
@login_required
def admin_delete_notice(request, notice_id):
    """管理员删除通知"""
    try:
        notice = HertzNotice.objects.get(notice_id=notice_id)
    except HertzNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在')
    
    try:
        with transaction.atomic():
            # 删除相关的用户通知状态记录
            HertzUserNotice.objects.filter(notice=notice).delete()
            # 删除通知
            notice.delete()
        
        return HertzResponse.success(message='通知删除成功')
    
    except Exception as e:
        return HertzResponse.error(message='通知删除失败', error=str(e))


@extend_schema(
    operation_id='admin_get_notice_list',
    summary='管理员获取通知列表',
    description='管理员查询通知列表，支持分页和筛选',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取通知列表成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['管理员-通知管理']
)
@api_view(['GET'])
@login_required
def admin_get_notice_list(request):
    """管理员获取通知列表"""
    try:
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        notice_type = request.GET.get('notice_type')
        status_filter = request.GET.get('status')
        priority = request.GET.get('priority')
        is_top = request.GET.get('is_top')
        keyword = request.GET.get('keyword')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # 构建查询条件
        queryset = HertzNotice.objects.all()
        
        if notice_type:
            queryset = queryset.filter(notice_type=notice_type)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        if is_top:
            queryset = queryset.filter(is_top=is_top.lower() == 'true')
        
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        
        if start_date:
            queryset = queryset.filter(publish_time__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(publish_time__lte=end_date)
        
        # 排序
        queryset = queryset.order_by('-is_top', '-priority', '-publish_time')
        
        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 序列化数据
        serializer = NoticeListSerializer(page_obj.object_list, many=True)
        
        return HertzResponse.success(
            message='获取通知列表成功',
            data={
                'notices': serializer.data,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
        )
    
    except Exception as e:
        return HertzResponse.error(message='获取通知列表失败', error=str(e))


@extend_schema(
    operation_id='admin_get_notice_detail',
    summary='管理员获取通知详情',
    description='管理员查看指定通知的详细信息',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取通知详情成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知不存在'
        )
    },
    tags=['管理员-通知管理']
)
@api_view(['GET'])
@login_required
def admin_get_notice_detail(request, notice_id):
    """管理员获取通知详情"""
    try:
        notice = HertzNotice.objects.get(notice_id=notice_id)
    except HertzNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在')
    
    try:
        serializer = NoticeDetailSerializer(notice)
        return HertzResponse.success(
            message='获取通知详情成功',
            data=serializer.data
        )
    
    except Exception as e:
        return HertzResponse.error(message='获取通知详情失败', error=str(e))


@extend_schema(
    operation_id='admin_publish_notice',
    summary='管理员发布通知',
    description='管理员将草稿状态的通知发布',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知发布成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知状态不允许发布'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知不存在'
        )
    },
    tags=['管理员-通知管理']
)
@api_view(['POST'])
@login_required
def admin_publish_notice(request, notice_id):
    """管理员发布通知"""
    try:
        notice = HertzNotice.objects.get(notice_id=notice_id)
    except HertzNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在')
    
    if notice.status not in (0, 2):  # 只有草稿状态才能发布
        return HertzResponse.fail(message='只有草稿状态的通知才能发布')
    
    try:
        with transaction.atomic():
            # 更新通知状态
            notice.status = 1
            notice.publish_time = timezone.now()
            notice.save(update_fields=['status', 'publish_time', 'updated_at'])
            
            # 为所有用户创建通知状态记录
            users = HertzUser.objects.filter(status=1, is_active=True)
            user_notices = [
                HertzUserNotice(user=user, notice=notice)
                for user in users
            ]
            HertzUserNotice.objects.bulk_create(user_notices, ignore_conflicts=True)
        
        return HertzResponse.success(message='通知发布成功')
    
    except Exception as e:
        return HertzResponse.error(message='通知发布失败', error=str(e))


@extend_schema(
    operation_id='admin_withdraw_notice',
    summary='管理员撤回通知',
    description='管理员撤回已发布的通知',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知撤回成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知状态不允许撤回'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='通知不存在'
        )
    },
    tags=['管理员-通知管理']
)
@api_view(['POST'])
@login_required
def admin_withdraw_notice(request, notice_id):
    """管理员撤回通知"""
    try:
        notice = HertzNotice.objects.get(notice_id=notice_id)
    except HertzNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在')
    
    if notice.status != 1:  # 只有已发布状态才能撤回
        return HertzResponse.fail(message='只有已发布的通知才能撤回')
    
    try:
        # 更新通知状态
        notice.status = 2  # 已撤回
        notice.save(update_fields=['status', 'updated_at'])
        
        return HertzResponse.success(message='通知撤回成功')
    
    except Exception as e:
        return HertzResponse.error(message='通知撤回失败', error=str(e))