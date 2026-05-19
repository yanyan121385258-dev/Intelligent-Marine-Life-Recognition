from rest_framework.decorators import api_view
from rest_framework import status
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, F
from drf_spectacular.utils import extend_schema, OpenApiResponse
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_captcha.serializers import HertzResponseSerializer
from studio_django_auth.utils.decorators import login_required
from ..models import HertzNotice, HertzUserNotice
from ..serializers.notice_serializers import (
    UserNoticeListSerializer, UserNoticeDetailSerializer,
    NoticeReadStatusSerializer, NoticeStarStatusSerializer,
    BatchNoticeReadSerializer
)


@extend_schema(
    operation_id='user_get_notice_list',
    summary='用户获取通知列表',
    description='用户查看自己的通知列表，支持分页和筛选',
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
    tags=['用户-通知管理']
)
@api_view(['GET'])
@login_required
def user_get_notice_list(request):
    """用户获取通知列表"""
    try:
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        notice_type = request.GET.get('notice_type')
        is_read = request.GET.get('is_read')
        is_starred = request.GET.get('is_starred')
        priority = request.GET.get('priority')
        keyword = request.GET.get('keyword')
        
        # 构建查询条件 - 只查询已发布且未过期的通知
        queryset = HertzUserNotice.objects.filter(
            user=request.user,
            notice__status=1  # 只显示已发布的通知
        ).select_related('notice', 'notice__publisher')
        
        # 过滤过期通知（可选，根据业务需求决定是否显示过期通知）
        show_expired = request.GET.get('show_expired', 'false').lower() == 'true'
        if not show_expired:
            queryset = queryset.filter(
                Q(notice__expire_time__isnull=True) | 
                Q(notice__expire_time__gt=timezone.now())
            )
        
        if notice_type:
            queryset = queryset.filter(notice__notice_type=notice_type)
        
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        if is_starred is not None:
            queryset = queryset.filter(is_starred=is_starred.lower() == 'true')
        
        if priority:
            queryset = queryset.filter(notice__priority=priority)
        
        if keyword:
            queryset = queryset.filter(notice__title__icontains=keyword)
        
        # 排序：置顶 > 优先级 > 发布时间
        queryset = queryset.order_by(
            '-notice__is_top', 
            '-notice__priority', 
            '-notice__publish_time'
        )
        
        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 序列化数据
        serializer = UserNoticeListSerializer(page_obj.object_list, many=True)
        
        # 统计信息
        total_count = HertzUserNotice.objects.filter(
            user=request.user,
            notice__status=1
        ).count()
        unread_count = HertzUserNotice.objects.filter(
            user=request.user,
            notice__status=1,
            is_read=False
        ).count()
        starred_count = HertzUserNotice.objects.filter(
            user=request.user,
            notice__status=1,
            is_starred=True
        ).count()
        
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
                },
                'statistics': {
                    'total_count': total_count,
                    'unread_count': unread_count,
                    'starred_count': starred_count
                }
            }
        )
    
    except Exception as e:
        return HertzResponse.error(message='获取通知列表失败', error=str(e))


@extend_schema(
    operation_id='user_get_notice_detail',
    summary='用户获取通知详情',
    description='用户查看指定通知的详细信息，自动标记为已读',
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
    tags=['用户-通知管理']
)
@api_view(['GET'])
@login_required
def user_get_notice_detail(request, notice_id):
    """用户获取通知详情"""
    try:
        # 查找用户的通知记录
        user_notice = HertzUserNotice.objects.select_related(
            'notice', 'notice__publisher'
        ).get(
            user=request.user,
            notice__notice_id=notice_id,
            notice__status=1  # 只能查看已发布的通知
        )
        
        # 检查通知是否过期
        if user_notice.notice.is_expired:
            return HertzResponse.fail(message='该通知已过期')
        
        # 自动标记为已读
        if not user_notice.is_read:
            user_notice.mark_as_read()
        
        # 增加查看次数
        HertzNotice.objects.filter(notice_id=notice_id).update(
            view_count=F('view_count') + 1
        )
        
        # 序列化数据
        serializer = UserNoticeDetailSerializer(user_notice)
        
        return HertzResponse.success(
            message='获取通知详情成功',
            data=serializer.data
        )
    
    except HertzUserNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在或无权访问')
    except Exception as e:
        return HertzResponse.error(message='获取通知详情失败', error=str(e))


@extend_schema(
    operation_id='user_mark_notice_read',
    summary='用户标记通知已读',
    description='用户手动标记指定通知为已读状态',
    request=NoticeReadStatusSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='标记已读成功'
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
    tags=['用户-通知管理']
)
@api_view(['POST'])
@login_required
def user_mark_notice_read(request):
    """用户标记通知已读"""
    try:
        serializer = NoticeReadStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        notice_id = serializer.validated_data['notice_id']
        
        # 查找用户的通知记录
        user_notice = HertzUserNotice.objects.get(
            user=request.user,
            notice__notice_id=notice_id,
            notice__status=1
        )
        
        # 标记为已读
        user_notice.mark_as_read()
        
        return HertzResponse.success(message='标记已读成功')
    
    except HertzUserNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在或无权访问')
    except Exception as e:
        return HertzResponse.error(message='标记已读失败', error=str(e))


@extend_schema(
    operation_id='user_batch_mark_read',
    summary='用户批量标记已读',
    description='用户批量标记多个通知为已读状态',
    request=BatchNoticeReadSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='批量标记已读成功'
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
    tags=['用户-通知管理']
)
@api_view(['POST'])
@login_required
def user_batch_mark_read(request):
    """用户批量标记已读"""
    try:
        serializer = BatchNoticeReadSerializer(data=request.data)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        notice_ids = serializer.validated_data['notice_ids']
        
        # 批量更新已读状态
        updated_count = HertzUserNotice.objects.filter(
            user=request.user,
            notice__notice_id__in=notice_ids,
            notice__status=1,
            is_read=False
        ).update(
            is_read=True,
            read_time=timezone.now(),
            updated_at=timezone.now()
        )
        
        return HertzResponse.success(
            message=f'批量标记已读成功，共标记{updated_count}条通知',
            data={'updated_count': updated_count}
        )
    
    except Exception as e:
        return HertzResponse.error(message='批量标记已读失败', error=str(e))


@extend_schema(
    operation_id='user_mark_all_read',
    summary='用户标记全部已读',
    description='用户标记所有未读通知为已读状态',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='标记全部已读成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户-通知管理']
)
@api_view(['POST'])
@login_required
def user_mark_all_read(request):
    """用户标记全部已读"""
    try:
        # 批量更新所有未读通知
        updated_count = HertzUserNotice.objects.filter(
            user=request.user,
            notice__status=1,
            is_read=False
        ).update(
            is_read=True,
            read_time=timezone.now(),
            updated_at=timezone.now()
        )
        
        return HertzResponse.success(
            message=f'标记全部已读成功，共标记{updated_count}条通知',
            data={'updated_count': updated_count}
        )
    
    except Exception as e:
        return HertzResponse.error(message='标记全部已读失败', error=str(e))


@extend_schema(
    operation_id='user_toggle_notice_star',
    summary='用户切换通知收藏状态',
    description='用户收藏或取消收藏指定通知',
    request=NoticeStarStatusSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='收藏状态更新成功'
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
    tags=['用户-通知管理']
)
@api_view(['POST'])
@login_required
def user_toggle_notice_star(request):
    """用户切换通知收藏状态"""
    try:
        serializer = NoticeStarStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        notice_id = serializer.validated_data['notice_id']
        is_starred = serializer.validated_data['is_starred']
        
        # 查找用户的通知记录
        user_notice = HertzUserNotice.objects.get(
            user=request.user,
            notice__notice_id=notice_id,
            notice__status=1
        )
        
        # 更新收藏状态
        if is_starred:
            user_notice.mark_as_starred()
            message = '收藏成功'
        else:
            user_notice.unmark_starred()
            message = '取消收藏成功'
        
        return HertzResponse.success(message=message)
    
    except HertzUserNotice.DoesNotExist:
        return HertzResponse.not_found(message='通知不存在或无权访问')
    except Exception as e:
        return HertzResponse.error(message='收藏状态更新失败', error=str(e))


@extend_schema(
    operation_id='user_get_notice_statistics',
    summary='用户获取通知统计信息',
    description='用户获取通知的统计数据，包括总数、未读数、收藏数等',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取统计信息成功'
        ),
        401: OpenApiResponse(
            response=HertzResponseSerializer,
            description='未授权访问'
        )
    },
    tags=['用户-通知管理']
)
@api_view(['GET'])
@login_required
def user_get_notice_statistics(request):
    """用户获取通知统计信息"""
    try:
        user_notices = HertzUserNotice.objects.filter(
            user=request.user,
            notice__status=1
        )
        
        # 统计各种状态的通知数量
        total_count = user_notices.count()
        unread_count = user_notices.filter(is_read=False).count()
        read_count = user_notices.filter(is_read=True).count()
        starred_count = user_notices.filter(is_starred=True).count()
        
        # 按通知类型统计
        type_statistics = {}
        for choice in HertzNotice.NOTICE_TYPE_CHOICES:
            type_id, type_name = choice
            count = user_notices.filter(notice__notice_type=type_id).count()
            type_statistics[type_name] = count
        
        # 按优先级统计
        priority_statistics = {}
        for choice in HertzNotice.PRIORITY_CHOICES:
            priority_id, priority_name = choice
            count = user_notices.filter(notice__priority=priority_id).count()
            priority_statistics[priority_name] = count
        
        return HertzResponse.success(
            message='获取统计信息成功',
            data={
                'total_count': total_count,
                'unread_count': unread_count,
                'read_count': read_count,
                'starred_count': starred_count,
                'type_statistics': type_statistics,
                'priority_statistics': priority_statistics
            }
        )
    
    except Exception as e:
        return HertzResponse.error(message='获取统计信息失败', error=str(e))