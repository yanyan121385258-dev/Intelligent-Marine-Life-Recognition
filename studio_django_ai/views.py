import json
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from studio_django_auth.utils.decorators import login_required
from .models import AIChat, AIChatMessage
from .serializers import AIChatSerializer, AIChatMessageSerializer, ChatRequestSerializer, AIChatDeleteSerializer
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_utils.ollama.ollama_client import OllamaClient
from studio_django_utils.log.log_decorator import operation_log
from django.conf import settings
import numpy as np
from studio_django_kb.models import KBChunk
from studio_django_kb.models import KBEntity, KBRelation
import json


class AIChatListView(GenericAPIView):
    """
    AI聊天列表接口
    获取用户创建的所有AI聊天
    """
    # 使用AuthMiddleware进行认证，不使用DRF权限类
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id='ai_chat_list',
        summary='获取AI聊天列表',
        description='获取当前用户的所有AI聊天会话',
        responses={
            200: OpenApiResponse(response=AIChatSerializer(many=True), description='成功'),
            401: OpenApiResponse(description='未授权访问'),
        },
        tags=['AI助手']
    )
    @login_required
    @operation_log('view', 'AI助手', description="获取AI聊天列表")
    def get(self, request, *args, **kwargs):
        # 获取查询参数
        query = request.GET.get('query', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 构建查询条件 - 使用user_id而不是user对象
        q_condition = Q(user_id=request.user_id)
        
        if query:
            q_condition &= Q(title__icontains=query)
        
        # 查询聊天列表
        chats = AIChat.objects.filter(q_condition).order_by('-updated_at')
        
        # 分页
        paginator = Paginator(chats, page_size)
        chats_page = paginator.get_page(page)
        
        # 构建返回数据
        chat_list = []
        for chat in chats_page:
            # 获取最近一条消息
            latest_message = AIChatMessage.objects.filter(chat=chat).order_by('-created_at').first()
            latest_content = latest_message.content[:50] + '...' if latest_message else ''
            
            chat_list.append({
                'id': chat.id,
                'title': chat.title,
                'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'latest_message': latest_content
            })
        
        return HertzResponse.success(data={
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'chats': chat_list
        })


class AIChatCreateView(GenericAPIView):
    """
    创建AI聊天接口
    """
    # 使用AuthMiddleware进行认证，不使用DRF权限类
    permission_classes = [AllowAny]
    serializer_class = AIChatSerializer
    
    @extend_schema(
        operation_id='ai_chat_create',
        summary='创建AI聊天',
        description='创建新的AI聊天会话',
        request=AIChatSerializer,
        responses={
            200: OpenApiResponse(response=AIChatSerializer, description='成功'),
            400: OpenApiResponse(description='参数错误'),
            401: OpenApiResponse(description='未授权访问'),
        },
        tags=['AI助手']
    )
    @login_required
    @operation_log('create', 'AI助手', description="创建AI聊天")
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        title = data.get('title', '新对话')
        
        # 创建聊天 - 使用user_id而不是user对象
        chat = AIChat.objects.create(
            user_id=request.user_id,
            title=title
        )
        
        return HertzResponse.success(data={
            'chat_id': chat.id,
            'title': chat.title
        }, message='创建成功')


class AIChatDetailView(GenericAPIView):
    """
    AI聊天详情接口
    获取聊天记录详情
    """
    # 使用AuthMiddleware进行认证，不使用DRF权限类
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id='ai_chat_detail',
        summary='获取AI聊天详情',
        description='获取指定AI聊天会话的详细信息和消息历史',
        responses={
            200: OpenApiResponse(response=AIChatMessageSerializer(many=True), description='成功'),
            401: OpenApiResponse(description='未授权访问'),
            404: OpenApiResponse(description='聊天不存在'),
        },
        tags=['AI助手']
    )
    @login_required
    @operation_log('view', 'AI助手', description="获取AI聊天详情")
    def get(self, request, chat_id, *args, **kwargs):
        try:
            # 使用user_id而不是user对象进行查询
            chat = AIChat.objects.get(id=chat_id, user_id=request.user_id)
            
            # 获取聊天消息
            messages = AIChatMessage.objects.filter(chat=chat).order_by('created_at')
            message_list = []
            
            for message in messages:
                message_list.append({
                    'id': message.id,
                    'role': message.role,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # 构建返回数据
            chat_data = {
                'id': chat.id,
                'title': chat.title,
                'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': chat.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'messages': message_list
            }
            
            return HertzResponse.success(data=chat_data)
        except AIChat.DoesNotExist:
            return HertzResponse.not_found(message='聊天不存在或无权访问')


class AIChatUpdateView(GenericAPIView):
    """
    更新AI聊天接口
    修改聊天标题
    """
    # 使用AuthMiddleware进行认证，不使用DRF权限类
    permission_classes = [AllowAny]
    serializer_class = AIChatSerializer
    
    @extend_schema(
        operation_id='ai_chat_update',
        summary='更新AI聊天',
        description='更新AI聊天会话的标题',
        request=AIChatSerializer,
        responses={
            200: OpenApiResponse(description='成功'),
            400: OpenApiResponse(description='参数错误'),
            401: OpenApiResponse(description='未授权访问'),
            404: OpenApiResponse(description='聊天不存在'),
        },
        tags=['AI助手']
    )
    @login_required
    @operation_log('update', 'AI助手', description="更新AI聊天")
    def put(self, request, chat_id, *args, **kwargs):
        try:
            # 使用user_id而不是user对象进行查询
            chat = AIChat.objects.get(id=chat_id, user_id=request.user_id)
            
            data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
            title = data.get('title')
            
            if title:
                chat.title = title
                chat.save()
            
            return HertzResponse.success(message='更新成功')
        except AIChat.DoesNotExist:
            return HertzResponse.not_found(message='聊天不存在或无权访问')


class AIChatDeleteView(GenericAPIView):
    """
    删除AI聊天接口
    """
    # 使用AuthMiddleware进行认证，不使用DRF权限类
    permission_classes = [AllowAny]
    serializer_class = AIChatDeleteSerializer
    
    @extend_schema(
        operation_id='ai_chat_delete',
        summary='删除AI聊天',
        description='删除指定的AI聊天会话',
        request=AIChatDeleteSerializer,
        responses={
            200: OpenApiResponse(description='成功'),
            400: OpenApiResponse(description='参数错误'),
            401: OpenApiResponse(description='未授权访问'),
        },
        tags=['AI助手']
    )
    @login_required
    @operation_log('delete', 'AI助手', description="删除AI聊天")
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        chat_ids = data.get('chat_ids', [])
        
        if not chat_ids:
            return HertzResponse.validation_error(message='请选择要删除的聊天')
        
        # 查询聊天记录（只查询用户自己的聊天） - 使用user_id而不是user对象
        chats = AIChat.objects.filter(id__in=chat_ids, user_id=request.user_id)
        
        if not chats.exists():
            return HertzResponse.not_found(message='所选聊天不存在或无权删除')
        
        # 删除消息和聊天记录
        for chat in chats:
            AIChatMessage.objects.filter(chat=chat).delete()
        
        deleted_count = chats.delete()[0]
        return HertzResponse.success(message=f'成功删除{deleted_count}个聊天')


class AIChatSendMessageView(GenericAPIView):
    """
    发送AI聊天消息接口
    """
    # 使用AuthMiddleware进行认证，不使用DRF权限类
    permission_classes = [AllowAny]
    serializer_class = ChatRequestSerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ollama_client = OllamaClient()
        self.model_name = getattr(settings, "AI_MODEL_NAME", "deepseek-r1:1.5b")
    
    @extend_schema(
        operation_id='ai_chat_send_message',
        summary='发送AI聊天消息',
        description='向指定的AI聊天会话发送消息并获取AI回复',
        request=ChatRequestSerializer,
        responses={
            200: OpenApiResponse(response=AIChatMessageSerializer, description='成功'),
            400: OpenApiResponse(description='参数错误'),
            401: OpenApiResponse(description='未授权访问'),
            404: OpenApiResponse(description='聊天不存在'),
        },
        tags=['AI助手']
    )
    @login_required
    @operation_log('create', 'AI助手', description="发送AI聊天消息")
    def post(self, request, chat_id, *args, **kwargs):
        try:
            # 检查聊天是否存在且属于当前用户 - 使用user_id而不是user对象
            chat = AIChat.objects.get(id=chat_id, user_id=request.user_id)
            
            # 获取请求数据
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return HertzResponse.validation_error(message='参数验证失败', errors=serializer.errors)
            
            content = serializer.validated_data['content']
            
            # 保存用户消息
            user_message = AIChatMessage.objects.create(
                chat=chat,
                role='user',
                content=content
            )
            
            messages = []
            chat_messages = AIChatMessage.objects.filter(chat=chat).order_by('created_at')
            for msg in chat_messages:
                messages.append({'role': msg.role, 'content': msg.content})

            def _tokens(text):
                return [t for t in ''.join([c.lower() if c.isalnum() else ' ' for c in text]).split() if t]
            def _encode(text, n_features=512):
                vec = np.zeros(n_features, dtype=float)
                for tok in _tokens(text):
                    idx = (hash(tok) % n_features)
                    vec[idx] += 1.0
                norm = np.linalg.norm(vec) or 1.0
                return (vec / norm).astype(float).tolist()
            def _sim(a, b):
                return float(np.dot(np.array(a, dtype=float), np.array(b, dtype=float)))

            q_emb = _encode(content)
            kb_chunks = KBChunk.objects.filter(item__user_id=request.user_id)
            scored = []
            for ch in kb_chunks:
                s = _sim(q_emb, ch.embedding)
                scored.append((s, ch))
            scored.sort(key=lambda x: x[0], reverse=True)
            contexts = [c.text for _, c in scored[:5]]
            graph_ctx = []
            tokens = _tokens(content)
            seen = set()
            for t in tokens:
                if t in seen or len(t) < 2:
                    continue
                seen.add(t)
                ents = KBEntity.objects.filter(name__icontains=t).order_by('id')[:2]
                for e in ents:
                    graph_ctx.append(f"{e.name} ({e.type}) {json.dumps(e.properties, ensure_ascii=False)}")
                    rels = KBRelation.objects.filter(source=e).select_related('target').order_by('id')[:3]
                    for r in rels:
                        graph_ctx.append(f"{e.name} -[{r.relation_type}]-> {r.target.name}")
            if contexts:
                ctx_block = "\n\n".join([f"[片段{i+1}]\n{t}" for i, t in enumerate(contexts)])
                if graph_ctx:
                    graph_block = "\n".join(graph_ctx)
                    ctx_block = ctx_block + "\n\n[图谱]\n" + graph_block
                system_prompt = "你是编程助手。结合提供的片段，简洁准确回答用户消息。无法回答时明确说明。"
                messages.insert(0, {'role': 'system', 'content': system_prompt})
                messages.append({'role': 'user', 'content': f"上下文:\n{ctx_block}\n\n问题: {content}"})
            
            # 调用AI模型生成回复
            try:
                # 为了简化实现，这里使用同步方式调用Ollama
                # 实际生产环境可以考虑使用异步任务队列处理
                ai_response = self.ollama_client.chat_completion(
                    model=self.model_name,
                    messages=messages
                )
                
                # 保存AI回复
                ai_message = AIChatMessage.objects.create(
                    chat=chat,
                    role='assistant',
                    content=ai_response
                )
                
                # 更新对话时间
                chat.save()  # 触发updated_at自动更新
                
                return HertzResponse.success(data={
                    'user_message': {
                        'id': user_message.id,
                        'role': user_message.role,
                        'content': user_message.content,
                        'created_at': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    'ai_message': {
                        'id': ai_message.id,
                        'role': ai_message.role,
                        'content': ai_message.content,
                        'created_at': ai_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            except Exception as e:
                # 如果AI生成失败，仍然保存用户消息，但返回错误
                return HertzResponse.error(message=f'AI回复生成失败：{str(e)}')
            
        except AIChat.DoesNotExist:
            return HertzResponse.not_found(message='聊天不存在或无权访问')
