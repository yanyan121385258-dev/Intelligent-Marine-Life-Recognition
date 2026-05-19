#!/usr/bin/env python
"""
启动脚本 - 同时支持HTTP和WebSocket
使用Daphne ASGI服务器启动Django应用，支持自动热重启
包含数据库初始化功能和菜单权限同步功能
"""

import os
import sys
import subprocess
import time
import threading
import django
import importlib.util
import re
import argparse
from pathlib import Path
from django.db import transaction
from django.db import models
from django.core.management import call_command
from studio_django_utils.config.menus_config import menus, add_new_menus
from studio_django_utils.config.departments_config import departments
from studio_django_utils.config.roles_config import roles



def register_app_in_settings(settings_path: str, app_name: str) -> bool:
    """
    在settings.py中注册新应用
    
    Args:
        settings_path: settings.py文件路径
        app_name: 应用名称
        
    Returns:
        bool: 注册是否成功
    """
    try:
        # 读取settings.py文件
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查应用是否已经注册
        if f"'{app_name}'" in content:
            print(f"应用 {app_name} 已在settings.py中注册")
            return True
        
        # 使用更精确的正则表达式匹配INSTALLED_APPS
        # 匹配从INSTALLED_APPS = [开始到对应的]结束
        pattern = r"INSTALLED_APPS\s*=\s*\[(.*?)\n\]"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("未找到INSTALLED_APPS配置")
            return False
        
        # 获取INSTALLED_APPS的内容
        apps_content = match.group(1)
        
        # 在最后一个应用后添加新应用
        # 找到最后一个应用的位置（以逗号结尾的行）
        lines = apps_content.split('\n')
        
        # 找到最后一个非空行的位置
        last_app_index = -1
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line and not line.startswith('#') and line.endswith(','):
                last_app_index = i
                break
        
        if last_app_index >= 0:
            # 在最后一个应用后添加新应用
            lines.insert(last_app_index + 1, f"    '{app_name}',  # 自动注册的应用")
        else:
            # 如果没有找到合适的位置，在最后添加
            lines.append(f"    '{app_name}',  # 自动注册的应用")
        
        # 重新组装内容
        new_apps_content = '\n'.join(lines)
        new_content = content.replace(
            f"INSTALLED_APPS = [{apps_content}\n]",
            f"INSTALLED_APPS = [{new_apps_content}\n]"
        )
        
        # 写回文件
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"应用 {app_name} 已注册到settings.py")
        return True

    except Exception as e:
        print(f"注册应用到settings.py失败: {e}")
        return False


def register_urls_in_project(urls_path: str, app_name: str) -> bool:
    """
    在项目urls.py中注册新应用的URL路由
    
    Args:
        urls_path: 项目urls.py文件路径
        app_name: 应用名称
        
    Returns:
        bool: 注册是否成功
    """
    try:
        # 读取urls.py文件
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查URL是否已经注册
        if f"include('{app_name}.urls')" in content:
            print(f"应用 {app_name} 的URL已在项目urls.py中注册")
            return True
        
        # 查找urlpatterns的位置
        pattern = r"(urlpatterns\s*=\s*\[)(.*?)(\n\])"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("未找到urlpatterns配置")
            return False
        
        # 获取urlpatterns的内容
        patterns_start = match.group(1)
        patterns_content = match.group(2)
        patterns_end = match.group(3)
        
        # 生成URL路由配置
        # 根据应用名称生成合适的URL前缀
        if app_name.startswith('studio_django_'):
            # 提取模块名作为URL前缀
            module_name = app_name.replace('studio_django_', '')
            url_prefix = f"api/{module_name}/"
            comment = f"# Hertz {module_name.title()} routes"
        else:
            url_prefix = f"api/{app_name}/"
            comment = f"# {app_name.title()} routes"
        
        new_route = f"\n    {comment}\n    path('{url_prefix}', include('{app_name}.urls')),"
        
        # 在API documentation routes之前添加新路由
        if "# API documentation routes" in patterns_content:
            new_patterns_content = patterns_content.replace(
                "    # API documentation routes",
                f"    {new_route}\n    \n    # API documentation routes"
            )
        else:
            # 如果没有找到API documentation routes，在最后添加
            new_patterns_content = patterns_content.rstrip() + new_route + "\n"
        
        # 重新组装内容
        new_content = content.replace(
            patterns_start + patterns_content + patterns_end,
            patterns_start + new_patterns_content + patterns_end
        )
        
        # 写回文件
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 应用 {app_name} 的URL已注册到项目urls.py")
        return True
        
    except Exception as e:
        print(f"❌ 注册URL到项目urls.py失败: {e}")
        return False


def scan_and_register_new_apps() -> list:
    """
    扫描项目目录，发现并注册新的Django应用
    
    Returns:
        list: 新注册的应用列表
    """
    print("扫描项目目录，查找新的Django应用...")
    
    project_root = Path(__file__).parent
    settings_path = project_root / 'server_django' / 'settings.py'
    urls_path = project_root / 'server_django' / 'urls.py'
    
    # 读取当前已注册的应用
    registered_apps = set()
    try:
        spec = importlib.util.spec_from_file_location("settings", settings_path)
        settings_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings_module)
        registered_apps = set(settings_module.INSTALLED_APPS)
    except Exception as e:
        print(f"读取settings.py失败: {e}")
        return []
    
    # 扫描项目目录，查找Django应用
    new_apps = []
    for item in project_root.iterdir():
        if item.is_dir() and item.name.startswith('studio_django_'):
            app_name = item.name
            
            # 检查是否是Django应用（包含apps.py文件）
            apps_py = item / 'apps.py'
            if apps_py.exists() and app_name not in registered_apps:
                print(f"发现新应用: {app_name}")
                
                # 1. 注册到settings.py
                if register_app_in_settings(str(settings_path), app_name):
                    # 2. 注册到urls.py
                    if register_urls_in_project(str(urls_path), app_name):
                        new_apps.append(app_name)
                        print(f"应用 {app_name} 注册成功")
                    else:
                        print(f"应用 {app_name} URL注册失败")
                else:
                    print(f"应用 {app_name} settings注册失败")

    if new_apps:
        print(f"成功注册 {len(new_apps)} 个新应用: {', '.join(new_apps)}")
    else:
        print("没有发现新的Django应用")
    
    return new_apps


def execute_migrations_for_new_apps(new_apps: list) -> bool:
    """
    为新注册的应用执行数据库迁移
    
    Args:
        new_apps: 新应用列表
        
    Returns:
        bool: 迁移是否成功
    """
    if not new_apps:
        return True
    
    try:
        print(f"为新应用执行数据库迁移: {', '.join(new_apps)}")
        
        for app_name in new_apps:
            print(f"为应用 {app_name} 生成迁移文件...")
            try:
                # 先检查应用是否在Django中正确加载
                from django.apps import apps
                try:
                    app_config = apps.get_app_config(app_name)
                    print(f"✅ 应用 {app_name} 已正确加载")
                except LookupError:
                    print(f"⚠️ 应用 {app_name} 未在Django中加载，跳过迁移")
                    continue
                
                # 生成迁移文件
                call_command('makemigrations', app_name, verbosity=1)
                print(f"✅ 应用 {app_name} 迁移文件生成成功")
                
                # 执行迁移
                call_command('migrate', app_name, verbosity=1)
                print(f"✅ 应用 {app_name} 迁移执行成功")
                
            except Exception as e:
                print(f"⚠️ 应用 {app_name} 迁移失败: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ 执行新应用迁移失败: {e}")
        return False
def init_superuser():
    """
    初始化超级管理员账号
    """
    from studio_django_auth.models import HertzUser
    
    print("正在初始化超级管理员账号...")
    
    # 检查是否已存在超级管理员
    if HertzUser.objects.filter(username='hertz').exists():
        print("超级管理员账号已存在，跳过创建")
        return HertzUser.objects.get(username='hertz')
    
    # 创建超级管理员
    superuser = HertzUser.objects.create_superuser(
        username='hertz',
        email='admin@hertz.com',
        password='hertz',
        real_name='超级管理员',
        status=1
    )
    
    print(f"超级管理员账号创建成功: {superuser.username}")
    return superuser

def init_demo_user():
    from studio_django_auth.models import HertzUser, HertzUserRole, HertzRole
    print("正在初始化普通用户账号...")
    if HertzUser.objects.filter(username='demo').exists():
        print("普通用户账号已存在，跳过创建")
        user = HertzUser.objects.get(username='demo')
    else:
        user = HertzUser.objects.create_user(
            username='demo',
            email='demo@hertz.com',
            password='123456',
            real_name='普通用户',
            status=1
        )
        print(f"普通用户账号创建成功: {user.username}")
    try:
        role = HertzRole.objects.get(role_id=3)
        user_role, created = HertzUserRole.objects.get_or_create(user=user, role=role)
        if created:
            print(f"为用户 {user.username} 分配角色ID: {role.role_id}")
        else:
            print(f"用户 {user.username} 已拥有角色ID: {role.role_id}")
    except HertzRole.DoesNotExist:
        print("角色ID=3不存在，跳过分配")
    return user


def init_departments():
    """
    初始化部门数据
    """
    from studio_django_auth.models import HertzDepartment
    
    print("正在初始化部门数据...")
    
    
    created_depts = {}
    
    for dept_data in departments:
        parent_code = dept_data.pop('parent_code', None)
        parent_id = None
        
        if parent_code and parent_code in created_depts:
            parent_id = created_depts[parent_code]
        
        dept, created = HertzDepartment.objects.get_or_create(
            dept_code=dept_data['dept_code'],
            defaults={
                **dept_data,
                'parent_id': parent_id
            }
        )
        
        created_depts[dept.dept_code] = dept
        
        if created:
            print(f"部门创建成功: {dept.dept_name}")
        else:
            print(f"部门已存在: {dept.dept_name}")
    
    return created_depts


def init_menus():
    """
    初始化菜单数据
    """
    from studio_django_auth.models import HertzMenu
    
    print("正在初始化菜单数据...")
    
    # 菜单数据结构
    created_menus = {}
    
    # 按层级创建菜单
    for menu_data in menus:
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
    
    return created_menus


def init_roles():
    """
    初始化角色数据
    """
    from studio_django_auth.models import HertzRole
    
    print("正在初始化角色数据...")
    

    
    created_roles = {}
    
    for role_data in roles:
        role, created = HertzRole.objects.get_or_create(
            role_code=role_data['role_code'],
            defaults=role_data
        )
        
        created_roles[role.role_code] = role
        
        if created:
            print(f"角色创建成功: {role.role_name}")
        else:
            print(f"角色已存在: {role.role_name}")
    
    return created_roles


def assign_role_menus(roles, menus):
    """
    分配角色菜单权限
    """
    from studio_django_auth.models import HertzRoleMenu
    
    print("正在分配角色菜单权限...")
    
    # 超级管理员拥有所有权限
    super_admin_role = roles['super_admin']
    
    for menu in menus.values():
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=super_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为超级管理员分配权限: {menu.menu_name}")
    
    # 系统管理员拥有系统管理权限和工作室权限
    system_admin_role = roles['system_admin']
    
    # 系统管理权限（包括日志管理和知识管理）
    system_menus = [menu for menu in menus.values() if menu.menu_code.startswith('system')]
    for menu in system_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=system_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为系统管理员分配系统权限: {menu.menu_name}")
    
    # 确保系统管理员拥有知识管理权限
    wiki_menus = [menu for menu in menus.values() if 'wiki' in menu.menu_code.lower()]
    for menu in wiki_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=system_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为系统管理员分配知识管理权限: {menu.menu_name}")
    
    # 确保系统管理员拥有日志管理权限
    log_menus = [menu for menu in menus.values() if 'log' in menu.menu_code.lower()]
    for menu in log_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=system_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为系统管理员分配日志权限: {menu.menu_name}")
    
    # 确保超级管理员也拥有所有日志权限（包括动态创建的子菜单）
    from studio_django_auth.models import HertzMenu
    all_log_menus = HertzMenu.objects.filter(menu_code__icontains='log', status=1)
    for menu in all_log_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=super_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为超级管理员分配日志权限: {menu.menu_name}")
    
    # 确保超级管理员也拥有所有知识管理权限（包括动态创建的子菜单）
    all_wiki_menus = HertzMenu.objects.filter(menu_code__icontains='wiki', status=1)
    for menu in all_wiki_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=super_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为超级管理员分配知识管理权限: {menu.menu_name}")
    
    # 工作室权限（包括通知公告、AI对话、系统监控）
    studio_menus = [menu for menu in menus.values() if menu.menu_code.startswith('studio')]
    for menu in studio_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=system_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为系统管理员分配工作室权限: {menu.menu_name}")
    
    # 普通用户拥有工作室基础权限（查询、列表、新增权限）
    normal_user_role = roles.get('normal_user')
    if normal_user_role:
        # 工作室目录权限
        studio_directory = [menu for menu in menus.values() if menu.menu_code == 'studio']
        for menu in studio_directory:
            role_menu, created = HertzRoleMenu.objects.get_or_create(
                role=normal_user_role,
                menu=menu
            )
            
            if created:
                print(f"为普通用户分配工作室目录权限: {menu.menu_name}")
        
        # 工作室各模块的基础权限（查询、列表、新增，排除编辑和删除）
        user_studio_menus = [
            menu for menu in menus.values() 
            if menu.menu_code in [
                # 通知公告模块
                'studio:notice', 'studio:notice:query', 'studio:notice:add',
                # AI对话模块 - 包含关键的list权限
                'studio:ai', 'studio:ai:query', 'studio:ai:add', 'studio:ai:list',
                # 系统监控模块
                'studio:system_monitor', 'studio:system_monitor:query', 'studio:system_monitor:add'
            ]
        ]
        for menu in user_studio_menus:
            role_menu, created = HertzRoleMenu.objects.get_or_create(
                role=normal_user_role,
                menu=menu
            )
            
            if created:
                print(f"为普通用户分配工作室权限: {menu.menu_name}")
        
        # 为普通用户分配知识库权限（查询、列表、新增权限）
        user_wiki_menus = [
            menu for menu in menus.values() 
            if menu.menu_code in [
                # 知识管理主菜单
                'system:wiki',
                # 知识分类权限
                'system:wiki:category', 'system:wiki:category:list', 
                'system:wiki:category:query', 'system:wiki:category:create',
                # 知识文章权限
                'system:wiki:article', 'system:wiki:article:list',
                'system:wiki:article:query', 'system:wiki:article:create'
            ]
        ]
        for menu in user_wiki_menus:
            role_menu, created = HertzRoleMenu.objects.get_or_create(
                role=normal_user_role,
                menu=menu
            )
            
            if created:
                print(f"为普通用户分配知识库权限: {menu.menu_name}")
        
        # 确保普通用户也拥有所有知识管理权限（包括动态创建的子菜单）
        all_wiki_menus = HertzMenu.objects.filter(menu_code__icontains='wiki', status=1)
        for menu in all_wiki_menus:
            # 只给普通用户分配查询和列表权限，不包括删除、修改和编辑权限
            if not any(perm in menu.menu_code for perm in ['remove', 'delete', 'edit', 'update']):
                role_menu, created = HertzRoleMenu.objects.get_or_create(
                    role=normal_user_role,
                    menu=menu
                )
                
                if created:
                    print(f"为普通用户分配知识管理权限: {menu.menu_name}")
    
    # 为超级管理员和系统管理员分配产品管理权限（包括动态创建的产品菜单）
    # 只查询小写的product菜单（正确的权限格式）
    all_product_menus = HertzMenu.objects.filter(
        menu_code__icontains='product',
        status=1
    )
    
    # 为超级管理员分配产品管理权限
    for menu in all_product_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=super_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为超级管理员分配产品管理权限: {menu.menu_name}")
    
    # 为系统管理员分配产品管理权限
    for menu in all_product_menus:
        role_menu, created = HertzRoleMenu.objects.get_or_create(
            role=system_admin_role,
            menu=menu
        )
        
        if created:
            print(f"为系统管理员分配产品管理权限: {menu.menu_name}")


def assign_user_roles(superuser, roles):
    """
    分配用户角色
    """
    from studio_django_auth.models import HertzUserRole
    
    print("正在分配用户角色...")
    
    # 为超级管理员分配超级管理员角色
    super_admin_role = roles['super_admin']
    
    user_role, created = HertzUserRole.objects.get_or_create(
        user=superuser,
        role=super_admin_role
    )
    
    if created:
        print(f"为用户 {superuser.username} 分配角色: {super_admin_role.role_name}")
    else:
        print(f"用户 {superuser.username} 已拥有角色: {super_admin_role.role_name}")


def sync_generated_menus():
    """
    同步代码生成器生成的菜单权限
    动态扫描所有pending_menus_*.py文件
    """
    print("正在检查是否有新生成的菜单需要同步...")
    
    import glob
    import importlib.util
    from studio_django_auth.models import HertzMenu
    
    # 动态扫描所有pending_menus_*.py文件
    project_root = Path(__file__).parent
    pending_files = list(project_root.glob('pending_menus*.py'))
    
    if not pending_files:
        print("没有待同步的菜单文件")
        return {}
    
    all_created_menus = {}
    total_synced_count = 0
    
    # 首先获取已存在的菜单，用于父级菜单查找
    existing_menus = {menu.menu_code: menu for menu in HertzMenu.objects.all()}
    
    for pending_file in pending_files:
        print(f"处理菜单文件: {pending_file.name}")
        
        try:
            # 动态导入菜单配置文件
            module_name = pending_file.stem  # 获取不带扩展名的文件名
            spec = importlib.util.spec_from_file_location(module_name, pending_file)
            pending_menus_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pending_menus_module)
            
            if not hasattr(pending_menus_module, 'pending_menus'):
                print(f"文件 {pending_file.name} 中没有找到 pending_menus 变量")
                continue
                
            pending_menus = pending_menus_module.pending_menus
            
            # 添加到菜单配置中
            add_new_menus(pending_menus)
            
            # 同步到数据库
            created_menus = {}
            synced_count = 0
            
            for menu_data in pending_menus:
                parent_code = menu_data.get('parent_code')
                parent_menu = None
                
                # 先从新创建的菜单中查找父级菜单
                if parent_code and parent_code in created_menus:
                    parent_menu = created_menus[parent_code]
                # 再从已存在的菜单中查找父级菜单
                elif parent_code and parent_code in existing_menus:
                    parent_menu = existing_menus[parent_code]
                # 最后从所有已创建的菜单中查找
                elif parent_code and parent_code in all_created_menus:
                    parent_menu = all_created_menus[parent_code]
                
                menu, created = HertzMenu.objects.get_or_create(
                    menu_code=menu_data['menu_code'],
                    defaults={
                        **{k: v for k, v in menu_data.items() if k != 'parent_code'},
                        'parent_id': parent_menu
                    }
                )
                
                # 如果菜单已存在但parent_id不同，更新parent_id
                if not created and menu.parent_id != parent_menu:
                    menu.parent_id = parent_menu
                    menu.save()
                
                created_menus[menu.menu_code] = menu
                all_created_menus[menu.menu_code] = menu
                
                if created:
                    print(f"新菜单同步成功: {menu.menu_name}")
                    synced_count += 1
                else:
                    print(f"菜单已存在: {menu.menu_name}")
            
            total_synced_count += synced_count
            print(f"文件 {pending_file.name} 处理完成，同步了 {synced_count} 个新菜单")
            
        except Exception as e:
            print(f"处理文件 {pending_file.name} 失败: {e}")
            continue
    
    print(f"菜单同步完成，总共同步了 {total_synced_count} 个新菜单")
    return all_created_menus


def assign_generated_menu_permissions(generated_menus):
    """
    为生成的菜单分配权限给超级管理员和系统管理员
    """
    if not generated_menus:
        return
    
    from studio_django_auth.models import HertzRole, HertzRoleMenu
    
    print("正在为生成的菜单分配权限...")
    
    try:
        # 获取角色
        super_admin_role = HertzRole.objects.get(role_code='super_admin')
        system_admin_role = HertzRole.objects.get(role_code='system_admin')
        
        # 为超级管理员分配所有生成的菜单权限
        for menu in generated_menus.values():
            role_menu, created = HertzRoleMenu.objects.get_or_create(
                role=super_admin_role,
                menu=menu
            )
            
            if created:
                print(f"为超级管理员分配权限: {menu.menu_name}")
        
        # 为系统管理员分配生成的菜单权限
        for menu in generated_menus.values():
            role_menu, created = HertzRoleMenu.objects.get_or_create(
                role=system_admin_role,
                menu=menu
            )
            
            if created:
                print(f"为系统管理员分配权限: {menu.menu_name}")
                
    except Exception as e:
        print(f"分配生成菜单权限失败: {e}")


def create_menu_generator_command():
    """
    创建菜单生成器命令行工具
    """
    generator_script = '''#!/usr/bin/env python
"""
菜单生成器命令行工具
用于快速生成菜单配置和权限同步
"""

import os
import sys
import argparse
import django
from pathlib import Path

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_django.settings')
django.setup()

from studio_django_utils.code_generator.menu_generator import MenuGenerator


def generate_crud_menu(args):
    """生成CRUD菜单"""
    generator = MenuGenerator()
    
    operations = args.operations.split(',') if args.operations else ['list', 'create', 'update', 'delete']
    
    menus = generator.generate_menu_config(
        module_name=args.module_name,
        model_name=args.model_name,
        operations=operations,
        parent_code=args.parent_code,
        menu_prefix=args.prefix,
        sort_order=args.sort_order,
        icon=args.icon
    )
    
    # 保存到待同步文件
    pending_file = os.path.join(project_root, 'pending_menus.py')
    with open(pending_file, 'w', encoding='utf-8') as f:
        f.write('# 待同步的菜单配置\\n')
        f.write('pending_menus = [\\n')
        for menu in menus:
            f.write('    {\\n')
            for key, value in menu.items():
                if isinstance(value, str):
                    f.write(f"        '{key}': '{value}',\\n")
                elif value is None:
                    f.write(f"        '{key}': None,\\n")
                else:
                    f.write(f"        '{key}': {value},\\n")
            f.write('    },\\n')
        f.write(']\\n')
    
    print(f"已生成 {len(menus)} 个菜单配置，保存到 pending_menus.py")
    print("请重启服务器以同步菜单到数据库")


def menu_generator_main():
    parser = argparse.ArgumentParser(description='菜单生成器')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # CRUD菜单生成命令
    crud_parser = subparsers.add_parser('crud', help='生成CRUD菜单')
    crud_parser.add_argument('module_name', help='模块名称（中文）')
    crud_parser.add_argument('model_name', help='模型名称（英文）')
    crud_parser.add_argument('--parent-code', default='system', help='父级菜单代码')
    crud_parser.add_argument('--prefix', default='system', help='菜单前缀')
    crud_parser.add_argument('--operations', help='操作列表（逗号分隔）')
    crud_parser.add_argument('--sort-order', type=int, default=1, help='排序')
    crud_parser.add_argument('--icon', help='图标')
    
    args = parser.parse_args()
    
    if args.command == 'crud':
        generate_crud_menu(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    menu_generator_main()
'''
    
    script_path = os.path.join(Path(__file__).parent, 'generate_menu.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(generator_script)
    
    print(f"菜单生成器命令行工具已创建: {script_path}")


def init_database():
    """
    数据库初始化主函数
    """
    print("开始初始化数据库...")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            superuser = init_superuser()
            
            # 2. 初始化部门
            departments = init_departments()
            
            # 3. 初始化菜单
            menus = init_menus()
            
            # 4. 同步代码生成器生成的菜单
            generated_menus = sync_generated_menus()
            
            # 5. 初始化角色
            roles = init_roles()
            
            # 6. 分配角色菜单权限
            assign_role_menus(roles, menus)
            
            # 7. 为生成的菜单分配权限
            assign_generated_menu_permissions(generated_menus)
            
            assign_user_roles(superuser, roles)
            demo_user = init_demo_user()
            
            # 9. 初始化YOLO模块数据
            # init_yolo_data()
            
            # 10. 创建菜单生成器命令行工具
            create_menu_generator_command()
            
            # 11. 删除待同步文件（如果存在）
            sync_file_path = os.path.join(Path(__file__).parent, 'pending_menus.py')
            if os.path.exists(sync_file_path):
                os.remove(sync_file_path)
                print("已删除待同步菜单文件")
            
            print("=" * 50)
            print("数据库初始化完成！")
            print("")
            print("超级管理员账号信息:")
            print(f"用户名: hertz")
            print(f"密码: hertz")
            print(f"邮箱: admin@hertz.com")
            print("")
            print("")
            print("菜单生成器工具:")
            print(f"使用命令: python generate_menu.py crud <模块名> <模型名>")
            print("")
            print("请妥善保管管理员账号信息！")
            print("")
            print("普通用户账号信息:")
            print("用户名: demo")
            print("密码: 123456")
            
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        sys.exit(1)


# 简化的文件监听实现，避免watchdog的兼容性问题
class SimpleFileWatcher:
    """简单的文件监听器"""
    
    def __init__(self, paths, callback):
        self.paths = paths
        self.callback = callback
        self.file_times = {}
        self.running = False
        self.thread = None
        self.last_check = 0
        self.check_interval = 1  # 检查间隔（秒）
        
    def _scan_files(self):
        """扫描文件变化"""
        for path in self.paths:
            if not path.exists():
                continue
                
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix in ['.py', '.html', '.css', '.js']:
                    try:
                        mtime = file_path.stat().st_mtime
                        if str(file_path) in self.file_times:
                            if mtime > self.file_times[str(file_path)]:
                                print(f"\n📝 检测到文件变化: {file_path}")
                                print("🔄 正在重启服务器...")
                                self.file_times[str(file_path)] = mtime
                                self.callback()
                                return
                        else:
                            self.file_times[str(file_path)] = mtime
                    except (OSError, PermissionError):
                        continue
    
    def _watch_loop(self):
        """监听循环"""
        while self.running:
            try:
                current_time = time.time()
                if current_time - self.last_check >= self.check_interval:
                    self._scan_files()
                    self.last_check = current_time
                time.sleep(0.1)
            except Exception:
                continue
    
    def start(self):
        """启动监听"""
        if not self.running:
            self.running = True
            # 初始化文件时间戳
            self._scan_files()
            self.thread = threading.Thread(target=self._watch_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """停止监听"""
        self.running = False
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=1)
            except KeyboardInterrupt:
                # 忽略键盘中断异常，直接继续执行
                pass

class ServerManager:
    """服务器管理器"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8000):
        self.process = None
        self.watcher = None
        self.base_dir = Path(__file__).resolve().parent
        self.running = True
        self.host = host
        self.port = int(port)
        
    def start_server(self):
        """启动服务器进程"""
        if self.process:
            self.stop_server()
            
        cmd = [
            sys.executable, '-m', 'daphne',
            '-b', self.host,
            '-p', str(self.port),
            'server_django.asgi:application'
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            print("服务器启动成功")
            return True
        except Exception as e:
            print(f"服务器启动失败: {e}")
            return False
    
    def stop_server(self):
        """停止服务器进程"""
        if self.process:
            try:
                if sys.platform == 'win32':
                    # Windows系统使用taskkill命令
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)], 
                                 capture_output=True)
                else:
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except Exception:
                pass
            finally:
                self.process = None
    
    def restart_server(self):
        """重启服务器"""
        self.stop_server()
        time.sleep(1)  # 延迟确保端口释放
        if self.running:
            self.start_server()
    
    def start_file_watcher(self):
        """启动文件监听器"""
        watch_paths = [
            self.base_dir,
        ]
        
        existing_paths = [path for path in watch_paths if path.exists()]
        if existing_paths:
            self.watcher = SimpleFileWatcher(existing_paths, self.restart_server)
            self.watcher.start()
            
            for path in existing_paths:
                print(f"监听目录: {path.name}")
    
    def stop_file_watcher(self):
        """停止文件监听器"""
        if self.watcher:
            self.watcher.stop()
    
    def shutdown(self):
        """关闭所有服务"""
        self.running = False
        self.stop_server()
        try:
            self.stop_file_watcher()
        except KeyboardInterrupt:
            # 忽略关闭过程中的键盘中断异常
            pass

def check_database_exists():
    """
    检查数据库是否存在
    """
    from django.conf import settings
    
    db_config = settings.DATABASES['default']
    
    if db_config['ENGINE'] == 'django.db.backends.sqlite3':
        db_path = Path(db_config['NAME'])
        return db_path.exists()
    else:
        try:
            from django.db import connection
            connection.ensure_connection()
            return True
        except Exception:
            return False

def create_mysql_database_if_missing():
    from django.conf import settings
    db = settings.DATABASES['default']
    if db['ENGINE'] != 'django.db.backends.mysql':
        return False
    name = db['NAME']
    host = db.get('HOST') or 'localhost'
    user = db.get('USER') or 'root'
    password = db.get('PASSWORD') or ''
    port = int(db.get('PORT') or 3306)
    try:
        import MySQLdb
    except Exception:
        return False
    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=password, port=port)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False


def run_migrations():
    """
    执行数据库迁移
    """
    print("正在检查并执行数据库迁移...")
    
    try:
        # 执行makemigrations
        print("执行makemigrations...")
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # 执行migrate
        print("执行migrate...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("数据库迁移完成")
        return True
    except Exception as e:
        print(f"数据库迁移失败: {str(e)}")
        return False


def check_initial_data():
    """
    检查是否存在初始数据
    """
    from studio_django_auth.models import HertzUser, HertzMenu
    
    try:
        # 检查是否存在超级管理员用户
        has_superuser = HertzUser.objects.filter(username='hertz').exists()
        
        # 检查是否存在工作室菜单（新增的菜单）
        has_studio_menu = HertzMenu.objects.filter(menu_code='studio').exists()
        
        # 只有当超级管理员和工作室菜单都存在时，才认为初始数据完整
        return has_superuser and has_studio_menu
    except Exception:
        # 如果表不存在或其他错误，返回False
        return False


def main():
    """
    主函数 - 自动化数据库检查、迁移、初始化和服务器启动
    """
    print("启动Hertz Server Django")
    print("开始自动化启动流程...")
    print("\n" + "=" * 50)
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_django.settings')
    django.setup()
    
    # 步骤0: 扫描并注册新应用
    print("步骤0: 扫描并注册新的Django应用...")
    new_apps = scan_and_register_new_apps()
    
    # 如果有新应用注册，需要重新加载Django设置
    if new_apps:
        print("重新加载Django设置...")
        # 重新导入settings模块
        import importlib
        from django.conf import settings
        
        # 重新导入settings模块
        settings_module = importlib.import_module('server_django.settings')
        importlib.reload(settings_module)
        
        # 重新配置Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_django.settings')
        django.setup()
        
        # 为新应用执行迁移
        execute_migrations_for_new_apps(new_apps)
    
    # 步骤1: 检查数据库是否存在
    print("步骤1: 检查数据库状态...")
    if not check_database_exists():
        print("数据库不存在，需要创建")
        created = create_mysql_database_if_missing()
        need_migration = True
    else:
        print("数据库文件存在")
        need_migration = False
    
    # 步骤2: 执行数据库迁移（如果需要）
    if need_migration or not check_initial_data():
        print("\n步骤2: 执行数据库迁移...")
        if not run_migrations():
            print("数据库迁移失败，无法继续")
            sys.exit(1)
    else:
        print("\n步骤2: 数据库迁移已完成")
    
    # 步骤3: 检查并初始化数据
    print("\n步骤3: 检查初始数据...")
    if not check_initial_data():
        print("缺少初始数据，开始初始化")
        init_database()
    else:
        print("初始数据已存在")
        # 即使初始数据存在，也要同步生成的菜单
        sync_generated_menus()
    
    print("\n" + "=" * 50)
    print("数据库准备完成！")
    
    # 步骤4: 启动服务器
    print("\n步骤4: 启动服务器...")
    print("启动Hertz Server Django (支持HTTP + WebSocket + 热重启)")
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--port', type=int)
    args, _ = parser.parse_known_args()
    env_port = os.environ.get('PORT') or os.environ.get('DJANGO_PORT')
    try:
        env_port_int = int(env_port) if env_port is not None else None
    except ValueError:
        env_port_int = None
    port = args.port or env_port_int or 8000
    print("使用Daphne ASGI服务器")
    print(f"HTTP服务: http://127.0.0.1:{port}/")
    print(f"WebSocket服务: ws://127.0.0.1:{port}/ws/")
    print("自动热重启: 已启用")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 检查依赖
    try:
        import daphne
    except ImportError:
        print("❌ 错误: 未安装daphne")
        print("请运行: pip install daphne")
        return
    
    try:
        import watchdog
    except ImportError:
        print("❌ 错误: 未安装watchdog")
        print("请运行: pip install watchdog")
        return
    
    # 创建服务器管理器
    server_manager = ServerManager(port=port)
    
    try:
        # 启动服务器
        if server_manager.start_server():
            # 启动文件监听器
            server_manager.start_file_watcher()
            
            # 保持主线程运行
            while server_manager.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\n收到停止信号，正在关闭服务器...")
                    break
        
    except Exception as e:
        print(f"启动失败: {e}")
    finally:
        server_manager.shutdown()
        print("服务器已停止")

if __name__ == "__main__":
    main()