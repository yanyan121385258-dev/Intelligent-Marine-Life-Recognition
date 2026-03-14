import type { RouteRecordRaw } from 'vue-router';
import { defineAsyncComponent } from 'vue';
import { getEnabledModuleKeys, isModuleEnabled } from '@/config/hertz_modules';

export interface UserMenuConfig {
  key: string;
  label: string;
  icon?: string;
  path: string;
  component: string;
  children?: UserMenuConfig[];
  disabled?: boolean;
  meta?: {
    title?: string;
    requiresAuth?: boolean;
    roles?: string[];
    [key: string]: any;
  };
  moduleKey?: string;
}

export interface MenuItem {
  key: string;
  label: string;
  icon?: string;
  path?: string;
  children?: MenuItem[];
  disabled?: boolean;
}

export const userMenuConfigs: UserMenuConfig[] = [
  {
    key: 'dashboard',
    label: '首页',
    icon: 'DashboardOutlined',
    path: '/dashboard',
    component: 'index.vue',
    meta: { title: '用户首页', requiresAuth: true },
  },
  {
    key: 'profile',
    label: '个人信息',
    icon: 'UserOutlined',
    path: '/user/profile',
    component: 'Profile.vue',
    meta: { title: '个人信息', requiresAuth: true, hideInMenu: true },
  },
  // { key: 'documents', label: '文档管理', icon: 'FileTextOutlined', path: '/user/documents', component: 'Documents.vue', meta: { title: '文档管理', requiresAuth: true } },
  {
    key: 'system-monitor',
    label: '系统监控',
    icon: 'DashboardOutlined',
    path: '/user/system-monitor',
    component: 'SystemMonitor.vue',
    meta: { title: '系统监控', requiresAuth: true },
    moduleKey: 'user.system-monitor',
  },
  {
    key: 'ai-chat',
    label: 'AI助手',
    icon: 'MessageOutlined',
    path: '/user/ai-chat',
    component: 'AiChat.vue',
    meta: { title: 'AI助手', requiresAuth: true },
    moduleKey: 'user.ai-chat',
  },
  {
    key: 'yolo-detection',
    label: 'YOLO检测',
    icon: 'ScanOutlined',
    path: '/user/yolo-detection',
    component: 'YoloDetection.vue',
    meta: { title: 'YOLO检测中心', requiresAuth: true },
    moduleKey: 'user.yolo-detection',
  },
  {
    key: 'live-detection',
    label: '实时检测',
    icon: 'VideoCameraOutlined',
    path: '/user/live-detection',
    component: 'LiveDetection.vue',
    meta: { title: '实时检测', requiresAuth: true },
    moduleKey: 'user.live-detection',
  },
  {
    key: 'detection-history',
    label: '检测历史',
    icon: 'HistoryOutlined',
    path: '/user/detection-history',
    component: 'DetectionHistory.vue',
    meta: { title: '检测历史记录', requiresAuth: true },
    moduleKey: 'user.detection-history',
  },
  {
    key: 'alert-center',
    label: '告警中心',
    icon: 'ExclamationCircleOutlined',
    path: '/user/alert-center',
    component: 'AlertCenter.vue',
    meta: { title: '告警中心', requiresAuth: true },
    moduleKey: 'user.alert-center',
  },
  {
    key: 'notice-center',
    label: '通知中心',
    icon: 'BellOutlined',
    path: '/user/notice',
    component: 'NoticeCenter.vue',
    meta: { title: '通知中心', requiresAuth: true },
    moduleKey: 'user.notice-center',
  },
  {
    key: 'knowledge-center',
    label: '文章中心',
    icon: 'DatabaseOutlined',
    path: '/user/knowledge',
    component: 'ArticleCenter.vue',
    meta: { title: '文章中心', requiresAuth: true },
    moduleKey: 'user.knowledge-center',
  },
  {
    key: 'kb-center',
    label: '知识库中心',
    icon: 'DatabaseOutlined',
    path: '/user/kb-center',
    component: 'KbCenter.vue',
    meta: { title: '知识库中心', requiresAuth: true },
    moduleKey: 'user.kb-center',
  },
];

const enabledModuleKeys = getEnabledModuleKeys();

const effectiveUserMenuConfigs: UserMenuConfig[] = userMenuConfigs.filter((config) =>
  isModuleEnabled(config.moduleKey, enabledModuleKeys)
);

const explicitComponentMap: Record<string, any> = {
  'index.vue': defineAsyncComponent(() => import('@/views/user_pages/index.vue')),
  'Profile.vue': defineAsyncComponent(() => import('@/views/user_pages/Profile.vue')),
  'Documents.vue': defineAsyncComponent(() => import('@/views/user_pages/Documents.vue')),
  'Messages.vue': defineAsyncComponent(() => import('@/views/user_pages/Messages.vue')),
  'SystemMonitor.vue': defineAsyncComponent(() => import('@/views/user_pages/SystemMonitor.vue')),
  'AiChat.vue': defineAsyncComponent(() => import('@/views/user_pages/AiChat.vue')),
  'YoloDetection.vue': defineAsyncComponent(() => import('@/views/user_pages/YoloDetection.vue')),
  'LiveDetection.vue': defineAsyncComponent(() => import('@/views/user_pages/LiveDetection.vue')),
  'DetectionHistory.vue': defineAsyncComponent(
    () => import('@/views/user_pages/DetectionHistory.vue')
  ),
  'AlertCenter.vue': defineAsyncComponent(() => import('@/views/user_pages/AlertCenter.vue')),
  'NoticeCenter.vue': defineAsyncComponent(() => import('@/views/user_pages/NoticeCenter.vue')),
  'ArticleCenter.vue': defineAsyncComponent(() => import('@/views/user_pages/ArticleCenter.vue')),
  'KbCenter.vue': defineAsyncComponent(() => import('@/views/user_pages/KbCenter.vue')),
};

export const userMenuItems: MenuItem[] = effectiveUserMenuConfigs.map((config) => ({
  key: config.key,
  label: config.label,
  icon: config.icon,
  path: config.path,
  disabled: config.disabled,
  children: config.children?.map((child) => ({
    key: child.key,
    label: child.label,
    icon: child.icon,
    path: child.path,
    disabled: child.disabled,
  })),
}));

const componentMap: Record<string, () => Promise<any>> = {
  'index.vue': () => import('@/views/user_pages/index.vue'),
  'Profile.vue': () => import('@/views/user_pages/Profile.vue'),
  'Documents.vue': () => import('@/views/user_pages/Documents.vue'),
  'Messages.vue': () => import('@/views/user_pages/Messages.vue'),
  'SystemMonitor.vue': () => import('@/views/user_pages/SystemMonitor.vue'),
  'AiChat.vue': () => import('@/views/user_pages/AiChat.vue'),
  'YoloDetection.vue': () => import('@/views/user_pages/YoloDetection.vue'),
  'LiveDetection.vue': () => import('@/views/user_pages/LiveDetection.vue'),
  'DetectionHistory.vue': () => import('@/views/user_pages/DetectionHistory.vue'),
  'AlertCenter.vue': () => import('@/views/user_pages/AlertCenter.vue'),
  'NoticeCenter.vue': () => import('@/views/user_pages/NoticeCenter.vue'),
  'ArticleCenter.vue': () => import('@/views/user_pages/ArticleCenter.vue'),
  'KbCenter.vue': () => import('@/views/user_pages/KbCenter.vue'),
};

const baseRoutes: RouteRecordRaw[] = effectiveUserMenuConfigs.map((config) => {
  const route: RouteRecordRaw = {
    path: config.path,
    name: `User${config.key.charAt(0).toUpperCase() + config.key.slice(1)}`,
    component: componentMap[config.component] || (() => import('@/views/NotFound.vue')),
    meta: {
      title: config.meta?.title || config.label,
      requiresAuth: config.meta?.requiresAuth ?? true,
      ...config.meta,
    },
    children: undefined,
  };
  if (config.children && config.children.length > 0) {
    route.children = config.children.map((child) => ({
      path: child.path,
      name: `User${child.key.charAt(0).toUpperCase() + child.key.slice(1)}`,
      component: componentMap[child.component] || (() => import('@/views/NotFound.vue')),
      meta: {
        title: child.meta?.title || child.label,
        requiresAuth: child.meta?.requiresAuth ?? true,
        ...child.meta,
      },
    }));
  }
  return route;
});

// 文章详情独立页面（不在菜单展示）
const knowledgeDetailRoute: RouteRecordRaw = {
  path: '/user/knowledge/:id',
  name: 'UserKnowledgeDetail',
  component: () => import('@/views/user_pages/ArticleDetail.vue'),
  meta: { title: '文章详情', requiresAuth: true, hideInMenu: true },
};

export const userRoutes: RouteRecordRaw[] = [...baseRoutes, knowledgeDetailRoute];

export function getMenuPath(menuKey: string): string {
  const findPath = (items: MenuItem[], key: string): string | null => {
    for (const item of items) {
      if (item.key === key && item.path) return item.path;
      if (item.children) {
        const childPath = findPath(item.children, key);
        if (childPath) return childPath;
      }
    }
    return null;
  };
  return findPath(userMenuItems, menuKey) || '/dashboard';
}

export function getMenuBreadcrumb(menuKey: string): string[] {
  const findBreadcrumb = (items: MenuItem[], key: string, path: string[] = []): string[] | null => {
    for (const item of items) {
      const currentPath = [...path, item.label];
      if (item.key === menuKey) return currentPath;
      if (item.children) {
        const childPath = findBreadcrumb(item.children, key, currentPath);
        if (childPath) return childPath;
      }
    }
    return null;
  };
  return findBreadcrumb(userMenuItems, menuKey) || ['仪表盘'];
}

export const generateComponentMap = () => {
  const map: Record<string, any> = {};
  const processConfigs = (configs: UserMenuConfig[]) => {
    configs.forEach((config) => {
      if (explicitComponentMap[config.component]) {
        map[config.key] = explicitComponentMap[config.component];
      } else {
        map[config.key] = defineAsyncComponent(() => import('@/views/NotFound.vue'));
      }
      if (config.children) processConfigs(config.children);
    });
  };
  processConfigs(effectiveUserMenuConfigs);
  return map;
};

export const userComponentMap = generateComponentMap();

export const getFilteredUserMenuItems = (
  userRoles: string[],
  userPermissions: string[]
): MenuItem[] => {
  return effectiveUserMenuConfigs
    .filter((config) => {
      // 隐藏菜单中不显示的项（如个人信息，只在用户下拉菜单中显示）
      if (config.meta?.hideInMenu) return false;
      if (!config.meta?.roles || config.meta.roles.length === 0) return true;
      return config.meta.roles.some((requiredRole) => userRoles.includes(requiredRole));
    })
    .map((config) => ({
      key: config.key,
      label: config.label,
      icon: config.icon,
      path: config.path,
      disabled: config.disabled,
      children: config.children
        ?.filter((child) => {
          if (!child.meta?.roles || child.meta.roles.length === 0) return true;
          return child.meta.roles.some((requiredRole) => userRoles.includes(requiredRole));
        })
        .map((child) => ({
          key: child.key,
          label: child.label,
          icon: child.icon,
          path: child.path,
          disabled: child.disabled,
        })),
    }));
};

export const hasUserMenuPermission = (menuKey: string, userRoles: string[]): boolean => {
  const menuConfig = userMenuConfigs.find((config) => config.key === menuKey);
  if (!menuConfig) return false;
  if (!menuConfig.meta?.roles || menuConfig.meta.roles.length === 0) return true;
  return menuConfig.meta.roles.some((requiredRole) => userRoles.includes(requiredRole));
};
