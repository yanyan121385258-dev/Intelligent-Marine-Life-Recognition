/**
 * 权限管理工具类
 * 统一管理用户权限检查和菜单过滤逻辑
 */

import { computed } from 'vue';
import { useUserStore } from '@/stores/hertz_user';
import { UserRole } from '@/router/admin_menu';

// 权限检查接口
export interface PermissionChecker {
  hasRole(role: string): boolean;
  hasPermission(permission: string): boolean;
  hasAnyRole(roles: string[]): boolean;
  hasAnyPermission(permissions: string[]): boolean;
  isAdmin(): boolean;
  isLoggedIn(): boolean;
}

// 权限管理类
export class PermissionManager implements PermissionChecker {
  // 延迟获取 Pinia store，避免在 Pinia 未初始化时调用
  private get userStore() {
    return useUserStore();
  }

  /**
   * 检查用户是否拥有指定角色
   */
  hasRole(role: string): boolean {
    const userRoles = this.userStore.userInfo?.roles?.map((r) => r.role_code) || [];
    return userRoles.includes(role);
  }

  /**
   * 检查用户是否拥有指定权限
   */
  hasPermission(permission: string): boolean {
    const userPermissions = this.userStore.userInfo?.permissions || [];
    return userPermissions.includes(permission);
  }

  /**
   * 检查用户是否拥有任意一个指定角色
   */
  hasAnyRole(roles: string[]): boolean {
    const userRoles = this.userStore.userInfo?.roles?.map((r) => r.role_code) || [];
    return roles.some((role) => userRoles.includes(role));
  }

  /**
   * 检查用户是否拥有任意一个指定权限
   */
  hasAnyPermission(permissions: string[]): boolean {
    const userPermissions = this.userStore.userInfo?.permissions || [];
    return permissions.some((permission) => userPermissions.includes(permission));
  }

  /**
   * 检查用户是否为管理员
   */
  isAdmin(): boolean {
    const adminRoles = [UserRole.ADMIN, UserRole.SYSTEM_ADMIN, UserRole.SUPER_ADMIN];
    return this.hasAnyRole(adminRoles);
  }

  /**
   * 检查用户是否已登录
   */
  isLoggedIn(): boolean {
    return this.userStore.isLoggedIn && !!this.userStore.userInfo;
  }

  /**
   * 获取用户角色列表
   */
  getUserRoles(): string[] {
    return this.userStore.userInfo?.roles?.map((r) => r.role_code) || [];
  }

  /**
   * 获取用户权限列表
   */
  getUserPermissions(): string[] {
    return this.userStore.userInfo?.permissions || [];
  }

  /**
   * 检查用户是否可以访问指定路径
   */
  canAccessPath(path: string, requiredRoles?: string[], requiredPermissions?: string[]): boolean {
    if (!this.isLoggedIn()) {
      return false;
    }

    // 如果没有指定权限要求，默认允许访问
    if (!requiredRoles && !requiredPermissions) {
      return true;
    }

    // 检查角色权限
    if (requiredRoles && requiredRoles.length > 0) {
      if (!this.hasAnyRole(requiredRoles)) {
        return false;
      }
    }

    // 检查具体权限
    if (requiredPermissions && requiredPermissions.length > 0) {
      if (!this.hasAnyPermission(requiredPermissions)) {
        return false;
      }
    }

    return true;
  }
}

// 创建全局权限管理实例
export const permissionManager = new PermissionManager();

// 便捷的权限检查函数
export const usePermission = () => {
  return {
    hasRole: (role: string) => permissionManager.hasRole(role),
    hasPermission: (permission: string) => permissionManager.hasPermission(permission),
    hasAnyRole: (roles: string[]) => permissionManager.hasAnyRole(roles),
    hasAnyPermission: (permissions: string[]) => permissionManager.hasAnyPermission(permissions),
    isAdmin: () => permissionManager.isAdmin(),
    isLoggedIn: () => permissionManager.isLoggedIn(),
    canAccessPath: (path: string, requiredRoles?: string[], requiredPermissions?: string[]) =>
      permissionManager.canAccessPath(path, requiredRoles, requiredPermissions),
  };
};

// Vue 3 组合式 API 权限检查 Hook
export const usePermissionCheck = () => {
  const userStore = useUserStore();

  return {
    // 响应式权限检查
    hasRole: (role: string) => computed(() => permissionManager.hasRole(role)),
    hasPermission: (permission: string) =>
      computed(() => permissionManager.hasPermission(permission)),
    hasAnyRole: (roles: string[]) => computed(() => permissionManager.hasAnyRole(roles)),
    hasAnyPermission: (permissions: string[]) =>
      computed(() => permissionManager.hasAnyPermission(permissions)),
    isAdmin: computed(() => permissionManager.isAdmin()),
    isLoggedIn: computed(() => permissionManager.isLoggedIn()),

    // 用户信息
    userRoles: computed(() => permissionManager.getUserRoles()),
    userPermissions: computed(() => permissionManager.getUserPermissions()),
    userInfo: computed(() => userStore.userInfo),
  };
};
