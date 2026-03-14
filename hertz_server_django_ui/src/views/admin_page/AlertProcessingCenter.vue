<template>
  <div class="alert-processing-center">
    <div class="page-header">
      <h1 class="page-title">
        <BellOutlined class="title-icon" />
        告警处理中心
      </h1>
      <p class="page-description">管理和处理所有用户的检测告警记录</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <a-row :gutter="16">
        <a-col :xs="24" :sm="6" :md="6" :lg="6" :xl="6">
          <a-card class="stat-card">
            <a-statistic title="总告警数" :value="totalAlerts" :value-style="{ color: '#1890ff' }">
              <template #prefix>
                <BellOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="6" :md="6" :lg="6" :xl="6">
          <a-card class="stat-card">
            <a-statistic title="待处理" :value="pendingAlerts" :value-style="{ color: '#faad14' }">
              <template #prefix>
                <ClockCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="6" :md="6" :lg="6" :xl="6">
          <a-card class="stat-card">
            <a-statistic
              title="已处理"
              :value="confirmedAlerts"
              :value-style="{ color: '#52c41a' }"
            >
              <template #prefix>
                <CheckCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="6" :md="6" :lg="6" :xl="6">
          <a-card class="stat-card">
            <a-statistic
              title="误报"
              :value="falsePositiveAlerts"
              :value-style="{ color: '#ff4d4f' }"
            >
              <template #prefix>
                <CloseCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <a-button @click="refreshAlerts" :loading="loading">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
        <a-button @click="batchProcess" :disabled="selectedRowKeys.length === 0" type="primary">
          <template #icon>
            <CheckOutlined />
          </template>
          批量处理
        </a-button>
      </div>
      <div class="action-right">
        <a-select
          v-model:value="statusFilter"
          placeholder="筛选状态"
          style="width: 120px; margin-right: 8px"
          @change="handleStatusFilter"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="pending">待处理</a-select-option>
          <a-select-option value="is_confirm">已处理</a-select-option>
          <a-select-option value="false_positive">误报</a-select-option>
        </a-select>
        <a-select
          v-model:value="levelFilter"
          placeholder="筛选等级"
          style="width: 120px; margin-right: 8px"
          @change="handleLevelFilter"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="high">高风险</a-select-option>
          <a-select-option value="medium">中等风险</a-select-option>
          <a-select-option value="low">低风险</a-select-option>
        </a-select>
        <a-input-search
          v-model:value="searchKeyword"
          placeholder="搜索告警内容"
          style="width: 200px"
          @search="handleSearch"
        />
      </div>
    </div>

    <!-- 告警列表 -->
    <a-card class="alerts-card">
      <a-table
        :columns="columns"
        :data-source="paginatedAlerts"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        row-key="id"
        class="alerts-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'alert_level'">
            <a-tag :color="getAlertLevelColor(record.alert_level)">
              {{ record.alert_level_display }}
            </a-tag>
          </template>

          <template v-if="column.key === 'alert_category'">
            <span>{{ record.alert_category || '-' }}</span>
          </template>

          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>

          <template v-if="column.key === 'detection_info'">
            <div class="detection-info">
              <div class="detection-image">
                <a-image
                  :src="getImageUrl(record.detection_info.result_filename)"
                  :alt="record.detection_info.original_filename"
                  :width="80"
                  :preview="{
                    src: getImageUrl(record.detection_info.result_filename),
                    mask: '点击查看',
                    zIndex: 10002,
                  }"
                  :fallback="'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5Zu+54mH5Yqg6L295aSx6LSlPC90ZXh0Pjwvc3ZnPg=='"
                  @error="handleImageError"
                />
              </div>
              <div class="detection-stats">
                <span>目标: {{ record.detection_info.object_count }}个</span>
                <span>置信度: {{ (record.detection_info.avg_confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </template>

          <template v-if="column.key === 'user_name'">
            <a-tag color="blue">{{ record.user_name }}</a-tag>
          </template>

          <template v-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>

          <template v-if="column.key === 'actions'">
            <div class="action-buttons">
              <a-button size="small" @click="viewAlertDetail(record)">
                <template #icon>
                  <EyeOutlined />
                </template>
                查看详情
              </a-button>
              <a-dropdown v-if="record.status === 'pending'">
                <a-button size="small" type="primary">
                  <template #icon>
                    <CheckOutlined />
                  </template>
                  处理
                  <DownOutlined />
                </a-button>
                <template #overlay>
                  <a-menu @click="({ key }) => handleProcessAlert(record, key)">
                    <a-menu-item key="is_confirm">
                      <CheckCircleOutlined />
                      标记为已处理
                    </a-menu-item>
                    <a-menu-item key="false_positive">
                      <CloseCircleOutlined />
                      标记为误报
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
              <a-button v-else size="small" @click="resetAlertStatus(record)">
                <template #icon>
                  <UndoOutlined />
                </template>
                重置状态
              </a-button>
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 告警详情弹窗 -->
    <a-modal v-model:visible="detailModalVisible" title="告警详情" :footer="null" width="800px">
      <div v-if="currentAlert" class="alert-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="告警ID">
            {{ currentAlert.id }}
          </a-descriptions-item>
          <a-descriptions-item label="告警等级">
            <a-tag :color="getAlertLevelColor(currentAlert.alert_level)">
              {{ currentAlert.alert_level_display }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="告警类别">
            {{ currentAlert.alert_category }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(currentAlert.status)">
              {{ getStatusText(currentAlert.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="检测文件">
            {{ currentAlert.detection_info.original_filename }}
          </a-descriptions-item>
          <a-descriptions-item label="检测类型">
            {{ currentAlert.detection_info.detection_type }}
          </a-descriptions-item>
          <a-descriptions-item label="检测目标数">
            {{ currentAlert.detection_info.object_count }}个
          </a-descriptions-item>
          <a-descriptions-item label="平均置信度">
            {{ (currentAlert.detection_info.avg_confidence * 100).toFixed(1) }}%
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ formatDate(currentAlert.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="用户">
            {{ currentAlert.user_name }}
          </a-descriptions-item>
        </a-descriptions>

        <!-- 检测结果图片对比 -->
        <div v-if="currentAlert.detection_info.detection_type === 'image'" class="image-comparison">
          <h4>检测结果对比</h4>
          <a-row :gutter="16">
            <a-col :span="12">
              <div class="image-container">
                <h5>原图</h5>
                <a-image
                  :src="getImageUrl(currentAlert.detection_info.original_filename)"
                  :alt="currentAlert.detection_info.original_filename"
                  class="comparison-image"
                  :preview="{
                    mask: '点击放大',
                    zIndex: 10002,
                  }"
                  @error="handleImageError"
                  :fallback="'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5Zu+54mH5Yqg6L295aSx6LSlPC90ZXh0Pjwvc3ZnPg=='"
                />
              </div>
            </a-col>
            <a-col :span="12">
              <div class="image-container">
                <h5>检测结果</h5>
                <a-image
                  :src="getImageUrl(currentAlert.detection_info.result_filename)"
                  :alt="currentAlert.detection_info.result_filename"
                  class="comparison-image"
                  :preview="{
                    mask: '点击放大',
                    zIndex: 10002,
                  }"
                  @error="handleImageError"
                  :fallback="'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5Zu+54mH5Yqg6L295aSx6LSlPC90ZXh0Pjwvc3ZnPg=='"
                />
              </div>
            </a-col>
          </a-row>
        </div>
      </div>
    </a-modal>

    <!-- 批量处理弹窗 -->
    <a-modal
      v-model:visible="batchProcessModalVisible"
      title="批量处理告警"
      @ok="confirmBatchProcess"
      @cancel="batchProcessModalVisible = false"
    >
      <div class="batch-process-content">
        <p>
          已选择 <strong>{{ selectedRowKeys.length }}</strong> 条告警记录
        </p>
        <a-radio-group v-model:value="batchProcessStatus">
          <a-radio value="is_confirm">
            <CheckCircleOutlined />
            标记为已处理
          </a-radio>
          <a-radio value="false_positive">
            <CloseCircleOutlined />
            标记为误报
          </a-radio>
        </a-radio-group>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import {
  BellOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  EyeOutlined,
  CheckOutlined,
  DownOutlined,
  UndoOutlined,
  FileOutlined,
} from '@ant-design/icons-vue';
import { alertApi, AlertRecord } from '@/api/yolo';
import { getFullFileUrl } from '@/utils/hertz_url';
import dayjs from 'dayjs';

// 响应式数据
const loading = ref(false);
const alerts = ref<AlertRecord[]>([]);
const currentAlert = ref<AlertRecord | null>(null);
const detailModalVisible = ref(false);
const batchProcessModalVisible = ref(false);
const searchKeyword = ref('');
const statusFilter = ref('');
const levelFilter = ref('');
const selectedRowKeys = ref<number[]>([]);
const batchProcessStatus = ref('is_confirm');

// 分页状态
const paginationState = reactive({
  current: 1,
  pageSize: 10,
});

// 分页配置
const pagination = computed(() => ({
  current: paginationState.current,
  pageSize: paginationState.pageSize,
  total: filteredAlerts.value.length,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`,
  onChange: (page: number, pageSize: number) => {
    console.log('📄 分页变化:', { page, pageSize });
    paginationState.current = page;
    paginationState.pageSize = pageSize;
  },
  onShowSizeChange: (current: number, size: number) => {
    console.log('📄 页面大小变化:', { current, size });
    paginationState.current = 1;
    paginationState.pageSize = size;
  },
}));

// 行选择配置
const rowSelection = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys: number[]) => {
    selectedRowKeys.value = keys;
    console.log('📋 选择的行:', keys);
  },
};

// 表格列配置
const columns = [
  {
    title: '告警等级',
    key: 'alert_level',
    width: 100,
  },
  {
    title: '告警类别',
    key: 'alert_category',
    width: 150,
  },
  {
    title: '检测信息',
    key: 'detection_info',
    width: 200,
  },
  {
    title: '用户',
    key: 'user_name',
    width: 100,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 150,
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
  },
];

// 计算属性
const totalAlerts = computed(() => alerts.value.length);
const pendingAlerts = computed(
  () => alerts.value.filter((alert) => alert.status === 'pending').length
);
const confirmedAlerts = computed(
  () => alerts.value.filter((alert) => alert.status === 'is_confirm').length
);
const falsePositiveAlerts = computed(
  () => alerts.value.filter((alert) => alert.status === 'false_positive').length
);

// 过滤后的告警数据（不分页）
const filteredAlerts = computed(() => {
  let filtered = alerts.value;

  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter((alert) => alert.status === statusFilter.value);
  }

  // 等级筛选
  if (levelFilter.value) {
    filtered = filtered.filter((alert) => alert.alert_level === levelFilter.value);
  }

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    filtered = filtered.filter(
      (alert) =>
        alert.alert_category.toLowerCase().includes(keyword) ||
        alert.detection_info.original_filename.toLowerCase().includes(keyword) ||
        alert.alert_level_display.toLowerCase().includes(keyword) ||
        alert.user_name.toLowerCase().includes(keyword)
    );
  }

  return filtered;
});

// 分页后的告警数据
const paginatedAlerts = computed(() => {
  const start = (paginationState.current - 1) * paginationState.pageSize;
  const end = start + paginationState.pageSize;
  return filteredAlerts.value.slice(start, end);
});

// 获取告警等级颜色
const getAlertLevelColor = (level: string) => {
  const colorMap = {
    high: 'red',
    medium: 'orange',
    low: 'green',
  };
  return colorMap[level] || 'default';
};

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colorMap = {
    pending: 'orange',
    is_confirm: 'green',
    false_positive: 'red',
  };
  return colorMap[status] || 'default';
};

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap = {
    pending: '待处理',
    is_confirm: '已处理',
    false_positive: '误报',
  };
  return textMap[status] || status;
};

// 格式化日期
const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss');
};

// 获取图片URL
const getImageUrl = (filePath: string) => {
  if (!filePath) {
    console.warn('⚠️ 文件路径为空');
    return '';
  }

  // 后端现在返回的已经是完整的相对路径
  const normalizedPath = filePath.startsWith('/') ? filePath : `/${filePath}`;
  const fullUrl = getFullFileUrl(normalizedPath);
  console.log('🖼️ 构建图片URL:', { filePath, normalizedPath, fullUrl });
  return fullUrl;
};

// 处理图片加载错误
const handleImageError = (event: Event) => {
  console.warn('⚠️ 图片加载失败:', event);
};

// 获取所有告警列表
const fetchAlerts = async () => {
  try {
    loading.value = true;
    console.log('🔍 获取所有告警记录...');

    const response = await alertApi.getAllAlerts();
    console.log('📋 告警记录API响应:', response);

    if (response.success && response.data) {
      alerts.value = response.data;
      console.log('✅ 告警记录获取成功:', alerts.value.length, '条');
    } else {
      console.error('❌ 获取告警记录失败:', response.message);
      message.error(response.message || '获取告警记录失败');
    }
  } catch (error) {
    console.error('❌ 获取告警记录异常:', error);
    message.error('获取告警记录失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

// 刷新告警列表
const refreshAlerts = () => {
  fetchAlerts();
};

// 查看告警详情
const viewAlertDetail = (alert: AlertRecord) => {
  console.log('🔍 查看告警详情:', alert.id);
  currentAlert.value = alert;
  detailModalVisible.value = true;
};

// 处理单个告警
const handleProcessAlert = async (alert: AlertRecord, status: string) => {
  try {
    console.log('🔍 处理告警:', { alertId: alert.id, status });

    const response = await alertApi.updateAlertStatus(alert.id.toString(), status);
    console.log('📋 更新告警状态API响应:', response);

    if (response.success) {
      message.success(`告警已${getStatusText(status)}`);
      // 更新本地数据
      const index = alerts.value.findIndex((a) => a.id === alert.id);
      if (index !== -1) {
        alerts.value[index].status = status;
      }
    } else {
      console.error('❌ 处理告警失败:', response.message);
      message.error(response.message || '处理告警失败');
    }
  } catch (error) {
    console.error('❌ 处理告警异常:', error);
    message.error('处理告警失败，请检查网络连接');
  }
};

// 重置告警状态
const resetAlertStatus = async (alert: AlertRecord) => {
  try {
    console.log('🔄 重置告警状态:', alert.id);

    const response = await alertApi.updateAlertStatus(alert.id.toString(), 'pending');
    console.log('📋 重置告警状态API响应:', response);

    if (response.success) {
      message.success('告警状态已重置为待处理');
      // 更新本地数据
      const index = alerts.value.findIndex((a) => a.id === alert.id);
      if (index !== -1) {
        alerts.value[index].status = 'pending';
      }
    } else {
      console.error('❌ 重置告警状态失败:', response.message);
      message.error(response.message || '重置告警状态失败');
    }
  } catch (error) {
    console.error('❌ 重置告警状态异常:', error);
    message.error('重置告警状态失败，请检查网络连接');
  }
};

// 批量处理
const batchProcess = () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要处理的告警记录');
    return;
  }
  batchProcessModalVisible.value = true;
};

// 确认批量处理
const confirmBatchProcess = async () => {
  try {
    console.log('🔍 批量处理告警:', {
      selectedIds: selectedRowKeys.value,
      status: batchProcessStatus.value,
    });

    const promises = selectedRowKeys.value.map((id) =>
      alertApi.updateAlertStatus(id.toString(), batchProcessStatus.value)
    );

    const results = await Promise.all(promises);
    const successCount = results.filter((r) => r.success).length;

    if (successCount === selectedRowKeys.value.length) {
      message.success(`成功处理 ${successCount} 条告警记录`);
      // 更新本地数据
      selectedRowKeys.value.forEach((id) => {
        const index = alerts.value.findIndex((a) => a.id === id);
        if (index !== -1) {
          alerts.value[index].status = batchProcessStatus.value;
        }
      });
      selectedRowKeys.value = [];
    } else {
      message.warning(
        `处理完成，成功 ${successCount} 条，失败 ${selectedRowKeys.value.length - successCount} 条`
      );
    }

    batchProcessModalVisible.value = false;
  } catch (error) {
    console.error('❌ 批量处理异常:', error);
    message.error('批量处理失败，请检查网络连接');
  }
};

// 处理状态筛选
const handleStatusFilter = () => {
  paginationState.current = 1;
  console.log('🔍 状态筛选变化，重置到第一页');
};

// 处理等级筛选
const handleLevelFilter = () => {
  paginationState.current = 1;
  console.log('🔍 等级筛选变化，重置到第一页');
};

// 处理搜索
const handleSearch = () => {
  paginationState.current = 1;
  console.log('🔍 搜索条件变化，重置到第一页');
};

// 组件挂载时获取数据
onMounted(() => {
  fetchAlerts();
});
</script>

<style scoped lang="scss">
.alert-processing-center {
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
      justify-content: flex-start;
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

  // 统计卡片 - 毛玻璃卡片
  .stats-cards {
    margin: 0 28px 24px 28px;

    :deep(.ant-card.stat-card) {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      border: 0.5px solid rgba(0, 0, 0, 0.08);
      border-radius: 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      text-align: center;

      &:hover {
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
        border-color: rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
      }

      .ant-statistic-title {
        color: #86868b;
      }

      .ant-statistic-content {
        font-weight: 700;
        letter-spacing: -0.2px;
      }
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

        &:not(.ant-btn-primary) {
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
    }

    .action-right {
      display: flex;
      align-items: center;

      .ant-select {
        margin-right: 8px;
        .ant-select-selector {
          border-radius: 10px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          height: 40px;

          &:hover {
            border-color: #3b82f6;
          }
        }
      }

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

  // 列表卡片与表格 - 苹果风格
  .alerts-card {
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

    .alerts-table {
      .detection-info {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .detection-image {
          :deep(.ant-image) {
            .ant-image-img {
              width: 80px;
              height: 60px;
              object-fit: cover;
              border-radius: 8px;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
              cursor: pointer;
              transition: all 0.3s ease;
              &:hover {
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                transform: scale(1.05);
              }
            }
            .ant-image-mask {
              border-radius: 8px;
            }
          }
        }

        .detection-stats {
          display: flex;
          gap: 8px;
          font-size: 12px;
          color: #86868b;
          flex-wrap: wrap;
          span {
            white-space: nowrap;
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
    }
  }

  // 详情
  .alert-detail {
    :deep(.ant-descriptions-item-label) {
      font-weight: 500;
      color: #1d1d1f;
      background: rgba(0, 0, 0, 0.02);
    }
    :deep(.ant-descriptions-item-content) {
      color: #86868b;
    }

    .image-comparison {
      margin-top: 24px;
      h4 {
        margin-bottom: 16px;
        color: #1d1d1f;
        font-weight: 600;
      }
      .image-container {
        text-align: center;
        h5 {
          margin-bottom: 8px;
          color: #86868b;
        }
        .comparison-image {
          width: 100%;
          max-width: 300px;
          max-height: 200px;
          object-fit: contain;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          background: rgba(255, 255, 255, 0.8);
        }
      }
    }
  }

  // 批量处理弹窗内容
  .batch-process-content {
    p {
      margin-bottom: 16px;
      font-size: 16px;
    }
    .ant-radio-group {
      display: flex;
      flex-direction: column;
      gap: 12px;
      .ant-radio-wrapper {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 12px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
        border-radius: 10px;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        background: rgba(255, 255, 255, 0.8);
        &:hover {
          border-color: #3b82f6;
          background: rgba(255, 255, 255, 1);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
          transform: translateY(-1px);
        }
      }
    }
  }

  // 标签样式
  :deep(.ant-tag) {
    border-radius: 6px;
    font-weight: 500;
    padding: 2px 10px;
    border: 0.5px solid currentColor;
    opacity: 0.85;
  }

  // 分页器 - 苹果风格
  :deep(.ant-pagination) {
    margin: 20px 0;
    padding: 16px 0;
    text-align: center;
    background: rgba(0, 0, 0, 0.02);
    border-top: 0.5px solid rgba(0, 0, 0, 0.08);

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
        a {
          color: #fff;
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
        &:hover {
          border-color: #3b82f6;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .alert-processing-center {
    .page-header {
      padding: 24px 16px;
    }
    .action-bar {
      margin: 0 16px 20px 16px;
      padding: 16px;
      flex-direction: column;
      align-items: stretch;
      .action-right {
        width: 100%;
        justify-content: space-between;
      }
    }
    .alerts-card {
      margin: 0 16px 20px 16px;
      border-radius: 12px;
    }
    .alerts-table .action-buttons {
      flex-direction: column;
      gap: 6px;
    }
  }
}
</style>
