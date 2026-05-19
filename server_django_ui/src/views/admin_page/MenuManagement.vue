<template>
  <div class="menu-management">
    <!-- 页面头部 - 苹果风格 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <MenuOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">菜单管理</h1>
          <p class="page-description">管理系统菜单权限和导航结构</p>
        </div>
      </div>
    </div>

    <!-- 操作栏 - 苹果风格 -->
    <div class="action-bar">
      <div class="search-section">
        <a-input
          v-model:value="searchText"
          placeholder="搜索菜单名称或编码"
          style="width: 300px"
          @pressEnter="handleSearchImmediate"
          @input="handleSearch"
          allow-clear
        />
        <a-button
          type="primary"
          class="search-btn"
          style="margin-left: 12px"
          :loading="loading"
          @click="handleSearchImmediate"
        >
          查询
        </a-button>
      </div>
      <div class="button-section">
        <a-button type="primary" @click="handleAdd" class="action-btn-primary">
          <template #icon><PlusOutlined /></template>
          添加菜单
        </a-button>
        <a-button @click="refreshData" class="action-btn-secondary">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </div>
    </div>

    <!-- 菜单树形表格 -->
    <div class="table-container">
      <a-table
        :columns="columns"
        :data-source="filteredMenuData"
        :loading="loading"
        :pagination="false"
        row-key="menu_id"
        size="middle"
        childrenColumnName="children"
        :default-expand-all-rows="false"
        :expanded-row-keys="expandedRowKeys"
        @expand="onExpand"
        :locale="tableLocale"
      >
        <!-- 菜单名称列 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'menu_name'">
            <div class="menu-name-container">
              <span class="menu-name">{{ record.menu_name }}</span>
              <span v-if="hasChildren(record)" class="children-count">
                ({{ getChildrenCount(record) }})
              </span>
            </div>
          </template>

          <!-- 菜单类型列 -->
          <template v-else-if="column.key === 'menu_type'">
            <a-tag :color="getMenuTypeColor(record.menu_type)">
              {{ getMenuTypeText(record.menu_type) }}
            </a-tag>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusValue(record.status) === 1 ? 'success' : 'error'">
              {{ getStatusValue(record.status) === 1 ? '启用' : '禁用' }}
            </a-tag>
          </template>

          <!-- 图标列 -->
          <template v-else-if="column.key === 'icon'">
            <component
              v-if="record.icon"
              :is="getIconComponent(record.icon)"
              style="font-size: 16px; color: #1890ff"
            />
            <span v-else class="text-gray">-</span>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleView(record)"> 查看 </a-button>
              <a-button type="link" size="small" @click="handleEdit(record)"> 编辑 </a-button>
              <a-button type="link" size="small" danger @click="handleDelete(record)">
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 菜单详情弹窗 -->
    <a-modal v-model:visible="detailVisible" title="菜单详情" :footer="null" width="600px">
      <a-spin :spinning="detailLoading">
        <a-descriptions :column="2" bordered v-if="menuDetail">
          <a-descriptions-item label="菜单名称">
            {{ menuDetail.menu_name }}
          </a-descriptions-item>
          <a-descriptions-item label="菜单编码">
            {{ menuDetail.menu_code }}
          </a-descriptions-item>
          <a-descriptions-item label="菜单类型">
            <a-tag :color="getMenuTypeColor(menuDetail.menu_type)">
              {{ getMenuTypeText(menuDetail.menu_type) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusValue(menuDetail.status) === 1 ? 'success' : 'error'">
              {{ getStatusValue(menuDetail.status) === 1 ? '启用' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="路径">
            {{ menuDetail.path || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="图标">
            <component
              v-if="menuDetail.icon"
              :is="getIconComponent(menuDetail.icon)"
              style="font-size: 16px; color: #1890ff"
            />
            <span v-else>-</span>
          </a-descriptions-item>
          <a-descriptions-item label="排序">
            {{ menuDetail.sort_order || 0 }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ formatDate(menuDetail.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="描述" :span="2">
            {{ menuDetail.description || '-' }}
          </a-descriptions-item>
        </a-descriptions>
      </a-spin>
    </a-modal>

    <!-- 添加/编辑菜单弹窗 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalMode === 'add' ? '添加菜单' : '编辑菜单'"
      :confirm-loading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      width="600px"
    >
      <a-form ref="formRef" :model="formData" :rules="formRules" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="菜单名称" name="menu_name">
              <a-input v-model:value="formData.menu_name" placeholder="请输入菜单名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="菜单编码" name="menu_code">
              <a-input v-model:value="formData.menu_code" placeholder="请输入菜单编码" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="菜单类型" name="menu_type">
              <a-select v-model:value="formData.menu_type" placeholder="请选择菜单类型">
                <a-select-option :value="1">菜单</a-select-option>
                <a-select-option :value="2">按钮</a-select-option>
                <a-select-option :value="3">接口</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态" name="status">
              <a-select v-model:value="formData.status" placeholder="请选择状态">
                <a-select-option :value="1">启用</a-select-option>
                <a-select-option :value="0">禁用</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="路径" name="path">
              <a-input v-model:value="formData.path" placeholder="请输入路径" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="组件" name="component">
              <a-input v-model:value="formData.component" placeholder="请输入组件路径" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="图标" name="icon">
              <a-input v-model:value="formData.icon" placeholder="请输入图标名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="权限标识" name="permission">
              <a-input v-model:value="formData.permission" placeholder="请输入权限标识" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="排序" name="sort_order">
              <a-input-number
                v-model:value="formData.sort_order"
                placeholder="请输入排序值"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="父级菜单" name="parent_id">
              <a-tree-select
                v-model:value="formData.parent_id"
                :tree-data="parentMenuOptions"
                placeholder="请选择父级菜单"
                allow-clear
                tree-default-expand-all
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="外部链接" name="is_external">
              <a-switch v-model:checked="formData.is_external" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="是否缓存" name="is_cache">
              <a-switch v-model:checked="formData.is_cache" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="是否可见" name="is_visible">
              <a-switch v-model:checked="formData.is_visible" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message, Modal } from 'ant-design-vue';
import type { FormInstance } from 'ant-design-vue';
import {
  PlusOutlined,
  ReloadOutlined,
  MenuOutlined,
  ApiOutlined,
  ControlOutlined,
  DashboardOutlined,
  UserOutlined,
  SettingOutlined,
  FileTextOutlined,
  TeamOutlined,
} from '@ant-design/icons-vue';
import { menuApi, type Menu, type CreateMenuParams } from '@/api';

// 响应式数据
const loading = ref(false);
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalMode = ref<'add' | 'edit'>('add');
const formRef = ref<FormInstance>();
const searchText = ref('');

// 菜单详情相关
const detailVisible = ref(false);
const detailLoading = ref(false);
const menuDetail = ref<Menu | null>(null);

// 菜单数据
const menuList = ref<Menu[]>([]);
const menuTree = ref<Menu[]>([]);
const expandedRowKeys = ref<number[]>([]);

// 表单数据
const formData = reactive<CreateMenuParams>({
  menu_name: '',
  menu_code: '',
  menu_type: 1, // 1=菜单, 2=按钮, 3=接口
  parent_id: 0,
  path: '',
  component: '',
  icon: '',
  permission: '',
  sort_order: 0,
  status: 0, // 0=禁用, 1=启用
  is_external: false,
  is_cache: true,
  is_visible: true,
});

// 当前编辑的菜单ID
const currentEditId = ref<number | null>(null);

// 表单验证规则
const formRules = {
  menu_name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
    { min: 2, max: 50, message: '菜单名称长度应在2-50个字符之间', trigger: 'blur' },
  ],
  menu_code: [
    { required: true, message: '请输入菜单编码', trigger: 'blur' },
    { min: 2, max: 50, message: '菜单编码长度应在2-50个字符之间', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_-]+$/,
      message: '菜单编码只能包含字母、数字、下划线和中划线',
      trigger: 'blur',
    },
  ],
  menu_type: [{ required: true, message: '请选择菜单类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  path: [{ max: 200, message: '路径长度不能超过200个字符', trigger: 'blur' }],
  component: [{ max: 200, message: '组件路径长度不能超过200个字符', trigger: 'blur' }],
  icon: [{ max: 50, message: '图标名称长度不能超过50个字符', trigger: 'blur' }],
  permission: [{ max: 100, message: '权限标识长度不能超过100个字符', trigger: 'blur' }],
  sort_order: [
    { type: 'number', min: 0, max: 9999, message: '排序值应在0-9999之间', trigger: 'blur' },
  ],
};

// 表格列定义
const columns = [
  {
    title: '菜单名称',
    dataIndex: 'menu_name',
    key: 'menu_name',
  },
  {
    title: '菜单编码',
    dataIndex: 'menu_code',
    key: 'menu_code',
  },
  {
    title: '菜单类型',
    dataIndex: 'menu_type',
    key: 'menu_type',
  },
  {
    title: '路径',
    dataIndex: 'path',
    key: 'path',
  },
  {
    title: '图标',
    dataIndex: 'icon',
    key: 'icon',
    align: 'center',
  },
  {
    title: '排序',
    dataIndex: 'sort_order',
    key: 'sort_order',
    align: 'center',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    align: 'center',
  },
  {
    title: '操作',
    key: 'action',
  },
];

// 计算属性
const filteredMenuData = computed(() => {
  if (!searchText.value) {
    return menuTree.value;
  }

  const filterMenu = (menus: Menu[]): Menu[] => {
    return menus.filter((menu) => {
      const matchesSearch =
        menu.menu_name.toLowerCase().includes(searchText.value.toLowerCase()) ||
        menu.menu_code.toLowerCase().includes(searchText.value.toLowerCase());

      if (matchesSearch) {
        return true;
      }

      if (menu.children && menu.children.length > 0) {
        const filteredChildren = filterMenu(menu.children);
        if (filteredChildren.length > 0) {
          menu.children = filteredChildren;
          return true;
        }
      }

      return false;
    });
  };

  return filterMenu([...menuTree.value]);
});

const parentMenuOptions = computed(() => {
  const buildOptions = (menus: Menu[], level = 0): any[] => {
    return menus.map((menu) => ({
      title: menu.menu_name,
      value: menu.menu_id,
      key: menu.menu_id,
      children:
        menu.children && menu.children.length > 0
          ? buildOptions(menu.children, level + 1)
          : undefined,
    }));
  };

  return buildOptions(menuTree.value);
});

const tableLocale = computed(() => ({
  emptyText: searchText.value ? '未找到匹配的菜单数据' : '暂无菜单数据，点击"添加菜单"开始创建',
}));

// 工具函数
const hasChildren = (menu: Menu): boolean => {
  return menu.children && menu.children.length > 0;
};

const getChildrenCount = (menu: Menu): number => {
  return menu.children ? menu.children.length : 0;
};

const getMenuTypeText = (type: number): string => {
  switch (type) {
    case 1:
      return '菜单';
    case 2:
      return '按钮';
    case 3:
      return '接口';
    default:
      return '未知';
  }
};

const getStatusText = (status: number): string => {
  return status === 1 ? '启用' : '禁用';
};

// 获取状态值，处理可能的类型问题
const getStatusValue = (status: number | string | undefined | null): number => {
  if (status === undefined || status === null) {
    return 0; // 默认为禁用
  }
  // 如果是字符串，转换为数字
  if (typeof status === 'string') {
    const num = parseInt(status, 10);
    return isNaN(num) ? 0 : num;
  }
  // 如果是数字，直接返回
  return Number(status);
};

const getMenuTypeColor = (type: number): string => {
  switch (type) {
    case 1:
      return 'blue';
    case 2:
      return 'green';
    case 3:
      return 'orange';
    default:
      return 'default';
  }
};

const getIconComponent = (iconName: string) => {
  const iconMap: Record<string, any> = {
    menu: MenuOutlined,
    api: ApiOutlined,
    control: ControlOutlined,
    dashboard: DashboardOutlined,
    user: UserOutlined,
    setting: SettingOutlined,
    file: FileTextOutlined,
    team: TeamOutlined,
  };
  return iconMap[iconName] || MenuOutlined;
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString('zh-CN');
};

// 数据获取
const fetchMenuList = async () => {
  try {
    loading.value = true;

    // 使用菜单树接口获取数据
    const response = await menuApi.getMenuTree();

    if (response.success && response.data) {
      // 后端返回的已经是树形结构，直接使用
      menuTree.value = response.data;

      // 收集所有菜单项用于统计
      const collectAllMenus = (menus: Menu[]): Menu[] => {
        let result: Menu[] = [];
        menus.forEach((menu) => {
          result.push(menu);
          if (menu.children && menu.children.length > 0) {
            result.push(...collectAllMenus(menu.children));
          }
        });
        return result;
      };

      menuList.value = collectAllMenus(menuTree.value);

      // 默认展开所有根节点
      expandedRowKeys.value = menuTree.value.map((menu) => menu.menu_id);

      // 调试：检查状态值
      if (menuList.value.length > 0) {
        console.log(
          '🔍 菜单状态值检查（前10条）:',
          menuList.value.slice(0, 10).map((m) => ({
            menu_name: m.menu_name,
            menu_id: m.menu_id,
            status: m.status,
            statusType: typeof m.status,
            statusValue: getStatusValue(m.status),
            isEnabled: getStatusValue(m.status) === 1,
          }))
        );

        // 检查是否有status为undefined或null的情况
        const undefinedStatus = menuList.value.filter(
          (m) => m.status === undefined || m.status === null
        );
        if (undefinedStatus.length > 0) {
          console.warn(
            '⚠️ 发现status为undefined或null的菜单:',
            undefinedStatus.map((m) => ({
              menu_name: m.menu_name,
              menu_id: m.menu_id,
              status: m.status,
            }))
          );
        }
      }

      console.log('菜单树数据加载成功:', {
        treeData: menuTree.value,
        totalCount: menuList.value.length,
        expandedKeys: expandedRowKeys.value,
      });
    } else {
      message.error(response.message || '获取菜单数据失败');
      menuTree.value = [];
      menuList.value = [];
    }
  } catch (error) {
    console.error('获取菜单数据失败:', error);
    message.error('获取菜单数据失败');
    menuTree.value = [];
    menuList.value = [];
  } finally {
    loading.value = false;
  }
};

// 构建菜单树
const buildMenuTree = (menus: Menu[]): Menu[] => {
  const menuMap = new Map<number, Menu>();
  const rootMenus: Menu[] = [];

  // 创建菜单映射
  menus.forEach((menu) => {
    menuMap.set(menu.menu_id, { ...menu, children: [] });
  });

  // 构建树结构
  menus.forEach((menu) => {
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

// 事件处理
const refreshData = async () => {
  try {
    searchText.value = ''; // 清空搜索条件
    await fetchMenuList();
    message.success('数据刷新成功');
  } catch (error) {
    console.error('刷新数据失败:', error);
    message.error('刷新数据失败，请稍后重试');
  }
};

// 搜索防抖
let searchTimeout: NodeJS.Timeout | null = null;

const handleSearch = () => {
  // 清除之前的搜索定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }

  // 设置新的搜索定时器，300ms后执行搜索
  searchTimeout = setTimeout(() => {
    // 搜索时不需要重新获取数据，filteredMenuData会自动过滤
  }, 300);
};

// 立即搜索（点击搜索按钮时）
const handleSearchImmediate = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  // 搜索时不需要重新获取数据，filteredMenuData会自动过滤
};

// 展开/收起菜单
const onExpand = (expanded: boolean, record: Menu) => {
  if (expanded) {
    if (!expandedRowKeys.value.includes(record.menu_id)) {
      expandedRowKeys.value.push(record.menu_id);
    }
  } else {
    const index = expandedRowKeys.value.indexOf(record.menu_id);
    if (index > -1) {
      expandedRowKeys.value.splice(index, 1);
    }
  }
};

const handleAdd = () => {
  modalMode.value = 'add';
  resetForm();
  modalVisible.value = true;
};

const handleEdit = (record: Menu) => {
  modalMode.value = 'edit';
  currentEditId.value = record.menu_id;

  // 填充表单数据
  Object.assign(formData, {
    menu_name: record.menu_name,
    menu_code: record.menu_code,
    menu_type: record.menu_type,
    parent_id: record.parent_id || 0,
    path: record.path || '',
    component: record.component || '',
    icon: record.icon || '',
    permission: record.permission || '',
    sort_order: record.sort_order || 0,
    status: record.status || 0,
    is_external: record.is_external || false,
    is_cache: record.is_cache !== undefined ? record.is_cache : true,
    is_visible: record.is_visible !== undefined ? record.is_visible : true,
  });

  modalVisible.value = true;
};

const handleView = async (record: Menu) => {
  try {
    detailLoading.value = true;
    detailVisible.value = true;

    const response = await menuApi.getMenu(record.menu_id);
    if (response.success) {
      menuDetail.value = response.data;
    } else {
      message.error(response.message || '获取菜单详情失败');
    }
  } catch (error) {
    console.error('获取菜单详情失败:', error);
    message.error('获取菜单详情失败');
  } finally {
    detailLoading.value = false;
  }
};

const handleDelete = (record: Menu) => {
  // 检查是否有子菜单
  const hasChildren = record.children && record.children.length > 0;
  const childrenCount = hasChildren ? record.children!.length : 0;

  Modal.confirm({
    title: '确认删除',
    content: hasChildren
      ? `菜单"${record.menu_name}"包含 ${childrenCount} 个子菜单，删除后子菜单也将被删除。此操作不可恢复，确定要继续吗？`
      : `确定要删除菜单"${record.menu_name}"吗？此操作不可恢复。`,
    okText: '确定删除',
    cancelText: '取消',
    okType: 'danger',
    width: 450,
    onOk: async () => {
      const hide = message.loading('正在删除菜单...', 0);
      try {
        const response = await menuApi.deleteMenu(record.menu_id);
        hide();

        if (response.success) {
          message.success(`菜单"${record.menu_name}"删除成功`);
          // 刷新数据
          await fetchMenuList();
        } else {
          message.error(response.message || '删除失败，请稍后重试');
        }
      } catch (error: any) {
        hide();
        console.error('删除菜单失败:', error);

        // 根据错误类型提供更具体的错误信息
        if (error.response?.status === 403) {
          message.error('权限不足，无法删除此菜单');
        } else if (error.response?.status === 404) {
          message.error('菜单不存在或已被删除');
        } else if (error.response?.status === 409) {
          message.error('菜单正在被使用，无法删除');
        } else {
          message.error('删除失败，请检查网络连接后重试');
        }
      }
    },
  });
};

const resetForm = () => {
  Object.assign(formData, {
    menu_name: '',
    menu_code: '',
    menu_type: 1, // 1=菜单, 2=按钮, 3=接口
    parent_id: 0,
    path: '',
    component: '',
    icon: '',
    permission: '',
    sort_order: 0,
    status: 0, // 0=禁用, 1=启用
    is_external: false,
    is_cache: true,
    is_visible: true,
  });
  currentEditId.value = null;
  formRef.value?.resetFields();
};

const handleModalOk = async () => {
  try {
    // 表单验证
    await formRef.value?.validate();
    modalLoading.value = true;

    // 数据预处理和验证
    const submitData = {
      menu_name: formData.menu_name.trim(),
      menu_code: formData.menu_code.trim(),
      menu_type: formData.menu_type,
      parent_id: formData.parent_id || undefined,
      path: formData.path?.trim() || '',
      icon: formData.icon?.trim() || '',
      sort_order: formData.sort_order || 0,
      description: formData.description?.trim() || '',
      status: formData.status,
    };

    // 额外的业务逻辑验证
    if (submitData.menu_name.length < 2) {
      message.error('菜单名称至少需要2个字符');
      return;
    }

    if (submitData.menu_code.length < 2) {
      message.error('菜单编码至少需要2个字符');
      return;
    }

    // 检查菜单编码格式（只允许字母、数字、下划线、中划线）
    if (!/^[a-zA-Z0-9_-]+$/.test(submitData.menu_code)) {
      message.error('菜单编码只能包含字母、数字、下划线和中划线');
      return;
    }

    let response;
    const isAdd = modalMode.value === 'add';
    const operationText = isAdd ? '添加' : '更新';

    if (isAdd) {
      response = await menuApi.createMenu(submitData);
    } else {
      response = await menuApi.updateMenu(currentEditId.value!, submitData);
    }

    if (response.success) {
      message.success(`菜单"${submitData.menu_name}"${operationText}成功`);
      modalVisible.value = false;
      // 刷新数据
      await fetchMenuList();
    } else {
      message.error(response.message || `${operationText}失败，请稍后重试`);
    }
  } catch (error: any) {
    console.error('表单提交失败:', error);

    // 根据错误类型提供更具体的错误信息
    if (error.response?.status === 400) {
      const errorMsg = error.response?.data?.message || '请检查输入的数据格式';
      message.error(`数据验证失败：${errorMsg}`);
    } else if (error.response?.status === 403) {
      message.error('权限不足，无法执行此操作');
    } else if (error.response?.status === 409) {
      message.error('菜单编码已存在，请使用其他编码');
    } else if (error.response?.status === 422) {
      message.error('数据格式错误，请检查必填字段');
    } else if (error.name === 'ValidationError') {
      message.error('请检查表单填写是否正确');
    } else {
      const operationText = modalMode.value === 'add' ? '添加' : '更新';
      message.error(`${operationText}失败，请检查网络连接后重试`);
    }
  } finally {
    modalLoading.value = false;
  }
};

const handleModalCancel = () => {
  modalVisible.value = false;
  resetForm();
};

// 组件挂载时获取数据
onMounted(() => {
  fetchMenuList();
});
</script>

<style scoped lang="scss">
.menu-management {
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
        padding: 10px 12px;
        font-size: 13px;
        letter-spacing: -0.1px;
      }

      .ant-table-tbody > tr {
        transition: all 0.2s ease;

        &:hover > td {
          background: rgba(0, 0, 0, 0.02);
        }

        > td {
          padding: 10px 12px;
          border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
          color: #1d1d1f;
        }
      }
    }

    .menu-name-container {
      display: flex;
      align-items: center;

      .menu-name {
        font-weight: 500;
        color: #1d1d1f;
        font-size: 14px;
      }

      .children-count {
        margin-left: 8px;
        color: #86868b;
        font-size: 12px;
      }
    }

    .text-gray {
      color: #86868b;
    }
  }

  :deep(.ant-form-item) {
    margin-bottom: 16px;
  }

  // 弹窗样式已由全局样式统一处理
}

// 响应式设计
@media (max-width: 1200px) {
  .menu-management {
    .page-header,
    .action-bar,
    .table-container {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .menu-management {
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

        :deep(.ant-input-search) {
          width: 100% !important;
        }
      }

      .button-section {
        width: 100%;
        flex-direction: column;

        .action-btn-primary,
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
