<template>
  <div class="department-management">
    <!-- 页面头部 - 苹果风格 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <ApartmentOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">部门管理</h1>
          <p class="page-description">管理组织架构和部门信息</p>
        </div>
      </div>
    </div>

    <!-- 操作栏 - 苹果风格 -->
    <div class="action-bar">
      <div class="button-section">
        <a-button type="primary" @click="handleAdd" class="action-btn-primary">
          <template #icon><PlusOutlined /></template>
          添加部门
        </a-button>
        <a-button @click="refreshData" class="action-btn-secondary">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
        <a-button @click="expandAll" class="action-btn-secondary">
          <template #icon><ExpandAltOutlined /></template>
          展开全部
        </a-button>
        <a-button @click="collapseAll" class="action-btn-secondary">
          <template #icon><ShrinkOutlined /></template>
          收起全部
        </a-button>
      </div>
    </div>

    <!-- 部门树形表格 -->
    <div class="table-container">
      <a-table
        :columns="columns"
        :data-source="paginatedData"
        :loading="loading"
        :pagination="pagination"
        :expanded-row-keys="expandedKeys"
        @expand="onExpand"
        @change="handleTableChange"
        row-key="dept_id"
        size="middle"
      >
        <!-- 部门名称列 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'dept_name'">
            <div class="dept-name-container">
              <span
                v-if="hasChildren(record)"
                class="toggle-icon"
                @click.stop="toggleChildren(record)"
              >
                <CaretDownOutlined v-if="isExpanded(record.dept_id)" />
                <CaretRightOutlined v-else />
              </span>
              <span class="dept-name">{{ record.dept_name }}</span>
              <span v-if="hasChildren(record)" class="children-count"
                >({{ getChildrenCount(record) }})</span
              >
            </div>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.key === 'status'">
            <a-tag :color="record.status === 1 ? 'green' : 'red'">
              {{ record.status === 1 ? '启用' : '禁用' }}
            </a-tag>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleViewDetail(record.dept_id)">
                查看详情
              </a-button>
              <a-button type="link" size="small" @click="handleEdit(record)"> 编辑 </a-button>
              <a-button type="link" size="small" @click="handleAddChild(record)">
                添加子部门
              </a-button>
              <a-popconfirm
                title="确定要删除这个部门吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.dept_id)"
              >
                <a-button type="link" size="small" danger> 删除 </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 添加/编辑部门弹窗 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalMode === 'add' ? '添加部门' : '编辑部门'"
      :confirm-loading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      width="600px"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item label="上级部门" name="parent_id">
          <a-tree-select
            v-model:value="formData.parent_id"
            :tree-data="departmentTreeOptions"
            placeholder="请选择上级部门"
            tree-default-expand-all
            :field-names="{ children: 'children', label: 'dept_name', value: 'dept_id' }"
            allow-clear
          />
        </a-form-item>

        <a-form-item label="部门名称" name="dept_name">
          <a-input v-model:value="formData.dept_name" placeholder="请输入部门名称" />
        </a-form-item>

        <a-form-item label="部门编码" name="dept_code">
          <a-input v-model:value="formData.dept_code" placeholder="请输入部门编码" />
        </a-form-item>

        <a-form-item label="负责人" name="leader">
          <a-input v-model:value="formData.leader" placeholder="请输入负责人姓名" />
        </a-form-item>

        <a-form-item label="联系电话" name="phone">
          <a-input v-model:value="formData.phone" placeholder="请输入联系电话" />
        </a-form-item>

        <a-form-item label="邮箱" name="email">
          <a-input v-model:value="formData.email" placeholder="请输入邮箱地址" />
        </a-form-item>

        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="formData.status">
            <a-radio :value="1">启用</a-radio>
            <a-radio :value="0">禁用</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="排序" name="sort_order">
          <a-input-number
            v-model:value="formData.sort_order"
            :min="0"
            :max="9999"
            placeholder="请输入排序值"
            style="width: 100%"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 部门详情弹窗 -->
    <a-modal v-model:visible="detailVisible" title="部门详情" :footer="null" width="600px">
      <a-spin :spinning="detailLoading">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="部门ID">
            {{ departmentDetail?.dept_id }}
          </a-descriptions-item>
          <a-descriptions-item label="部门名称">
            {{ departmentDetail?.dept_name }}
          </a-descriptions-item>
          <a-descriptions-item label="部门编码">
            {{ departmentDetail?.dept_code }}
          </a-descriptions-item>
          <a-descriptions-item label="上级部门ID">
            {{ departmentDetail?.parent_id || '无' }}
          </a-descriptions-item>
          <a-descriptions-item label="负责人">
            {{ departmentDetail?.leader }}
          </a-descriptions-item>
          <a-descriptions-item label="联系电话">
            {{ departmentDetail?.phone || '未设置' }}
          </a-descriptions-item>
          <a-descriptions-item label="邮箱">
            {{ departmentDetail?.email || '未设置' }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="departmentDetail?.status === 1 ? 'green' : 'red'">
              {{ departmentDetail?.status === 1 ? '启用' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="排序">
            {{ departmentDetail?.sort_order }}
          </a-descriptions-item>
          <a-descriptions-item label="用户数量">
            {{ departmentDetail?.user_count || 0 }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间" :span="2">
            {{
              departmentDetail?.created_at
                ? new Date(departmentDetail.created_at).toLocaleString()
                : ''
            }}
          </a-descriptions-item>
          <a-descriptions-item label="更新时间" :span="2">
            {{
              departmentDetail?.updated_at
                ? new Date(departmentDetail.updated_at).toLocaleString()
                : ''
            }}
          </a-descriptions-item>
        </a-descriptions>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { message } from 'ant-design-vue';
import type { FormInstance } from 'ant-design-vue';
import {
  PlusOutlined,
  ReloadOutlined,
  ExpandAltOutlined,
  ShrinkOutlined,
  CaretDownOutlined,
  CaretRightOutlined,
  ApartmentOutlined,
} from '@ant-design/icons-vue';
import { departmentApi, type Department, type CreateDepartmentParams } from '@/api';

// 响应式数据
const loading = ref(false);
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalMode = ref<'add' | 'edit'>('add');
const formRef = ref<FormInstance>();
const expandedKeys = ref<number[]>([]);

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 5,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['5', '10', '20', '50'],
  showTotal: (total: number) => `共 ${total} 条`,
  hideOnSinglePage: false,
});

// 判断部门是否有子部门
const hasChildren = (dept: Department): boolean => {
  return dept.children && dept.children.length > 0;
};

// 获取子部门数量
const getChildrenCount = (dept: Department): number => {
  return dept.children ? dept.children.length : 0;
};

// 判断部门是否展开
const isExpanded = (deptId: number): boolean => {
  return expandedKeys.value.includes(deptId);
};

// 切换部门折叠状态
const toggleChildren = (dept: Department) => {
  const index = expandedKeys.value.indexOf(dept.dept_id);
  if (index > -1) {
    // 如果已展开，则折叠
    expandedKeys.value.splice(index, 1);
  } else {
    // 如果已折叠，则展开
    expandedKeys.value.push(dept.dept_id);
  }
};

// 分页后的数据
const paginatedData = computed(() => {
  const startIndex = (pagination.current - 1) * pagination.pageSize;
  const endIndex = startIndex + pagination.pageSize;
  pagination.total = departmentTree.value.length;
  return departmentTree.value.slice(startIndex, endIndex);
});

// 表格变化处理
const handleTableChange = (pag: any) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
};

// 部门详情相关
const detailVisible = ref(false);
const detailLoading = ref(false);
const departmentDetail = ref<Department | null>(null);

// 部门数据
const departmentList = ref<Department[]>([]);
const departmentTree = ref<Department[]>([]);

// 表单数据
const formData = reactive<CreateDepartmentParams>({
  parent_id: null,
  dept_name: '',
  dept_code: '',
  leader: '',
  phone: '',
  email: '',
  status: 1,
  sort_order: 0,
});

// 当前编辑的部门ID
const currentEditId = ref<number | null>(null);

// 表格列定义
const columns = [
  {
    title: '部门名称',
    dataIndex: 'dept_name',
    key: 'dept_name',
    fixed: 'left',
  },
  {
    title: '部门编码',
    dataIndex: 'dept_code',
    key: 'dept_code',
  },
  {
    title: '负责人',
    dataIndex: 'leader',
    key: 'leader',
  },
  {
    title: '联系电话',
    dataIndex: 'phone',
    key: 'phone',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
  },
  {
    title: '排序',
    dataIndex: 'sort_order',
    key: 'sort_order',
  },
  {
    title: '操作',
    key: 'action',
    fixed: 'right',
  },
];

// 表单验证规则
const formRules = computed(() => ({
  dept_name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
    { min: 2, max: 50, message: '部门名称长度在2-50个字符', trigger: 'blur' },
  ],
  dept_code: [
    { required: true, message: '请输入部门编码', trigger: 'blur' },
    { min: 2, max: 20, message: '部门编码长度在2-20个字符', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9_-]+$/,
      message: '部门编码只能包含字母、数字、下划线和横线',
      trigger: 'blur',
    },
  ],
  leader: [{ max: 20, message: '负责人姓名不能超过20个字符', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  sort_order: [
    { required: true, message: '请输入排序值', trigger: 'blur' },
    { type: 'number', min: 0, max: 9999, message: '排序值范围为0-9999', trigger: 'blur' },
  ],
}));

// 部门树选择器选项
const departmentTreeOptions = computed(() => {
  const addRootOption = (tree: Department[]): Department[] => {
    return [{ dept_id: 0, dept_name: '根部门', children: tree } as Department, ...tree];
  };
  return addRootOption(departmentTree.value);
});

// 获取部门树数据
const fetchDepartmentTree = async () => {
  try {
    loading.value = true;
    const response = await departmentApi.getDepartmentList();
    if (response.success) {
      // 后端直接返回树形结构
      departmentTree.value = response.data;
      // 默认展开第一级
      expandedKeys.value = departmentTree.value.map((item) => item.dept_id);
    } else {
      message.error(response.message || '获取部门数据失败');
    }
  } catch (error) {
    console.error('获取部门数据失败:', error);
    message.error('获取部门数据失败');
  } finally {
    loading.value = false;
  }
};

// 刷新数据
const refreshData = () => {
  fetchDepartmentTree();
};

// 展开/收起处理
const onExpand = (expanded: boolean, record: Department) => {
  if (expanded) {
    expandedKeys.value.push(record.dept_id);
  } else {
    const index = expandedKeys.value.indexOf(record.dept_id);
    if (index > -1) {
      expandedKeys.value.splice(index, 1);
    }
  }
};

// 展开全部
const expandAll = () => {
  const getAllKeys = (tree: Department[]): number[] => {
    let keys: number[] = [];
    tree.forEach((item) => {
      keys.push(item.dept_id);
      if (item.children && item.children.length > 0) {
        keys = keys.concat(getAllKeys(item.children));
      }
    });
    return keys;
  };
  expandedKeys.value = getAllKeys(departmentTree.value);
};

// 收起全部
const collapseAll = () => {
  expandedKeys.value = [];
};

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    parent_id: 0,
    dept_name: '',
    dept_code: '',
    leader: '',
    phone: '',
    email: '',
    status: 1,
    sort_order: 0,
  });
  currentEditId.value = null;
  formRef.value?.resetFields();
};

// 查看部门详情
const handleViewDetail = async (deptId: number) => {
  console.log('点击查看详情，部门ID:', deptId);
  try {
    detailLoading.value = true;
    detailVisible.value = true;
    console.log('弹窗状态设置为:', detailVisible.value);
    const response = await departmentApi.getDepartment(deptId);
    if (response.success) {
      departmentDetail.value = response.data;
      console.log('获取部门详情成功:', response.data);
    } else {
      message.error(response.message || '获取部门详情失败');
    }
  } catch (error) {
    console.error('获取部门详情失败:', error);
    message.error('获取部门详情失败');
  } finally {
    detailLoading.value = false;
  }
};

// 添加部门
const handleAdd = () => {
  resetForm();
  modalMode.value = 'add';
  modalVisible.value = true;
};

// 添加子部门
const handleAddChild = (parent: Department) => {
  resetForm();
  formData.parent_id = parent.dept_id;
  modalMode.value = 'add';
  modalVisible.value = true;
};

// 编辑部门
const handleEdit = (record: Department) => {
  console.log('点击编辑部门，部门信息:', record);
  resetForm();
  Object.assign(formData, {
    parent_id: record.parent_id,
    dept_name: record.dept_name,
    dept_code: record.dept_code,
    leader: record.leader,
    phone: record.phone,
    email: record.email,
    status: record.status,
    sort_order: record.sort_order,
  });
  currentEditId.value = record.dept_id;
  modalMode.value = 'edit';
  modalVisible.value = true;
  console.log('编辑弹窗状态设置为:', modalVisible.value);
  console.log('表单数据:', formData);
};

// 删除部门
const handleDelete = async (id: number) => {
  try {
    const response = await departmentApi.deleteDepartment(id);
    if (response.success) {
      message.success('删除成功');
      await fetchDepartmentTree();
    } else {
      message.error(response.message || '删除失败');
    }
  } catch (error) {
    console.error('删除部门失败:', error);
    message.error('删除失败');
  }
};

// 弹窗确定
const handleModalOk = async () => {
  try {
    await formRef.value?.validate();
    modalLoading.value = true;

    // 确保数据类型正确，符合后端要求
    const submitData = {
      parent_id: Number(formData.parent_id) || 0,
      dept_name: String(formData.dept_name || '').trim(),
      dept_code: String(formData.dept_code || '').trim(),
      leader: String(formData.leader || '').trim(),
      phone: String(formData.phone || '').trim(),
      email: String(formData.email || '').trim(),
      status: Number(formData.status) || 0,
      sort_order: Number(formData.sort_order) || 0,
    };

    console.log('提交数据:', submitData);
    console.log('操作模式:', modalMode.value);

    let response;
    if (modalMode.value === 'add') {
      response = await departmentApi.createDepartment(submitData);
    } else {
      response = await departmentApi.updateDepartment(currentEditId.value!, submitData);
    }

    if (response.success) {
      message.success(modalMode.value === 'add' ? '添加成功' : '更新成功');
      modalVisible.value = false;
      await fetchDepartmentTree();
    } else {
      message.error(response.message || (modalMode.value === 'add' ? '添加失败' : '更新失败'));
    }
  } catch (error) {
    console.error('操作失败:', error);
    message.error('操作失败');
  } finally {
    modalLoading.value = false;
  }
};

// 弹窗取消
const handleModalCancel = () => {
  modalVisible.value = false;
  resetForm();
};

// 组件挂载时获取数据
onMounted(() => {
  fetchDepartmentTree();
});
</script>

<style scoped lang="scss">
.department-management {
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
        background: rgba(59, 130, 246, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(59, 130, 246, 0.15);
        }

        .header-icon {
          font-size: 24px;
          color: #3b82f6;
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

    .dept-name-container {
      display: flex;
      align-items: center;

      .toggle-icon {
        margin-right: 8px;
        cursor: pointer;
        color: #3b82f6;
        font-size: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 4px;
        transition: all 0.2s ease;

        &:hover {
          color: #2563eb;
          background: rgba(59, 130, 246, 0.1);
        }
      }

      .dept-name {
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

  :deep(.ant-form-item) {
    margin-bottom: 16px;
  }

  // 弹窗样式已由全局样式统一处理
}

// 响应式设计
@media (max-width: 1200px) {
  .department-management {
    .page-header,
    .action-bar,
    .table-container {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .department-management {
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

      .button-section {
        width: 100%;
        flex-wrap: wrap;
        gap: 8px;

        .action-btn-primary,
        .action-btn-secondary {
          flex: 1;
          min-width: 120px;
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
