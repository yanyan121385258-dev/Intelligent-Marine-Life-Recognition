import { menuApi, type Menu } from '@/api/menu';

// 菜单key和菜单ID的映射关系
const menuKeyToIdMap: Map<string, number> = new Map();
const menuIdToKeyMap: Map<number, string> = new Map();
const isInitialized = false;

// 菜单key和菜单code的映射关系（用于建立映射）
const MENU_KEY_TO_CODE_MAP: { [key: string]: string } = {
  dashboard: 'dashboard',
  'user-management': 'user_management',
  'department-management': 'department_management',
  'menu-management': 'menu_management',
  teacher: 'role_management',
};

/**
 * 初始化菜单映射
 */
export const initializeMenuMapping = async (): Promise<void> => {
  try {
    // 获取菜单树数据
    const response = await menuApi.getMenuTree();

    if (response.success && response.data) {
      // 清空现有映射
      menuKeyToIdMap.clear();
      menuIdToKeyMap.clear();

      // 构建菜单映射
      buildMenuMapping(response.data);
    }
  } catch (error) {
    console.error('初始化菜单映射时发生错误:', error);
  }
};

/**
 * 递归构建菜单映射关系
 */
const buildMenuMapping = (menus: Menu[]): void => {
  menus.forEach((menu) => {
    // 根据menu_code找到对应的key
    const menuKey = Object.keys(MENU_KEY_TO_CODE_MAP).find(
      (key) => MENU_KEY_TO_CODE_MAP[key] === menu.menu_code
    );

    if (menuKey) {
      menuKeyToIdMap.set(menuKey, menu.menu_id);
      menuIdToKeyMap.set(menu.menu_id, menuKey);
    }

    // 递归处理子菜单
    if (menu.children && menu.children.length > 0) {
      buildMenuMapping(menu.children);
    }
  });
};

/**
 * 根据菜单key获取菜单ID
 */
export const getMenuIdByKey = (menuKey: string): number | undefined => {
  return menuKeyToIdMap.get(menuKey);
};

/**
 * 根据菜单ID获取菜单key
 */
export const getMenuKeyById = (menuId: number): string | undefined => {
  return menuIdToKeyMap.get(menuId);
};

/**
 * 检查用户是否有指定菜单的权限
 */
export const hasMenuPermissionById = (menuKey: string, userMenuPermissions: number[]): boolean => {
  const menuId = getMenuIdByKey(menuKey);

  if (!menuId) {
    // 降级策略：如果没有找到菜单映射，则允许显示（向后兼容）
    return true;
  }

  return userMenuPermissions.includes(menuId);
};

/**
 * 获取用户有权限的菜单keys
 */
export const getPermittedMenuKeys = (userMenuPermissions: number[]): string[] => {
  const permittedKeys: string[] = [];
  userMenuPermissions.forEach((menuId) => {
    const menuKey = getMenuKeyById(menuId);
    if (menuKey) {
      permittedKeys.push(menuKey);
    }
  });
  return permittedKeys;
};
