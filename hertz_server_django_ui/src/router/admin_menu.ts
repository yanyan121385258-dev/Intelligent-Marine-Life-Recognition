import type { RouteRecordRaw } from 'vue-router';
import { getEnabledModuleKeys, isModuleEnabled } from '@/config/hertz_modules';

// 角色权限枚举
export enum UserRole {
  ADMIN = 'admin',
  SYSTEM_ADMIN = 'system_admin',
  NORMAL_USER = 'normal_user',
  SUPER_ADMIN = 'super_admin',
}

// 统一菜单配置接口 - 只需要在这里配置一次
export interface AdminMenuItem {
  key: string; // 菜单唯一标识
  title: string; // 菜单标题
  icon?: string; // 菜单图标
  path: string; // 路由路径
  component: string; // 组件路径（相对于@/views/admin_page/）
  isDefault?: boolean; // 是否为默认路由（首页）
  roles?: UserRole[]; // 允许访问的角色，不设置则使用默认管理员角色
  permission?: string; // 所需权限标识符
  children?: AdminMenuItem[]; // 子菜单
  moduleKey?: string;
}

// 🎯 统一配置中心 - 只需要在这里修改菜单配置
export const ADMIN_MENU_CONFIG: AdminMenuItem[] = [
  {
    key: 'dashboard',
    title: '仪表盘',
    icon: 'DashboardOutlined',
    path: '/admin',
    component: 'Dashboard.vue',
    isDefault: true, // 标记为默认首页
  },
  {
    key: 'user-management',
    title: '用户管理',
    icon: 'UserOutlined',
    path: '/admin/user-management',
    component: 'UserManagement.vue',
    permission: 'system:user:list', // 需要用户列表权限
    moduleKey: 'admin.user-management',
  },
  {
    key: 'department-management',
    title: '部门管理',
    icon: 'SettingOutlined',
    path: '/admin/department-management',
    component: 'DepartmentManagement.vue',
    permission: 'system:dept:list', // 需要部门列表权限
    moduleKey: 'admin.department-management',
  },
  {
    key: 'menu-management',
    title: '菜单管理',
    icon: 'SettingOutlined',
    path: '/admin/menu-management',
    component: 'MenuManagement.vue',
    permission: 'system:menu:list', // 需要菜单列表权限
    moduleKey: 'admin.menu-management',
  },
  {
    key: 'teacher',
    title: '角色管理',
    icon: 'UserOutlined',
    path: '/admin/teacher',
    component: 'Role.vue',
    permission: 'system:role:list', // 需要角色列表权限
    moduleKey: 'admin.role-management',
  },
  {
    key: 'notification-management',
    title: '通知管理',
    icon: 'UserOutlined',
    path: '/admin/notification-management',
    component: 'NotificationManagement.vue',
    permission: 'studio:notice:list', // 需要通知列表权限
    moduleKey: 'admin.notification-management',
  },
  {
    key: 'log-management',
    title: '日志管理',
    icon: 'FileSearchOutlined',
    path: '/admin/log-management',
    component: 'LogManagement.vue',
    permission: 'log.view_operationlog', // 查看操作日志权限
    moduleKey: 'admin.log-management',
  },
  {
    key: 'knowledge-base',
    title: '文章管理',
    icon: 'DatabaseOutlined',
    path: '/admin/article-management',
    component: 'ArticleManagement.vue',
    // 菜单访问权限：需要具备文章列表权限
    permission: 'system:knowledge:article:list',
    moduleKey: 'admin.knowledge-base',
  },
  {
    key: 'yolo-model',
    title: 'YOLO模型',
    icon: 'ClusterOutlined',
    path: '/admin/yolo-model',
    component: 'ModelManagement.vue', // 默认显示模型管理页面
    // 父菜单不设置权限，由子菜单的权限决定是否显示
    moduleKey: 'admin.yolo-model',
    children: [
      {
        key: 'model-management',
        title: '模型管理',
        icon: 'RobotOutlined',
        path: '/admin/model-management',
        component: 'ModelManagement.vue',
        permission: 'system:yolo:model:list',
      },
      {
        key: 'dataset-management',
        title: '数据集管理',
        icon: 'DatabaseOutlined',
        path: '/admin/dataset-management',
        component: 'DatasetManagement.vue',
      },
      {
        key: 'yolo-train-management',
        title: 'YOLO训练',
        icon: 'HistoryOutlined',
        path: '/admin/yolo-train',
        component: 'YoloTrainManagement.vue',
      },
      {
        key: 'alert-level-management',
        title: '模型类别管理',
        icon: 'WarningOutlined',
        path: '/admin/alert-level-management',
        component: 'AlertLevelManagement.vue',
        permission: 'system:yolo:alert:list',
      },
      {
        key: 'alert-processing-center',
        title: '告警处理中心',
        icon: 'BellOutlined',
        path: '/admin/alert-processing-center',
        component: 'AlertProcessingCenter.vue',
        permission: 'system:yolo:alert:process',
      },
      {
        key: 'detection-history-management',
        title: '检测历史管理',
        icon: 'HistoryOutlined',
        path: '/admin/detection-history-management',
        component: 'DetectionHistoryManagement.vue',
        permission: 'system:yolo:history:list',
      },
    ],
  },
];

// 默认管理员角色 - 修改为空数组，通过自定义权限检查函数处理
const DEFAULT_ADMIN_ROLES: UserRole[] = [];

// 组件映射 - 静态导入以支持Vite分析
const COMPONENT_MAP: { [key: string]: () => Promise<any> } = {
  'Dashboard.vue': () => import('@/views/admin_page/Dashboard.vue'),
  'UserManagement.vue': () => import('@/views/admin_page/UserManagement.vue'),
  'DepartmentManagement.vue': () => import('@/views/admin_page/DepartmentManagement.vue'),
  'Role.vue': () => import('@/views/admin_page/Role.vue'),
  'MenuManagement.vue': () => import('@/views/admin_page/MenuManagement.vue'),
  'NotificationManagement.vue': () => import('@/views/admin_page/NotificationManagement.vue'),
  'LogManagement.vue': () => import('@/views/admin_page/LogManagement.vue'),
  'ArticleManagement.vue': () => import('@/views/admin_page/ArticleManagement.vue'),
  'ModelManagement.vue': () => import('@/views/admin_page/ModelManagement.vue'),
  'DatasetManagement.vue': () => import('@/views/admin_page/DatasetManagement.vue'),
  'YoloTrainManagement.vue': () => import('@/views/admin_page/YoloTrainManagement.vue'),
  'AlertLevelManagement.vue': () => import('@/views/admin_page/AlertLevelManagement.vue'),
  'AlertProcessingCenter.vue': () => import('@/views/admin_page/AlertProcessingCenter.vue'),
  'DetectionHistoryManagement.vue': () =>
    import('@/views/admin_page/DetectionHistoryManagement.vue'),
};

// 🚀 自动生成路由配置
function generateAdminRoutes(): RouteRecordRaw {
  const children: RouteRecordRaw[] = [];
  const enabledModuleKeys = getEnabledModuleKeys();

  ADMIN_MENU_CONFIG.forEach((item) => {
    if (!isModuleEnabled(item.moduleKey, enabledModuleKeys)) {
      return;
    }
    // 如果有子菜单，将子菜单作为独立的路由项
    if (item.children && item.children.length > 0) {
      // 为每个子菜单创建独立的路由
      item.children.forEach((child) => {
        children.push({
          path: child.path.replace('/admin/', ''),
          name: child.key,
          component:
            COMPONENT_MAP[child.component] || (() => import('@/views/admin_page/Dashboard.vue')),
          meta: {
            title: child.title,
            requiresAuth: true,
            roles: child.roles || DEFAULT_ADMIN_ROLES,
          },
        });
      });
    } else {
      // 没有子菜单的普通菜单项
      children.push({
        path: item.isDefault ? '' : item.path.replace('/admin/', ''),
        name: item.key,
        component:
          COMPONENT_MAP[item.component] || (() => import('@/views/admin_page/Dashboard.vue')),
        meta: {
          title: item.title,
          requiresAuth: true,
          roles: item.roles || DEFAULT_ADMIN_ROLES,
        },
      });
    }
  });

  return {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin_page/index.vue'),
    meta: {
      title: '管理后台',
      requiresAuth: true,
      roles: DEFAULT_ADMIN_ROLES,
    },
    children,
  };
}

// 🚀 自动生成菜单配置
export interface MenuConfig {
  key: string;
  title: string;
  icon?: string;
  path: string;
  children?: MenuConfig[];
}

function generateMenuConfig(): MenuConfig[] {
  return ADMIN_MENU_CONFIG.map((item) => ({
    key: item.key,
    title: item.title,
    icon: item.icon,
    path: item.path,
    children: item.children?.map((child) => ({
      key: child.key,
      title: child.title,
      icon: child.icon,
      path: child.path,
    })),
  }));
}

// 🚀 自动生成路径映射函数
function generatePathKeyMapping(): { [path: string]: string } {
  const mapping: { [path: string]: string } = {};

  function addToMapping(items: AdminMenuItem[], parentPath = '') {
    items.forEach((item) => {
      mapping[item.path] = item.key;
      if (item.children) {
        addToMapping(item.children, item.path);
      }
    });
  }

  addToMapping(ADMIN_MENU_CONFIG);
  return mapping;
}

// 导出的配置和函数
export const adminMenuRoutes: RouteRecordRaw = generateAdminRoutes();
export const adminMenuConfig: MenuConfig[] = generateMenuConfig();

// 路径到key的映射
const pathKeyMapping = generatePathKeyMapping();

// 🎯 根据路径获取菜单key - 自动生成
export const getMenuKeyByPath = (path: string): string => {
  // 精确匹配
  if (pathKeyMapping[path]) {
    return pathKeyMapping[path];
  }

  // 模糊匹配
  for (const [mappedPath, key] of Object.entries(pathKeyMapping)) {
    if (path.includes(mappedPath) && mappedPath !== '/admin') {
      return key;
    }
  }

  // 默认返回dashboard
  return 'dashboard';
};

// 🎯 根据菜单key获取路径 - 自动生成
export const getPathByMenuKey = (key: string): string => {
  const menuItem = ADMIN_MENU_CONFIG.find((item) => item.key === key);
  if (menuItem) {
    // 如果有子菜单，返回第一个子菜单的路径
    if (menuItem.children && menuItem.children.length > 0) {
      const firstChildPath = menuItem.children[0].path;
      return firstChildPath;
    }
    return menuItem.path;
  }

  // 在子菜单中查找
  for (const item of ADMIN_MENU_CONFIG) {
    if (item.children) {
      const childItem = item.children.find((child) => child.key === key);
      if (childItem) {
        return childItem.path;
      }
    }
  }

  return '/admin';
};

// 🎯 根据菜单key获取标题 - 自动生成
export const getTitleByMenuKey = (key: string): string => {
  const menuItem = ADMIN_MENU_CONFIG.find((item) => item.key === key);
  if (menuItem) return menuItem.title;

  // 在子菜单中查找
  for (const item of ADMIN_MENU_CONFIG) {
    if (item.children) {
      const childItem = item.children.find((child) => child.key === key);
      if (childItem) return childItem.title;
    }
  }

  return '仪表盘';
};

// 菜单权限检查
export const hasMenuPermission = (menuKey: string, userRole: string): boolean => {
  const menuItem = ADMIN_MENU_CONFIG.find((item) => item.key === menuKey);
  if (!menuItem) return false;

  return menuItem.roles
    ? menuItem.roles.includes(userRole as UserRole)
    : DEFAULT_ADMIN_ROLES.includes(userRole as UserRole);
};

// 🎯 新增：根据用户权限过滤菜单配置
export const getFilteredMenuConfig = (
  userRoles: string[],
  userPermissions: string[],
  userMenuPermissions?: number[]
): MenuConfig[] => {
  const userRole = userRoles[0]; // 取第一个角色作为主要角色

  // 仅管理员角色显示管理端菜单
  const adminRoles = ['admin', 'system_admin', 'super_admin'];
  const isAdminRole = userRoles.some((r) => adminRoles.includes(r));
  if (!isAdminRole) {
    return [];
  }

  // 对 super_admin / system_admin 开放所有管理菜单（忽略权限字符串过滤）
  const isPrivilegedAdmin = userRoles.includes('super_admin') || userRoles.includes('system_admin');

  const enabledModuleKeys = getEnabledModuleKeys();

  // 过滤菜单项 - 基于模块开关和权限字符串检查
  const filteredMenus = ADMIN_MENU_CONFIG.filter((menuItem) => {
    if (!isModuleEnabled(menuItem.moduleKey, enabledModuleKeys)) {
      return false;
    }

    // 如果菜单没有配置权限要求，则默认允许访问（如仪表盘）
    if (!menuItem.permission) {
      return true;
    }

    // 检查用户是否有该菜单所需的权限
    const hasMenuPermission = isPrivilegedAdmin
      ? true
      : hasPermission(menuItem.permission, userPermissions);

    if (!hasMenuPermission) {
      return false;
    }

    // 如果有子菜单，检查是否有子菜单有权限
    if (menuItem.children && menuItem.children.length > 0) {
      const filteredChildren = menuItem.children.filter((child) => {
        // 如果子菜单没有配置权限要求，则默认允许访问
        if (!child.permission) {
          return true;
        }

        const childHasPermission = hasPermission(child.permission, userPermissions);
        return childHasPermission;
      });

      // 如果没有任何子菜单有权限，则不显示父菜单
      if (filteredChildren.length === 0) {
        return false;
      }
    }

    return true;
  }).map((menuItem) => {
    // 创建新对象，避免修改原始配置
    const menuConfig: MenuConfig = {
      key: menuItem.key,
      title: menuItem.title,
      icon: menuItem.icon,
      path: menuItem.path,
    };

    // 如果有子菜单，创建新的子菜单配置
    if (menuItem.children && menuItem.children.length > 0) {
      const filteredChildren = menuItem.children.filter((child) => {
        // 如果子菜单没有配置权限要求，则默认允许访问
        if (!child.permission) {
          return true;
        }
        return isPrivilegedAdmin ? true : hasPermission(child.permission, userPermissions);
      });

      menuConfig.children = filteredChildren.map((child) => ({
        key: child.key,
        title: child.title,
        icon: child.icon,
        path: child.path,
      }));
    }

    return menuConfig;
  });

  return filteredMenus;
};

// 🎯 新增：检查用户是否有任何管理员菜单权限
// 修改逻辑：只有normal_user角色不能访问管理端，其他所有角色都可以访问
export const hasAnyAdminPermission = (userRoles: string[]): boolean => {
  // 仅当包含 admin/system_admin/super_admin 之一才视为管理员
  const adminRoles = ['admin', 'system_admin', 'super_admin'];
  return userRoles.some((role) => adminRoles.includes(role));
};

/**
 * 检查用户是否有指定权限
 */
const hasPermission = (permission: string, userPermissions: string[]): boolean => {
  return userPermissions.includes(permission);
};
