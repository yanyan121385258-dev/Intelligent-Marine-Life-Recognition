from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db import transaction
from django.db.models import Q, Count
from studio_django_auth.utils.decorators import permission_required, no_login_required
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_utils.log.log_decorator import operation_log
from studio_django_captcha.serializers import HertzResponseSerializer
from .models import Wiki, WikiArticle
from .serializers import (
    WikiSerializer, WikiTreeSerializer, WikiArticleSerializer,
    WikiArticleListSerializer, WikiArticleCreateSerializer,
    WikiArticleUpdateSerializer
)
from studio_django_auth.utils.decorators import login_required
import json
import re

# ==================== 知识分类管理 ====================                                    

@extend_schema(
    operation_id='wiki_category_list',
    summary='获取知识分类列表',
    description='分页获取知识分类列表，支持按分类名称、状态等条件筛选',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取知识分类列表成功'
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
    tags=['知识分类管理']
)
@api_view(['GET'])
@no_login_required
def wiki_category_list(request):
    """知识分类列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    name = request.GET.get('name', '')
    parent_id = request.GET.get('parent_id', '')
    is_active = request.GET.get('is_active', '')
    
    # 构建查询条件
    queryset = Wiki.objects.all()
    
    if name:
        queryset = queryset.filter(name__icontains=name)
    if parent_id:
        if parent_id == '0':  # 查询顶级分类
            queryset = queryset.filter(parent__isnull=True)
        else:
            queryset = queryset.filter(parent_id=parent_id)
    if is_active:
        queryset = queryset.filter(is_active=is_active == 'true')
    
    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    categories = queryset.order_by('sort_order', 'name')[start:end]
    
    serializer = WikiSerializer(categories, many=True)
    
    return HertzResponse.success(data={
        'list': serializer.data,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@extend_schema(
    operation_id='wiki_category_tree',
    summary='获取知识分类树形结构',
    description='获取完整的知识分类树形结构',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取知识分类树形结构成功'
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
    tags=['知识分类管理']
)
@api_view(['GET'])
@no_login_required
def wiki_category_tree(request):
    """知识分类树形结构"""
    categories = Wiki.objects.filter(is_active=True).order_by('sort_order', 'name')
    serializer = WikiTreeSerializer(categories, many=True)
    return HertzResponse.success(data=serializer.data)


@extend_schema(
    operation_id='wiki_category_create',
    summary='创建知识分类',
    description='创建新的知识分类',
    request=WikiSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识分类创建成功'
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
    tags=['知识分类管理']
)
@api_view(['POST'])
@no_login_required
@operation_log(action_type='CREATE', module='知识分类管理', description='创建知识分类')
def wiki_category_create(request):
    """创建知识分类"""
    serializer = WikiSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    try:
        category = serializer.save()
        return HertzResponse.success(
            message='知识分类创建成功',
            data=WikiSerializer(category).data
        )
    except Exception as e:
        return HertzResponse.error(message=f'知识分类创建失败: {str(e)}')


@extend_schema(
    operation_id='wiki_category_detail',
    summary='获取知识分类详情',
    description='根据分类ID获取知识分类详细信息',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取知识分类详情成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识分类不存在'
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
    tags=['知识分类管理']
)
@api_view(['GET'])
@no_login_required
def wiki_category_detail(request, category_id):
    """知识分类详情"""
    try:
        category = Wiki.objects.get(id=category_id)
        serializer = WikiSerializer(category)
        return HertzResponse.success(data=serializer.data)
    except Wiki.DoesNotExist:
        return HertzResponse.not_found(message='知识分类不存在')


@extend_schema(
    operation_id='wiki_category_update',
    summary='更新知识分类',
    description='根据分类ID更新知识分类信息',
    request=WikiSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识分类更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识分类不存在'
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
    tags=['知识分类管理']
)
@api_view(['PUT'])
@no_login_required
@operation_log(action_type='UPDATE', module='知识分类管理', description='更新知识分类')
def wiki_category_update(request, category_id):
    """更新知识分类"""
    try:
        category = Wiki.objects.get(id=category_id)
        serializer = WikiSerializer(category, data=request.data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        category = serializer.save()
        return HertzResponse.success(
            message='知识分类更新成功',
            data=WikiSerializer(category).data
        )
    except Wiki.DoesNotExist:
        return HertzResponse.not_found(message='知识分类不存在')
    except Exception as e:
        return HertzResponse.error(message=f'知识分类更新失败: {str(e)}')


@extend_schema(
    operation_id='wiki_category_delete',
    summary='删除知识分类',
    description='根据分类ID删除知识分类（软删除）',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识分类删除成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='该分类下还有子分类或文章，无法删除'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识分类不存在'
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
    tags=['知识分类管理']
)
@api_view(['DELETE'])
@no_login_required
@operation_log(action_type='DELETE', module='知识分类管理', description='删除知识分类')
def wiki_category_delete(request, category_id):
    """删除知识分类"""
    try:
        category = Wiki.objects.get(id=category_id)
        
        # 检查是否有子分类
        if Wiki.objects.filter(parent=category).exists():
            return HertzResponse.error(message='该分类下还有子分类，无法删除')
        
        # 检查是否有文章
        if WikiArticle.objects.filter(category=category).exists():
            return HertzResponse.error(message='该分类下还有文章，无法删除')
        
        # 软删除
        category.is_active = False
        category.save(update_fields=['is_active'])
        
        return HertzResponse.success(message='知识分类删除成功')
    except Wiki.DoesNotExist:
        return HertzResponse.not_found(message='知识分类不存在')
    except Exception as e:
        return HertzResponse.error(message=f'知识分类删除失败: {str(e)}')


# ==================== 知识文章管理 ====================

@extend_schema(
    operation_id='wiki_article_list',
    summary='获取知识文章列表',
    description='分页获取知识文章列表，支持按标题、分类、作者、状态等条件筛选',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取知识文章列表成功'
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
    tags=['知识文章管理']
)
@api_view(['GET'])
@no_login_required
def wiki_article_list(request):
    """知识文章列表"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    title = request.GET.get('title', '')
    category_id = request.GET.get('category_id', '')
    author_id = request.GET.get('author_id', '')
    status = request.GET.get('status', '')
    
    # 构建查询条件
    queryset = WikiArticle.objects.all()
    
    if title:
        queryset = queryset.filter(title__icontains=title)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if author_id:
        queryset = queryset.filter(author_id=author_id)
    if status:
        queryset = queryset.filter(status=status)
    
    # 分页
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    articles = queryset.order_by('-created_at')[start:end]
    
    serializer = WikiArticleListSerializer(articles, many=True)
    
    return HertzResponse.success(data={
        'list': serializer.data,
        'total': total,
        'page': page,
        'page_size': page_size
    })


@extend_schema(
    operation_id='wiki_article_create',
    summary='创建知识文章',
    description='创建新的知识文章',
    request=WikiArticleCreateSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章创建成功'
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
    tags=['知识文章管理']
)
@api_view(['POST'])
@login_required
@operation_log(action_type='CREATE', module='知识文章管理', description='创建知识文章')
def wiki_article_create(request):
    """创建知识文章"""
    serializer = WikiArticleCreateSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
    
    try:
        article = serializer.save()
        return HertzResponse.success(
            message='知识文章创建成功',
            data=WikiArticleSerializer(article).data
        )
    except Exception as e:
        return HertzResponse.error(message=f'知识文章创建失败: {str(e)}')


@extend_schema(
    operation_id='wiki_article_detail',
    summary='获取知识文章详情',
    description='根据文章ID获取知识文章详细信息，并增加浏览量',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='获取知识文章详情成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章不存在'
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
    tags=['知识文章管理']
)
@api_view(['GET'])
@no_login_required
def wiki_article_detail(request, article_id):
    """知识文章详情"""
    try:
        article = WikiArticle.objects.select_related('category', 'author').get(id=article_id)
        
        # 增加浏览量
        article.increment_view_count()
        
        serializer = WikiArticleSerializer(article)
        return HertzResponse.success(data=serializer.data)
    except WikiArticle.DoesNotExist:
        return HertzResponse.not_found(message='知识文章不存在')


@extend_schema(
    operation_id='wiki_article_update',
    summary='更新知识文章',
    description='根据文章ID更新知识文章信息',
    request=WikiArticleUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章更新成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='参数验证失败'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章不存在'
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
    tags=['知识文章管理']
)
@api_view(['PUT'])
@no_login_required
@operation_log(action_type='UPDATE', module='知识文章管理', description='更新知识文章')
def wiki_article_update(request, article_id):
    """更新知识文章"""
    try:
        article = WikiArticle.objects.get(id=article_id)
        serializer = WikiArticleUpdateSerializer(article, data=request.data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
        
        article = serializer.save()
        return HertzResponse.success(
            message='知识文章更新成功',
            data=WikiArticleSerializer(article).data
        )
    except WikiArticle.DoesNotExist:
        return HertzResponse.not_found(message='知识文章不存在')
    except Exception as e:
        return HertzResponse.error(message=f'知识文章更新失败: {str(e)}')


@extend_schema(
    operation_id='wiki_article_delete',
    summary='删除知识文章',
    description='根据文章ID删除知识文章',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章删除成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章不存在'
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
    tags=['知识文章管理']
)
@api_view(['DELETE'])
@no_login_required
@operation_log(action_type='DELETE', module='知识文章管理', description='删除知识文章')
def wiki_article_delete(request, article_id):
    """删除知识文章"""
    try:
        article = WikiArticle.objects.get(id=article_id)
        article.delete()
        return HertzResponse.success(message='知识文章删除成功')
    except WikiArticle.DoesNotExist:
        return HertzResponse.not_found(message='知识文章不存在')
    except Exception as e:
        return HertzResponse.error(message=f'知识文章删除失败: {str(e)}')


@extend_schema(
    operation_id='wiki_article_publish',
    summary='发布知识文章',
    description='将草稿状态的文章发布',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章发布成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='文章状态不允许发布'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章不存在'
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
    tags=['知识文章管理']
)
@api_view(['POST'])
@no_login_required
@operation_log(action_type='PUBLISH', module='知识文章管理', description='发布知识文章')
def wiki_article_publish(request, article_id):
    """发布知识文章"""
    try:
        article = WikiArticle.objects.get(id=article_id)
        
        if article.status == 'published':
            return HertzResponse.error(message='文章已经是发布状态')
        
        article.status = 'published'
        if not article.published_at:
            from django.utils import timezone
            article.published_at = timezone.now()
        article.save(update_fields=['status', 'published_at'])
        
        return HertzResponse.success(message='知识文章发布成功')
    except WikiArticle.DoesNotExist:
        return HertzResponse.not_found(message='知识文章不存在')
    except Exception as e:
        return HertzResponse.error(message=f'知识文章发布失败: {str(e)}')


@extend_schema(
    operation_id='wiki_article_archive',
    summary='归档知识文章',
    description='将文章状态设置为归档',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章归档成功'
        ),
        404: OpenApiResponse(
            response=HertzResponseSerializer,
            description='知识文章不存在'
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
    tags=['知识文章管理']
)
@api_view(['POST'])
@no_login_required
@operation_log(action_type='ARCHIVE', module='知识文章管理', description='归档知识文章')
def wiki_article_archive(request, article_id):
    """归档知识文章"""
    try:
        article = WikiArticle.objects.get(id=article_id)
        article.status = 'archived'
        article.save(update_fields=['status'])
        return HertzResponse.success(message='知识文章归档成功')
    except WikiArticle.DoesNotExist:
        return HertzResponse.not_found(message='知识文章不存在')
    except Exception as e:
        return HertzResponse.error(message=f'知识文章归档失败: {str(e)}')


@extend_schema(
    operation_id='wiki_article_import',
    summary='导入知识文章',
    description='支持导入 Markdown(.md)、HTML(.html)、JSON(.json) 格式的文章文件',
    responses={
        200: OpenApiResponse(
            response=HertzResponseSerializer,
            description='导入成功'
        ),
        400: OpenApiResponse(
            response=HertzResponseSerializer,
            description='导入失败'
        )
    },
    tags=['知识文章管理']
)
@api_view(['POST'])
@no_login_required
@parser_classes([MultiPartParser, FormParser])
@operation_log(action_type='IMPORT', module='知识文章管理', description='导入知识文章')
def wiki_article_import(request):
    """导入知识文章"""
    try:
        # 获取上传的文件
        file_obj = request.FILES.get('file')
        if not file_obj:
            return HertzResponse.validation_error(message='请选择要导入的文件')
        
        # 获取分类ID（可选）
        category_id = request.data.get('category_id')
        status = request.data.get('status', 'draft')
        
        # 如果没有指定分类，获取默认分类或创建一个
        if not category_id:
            # 尝试获取第一个可用分类
            default_category = Wiki.objects.filter(is_active=True).first()
            if default_category:
                category_id = default_category.id
            else:
                # 创建一个默认分类
                default_category = Wiki.objects.create(
                    name='未分类',
                    description='默认分类，用于存放未分类的文章',
                    is_active=True
                )
                category_id = default_category.id
        
        # 获取或创建默认作者
        from studio_django_auth.models import HertzUser
        default_author = HertzUser.objects.filter(is_active=True).first()
        if not default_author:
            # 创建一个默认用户
            default_author = HertzUser.objects.create(
                username='import_user',
                email='import@example.com',
                real_name='导入用户',
                is_active=True
            )
        
        # 获取文件内容
        file_content = file_obj.read().decode('utf-8')
        
        # 根据文件扩展名判断格式
        filename = file_obj.name.lower()
        imported_count = 0
        errors = []
        
        if filename.endswith('.json'):
            # JSON格式 - 批量导入
            try:
                data = json.loads(file_content)
                if isinstance(data, list):
                    for item in data:
                        try:
                            title = item.get('title', '未命名文章')
                            content = item.get('content', '')
                            summary = item.get('summary', '')
                            item_category_id = item.get('category', category_id)
                            item_status = item.get('status', status)
                            tags = item.get('tags', '')
                            
                            WikiArticle.objects.create(
                                title=title,
                                content=content,
                                summary=summary,
                                category_id=item_category_id,
                                author_id=default_author.user_id,
                                status=item_status,
                                tags=tags
                            )
                            imported_count += 1
                        except Exception as e:
                            errors.append(f"导入文章 '{title}' 失败: {str(e)}")
                else:
                    return HertzResponse.validation_error(message='JSON文件格式错误，应为数组格式')
            except json.JSONDecodeError:
                return HertzResponse.validation_error(message='JSON文件格式错误')
        
        elif filename.endswith('.md') or filename.endswith('.markdown'):
            # Markdown格式
            title = extract_title_from_markdown(file_content) or filename.replace('.md', '').replace('.markdown', '')
            summary = extract_summary_from_markdown(file_content)
            
            # 直接创建文章对象
            try:
                WikiArticle.objects.create(
                    title=title,
                    content=file_content,
                    summary=summary,
                    category_id=category_id,
                    author_id=default_author.user_id,
                    status=status
                )
                imported_count = 1
            except Exception as e:
                return HertzResponse.error(message=f'导入失败: {str(e)}')
        
        elif filename.endswith('.html'):
            # HTML格式
            title = extract_title_from_html(file_content) or filename.replace('.html', '')
            summary = extract_summary_from_html(file_content)
            
            try:
                WikiArticle.objects.create(
                    title=title,
                    content=file_content,
                    summary=summary,
                    category_id=category_id,
                    author_id=default_author.user_id,
                    status=status
                )
                imported_count = 1
            except Exception as e:
                return HertzResponse.error(message=f'导入失败: {str(e)}')
        
        else:
            return HertzResponse.validation_error(message='不支持的文件格式，请上传 .md、.html 或 .json 文件')
        
        if errors:
            return HertzResponse.success(
                message=f'导入完成，成功导入 {imported_count} 篇文章，{len(errors)} 篇失败',
                data={'imported_count': imported_count, 'errors': errors}
            )
        
        return HertzResponse.success(
            message=f'成功导入 {imported_count} 篇文章',
            data={'imported_count': imported_count}
        )
    
    except Exception as e:
        return HertzResponse.error(message=f'导入失败: {str(e)}')


def extract_title_from_markdown(content):
    """从Markdown内容中提取标题"""
    lines = content.strip().split('\n')
    for line in lines:
        # 查找一级标题
        if line.startswith('# '):
            return line[2:].strip()
        # 查找二级标题
        if line.startswith('## '):
            return line[3:].strip()
    return None


def extract_summary_from_markdown(content):
    """从Markdown内容中提取摘要"""
    lines = content.strip().split('\n')
    summary_lines = []
    for line in lines:
        # 跳过标题、空行和代码块
        if line.startswith('#') or line.strip() == '' or line.startswith('```'):
            continue
        summary_lines.append(line)
        if len('\n'.join(summary_lines)) >= 100:
            break
    result = '\n'.join(summary_lines).strip()
    # 截取前200个字符作为摘要
    return result[:200] if len(result) > 200 else result


def extract_title_from_html(content):
    """从HTML内容中提取标题"""
    match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # 如果没有title标签，查找h1标签
    match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # 查找h2标签
    match = re.search(r'<h2[^>]*>([^<]+)</h2>', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    return None


def extract_summary_from_html(content):
    """从HTML内容中提取摘要"""
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', content)
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()
    # 截取前200个字符作为摘要
    return text[:200] if len(text) > 200 else text