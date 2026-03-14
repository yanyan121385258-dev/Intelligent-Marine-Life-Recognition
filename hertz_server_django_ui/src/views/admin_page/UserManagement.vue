<template>
  <div class="user-management">
    <!-- 页面头部 - 苹果风格 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <UserOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">用户管理</h1>
          <p class="page-description">管理系统用户信息与权限配置</p>
        </div>
      </div>
    </div>

    <!-- 操作栏 - 苹果风格 -->
    <div class="action-bar">
      <div class="search-section">
        <a-input
          v-model:value="searchKeyword"
          placeholder="搜索用户名、邮箱..."
          style="width: 300px"
          @pressEnter="handleSearch"
          allow-clear
        />
        <a-button
          type="primary"
          class="search-btn"
          style="margin-left: 12px"
          :loading="loading"
          @click="handleSearch"
        >
          查询
        </a-button>
        <a-select
          v-model:value="statusFilter"
          placeholder="用户状态"
          style="width: 120px; margin-left: 12px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option :value="1">活跃</a-select-option>
          <a-select-option :value="0">禁用</a-select-option>
        </a-select>
        <a-select
          v-model:value="roleFilter"
          placeholder="用户角色"
          style="width: 150px; margin-left: 12px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option
            v-for="role in availableRolesForFilter"
            :key="role.role_id"
            :value="role.role_id"
          >
            {{ role.role_name }}
          </a-select-option>
        </a-select>
      </div>
      <div class="button-section">
        <a-button type="primary" @click="handleAdd" class="action-btn-primary">
          <template #icon><PlusOutlined /></template>
          添加用户
        </a-button>
        <a-button
          danger
          :disabled="selectedRowKeys.length === 0"
          @click="handleBatchDelete"
          class="action-btn-danger"
        >
          <template #icon><DeleteOutlined /></template>
          批量删除
        </a-button>
        <a-button @click="handleRefresh" class="action-btn-secondary">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </div>
    </div>

    <!-- 用户表格 -->
    <div class="table-container">
      <a-table
        :columns="columns"
        :data-source="userList"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        row-key="user_id"
        @change="handleTableChange"
      >
        <!-- 用户名列 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'username'">
            <div class="user-info">
              <a-avatar :size="32" style="margin-right: 8px">
                {{ record.username.charAt(0).toUpperCase() }}
              </a-avatar>
              <div>
                <div class="username">{{ record.username }}</div>
                <div class="email">{{ record.email }}</div>
              </div>
            </div>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.key === 'status'">
            <a-tag :color="record.status === 1 ? 'green' : 'red'">
              {{ record.status === 1 ? '活跃' : '禁用' }}
            </a-tag>
          </template>

          <!-- 角色列 -->
          <template v-else-if="column.key === 'role'">
            <a-space v-if="record.roles && record.roles.length > 0">
              <a-tag
                v-for="role in record.roles"
                :key="role.role_id"
                :color="role.role_code === 'super_admin' ? 'purple' : 'blue'"
              >
                {{ role.role_name }}
              </a-tag>
            </a-space>
            <a-tag v-else color="default">普通用户</a-tag>
          </template>

          <!-- 最后登录列 -->
          <template v-else-if="column.key === 'last_login_time'">
            <span v-if="record.last_login_time">
              {{ formatDate(record.last_login_time) }}
            </span>
            <span v-else class="text-gray">从未登录</span>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleViewDetail(record)">
                查看详情
              </a-button>
              <a-button type="link" size="small" @click="handleEdit(record)"> 编辑 </a-button>
              <a-button type="link" size="small" @click="handleAssignRoles(record)">
                分配角色
              </a-button>
              <a-button type="link" size="small" danger @click="handleDelete(record)">
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 用户详情/编辑弹窗 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      width="600px"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form ref="formRef" :model="formData" :rules="formRules" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="用户名" name="username">
              <a-input v-model:value="formData.username" placeholder="请输入用户名" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="邮箱" name="email">
              <a-input v-model:value="formData.email" placeholder="请输入邮箱" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="真实姓名" name="real_name">
              <a-input v-model:value="formData.real_name" placeholder="请输入真实姓名" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="手机号" name="phone">
              <a-input v-model:value="formData.phone" placeholder="请输入手机号" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="性别" name="gender">
              <a-select v-model:value="formData.gender" placeholder="请选择性别">
                <a-select-option :value="1">男</a-select-option>
                <a-select-option :value="2">女</a-select-option>
                <a-select-option :value="0">未知</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="生日" name="birthday">
              <a-date-picker
                v-model:value="formData.birthday"
                placeholder="请选择生日"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="部门ID" name="department_id">
              <a-input-number
                v-model:value="formData.department_id"
                placeholder="请输入部门ID"
                style="width: 100%"
                :min="0"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="24">
            <a-form-item label="头像URL" name="avatar">
              <a-input v-model:value="formData.avatar" placeholder="请输入头像URL" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16" v-if="modalMode === 'add'">
          <a-col :span="24">
            <a-form-item label="密码" name="password">
              <a-input-password v-model:value="formData.password" placeholder="请输入密码" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="24">
            <a-form-item label="状态" name="status">
              <a-select v-model:value="formData.status" placeholder="请选择状态">
                <a-select-option :value="1">活跃</a-select-option>
                <a-select-option :value="0">禁用</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 用户详情弹窗 -->
    <a-modal v-model:visible="detailModalVisible" title="用户详情" width="700px" :footer="null">
      <div v-if="userDetail" class="user-detail-content">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="用户ID">
            {{ userDetail.user_id }}
          </a-descriptions-item>
          <a-descriptions-item label="用户名">
            {{ userDetail.username }}
          </a-descriptions-item>
          <a-descriptions-item label="邮箱">
            {{ userDetail.email }}
          </a-descriptions-item>
          <a-descriptions-item label="真实姓名">
            {{ userDetail.real_name || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="手机号">
            {{ userDetail.phone || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="性别">
            {{ getGenderText(userDetail.gender) }}
          </a-descriptions-item>
          <a-descriptions-item label="生日">
            {{ userDetail.birthday || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="部门ID">
            {{ userDetail.department_id || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="userDetail.status === 1 ? 'green' : 'red'">
              {{ userDetail.status === 1 ? '活跃' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="角色">
            <a-space v-if="userDetail.roles && userDetail.roles.length > 0">
              <a-tag
                v-for="role in userDetail.roles"
                :key="role.role_id"
                :color="role.role_code === 'super_admin' ? 'purple' : 'blue'"
              >
                {{ role.role_name }}
              </a-tag>
            </a-space>
            <a-tag v-else color="default">普通用户</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="注册时间">
            {{ formatDate(userDetail.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="更新时间">
            {{ formatDate(userDetail.updated_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="最后登录时间">
            {{ userDetail.last_login_time ? formatDate(userDetail.last_login_time) : '从未登录' }}
          </a-descriptions-item>
          <a-descriptions-item label="最后登录IP">
            {{ userDetail.last_login_ip || '-' }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
      <div v-else class="loading-container">
        <a-spin size="large" />
      </div>
    </a-modal>

    <!-- 角色分配弹窗 -->
    <a-modal
      v-model:visible="roleModalVisible"
      title="分配角色"
      width="500px"
      @ok="handleRoleModalOk"
      @cancel="handleRoleModalCancel"
    >
      <div v-if="currentRoleUser" class="role-assign-content">
        <div class="user-info-section">
          <h4>用户信息</h4>
          <p><strong>用户名：</strong>{{ currentRoleUser.username }}</p>
          <p><strong>邮箱：</strong>{{ currentRoleUser.email }}</p>
          <p>
            <strong>当前角色：</strong>
            <a-space v-if="currentRoleUser.roles && currentRoleUser.roles.length > 0">
              <a-tag
                v-for="role in currentRoleUser.roles"
                :key="role.role_id"
                :color="role.role_code === 'super_admin' ? 'purple' : 'blue'"
              >
                {{ role.role_name }}
              </a-tag>
            </a-space>
            <a-tag v-else color="default">普通用户</a-tag>
          </p>
        </div>

        <a-divider />

        <div class="role-selection-section">
          <h4>选择角色</h4>
          <a-form :model="roleFormData" layout="vertical">
            <a-form-item label="角色" name="role_code">
              <a-radio-group v-model:value="roleFormData.role_code">
                <a-row>
                  <!-- 动态生成角色选项 -->
                  <a-col
                    :span="24"
                    v-for="role in availableRoles"
                    :key="role.role_id"
                    style="margin-bottom: 8px"
                  >
                    <a-radio :value="role.role_id">
                      <a-tag
                        :color="
                          role.role_code === 'super_admin'
                            ? 'purple'
                            : role.role_code === 'admin'
                              ? 'blue'
                              : 'default'
                        "
                        style="margin-left: 8px"
                      >
                        {{ role.role_name }}
                      </a-tag>
                      <span style="margin-left: 8px; color: #666">{{ role.role_code }}</span>
                    </a-radio>
                  </a-col>
                  <!-- 如果没有角色数据，显示加载状态或默认选项 -->
                  <a-col :span="24" v-if="availableRoles.length === 0">
                    <a-spin size="small" style="margin-right: 8px" />
                    <span style="color: #666">正在加载角色列表...</span>
                  </a-col>
                </a-row>
              </a-radio-group>
            </a-form-item>
          </a-form>
        </div>
      </div>
      <div v-else class="loading-container">
        <a-spin size="large" />
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { PlusOutlined, DeleteOutlined, ReloadOutlined, UserOutlined } from '@ant-design/icons-vue';
import { userApi } from '@/api';
import type { User, UserListResponse, Role, AssignRolesParams } from '@/api';
import type { TableColumnsType, TableProps } from 'ant-design-vue';

// 响应式数据
const loading = ref(false);
const userList = ref<User[]>([]);
const selectedRowKeys = ref<number[]>([]);
const searchKeyword = ref('');
const statusFilter = ref<number | ''>('');
const roleFilter = ref<number | ''>('');
const currentUserInfo = ref<User | null>(null);
const availableRolesForFilter = ref<Role[]>([]);

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 5, // 改为5条，更容易看到分页效果
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number, range: [number, number]) =>
    `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
  pageSizeOptions: ['5', '10', '20', '50'], // 添加5条选项
  showLessItems: false,
  size: 'default',
  hideOnSinglePage: false, // 即使只有一页也显示分页器
});

// 弹窗相关
const modalVisible = ref(false);
const modalMode = ref<'add' | 'edit'>('add');
const currentUser = ref<User | null>(null);
const formRef = ref();

// 用户详情弹窗相关
const detailModalVisible = ref(false);
const userDetail = ref<User | null>(null);

// 角色分配弹窗相关
const roleModalVisible = ref(false);
const currentRoleUser = ref<User | null>(null);
const availableRoles = ref<Role[]>([]);
const roleFormData = ref<{
  role_code: number;
}>({
  role_code: 0, // 默认为普通用户
});

// 表单数据
const formData = reactive({
  username: '',
  email: '',
  phone: '',
  real_name: '',
  avatar: '',
  gender: 0,
  birthday: '',
  department_id: 0,
  status: 1,
  password: '',
});

// 表单验证规则
const formRules = computed(() => ({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: modalMode.value === 'add', message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20个字符', trigger: 'blur' },
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }],
  real_name: [{ min: 2, max: 20, message: '真实姓名长度为2-20个字符', trigger: 'blur' }],
  avatar: [{ type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  birthday: [{ type: 'string', message: '请选择正确的日期格式', trigger: 'change' }],
  department_id: [{ type: 'number', min: 0, message: '部门ID必须为非负数', trigger: 'blur' }],
  status: [{ required: true, message: '请选择用户状态', trigger: 'change' }],
}));

// 计算属性
const modalTitle = computed(() => (modalMode.value === 'add' ? '添加用户' : '编辑用户'));

// 表格列配置
const columns: TableColumnsType = [
  {
    title: '用户信息',
    key: 'username',
    width: 250,
    fixed: 'left',
  },
  {
    title: '真实姓名',
    dataIndex: 'real_name',
    key: 'real_name',
    width: 120,
    customRender: ({ text }) => text || '-',
  },
  {
    title: '手机号',
    dataIndex: 'phone',
    key: 'phone',
    width: 130,
    customRender: ({ text }) => text || '-',
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
  },
  {
    title: '角色',
    key: 'role',
    width: 120,
  },
  {
    title: '注册时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
    customRender: ({ text }) => formatDate(text),
  },
  {
    title: '最后登录',
    key: 'last_login_time',
    width: 150,
  },
  {
    title: '操作',
    key: 'action',
    width: 180,
    fixed: 'right',
  },
];

// 行选择配置
const rowSelection: TableProps['rowSelection'] = {
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys: number[]) => {
    selectedRowKeys.value = keys;
  },
};

// 方法
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('zh-CN');
};

const getGenderText = (gender: number) => {
  switch (gender) {
    case 1:
      return '男';
    case 2:
      return '女';
    default:
      return '未知';
  }
};

// 获取当前用户信息
const fetchCurrentUserInfo = async () => {
  try {
    const response = await userApi.getUserInfo();
    if (response.success) {
      currentUserInfo.value = response.data;
      console.log('当前用户信息:', response.data);
    } else {
      message.error(response.message || '获取用户信息失败');
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
    message.error('获取用户信息失败');
  }
};

// 存储所有用户数据（用于客户端筛选）
const allUsers = ref<User[]>([]);

const fetchUserList = async () => {
  try {
    loading.value = true;

    // 检查是否需要客户端筛选（如果后端不支持这些参数）
    const needsClientFilter =
      (searchKeyword.value && searchKeyword.value.trim()) ||
      (roleFilter.value !== '' && roleFilter.value !== null && roleFilter.value !== undefined);

    // 构建查询参数
    const params: any = {
      page: pagination.current,
      page_size: needsClientFilter ? 1000 : pagination.pageSize, // 如果需要客户端筛选，获取更多数据
    };

    // 只有当搜索关键词不为空时才添加search参数
    if (searchKeyword.value && searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }

    // 只有当状态筛选有值时才添加status参数
    if (
      statusFilter.value !== '' &&
      statusFilter.value !== null &&
      statusFilter.value !== undefined
    ) {
      params.status = statusFilter.value;
    }

    // 只有当角色筛选有值时才添加role_ids参数
    if (roleFilter.value !== '' && roleFilter.value !== null && roleFilter.value !== undefined) {
      params.role_ids = String(roleFilter.value);
    }

    console.log('🔍 搜索参数:', params);
    console.log('🔍 搜索关键词:', searchKeyword.value);
    console.log('🔍 状态筛选:', statusFilter.value);
    console.log('🔍 角色筛选:', roleFilter.value);
    console.log('🔍 需要客户端筛选:', needsClientFilter);

    const response = await userApi.getUserList(params);
    if (response.success) {
      let filteredList = response.data.list;

      // 如果后端不支持搜索或角色筛选，在前端进行客户端筛选
      if (needsClientFilter) {
        // 保存所有数据用于筛选
        allUsers.value = response.data.list;

        // 客户端搜索筛选
        if (searchKeyword.value && searchKeyword.value.trim()) {
          const keyword = searchKeyword.value.trim().toLowerCase();
          filteredList = filteredList.filter((user: User) => {
            const username = (user.username || '').toLowerCase();
            const email = (user.email || '').toLowerCase();
            const realName = (user.real_name || '').toLowerCase();
            return (
              username.includes(keyword) || email.includes(keyword) || realName.includes(keyword)
            );
          });
        }

        // 客户端角色筛选
        if (
          roleFilter.value !== '' &&
          roleFilter.value !== null &&
          roleFilter.value !== undefined
        ) {
          filteredList = filteredList.filter((user: User) => {
            if (!user.roles || user.roles.length === 0) {
              return false;
            }
            return user.roles.some((role) => role.role_id === roleFilter.value);
          });
        }

        // 客户端分页
        const startIndex = (pagination.current - 1) * pagination.pageSize;
        const endIndex = startIndex + pagination.pageSize;
        const paginatedList = filteredList.slice(startIndex, endIndex);

        userList.value = paginatedList;
        pagination.total = filteredList.length; // 使用筛选后的总数
        console.log('✅ 客户端筛选后总数:', filteredList.length, '条');
        console.log('✅ 当前页显示:', paginatedList.length, '条');
      } else {
        // 不需要客户端筛选，直接使用后端返回的数据
        userList.value = filteredList;
        pagination.total = response.data.total;
        console.log('✅ 获取到用户列表:', userList.value.length, '条');
      }
    } else {
      message.error(response.message || '获取用户列表失败');
    }
  } catch (error) {
    console.error('获取用户列表失败:', error);
    message.error('获取用户列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取角色列表用于筛选
const fetchRolesForFilter = async () => {
  try {
    const response = await userApi.getRoleList();
    if (response.success && response.data) {
      // 检查返回的数据结构：可能是数组或包含list的对象
      availableRolesForFilter.value = Array.isArray(response.data)
        ? response.data
        : (response.data as any).list || [];
    }
  } catch (error) {
    console.error('获取角色列表失败:', error);
  }
};

// 重置分页到第一页
const resetPagination = () => {
  pagination.current = 1;
};

const handleSearch = () => {
  resetPagination();
  fetchUserList();
};

const handleRefresh = () => {
  searchKeyword.value = '';
  statusFilter.value = '';
  roleFilter.value = '';
  resetPagination();
  // 刷新时重新获取角色列表，确保数据是最新的
  fetchRolesForFilter();
  fetchUserList();
};

const handleTableChange = (pag: any, filters: any, sorter: any) => {
  console.log('分页参数变化:', pag);
  console.log('筛选参数:', filters);
  console.log('排序参数:', sorter);

  // 更新分页参数
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;

  // 重新获取数据
  fetchUserList();
};

const testModal = () => {
  console.log('=== 测试模态框 ===');
  console.log('测试前detailModalVisible状态:', detailModalVisible.value);
  detailModalVisible.value = true;
  console.log('测试后detailModalVisible状态:', detailModalVisible.value);

  // 设置一些测试数据
  userDetail.value = {
    user_id: 1,
    username: 'test_user',
    email: 'test@example.com',
    real_name: '测试用户',
    phone: '13800138000',
    gender: 1,
    birthday: '1990-01-01',
    department_id: 1,
    status: 1,
    roles: [{ role_id: 1, role_name: '管理员', role_code: 'admin' }],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    last_login_time: '2024-01-01T00:00:00Z',
    last_login_ip: '127.0.0.1',
  };
  console.log('设置测试数据:', userDetail.value);
};

const handleViewDetail = async (user: User) => {
  try {
    console.log('=== 开始查看用户详情 ===');
    console.log('点击查看详情，用户信息:', user);
    console.log('当前detailModalVisible状态:', detailModalVisible.value);

    detailModalVisible.value = true;
    userDetail.value = null; // 先清空，显示加载状态

    console.log('设置后detailModalVisible状态:', detailModalVisible.value);
    console.log('设置后userDetail状态:', userDetail.value);

    // 添加一个短暂延迟来确保DOM更新
    await new Promise((resolve) => setTimeout(resolve, 100));
    console.log('延迟后detailModalVisible状态:', detailModalVisible.value);

    const response = await userApi.getUser(user.user_id);
    console.log('API响应:', response);
    if (response.success) {
      userDetail.value = response.data;
      console.log('用户详情数据设置为:', userDetail.value);
    } else {
      message.error(response.message || '获取用户详情失败');
      detailModalVisible.value = false;
    }
    console.log('=== 查看用户详情结束 ===');
  } catch (error) {
    console.error('获取用户详情失败:', error);
    message.error('获取用户详情失败');
    detailModalVisible.value = false;
  }
};

// 分配角色
const handleAssignRoles = async (user: User) => {
  console.log('分配角色被点击，用户数据:', user);

  try {
    roleModalVisible.value = true;
    currentRoleUser.value = null;
    availableRoles.value = [];
    roleFormData.value.role_code = 0; // 默认为普通用户

    // 并行获取用户详情和角色列表
    const [userResponse, rolesResponse] = await Promise.all([
      userApi.getUser(user.user_id),
      userApi.getRoleList(),
    ]);

    // 处理角色列表
    if (rolesResponse.success && rolesResponse.data) {
      // 检查返回的数据结构：可能是数组或包含list的对象
      availableRoles.value = Array.isArray(rolesResponse.data)
        ? rolesResponse.data
        : (rolesResponse.data as any).list || [];
      console.log('获取到的角色列表:', availableRoles.value);
    } else {
      message.error(rolesResponse.message || '获取角色列表失败');
      // 即使角色列表获取失败，也不关闭弹窗，使用默认角色
      availableRoles.value = [];
    }

    // 处理用户详情
    if (userResponse.success && userResponse.data) {
      currentRoleUser.value = userResponse.data;
      // 根据用户当前角色设置role_code，使用动态角色列表中的role_id
      if (userResponse.data.roles && userResponse.data.roles.length > 0) {
        const currentRole = userResponse.data.roles[0];
        // 在可用角色列表中查找匹配的角色
        const matchedRole = availableRoles.value.find(
          (role) => role.role_code === currentRole.role_code
        );
        if (matchedRole) {
          roleFormData.value.role_code = matchedRole.role_id;
        } else {
          // 如果找不到匹配的角色，使用第一个可用角色或默认值
          roleFormData.value.role_code =
            availableRoles.value.length > 0 ? availableRoles.value[0].role_id : 0;
        }
      } else {
        // 如果用户没有角色，使用第一个可用角色或默认值
        roleFormData.value.role_code =
          availableRoles.value.length > 0 ? availableRoles.value[0].role_id : 0;
      }
    } else {
      message.error(userResponse.message || '获取用户信息失败');
      roleModalVisible.value = false;
      return;
    }
  } catch (error) {
    console.error('获取角色分配数据失败:', error);
    message.error('获取角色分配数据失败');
    roleModalVisible.value = false;
  }
};

// 角色分配弹窗确认
const handleRoleModalOk = async () => {
  if (!currentRoleUser.value) {
    message.error('用户信息不存在');
    return;
  }

  try {
    const params: AssignRolesParams = {
      user_id: currentRoleUser.value.user_id,
      role_ids: [roleFormData.value.role_code],
    };

    console.log('角色分配请求数据:', params);
    console.log('用户ID:', params.user_id);
    console.log('角色IDs:', params.role_ids);

    const response = await userApi.assignRoles(params);
    if (response.success) {
      message.success('角色分配成功');
      roleModalVisible.value = false;
      // 刷新用户列表
      await fetchUserList();
    } else {
      message.error(response.message || '角色分配失败');
    }
  } catch (error) {
    console.error('角色分配失败:', error);
    message.error('角色分配失败');
  }
};

// 角色分配弹窗取消
const handleRoleModalCancel = () => {
  roleModalVisible.value = false;
  currentRoleUser.value = null;
  roleFormData.value.role_code = 0;
};

const handleAdd = () => {
  modalMode.value = 'add';
  currentUser.value = null;
  resetForm();
  modalVisible.value = true;
};

const handleEdit = (user: User) => {
  modalMode.value = 'edit';
  currentUser.value = user;
  Object.assign(formData, {
    username: user.username,
    email: user.email,
    phone: user.phone || '',
    real_name: user.real_name || '',
    avatar: user.avatar || '',
    gender: user.gender,
    birthday: user.birthday || '',
    department_id: user.department_id || 0,
    status: user.status,
    password: '', // 编辑时密码字段为空
  });
  modalVisible.value = true;
};

const handleDelete = (user: User) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        const response = await userApi.deleteUser(user.user_id);
        if (response.success) {
          message.success('删除成功');
          fetchUserList();
        } else {
          message.error(response.message || '删除用户失败');
        }
      } catch (error) {
        console.error('删除用户失败:', error);
        message.error('删除用户失败');
      }
    },
  });
};

const handleBatchDelete = () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要删除的用户');
    return;
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个用户吗？此操作不可恢复。`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        loading.value = true;
        const deletePromises = selectedRowKeys.value.map((id) => userApi.deleteUser(id));

        const results = await Promise.allSettled(deletePromises);
        const successCount = results.filter(
          (r) => r.status === 'fulfilled' && r.value.success
        ).length;
        const failCount = results.length - successCount;

        if (successCount > 0) {
          message.success(
            `成功删除 ${successCount} 个用户${failCount > 0 ? `，${failCount} 个删除失败` : ''}`
          );
          selectedRowKeys.value = [];
          await fetchUserList();
        } else {
          message.error('批量删除失败，请重试');
        }
      } catch (error) {
        console.error('批量删除失败:', error);
        message.error('批量删除失败');
      } finally {
        loading.value = false;
      }
    },
  });
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();

    let response;
    if (modalMode.value === 'add') {
      // 添加模式：确保数据格式符合后端API要求
      const createData = {
        username: formData.username,
        email: formData.email,
        phone: formData.phone || '',
        real_name: formData.real_name || '',
        avatar: formData.avatar || '',
        gender: Number(formData.gender),
        birthday: formData.birthday || '',
        department_id: Number(formData.department_id),
        status: Number(formData.status),
        password: formData.password,
      };

      response = await userApi.createUser(createData);
      if (response.success) {
        message.success('添加用户成功');
      } else {
        message.error(response.message || '添加用户失败');
        return;
      }
    } else {
      // 编辑模式：发送完整的用户数据，包括未修改的字段
      const updateData = {
        username: formData.username || currentUser.value!.username,
        email: formData.email || currentUser.value!.email,
        phone: formData.phone || currentUser.value!.phone || '',
        real_name: formData.real_name || currentUser.value!.real_name || '',
        avatar: formData.avatar || currentUser.value!.avatar || '',
        gender: formData.gender !== undefined ? Number(formData.gender) : currentUser.value!.gender,
        birthday: formData.birthday || currentUser.value!.birthday || '',
        department_id:
          formData.department_id !== undefined
            ? Number(formData.department_id)
            : currentUser.value!.department_id || 0,
        status: formData.status !== undefined ? Number(formData.status) : currentUser.value!.status,
        password: formData.password || '', // 如果没有输入新密码，发送空字符串
      };

      response = await userApi.updateUser(currentUser.value!.user_id, updateData);
      if (response.success) {
        message.success('更新用户成功');
      } else {
        message.error(response.message || '更新用户失败');
        return;
      }
    }

    modalVisible.value = false;
    await fetchUserList();
  } catch (error) {
    console.error('操作失败:', error);
    if (error.response && error.response.data && error.response.data.message) {
      message.error(error.response.data.message);
    } else {
      message.error('操作失败，请检查网络连接或联系管理员');
    }
  }
};

const handleModalCancel = () => {
  modalVisible.value = false;
  resetForm();
};

const resetForm = () => {
  Object.assign(formData, {
    username: '',
    email: '',
    phone: '',
    real_name: '',
    avatar: '',
    gender: 0,
    birthday: '',
    department_id: 0,
    status: 1,
    password: '',
  });
  formRef.value?.resetFields();
};

// 生命周期
onMounted(() => {
  fetchCurrentUserInfo();
  fetchRolesForFilter();
  fetchUserList();
});
</script>

<style scoped lang="scss">
.user-management {
  padding: 0;
  background: #f5f5f7;
  min-height: 100vh;

  // 页面头部 - 苹果风格
  .page-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    padding: 32px 28px;
    margin-bottom: 24px;
    border-radius: 0;
    box-shadow: 0 0.5px 0 rgba(0, 0, 0, 0.08);
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

    .header-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .header-icon-wrapper {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(16, 185, 129, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(16, 185, 129, 0.15);
        }

        .header-icon {
          font-size: 24px;
          color: #10b981;
        }
      }

      .header-text {
        .page-title {
          font-size: 24px;
          font-weight: 600;
          color: #1d1d1f;
          margin: 0 0 4px 0;
          letter-spacing: -0.3px;
          line-height: 1.2;
        }

        .page-description {
          color: #86868b;
          font-size: 14px;
          margin: 0;
          font-weight: 400;
        }
      }
    }
  }

  // 操作栏 - 苹果风格
  .action-bar {
    margin: 0 28px 24px 28px;
    padding: 20px 24px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .search-section {
      display: flex;
      align-items: center;
      flex: 1;

      :deep(.ant-input-search) {
        .ant-input-affix-wrapper {
          border-radius: 12px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }

          &.ant-input-affix-wrapper-focused {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }

        .ant-input-search-button {
          border-radius: 0 12px 12px 0;
          border-left: none;
        }
      }

      :deep(.ant-select) {
        .ant-select-selector {
          border-radius: 12px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }
        }

        &.ant-select-focused .ant-select-selector {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }
    }

    .button-section {
      display: flex;
      gap: 12px;

      .action-btn-primary {
        border-radius: 12px;
        height: 40px;
        padding: 0 20px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
        }

        &:active {
          transform: translateY(0);
        }
      }

      .action-btn-danger {
        border-radius: 12px;
        height: 40px;
        padding: 0 20px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }

        &:active:not(:disabled) {
          transform: translateY(0);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }

      .action-btn-secondary {
        border-radius: 12px;
        height: 40px;
        padding: 0 20px;
        font-weight: 500;
        border-color: rgba(0, 0, 0, 0.12);
        color: #1d1d1f;
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          background: rgba(0, 0, 0, 0.04);
          border-color: rgba(0, 0, 0, 0.16);
          transform: translateY(-1px);
        }

        &:active {
          transform: translateY(0);
        }
      }
    }
  }

  // 表格容器 - 苹果风格
  .table-container {
    margin: 0 28px 24px 28px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    :deep(.ant-table) {
      background: transparent;

      .ant-table-thead > tr > th {
        background: rgba(0, 0, 0, 0.02);
        font-weight: 600;
        color: #1d1d1f;
        border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
        padding: 16px;
        font-size: 13px;
        letter-spacing: -0.1px;
      }

      .ant-table-tbody > tr {
        transition: all 0.2s ease;

        &:hover > td {
          background: rgba(0, 0, 0, 0.02);
        }

        > td {
          padding: 16px;
          border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
          color: #1d1d1f;
        }
      }
    }

    .user-info {
      display: flex;
      align-items: center;

      :deep(.ant-avatar) {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        font-weight: 600;
      }

      .username {
        font-weight: 500;
        color: #1d1d1f;
        font-size: 14px;
        margin-bottom: 2px;
      }

      .email {
        font-size: 12px;
        color: #86868b;
        margin-top: 2px;
      }
    }

    .text-gray {
      color: #86868b;
    }

    // 分页器样式优化 - 苹果风格
    :deep(.ant-pagination) {
      margin: 20px 24px;
      padding: 16px 0;
      text-align: center;
      background: rgba(0, 0, 0, 0.02);
      border-top: 0.5px solid rgba(0, 0, 0, 0.08);

      .ant-pagination-total-text {
        color: #86868b;
        font-size: 13px;
        font-weight: 400;
      }

      .ant-pagination-item {
        border-radius: 8px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
        margin: 0 4px;
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          border-color: #3b82f6;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
        }

        &.ant-pagination-item-active {
          background: #3b82f6;
          border-color: #3b82f6;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);

          a {
            color: white;
            font-weight: 600;
          }
        }
      }

      .ant-pagination-prev,
      .ant-pagination-next {
        border-radius: 8px;
        margin: 0 8px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          border-color: #3b82f6;
          color: #3b82f6;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
        }
      }

      .ant-pagination-jump-prev,
      .ant-pagination-jump-next {
        border-radius: 8px;
      }

      .ant-select {
        margin: 0 8px;

        .ant-select-selector {
          border-radius: 8px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }
        }
      }

      .ant-pagination-options-quick-jumper {
        margin-left: 16px;
        color: #86868b;
        font-size: 13px;

        input {
          border-radius: 8px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }

          &:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }
      }
    }
  }

  .user-detail-content {
    .loading-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
    }

    .role-assign-content {
      .user-info-section {
        h4 {
          margin-bottom: 12px;
          color: #1d1d1f;
          font-weight: 600;
        }

        p {
          margin-bottom: 8px;
          line-height: 1.6;
          color: #86868b;

          strong {
            color: #1d1d1f;
            margin-right: 8px;
          }
        }
      }

      .role-selection-section {
        h4 {
          margin-bottom: 16px;
          color: #1d1d1f;
          font-weight: 600;
        }

        .ant-checkbox-wrapper {
          display: flex;
          align-items: center;
          padding: 8px 12px;
          border-radius: 8px;
          transition: background-color 0.2s;

          &:hover {
            background-color: rgba(0, 0, 0, 0.02);
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .user-management {
    .page-header,
    .action-bar,
    .table-container {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .user-management {
    .page-header {
      padding: 24px 16px;

      .header-content {
        .header-icon-wrapper {
          width: 40px;
          height: 40px;

          .header-icon {
            font-size: 20px;
          }
        }

        .header-text {
          .page-title {
            font-size: 20px;
          }

          .page-description {
            font-size: 13px;
          }
        }
      }
    }

    .action-bar {
      margin: 0 16px 20px 16px;
      padding: 16px;
      flex-direction: column;
      align-items: stretch;
      gap: 16px;

      .search-section {
        width: 100%;
        flex-direction: column;
        gap: 12px;

        :deep(.ant-input-search),
        :deep(.ant-select) {
          width: 100% !important;
          margin-left: 0 !important;
        }
      }

      .button-section {
        width: 100%;
        flex-direction: column;

        .action-btn-primary,
        .action-btn-danger,
        .action-btn-secondary {
          width: 100%;
        }
      }
    }

    .table-container {
      margin: 0 16px 20px 16px;
      border-radius: 12px;
    }
  }
}
</style>
