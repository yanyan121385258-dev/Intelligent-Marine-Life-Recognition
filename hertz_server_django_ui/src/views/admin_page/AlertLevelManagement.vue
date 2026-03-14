<template>
  <div class="alert-level-management">
    <div class="page-header">
      <h2 class="page-title">
        <WarningOutlined class="title-icon" />
        模型类别管理
      </h2>
      <p class="page-description">管理YOLO检测的警告等级配置</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <a-button @click="refreshLevels">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
        <a-button type="primary" :disabled="!selectedRowKeys.length" @click="openBatchEdit">
          批量修改等级
        </a-button>
      </div>
      <div class="action-right">
        <a-input-search
          v-model:value="searchKeyword"
          placeholder="搜索警告等级名称"
          style="width: 250px"
          @search="handleSearch"
        />
      </div>
    </div>

    <!-- 警告等级表格 -->
    <a-table
      :columns="columns"
      :data-source="filteredLevels"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
      :row-selection="rowSelection"
      class="levels-table"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          {{ record.name }}
        </template>

        <template v-if="column.key === 'display_name'">
          {{ record.display_name }}
        </template>

        <template v-if="column.key === 'alias'">
          <div class="alias-cell">
            <div v-if="!record.editingAlias" class="alias-display" @click="startEditAlias(record)">
              <span class="alias-text">{{ record.alias || '点击编辑' }}</span>
              <EditOutlined class="edit-icon" />
            </div>
            <a-input
              v-else
              v-model:value="record.tempAlias"
              size="small"
              placeholder="请输入别名"
              @blur="saveAlias(record)"
              @pressEnter="saveAlias(record)"
              @keyup.esc="cancelEditAlias(record)"
              ref="aliasInput"
              class="alias-input"
            />
          </div>
        </template>

        <template v-if="column.key === 'alert_level'">
          <a-tag :color="getAlertLevelColor(record.alert_level)">
            {{ record.alert_level_display }}
          </a-tag>
        </template>

        <template v-if="column.key === 'status'">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>

        <template v-if="column.key === 'actions'">
          <div class="action-buttons">
            <a-button size="small" @click="editAlertLevel(record)">
              <template #icon>
                <EditOutlined />
              </template>
              切换等级
            </a-button>
            <a-button
              size="small"
              :type="record.is_active ? 'default' : 'primary'"
              @click="toggleStatus(record)"
            >
              <template #icon>
                <PoweroffOutlined />
              </template>
              {{ record.is_active ? '禁用' : '启用' }}
            </a-button>
          </div>
        </template>
      </template>
    </a-table>

    <!-- 详情弹窗 -->
    <a-modal v-model:visible="detailModalVisible" title="警告等级详情" :footer="null" width="600px">
      <div v-if="currentLevel" class="level-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="名称">
            {{ currentLevel.name }}
          </a-descriptions-item>
          <a-descriptions-item label="显示名称">
            {{ currentLevel.display_name }}
          </a-descriptions-item>
          <a-descriptions-item label="警告等级">
            <a-tag :color="getAlertLevelColor(currentLevel.alert_level)">
              {{ currentLevel.alert_level_display }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="currentLevel.is_active ? 'green' : 'red'">
              {{ currentLevel.is_active ? '启用' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="模型名称">
            {{ currentLevel.model_name }}
          </a-descriptions-item>
          <a-descriptions-item label="类别ID">
            {{ currentLevel.category_id }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>

    <!-- 切换警告等级弹窗 -->
    <a-modal
      v-model:visible="editModalVisible"
      title="切换警告等级"
      @ok="handleEdit"
      @cancel="handleEditCancel"
      width="500px"
    >
      <div v-if="currentLevel" class="alert-level-edit">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="名称">
            {{ currentLevel.name }}
          </a-descriptions-item>
          <a-descriptions-item label="显示名称">
            {{ currentLevel.display_name }}
          </a-descriptions-item>
          <a-descriptions-item label="当前警告等级">
            <a-tag :color="getAlertLevelColor(currentLevel.alert_level)">
              {{ currentLevel.alert_level_display }}
            </a-tag>
          </a-descriptions-item>
        </a-descriptions>

        <a-form
          ref="editFormRef"
          :model="editForm"
          :rules="editRules"
          layout="vertical"
          style="margin-top: 20px"
        >
          <a-form-item label="新的警告等级" name="alert_level">
            <a-select
              v-model:value="editForm.alert_level"
              placeholder="请选择新的警告等级"
              style="width: 100%"
            >
              <a-select-option value="low">低</a-select-option>
              <a-select-option value="medium">中</a-select-option>
              <a-select-option value="high">高</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- 批量切换警告等级弹窗 -->
    <a-modal
      v-model:visible="batchEditModalVisible"
      title="批量修改警告等级"
      @ok="handleBatchEdit"
      @cancel="handleBatchEditCancel"
      width="500px"
    >
      <div class="alert-level-edit">
        <p style="margin-bottom: 12px">
          已选择 <strong>{{ selectedRowKeys.length }}</strong> 个类别，将统一修改为新的警告等级。
        </p>

        <a-form
          ref="batchEditFormRef"
          :model="batchEditForm"
          :rules="editRules"
          layout="vertical"
          style="margin-top: 12px"
        >
          <a-form-item label="新的警告等级" name="alert_level">
            <a-select
              v-model:value="batchEditForm.alert_level"
              placeholder="请选择新的警告等级"
              style="width: 100%"
            >
              <a-select-option value="low">低</a-select-option>
              <a-select-option value="medium">中</a-select-option>
              <a-select-option value="high">高</a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import {
  WarningOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  PoweroffOutlined,
} from '@ant-design/icons-vue';
import { yoloApi, AlertLevel, YoloModel } from '@/api/yolo';
import dayjs from 'dayjs';

// 响应式数据
const loading = ref(false);
const editing = ref(false);
const levels = ref<AlertLevel[]>([]);
const searchKeyword = ref('');
const currentModel = ref<YoloModel | null>(null);
const selectedRowKeys = ref<number[]>([]);

// 表格多选配置
const rowSelection = computed(() => ({
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys: (string | number)[]) => {
    selectedRowKeys.value = keys as number[];
  },
}));

// 弹窗状态
const detailModalVisible = ref(false);
const editModalVisible = ref(false);
const currentLevel = ref<AlertLevel | null>(null);
const batchEditModalVisible = ref(false);

// 编辑表单
const editForm = reactive({
  alert_level: 'low' as 'low' | 'medium' | 'high',
});

// 批量编辑表单
const batchEditForm = reactive({
  alert_level: 'low' as 'low' | 'medium' | 'high',
});

// 表单引用
const editFormRef = ref();
const batchEditFormRef = ref();

// 表单验证规则
const editRules = {
  alert_level: [{ required: true, message: '请选择警告等级', trigger: 'change' }],
};

// 分页配置（受控分页）
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`,
  onChange: (page: number, pageSize: number) => {
    pagination.current = page;
    pagination.pageSize = pageSize;
  },
  onShowSizeChange: (page: number, pageSize: number) => {
    pagination.current = page;
    pagination.pageSize = pageSize;
  },
});

// 表格列配置
const columns = [
  {
    title: '名称',
    key: 'name',
    width: 120,
  },
  {
    title: '显示名称',
    key: 'display_name',
    width: 150,
  },
  {
    title: '别名',
    key: 'alias',
    width: 120,
  },
  {
    title: '警告等级',
    key: 'alert_level',
    width: 120,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
  },
];

// 过滤后的等级列表
const filteredLevels = computed(() => {
  if (!searchKeyword.value) {
    return levels.value;
  }
  return levels.value.filter(
    (level) =>
      level.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      level.display_name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      level.alert_level_display.toLowerCase().includes(searchKeyword.value.toLowerCase())
  );
});

// 格式化日期
const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss');
};

// 获取警告等级颜色
const getAlertLevelColor = (level: string) => {
  const colorMap = {
    low: 'green',
    medium: 'orange',
    high: 'red',
  };
  return colorMap[level] || 'default';
};

// 获取警告等级列表（仅显示当前启用模型的类别）
const fetchLevels = async () => {
  try {
    loading.value = true;
    console.log('🔍 开始获取警告等级列表...');

    // 先获取当前启用的模型
    let enabledModelId: string | null = null;
    try {
      const modelResp = await yoloApi.getCurrentEnabledModel();
      console.log('📋 当前启用模型API响应:', modelResp);
      if (modelResp.success && modelResp.data) {
        currentModel.value = modelResp.data;
        enabledModelId = modelResp.data.id;
      } else {
        currentModel.value = null;
      }
    } catch (e) {
      console.error('❌ 获取当前启用模型失败:', e);
      currentModel.value = null;
    }

    // 再获取所有类别
    const response = await yoloApi.getAlertLevels();
    console.log('📋 警告等级API响应:', response);

    if (response.success && response.data) {
      let data = response.data;

      // 如果有启用模型，则按模型过滤类别
      if (enabledModelId) {
        const modelIdNum = Number(enabledModelId);
        data = data.filter((level) => level.model === modelIdNum);
        console.log('✅ 过滤后类别列表:', data);
      }

      levels.value = data;
      pagination.total = data.length;
      pagination.current = 1;
      console.log('✅ 警告等级获取成功:', levels.value);
    } else {
      console.error('❌ 获取警告等级失败:', response.message);
      message.error(response.message || '获取警告等级失败');
    }
  } catch (error) {
    console.error('❌ 获取警告等级异常:', error);
    message.error('获取警告等级失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

// 刷新等级列表
const refreshLevels = () => {
  fetchLevels();
};

// 查看详情
const viewDetails = (level: AlertLevel) => {
  currentLevel.value = level;
  detailModalVisible.value = true;
};

// 编辑警告等级
const editAlertLevel = (level: AlertLevel) => {
  currentLevel.value = level;
  editForm.alert_level = level.alert_level;
  editModalVisible.value = true;
};

// 开始编辑alias
const startEditAlias = (record: AlertLevel) => {
  record.editingAlias = true;
  record.tempAlias = record.alias;
  // 使用nextTick确保DOM更新后再聚焦
  nextTick(() => {
    const input = document.querySelector('.alias-cell input') as HTMLInputElement;
    if (input) {
      input.focus();
      input.select();
    }
  });
};

// 保存alias
const saveAlias = async (record: AlertLevel) => {
  const newAlias = record.tempAlias?.trim() || '';

  if (newAlias === record.alias) {
    // 没有变化，直接取消编辑
    cancelEditAlias(record);
    return;
  }

  try {
    console.log('🔍 开始更新alias...', record.id, newAlias);

    // 调用API更新alias
    const response = await yoloApi.updateAlertLevel(record.id.toString(), {
      alias: newAlias,
    });

    console.log('📋 更新alias API响应:', response);

    if (response.success) {
      record.alias = newAlias;
      message.success('别名更新成功');
    } else {
      console.error('❌ 更新alias失败:', response.message);
      message.error(response.message || '更新别名失败');
    }
  } catch (error) {
    console.error('❌ 更新alias异常:', error);
    message.error('更新别名失败，请检查网络连接');
  } finally {
    record.editingAlias = false;
    // 不要清空tempAlias，保持数据一致性
  }
};

// 取消编辑alias
const cancelEditAlias = (record: AlertLevel) => {
  record.editingAlias = false;
  record.tempAlias = '';
};

// 处理编辑
const handleEdit = async () => {
  try {
    await editFormRef.value.validate();

    if (!currentLevel.value) return;

    editing.value = true;
    console.log('开始切换警告等级...', currentLevel.value.id, editForm);

    // 构造更新数据 - 只传递 alert_level
    const updateData = {
      alert_level: editForm.alert_level,
    };

    console.log('发送更新数据:', updateData);

    const response = await yoloApi.updateAlertLevel(currentLevel.value.id.toString(), updateData);
    console.log('更新警告等级API响应:', response);

    if (response.success) {
      message.success(`警告等级已切换为: ${editForm.alert_level}`);
      editModalVisible.value = false;
      fetchLevels();
    } else {
      console.error('切换警告等级失败:', response.message);
      message.error(response.message || '切换失败');
    }
  } catch (error) {
    console.error('切换警告等级异常:', error);
    message.error('切换失败');
  } finally {
    editing.value = false;
  }
};

// 取消编辑
const handleEditCancel = () => {
  editModalVisible.value = false;
  currentLevel.value = null;
};

// 打开批量编辑弹窗
const openBatchEdit = () => {
  if (!selectedRowKeys.value.length) {
    message.warning('请先选择要修改的类别');
    return;
  }
  batchEditForm.alert_level = 'low';
  batchEditModalVisible.value = true;
};

// 批量修改警告等级
const handleBatchEdit = async () => {
  try {
    if (batchEditFormRef.value && batchEditFormRef.value.validate) {
      await batchEditFormRef.value.validate();
    }

    if (!selectedRowKeys.value.length) {
      message.warning('请先选择要修改的类别');
      return;
    }

    editing.value = true;
    const targetLevel = batchEditForm.alert_level;
    let successCount = 0;
    let failCount = 0;

    for (const id of selectedRowKeys.value) {
      try {
        const response = await yoloApi.updateAlertLevel(id.toString(), {
          alert_level: targetLevel,
        });
        if (response.success) {
          successCount++;
        } else {
          failCount++;
        }
      } catch (error) {
        console.error('批量切换警告等级异常:', error);
        failCount++;
      }
    }

    if (successCount > 0) {
      message.success(`成功更新 ${successCount} 条警告等级`);
    }
    if (failCount > 0) {
      message.error(`${failCount} 条更新失败，请检查日志`);
    }

    batchEditModalVisible.value = false;
    selectedRowKeys.value = [];
    fetchLevels();
  } catch (error) {
    console.error('批量切换警告等级失败:', error);
  } finally {
    editing.value = false;
  }
};

// 取消批量编辑
const handleBatchEditCancel = () => {
  batchEditModalVisible.value = false;
};

// 切换状态
const toggleStatus = async (level: AlertLevel) => {
  try {
    console.log('开始切换警告等级状态...', level.id);

    const response = await yoloApi.toggleAlertLevelStatus(level.id.toString());
    console.log('切换状态API响应:', response);

    if (response.success) {
      message.success(level.is_active ? '警告等级已禁用' : '警告等级已启用');
      fetchLevels();
    } else {
      console.error('❌ 切换状态失败:', response.message);
      message.error(response.message || '状态切换失败');
    }
  } catch (error) {
    console.error('❌ 切换状态异常:', error);
    message.error('状态切换失败');
  }
};

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理，这里只负责重置分页
  pagination.current = 1;
  pagination.total = filteredLevels.value.length;
};

// 组件挂载时获取数据
onMounted(() => {
  fetchLevels();
});
</script>

<style scoped lang="scss">
.alert-level-management {
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

    .page-title {
      display: flex;
      align-items: center;
      margin: 0 0 4px 0;
      font-size: 24px;
      font-weight: 600;
      color: #1d1d1f;
      letter-spacing: -0.3px;
      line-height: 1.2;

      .title-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(245, 158, 11, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        color: #f59e0b;
        font-size: 24px;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(245, 158, 11, 0.15);
        }
      }
    }

    .page-description {
      margin: 0;
      color: #86868b;
      font-size: 14px;
      font-weight: 400;
      padding-left: 64px;
    }
  }

  // 操作栏 - 苹果风格
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0 28px 24px 28px;
    padding: 20px 24px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    flex-wrap: wrap;
    gap: 16px;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .action-left {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;

      .ant-btn {
        border-radius: 12px;
        height: 40px;
        padding: 0 20px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        border-color: rgba(0, 0, 0, 0.12);
        color: #1d1d1f;
        background: rgba(255, 255, 255, 0.8);

        &:hover {
          background: rgba(0, 0, 0, 0.04);
          border-color: rgba(0, 0, 0, 0.16);
          transform: translateY(-1px);
        }
      }
    }

    .action-right {
      display: flex;
      align-items: center;

      :deep(.ant-input-search) {
        .ant-input {
          border-radius: 10px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          height: 40px;

          &:hover {
            border-color: #3b82f6;
          }

          &:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }

        .ant-btn {
          border-radius: 0 10px 10px 0;
          height: 40px;
        }
      }
    }
  }

  // 表格容器 - 苹果风格
  .levels-table {
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

    .action-buttons {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;

      .ant-btn {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          transform: translateY(-1px);
        }
      }
    }

    .alias-cell {
      .alias-display {
        cursor: pointer;
        padding: 8px 12px;
        border-radius: 10px;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 100px;
        border: 0.5px dashed rgba(0, 0, 0, 0.12);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        position: relative;

        &:hover {
          border-color: #3b82f6;
          background: rgba(255, 255, 255, 1);
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);

          .alias-text {
            color: #3b82f6;
            font-weight: 500;
          }

          .edit-icon {
            color: #3b82f6;
            transform: scale(1.1);
          }
        }

        .alias-text {
          color: #1d1d1f;
          font-size: 13px;
          transition: all 0.2s ease;
          flex: 1;

          &:empty::before {
            content: '点击编辑';
            color: #86868b;
            font-style: italic;
          }
        }

        .edit-icon {
          color: #86868b;
          font-size: 12px;
          margin-left: 6px;
          transition: all 0.2s ease;
        }
      }

      .alias-input {
        border: 0.5px solid #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 1) !important;

        &:focus {
          border-color: #3b82f6 !important;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
        }
      }
    }

    // 标签样式优化
    :deep(.ant-tag) {
      border-radius: 6px;
      font-weight: 500;
      padding: 2px 10px;
      border: 0.5px solid currentColor;
      opacity: 0.8;
    }
  }

  .level-detail {
    :deep(.ant-descriptions-item-label) {
      font-weight: 500;
      color: #1d1d1f;
      background: rgba(0, 0, 0, 0.02);
    }

    :deep(.ant-descriptions-item-content) {
      color: #86868b;
    }
  }

  // 分页器样式优化 - 苹果风格
  :deep(.ant-pagination) {
    margin: 20px 0;
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
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .alert-level-management {
    .page-header,
    .action-bar,
    .levels-table {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .alert-level-management {
    .page-header {
      padding: 24px 16px;

      .page-title {
        font-size: 20px;

        .title-icon {
          width: 40px;
          height: 40px;
          font-size: 20px;
          margin-right: 12px;
        }
      }

      .page-description {
        font-size: 13px;
        padding-left: 52px;
      }
    }

    .action-bar {
      margin: 0 16px 20px 16px;
      padding: 16px;
      flex-direction: column;
      align-items: stretch;

      .action-left {
        width: 100%;
        justify-content: flex-start;
      }

      .action-right {
        width: 100%;

        :deep(.ant-input-search) {
          width: 100% !important;
        }
      }
    }

    .levels-table {
      margin: 0 16px 20px 16px;
      border-radius: 12px;
    }
  }
}
</style>
