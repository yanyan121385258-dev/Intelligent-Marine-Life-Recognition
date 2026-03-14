# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1760498624.4341366
_enable_loop = True
_template_filename = 'C:/2025.8/project/9/moban/hertz_server_django/hertz_studio_django_utils/code_generator/templates/django/views.mako'
_template_uri = 'django/views.mako'
_source_encoding = 'utf-8'
_exports = []



from datetime import datetime


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        operations = context.get('operations', UNDEFINED)
        pagination = context.get('pagination', UNDEFINED)
        isinstance = context.get('isinstance', UNDEFINED)
        permissions = context.get('permissions', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        ordering = context.get('ordering', UNDEFINED)
        model_name = context.get('model_name', UNDEFINED)
        search_fields = context.get('search_fields', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('"""\nDjango视图模板\n"""\n')
        __M_writer('\n')

# 生成操作列表
        operations_list = operations or ['create', 'get', 'update', 'delete', 'list']
        permissions_list = permissions or []
        snake_model_name = model_name.lower()
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['operations_list','snake_model_name','permissions_list'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\nfrom rest_framework.decorators import api_view\nfrom rest_framework.response import Response\nfrom rest_framework import status\nfrom drf_spectacular.utils import extend_schema, OpenApiResponse\nfrom django.core.paginator import Paginator\nfrom django.db.models import Q\n\nfrom .models import ')
        __M_writer(str(model_name))
        __M_writer('\nfrom .serializers import (\n    ')
        __M_writer(str(model_name))
        __M_writer('Serializer,\n    ')
        __M_writer(str(model_name))
        __M_writer('CreateSerializer,\n    ')
        __M_writer(str(model_name))
        __M_writer('UpdateSerializer,\n    ')
        __M_writer(str(model_name))
        __M_writer('ListSerializer\n)\nfrom hertz_studio_django_utils.responses import HertzResponse\n')
        if permissions_list:
            __M_writer('from hertz_studio_django_auth.utils.decorators import login_required, permission_required\n')
        __M_writer('\n\n')
        if 'create' in operations_list:
            __M_writer("@extend_schema(\n    operation_id='create_")
            __M_writer(str(snake_model_name))
            __M_writer("',\n    summary='创建")
            __M_writer(str(model_name))
            __M_writer("',\n    description='创建新的")
            __M_writer(str(model_name))
            __M_writer("实例',\n    request=")
            __M_writer(str(model_name))
            __M_writer('CreateSerializer,\n    responses={\n        201: OpenApiResponse(response=')
            __M_writer(str(model_name))
            __M_writer("Serializer, description='创建成功'),\n        400: OpenApiResponse(description='参数错误'),\n    },\n    tags=['")
            __M_writer(str(model_name))
            __M_writer("']\n)\n@api_view(['POST'])\n")
            if 'create' in permissions_list:

    # 获取权限代码，如果permissions_list是字典，则获取对应的权限代码
                if isinstance(permissions_list, dict) and 'create' in permissions_list:
                    permission_code = permissions_list['create']
                else:
                    permission_code = f'{snake_model_name}:create'
                
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['permission_code'] if __M_key in __M_locals_builtin_stored]))
                __M_writer("\n@permission_required('")
                __M_writer(str(permission_code))
                __M_writer("')\n")
            __M_writer('def create_')
            __M_writer(str(snake_model_name))
            __M_writer('(request):\n    """\n    创建')
            __M_writer(str(model_name))
            __M_writer('\n    \n    创建时间: ')
            __M_writer(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            __M_writer('\n    """\n    try:\n        serializer = ')
            __M_writer(str(model_name))
            __M_writer('CreateSerializer(data=request.data)\n        if serializer.is_valid():\n            instance = serializer.save()\n            response_serializer = ')
            __M_writer(str(model_name))
            __M_writer("Serializer(instance)\n            return HertzResponse.success(\n                data=response_serializer.data,\n                message='")
            __M_writer(str(model_name))
            __M_writer("创建成功'\n            )\n        return HertzResponse.validation_error(\n            message='参数验证失败',\n            errors=serializer.errors\n        )\n    except Exception as e:\n        return HertzResponse.error(\n            message='创建")
            __M_writer(str(model_name))
            __M_writer("失败',\n            error=str(e)\n        )\n\n\n")
        if 'get' in operations_list or 'retrieve' in operations_list:
            __M_writer("@extend_schema(\n    operation_id='get_")
            __M_writer(str(snake_model_name))
            __M_writer("',\n    summary='获取")
            __M_writer(str(model_name))
            __M_writer("详情',\n    description='根据ID获取")
            __M_writer(str(model_name))
            __M_writer("详情',\n    responses={\n        200: OpenApiResponse(response=")
            __M_writer(str(model_name))
            __M_writer("Serializer, description='获取成功'),\n        404: OpenApiResponse(description='")
            __M_writer(str(model_name))
            __M_writer("不存在'),\n    },\n    tags=['")
            __M_writer(str(model_name))
            __M_writer("']\n)\n@api_view(['GET'])\n")
            if 'get' in permissions_list or 'retrieve' in permissions_list:

    # 获取权限代码
                if isinstance(permissions_list, dict):
                    permission_code = permissions_list.get('get') or permissions_list.get('retrieve') or f'{snake_model_name}:query'
                else:
                    permission_code = f'{snake_model_name}:query'
                
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['permission_code'] if __M_key in __M_locals_builtin_stored]))
                __M_writer("\n@permission_required('")
                __M_writer(str(permission_code))
                __M_writer("')\n")
            __M_writer('def get_')
            __M_writer(str(snake_model_name))
            __M_writer('(request, ')
            __M_writer(str(snake_model_name))
            __M_writer('_id):\n    """\n    获取')
            __M_writer(str(model_name))
            __M_writer('详情\n    \n    Args:\n        ')
            __M_writer(str(snake_model_name))
            __M_writer('_id: ')
            __M_writer(str(model_name))
            __M_writer('ID\n    """\n    try:\n        instance = ')
            __M_writer(str(model_name))
            __M_writer('.get_by_id(')
            __M_writer(str(snake_model_name))
            __M_writer("_id)\n        if not instance:\n            return HertzResponse.not_found(message='")
            __M_writer(str(model_name))
            __M_writer("不存在')\n            \n        serializer = ")
            __M_writer(str(model_name))
            __M_writer("Serializer(instance)\n        return HertzResponse.success(\n            data=serializer.data,\n            message='获取")
            __M_writer(str(model_name))
            __M_writer("详情成功'\n        )\n    except Exception as e:\n        return HertzResponse.error(\n            message='获取")
            __M_writer(str(model_name))
            __M_writer("详情失败',\n            error=str(e)\n        )\n\n\n")
        if 'update' in operations_list:
            __M_writer("@extend_schema(\n    operation_id='update_")
            __M_writer(str(snake_model_name))
            __M_writer("',\n    summary='更新")
            __M_writer(str(model_name))
            __M_writer("',\n    description='根据ID更新")
            __M_writer(str(model_name))
            __M_writer("信息',\n    request=")
            __M_writer(str(model_name))
            __M_writer('UpdateSerializer,\n    responses={\n        200: OpenApiResponse(response=')
            __M_writer(str(model_name))
            __M_writer("Serializer, description='更新成功'),\n        404: OpenApiResponse(description='")
            __M_writer(str(model_name))
            __M_writer("不存在'),\n        400: OpenApiResponse(description='参数错误'),\n    },\n    tags=['")
            __M_writer(str(model_name))
            __M_writer("']\n)\n@api_view(['PUT', 'PATCH'])\n")
            if 'update' in permissions_list:

    # 获取权限代码
                if isinstance(permissions_list, dict) and 'update' in permissions_list:
                    permission_code = permissions_list['update']
                else:
                    permission_code = f'{snake_model_name}:update'
                
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['permission_code'] if __M_key in __M_locals_builtin_stored]))
                __M_writer("\n@permission_required('")
                __M_writer(str(permission_code))
                __M_writer("')\n")
            __M_writer('def update_')
            __M_writer(str(snake_model_name))
            __M_writer('(request, ')
            __M_writer(str(snake_model_name))
            __M_writer('_id):\n    """\n    更新')
            __M_writer(str(model_name))
            __M_writer('\n    \n    Args:\n        ')
            __M_writer(str(snake_model_name))
            __M_writer('_id: ')
            __M_writer(str(model_name))
            __M_writer('ID\n    """\n    try:\n        instance = ')
            __M_writer(str(model_name))
            __M_writer('.get_by_id(')
            __M_writer(str(snake_model_name))
            __M_writer("_id)\n        if not instance:\n            return HertzResponse.not_found(message='")
            __M_writer(str(model_name))
            __M_writer("不存在')\n            \n        partial = request.method == 'PATCH'\n        serializer = ")
            __M_writer(str(model_name))
            __M_writer('UpdateSerializer(\n            instance, \n            data=request.data, \n            partial=partial\n        )\n        \n        if serializer.is_valid():\n            updated_instance = serializer.save()\n            response_serializer = ')
            __M_writer(str(model_name))
            __M_writer("Serializer(updated_instance)\n            return HertzResponse.success(\n                data=response_serializer.data,\n                message='")
            __M_writer(str(model_name))
            __M_writer("更新成功'\n            )\n        return HertzResponse.validation_error(\n            message='参数验证失败',\n            errors=serializer.errors\n        )\n    except Exception as e:\n        return HertzResponse.error(\n            message='更新")
            __M_writer(str(model_name))
            __M_writer("失败',\n            error=str(e)\n        )\n\n\n")
        if 'delete' in operations_list:
            __M_writer("@extend_schema(\n    operation_id='delete_")
            __M_writer(str(snake_model_name))
            __M_writer("',\n    summary='删除")
            __M_writer(str(model_name))
            __M_writer("',\n    description='根据ID删除")
            __M_writer(str(model_name))
            __M_writer("',\n    responses={\n        200: OpenApiResponse(description='删除成功'),\n        404: OpenApiResponse(description='")
            __M_writer(str(model_name))
            __M_writer("不存在'),\n    },\n    tags=['")
            __M_writer(str(model_name))
            __M_writer("']\n)\n@api_view(['DELETE'])\n")
            if 'delete' in permissions_list:

    # 获取权限代码
                if isinstance(permissions_list, dict) and 'delete' in permissions_list:
                    permission_code = permissions_list['delete']
                else:
                    permission_code = f'{snake_model_name}:delete'
                
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['permission_code'] if __M_key in __M_locals_builtin_stored]))
                __M_writer("\n@permission_required('")
                __M_writer(str(permission_code))
                __M_writer("')\n")
            __M_writer('def delete_')
            __M_writer(str(snake_model_name))
            __M_writer('(request, ')
            __M_writer(str(snake_model_name))
            __M_writer('_id):\n    """\n    删除')
            __M_writer(str(model_name))
            __M_writer('\n    \n    Args:\n        ')
            __M_writer(str(snake_model_name))
            __M_writer('_id: ')
            __M_writer(str(model_name))
            __M_writer('ID\n    """\n    try:\n        instance = ')
            __M_writer(str(model_name))
            __M_writer('.get_by_id(')
            __M_writer(str(snake_model_name))
            __M_writer("_id)\n        if not instance:\n            return HertzResponse.not_found(message='")
            __M_writer(str(model_name))
            __M_writer("不存在')\n            \n        instance.delete()\n        return HertzResponse.success(message='")
            __M_writer(str(model_name))
            __M_writer("删除成功')\n    except Exception as e:\n        return HertzResponse.error(\n            message='删除")
            __M_writer(str(model_name))
            __M_writer("失败',\n            error=str(e)\n        )\n\n\n")
        if 'list' in operations_list:
            __M_writer("@extend_schema(\n    operation_id='list_")
            __M_writer(str(snake_model_name))
            __M_writer("',\n    summary='获取")
            __M_writer(str(model_name))
            __M_writer("列表',\n    description='分页获取")
            __M_writer(str(model_name))
            __M_writer("列表',\n    responses={\n        200: OpenApiResponse(response=")
            __M_writer(str(model_name))
            __M_writer("ListSerializer, description='获取成功'),\n    },\n    tags=['")
            __M_writer(str(model_name))
            __M_writer("']\n)\n@api_view(['GET'])\n")
            if 'list' in permissions_list:

    # 获取权限代码
                if isinstance(permissions_list, dict) and 'list' in permissions_list:
                    permission_code = permissions_list['list']
                else:
                    permission_code = f'{snake_model_name}:list'
                
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['permission_code'] if __M_key in __M_locals_builtin_stored]))
                __M_writer("\n@permission_required('")
                __M_writer(str(permission_code))
                __M_writer("')\n")
            __M_writer('def list_')
            __M_writer(str(snake_model_name))
            __M_writer('(request):\n    """\n    获取')
            __M_writer(str(model_name))
            __M_writer('列表\n    \n    支持分页、搜索和排序\n    """\n    try:\n        queryset = ')
            __M_writer(str(model_name))
            __M_writer(".objects.all()\n        \n        # 搜索功能\n        search = request.GET.get('search', '')\n        if search:\n")
            if search_fields:
                __M_writer('            search_q = Q()\n')
                for field in search_fields:
                    __M_writer('            search_q |= Q(')
                    __M_writer(str(field))
                    __M_writer('__icontains=search)\n')
                __M_writer('            queryset = queryset.filter(search_q)\n')
            else:
                __M_writer('            # 默认搜索字段，可根据需要调整\n            queryset = queryset.filter(\n                Q(id__icontains=search)\n            )\n')
            __M_writer("        \n        # 排序功能\n        ordering = request.GET.get('ordering', '-created_at')\n")
            if ordering:
                __M_writer('        valid_orderings = [')
                __M_writer(str(', '.join([f"'{field}'" for field in ordering] + [f"'-{field}'" for field in ordering])))
                __M_writer(']\n')
            else:
                __M_writer("        valid_orderings = ['created_at', '-created_at', 'updated_at', '-updated_at']\n")
            __M_writer('        if ordering in valid_orderings:\n            queryset = queryset.order_by(ordering)\n        \n        # 分页功能\n')
            if pagination:
                __M_writer("        page = int(request.GET.get('page', 1))\n        page_size = int(request.GET.get('page_size', 20))\n        paginator = Paginator(queryset, page_size)\n        page_obj = paginator.get_page(page)\n        \n        serializer = ")
                __M_writer(str(model_name))
                __M_writer("ListSerializer(page_obj.object_list, many=True)\n        \n        return HertzResponse.success(\n            data={\n                'results': serializer.data,\n                'pagination': {\n                    'page': page,\n                    'page_size': page_size,\n                    'total_pages': paginator.num_pages,\n                    'total_count': paginator.count,\n                    'has_next': page_obj.has_next(),\n                    'has_previous': page_obj.has_previous(),\n                }\n            },\n            message='获取")
                __M_writer(str(model_name))
                __M_writer("列表成功'\n        )\n")
            else:
                __M_writer('        serializer = ')
                __M_writer(str(model_name))
                __M_writer("ListSerializer(queryset, many=True)\n        return HertzResponse.success(\n            data=serializer.data,\n            message='获取")
                __M_writer(str(model_name))
                __M_writer("列表成功'\n        )\n")
            __M_writer("    except Exception as e:\n        return HertzResponse.error(\n            message='获取")
            __M_writer(str(model_name))
            __M_writer("列表失败',\n            error=str(e)\n        )\n\n\n")
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "C:/2025.8/project/9/moban/hertz_server_django/hertz_studio_django_utils/code_generator/templates/django/views.mako", "uri": "django/views.mako", "source_encoding": "utf-8", "line_map": {"16": 4, "17": 5, "18": 6, "19": 7, "20": 0, "33": 1, "34": 6, "35": 7, "36": 8, "37": 9, "38": 10, "39": 11, "40": 12, "41": 13, "44": 12, "45": 20, "46": 20, "47": 22, "48": 22, "49": 23, "50": 23, "51": 24, "52": 24, "53": 25, "54": 25, "55": 28, "56": 29, "57": 31, "58": 33, "59": 34, "60": 35, "61": 35, "62": 36, "63": 36, "64": 37, "65": 37, "66": 38, "67": 38, "68": 40, "69": 40, "70": 43, "71": 43, "72": 46, "73": 47, "74": 48, "75": 49, "76": 50, "77": 51, "78": 52, "79": 53, "80": 54, "83": 53, "84": 54, "85": 54, "86": 56, "87": 56, "88": 56, "89": 58, "90": 58, "91": 60, "92": 60, "93": 63, "94": 63, "95": 66, "96": 66, "97": 69, "98": 69, "99": 77, "100": 77, "101": 83, "102": 84, "103": 85, "104": 85, "105": 86, "106": 86, "107": 87, "108": 87, "109": 89, "110": 89, "111": 90, "112": 90, "113": 92, "114": 92, "115": 95, "116": 96, "117": 97, "118": 98, "119": 99, "120": 100, "121": 101, "122": 102, "123": 103, "126": 102, "127": 103, "128": 103, "129": 105, "130": 105, "131": 105, "132": 105, "133": 105, "134": 107, "135": 107, "136": 110, "137": 110, "138": 110, "139": 110, "140": 113, "141": 113, "142": 113, "143": 113, "144": 115, "145": 115, "146": 117, "147": 117, "148": 120, "149": 120, "150": 124, "151": 124, "152": 130, "153": 131, "154": 132, "155": 132, "156": 133, "157": 133, "158": 134, "159": 134, "160": 135, "161": 135, "162": 137, "163": 137, "164": 138, "165": 138, "166": 141, "167": 141, "168": 144, "169": 145, "170": 146, "171": 147, "172": 148, "173": 149, "174": 150, "175": 151, "176": 152, "179": 151, "180": 152, "181": 152, "182": 154, "183": 154, "184": 154, "185": 154, "186": 154, "187": 156, "188": 156, "189": 159, "190": 159, "191": 159, "192": 159, "193": 162, "194": 162, "195": 162, "196": 162, "197": 164, "198": 164, "199": 167, "200": 167, "201": 175, "202": 175, "203": 178, "204": 178, "205": 186, "206": 186, "207": 192, "208": 193, "209": 194, "210": 194, "211": 195, "212": 195, "213": 196, "214": 196, "215": 199, "216": 199, "217": 201, "218": 201, "219": 204, "220": 205, "221": 206, "222": 207, "223": 208, "224": 209, "225": 210, "226": 211, "227": 212, "230": 211, "231": 212, "232": 212, "233": 214, "234": 214, "235": 214, "236": 214, "237": 214, "238": 216, "239": 216, "240": 219, "241": 219, "242": 219, "243": 219, "244": 222, "245": 222, "246": 222, "247": 222, "248": 224, "249": 224, "250": 227, "251": 227, "252": 230, "253": 230, "254": 236, "255": 237, "256": 238, "257": 238, "258": 239, "259": 239, "260": 240, "261": 240, "262": 242, "263": 242, "264": 244, "265": 244, "266": 247, "267": 248, "268": 249, "269": 250, "270": 251, "271": 252, "272": 253, "273": 254, "274": 255, "277": 254, "278": 255, "279": 255, "280": 257, "281": 257, "282": 257, "283": 259, "284": 259, "285": 264, "286": 264, "287": 269, "288": 270, "289": 271, "290": 272, "291": 272, "292": 272, "293": 274, "294": 275, "295": 276, "296": 281, "297": 284, "298": 285, "299": 285, "300": 285, "301": 286, "302": 287, "303": 289, "304": 293, "305": 294, "306": 299, "307": 299, "308": 313, "309": 313, "310": 315, "311": 316, "312": 316, "313": 316, "314": 319, "315": 319, "316": 322, "317": 324, "318": 324, "324": 318}}
__M_END_METADATA
"""
