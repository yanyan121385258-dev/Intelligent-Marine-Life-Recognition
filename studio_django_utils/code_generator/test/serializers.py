from rest_framework import serializers
from django.utils import timezone
from models import *

class TestSerializer(serializers.ModelSerializer):
    """
    测试序列化器
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    articales_count = serializers.SerializerMethodField()
    full_path = serializers.CharField(source='get_full_path',read_only=True)

    class Meta:
        model = Testmodels
        fields=[
            'name','parent','is_active','full_path','created_at','updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


        def get_children_count(self, obj):
            """获取子分类数量"""
            return obj.children.filter(is_active=True).count()
