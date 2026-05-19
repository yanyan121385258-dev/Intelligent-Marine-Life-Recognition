from rest_framework import serializers
from django.utils import timezone
from .models import Wiki, WikiArticle
from studio_django_auth.models import HertzUser


class WikiSerializer(serializers.ModelSerializer):
    """
    知识分类序列化器
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()
    full_path = serializers.CharField(source='get_full_path', read_only=True)

    class Meta:
        model = Wiki
        fields = [
            'id', 'name', 'description', 'parent', 'parent_name', 
            'sort_order', 'is_active', 'created_at', 'updated_at',
            'children_count', 'articles_count', 'full_path'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children_count(self, obj):
        """获取子分类数量"""
        return obj.children.filter(is_active=True).count()

    def get_articles_count(self, obj):
        """获取文章数量"""
        return obj.articles.filter(status='published').count()

    def validate_name(self, value):
        """验证分类名称唯一性"""
        # 检查名称是否已存在
        if Wiki.objects.filter(name=value).exists():
            # 如果是更新操作，允许同名（即自己）
            if self.instance and self.instance.name == value:
                return value
            raise serializers.ValidationError("分类名称已存在")
        return value

    def validate_parent(self, value):
        """验证父分类"""
        if value and self.instance:
            # 防止循环引用
            if value == self.instance:
                raise serializers.ValidationError("不能将自己设置为父分类")
            
            # 检查是否会形成循环
            current = value
            while current.parent:
                if current.parent == self.instance:
                    raise serializers.ValidationError("不能形成循环引用")
                current = current.parent
        return value


class WikiTreeSerializer(serializers.ModelSerializer):
    """
    知识分类树形结构序列化器
    """
    children = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Wiki
        fields = [
            'id', 'name', 'description', 'sort_order', 
            'is_active', 'articles_count', 'children'
        ]

    def get_children(self, obj):
        """获取子分类"""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return WikiTreeSerializer(children, many=True).data

    def get_articles_count(self, obj):
        """获取文章数量"""
        return obj.articles.filter(status='published').count()


class WikiArticleSerializer(serializers.ModelSerializer):
    """
    知识文章序列化器
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    tags_list = serializers.ListField(source='get_tags_list', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WikiArticle
        fields = [
            'id', 'title', 'content', 'summary', 'image', 'category', 'category_name',
            'author', 'author_name', 'status', 'status_display', 'tags', 'tags_list',
            'view_count', 'sort_order', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']

    def validate_category(self, value):
        """验证分类"""
        if not value.is_active:
            raise serializers.ValidationError("所选分类已被禁用")
        return value

    def validate_status(self, value):
        """验证状态"""
        if value not in ['draft', 'published', 'archived']:
            raise serializers.ValidationError("无效的文章状态")
        return value

    def create(self, validated_data):
        """创建文章"""
        # 设置作者为当前用户
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        
        # 如果状态为已发布，设置发布时间
        if validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新文章"""
        # 如果状态从非发布改为发布，设置发布时间
        if (validated_data.get('status') == 'published' and 
            instance.status != 'published' and 
            not instance.published_at):
            validated_data['published_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class WikiArticleListSerializer(serializers.ModelSerializer):
    """
    知识文章列表序列化器（简化版）
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WikiArticle
        fields = [
            'id', 'title', 'summary', 'image', 'category_name', 'author_name',
            'status', 'status_display', 'view_count', 'created_at', 'updated_at', 'published_at'
        ]


class WikiArticleCreateSerializer(serializers.ModelSerializer):
    """
    知识文章创建序列化器
    """
    class Meta:
        model = WikiArticle
        fields = [
            'title', 'content', 'summary', 'image', 'category',
            'status', 'tags', 'sort_order'
        ]

    def validate_category(self, value):
        """验证分类"""
        if not value.is_active:
            raise serializers.ValidationError("所选分类已被禁用")
        return value

    def create(self, validated_data):
        """创建文章"""
        # 设置作者为当前用户
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        
        # 如果状态为已发布，设置发布时间
        if validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()
        
        return super().create(validated_data)


class WikiArticleUpdateSerializer(serializers.ModelSerializer):
    """
    知识文章更新序列化器
    """
    class Meta:
        model = WikiArticle
        fields = [
            'title', 'content', 'summary', 'image', 'category',
            'status', 'tags', 'sort_order'
        ]

    def validate_category(self, value):
        """验证分类"""
        if not value.is_active:
            raise serializers.ValidationError("所选分类已被禁用")
        return value

    def update(self, instance, validated_data):
        """更新文章"""
        # 如果状态从非发布改为发布，设置发布时间
        if (validated_data.get('status') == 'published' and 
            instance.status != 'published' and 
            not instance.published_at):
            validated_data['published_at'] = timezone.now()
        
        return super().update(instance, validated_data)