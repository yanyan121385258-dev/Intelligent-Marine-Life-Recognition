# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1760424185.601884
_enable_loop = True
_template_filename = 'C:/2025.8/project/9/moban/server_django/studio_django_utils/code_generator/templates/django/serializers.mako'
_template_uri = 'django/serializers.mako'
_source_encoding = 'utf-8'
_exports = []



from datetime import datetime


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        model_name = context.get('model_name', UNDEFINED)
        fields = context.get('fields', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('"""\nDjango序列化器模板\n"""\n')
        __M_writer('\n')

# 生成字段列表
        all_fields = []
        create_fields_list = []
        update_fields_list = []
        list_fields_list = []
        
        # 处理字段列表
        for field in fields:
            field_name = field['name']
            all_fields.append(field_name)
            
            # 排除自动生成的字段
            if field_name not in ['id', 'created_at', 'updated_at']:
                create_fields_list.append(field_name)
                update_fields_list.append(field_name)
            
            list_fields_list.append(field_name)
        
        # 添加默认字段
        if 'id' not in all_fields:
            all_fields.insert(0, 'id')
        if 'created_at' not in all_fields:
            all_fields.append('created_at')
        if 'updated_at' not in all_fields:
            all_fields.append('updated_at')
        
        # 如果没有指定列表字段，使用所有字段
        if not list_fields_list:
            list_fields_list = all_fields
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['all_fields','field_name','update_fields_list','field','create_fields_list','list_fields_list'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\nfrom rest_framework import serializers\nfrom .models import ')
        __M_writer(str(model_name))
        __M_writer('\n\n\nclass ')
        __M_writer(str(model_name))
        __M_writer('Serializer(serializers.ModelSerializer):\n    """\n    ')
        __M_writer(str(model_name))
        __M_writer('序列化器\n    \n    用于')
        __M_writer(str(model_name))
        __M_writer('模型的序列化和反序列化\n    创建时间: ')
        __M_writer(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        __M_writer('\n    """\n    \n    class Meta:\n        model = ')
        __M_writer(str(model_name))
        __M_writer('\n        fields = [')
        __M_writer(str(', '.join([f"'{field}'" for field in all_fields])))
        __M_writer("]\n        read_only_fields = ['id', 'created_at', 'updated_at']\n        \n")
        for field in fields:
            pass
            if field.get('validators'):
                __M_writer('    def validate_')
                __M_writer(str(field['name']))
                __M_writer('(self, value):\n        """\n        验证')
                __M_writer(str(field['name']))
                __M_writer('字段\n        """\n')
                for validator_name, validator_rule in field['validators'].items():
                    __M_writer('        # ')
                    __M_writer(str(validator_name))
                    __M_writer('验证: ')
                    __M_writer(str(validator_rule))
                    __M_writer('\n')
                __M_writer('        return value\n        \n')
        __M_writer('    def validate(self, attrs):\n        """\n        对象级别的验证\n        """\n        # 在这里添加跨字段验证逻辑\n        return attrs\n        \n    def create(self, validated_data):\n        """\n        创建')
        __M_writer(str(model_name))
        __M_writer('实例\n        """\n        return ')
        __M_writer(str(model_name))
        __M_writer('.objects.create(**validated_data)\n        \n    def update(self, instance, validated_data):\n        """\n        更新')
        __M_writer(str(model_name))
        __M_writer('实例\n        """\n        for attr, value in validated_data.items():\n            setattr(instance, attr, value)\n        instance.save()\n        return instance\n\n\nclass ')
        __M_writer(str(model_name))
        __M_writer('CreateSerializer(serializers.ModelSerializer):\n    """\n    ')
        __M_writer(str(model_name))
        __M_writer('创建序列化器\n    \n    用于创建')
        __M_writer(str(model_name))
        __M_writer('实例\n    """\n    \n    class Meta:\n        model = ')
        __M_writer(str(model_name))
        __M_writer('\n        fields = [')
        __M_writer(str(', '.join([f"'{field}'" for field in create_fields_list])))
        __M_writer(']\n        \n')
        for field in fields:
            pass
            if field['name'] in create_fields_list and field.get('validators'):
                __M_writer('    def validate_')
                __M_writer(str(field['name']))
                __M_writer('(self, value):\n        """\n        验证')
                __M_writer(str(field['name']))
                __M_writer('字段\n        """\n')
                for validator_name, validator_rule in field['validators'].items():
                    __M_writer('        # ')
                    __M_writer(str(validator_name))
                    __M_writer('验证: ')
                    __M_writer(str(validator_rule))
                    __M_writer('\n')
                __M_writer('        return value\n        \n')
        __M_writer('\n\nclass ')
        __M_writer(str(model_name))
        __M_writer('UpdateSerializer(serializers.ModelSerializer):\n    """\n    ')
        __M_writer(str(model_name))
        __M_writer('更新序列化器\n    \n    用于更新')
        __M_writer(str(model_name))
        __M_writer('实例\n    """\n    \n    class Meta:\n        model = ')
        __M_writer(str(model_name))
        __M_writer('\n        fields = [')
        __M_writer(str(', '.join([f"'{field}'" for field in update_fields_list])))
        __M_writer(']\n        \n')
        for field in fields:
            pass
            if field['name'] in update_fields_list and field.get('validators'):
                __M_writer('    def validate_')
                __M_writer(str(field['name']))
                __M_writer('(self, value):\n        """\n        验证')
                __M_writer(str(field['name']))
                __M_writer('字段\n        """\n')
                for validator_name, validator_rule in field['validators'].items():
                    __M_writer('        # ')
                    __M_writer(str(validator_name))
                    __M_writer('验证: ')
                    __M_writer(str(validator_rule))
                    __M_writer('\n')
                __M_writer('        return value\n        \n')
        __M_writer('\n\nclass ')
        __M_writer(str(model_name))
        __M_writer('ListSerializer(serializers.ModelSerializer):\n    """\n    ')
        __M_writer(str(model_name))
        __M_writer('列表序列化器\n    \n    用于列表显示')
        __M_writer(str(model_name))
        __M_writer('实例\n    """\n    \n    class Meta:\n        model = ')
        __M_writer(str(model_name))
        __M_writer('\n        fields = [')
        __M_writer(str(', '.join([f"'{field}'" for field in list_fields_list])))
        __M_writer(']\n        read_only_fields = [')
        __M_writer(str(', '.join([f"'{field}'" for field in list_fields_list])))
        __M_writer(']')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "C:/2025.8/project/9/moban/server_django/studio_django_utils/code_generator/templates/django/serializers.mako", "uri": "django/serializers.mako", "source_encoding": "utf-8", "line_map": {"16": 4, "17": 5, "18": 6, "19": 7, "20": 0, "27": 1, "28": 6, "29": 7, "30": 8, "31": 9, "32": 10, "33": 11, "34": 12, "35": 13, "36": 14, "37": 15, "38": 16, "39": 17, "40": 18, "41": 19, "42": 20, "43": 21, "44": 22, "45": 23, "46": 24, "47": 25, "48": 26, "49": 27, "50": 28, "51": 29, "52": 30, "53": 31, "54": 32, "55": 33, "56": 34, "57": 35, "58": 36, "59": 37, "60": 38, "63": 37, "64": 39, "65": 39, "66": 42, "67": 42, "68": 44, "69": 44, "70": 46, "71": 46, "72": 47, "73": 47, "74": 51, "75": 51, "76": 52, "77": 52, "78": 55, "80": 56, "81": 57, "82": 57, "83": 57, "84": 59, "85": 59, "86": 61, "87": 62, "88": 62, "89": 62, "90": 62, "91": 62, "92": 64, "93": 68, "94": 77, "95": 77, "96": 79, "97": 79, "98": 83, "99": 83, "100": 91, "101": 91, "102": 93, "103": 93, "104": 95, "105": 95, "106": 99, "107": 99, "108": 100, "109": 100, "110": 102, "112": 103, "113": 104, "114": 104, "115": 104, "116": 106, "117": 106, "118": 108, "119": 109, "120": 109, "121": 109, "122": 109, "123": 109, "124": 111, "125": 115, "126": 117, "127": 117, "128": 119, "129": 119, "130": 121, "131": 121, "132": 125, "133": 125, "134": 126, "135": 126, "136": 128, "138": 129, "139": 130, "140": 130, "141": 130, "142": 132, "143": 132, "144": 134, "145": 135, "146": 135, "147": 135, "148": 135, "149": 135, "150": 137, "151": 141, "152": 143, "153": 143, "154": 145, "155": 145, "156": 147, "157": 147, "158": 151, "159": 151, "160": 152, "161": 152, "162": 153, "163": 153, "169": 163}}
__M_END_METADATA
"""
