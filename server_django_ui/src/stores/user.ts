import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { request } from '@/utils/request';
import { changePassword } from '@/api/password';
import type { ChangePasswordParams } from '@/api/password';
import { roleApi } from '@/api/role';
import { initializeMenuMapping } from '@/utils/menu_mapping';
import { logoutUser } from '@/api/auth';
import { hasModuleSelection } from '@/config/modules';

// 用户信息接口
interface UserInfo {
  user_id: number;
  username: string;
  email: string;
  phone?: string;
  real_name?: string;
  avatar?: string;
  roles: Array<{
    role_id: number;
    role_name: string;
    role_code: string;
  }>;
  permissions: string[];
  menu_permissions?: number[]; // 用户拥有的菜单权限ID列表
}

// 登录参数接口
interface LoginParams {
  username: string;
  password: string;
  remember?: boolean;
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<UserInfo | null>(null);
  const token = ref<string>('');
  const isLoggedIn = ref<boolean>(false);
  const loading = ref<boolean>(false);
  const userMenuPermissions = ref<number[]>([]); // 用户菜单权限ID列表

  // 计算属性
  const hasPermission = computed(() => (permission: string) => {
    return userInfo.value?.permissions?.includes(permission) || false;
  });

  const isAdmin = computed(() => {
    const userRole = userInfo.value?.roles?.[0]?.role_code;
    return userRole === 'admin' || userRole === 'system_admin' || userRole === 'super_admin';
  });

  // 方法
  const login = async (params: LoginParams) => {
    loading.value = true;
    try {
      const response = await request.post<{
        access_token: string;
        refresh_token: string;
        user_info: UserInfo;
      }>('/api/auth/login/', params);

      token.value = response.access_token;
      userInfo.value = response.user_info;
      isLoggedIn.value = true;

      // 保存到本地存储
      localStorage.setItem('token', response.access_token);
      if (params.remember) {
        localStorage.setItem('userInfo', JSON.stringify(response.user_info));
      }

      // 获取用户菜单权限（模板模式首次运行时跳过）
      const isTemplateMode = import.meta.env.VITE_TEMPLATE_SETUP_MODE === 'true';
      if (!isTemplateMode || hasModuleSelection()) {
        await fetchUserMenuPermissions();
      }

      return response;
    } catch (error) {
      console.error('登录失败:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    loading.value = true;
    try {
      // 调用封装好的退出登录接口
      await logoutUser();

      // 清除状态
      token.value = '';
      userInfo.value = null;
      isLoggedIn.value = false;

      // 清除本地存储
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
    } catch (error) {
      console.error('退出登录失败:', error);
      // 即使请求失败也要清除本地状态
      token.value = '';
      userInfo.value = null;
      isLoggedIn.value = false;
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
    } finally {
      loading.value = false;
    }
  };

  const updateUserInfo = async (info: Partial<UserInfo>) => {
    try {
      const response = await request.put<UserInfo>('/user/profile', info);

      userInfo.value = { ...userInfo.value, ...response };
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value));

      return response;
    } catch (error) {
      console.error('更新用户信息失败:', error);
      throw error;
    }
  };

  const checkAuth = async () => {
    console.log('🔍 检查用户认证状态...');

    const savedToken = localStorage.getItem('token');
    const savedUserInfo = localStorage.getItem('userInfo');

    console.log('💾 localStorage中的token:', savedToken ? '存在' : '不存在');
    console.log('💾 localStorage中的userInfo:', savedUserInfo ? '存在' : '不存在');

    if (savedToken && savedUserInfo) {
      try {
        const parsedUserInfo = JSON.parse(savedUserInfo);
        token.value = savedToken;
        userInfo.value = parsedUserInfo;
        isLoggedIn.value = true;

        console.log('✅ 用户状态恢复成功');
        console.log('👤 恢复的用户信息:', parsedUserInfo);
        console.log('🔐 登录状态:', isLoggedIn.value);

        // 获取用户菜单权限（模板模式首次运行时跳过）
        const isTemplateMode = import.meta.env.VITE_TEMPLATE_SETUP_MODE === 'true';
        if (!isTemplateMode || hasModuleSelection()) {
          await fetchUserMenuPermissions();
        }
      } catch (error) {
        console.error('❌ 解析用户信息失败:', error);
        clearAuth();
      }
    } else {
      console.log('❌ 没有找到保存的认证信息');
    }
  };

  const clearAuth = () => {
    token.value = '';
    userInfo.value = null;
    isLoggedIn.value = false;
    userMenuPermissions.value = [];
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
  };

  const updatePassword = async (params: ChangePasswordParams) => {
    try {
      await changePassword(params);
      return true;
    } catch (error) {
      console.error('修改密码失败:', error);
      throw error;
    }
  };

  // 获取用户菜单权限
  const fetchUserMenuPermissions = async () => {
    if (!userInfo.value?.roles?.length) {
      userMenuPermissions.value = [];
      return [];
    }

    try {
      const adminRoleCodes = ['admin', 'system_admin', 'super_admin'];
      const hasAdminRole = userInfo.value.roles.some((role) =>
        adminRoleCodes.includes(role.role_code)
      );

      if (!hasAdminRole) {
        userMenuPermissions.value = [];
        return [];
      }

      // 获取用户所有角色的菜单权限
      const allMenuPermissions = new Set<number>();

      for (const role of userInfo.value.roles) {
        try {
          const response = await roleApi.getRolePermissions(role.role_id);
          if (response.success) {
            // 假设response.data直接返回Permission[]数组
            // 我们只需要提取permission_id作为菜单权限ID
            const permissions = response.data;
            if (Array.isArray(permissions)) {
              permissions.forEach((permission: any) => {
                if (permission.permission_id) {
                  const id =
                    typeof permission.permission_id === 'number'
                      ? permission.permission_id
                      : Number(permission.permission_id);
                  if (!isNaN(id)) {
                    allMenuPermissions.add(id);
                  }
                }
              });
            }
          }
        } catch (error) {
          console.error(`获取角色 ${role.role_name} 的菜单权限失败:`, error);
        }
      }

      const permissions = Array.from(allMenuPermissions);
      userMenuPermissions.value = permissions;

      // 同时更新用户信息中的菜单权限
      if (userInfo.value) {
        userInfo.value.menu_permissions = permissions;
      }

      // 初始化菜单映射关系
      await initializeMenuMapping();

      return permissions;
    } catch (error) {
      console.error('获取用户菜单权限失败:', error);
      userMenuPermissions.value = [];
      return [];
    }
  };

  return {
    // 状态
    userInfo,
    token,
    isLoggedIn,
    loading,
    userMenuPermissions,

    // 计算属性
    hasPermission,
    isAdmin,

    // 方法
    login,
    logout,
    updateUserInfo,
    checkAuth,
    clearAuth,
    updatePassword,
    fetchUserMenuPermissions,
  };
});
