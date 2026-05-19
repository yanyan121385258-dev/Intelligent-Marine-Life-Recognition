import json
import numpy as np
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiResponse
from studio_django_auth.utils.decorators import login_required
from studio_django_utils.responses.HertzResponse import HertzResponse
from studio_django_utils.ollama.ollama_client import OllamaClient
from django.conf import settings
from .models import KBItem, KBChunk, KBEntity, KBRelation
from .serializers import (
    KBItemCreateSerializer,
    KBItemSerializer,
    KBChunkSerializer,
    KBEntitySerializer,
    KBRelationSerializer,
)


def _chunk_text(text, max_len=500):
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks


class _Embedder:
    def __init__(self, n_features=512):
        self.n_features = int(n_features)

    def _tokens(self, text):
        return [t for t in ''.join([c.lower() if c.isalnum() else ' ' for c in text]).split() if t]

    def encode(self, text):
        vec = np.zeros(self.n_features, dtype=float)
        for tok in self._tokens(text):
            idx = (hash(tok) % self.n_features)
            vec[idx] += 1.0
        norm = np.linalg.norm(vec) or 1.0
        return (vec / norm).astype(float).tolist()

    def similarity(self, a, b):
        return float(np.dot(np.array(a, dtype=float), np.array(b, dtype=float)))

ollama_client = OllamaClient()
model_name = getattr(settings, "AI_MODEL_NAME", "deepseek-r1:1.5b")

DOMAIN_ENTITY_TYPES = [
    "Language", "Framework", "Library", "Tool", "Concept", "API", "Function", "Class", "File", "Repository", "Version"
]
DOMAIN_RELATION_TYPES = [
    "depends_on", "uses", "implements", "extends", "calls", "imports", "defines", "belongs_to", "version_of"
]

def _get_request_data(request):
    ct = request.META.get('CONTENT_TYPE', '')
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        if 'application/json' in ct:
            try:
                return json.loads(request.body)
            except Exception:
                return {}
        data = request.POST.dict()
        if not data:
            data = request.GET.dict()
        return data
    return request.GET.dict()

def _fallback_extract_programming(text):
    ents = []
    rels = []
    t = text or ''
    try:
        import re
        patterns = [
            (r"\bprint\(", {"name": "print", "type": "Function", "lang": "Python"}, {"relation_type": "belongs_to", "target": "Python"}),
            (r"console\.log\(", {"name": "console.log", "type": "Function", "lang": "JavaScript"}, {"relation_type": "belongs_to", "target": "JavaScript"}),
            (r"\bprintf\(", {"name": "printf", "type": "Function", "lang": "C"}, {"relation_type": "belongs_to", "target": "C"}),
            (r"System\.out\.println\(", {"name": "println", "type": "Function", "lang": "Java"}, {"relation_type": "belongs_to", "target": "Java"}),
            (r"fmt\.Println\(", {"name": "Println", "type": "Function", "lang": "Go"}, {"relation_type": "belongs_to", "target": "Go"}),
        ]
        for pat, func_info, rel_info in patterns:
            if re.search(pat, t):
                ents.append({"name": func_info["name"], "type": func_info["type"], "properties": {"language": func_info["lang"]}})
                ents.append({"name": rel_info["target"], "type": "Language", "properties": {}})
                rels.append({"source": func_info["name"], "target": rel_info["target"], "relation_type": rel_info["relation_type"], "properties": {}})
    except Exception:
        pass
    return {"entities": ents, "relations": rels}

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def kb_item_create(request):
    data = _get_request_data(request)
    if request.FILES.get('file'):
        data['file'] = request.FILES.get('file')
    serializer = KBItemCreateSerializer(data=data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(errors=serializer.errors)
    item = KBItem.objects.create(
        user_id=request.user_id,
        title=serializer.validated_data.get('title'),
        modality=serializer.validated_data.get('modality', 'text'),
        source_type=serializer.validated_data.get('source_type', 'text'),
        content=serializer.validated_data.get('content'),
        file=serializer.validated_data.get('file'),
        metadata=serializer.validated_data.get('metadata', {}),
    )
    content = item.content or ''
    embedder = _Embedder()
    chunks = _chunk_text(content)
    created = 0
    for i, ch in enumerate(chunks):
        emb = embedder.encode(ch)
        KBChunk.objects.create(item=item, index=i, text=ch, embedding=emb)
        created += 1
    resp_data = KBItemSerializer(item).data
    resp_data.update({'created_chunk_count': created})
    auto = bool(data.get('auto_graph_extract', False))
    if auto:
        subreq = request
        subreq._body = json.dumps({"item_id": item.id, "overwrite": False}).encode('utf-8')
        subresp = kb_graph_extract(subreq)
        try:
            payload = json.loads(subresp.content.decode('utf-8'))
            resp_data['graph_extract'] = payload.get('data')
        except Exception:
            resp_data['graph_extract'] = None
    return HertzResponse.success(data=resp_data)


@login_required
@require_http_methods(["GET"])
def kb_item_list(request):
    query = request.GET.get('query', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    q = Q(user_id=request.user_id)
    if query:
        q &= Q(title__icontains=query)
    items = KBItem.objects.filter(q).order_by('-updated_at')
    paginator = Paginator(items, page_size)
    page_obj = paginator.get_page(page)
    return HertzResponse.success(data={
        'total': paginator.count,
        'page': page,
        'page_size': page_size,
        'list': [KBItemSerializer(i).data for i in page_obj]
    })


@login_required
@require_http_methods(["GET"])
def kb_search(request):
    q = request.GET.get('q', '')
    k = int(request.GET.get('k', 5))
    embedder = _Embedder()
    q_emb = embedder.encode(q)
    chunks = KBChunk.objects.filter(item__user_id=request.user_id)
    scored = []
    for ch in chunks:
        s = embedder.similarity(q_emb, ch.embedding)
        scored.append((s, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [KBChunkSerializer(c).data for _, c in scored[:k]]
    return HertzResponse.success(data={'results': top})


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def kb_qa(request):
    data = _get_request_data(request)
    question = data.get('question', '')
    k = int(data.get('k', 5))
    embedder = _Embedder()
    q_emb = embedder.encode(question)
    chunks = KBChunk.objects.filter(item__user_id=request.user_id)
    scored = []
    for ch in chunks:
        s = embedder.similarity(q_emb, ch.embedding)
        scored.append((s, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    contexts = [c.text for _, c in scored[:k]]
    context_block = "\n\n".join([f"[片段{i+1}]\n{t}" for i, t in enumerate(contexts)])
    system_prompt = "你是编程助手。结合提供的片段，简洁准确回答问题。无法回答时明确说明。"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"上下文:\n{context_block}\n\n问题: {question}"},
    ]
    try:
        answer = ollama_client.chat_completion(model=model_name, messages=messages)
        return HertzResponse.success(data={'answer': answer, 'contexts': contexts})
    except Exception as e:
            return HertzResponse.error(message=f'LLM错误: {str(e)}')


@login_required
@require_http_methods(["GET", "POST"])
@csrf_exempt
def kb_entity_list_create(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        q = Q()
        if query:
            q &= Q(name__icontains=query) | Q(type__icontains=query)
        entities = KBEntity.objects.filter(q).order_by('-id')
        paginator = Paginator(entities, page_size)
        page_obj = paginator.get_page(page)
        return HertzResponse.success(data={
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'list': [KBEntitySerializer(e).data for e in page_obj]
        })
    data = _get_request_data(request)
    serializer = KBEntitySerializer(data=data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(errors=serializer.errors)
    entity = serializer.save()
    return HertzResponse.success(data=KBEntitySerializer(entity).data)


@login_required
@require_http_methods(["PUT", "DELETE"])
@csrf_exempt
def kb_entity_update_delete(request, pk):
    try:
        entity = KBEntity.objects.get(id=pk)
    except KBEntity.DoesNotExist:
        return HertzResponse.not_found('实体不存在')
    if request.method == 'PUT':
        data = _get_request_data(request)
        serializer = KBEntitySerializer(entity, data=data, partial=True)
        if not serializer.is_valid():
            return HertzResponse.validation_error(errors=serializer.errors)
        entity = serializer.save()
        return HertzResponse.success(data=KBEntitySerializer(entity).data)
    entity.delete()
    return HertzResponse.success(message='删除成功')



@login_required
@require_http_methods(["GET", "POST"])
@csrf_exempt
def kb_relation_list_create(request):
    if request.method == 'GET':
        source = request.GET.get('source')
        target = request.GET.get('target')
        relation_type = request.GET.get('relation_type')
        q = Q()
        if source:
            q &= Q(source_id=source)
        if target:
            q &= Q(target_id=target)
        if relation_type:
            q &= Q(relation_type__icontains=relation_type)
        relations = KBRelation.objects.filter(q).order_by('-id')
        return HertzResponse.success(data={'list': [KBRelationSerializer(r).data for r in relations]})
    data = _get_request_data(request)
    serializer = KBRelationSerializer(data=data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(errors=serializer.errors)
    relation = serializer.save()
    return HertzResponse.success(data=KBRelationSerializer(relation).data)


@login_required
@require_http_methods(["DELETE"])
@csrf_exempt
def kb_relation_delete(request, pk):
    try:
        relation = KBRelation.objects.get(id=pk)
    except KBRelation.DoesNotExist:
        return HertzResponse.not_found('关系不存在')
    relation.delete()
    return HertzResponse.success(message='删除成功')


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def kb_graph_extract(request):
    data = _get_request_data(request)
    text = data.get('text')
    item_id = data.get('item_id')
    overwrite = bool(data.get('overwrite', False))
    if not text and not item_id:
        return HertzResponse.validation_error(message='需要 text 或 item_id')
    if not text and item_id:
        try:
            item = KBItem.objects.get(id=item_id)
        except KBItem.DoesNotExist:
            return HertzResponse.not_found('条目不存在')
        chunks = KBChunk.objects.filter(item=item).order_by('index')
        text = '\n'.join([c.text for c in chunks])
    schema_desc = {
        "types": DOMAIN_ENTITY_TYPES,
        "relations": DOMAIN_RELATION_TYPES
    }
    prompt = {"role": "system", "content": json.dumps({
        "task": "extract_entities_relations",
        "schema": schema_desc,
        "format": {
            "entities": [{"name": "string", "type": "one_of(types)", "properties": "object"}],
            "relations": [{"source": "entity_name", "target": "entity_name", "relation_type": "one_of(relations)", "properties": "object"}]
        },
        "rules": [
            "only return JSON, no explanations",
            "prefer precise programming domain types",
            "use lowercase keys"
        ]
    })}
    user_msg = {"role": "user", "content": text}
    parsed = {"entities": [], "relations": []}
    try:
        result = ollama_client.chat_completion(model=model_name, messages=[prompt, user_msg], response_format="json")
        try:
            parsed = json.loads(result)
        except Exception:
            if isinstance(result, str) and '{' in result and '}' in result:
                s = result.find('{')
                e = result.rfind('}')
                try:
                    parsed = json.loads(result[s:e+1])
                except Exception:
                    pass
    except Exception:
        pass
    fb = _fallback_extract_programming(text)
    entities = (parsed.get('entities') or []) + fb.get('entities', [])
    relations = (parsed.get('relations') or []) + fb.get('relations', [])
    name_map = {}
    for e in entities:
        name = (e.get('name') or '').strip()
        etype = (e.get('type') or 'Concept').strip()
        props = e.get('properties') or {}
        if not name:
            continue
        if etype not in DOMAIN_ENTITY_TYPES:
            etype = 'Concept'
        obj, created = KBEntity.objects.get_or_create(name=name, type=etype, defaults={"properties": props})
        if not created:
            if overwrite:
                obj.properties = props or {}
            else:
                merged = dict(obj.properties or {})
                merged.update(props or {})
                obj.properties = merged
            obj.save()
        name_map[name] = obj
    saved = 0
    for r in relations:
        sname = r.get('source')
        tname = r.get('target')
        rtype = (r.get('relation_type') or 'depends_on').strip()
        props = r.get('properties') or {}
        if not sname or not tname:
            continue
        src = name_map.get(sname)
        tgt = name_map.get(tname)
        if not src or not tgt:
            continue
        if rtype not in DOMAIN_RELATION_TYPES:
            rtype = 'uses'
        exists = KBRelation.objects.filter(source=src, target=tgt, relation_type=rtype).first()
        if exists:
            if overwrite:
                exists.properties = props or {}
            else:
                merged = dict(exists.properties or {})
                merged.update(props or {})
                exists.properties = merged
            exists.save()
        else:
            KBRelation.objects.create(source=src, target=tgt, relation_type=rtype, properties=props)
            saved += 1
    return HertzResponse.success(data={"entities": len(name_map), "relations": saved})


@extend_schema(operation_id='kb_graph_extract_batch', summary='批量抽取实体与关系', tags=['知识图谱'])
@login_required
@require_http_methods(["POST"])
def kb_graph_extract_batch(request):
    data = _get_request_data(request)
    item_ids = data.get('item_ids') or []
    overwrite = bool(data.get('overwrite', False))
    max_items = int(data.get('max_items', 20))
    items_qs = KBItem.objects.filter(user_id=request.user_id)
    if item_ids:
        items_qs = items_qs.filter(id__in=item_ids)
    items = list(items_qs.order_by('-updated_at')[:max_items])
    total_entities = 0
    total_relations = 0
    for item in items:
        chunks = KBChunk.objects.filter(item=item).order_by('index')
        text = '\n'.join([c.text for c in chunks])
        subreq = request
        subreq_body = json.dumps({"text": text, "overwrite": overwrite}).encode('utf-8')
        subreq._body = subreq_body
        resp = kb_graph_extract(subreq)
        try:
            payload = json.loads(resp.content.decode('utf-8'))
            data = payload.get('data') or {}
            total_entities += int(data.get('entities', 0))
            total_relations += int(data.get('relations', 0))
        except Exception:
            pass
    return HertzResponse.success(data={"entities": total_entities, "relations": total_relations, "processed": len(items)})
