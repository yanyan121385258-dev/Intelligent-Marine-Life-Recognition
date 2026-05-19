<template>
  <div class="admin-layout">
    <a-layout style="min-height: 100vh">
      <!-- 侧边栏 -->
      <a-layout-sider
        v-model:collapsed="collapsed"
        :trigger="null"
        collapsible
        theme="dark"
        width="260"
        class="admin-sider"
      >
        <!-- Logo 区域 -->
        <div class="logo">
          <div class="logo-icon-wrapper">
            <DashboardOutlined class="logo-icon" />
          </div>
          <div v-if="!collapsed" class="logo-text-wrapper">
            <span class="logo-text">管理后台</span>
            <span class="logo-subtitle">Admin Panel</span>
          </div>
        </div>

        <!-- 菜单 -->
        <a-menu
          v-if="hasAdminAccess"
          v-model:selectedKeys="selectedKeys"
          v-model:openKeys="openKeys"
          mode="inline"
          theme="dark"
          :inline-collapsed="collapsed"
          class="admin-menu"
          @click="handleMenuClick"
          @openChange="handleOpenChange"
        >
          <template v-for="menuItem in filteredMenuConfig" :key="menuItem.key">
            <!-- 有子菜单的项目 -->
            <a-sub-menu
              v-if="menuItem.children && menuItem.children.length > 0"
              :key="menuItem.key"
            >
              <template #icon>
                <DashboardOutlined v-if="menuItem.icon === 'DashboardOutlined'" />
                <UserOutlined v-else-if="menuItem.icon === 'UserOutlined'" />
                <SettingOutlined v-else-if="menuItem.icon === 'SettingOutlined'" />
                <FileSearchOutlined v-else-if="menuItem.icon === 'FileSearchOutlined'" />
                <DatabaseOutlined v-else-if="menuItem.icon === 'DatabaseOutlined'" />
                <RobotOutlined v-else-if="menuItem.icon === 'RobotOutlined'" />
                <WarningOutlined v-else-if="menuItem.icon === 'WarningOutlined'" />
                <BellOutlined v-else-if="menuItem.icon === 'BellOutlined'" />
                <HistoryOutlined v-else-if="menuItem.icon === 'HistoryOutlined'" />
                <ClusterOutlined v-else-if="menuItem.icon === 'ClusterOutlined'" />
              </template>
              <template #title>{{ menuItem.title }}</template>

              <!-- 子菜单项 -->
              <a-menu-item v-for="childItem in menuItem.children" :key="childItem.key">
                <template #icon>
                  <DashboardOutlined v-if="childItem.icon === 'DashboardOutlined'" />
                  <UserOutlined v-else-if="childItem.icon === 'UserOutlined'" />
                  <SettingOutlined v-else-if="childItem.icon === 'SettingOutlined'" />
                  <FileSearchOutlined v-else-if="childItem.icon === 'FileSearchOutlined'" />
                  <DatabaseOutlined v-else-if="childItem.icon === 'DatabaseOutlined'" />
                  <RobotOutlined v-else-if="childItem.icon === 'RobotOutlined'" />
                  <WarningOutlined v-else-if="childItem.icon === 'WarningOutlined'" />
                  <BellOutlined v-else-if="childItem.icon === 'BellOutlined'" />
                  <HistoryOutlined v-else-if="childItem.icon === 'HistoryOutlined'" />
                  <ClusterOutlined v-else-if="childItem.icon === 'ClusterOutlined'" />
                </template>
                <span>{{ childItem.title }}</span>
              </a-menu-item>
            </a-sub-menu>

            <!-- 没有子菜单的项目 -->
            <a-menu-item v-else :key="menuItem.key">
              <template #icon>
                <DashboardOutlined v-if="menuItem.icon === 'DashboardOutlined'" />
                <UserOutlined v-else-if="menuItem.icon === 'UserOutlined'" />
                <SettingOutlined v-else-if="menuItem.icon === 'SettingOutlined'" />
                <FileSearchOutlined v-else-if="menuItem.icon === 'FileSearchOutlined'" />
                <DatabaseOutlined v-else-if="menuItem.icon === 'DatabaseOutlined'" />
                <RobotOutlined v-else-if="menuItem.icon === 'RobotOutlined'" />
                <WarningOutlined v-else-if="menuItem.icon === 'WarningOutlined'" />
                <BellOutlined v-else-if="menuItem.icon === 'BellOutlined'" />
                <HistoryOutlined v-else-if="menuItem.icon === 'HistoryOutlined'" />
                <ClusterOutlined v-else-if="menuItem.icon === 'ClusterOutlined'" />
              </template>
              <span>{{ menuItem.title }}</span>
            </a-menu-item>
          </template>
        </a-menu>

        <!-- 无权限提示 -->
        <div v-else class="no-permission">
          <div class="no-permission-content">
            <UserOutlined class="no-permission-icon" />
            <p class="no-permission-text">您没有管理员权限</p>
            <p class="no-permission-desc">请联系系统管理员获取相应权限</p>
          </div>
        </div>
      </a-layout-sider>

      <!-- 主体布局 -->
      <a-layout>
        <!-- 顶部导航 -->
        <a-layout-header class="header">
          <div class="header-left">
            <a-button type="text" @click="toggleCollapsed" class="trigger">
              <template #icon>
                <MenuUnfoldOutlined v-if="collapsed" />
                <MenuFoldOutlined v-else />
              </template>
            </a-button>

            <!-- 面包屑导航 -->
            <a-breadcrumb class="breadcrumb">
              <a-breadcrumb-item v-for="item in breadcrumbItems" :key="item.path">
                {{ item.title }}
              </a-breadcrumb-item>
            </a-breadcrumb>
          </div>

          <div class="header-right">
            <!-- 全屏按钮 -->
            <a-tooltip title="全屏">
              <a-button type="text" @click="toggleFullscreen" class="header-action-btn">
                <template #icon>
                  <FullscreenOutlined v-if="!isFullscreen" />
                  <FullscreenExitOutlined v-else />
                </template>
              </a-button>
            </a-tooltip>

            <!-- 用户信息下拉菜单 -->
            <a-dropdown
              placement="bottomRight"
              :overlay-style="{
                borderRadius: '14px',
                padding: '6px',
                minWidth: '200px',
                zIndex: 1050,
              }"
              trigger="click"
            >
              <div class="user-info">
                <a-avatar :src="userStore.userInfo?.avatar" class="user-avatar" :size="32">
                  <template #icon>
                    <UserOutlined />
                  </template>
                </a-avatar>
                <div class="user-info-text">
                  <span class="username">{{ userStore.userInfo?.username || '管理员' }}</span>
                  <span class="user-role">管理员</span>
                </div>
                <DownOutlined class="dropdown-icon" />
              </div>

              <template #overlay>
                <a-menu class="user-dropdown-menu">
                  <a-menu-item
                    key="user-info"
                    @click="() => handleUserMenuClick({ key: 'user-info' })"
                    class="menu-item"
                  >
                    <template #icon>
                      <UserOutlined class="menu-icon" />
                    </template>
                    <span class="menu-text">个人信息</span>
                  </a-menu-item>
                  <a-menu-item
                    key="change-password"
                    @click="() => handleUserMenuClick({ key: 'change-password' })"
                    class="menu-item"
                  >
                    <template #icon>
                      <LockOutlined class="menu-icon" />
                    </template>
                    <span class="menu-text">修改密码</span>
                  </a-menu-item>
                  <a-menu-divider class="menu-divider" />
                  <a-menu-item
                    key="logout"
                    @click="() => handleUserMenuClick({ key: 'logout' })"
                    class="menu-item logout-item"
                  >
                    <template #icon>
                      <LogoutOutlined class="menu-icon" />
                    </template>
                    <span class="menu-text">退出登录</span>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </a-layout-header>

        <!-- 内容区域 -->
        <a-layout-content class="content">
          <div class="content-wrapper">
            <!-- 使用router-view来显示子页面 -->
            <router-view />
          </div>
        </a-layout-content>


      </a-layout>
    </a-layout>

    <!-- 个人信息弹窗 -->
    <a-modal
      v-model:visible="userInfoModalVisible"
      :title="isEditingUserInfo ? '编辑个人信息' : '个人信息'"
      :confirm-loading="userInfoSaving"
      :footer="isEditingUserInfo ? undefined : null"
      @ok="handleUserInfoSave"
      @cancel="handleUserInfoCancel"
      width="600px"
    >
      <div v-if="userInfoLoading" class="loading-container">
        <a-spin size="large" />
        <p>正在加载用户信息...</p>
      </div>

      <div v-else-if="currentUserInfo" class="user-info-content">
        <!-- 用户头像区域 -->
        <div class="user-avatar-section">
          <a-upload :show-upload-list="false" :before-upload="handleAdminAvatarBeforeUpload">
            <a-avatar
              :size="80"
              :src="currentUserInfo.avatar || userStore.userInfo?.avatar"
              class="large-avatar"
            >
              <template #icon>
                <UserOutlined />
              </template>
              {{ currentUserInfo.username?.charAt(0)?.toUpperCase() }}
            </a-avatar>
          </a-upload>
          <h3 class="user-display-name">
            {{ currentUserInfo.real_name || currentUserInfo.username }}
          </h3>
          <a-button
            v-if="!isEditingUserInfo"
            type="primary"
            size="small"
            @click="startEditUserInfo"
            class="edit-btn"
          >
            <template #icon>
              <EditOutlined />
            </template>
            编辑信息
          </a-button>
        </div>

        <!-- 查看模式 -->
        <div v-if="!isEditingUserInfo">
          <a-descriptions :column="1" bordered class="user-details">
            <a-descriptions-item label="用户名">
              {{ currentUserInfo.username }}
            </a-descriptions-item>
            <a-descriptions-item label="真实姓名">
              {{ currentUserInfo.real_name || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="邮箱">
              {{ currentUserInfo.email || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="手机号">
              {{ currentUserInfo.phone || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="性别">
              {{
                currentUserInfo.gender === 1 ? '男' : currentUserInfo.gender === 2 ? '女' : '未设置'
              }}
            </a-descriptions-item>
            <a-descriptions-item label="生日">
              {{ currentUserInfo.birthday || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="用户角色">
              <a-tag
                v-if="currentUserInfo.roles?.some((role) => role.role_code === 'super_admin')"
                color="purple"
              >
                超级管理员
              </a-tag>
              <a-tag
                v-else-if="currentUserInfo.roles?.some((role) => role.role_code === 'admin')"
                color="blue"
              >
                管理员
              </a-tag>
              <a-tag v-else color="default"> 普通用户 </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="账户状态">
              <a-tag :color="currentUserInfo.status === 1 ? 'green' : 'red'">
                {{ currentUserInfo.status === 1 ? '正常' : '已禁用' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="注册时间">
              {{
                currentUserInfo.created_at
                  ? new Date(currentUserInfo.created_at).toLocaleString()
                  : '未知'
              }}
            </a-descriptions-item>
            <a-descriptions-item label="最后登录">
              {{
                currentUserInfo.last_login_time
                  ? new Date(currentUserInfo.last_login_time).toLocaleString()
                  : '从未登录'
              }}
            </a-descriptions-item>
          </a-descriptions>
        </div>

        <!-- 编辑模式 -->
        <div v-else>
          <a-form
            ref="userInfoFormRef"
            :model="userInfoForm"
            :rules="userInfoRules"
            layout="vertical"
            class="user-info-form"
          >
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="真实姓名" name="real_name">
                  <a-input v-model:value="userInfoForm.real_name" placeholder="请输入真实姓名" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="邮箱" name="email">
                  <a-input
                    v-model:value="userInfoForm.email"
                    placeholder="请输入邮箱地址"
                    type="email"
                  />
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="手机号" name="phone">
                  <a-input v-model:value="userInfoForm.phone" placeholder="请输入手机号" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="性别" name="gender">
                  <a-select v-model:value="userInfoForm.gender" placeholder="请选择性别">
                    <a-select-option :value="0">未设置</a-select-option>
                    <a-select-option :value="1">男</a-select-option>
                    <a-select-option :value="2">女</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="头像链接" name="avatar">
              <a-input v-model:value="userInfoForm.avatar" placeholder="请输入头像链接地址" />
            </a-form-item>

            <a-form-item label="生日" name="birthday">
              <a-date-picker
                v-model:value="userInfoForm.birthday"
                placeholder="请选择生日"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-form>
        </div>
      </div>

      <div v-else class="no-data">
        <a-empty description="暂无用户信息" />
      </div>
    </a-modal>

    <!-- 修改密码弹窗 -->
    <a-modal
      v-model:visible="passwordModalVisible"
      title="修改密码"
      :confirm-loading="passwordLoading"
      @ok="handlePasswordSubmit"
      @cancel="handlePasswordCancel"
      width="400px"
    >
      <a-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" layout="vertical">
        <a-form-item label="当前密码" name="old_password">
          <a-input-password
            v-model:value="passwordForm.old_password"
            placeholder="请输入当前密码"
            autocomplete="current-password"
          />
        </a-form-item>
        <a-form-item label="新密码" name="new_password">
          <a-input-password
            v-model:value="passwordForm.new_password"
            placeholder="请输入新密码"
            autocomplete="new-password"
          />
        </a-form-item>
        <a-form-item label="确认新密码" name="confirm_password">
          <a-input-password
            v-model:value="passwordForm.confirm_password"
            placeholder="请再次输入新密码"
            autocomplete="new-password"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { message } from 'ant-design-vue';
import {
  adminMenuConfig,
  getMenuKeyByPath,
  getPathByMenuKey,
  getTitleByMenuKey,
  getFilteredMenuConfig,
  hasAnyAdminPermission,
} from '@/router/admin_menu';
import { userApi, User } from '@/api/user';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  UserOutlined,
  SettingOutlined,
  HomeOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  BellOutlined,
  DownOutlined,
  LogoutOutlined,
  LockOutlined,
  EyeOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  UserAddOutlined,
  PlusOutlined,
  DatabaseOutlined,
  EditOutlined,
  FileSearchOutlined,
  RobotOutlined,
  WarningOutlined,
  HistoryOutlined,
  ClusterOutlined,
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

// 侧边栏折叠状态
const collapsed = ref(false);

// 菜单相关状态
const selectedKeys = ref(['dashboard']);
const openKeys = ref(['yolo-model']); // 默认展开YOLO模型菜单

// 🎯 动态菜单配置 - 根据用户权限过滤
const filteredMenuConfig = computed(() => {
  if (!userStore.userInfo) {
    return [];
  }

  const userRoles = userStore.userInfo.roles?.map((role) => role.role_code) || [];
  const userPermissions = userStore.userInfo.permissions || [];
  const userMenuPermissions = userStore.userMenuPermissions || [];

  console.log('🔍 菜单过滤调试信息:', {
    userRoles,
    userPermissions,
    userMenuPermissions,
  });

  const filtered = getFilteredMenuConfig(userRoles, userPermissions, userMenuPermissions);
  console.log('📋 过滤后的菜单配置:', filtered);

  return filtered;
});

// 🎯 检查用户是否有管理员权限
const hasAdminAccess = computed(() => {
  if (!userStore.userInfo) {
    return false;
  }

  const userRoles = userStore.userInfo.roles?.map((role) => role.role_code) || [];
  return hasAnyAdminPermission(userRoles);
});

// 全屏状态
const isFullscreen = ref(false);

// 面包屑数据
const breadcrumbItems = computed(() => {
  // 根据当前路由获取菜单key和标题
  const menuKey = getMenuKeyByPath(route.path);
  const title = getTitleByMenuKey(menuKey);

  return [{ title, path: menuKey }];
});

// 当前视图标题映射
const currentViewTitle = computed(() => {
  // 根据当前路由获取菜单key和标题
  const menuKey = getMenuKeyByPath(route.path);
  return getTitleByMenuKey(menuKey);
});

// 最近活动数据
const recentActivities = ref([
  {
    action: '用户 张三 登录了系统',
    time: '2分钟前',
    avatar: '',
  },
  {
    action: '管理员 李四 创建了新菜单',
    time: '5分钟前',
    avatar: '',
  },
  {
    action: '用户 王五 修改了个人信息',
    time: '10分钟前',
    avatar: '',
  },
  {
    action: '系统自动备份完成',
    time: '1小时前',
    avatar: '',
  },
]);

// 修改密码相关状态
const passwordModalVisible = ref(false);
const passwordLoading = ref(false);
const passwordFormRef = ref();
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
});

// 个人信息相关状态
const userInfoModalVisible = ref(false);
const currentUserInfo = ref<User | null>(null);
const userInfoLoading = ref(false);
const isEditingUserInfo = ref(false);
const userInfoSaving = ref(false);
const userInfoFormRef = ref();
const userInfoForm = ref({
  email: '',
  phone: '',
  real_name: '',
  avatar: '',
  gender: 0,
  birthday: '',
});

// 密码表单验证规则
const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string) => {
        if (value && value !== passwordForm.value.new_password) {
          return Promise.reject('两次输入的密码不一致');
        }
        return Promise.resolve();
      },
      trigger: 'blur',
    },
  ],
};

// 用户信息表单验证规则
const userInfoRules = {
  real_name: [{ max: 50, message: '真实姓名不能超过50个字符', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }],
};

// 切换侧边栏折叠状态
const toggleCollapsed = () => {
  collapsed.value = !collapsed.value;
};

// 监听路由变化，更新选中的菜单
watch(
  () => route.path,
  (newPath) => {
    const menuKey = getMenuKeyByPath(newPath);
    selectedKeys.value = [menuKey];
  },
  { immediate: true }
);

// 处理菜单点击 - 使用路由导航
const handleMenuClick = ({ key }: { key: string }) => {
  console.log('🖱️ 菜单点击:', key);
  selectedKeys.value = [key];

  // 使用配置化的路径获取方法
  const path = getPathByMenuKey(key);
  console.log('🛣️ 获取到的路径:', path);

  router.push(path);
};

// 处理子菜单展开/收起
const handleOpenChange = (keys: string[]) => {
  openKeys.value = keys;
};

// 处理用户菜单点击
const handleUserMenuClick = ({ key }: { key: string }) => {
  console.log('用户菜单点击:', key);
  switch (key) {
    case 'change-password':
      console.log('打开修改密码弹窗');
      passwordModalVisible.value = true;
      console.log('passwordModalVisible.value:', passwordModalVisible.value);
      break;
    case 'user-info':
      console.log('打开个人信息弹窗');
      fetchCurrentUserInfo();
      userInfoModalVisible.value = true;
      break;
    case 'logout':
      handleLogout();
      break;
  }
};

// 退出登录
const handleLogout = async () => {
  try {
    await userStore.logout();
    message.success('退出登录成功');
    router.push('/login');
  } catch (error) {
    console.error('退出登录失败:', error);
    message.error('退出登录失败');
  }
};

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
    isFullscreen.value = true;
  } else {
    document.exitFullscreen();
    isFullscreen.value = false;
  }
};

// 监听全屏状态变化
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement;
};

// 快捷操作
const handleQuickAction = (action: string) => {
  switch (action) {
    case 'add-user':
      message.info('跳转到添加用户页面');
      break;
    case 'add-menu':
      message.info('跳转到添加菜单页面');
      break;
    case 'system-settings':
      message.info('跳转到系统设置页面');
      break;
    case 'backup':
      message.info('开始数据备份');
      break;
  }
};

// 获取当前用户信息
const fetchCurrentUserInfo = async () => {
  try {
    userInfoLoading.value = true;
    console.log('🔍 开始获取当前用户信息...');

    const response = await userApi.getUserInfo();
    console.log('📋 用户信息API响应:', response);

    if (response.success && response.data) {
      currentUserInfo.value = response.data;
      console.log('✅ 用户信息获取成功:', currentUserInfo.value);
    } else {
      console.error('❌ 获取用户信息失败:', response.message);
      message.error(response.message || '获取用户信息失败');
    }
  } catch (error) {
    console.error('❌ 获取用户信息异常:', error);
    message.error('获取用户信息失败，请稍后重试');
  } finally {
    userInfoLoading.value = false;
  }
};

const handleAdminAvatarBeforeUpload = async (file: File) => {
  const isImage = file.type.startsWith('image/');
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isImage) {
    message.error('只能上传图片文件作为头像');
    return false;
  }
  if (!isLt2M) {
    message.error('头像图片大小不能超过 2MB');
    return false;
  }

  try {
    const res: any = await userApi.uploadAvatar(file);
    const updated = res?.data ?? res;
    const newAvatar = updated?.avatar || updated?.avatar_url;

    if (newAvatar) {
      if (currentUserInfo.value) {
        currentUserInfo.value.avatar = newAvatar;
      }

      if (userInfoForm.value) {
        (userInfoForm.value as any).avatar = newAvatar;
      }

      if (userStore.userInfo) {
        userStore.userInfo.avatar = newAvatar;
        localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo));
      }

      const ok = typeof res?.success === 'boolean' ? res.success : true;
      if (ok) {
        message.success(res?.message || '头像上传成功');
      } else {
        message.error(res?.message || '头像上传失败');
      }
    } else {
      message.error(res?.message || '头像上传失败：未返回头像地址');
    }
  } catch (error: any) {
    message.error(error?.message || '头像上传失败，请稍后重试');
  }

  return false;
};

// 开始编辑用户信息
const startEditUserInfo = () => {
  if (currentUserInfo.value) {
    // 将当前用户信息填充到表单中，按照后端要求的格式
    userInfoForm.value = {
      email: currentUserInfo.value.email || '',
      phone: currentUserInfo.value.phone || '',
      real_name: currentUserInfo.value.real_name || '',
      avatar: currentUserInfo.value.avatar || '',
      gender: currentUserInfo.value.gender || 0,
      birthday: currentUserInfo.value.birthday || '',
    };
    isEditingUserInfo.value = true;
  }
};

// 保存用户信息
const handleUserInfoSave = async () => {
  try {
    await userInfoFormRef.value.validate();
    userInfoSaving.value = true;

    console.log('🔄 开始保存用户信息:', userInfoForm.value);

    const payload: any = { ...userInfoForm.value };
    // 头像在单独的上传接口中更新，这里不再提交 avatar 字段，避免 URL 校验报错
    if ('avatar' in payload) {
      delete payload.avatar;
    }

    const response = await userApi.updateUserInfo(payload);
    console.log('📋 更新用户信息API响应:', response);

    if (response.success && response.data) {
      currentUserInfo.value = response.data;
      message.success('个人信息更新成功');
      isEditingUserInfo.value = false;

      // 更新用户store中的信息
      if (userStore.userInfo) {
        Object.assign(userStore.userInfo, response.data);
      }
    } else {
      console.error('❌ 更新用户信息失败:', response.message);
      message.error(response.message || '更新用户信息失败');
    }
  } catch (error) {
    console.error('❌ 更新用户信息异常:', error);
    message.error('更新用户信息失败，请稍后重试');
  } finally {
    userInfoSaving.value = false;
  }
};

// 取消编辑用户信息
const handleUserInfoCancel = () => {
  if (isEditingUserInfo.value) {
    isEditingUserInfo.value = false;
    // 重置表单
    userInfoFormRef.value?.resetFields();
  } else {
    userInfoModalVisible.value = false;
  }
};

// 处理密码修改提交
const handlePasswordSubmit = async () => {
  try {
    await passwordFormRef.value.validate();
    passwordLoading.value = true;

    // 调试信息：检查token状态
    const token = localStorage.getItem('token');
    const userInfo = userStore.userInfo;
    console.log('🔍 调试信息:');
    console.log('Token存在:', !!token);
    console.log('Token长度:', token?.length || 0);
    console.log('用户信息:', userInfo);
    console.log('用户登录状态:', userStore.isLoggedIn);

    // 调用修改密码的API
    await userStore.updatePassword(passwordForm.value);

    message.success('密码修改成功');
    passwordModalVisible.value = false;
    resetPasswordForm();
  } catch (error) {
    console.error('密码修改失败:', error);
    message.error('密码修改失败，请检查当前密码是否正确');
  } finally {
    passwordLoading.value = false;
  }
};

// 取消密码修改
const handlePasswordCancel = () => {
  passwordModalVisible.value = false;
  resetPasswordForm();
};

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: '',
  };
  passwordFormRef.value?.resetFields();
};

onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange);
});

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange);
});
</script>

<style scoped lang="scss">
// 确保菜单可点击的全局重置
.admin-layout {
  min-height: 100vh;
  overflow: auto;
  background: linear-gradient(180deg, #0a192f 0%, #172a45 30%, #233e60 60%, #2d5280 100%);
  position: relative;
  z-index: 1;
}

// 确保所有元素都不会阻止菜单点击
:deep(*) {
  &::before,
  &::after {
    pointer-events: auto;
  }
}

// 专门针对侧边栏菜单的保护
:deep(.admin-menu *) {
  pointer-events: auto !important;
  cursor: pointer !important;
}

// 侧边栏 - 海洋科技风格
:deep(.admin-sider) {
  background: rgba(10, 25, 47, 0.95) !important;
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  box-shadow: 2px 0 20px rgba(100, 255, 218, 0.2);
  border-right: 2px solid rgba(100, 255, 218, 0.3);
  position: relative;
  z-index: 99999;
  pointer-events: auto !important;

  &::before,
  &::after {
    content: none !important;
  }

  .ant-layout-sider-children {
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 99999;
    pointer-events: auto !important;
  }
}

// Logo 区域 - 海洋科技风格
.logo {
  height: 72px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 24px;
  background: rgba(10, 25, 47, 0.95);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  margin-bottom: 0;
  border-bottom: 2px solid rgba(100, 255, 218, 0.3);
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  position: relative;

  .logo-icon-wrapper {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #64ffda 0%, #48cae4 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

    &:hover {
      transform: scale(1.05);
      box-shadow: 0 0 30px rgba(100, 255, 218, 0.7);
    }

    .logo-icon {
      font-size: 22px;
      color: #001d3d;
    }
  }

  .logo-text-wrapper {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;

    .logo-text {
      color: #64ffda;
      font-size: 17px;
      font-weight: 600;
      letter-spacing: -0.2px;
      line-height: 1.2;
      transition: color 0.3s ease;
      text-shadow: 0 0 10px rgba(202, 240, 248, 0.5);
    }

    .logo-subtitle {
      color: #a8b2d1;
      font-size: 11px;
      font-weight: 400;
      letter-spacing: 0.3px;
      text-transform: uppercase;
      text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);
    }
  }
}

// 顶部导航栏 - 海洋科技风格
.header {
  background: rgba(17, 34, 64, 0.9);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 0 28px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 20px rgba(100, 255, 218, 0.2);
  border-bottom: 2px solid rgba(100, 255, 218, 0.3);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    .trigger {
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 17px;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      border-radius: 8px;
      color: #a8b2d1;

      &:hover {
        background: rgba(100, 255, 218, 0.1);
        color: #64ffda;
        transform: scale(1.05);
      }

      &:active {
        transform: scale(0.95);
      }
    }

    .breadcrumb {
      :deep(.ant-breadcrumb-link) {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #a8b2d1;
        font-size: 13px;
        transition: color 0.2s ease;
        font-weight: 400;

        &:hover {
          color: #64ffda;
        }
      }

      :deep(.ant-breadcrumb-separator) {
        color: rgba(100, 255, 218, 0.3);
        margin: 0 10px;
      }

      .breadcrumb-icon {
        font-size: 13px;
        color: #90e0ef;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 8px;

    .header-action-btn {
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      color: #90e0ef;
      font-size: 17px;

      &:hover {
        background: rgba(100, 255, 218, 0.1);
        color: #64ffda;
        transform: scale(1.05);
      }

      &:active {
        transform: scale(0.95);
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 8px 4px 4px;
      cursor: pointer;
      border-radius: 20px;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      background: rgba(100, 255, 218, 0.05);
      position: relative;

      &:hover {
        background: rgba(100, 255, 218, 0.1);
        transform: scale(1.02);
      }

      &:active {
        transform: scale(0.98);
      }

      .user-avatar {
        flex-shrink: 0;
        border: 2px solid rgba(100, 255, 218, 0.4);
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.3);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      }

      &:hover .user-avatar {
        box-shadow: 0 0 25px rgba(100, 255, 218, 0.5);
      }

      .user-info-text {
        display: flex;
        flex-direction: column;
        gap: 0;
        min-width: 0;

        .username {
          font-weight: 500;
          color: #ccd6f6;
          font-size: 13px;
          line-height: 1.3;
          letter-spacing: -0.1px;
        }

        .user-role {
          font-size: 11px;
          color: #90e0ef;
          line-height: 1.3;
          font-weight: 400;
        }
      }

      .dropdown-icon {
        font-size: 10px;
        color: #90e0ef;
        transition: transform 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        margin-left: 4px;
        opacity: 0.7;
      }

      &:hover .dropdown-icon {
        transform: translateY(1px);
        opacity: 1;
        color: #64ffda;
      }
    }
  }
}

// 用户下拉菜单 - 海洋科技风格
:deep(.user-dropdown-menu) {
  border-radius: 14px;
  box-shadow:
    0 0 40px rgba(100, 255, 218, 0.3),
    0 0 0 2px rgba(100, 255, 218, 0.2);
  border: 2px solid rgba(100, 255, 218, 0.3);
  padding: 6px;
  background: rgba(17, 34, 64, 0.9);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  min-width: 200px;
  overflow: hidden;
  z-index: 1050 !important;
  position: relative;

  .ant-menu-item {
    border-radius: 10px;
    margin: 1px 0;
    height: 40px;
    line-height: 40px;
    padding: 0 14px;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    color: #ccd6f6;
    font-size: 14px;
    font-weight: 400;
    display: flex;
    align-items: center;
    gap: 12px;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%) scaleY(0);
      width: 3px;
      height: 20px;
      background: #64ffda;
      transition: transform 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      border-radius: 0 2px 2px 0;
      opacity: 0;
      box-shadow: 0 0 15px rgba(100, 255, 218, 0.5);
    }

    &:hover {
      background: rgba(100, 255, 218, 0.15);
      color: #64ffda;
      transform: translateX(2px);

      &::before {
        transform: translateY(-50%) scaleY(1);
        opacity: 1;
      }
    }

    &:active {
      transform: translateX(0);
      background: rgba(100, 255, 218, 0.2);
    }

    &.logout-item {
      color: #ff6b6b;

      &::before {
        background: #ff6b6b;
        box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
      }

      &:hover {
        background: rgba(255, 107, 107, 0.15);
        color: #ff6b6b;
        transform: translateX(2px);

        &::before {
          transform: translateY(-50%) scaleY(1);
          opacity: 1;
        }
      }

      &:active {
        background: rgba(255, 107, 107, 0.2);
        transform: translateX(0);
      }
    }

    .menu-icon {
      font-size: 16px;
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      color: #90e0ef;
      position: relative;
      opacity: 0.8;
    }

    &:hover .menu-icon {
      color: #64ffda;
      opacity: 1;
      transform: scale(1.08);
      filter: drop-shadow(0 0 10px rgba(100, 255, 218, 0.6));
    }

    &.logout-item .menu-icon {
      color: #ff6b6b;
      opacity: 0.9;
    }

    &.logout-item:hover .menu-icon {
      color: #ff6b6b;
      opacity: 1;
      transform: scale(1.08);
      filter: drop-shadow(0 0 10px rgba(255, 107, 107, 0.6));
    }

    .menu-text {
      flex: 1;
      letter-spacing: -0.2px;
      font-weight: 400;
      transition: font-weight 0.2s ease;
    }

    &:hover .menu-text {
      font-weight: 500;
    }
  }

  .ant-menu-item-icon {
    font-size: 16px;
    margin-right: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  // 分隔线样式
  .menu-divider,
  :deep(.ant-menu-item-divider) {
    margin: 8px 6px;
    border-color: rgba(0, 0, 0, 0.1);
    height: 0.5px;
    background: rgba(0, 0, 0, 0.1);
    border: none;
  }

  // 确保菜单项之间的间距
  .ant-menu-item + .ant-menu-item-divider {
    margin-top: 8px;
    margin-bottom: 8px;
  }

  // 第一个和最后一个菜单项的样式
  .ant-menu-item:first-child {
    margin-top: 0;
  }

  .ant-menu-item:last-child {
    margin-bottom: 0;
  }
}

// 确保下拉菜单容器有足够高的 z-index
:deep(.ant-dropdown) {
  z-index: 1050 !important;

  .ant-dropdown-menu {
    z-index: 1050 !important;
  }
}

// 内容区域 - 海洋科技风格
.content {
  margin: 0;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  border: none;
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  .content-wrapper {
    padding: 0;
    min-height: 0;
    height: auto;
    box-sizing: border-box;
    overflow: visible;
  }

  .dashboard-view {
    .ant-card {
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      border: 1px solid rgba(100, 255, 218, 0.2);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
      }

      .ant-statistic-title {
        color: #8892b0;
        font-size: 14px;
        font-weight: 500;
      }

      .ant-statistic-content {
        font-size: 28px;
        font-weight: 700;
      }
    }
  }

  .page-view {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
  }
}

// 底部 - 海洋科技风格
.footer {
  background: rgba(17, 34, 64, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  text-align: center;
  padding: 20px 28px;
  border-top: 1px solid rgba(100, 255, 218, 0.2);
  box-shadow: 0 -2px 20px rgba(100, 255, 218, 0.1);

  .footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;

    .footer-text {
      color: #90e0ef;
      font-size: 12px;
      font-weight: 400;
    }

    .footer-links {
      display: flex;
      align-items: center;
      gap: 4px;

      .footer-link {
        color: #90e0ef;
        text-decoration: none;
        font-size: 12px;
        transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 400;

        &:hover {
          color: #64ffda;
          background: rgba(100, 255, 218, 0.1);
        }
      }

      .footer-divider {
        margin: 0 4px;
        border-color: rgba(100, 255, 218, 0.3);
      }
    }
  }
}

// 个人信息弹窗样式
.loading-container {
  text-align: center;
  padding: 40px 0;

  p {
    margin-top: 16px;
    color: rgba(0, 0, 0, 0.65);
  }
}

.user-info-content {
  .user-avatar-section {
    text-align: center;
    padding: 20px 0;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 20px;
    position: relative;

    .large-avatar {
      margin-bottom: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .user-display-name {
      margin: 0 0 12px 0;
      font-size: 18px;
      font-weight: 600;
      color: rgba(0, 0, 0, 0.85);
    }

    .edit-btn {
      margin-top: 8px;
    }
  }

  .user-details {
    .ant-descriptions-item-label {
      font-weight: 500;
      color: rgba(0, 0, 0, 0.85);
      width: 100px;
    }

    .ant-descriptions-item-content {
      color: rgba(0, 0, 0, 0.65);
    }
  }

  .user-info-form {
    .ant-form-item {
      margin-bottom: 16px;
    }

    .ant-input,
    .ant-select,
    .ant-picker {
      border-radius: 4px;
    }

    .ant-form-item-label > label {
      font-weight: 500;
      color: rgba(0, 0, 0, 0.85);
    }
  }
}

.no-data {
  text-align: center;
  padding: 40px 0;
}

// 菜单样式 - 海洋科技风格
:deep(.admin-menu) {
  background: transparent !important;
  border: none;
  padding: 16px 12px;
  position: relative;
  z-index: 999999;
  pointer-events: auto !important;

  &::before,
  &::after {
    content: none !important;
  }

  .ant-menu-item,
  .ant-menu-submenu-title {
    height: 44px;
    line-height: 44px;
    margin: 2px 0;
    border-radius: 10px;
    padding: 0 14px !important;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    color: #90e0ef;
    font-weight: 400;
    font-size: 14px;
    position: relative;
    z-index: 999999;
    pointer-events: auto !important;
    cursor: pointer !important;

    &::before,
    &::after {
      content: none !important;
    }

    &:hover {
      background: rgba(100, 255, 218, 0.1) !important;
      color: #64ffda !important;
      transform: translateX(2px);

      .anticon {
        color: #64ffda;
        filter: drop-shadow(0 0 8px rgba(100, 255, 218, 0.5));
      }
    }

    .anticon {
      font-size: 17px;
      margin-right: 10px;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
  }

  .ant-menu-item-selected {
    background: rgba(100, 255, 218, 0.15) !important;
    color: #64ffda !important;
    font-weight: 500;
    box-shadow: 0 0 20px rgba(100, 255, 218, 0.2);

    &::after {
      display: none;
    }

    .anticon {
      color: #64ffda;
      filter: drop-shadow(0 0 10px rgba(100, 255, 218, 0.6));
    }
  }

  .ant-menu-submenu {
    .ant-menu-submenu-title {
      &:hover {
        background: rgba(100, 255, 218, 0.1) !important;
        color: #64ffda !important;
      }
    }

    &.ant-menu-submenu-open {
      .ant-menu-submenu-title {
        background: rgba(100, 255, 218, 0.1) !important;
        color: #64ffda !important;

        .anticon {
          color: #64ffda;
        }
      }
    }

    .ant-menu {
      background: rgba(0, 29, 61, 0.5) !important;
      padding: 6px 0;
      margin: 6px 0;
      border-radius: 8px;
      border: 1px solid rgba(100, 255, 218, 0.2);

      .ant-menu-item {
        height: 36px;
        line-height: 36px;
        margin: 1px 6px;
        padding-left: 44px !important;
        border-radius: 8px;
        font-size: 13px;

        &:hover {
          background: rgba(100, 255, 218, 0.1) !important;
          color: #64ffda !important;
        }

        &.ant-menu-item-selected {
          background: rgba(100, 255, 218, 0.15) !important;
          color: #64ffda !important;
          font-weight: 500;
        }
      }
    }
  }

  // 折叠状态下的菜单样式
  &.ant-menu-inline-collapsed {
    .ant-menu-item,
    .ant-menu-submenu-title {
      padding: 0 14px !important;
      text-align: center;

      .anticon {
        margin-right: 0;
      }
    }
  }
}

// 无权限提示样式 - 智慧监控系统风格
.no-permission {
  padding: 40px 20px;
  text-align: center;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;

  .no-permission-content {
    color: #6b7280;

    .no-permission-icon {
      font-size: 64px;
      margin-bottom: 20px;
      color: #d1d5db;
      opacity: 0.6;
    }

    .no-permission-text {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 12px;
      color: #374151;
    }

    .no-permission-desc {
      font-size: 14px;
      margin: 0;
      color: #6b7280;
      line-height: 1.6;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header {
    padding: 0 16px;
    height: 64px;

    .header-left {
      .breadcrumb {
        display: none;
      }
    }

    .header-right {
      .user-info {
        .user-info-text {
          display: none;
        }
      }
    }
  }

  .logo {
    padding: 12px 16px;
    height: 64px;

    .logo-text-wrapper {
      .logo-subtitle {
        display: none;
      }
    }
  }

  .footer {
    padding: 16px;

    .footer-content {
      flex-direction: column;
      gap: 12px;

      .footer-links {
        flex-wrap: wrap;
        justify-content: center;
      }
    }
  }
}
</style>
