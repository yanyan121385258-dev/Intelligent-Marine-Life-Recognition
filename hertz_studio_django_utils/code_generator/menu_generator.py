#!/usr/bin/env python
"""
菜单权限生成器
用于自动生成菜单配置和权限同步功能
"""

from typing import Dict, List, Optional, Any
import os
from pathlib import Path


class MenuGenerator:
    """
    菜单权限生成器
    
    用于根据模型和操作自动生成菜单配置，包括：
    1. 菜单项配置
    2. 权限配置
    3. 菜单层级结构
    """
    
    def __init__(self):
        """初始化菜单生成器"""
        self.menu_types = {
            'directory': 1,  # 目录
            'menu': 2,       # 菜单
            'button': 3      # 按钮
        }
        
        # 标准操作映射 - 与视图生成器保持一致
        self.operation_mapping = {
            'list': {'name': '查询', 'permission': 'list'},
            'create': {'name': '新增', 'permission': 'add'},
            'retrieve': {'name': '详情', 'permission': 'list'},  # 统一使用list权限
            'update': {'name': '修改', 'permission': 'edit'},
            'delete': {'name': '删除', 'permission': 'remove'},
            'export': {'name': '导出', 'permission': 'export'},
            'import': {'name': '导入', 'permission': 'import'},
        }
    
    def generate_menu_config(
        self,
        module_name: str,
        model_name: str,
        operations: List[str],
        parent_code: Optional[str] = None,
        menu_prefix: str = 'system',
        sort_order: int = 1,
        icon: Optional[str] = None,
        component_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        生成菜单配置
        
        Args:
            module_name: 模块名称（中文）
            model_name: 模型名称（英文，snake_case）
            operations: 操作列表
            parent_code: 父级菜单代码
            menu_prefix: 菜单前缀
            sort_order: 排序
            icon: 图标
            component_path: 组件路径
            
        Returns:
            List[Dict]: 菜单配置列表
        """
        menus = []
        
        # 生成主菜单
        main_menu_code = f"{menu_prefix}:{model_name}"
        main_menu = {
            'menu_name': module_name,
            'menu_code': main_menu_code,
            'menu_type': self.menu_types['menu'],
            'path': f"/{menu_prefix}/{model_name}",
            'component': component_path or f"{menu_prefix}/{model_name}/index",
            'icon': icon or model_name,
            'permission': f"{main_menu_code}:list",
            'sort_order': sort_order,
            'parent_code': parent_code
        }
        menus.append(main_menu)
        
        # 生成操作按钮
        for i, operation in enumerate(operations, 1):
            if operation in self.operation_mapping:
                op_config = self.operation_mapping[operation]
                button_menu = {
                    'menu_name': f"{module_name}{op_config['name']}",
                    'menu_code': f"{main_menu_code}:{op_config['permission']}",
                    'menu_type': self.menu_types['button'],
                    'permission': f"{main_menu_code}:{op_config['permission']}",
                    'sort_order': i,
                    'parent_code': main_menu_code
                }
                menus.append(button_menu)
        
        return menus
    
    def generate_directory_config(
        self,
        directory_name: str,
        directory_code: str,
        path: str,
        icon: str = 'folder',
        sort_order: int = 1
    ) -> Dict[str, Any]:
        """
        生成目录配置
        
        Args:
            directory_name: 目录名称
            directory_code: 目录代码
            path: 路径
            icon: 图标
            sort_order: 排序
            
        Returns:
            Dict: 目录配置
        """
        return {
            'menu_name': directory_name,
            'menu_code': directory_code,
            'menu_type': self.menu_types['directory'],
            'path': path,
            'icon': icon,
            'sort_order': sort_order,
            'parent_code': None
        }
    
    def generate_custom_menu_config(
        self,
        menu_name: str,
        menu_code: str,
        operations: List[Dict[str, str]],
        parent_code: Optional[str] = None,
        path: Optional[str] = None,
        component: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: int = 1
    ) -> List[Dict[str, Any]]:
        """
        生成自定义菜单配置
        
        Args:
            menu_name: 菜单名称
            menu_code: 菜单代码
            operations: 自定义操作列表 [{'name': '操作名', 'permission': '权限码'}]
            parent_code: 父级菜单代码
            path: 路径
            component: 组件
            icon: 图标
            sort_order: 排序
            
        Returns:
            List[Dict]: 菜单配置列表
        """
        menus = []
        
        # 生成主菜单
        main_menu = {
            'menu_name': menu_name,
            'menu_code': menu_code,
            'menu_type': self.menu_types['menu'],
            'sort_order': sort_order,
            'parent_code': parent_code
        }
        
        if path:
            main_menu['path'] = path
        if component:
            main_menu['component'] = component
        if icon:
            main_menu['icon'] = icon
        if operations:
            main_menu['permission'] = f"{menu_code}:{operations[0]['permission']}"
        
        menus.append(main_menu)
        
        # 生成操作按钮
        for i, operation in enumerate(operations, 1):
            button_menu = {
                'menu_name': f"{menu_name}{operation['name']}",
                'menu_code': f"{menu_code}:{operation['permission']}",
                'menu_type': self.menu_types['button'],
                'permission': f"{menu_code}:{operation['permission']}",
                'sort_order': i,
                'parent_code': menu_code
            }
            menus.append(button_menu)
        
        return menus
    
    def update_menus_config_file(
        self,
        new_menus: List[Dict[str, Any]],
        config_file_path: str = None
    ) -> bool:
        """
        更新菜单配置文件
        
        Args:
            new_menus: 新的菜单配置列表
            config_file_path: 配置文件路径
            
        Returns:
            bool: 更新是否成功
        """
        if not config_file_path:
            config_file_path = os.path.join(
                Path(__file__).parent.parent,
                'config',
                'menus_config.py'
            )
        
        try:
            # 读取现有配置
            with open(config_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找现有菜单列表的结束位置
            import_end = content.find(']')
            if import_end == -1:
                return False
            
            # 生成新菜单配置代码
            new_menu_code = self._generate_menu_code(new_menus)
            
            # 在现有菜单列表末尾添加新菜单（在最后一个 ] 之前）
            updated_content = (
                content[:import_end] + 
                ',\n\n    # 新增菜单配置\n' +
                new_menu_code +
                content[import_end:]
            )
            
            # 写入更新后的配置
            with open(config_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return True
            
        except Exception as e:
            print(f"更新菜单配置文件失败: {e}")
            return False
    
    def _generate_menu_code(self, menus: List[Dict[str, Any]]) -> str:
        """
        生成菜单配置代码
        
        Args:
            menus: 菜单配置列表
            
        Returns:
            str: 菜单配置代码
        """
        code_lines = []
        
        for menu in menus:
            code_lines.append("    {")
            for key, value in menu.items():
                if isinstance(value, str):
                    code_lines.append(f"        '{key}': '{value}',")
                elif value is None:
                    code_lines.append(f"        '{key}': None,")
                else:
                    code_lines.append(f"        '{key}': {value},")
            code_lines.append("    }")
        
        return '\n'.join(code_lines)
    
    def generate_permission_sync_code(
        self,
        menu_configs: List[Dict[str, Any]]
    ) -> str:
        """
        生成权限同步代码
        
        Args:
            menu_configs: 菜单配置列表
            
        Returns:
            str: 权限同步代码
        """
        sync_code = '''
def sync_new_menus():
    """
    同步新增菜单到数据库
    """
    from hertz_studio_django_auth.models import HertzMenu
    from django.db import transaction
    
    new_menus = [
'''
        
        # 添加菜单配置
        sync_code += self._generate_menu_code(menu_configs)
        
        sync_code += '''
    ]
    
    print("正在同步新增菜单...")
    
    with transaction.atomic():
        created_menus = {}
        
        # 按层级创建菜单
        for menu_data in new_menus:
            parent_code = menu_data.pop('parent_code', None)
            parent_id = None
            
            if parent_code and parent_code in created_menus:
                parent_id = created_menus[parent_code]
            
            menu, created = HertzMenu.objects.get_or_create(
                menu_code=menu_data['menu_code'],
                defaults={
                    **menu_data,
                    'parent_id': parent_id
                }
            )
            
            created_menus[menu.menu_code] = menu
            
            if created:
                print(f"菜单创建成功: {menu.menu_name}")
            else:
                print(f"菜单已存在: {menu.menu_name}")
    
    print("菜单同步完成")
'''
        
        return sync_code
    
    def create_menu_sync_script(
        self,
        menu_configs: List[Dict[str, Any]],
        script_path: str = None
    ) -> bool:
        """
        创建菜单同步脚本
        
        Args:
            menu_configs: 菜单配置列表
            script_path: 脚本路径
            
        Returns:
            bool: 创建是否成功
        """
        if not script_path:
            script_path = os.path.join(
                Path(__file__).parent.parent.parent,
                'sync_menus.py'
            )
        
        try:
            script_content = f'''#!/usr/bin/env python
"""
菜单同步脚本
自动生成的菜单权限同步脚本
"""

import os
import sys
import django

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hertz_server_django.settings')
django.setup()

{self.generate_permission_sync_code(menu_configs)}

if __name__ == "__main__":
    sync_new_menus()
'''
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            return True
            
        except Exception as e:
            print(f"创建菜单同步脚本失败: {e}")
            return False


# 使用示例
def example_usage():
    """使用示例"""
    generator = MenuGenerator()
    
    # 生成标准CRUD菜单
    crud_menus = generator.generate_menu_config(
        module_name="产品管理",
        model_name="product",
        operations=['list', 'create', 'update', 'delete'],
        parent_code="system",
        sort_order=5,
        icon="product"
    )
    
    # 生成自定义菜单
    custom_menus = generator.generate_custom_menu_config(
        menu_name="报表管理",
        menu_code="system:report",
        operations=[
            {'name': '查看', 'permission': 'view'},
            {'name': '导出', 'permission': 'export'},
            {'name': '打印', 'permission': 'print'}
        ],
        parent_code="system",
        path="/system/report",
        component="system/report/index",
        icon="report",
        sort_order=8
    )
    
    # 更新配置文件
    all_menus = crud_menus + custom_menus
    generator.update_menus_config_file(all_menus)
    
    # 创建同步脚本
    generator.create_menu_sync_script(all_menus)
    
    print("菜单配置生成完成")


if __name__ == "__main__":
    example_usage()