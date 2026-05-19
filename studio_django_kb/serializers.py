from rest_framework import serializers
from .models import KBItem, KBChunk, KBEntity, KBRelation


class KBItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBItem
        fields = ['title', 'modality', 'source_type', 'content', 'file', 'metadata']
        extra_kwargs = {
            'modality': {'required': False},
            'source_type': {'required': False},
            'content': {'required': False},
            'file': {'required': False},
            'metadata': {'required': False},
        }

    def validate(self, attrs):
        source_type = attrs.get('source_type', 'text')
        content = attrs.get('content')
        file = attrs.get('file')
        if source_type == 'text' and not content:
            raise serializers.ValidationError({'content': '当 source_type=text 时，content 必填'})
        if source_type == 'file' and not file:
            raise serializers.ValidationError({'file': '当 source_type=file 时，file 必填'})
        return attrs


class KBItemSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = KBItem
        fields = ['id', 'title', 'modality', 'source_type', 'metadata', 'created_at', 'updated_at', 'chunk_count']

    def get_chunk_count(self, obj):
        return obj.chunks.count()


class KBChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBChunk
        fields = ['id', 'item', 'index', 'text', 'embedding', 'created_at']


class KBEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = KBEntity
        fields = ['id', 'name', 'type', 'properties', 'created_at']


class KBRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KBRelation
        fields = ['id', 'source', 'target', 'relation_type', 'properties', 'source_chunk', 'created_at']
