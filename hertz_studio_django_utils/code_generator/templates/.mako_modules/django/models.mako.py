# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1760426258.0375054
_enable_loop = True
_template_filename = 'C:/2025.8/project/9/moban/hertz_server_django/hertz_studio_django_utils/code_generator/templates/django/models.mako'
_template_uri = 'django/models.mako'
_source_encoding = 'utf-8'
_exports = []



from datetime import datetime


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        any = context.get('any', UNDEFINED)
        chr = context.get('chr', UNDEFINED)
        ordering = context.get('ordering', UNDEFINED)
        fields = context.get('fields', UNDEFINED)
        verbose_name = context.get('verbose_name', UNDEFINED)
        model_name = context.get('model_name', UNDEFINED)
        str = context.get('str', UNDEFINED)
        table_name = context.get('table_name', UNDEFINED)
        status_choices = context.get('status_choices', UNDEFINED)
        tuple = context.get('tuple', UNDEFINED)
        isinstance = context.get('isinstance', UNDEFINED)
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('"""\r\nDjango模型模板\r\n"""\r\n')
        __M_writer('\r\n')

# 导入必要的模块
        imports = []
        if any(field.get('type') == 'ForeignKey' for field in fields):
            imports.append('from django.contrib.auth import get_user_model')
        if any(field.get('type') in ['DateTimeField', 'DateField', 'TimeField'] for field in fields):
            imports.append('from django.utils import timezone')
        if any(field.get('choices') for field in fields):
            imports.append('from django.core.validators import validate_email')
        
        # 生成状态选择项
        status_choices_code = ""
        if status_choices:
            choices_list = []
            for choice in status_choices:
                if isinstance(choice, tuple) and len(choice) == 2:
                    choices_list.append(f"        ('{choice[0]}', '{choice[1]}')")
                else:
                    choices_list.append(f"        ('{choice}', '{choice}')")
            status_choices_code = f"""    STATUS_CHOICES = [
{',{}'.format(chr(10)).join(choices_list)},
    ]"""
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field','choice','choices_list','imports','status_choices_code'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('from django.db import models\r\n')
        for import_line in imports:
            __M_writer(str(import_line))
            __M_writer('\r\n')
        __M_writer('\r\nclass ')
        __M_writer(str(model_name))
        __M_writer('(models.Model):\r\n    """\r\n    ')
        __M_writer(str(verbose_name or model_name))
        __M_writer('模型\r\n')
        if table_name:
            __M_writer('    \r\n    数据表名: ')
            __M_writer(str(table_name))
            __M_writer('\r\n')
        __M_writer('    创建时间: ')
        __M_writer(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        __M_writer('\r\n    """\r\n')
        if status_choices_code:
            __M_writer(str(status_choices_code))
            __M_writer('\r\n\r\n')
        for field in fields:

            field_name = field['name']
            # 使用转换后的Django字段类型
            field_type = field.get('type', 'CharField')
            field_options = []
            
            # 处理字段选项
            if field.get('verbose_name'):
                field_options.append(f"verbose_name='{field['verbose_name']}'")
            if field.get('help_text'):
                field_options.append(f"help_text='{field['help_text']}'")
            if field.get('max_length'):
                field_options.append(f"max_length={field['max_length']}")
            if field.get('null'):
                field_options.append(f"null={field['null']}")
            if field.get('blank'):
                field_options.append(f"blank={field['blank']}")
            if field.get('default') is not None:
                if isinstance(field['default'], str):
                    field_options.append(f"default='{field['default']}'")
                else:
                    field_options.append(f"default={field['default']}")
            if field.get('unique'):
                field_options.append(f"unique={field['unique']}")
            if field.get('db_index'):
                field_options.append(f"db_index={field['db_index']}")
            
            # 处理特殊字段类型
            if field_type == 'ForeignKey':
                if field.get('to'):
                    field_options.insert(0, f"'{field['to']}'")
                else:
                    field_options.insert(0, "get_user_model()")
                if field.get('on_delete'):
                    field_options.append(f"on_delete=models.{field['on_delete']}")
                else:
                    field_options.append("on_delete=models.CASCADE")
            elif field_type == 'ManyToManyField':
                if field.get('to'):
                    field_options.insert(0, f"'{field['to']}'")
            elif field_type == 'OneToOneField':
                if field.get('to'):
                    field_options.insert(0, f"'{field['to']}'")
                if field.get('on_delete'):
                    field_options.append(f"on_delete=models.{field['on_delete']}")
                else:
                    field_options.append("on_delete=models.CASCADE")
            
            # 处理选择项
            if field.get('choices'):
                if field_name == 'status' and status_choices:
                    field_options.append("choices=STATUS_CHOICES")
                else:
                    choices_list = []
                    for choice in field['choices']:
                        if isinstance(choice, tuple) and len(choice) == 2:
                            choices_list.append(f"('{choice[0]}', '{choice[1]}')")
                        else:
                            choices_list.append(f"('{choice}', '{choice}')")
                    field_options.append(f"choices=[{', '.join(choices_list)}]")
            
            # 处理特殊字段类型的额外参数
            if field_type == 'DecimalField':
                if not any('max_digits' in opt for opt in field_options):
                    field_options.append('max_digits=10')
                if not any('decimal_places' in opt for opt in field_options):
                    field_options.append('decimal_places=2')
            elif field_type == 'DateTimeField':
                if field_name == 'created_at' and not any('auto_now_add' in opt for opt in field_options):
                    field_options.append('auto_now_add=True')
                elif field_name == 'updated_at' and not any('auto_now' in opt for opt in field_options):
                    field_options.append('auto_now=True')
            
            options_str = ', '.join(field_options) if field_options else ''
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_options','options_str','choice','choices_list','opt','field_name','field_type'] if __M_key in __M_locals_builtin_stored]))
            __M_writer('\r\n    ')
            __M_writer(str(field_name))
            __M_writer(' = models.')
            __M_writer(str(field_type))
            __M_writer('(')
            __M_writer(str(options_str))
            __M_writer(')\r\n')
        __M_writer('\r\n    class Meta:\r\n')
        if table_name:
            __M_writer("        db_table = '")
            __M_writer(str(table_name))
            __M_writer("'\r\n")
        __M_writer("        verbose_name = '")
        __M_writer(str(verbose_name or model_name))
        __M_writer("'\r\n        verbose_name_plural = '")
        __M_writer(str(verbose_name or model_name))
        __M_writer("'\r\n")
        if ordering:
            __M_writer('        ordering = [')
            __M_writer(str(', '.join([f"'{field}'" for field in ordering])))
            __M_writer(']\r\n')
        else:
            __M_writer("        ordering = ['-created_at']\r\n")
        __M_writer('\r\n    def __str__(self):\r\n        """字符串表示"""\r\n')
        if fields:
            __M_writer('        ')

        # 寻找合适的字段作为字符串表示
            str_field = None
            for field in fields:
                if field['name'] in ['name', 'title', 'username', 'email']:
                    str_field = field['name']
                    break
            if not str_field:
                # 如果没有找到合适的字段，使用第一个字符串字段
                for field in fields:
                    if field['type'] in ['CharField', 'TextField', 'EmailField']:
                        str_field = field['name']
                        break
            if not str_field:
                str_field = 'id'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field','str_field'] if __M_key in __M_locals_builtin_stored]))
            __M_writer('\r\n        return str(self.')
            __M_writer(str(str_field))
            __M_writer(')\r\n')
        else:
            __M_writer('        return f"')
            __M_writer(str(model_name))
            __M_writer('({self.id})"\r\n')
        __M_writer('\r\n    def save(self, *args, **kwargs):\r\n        """保存方法"""\r\n        super().save(*args, **kwargs)\r\n\r\n    @classmethod\r\n    def get_by_id(cls, obj_id):\r\n        """根据ID获取对象"""\r\n        try:\r\n            return cls.objects.get(id=obj_id)\r\n        except cls.DoesNotExist:\r\n            return None')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "C:/2025.8/project/9/moban/hertz_server_django/hertz_studio_django_utils/code_generator/templates/django/models.mako", "uri": "django/models.mako", "source_encoding": "utf-8", "line_map": {"16": 4, "17": 5, "18": 6, "19": 7, "20": 0, "37": 1, "38": 6, "39": 7, "40": 8, "41": 9, "42": 10, "43": 11, "44": 12, "45": 13, "46": 14, "47": 15, "48": 16, "49": 17, "50": 18, "51": 19, "52": 20, "53": 21, "54": 22, "55": 23, "56": 24, "57": 25, "58": 26, "59": 27, "60": 28, "61": 29, "62": 30, "65": 30, "66": 31, "67": 32, "68": 32, "69": 34, "70": 35, "71": 35, "72": 37, "73": 37, "74": 38, "75": 39, "76": 40, "77": 40, "78": 42, "79": 42, "80": 42, "81": 44, "82": 45, "83": 45, "84": 48, "85": 49, "86": 50, "87": 51, "88": 52, "89": 53, "90": 54, "91": 55, "92": 56, "93": 57, "94": 58, "95": 59, "96": 60, "97": 61, "98": 62, "99": 63, "100": 64, "101": 65, "102": 66, "103": 67, "104": 68, "105": 69, "106": 70, "107": 71, "108": 72, "109": 73, "110": 74, "111": 75, "112": 76, "113": 77, "114": 78, "115": 79, "116": 80, "117": 81, "118": 82, "119": 83, "120": 84, "121": 85, "122": 86, "123": 87, "124": 88, "125": 89, "126": 90, "127": 91, "128": 92, "129": 93, "130": 94, "131": 95, "132": 96, "133": 97, "134": 98, "135": 99, "136": 100, "137": 101, "138": 102, "139": 103, "140": 104, "141": 105, "142": 106, "143": 107, "144": 108, "145": 109, "146": 110, "147": 111, "148": 112, "149": 113, "150": 114, "151": 115, "152": 116, "153": 117, "154": 118, "155": 119, "156": 120, "157": 121, "158": 122, "159": 123, "160": 124, "163": 123, "164": 124, "165": 124, "166": 124, "167": 124, "168": 124, "169": 124, "170": 126, "171": 128, "172": 129, "173": 129, "174": 129, "175": 131, "176": 131, "177": 131, "178": 132, "179": 132, "180": 133, "181": 134, "182": 134, "183": 134, "184": 135, "185": 136, "186": 138, "187": 141, "188": 142, "189": 142, "190": 143, "191": 144, "192": 145, "193": 146, "194": 147, "195": 148, "196": 149, "197": 150, "198": 151, "199": 152, "200": 153, "201": 154, "202": 155, "203": 156, "204": 157, "205": 158, "208": 157, "209": 158, "210": 158, "211": 159, "212": 160, "213": 160, "214": 160, "215": 162, "221": 215}}
__M_END_METADATA
"""
