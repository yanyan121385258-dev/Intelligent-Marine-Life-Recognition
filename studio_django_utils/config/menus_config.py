#!/usr/bin/env python
"""
菜单配置文件
包含系统所有菜单配置和动态菜单生成功能
"""

from typing import List, Dict, Any, Optional


def add_new_menus(new_menus: List[Dict[str, Any]]) -> None:
    """
    动态添加新菜单到配置中
    
    Args:
        new_menus: 新菜单配置列表
    """
    global menus
    menus.extend(new_menus)
    print(f"已添加 {len(new_menus)} 个新菜单到配置中")


def get_menus_by_parent(parent_code: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    根据父级代码获取菜单列表
    
    Args:
        parent_code: 父级菜单代码，None表示获取顶级菜单
        
    Returns:
        List[Dict]: 菜单列表
    """
    return [menu for menu in menus if menu.get('parent_code') == parent_code]


def get_menu_by_code(menu_code: str) -> Optional[Dict[str, Any]]:
    """
    根据菜单代码获取菜单配置
    
    Args:
        menu_code: 菜单代码
        
    Returns:
        Optional[Dict]: 菜单配置，未找到返回None
    """
    for menu in menus:
        if menu.get('menu_code') == menu_code:
            return menu
    return None


def generate_menu_permissions() -> List[str]:
    """
    生成所有菜单权限列表
    
    Returns:
        List[str]: 权限代码列表
    """
    permissions = []
    for menu in menus:
        if menu.get('permission'):
            permissions.append(menu['permission'])
    return permissions


menus = [
    # 系统管理目录
    {
        'menu_name': '系统管理',
        'menu_code': 'system',
        'menu_type': 1,  # 目录
        'path': '/system',
        'icon': 'system',
        'sort_order': 1,
        'parent_code': None
    },

    # 用户管理菜单
    {
        'menu_name': '用户管理',
        'menu_code': 'system:user',
        'menu_type': 2,  # 菜单
        'path': '/system/user',
        'component': 'system/user/index',
        'icon': 'user',
        'permission': 'system:user:list',
        'sort_order': 1,
        'parent_code': 'system'
    },
    {
        'menu_name': '用户查询',
        'menu_code': 'system:user:query',
        'menu_type': 3,  # 按钮
        'permission': 'system:user:query',
        'sort_order': 1,
        'parent_code': 'system:user'
    },
    {
        'menu_name': '用户新增',
        'menu_code': 'system:user:add',
        'menu_type': 3,
        'permission': 'system:user:add',
        'sort_order': 2,
        'parent_code': 'system:user'
    },
    {
        'menu_name': '用户修改',
        'menu_code': 'system:user:edit',
        'menu_type': 3,
        'permission': 'system:user:edit',
        'sort_order': 3,
        'parent_code': 'system:user'
    },
    {
        'menu_name': '用户删除',
        'menu_code': 'system:user:remove',
        'menu_type': 3,
        'permission': 'system:user:remove',
        'sort_order': 4,
        'parent_code': 'system:user'
    },
    {
        'menu_name': '分配角色',
        'menu_code': 'system:user:role',
        'menu_type': 3,
        'permission': 'system:user:role',
        'sort_order': 5,
        'parent_code': 'system:user'
    },

    # 角色管理菜单
    {
        'menu_name': '角色管理',
        'menu_code': 'system:role',
        'menu_type': 2,
        'path': '/system/role',
        'component': 'system/role/index',
        'icon': 'role',
        'permission': 'system:role:list',
        'sort_order': 2,
        'parent_code': 'system'
    },
    {
        'menu_name': '角色查询',
        'menu_code': 'system:role:query',
        'menu_type': 3,
        'permission': 'system:role:query',
        'sort_order': 1,
        'parent_code': 'system:role'
    },
    {
        'menu_name': '角色新增',
        'menu_code': 'system:role:add',
        'menu_type': 3,
        'permission': 'system:role:add',
        'sort_order': 2,
        'parent_code': 'system:role'
    },
    {
        'menu_name': '角色修改',
        'menu_code': 'system:role:edit',
        'menu_type': 3,
        'permission': 'system:role:edit',
        'sort_order': 3,
        'parent_code': 'system:role'
    },
    {
        'menu_name': '角色删除',
        'menu_code': 'system:role:remove',
        'menu_type': 3,
        'permission': 'system:role:remove',
        'sort_order': 4,
        'parent_code': 'system:role'
    },
    {
        'menu_name': '分配权限',
        'menu_code': 'system:role:menu',
        'menu_type': 3,
        'permission': 'system:role:menu',
        'sort_order': 5,
        'parent_code': 'system:role'
    },

    # 菜单管理菜单
    {
        'menu_name': '菜单管理',
        'menu_code': 'system:menu',
        'menu_type': 2,
        'path': '/system/menu',
        'component': 'system/menu/index',
        'icon': 'menu',
        'permission': 'system:menu:list',
        'sort_order': 3,
        'parent_code': 'system'
    },
    {
        'menu_name': '菜单查询',
        'menu_code': 'system:menu:query',
        'menu_type': 3,
        'permission': 'system:menu:query',
        'sort_order': 1,
        'parent_code': 'system:menu'
    },
    {
        'menu_name': '菜单新增',
        'menu_code': 'system:menu:add',
        'menu_type': 3,
        'permission': 'system:menu:add',
        'sort_order': 2,
        'parent_code': 'system:menu'
    },
    {
        'menu_name': '菜单修改',
        'menu_code': 'system:menu:edit',
        'menu_type': 3,
        'permission': 'system:menu:edit',
        'sort_order': 3,
        'parent_code': 'system:menu'
    },
    {
        'menu_name': '菜单删除',
        'menu_code': 'system:menu:remove',
        'menu_type': 3,
        'permission': 'system:menu:remove',
        'sort_order': 4,
        'parent_code': 'system:menu'
    },

    # 部门管理菜单
    {
        'menu_name': '部门管理',
        'menu_code': 'system:dept',
        'menu_type': 2,
        'path': '/system/dept',
        'component': 'system/dept/index',
        'icon': 'dept',
        'permission': 'system:dept:list',
        'sort_order': 4,
        'parent_code': 'system'
    },
    {
        'menu_name': '部门查询',
        'menu_code': 'system:dept:query',
        'menu_type': 3,
        'permission': 'system:dept:query',
        'sort_order': 1,
        'parent_code': 'system:dept'
    },
    {
        'menu_name': '部门新增',
        'menu_code': 'system:dept:add',
        'menu_type': 3,
        'permission': 'system:dept:add',
        'sort_order': 2,
        'parent_code': 'system:dept'
    },
    {
        'menu_name': '部门修改',
        'menu_code': 'system:dept:edit',
        'menu_type': 3,
        'permission': 'system:dept:edit',
        'sort_order': 3,
        'parent_code': 'system:dept'
    },
    {
        'menu_name': '部门删除',
        'menu_code': 'system:dept:remove',
        'menu_type': 3,
        'permission': 'system:dept:remove',
        'sort_order': 4,
        'parent_code': 'system:dept'
    },

    # ==================== 工作室模块 ====================
    # 工作室目录
    {
        'menu_name': '工作室',
        'menu_code': 'studio',
        'menu_type': 1,  # 目录
        'path': '/studio',
        'icon': 'appstore',
        'sort_order': 10,
        'parent_code': None
    },

    # ==================== 通知公告模块 ====================
    # 通知公告菜单
    {
        'menu_name': '通知公告',
        'menu_code': 'studio:notice',
        'menu_type': 2,  # 菜单
        'path': '/studio/notice',
        'component': 'studio/notice/index',
        'icon': 'notice',
        'permission': 'studio:notice:list',
        'sort_order': 1,
        'parent_code': 'studio'
    },
    {
        'menu_name': '通知查询',
        'menu_code': 'studio:notice:query',
        'menu_type': 3,  # 按钮
        'permission': 'studio:notice:query',
        'sort_order': 1,
        'parent_code': 'studio:notice'
    },
    {
        'menu_name': '通知新增',
        'menu_code': 'studio:notice:add',
        'menu_type': 3,
        'permission': 'studio:notice:add',
        'sort_order': 2,
        'parent_code': 'studio:notice'
    },
    {
        'menu_name': '通知修改',
        'menu_code': 'studio:notice:edit',
        'menu_type': 3,
        'permission': 'studio:notice:edit',
        'sort_order': 3,
        'parent_code': 'studio:notice'
    },
    {
        'menu_name': '通知删除',
        'menu_code': 'studio:notice:remove',
        'menu_type': 3,
        'permission': 'studio:notice:remove',
        'sort_order': 4,
        'parent_code': 'studio:notice'
    },

    # ==================== AI对话模块 ====================
    # AI对话菜单
    {
        'menu_name': 'AI对话',
        'menu_code': 'studio:ai',
        'menu_type': 2,  # 菜单
        'path': '/studio/ai',
        'component': 'studio/ai/index',
        'icon': 'robot',
        'permission': 'studio:ai:list',
        'sort_order': 2,
        'parent_code': 'studio'
    },
    {
        'menu_name': 'AI查询',
        'menu_code': 'studio:ai:query',
        'menu_type': 3,  # 按钮
        'permission': 'studio:ai:query',
        'sort_order': 1,
        'parent_code': 'studio:ai'
    },
    {
        'menu_name': 'AI新增',
        'menu_code': 'studio:ai:add',
        'menu_type': 3,
        'permission': 'studio:ai:add',
        'sort_order': 2,
        'parent_code': 'studio:ai'
    },
    {
        'menu_name': 'AI修改',
        'menu_code': 'studio:ai:edit',
        'menu_type': 3,
        'permission': 'studio:ai:edit',
        'sort_order': 3,
        'parent_code': 'studio:ai'
    },
    {
        'menu_name': 'AI删除',
        'menu_code': 'studio:ai:remove',
        'menu_type': 3,
        'permission': 'studio:ai:remove',
        'sort_order': 4,
        'parent_code': 'studio:ai'
    },

    # ==================== 系统监控模块 ====================
    # 系统监控菜单
    {
        'menu_name': '系统监控',
        'menu_code': 'studio:system_monitor',
        'menu_type': 2,  # 菜单
        'path': '/studio/monitor',
        'component': 'studio/system_monitor/index',
        'icon': 'monitor',
        'permission': 'studio:system_monitor:list',
        'sort_order': 3,
        'parent_code': 'studio'
    },
    {
        'menu_name': '监控查询',
        'menu_code': 'studio:system_monitor:query',
        'menu_type': 3,  # 按钮
        'permission': 'studio:system_monitor:query',
        'sort_order': 1,
        'parent_code': 'studio:system_monitor'
    },
    {
        'menu_name': '监控新增',
        'menu_code': 'studio:system_monitor:add',
        'menu_type': 3,
        'permission': 'studio:system_monitor:add',
        'sort_order': 2,
        'parent_code': 'studio:system_monitor'
    },
    {
        'menu_name': '监控修改',
        'menu_code': 'studio:system_monitor:edit',
        'menu_type': 3,
        'permission': 'studio:system_monitor:edit',
        'sort_order': 3,
        'parent_code': 'studio:system_monitor'
    },
    {
        'menu_name': '监控删除',
        'menu_code': 'studio:system_monitor:remove',
        'menu_type': 3,
        'permission': 'studio:system_monitor:remove',
        'sort_order': 4,
        'parent_code': 'studio:system_monitor'
    },

    # 知识管理菜单
    {
        'menu_name': '知识管理',
        'menu_code': 'system:wiki',
        'menu_type': 2,  # 菜单
        'path': '/system/wiki',
        'component': 'system/wiki/index',
        'icon': 'book',
        'permission': 'system:wiki:list',
        'sort_order': 6,
        'parent_code': 'system'
    },

    # 知识分类管理
    {
        'menu_name': '知识分类',
        'menu_code': 'system:wiki:category',
        'menu_type': 2,  # 菜单
        'path': '/system/wiki/category',
        'component': 'system/wiki/category/index',
        'icon': 'folder',
        'permission': 'system:wiki:category:list',
        'sort_order': 1,
        'parent_code': 'system:wiki'
    },
    {
        'menu_name': '分类查询',
        'menu_code': 'system:wiki:category:query',
        'menu_type': 3,  # 按钮
        'permission': 'system:wiki:category:query',
        'sort_order': 1,
        'parent_code': 'system:wiki:category'
    },
    {
        'menu_name': '分类新增',
        'menu_code': 'system:wiki:category:add',
        'menu_type': 3,
        'permission': 'system:wiki:category:add',
        'sort_order': 2,
        'parent_code': 'system:wiki:category'
    },
    {
        'menu_name': '分类修改',
        'menu_code': 'system:wiki:category:edit',
        'menu_type': 3,
        'permission': 'system:wiki:category:update',
        'sort_order': 3,
        'parent_code': 'system:wiki:category'
    },
    {
        'menu_name': '分类删除',
        'menu_code': 'system:wiki:category:remove',
        'menu_type': 3,
        'permission': 'system:wiki:category:remove',
        'sort_order': 4,
        'parent_code': 'system:wiki:category'
    },

    # 知识文章管理
    {
        'menu_name': '知识文章',
        'menu_code': 'system:wiki:article',
        'menu_type': 2,  # 菜单
        'path': '/system/wiki/article',
        'component': 'system/wiki/article/index',
        'icon': 'file-text',
        'permission': 'system:wiki:article:list',
        'sort_order': 2,
        'parent_code': 'system:wiki'
    },
    {
        'menu_name': '文章查询',
        'menu_code': 'system:wiki:article:query',
        'menu_type': 3,  # 按钮
        'permission': 'system:wiki:article:query',
        'sort_order': 1,
        'parent_code': 'system:wiki:article'
    },
    {
        'menu_name': '文章新增',
        'menu_code': 'system:wiki:article:add',
        'menu_type': 3,
        'permission': 'system:wiki:article:add',
        'sort_order': 2,
        'parent_code': 'system:wiki:article'
    },
    {
        'menu_name': '文章修改',
        'menu_code': 'system:wiki:article:edit',
        'menu_type': 3,
        'permission': 'system:wiki:article:edit',
        'sort_order': 3,
        'parent_code': 'system:wiki:article'
    },
    {
        'menu_name': '文章删除',
        'menu_code': 'system:wiki:article:remove',
        'menu_type': 3,
        'permission': 'system:wiki:article:remove',
        'sort_order': 4,
        'parent_code': 'system:wiki:article'
    },
    {
        'menu_name': '文章发布',
        'menu_code': 'system:wiki:article:publish',
        'menu_type': 3,
        'permission': 'system:wiki:article:publish',
        'sort_order': 5,
        'parent_code': 'system:wiki:article'
    },

    # 日志管理菜单
    {
        'menu_name': '日志管理',
        'menu_code': 'system:log',
        'menu_type': 2,  # 菜单
        'path': '/system/log',
        'component': 'system/log/index',
        'icon': 'log',
        'permission': 'log.view_operationlog',
        'sort_order': 7,
        'parent_code': 'system'
    },
    {
        'menu_name': '日志查询',
        'menu_code': 'system:log:query',
        'menu_type': 3,  # 按钮
        'permission': 'log.view_operationlog',
        'sort_order': 1,
        'parent_code': 'system:log'
    },
    {
        'menu_name': '日志详情',
        'menu_code': 'system:log:detail',
        'menu_type': 3,
        'permission': 'log.view_operationlog',
        'sort_order': 2,
        'parent_code': 'system:log'
    },

    # YOLO古建筑识别模块
    {
        'menu_name': 'YOLO识别',
        'menu_code': 'studio:yolo',
        'menu_type': 2,  # 菜单
        'path': '/studio/yolo',
        'component': 'studio/yolo/index',
        'icon': 'camera',
        'permission': 'studio:yolo:list',
        'sort_order': 4,
        'parent_code': 'studio'
    },
    {
        'menu_name': '图像识别',
        'menu_code': 'studio:yolo:recognition',
        'menu_type': 3,  # 按钮
        'permission': 'studio:yolo:recognition',
        'sort_order': 1,
        'parent_code': 'studio:yolo'
    },
    {
        'menu_name': '识别历史',
        'menu_code': 'studio:yolo:history',
        'menu_type': 3,
        'permission': 'studio:yolo:history',
        'sort_order': 2,
        'parent_code': 'studio:yolo'
    },
    {
        'menu_name': '问答记录',
        'menu_code': 'studio:yolo:question',
        'menu_type': 3,
        'permission': 'studio:yolo:question',
        'sort_order': 3,
        'parent_code': 'studio:yolo'
    },
    {
        'menu_name': '记录收藏',
        'menu_code': 'studio:yolo:favorite',
        'menu_type': 3,
        'permission': 'studio:yolo:favorite',
        'sort_order': 4,
        'parent_code': 'studio:yolo'
    },
    {
        'menu_name': '记录删除',
        'menu_code': 'studio:yolo:delete',
        'menu_type': 3,
        'permission': 'studio:yolo:delete',
        'sort_order': 5,
        'parent_code': 'studio:yolo'
    },
    {
        'menu_name': '统计信息',
        'menu_code': 'studio:yolo:statistics',
        'menu_type': 3,
        'permission': 'studio:yolo:statistics',
        'sort_order': 6,
        'parent_code': 'studio:yolo'
    }
]


