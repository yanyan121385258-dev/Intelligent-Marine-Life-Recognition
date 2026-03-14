import { request } from '@/utils/hertz_request';

import type { ApiResponse } from '@/types/api_response';

// 后端返回的原始菜单数据格式
export interface RawMenu {
  menu_id: number;
  menu_name: string;
  menu_code: string;
  menu_type: number; // 后端返回数字：1=菜单, 2=按钮, 3=接口
  parent_id?: number | null;
  path?: string;
  component?: string | null;
  icon?: string;
  permission?: string;
  sort_order?: number;
  description?: string;
  status?: number;
  is_external?: boolean;
  is_cache?: boolean;
  is_visible?: boolean;
  created_at?: string;
  updated_at?: string;
  children?: RawMenu[];
}

// 前端使用的菜单接口类型定义
export interface Menu {
  menu_id: number;
  menu_name: string;
  menu_code: string;
  menu_type: number; // 1=菜单, 2=按钮, 3=接口
  parent_id?: number;
  path?: string;
  component?: string;
  icon?: string;
  permission?: string;
  sort_order?: number;
  description?: string;
  status?: number;
  is_external?: boolean;
  is_cache?: boolean;
  is_visible?: boolean;
  created_at?: string;
  updated_at?: string;
  children?: Menu[];
}

// 菜单列表数据结构
export interface MenuListData {
  list: Menu[];
  total: number;
  page: number;
  page_size: number;
}

// 菜单列表响应类型
export type MenuListResponse = ApiResponse<MenuListData>;

// 菜单列表查询参数
export interface MenuListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: number;
  menu_type?: string;
  parent_id?: number;
}

// 创建菜单参数
export interface CreateMenuParams {
  menu_name: string;
  menu_code: string;
  menu_type: number; // 1=菜单, 2=按钮, 3=接口
  parent_id?: number;
  path?: string;
  component?: string;
  icon?: string;
  permission?: string;
  sort_order?: number;
  description?: string;
  status?: number;
  is_external?: boolean;
  is_cache?: boolean;
  is_visible?: boolean;
}

// 更新菜单参数
export type UpdateMenuParams = Partial<CreateMenuParams>;

// 菜单树响应类型
export type MenuTreeResponse = ApiResponse<Menu[]>;

// 数据转换工具函数
const convertMenuType = (type: number): 'menu' | 'button' | 'api' => {
  switch (type) {
    case 1:
      return 'menu';
    case 2:
      return 'button';
    case 3:
      return 'api';
    default:
      return 'menu';
  }
};

// 解码Unicode字符串
const decodeUnicode = (str: string): string => {
  try {
    return str.replace(/\\u[\dA-F]{4}/gi, (match) => {
      return String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16));
    });
  } catch (error) {
    return str;
  }
};

// 转换原始菜单数据为前端格式
const transformRawMenu = (rawMenu: RawMenu): Menu => {
  // 确保status字段被正确转换
  let statusValue: number;
  if (rawMenu.status === undefined || rawMenu.status === null) {
    // 如果status缺失，默认为启用（1）
    statusValue = 1;
  } else {
    // 如果有值，转换为数字
    if (typeof rawMenu.status === 'string') {
      const parsed = parseInt(rawMenu.status, 10);
      statusValue = isNaN(parsed) ? 1 : parsed;
    } else {
      statusValue = Number(rawMenu.status);
      // 如果转换失败，默认为启用
      if (isNaN(statusValue)) {
        statusValue = 1;
      }
    }
  }

  return {
    menu_id: rawMenu.menu_id,
    menu_name: decodeUnicode(rawMenu.menu_name),
    menu_code: rawMenu.menu_code,
    menu_type: rawMenu.menu_type,
    parent_id: rawMenu.parent_id || undefined,
    path: rawMenu.path,
    component: rawMenu.component,
    icon: rawMenu.icon,
    permission: rawMenu.permission,
    sort_order: rawMenu.sort_order,
    description: rawMenu.description,
    status: statusValue, // 使用转换后的值
    is_external: rawMenu.is_external,
    is_cache: rawMenu.is_cache,
    is_visible: rawMenu.is_visible,
    created_at: rawMenu.created_at,
    updated_at: rawMenu.updated_at,
    children: rawMenu.children ? rawMenu.children.map(transformRawMenu) : [],
  };
};

// 将菜单数据数组转换为列表格式
const transformToMenuList = (rawMenus: RawMenu[]): MenuListData => {
  const transformedMenus = rawMenus.map(transformRawMenu);

  // 递归收集所有菜单项
  const collectAllMenus = (menu: Menu): Menu[] => {
    const result = [menu];
    if (menu.children && menu.children.length > 0) {
      menu.children.forEach((child) => {
        result.push(...collectAllMenus(child));
      });
    }
    return result;
  };

  // 收集所有菜单项
  const allMenus: Menu[] = [];
  transformedMenus.forEach((menu) => {
    allMenus.push(...collectAllMenus(menu));
  });

  return {
    list: allMenus,
    total: allMenus.length,
    page: 1,
    page_size: allMenus.length,
  };
};

// 构建菜单树结构
const buildMenuTree = (rawMenus: RawMenu[]): Menu[] => {
  const transformedMenus = rawMenus.map(transformRawMenu);

  // 创建菜单映射
  const menuMap = new Map<number, Menu>();
  transformedMenus.forEach((menu) => {
    menuMap.set(menu.menu_id, { ...menu, children: [] });
  });

  // 构建树结构
  const rootMenus: Menu[] = [];
  transformedMenus.forEach((menu) => {
    const menuItem = menuMap.get(menu.menu_id)!;

    if (menu.parent_id && menuMap.has(menu.parent_id)) {
      const parent = menuMap.get(menu.parent_id)!;
      if (!parent.children) parent.children = [];
      parent.children.push(menuItem);
    } else {
      rootMenus.push(menuItem);
    }
  });

  return rootMenus;
};

// 菜单API
export const menuApi = {
  // 获取菜单列表
  getMenuList: async (params?: MenuListParams): Promise<MenuListResponse> => {
    try {
      const response = await request.get<ApiResponse<RawMenu[]>>('/api/menus/', { params });

      if (response.success && response.data && Array.isArray(response.data)) {
        const menuListData = transformToMenuList(response.data);
        return {
          success: true,
          code: response.code,
          message: response.message,
          data: menuListData,
        };
      }

      return {
        success: false,
        code: response.code || 500,
        message: response.message || '获取菜单数据失败',
        data: {
          list: [],
          total: 0,
          page: 1,
          page_size: 10,
        },
      };
    } catch (error) {
      console.error('获取菜单列表失败:', error);
      return {
        success: false,
        code: 500,
        message: '网络请求失败',
        data: {
          list: [],
          total: 0,
          page: 1,
          page_size: 10,
        },
      };
    }
  },

  // 获取菜单树
  getMenuTree: async (): Promise<MenuTreeResponse> => {
    try {
      const response = await request.get<ApiResponse<RawMenu[]>>('/api/menus/tree/');

      if (response.success && response.data && Array.isArray(response.data)) {
        // 调试：检查原始数据中的status值
        if (response.data.length > 0) {
          console.log(
            '🔍 原始菜单数据status检查（前5条）:',
            response.data.slice(0, 5).map((m: RawMenu) => ({
              menu_name: m.menu_name,
              menu_id: m.menu_id,
              status: m.status,
              statusType: typeof m.status,
            }))
          );
        }

        // 后端已经返回树形结构，直接转换数据格式即可
        const transformedData = response.data.map(transformRawMenu);

        // 调试：检查转换后的status值
        if (transformedData.length > 0) {
          console.log(
            '🔍 转换后菜单数据status检查（前5条）:',
            transformedData.slice(0, 5).map((m: Menu) => ({
              menu_name: m.menu_name,
              menu_id: m.menu_id,
              status: m.status,
              statusType: typeof m.status,
            }))
          );
        }

        return {
          success: true,
          code: response.code,
          message: response.message,
          data: transformedData,
        };
      }

      return {
        success: false,
        code: response.code || 500,
        message: response.message || '获取菜单树失败',
        data: [],
      };
    } catch (error) {
      console.error('获取菜单树失败:', error);
      return {
        success: false,
        code: 500,
        message: '网络请求失败',
        data: [],
      };
    }
  },

  // 获取单个菜单
  getMenu: async (id: number): Promise<ApiResponse<Menu>> => {
    try {
      const response = await request.get<ApiResponse<RawMenu>>(`/api/menus/${id}/`);

      if (response.success && response.data) {
        const transformedMenu = transformRawMenu(response.data);
        return {
          success: true,
          code: response.code,
          message: response.message,
          data: transformedMenu,
        };
      }

      return response as ApiResponse<Menu>;
    } catch (error) {
      console.error('获取菜单详情失败:', error);
      return {
        success: false,
        code: 500,
        message: '网络请求失败',
        data: {} as Menu,
      };
    }
  },

  // 创建菜单
  createMenu: (data: CreateMenuParams): Promise<ApiResponse<Menu>> => {
    return request.post('/api/menus/create/', data);
  },

  // 更新菜单
  updateMenu: (id: number, data: UpdateMenuParams): Promise<ApiResponse<Menu>> => {
    return request.put(`/api/menus/${id}/update/`, data);
  },

  // 删除菜单
  deleteMenu: (id: number): Promise<ApiResponse<any>> => {
    return request.delete(`/api/menus/${id}/delete/`);
  },

  // 批量删除菜单
  batchDeleteMenus: (ids: number[]): Promise<ApiResponse<any>> => {
    return request.post('/api/menus/batch-delete/', { menu_ids: ids });
  },
};
