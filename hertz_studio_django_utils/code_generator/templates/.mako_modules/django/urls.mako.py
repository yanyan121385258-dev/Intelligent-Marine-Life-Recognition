# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1760498624.445131
_enable_loop = True
_template_filename = 'C:/2025.8/project/9/moban/hertz_server_django/hertz_studio_django_utils/code_generator/templates/django/urls.mako'
_template_uri = 'django/urls.mako'
_source_encoding = 'utf-8'
_exports = []



from datetime import datetime


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        app_name = context.get('app_name', UNDEFINED)
        operations = context.get('operations', UNDEFINED)
        model_name = context.get('model_name', UNDEFINED)
        prefix = context.get('prefix', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('"""\nDjango URL配置模板\n"""\n')
        __M_writer('\n')

# 生成操作列表
        operations_list = operations or ['create', 'get', 'update', 'delete', 'list']
        snake_model_name = model_name.lower()
        resource_name = snake_model_name
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['operations_list','resource_name','snake_model_name'] if __M_key in __M_locals_builtin_stored]))
        __M_writer("\nfrom django.urls import path\nfrom . import views\n\napp_name = '")
        __M_writer(str(app_name or snake_model_name))
        __M_writer("'\n\nurlpatterns = [\n")
        if 'create' in operations_list:
            __M_writer('    # 创建')
            __M_writer(str(model_name))
            __M_writer("\n    path('', views.create_")
            __M_writer(str(snake_model_name))
            __M_writer(", name='create_")
            __M_writer(str(snake_model_name))
            __M_writer("'),\n")
        __M_writer('    \n')
        if 'list' in operations_list:
            __M_writer('    # 获取')
            __M_writer(str(model_name))
            __M_writer("列表\n    path('list/', views.list_")
            __M_writer(str(snake_model_name))
            __M_writer(", name='list_")
            __M_writer(str(snake_model_name))
            __M_writer("'),\n")
        __M_writer('    \n')
        if 'get' in operations_list:
            __M_writer('    # 获取')
            __M_writer(str(model_name))
            __M_writer("详情\n    path('<int:")
            __M_writer(str(snake_model_name))
            __M_writer("_id>/', views.get_")
            __M_writer(str(snake_model_name))
            __M_writer(", name='get_")
            __M_writer(str(snake_model_name))
            __M_writer("'),\n")
        __M_writer('    \n')
        if 'update' in operations_list:
            __M_writer('    # 更新')
            __M_writer(str(model_name))
            __M_writer("\n    path('<int:")
            __M_writer(str(snake_model_name))
            __M_writer("_id>/update/', views.update_")
            __M_writer(str(snake_model_name))
            __M_writer(", name='update_")
            __M_writer(str(snake_model_name))
            __M_writer("'),\n")
        __M_writer('    \n')
        if 'delete' in operations_list:
            __M_writer('    # 删除')
            __M_writer(str(model_name))
            __M_writer("\n    path('<int:")
            __M_writer(str(snake_model_name))
            __M_writer("_id>/delete/', views.delete_")
            __M_writer(str(snake_model_name))
            __M_writer(", name='delete_")
            __M_writer(str(snake_model_name))
            __M_writer("'),\n")
        __M_writer(']\n\n# RESTful风格的URL配置（可选）\nrestful_urlpatterns = [\n')
        if 'create' in operations_list or 'list' in operations_list:
            __M_writer('    # POST: 创建')
            __M_writer(str(model_name))
            __M_writer(', GET: 获取')
            __M_writer(str(model_name))
            __M_writer("列表\n    path('")
            __M_writer(str(prefix))
            __M_writer(str(resource_name))
            __M_writer("/', views.")
            __M_writer(str('create_' + snake_model_name if 'create' in operations_list else 'list_' + snake_model_name))
            __M_writer(", name='")
            __M_writer(str(snake_model_name))
            __M_writer("_collection'),\n")
        __M_writer('    \n')
        if 'get' in operations_list or 'update' in operations_list or 'delete' in operations_list:
            __M_writer("    # GET: 获取详情, PUT/PATCH: 更新, DELETE: 删除\n    path('")
            __M_writer(str(prefix))
            __M_writer(str(resource_name))
            __M_writer('/<int:')
            __M_writer(str(snake_model_name))
            __M_writer("_id>/', views.update_")
            __M_writer(str(snake_model_name))
            __M_writer(", name='")
            __M_writer(str(snake_model_name))
            __M_writer("_detail'),\n")
        __M_writer(']')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "C:/2025.8/project/9/moban/hertz_server_django/hertz_studio_django_utils/code_generator/templates/django/urls.mako", "uri": "django/urls.mako", "source_encoding": "utf-8", "line_map": {"16": 4, "17": 5, "18": 6, "19": 7, "20": 0, "29": 1, "30": 6, "31": 7, "32": 8, "33": 9, "34": 10, "35": 11, "36": 12, "37": 13, "40": 12, "41": 16, "42": 16, "43": 19, "44": 20, "45": 20, "46": 20, "47": 21, "48": 21, "49": 21, "50": 21, "51": 23, "52": 24, "53": 25, "54": 25, "55": 25, "56": 26, "57": 26, "58": 26, "59": 26, "60": 28, "61": 29, "62": 30, "63": 30, "64": 30, "65": 31, "66": 31, "67": 31, "68": 31, "69": 31, "70": 31, "71": 33, "72": 34, "73": 35, "74": 35, "75": 35, "76": 36, "77": 36, "78": 36, "79": 36, "80": 36, "81": 36, "82": 38, "83": 39, "84": 40, "85": 40, "86": 40, "87": 41, "88": 41, "89": 41, "90": 41, "91": 41, "92": 41, "93": 43, "94": 47, "95": 48, "96": 48, "97": 48, "98": 48, "99": 48, "100": 49, "101": 49, "102": 49, "103": 49, "104": 49, "105": 49, "106": 49, "107": 51, "108": 52, "109": 53, "110": 54, "111": 54, "112": 54, "113": 54, "114": 54, "115": 54, "116": 54, "117": 54, "118": 54, "119": 56, "125": 119}}
__M_END_METADATA
"""
