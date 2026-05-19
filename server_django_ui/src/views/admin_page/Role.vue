<template>
  <div class="role-management">
    <!-- 页面头部 - 苹果风格 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <DatabaseOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">角色管理</h1>
          <p class="page-description">管理系统角色与权限配置</p>
        </div>
      </div>
    </div>

    <!-- 操作栏 - 苹果风格 -->
    <div class="action-bar">
      <div class="button-section">
        <a-button type="primary" @click="handleAdd" class="action-btn-primary">
          <template #icon><PlusOutlined /></template>
          添加角色
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

    <!-- 角色表格 -->
    <div class="table-container">
      <a-table
        :columns="columns"
        :data-source="roleList"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        row-key="role_id"
        @change="handleTableChange"
      >
        <!-- 角色名称列 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role_name'">
            <div class="role-info">
              <a-tag :color="getRoleColor(record.role_code)" style="margin-right: 8px">
                {{ record.role_name }}
              </a-tag>
              <span class="role-code">{{ record.role_code }}</span>
            </div>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.key === 'status'">
            <a-tag :color="record.status === 1 ? 'green' : 'red'">
              {{ record.status === 1 ? '启用' : '禁用' }}
            </a-tag>
          </template>

          <!-- 创建时间列 -->
          <template v-else-if="column.key === 'created_at'">
            <span v-if="record.created_at">
              {{ formatDate(record.created_at) }}
            </span>
            <span v-else class="text-gray">-</span>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleViewDetail(record)">
                查看详情
              </a-button>
              <a-button type="link" size="small" @click="handleEdit(record)"> 编辑 </a-button>
              <a-button type="link" size="small" @click="handleAssignPermissions(record)">
                分配权限
              </a-button>
              <a-button type="link" size="small" danger @click="handleDelete(record)">
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 角色详情/编辑弹窗 -->
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
            <a-form-item label="角色名称" name="role_name">
              <a-input v-model:value="formData.role_name" placeholder="请输入角色名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="角色代码" name="role_code">
              <a-input
                v-model:value="formData.role_code"
                placeholder="请输入角色代码"
                :disabled="modalMode === 'edit'"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="24">
            <a-form-item label="角色描述" name="description">
              <a-textarea
                v-model:value="formData.description"
                placeholder="请输入角色描述"
                :rows="3"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="24">
            <a-form-item label="状态" name="status">
              <a-select v-model:value="formData.status" placeholder="请选择状态">
                <a-select-option :value="1">启用</a-select-option>
                <a-select-option :value="0">禁用</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 角色详情弹窗 -->
    <a-modal
      v-model:visible="detailModalVisible"
      title="角色详情"
      width="700px"
      :footer="detailError ? null : undefined"
      @cancel="handleDetailModalCancel"
    >
      <!-- 加载状态 -->
      <div v-if="detailLoading" class="loading-container">
        <a-spin size="large" />
        <p class="loading-text">正在获取角色详情...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="detailError" class="error-container">
        <a-result status="error" title="获取角色详情失败" :sub-title="detailError">
          <template #extra>
            <a-space>
              <a-button type="primary" @click="retryGetRoleDetail">
                <template #icon><ReloadOutlined /></template>
                重试
              </a-button>
              <a-button @click="detailModalVisible = false">关闭</a-button>
            </a-space>
          </template>
        </a-result>
      </div>

      <!-- 角色详情内容 -->
      <div v-else-if="roleDetail" class="role-detail-content">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="角色ID">
            <a-tag color="blue">{{ roleDetail.role_id }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="角色名称">
            <a-tag :color="getRoleColor(roleDetail.role_code)">
              {{ roleDetail.role_name }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="角色代码">
            <a-tag color="geekblue">{{ roleDetail.role_code }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="roleDetail.status === 1 ? 'green' : 'red'">
              {{ roleDetail.status === 1 ? '启用' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="角色描述" :span="2">
            <div class="description-content">
              {{ roleDetail.description || '暂无描述' }}
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            <div class="time-info">
              <ClockCircleOutlined style="margin-right: 4px; color: #666" />
              {{ formatDate(roleDetail.created_at) }}
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="更新时间">
            <div class="time-info">
              <ClockCircleOutlined style="margin-right: 4px; color: #666" />
              {{ formatDate(roleDetail.updated_at) }}
            </div>
          </a-descriptions-item>
        </a-descriptions>

        <!-- 操作按钮 -->
        <div class="detail-actions">
          <a-space>
            <a-button type="primary" @click="handleEditFromDetail">
              <template #icon><EditOutlined /></template>
              编辑角色
            </a-button>
            <a-button @click="handleRefreshDetail">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
            <a-button danger @click="handleDeleteFromDetail">
              <template #icon><DeleteOutlined /></template>
              删除角色
            </a-button>
          </a-space>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-container">
        <a-empty description="暂无角色详情数据" />
      </div>
    </a-modal>

    <!-- 权限分配弹窗 -->
    <a-modal
      v-model:visible="permissionModalVisible"
      title="分配角色权限"
      width="800px"
      @ok="handlePermissionModalOk"
      @cancel="handlePermissionModalCancel"
    >
      <div v-if="permissionLoading" class="loading-container">
        <a-spin size="large" />
        <p class="loading-text">正在加载权限数据...</p>
      </div>

      <div v-else-if="permissionError" class="error-container">
        <a-result status="error" title="加载权限数据失败" :sub-title="permissionError">
          <template #extra>
            <a-space>
              <a-button type="primary" @click="retryLoadPermissions">
                <template #icon><ReloadOutlined /></template>
                重试
              </a-button>
              <a-button @click="permissionModalVisible = false">关闭</a-button>
            </a-space>
          </template>
        </a-result>
      </div>

      <div v-else class="permission-assignment-content">
        <div class="role-info-section">
          <a-descriptions :column="2" size="small" bordered>
            <a-descriptions-item label="角色名称">
              <a-tag :color="getRoleColor(currentPermissionRole?.role_code || '')">
                {{ currentPermissionRole?.role_name }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="角色代码">
              <a-tag color="geekblue">{{ currentPermissionRole?.role_code }}</a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </div>

        <a-divider>菜单权限配置</a-divider>

        <div class="permission-config">
          <div class="config-section">
            <!-- 用户类型选择 -->
            <!-- <div class="config-item">
              <div class="option-label">用户类型：</div>
              <a-radio-group v-model:value="selectedUserType" @change="handleUserTypeChange">
                <a-radio-button value="admin">管理员</a-radio-button>
                <a-radio-button value="user">普通用户</a-radio-button>
              </a-radio-group>
            </div> -->

            <!-- 菜单选择 - 修改为菜单选择 -->
            <div class="config-item">
              <div class="option-label">菜单权限：</div>
              <a-select
                v-model:value="selectedMenuIds"
                style="width: 100%"
                :placeholder="
                  selectedMenuIds.length > 0
                    ? `已选择 ${selectedMenuIds.length} 个菜单权限`
                    : '请选择菜单权限'
                "
                :loading="menuLoading"
                @change="handleMenuChange"
                :disabled="!flatMenuList.length"
                mode="multiple"
                :max-tag-count="0"
                :show-search="false"
                :show-arrow="true"
                :allow-clear="false"
              >
                <a-select-option
                  v-for="menu in flatMenuList"
                  :key="menu.menu_id"
                  :value="menu.menu_id"
                >
                  {{ menu.display_name }}
                </a-select-option>
              </a-select>
            </div>
          </div>

          <div class="permission-description">
            <a-alert type="info" show-icon>
              <template #message>菜单权限配置说明</template>
              <template #description>
                <p>请选择角色可以访问的菜单权限，可以选择多个菜单进行权限分配。</p>
              </template>
            </a-alert>
          </div>

          <!-- 临时调试信息 -->
          <!-- <div style="margin-top: 10px; padding: 10px; background: #f5f5f5; font-size: 12px;">
            <div><strong>调试信息：</strong></div>
            <div>selectedMenuIds: {{ JSON.stringify(selectedMenuIds) }}</div>
            <div>flatMenuList长度: {{ flatMenuList.length }}</div>
            <div>前3个菜单: {{ JSON.stringify(flatMenuList.slice(0, 3).map(m => ({ id: m.menu_id, name: m.menu_name }))) }}</div>
          </div> -->
        </div>

        <!-- <div class="permission-tree-section">
          <div class="permission-tree-header">
            <a-space>
              <a-button size="small" @click="expandAllPermissions">
                <template #icon><PlusOutlined /></template>
                展开全部
              </a-button>
              <a-button size="small" @click="collapseAllPermissions">
                <template #icon><MinusOutlined /></template>
                收起全部
              </a-button>
              <a-button size="small" @click="selectAllPermissions">
                <template #icon><CheckOutlined /></template>
                全选
              </a-button>
              <a-button size="small" @click="clearAllPermissions">
                <template #icon><CloseOutlined /></template>
                清空
              </a-button>
            </a-space>
          </div>
          
          <div class="permission-tree-container">
            <a-tree
              v-model:checkedKeys="selectedPermissionIds"
              v-model:expandedKeys="expandedPermissionKeys"
              :tree-data="permissionTreeData"
              :checkable="true"
              :check-strictly="false"
              :selectable="false"
              :height="400"
              :virtual="false"
            >
              <template #title="{ title, permission_type, description }">
                <div class="permission-node">
                  <span class="permission-title">{{ title }}</span>
                  <a-tag 
                    :color="getPermissionTypeColor(permission_type)" 
                    size="small"
                    style="margin-left: 8px"
                  >
                    {{ getPermissionTypeText(permission_type) }}
                  </a-tag>
                  <span v-if="description" class="permission-description">
                    {{ description }}
                  </span>
                </div>
              </template>
            </a-tree>
          </div>
        </div> -->

        <!-- <div class="permission-summary">
          <a-alert
            :message="`已选择 ${permissionStats.selected} / ${permissionStats.total} 个权限`"
            type="info"
            show-icon
          >
            <template #description>
              <div class="permission-stats">
                <a-space wrap>
                  <a-tag v-if="permissionStats.byType.menu" color="blue">
                    菜单权限: {{ permissionStats.byType.menu }}
                  </a-tag>
                  <a-tag v-if="permissionStats.byType.button" color="green">
                    按钮权限: {{ permissionStats.byType.button }}
                  </a-tag>
                  <a-tag v-if="permissionStats.byType.api" color="orange">
                    接口权限: {{ permissionStats.byType.api }}
                  </a-tag>
                </a-space>
              </div>
            </template>
          </a-alert>
        </div> -->
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  PlusOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EditOutlined,
  ClockCircleOutlined,
  MinusOutlined,
  CheckOutlined,
  CloseOutlined,
  DatabaseOutlined,
} from '@ant-design/icons-vue';
import {
  roleApi,
  type Role,
  type RoleListResponse,
  type CreateRoleParams,
  type UpdateRoleParams,
  type Permission,
  type AssignRolePermissionsParams,
} from '@/api/role';
import type { TableColumnsType, TableProps } from 'ant-design-vue';

// 响应式数据
const loading = ref(false);
const roleList = ref<Role[]>([]);
const selectedRowKeys = ref<number[]>([]);
const searchKeyword = ref('');
const statusFilter = ref<number | ''>('');

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number, range: [number, number]) =>
    `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
});

// 弹窗相关
const modalVisible = ref(false);
const modalMode = ref<'add' | 'edit'>('add');
const currentRole = ref<Role | null>(null);
const formRef = ref();

// 角色详情弹窗相关
const detailModalVisible = ref(false);
const roleDetail = ref<Role | null>(null);
const detailLoading = ref(false);
const detailError = ref('');
const currentDetailRole = ref<Role | null>(null);

// 权限分配弹窗相关
const permissionModalVisible = ref(false);
const currentPermissionRole = ref<Role | null>(null);
const permissionLoading = ref(false);
const permissionError = ref('');
const permissionTreeData = ref<any[]>([]);
const selectedPermissionIds = ref<number[]>([]);
const expandedPermissionKeys = ref<number[]>([]);
const allPermissions = ref<Permission[]>([]);
// 用户类型选择
const selectedUserType = ref<'user' | 'admin'>('user');
// 菜单树相关 - 修改为菜单树
const menuTree = ref<any[]>([]);
const menuLoading = ref(false);
const selectedMenuIds = ref<number[]>([]);
const flatMenuList = ref<any[]>([]); // 扁平化的菜单列表，用于选择器显示
const departmentTree = ref<Department[]>([]);
const departmentLoading = ref(false);
const selectedDepartmentIds = ref<number[]>([]);

// 表单数据
const formData = reactive({
  role_name: '',
  role_code: '',
  description: '',
  status: 1,
});

// 表单验证规则
const formRules = computed(() => ({
  role_name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度为2-50个字符', trigger: 'blur' },
  ],
  role_code: [
    { required: true, message: '请输入角色代码', trigger: 'blur' },
    { min: 2, max: 50, message: '角色代码长度为2-50个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '角色代码只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  description: [{ max: 200, message: '描述长度不能超过200个字符', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}));

// 计算属性
const modalTitle = computed(() => (modalMode.value === 'add' ? '添加角色' : '编辑角色'));

// 权限选择统计
const permissionStats = computed(() => {
  const total = allPermissions.value.length;
  const selected = selectedPermissionIds.value.length;
  const byType = allPermissions.value.reduce(
    (acc, permission) => {
      if (selectedPermissionIds.value.includes(permission.permission_id)) {
        acc[permission.permission_type] = (acc[permission.permission_type] || 0) + 1;
      }
      return acc;
    },
    {} as Record<string, number>
  );

  return {
    total,
    selected,
    byType,
  };
});

// 表格列配置
const columns: TableColumnsType = [
  {
    title: '角色信息',
    key: 'role_name',
    width: 200,
    fixed: 'left',
  },
  {
    title: '角色描述',
    dataIndex: 'description',
    key: 'description',
    width: 250,
    customRender: ({ text }) => text || '-',
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
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
  selectedRowKeys: selectedRowKeys,
  onChange: (keys: number[]) => {
    selectedRowKeys.value = keys;
  },
};

// 方法
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('zh-CN');
};

const getRoleColor = (roleCode: string) => {
  switch (roleCode) {
    case 'super_admin':
      return 'purple';
    case 'admin':
      return 'blue';
    case 'user':
      return 'default';
    default:
      return 'cyan';
  }
};

// 获取权限类型颜色
const getPermissionTypeColor = (type: string) => {
  switch (type) {
    case 'menu':
      return 'blue';
    case 'button':
      return 'green';
    case 'api':
      return 'orange';
    default:
      return 'default';
  }
};

// 获取权限类型文本
const getPermissionTypeText = (type: string) => {
  switch (type) {
    case 'menu':
      return '菜单';
    case 'button':
      return '按钮';
    case 'api':
      return '接口';
    default:
      return '未知';
  }
};

// 扁平化菜单树数据的递归函数
const flattenMenuTree = (menuItems: any[], level: number = 0): any[] => {
  const result: any[] = [];

  menuItems.forEach((menu) => {
    // 添加当前菜单项，带有层级缩进
    const indent = '　'.repeat(level); // 使用全角空格进行缩进
    result.push({
      ...menu,
      menu_id: Number(menu.menu_id), // 确保menu_id是数字类型
      display_name: `${indent}${menu.menu_name}`,
      level: level,
    });

    // 递归处理子菜单
    if (menu.children && menu.children.length > 0) {
      result.push(...flattenMenuTree(menu.children, level + 1));
    }
  });

  return result;
};

// 构建权限树数据
const buildPermissionTree = (permissions: Permission[]): any[] => {
  const tree: any[] = [];
  const map = new Map<number, any>();

  // 创建节点映射
  permissions.forEach((permission) => {
    const node = {
      key: permission.permission_id,
      title: permission.permission_name,
      permission_type: permission.permission_type,
      description: permission.description,
      children: [],
    };
    map.set(permission.permission_id, node);
  });

  // 构建树结构
  permissions.forEach((permission) => {
    const node = map.get(permission.permission_id);
    if (permission.parent_id && map.has(permission.parent_id)) {
      const parent = map.get(permission.parent_id);
      parent.children.push(node);
    } else {
      tree.push(node);
    }
  });

  return tree;
};

// 获取角色列表
const fetchRoleList = async () => {
  try {
    loading.value = true;
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchKeyword.value || undefined,
      status: statusFilter.value || undefined,
    };

    const response = await roleApi.getRoleList(params);
    if (response.success) {
      roleList.value = response.data.list;
      pagination.total = response.data.total;
    } else {
      message.error(response.message || '获取角色列表失败');
    }
  } catch (error) {
    console.error('获取角色列表失败:', error);
    message.error('获取角色列表失败');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.current = 1;
  fetchRoleList();
};

const handleRefresh = () => {
  searchKeyword.value = '';
  statusFilter.value = '';
  pagination.current = 1;
  fetchRoleList();
};

const handleTableChange = (pag: any) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchRoleList();
};

// 添加角色
const handleAdd = () => {
  modalMode.value = 'add';
  currentRole.value = null;
  resetFormData();
  modalVisible.value = true;
};

// 编辑角色
const handleEdit = (role: Role) => {
  modalMode.value = 'edit';
  currentRole.value = role;
  formData.role_name = role.role_name;
  formData.role_code = role.role_code;
  formData.description = role.description || '';
  formData.status = role.status || 1;
  modalVisible.value = true;
};

// 查看角色详情
const handleViewDetail = async (role: Role) => {
  currentDetailRole.value = role;
  detailModalVisible.value = true;
  await fetchRoleDetail(role.role_id);
};

// 获取角色详情
const fetchRoleDetail = async (roleId: number) => {
  try {
    detailLoading.value = true;
    detailError.value = '';
    roleDetail.value = null;

    const response = await roleApi.getRole(roleId);
    if (response.success) {
      roleDetail.value = response.data;
    } else {
      detailError.value = response.message || '获取角色详情失败';
      console.error('获取角色详情失败:', response);
    }
  } catch (error: any) {
    console.error('获取角色详情失败:', error);
    detailError.value = error.message || '网络请求失败，请检查网络连接';
  } finally {
    detailLoading.value = false;
  }
};

// 重试获取角色详情
const retryGetRoleDetail = () => {
  if (currentDetailRole.value) {
    fetchRoleDetail(currentDetailRole.value.role_id);
  }
};

// 从详情页面编辑角色
const handleEditFromDetail = () => {
  if (roleDetail.value) {
    detailModalVisible.value = false;
    handleEdit(roleDetail.value);
  }
};

// 从详情页面删除角色
const handleDeleteFromDetail = () => {
  if (roleDetail.value) {
    detailModalVisible.value = false;
    handleDelete(roleDetail.value);
  }
};

// 刷新角色详情
const handleRefreshDetail = () => {
  if (currentDetailRole.value) {
    fetchRoleDetail(currentDetailRole.value.role_id);
  }
};

// 关闭详情弹窗
const handleDetailModalCancel = () => {
  detailModalVisible.value = false;
  roleDetail.value = null;
  detailError.value = '';
  detailLoading.value = false;
  currentDetailRole.value = null;
};

// 分配权限
const handleAssignPermissions = async (role: Role) => {
  currentPermissionRole.value = role;
  permissionModalVisible.value = true;

  // 先获取菜单树数据，再获取权限数据，确保菜单数据加载完成后再设置默认选中
  await fetchMenuTree(); // 获取菜单树数据
  fetchPermissionData(role.role_id);
};

// 获取权限数据
const fetchPermissionData = async (roleId: number) => {
  permissionLoading.value = true;
  permissionError.value = '';

  try {
    // 并行获取所有权限和角色当前权限
    const [allPermissionsRes, rolePermissionsRes] = await Promise.all([
      roleApi.getPermissionList(),
      roleApi.getRolePermissions(roleId),
    ]);

    if (allPermissionsRes.success && rolePermissionsRes.success) {
      allPermissions.value = allPermissionsRes.data.list || allPermissionsRes.data;
      permissionTreeData.value = buildPermissionTree(allPermissions.value);

      // 获取角色当前的菜单权限数据
      const currentMenus = rolePermissionsRes.data.list || rolePermissionsRes.data;
      console.log('角色当前菜单权限数据:', currentMenus);

      // currentMenus 是一个数字数组，直接包含 menu_id
      if (Array.isArray(currentMenus)) {
        // 从菜单数据中提取menu_id用于权限选择器
        selectedPermissionIds.value = currentMenus
          .map((menuId: any) => Number(menuId))
          .filter((id) => !isNaN(id));

        // 将角色已有的菜单权限设置为默认勾选状态（用于菜单选择器）
        selectedMenuIds.value = currentMenus
          .map((menuId: any) => Number(menuId))
          .filter((id) => !isNaN(id));
      } else {
        // 如果是对象数组格式，使用原来的逻辑
        selectedPermissionIds.value = currentMenus
          .map((menu: any) => Number(menu.menu_id))
          .filter((id) => !isNaN(id));
        selectedMenuIds.value = currentMenus
          .map((menu: any) => Number(menu.menu_id))
          .filter((id) => !isNaN(id));
      }

      console.log('设置的selectedMenuIds:', selectedMenuIds.value);
      console.log('currentMenus原始数据:', currentMenus);

      // 默认展开所有节点
      expandedPermissionKeys.value = allPermissions.value
        .filter((p) => p.parent_id === null || p.parent_id === 0)
        .map((p) => p.permission_id);
    } else {
      throw new Error(
        allPermissionsRes.message || rolePermissionsRes.message || '获取权限数据失败'
      );
    }
  } catch (error) {
    console.error('获取权限数据失败:', error);
    permissionError.value = '获取权限数据失败，请重试';
  } finally {
    permissionLoading.value = false;
  }
};

// 重试加载权限
const retryLoadPermissions = async () => {
  if (currentPermissionRole.value) {
    // 先获取菜单树数据，再获取权限数据
    await fetchMenuTree();
    fetchPermissionData(currentPermissionRole.value.role_id);
  }
};

// 获取菜单树数据 - 修改为使用菜单树API
const fetchMenuTree = async () => {
  try {
    menuLoading.value = true;
    const response = await roleApi.getPermissionTree();
    if (response.success) {
      menuTree.value = response.data;
      // 扁平化菜单树数据，用于选择器显示
      flatMenuList.value = flattenMenuTree(response.data);
      console.log('菜单树数据:', response.data);
      console.log('扁平化菜单列表:', flatMenuList.value);
    } else {
      message.error(response.message || '获取菜单数据失败');
    }
  } catch (error) {
    console.error('获取菜单数据失败:', error);
    message.error('获取菜单数据失败');
  } finally {
    menuLoading.value = false;
  }
};

// 菜单选择变更处理 - 修改为菜单选择
const handleMenuChange = (value: number[]) => {
  console.log('选择的菜单ID:', value);
  console.log(
    '当前flatMenuList:',
    flatMenuList.value.map((m) => ({ id: m.menu_id, name: m.display_name }))
  );
  selectedMenuIds.value = value;
};

// 用户类型变更处理
const handleUserTypeChange = (e: any) => {
  const userType = e.target.value;
  console.log('用户类型变更为:', userType);
  // 可以在这里根据用户类型预设不同的权限
  if (userType === 'admin') {
    // 管理员可能需要更多权限，可以在这里预设
    message.info('已切换到管理员权限模式');
  } else {
    // 普通用户可能需要较少权限
    message.info('已切换到普通用户权限模式');
  }
};

// 权限分配弹窗确认
const handlePermissionModalOk = async () => {
  if (!currentPermissionRole.value) return;

  try {
    // 根据用户类型构建请求数据
    const userTypeValue = selectedUserType.value === 'admin' ? 1 : 0;

    // 构建权限分配请求数据，使用菜单ID而不是部门ID
    const params = {
      role_id: currentPermissionRole.value.role_id,
      menu_ids: selectedMenuIds.value, // 修改为使用菜单ID
      user_type: userTypeValue,
    };

    console.log('提交的权限数据:', params);

    const response = await roleApi.assignRolePermissions(params);
    if (response.success) {
      message.success('权限分配成功');
      handlePermissionModalCancel();
      await fetchRoleList(); // 刷新角色列表
    } else {
      throw new Error(response.message || '权限分配失败');
    }
  } catch (error) {
    console.error('权限分配失败:', error);
    message.error('权限分配失败，请重试');
  }
};

// 权限分配弹窗取消
const handlePermissionModalCancel = () => {
  permissionModalVisible.value = false;
  currentPermissionRole.value = null;
  selectedPermissionIds.value = [];
  expandedPermissionKeys.value = [];
  permissionError.value = '';
  allPermissions.value = [];
  permissionTreeData.value = [];
  selectedMenuIds.value = []; // 重置菜单选择
};

// 展开所有权限节点
const expandAllPermissions = () => {
  expandedPermissionKeys.value = allPermissions.value.map((p) => p.permission_id);
};

// 收起所有权限节点
const collapseAllPermissions = () => {
  expandedPermissionKeys.value = [];
};

// 全选权限
const selectAllPermissions = () => {
  selectedPermissionIds.value = allPermissions.value.map((p) => p.permission_id);
};

// 清空权限选择
const clearAllPermissions = () => {
  selectedPermissionIds.value = [];
};

// 删除角色
const handleDelete = (role: Role) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除角色 "${role.role_name}" 吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        const response = await roleApi.deleteRole(role.role_id);
        if (response.success) {
          message.success('删除成功');
          await fetchRoleList();
        } else {
          message.error(response.message || '删除失败');
        }
      } catch (error) {
        console.error('删除角色失败:', error);
        message.error('删除失败');
      }
    },
  });
};

// 批量删除
const handleBatchDelete = () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要删除的角色');
    return;
  }

  Modal.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个角色吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        const response = await roleApi.batchDeleteRoles(selectedRowKeys.value);
        if (response.success) {
          message.success('批量删除成功');
          selectedRowKeys.value = [];
          await fetchRoleList();
        } else {
          message.error(response.message || '批量删除失败');
        }
      } catch (error) {
        console.error('批量删除失败:', error);
        message.error('批量删除失败');
      }
    },
  });
};

// 弹窗确认
const handleModalOk = async () => {
  try {
    await formRef.value.validate();

    if (modalMode.value === 'add') {
      const params: CreateRoleParams = {
        role_name: formData.role_name,
        role_code: formData.role_code,
        description: formData.description,
        status: formData.status,
      };

      const response = await roleApi.createRole(params);
      if (response.success) {
        message.success('添加成功');
        modalVisible.value = false;
        await fetchRoleList();
      } else {
        message.error(response.message || '添加失败');
      }
    } else {
      if (!currentRole.value) {
        message.error('角色信息不存在');
        return;
      }

      const params: UpdateRoleParams = {
        role_name: formData.role_name,
        description: formData.description,
        status: formData.status,
      };

      const response = await roleApi.updateRole(currentRole.value.role_id, params);
      if (response.success) {
        message.success('更新成功');
        modalVisible.value = false;
        await fetchRoleList();
      } else {
        message.error(response.message || '更新失败');
      }
    }
  } catch (error) {
    console.error('表单验证失败:', error);
  }
};

// 弹窗取消
const handleModalCancel = () => {
  modalVisible.value = false;
  resetFormData();
};

// 重置表单数据
const resetFormData = () => {
  formData.role_name = '';
  formData.role_code = '';
  formData.description = '';
  formData.status = 1;
  formRef.value?.resetFields();
};

// 组件挂载时获取数据
onMounted(() => {
  fetchRoleList();
});
</script>

<style scoped lang="scss">
.role-management {
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
        background: rgba(139, 92, 246, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(139, 92, 246, 0.15);
        }

        .header-icon {
          font-size: 24px;
          color: #8b5cf6;
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
    justify-content: flex-end;
    align-items: center;
    gap: 16px;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
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

    .role-info {
      display: flex;
      align-items: center;

      :deep(.ant-tag) {
        border-radius: 6px;
        font-weight: 500;
        padding: 2px 8px;
      }
    }

    .role-code {
      color: #86868b;
      font-size: 12px;
      margin-left: 8px;
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

  .loading-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 200px;
    gap: 16px;
  }

  .loading-text {
    margin: 0;
    color: #86868b;
    font-size: 14px;
  }

  .error-container {
    padding: 20px 0;
  }

  .empty-container {
    padding: 40px 0;
    text-align: center;
  }

  .role-detail-content {
    padding: 16px 0;

    :deep(.ant-descriptions) {
      .ant-descriptions-item-label {
        font-weight: 500;
        color: #1d1d1f;
      }

      .ant-descriptions-item-content {
        color: #86868b;
      }
    }
  }

  .description-content {
    line-height: 1.6;
    color: #1d1d1f;
    word-break: break-word;
  }

  .time-info {
    display: flex;
    align-items: center;
    color: #86868b;
    font-size: 13px;
  }

  .detail-actions {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 0.5px solid rgba(0, 0, 0, 0.08);
    text-align: center;
  }

  /* 权限分配相关样式 */
  .permission-assignment-content {
    padding: 16px 0;
  }

  .role-info-section {
    margin-bottom: 20px;

    :deep(.ant-descriptions) {
      .ant-descriptions-item-label {
        font-weight: 500;
        color: #1d1d1f;
      }

      .ant-descriptions-item-content {
        color: #86868b;
      }
    }
  }

  .permission-tree-section {
    margin-bottom: 20px;
  }

  .permission-tree-header {
    margin-bottom: 12px;
    padding: 12px;
    background: rgba(0, 0, 0, 0.02);
    border-radius: 8px;
  }

  .permission-tree-container {
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.5);
  }

  .permission-node {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
  }

  .permission-title {
    font-weight: 500;
    color: #1d1d1f;
  }

  .permission-description {
    color: #86868b;
    font-size: 12px;
    margin-left: 8px;
  }

  .permission-summary {
    margin-top: 16px;
  }

  /* 用户类型选择样式 */
  .user-type-selection {
    margin-bottom: 16px;
    text-align: center;
  }

  .user-type-selection .ant-radio-group {
    margin-bottom: 12px;
  }

  .user-type-selection .ant-radio-button-wrapper {
    min-width: 120px;
    text-align: center;
  }

  /* 权限配置样式 */
  .permission-config {
    margin-bottom: 20px;

    .config-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-bottom: 16px;
    }

    .config-item {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .option-label {
        font-weight: 500;
        margin-bottom: 4px;
        color: #1d1d1f;
      }
    }

    .permission-description {
      margin-top: 16px;
    }
  }

  // 弹窗样式已由全局样式统一处理，此处仅保留页面特定样式
}

// 响应式设计
@media (max-width: 1200px) {
  .role-management {
    .page-header,
    .action-bar,
    .table-container {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .role-management {
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
