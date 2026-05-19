import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { adminMenuRoutes, UserRole } from './admin_menu';
import { userRoutes } from './user_menu_ai';

const fixedRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    redirect: '/login',
    meta: {
      title: '首页',
      requiresAuth: false,
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/register.vue'),
    meta: {
      title: '注册',
      requiresAuth: false,
    },
  },
  adminMenuRoutes,
];

// 动态生成路由配置
function generateDynamicRoutes(targetDir: string = ''): RouteRecordRaw[] {
  if (!targetDir) {
    return [];
  }
  const viewsContext = import.meta.glob('@/views/**/*.vue', { eager: true });

  return Object.entries(viewsContext)
    .map(([path, component]) => {
      const relativePath = path.match(/\/views\/(.+?)\.vue$/)?.[1];
      if (!relativePath) return null;

      const fileName = relativePath.replace('.vue', '');
      const routeName = fileName.split('/').pop()!;

      // 过滤条件
      if (targetDir && !fileName.startsWith(targetDir)) {
        return null;
      }

      // 生成路径和标题
      const routePath = `/${fileName.replace(/([A-Z])/g, '$1').toLowerCase()}`;
      const requiresAuth =
        (!routePath.startsWith('/demo') && !routePath.startsWith('/public')) ||
        routePath.startsWith('/user_pages') ||
        routePath.startsWith('/admin_page');
      const pageTitle = (component as any)?.default?.title;

      // 根据路径设置角色权限
      let roles: UserRole[] = [];
      if (routePath.startsWith('/admin_page')) {
        roles = [UserRole.ADMIN, UserRole.SYSTEM_ADMIN, UserRole.SUPER_ADMIN];
      } else if (routePath.startsWith('/user_pages')) {
        roles = [UserRole.NORMAL_USER, UserRole.ADMIN, UserRole.SYSTEM_ADMIN, UserRole.SUPER_ADMIN];
      } else if (routePath.startsWith('/demo')) {
        roles = []; // demo页面不需要特定角色
      }

      return {
        path: routePath,
        name: routeName,
        component: () => import(/* @vite-ignore */ path),
        meta: {
          title: pageTitle,
          requiresAuth,
          roles: requiresAuth ? roles : [],
        },
      };
    })
    .filter(Boolean) as RouteRecordRaw[];
}

// 合并固定路由和动态路由
const routes: RouteRecordRaw[] = [
  ...fixedRoutes,
  ...userRoutes, // 用户菜单路由 - 现在通过统一配置自动生成
  ...generateDynamicRoutes('demo'), // 生成demo文件夹的路由
  ...generateDynamicRoutes('admin_page'), //生成admin_page文件夹的路由
  // 404页面始终放在最后
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面未找到',
      requiresAuth: false,
    },
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// 递归打印路由信息
function printRoute(route: RouteRecordRaw, level: number = 0) {
  const indent = '  '.repeat(level);
  const icon = route.meta.requiresAuth ? '🔒' : '🔓';
  const auth = route.meta.requiresAuth ? '需要登录' : '公开访问';

  // 递归打印子路由
  if (route.children && route.children.length > 0) {
    route.children.forEach((child) => printRoute(child, level + 1));
  }
}

// 路由调试信息
function logRouteInfo() {
  routes.forEach((route) => printRoute(route));
}

// 重定向计数器，防止无限重定向
let redirectCount = 0;
const MAX_REDIRECTS = 3;

// 路由守卫
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore();

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 管理系统`;
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    redirectCount++;
    if (redirectCount > MAX_REDIRECTS) {
      redirectCount = 0;
      next({ name: 'Home' });
      return;
    }
    next({ name: 'Login', query: { redirect: to.fullPath } });
    return;
  }

  // 已登录用户访问登录页，根据角色重定向到对应首页
  if (to.name === 'Login' && userStore.isLoggedIn) {
    const userRole = userStore.userInfo?.roles?.[0]?.role_code;

    // 重置重定向计数器
    redirectCount = 0;

    // 仅管理员角色进入管理端，其余（含未定义）进入用户端
    const adminRoles = [UserRole.ADMIN, UserRole.SYSTEM_ADMIN, UserRole.SUPER_ADMIN];
    const isAdmin = adminRoles.includes(userRole as UserRole);
    if (isAdmin) {
      next({ name: 'Admin' });
    } else {
      next({ name: 'UserDashboard' });
    }
    return;
  }

  // 检查角色权限
  if (to.meta.requiresAuth && to.meta.roles && Array.isArray(to.meta.roles)) {
    const userRole = userStore.userInfo?.roles?.[0]?.role_code;

    // 特殊处理：如果是管理端路由，使用自定义权限检查
    let hasPermission = false;
    if (to.path.startsWith('/admin')) {
      // 管理端路由：仅 admin/system_admin/super_admin 可访问
      const adminRoles = [UserRole.ADMIN, UserRole.SYSTEM_ADMIN, UserRole.SUPER_ADMIN];
      hasPermission = adminRoles.includes(userRole as UserRole);
    } else {
      // 其他路由：使用原有的角色检查逻辑
      hasPermission = to.meta.roles.length === 0 || to.meta.roles.includes(userRole as UserRole);
    }

    if (!hasPermission) {
      // 增加重定向计数
      redirectCount++;

      // 防止无限重定向
      if (redirectCount > MAX_REDIRECTS) {
        redirectCount = 0;
        next({ name: 'Home' });
        return;
      }

      // 防止无限重定向：检查是否已经在重定向过程中
      if (to.name === 'Admin' || to.name === 'UserDashboard') {
        redirectCount = 0;
        next({ name: 'Home' });
        return;
      }

      // 没有权限，根据用户角色重定向到对应首页
      // 只有normal_user角色跳转到用户端，其他角色（包括未定义的）都跳转到管理端
      if (userRole === 'normal_user') {
        next({ name: 'UserDashboard' });
      } else {
        next({ name: 'Admin' });
      }
      return;
    }
  }

  // 成功通过所有检查，重置重定向计数器
  redirectCount = 0;
  next();
});

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error);
});

// 输出路由信息
logRouteInfo();

export default router;
