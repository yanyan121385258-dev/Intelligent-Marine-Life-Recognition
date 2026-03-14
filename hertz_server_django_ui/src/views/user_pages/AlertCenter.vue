<template>
  <div class="alert-center-page">
    <div class="page-header">
      <h1 class="page-title">
        <BellOutlined class="title-icon" />
        告警中心
      </h1>
      <p class="page-description">查看和管理您的检测告警记录</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <a-row :gutter="16">
        <a-col :xs="24" :sm="8" :md="8" :lg="8" :xl="8">
          <a-card class="stat-card">
            <a-statistic title="总告警数" :value="totalAlerts" :value-style="{ color: '#1890ff' }">
              <template #prefix>
                <BellOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="8" :md="8" :lg="8" :xl="8">
          <a-card class="stat-card">
            <a-statistic
              title="高风险告警"
              :value="highRiskAlerts"
              :value-style="{ color: '#ff4d4f' }"
            >
              <template #prefix>
                <ExclamationCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="8" :md="8" :lg="8" :xl="8">
          <a-card class="stat-card">
            <a-statistic
              title="中等风险告警"
              :value="mediumRiskAlerts"
              :value-style="{ color: '#faad14' }"
            >
              <template #prefix>
                <ExclamationCircleOutlined />
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
      </div>
      <div class="action-right">
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

    <!-- 表格布局 -->
    <a-card v-if="layoutMode === 'table'" class="alerts-card" :key="`table-${layoutKey}`">
      <a-table
        :columns="columns"
        :data-source="paginatedAlerts"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        class="alerts-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'alert_level'">
            <a-tag :color="getAlertLevelColor(record.alert_level)">
              {{ record.alert_level_display }}
            </a-tag>
          </template>

          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>

          <template v-if="column.key === 'detection_info'">
            <div class="detection-info">
              <div class="file-info">
                <FileOutlined />
                <span>{{ record.detection_info.original_filename }}</span>
              </div>
              <div class="detection-stats">
                <span>检测目标: {{ record.detection_info.object_count }}个</span>
                <span>置信度: {{ (record.detection_info.avg_confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>
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
            </div>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 卡片布局 -->
    <div v-else-if="layoutMode === 'card'" class="alerts-card-layout" :key="`card-${layoutKey}`">
      <a-spin :spinning="loading">
        <div class="alerts-card-grid">
          <a-card
            v-for="alert in paginatedAlerts"
            :key="alert.id"
            class="alert-card-item"
            :class="`alert-level-${alert.alert_level}`"
          >
            <div class="card-header">
              <div class="card-title-row">
                <a-tag :color="getAlertLevelColor(alert.alert_level)" class="level-tag">
                  {{ alert.alert_level_display }}
                </a-tag>
                <span class="alert-category">{{ alert.alert_category }}</span>
              </div>
              <a-tag :color="getStatusColor(alert.status)" class="status-tag">
                {{ getStatusText(alert.status) }}
              </a-tag>
            </div>
            <div class="card-content">
              <div class="file-info">
                <FileOutlined />
                <span class="filename">{{ alert.detection_info.original_filename }}</span>
              </div>
              <div class="detection-stats">
                <div class="stat-item">
                  <span class="stat-label">检测目标:</span>
                  <span class="stat-value">{{ alert.detection_info.object_count }}个</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">置信度:</span>
                  <span class="stat-value"
                    >{{ (alert.detection_info.avg_confidence * 100).toFixed(1) }}%</span
                  >
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="card-time">
                <ClockCircleOutlined />
                <span>{{ formatDate(alert.created_at) }}</span>
              </div>
              <a-button size="small" type="primary" @click="viewAlertDetail(alert)">
                <template #icon>
                  <EyeOutlined />
                </template>
                查看详情
              </a-button>
            </div>
          </a-card>
        </div>
        <div class="pagination-wrapper">
          <a-pagination
            v-model:current="paginationState.current"
            v-model:pageSize="paginationState.pageSize"
            :total="filteredAlerts.length"
            :showSizeChanger="true"
            :showQuickJumper="true"
            :showTotal="(total: number) => `共 ${total} 条记录`"
            @change="
              (page: number, pageSize: number) => {
                paginationState.current = page;
                paginationState.pageSize = pageSize;
              }
            "
            @showSizeChange="
              (current: number, size: number) => {
                paginationState.current = 1;
                paginationState.pageSize = size;
              }
            "
          />
        </div>
      </a-spin>
    </div>

    <!-- 时间线布局 -->
    <div
      v-else-if="layoutMode === 'timeline'"
      class="alerts-timeline-layout"
      :key="`timeline-${layoutKey}`"
    >
      <a-spin :spinning="loading">
        <div class="timeline-container">
          <a-timeline>
            <a-timeline-item
              v-for="alert in paginatedAlerts"
              :key="alert.id"
              :color="getAlertLevelColor(alert.alert_level)"
            >
              <a-card class="timeline-card" :class="`alert-level-${alert.alert_level}`">
                <div class="timeline-header">
                  <div class="timeline-title-row">
                    <a-tag :color="getAlertLevelColor(alert.alert_level)" class="level-tag">
                      {{ alert.alert_level_display }}
                    </a-tag>
                    <span class="alert-category">{{ alert.alert_category }}</span>
                    <a-tag :color="getStatusColor(alert.status)" class="status-tag">
                      {{ getStatusText(alert.status) }}
                    </a-tag>
                  </div>
                  <div class="timeline-time">
                    <ClockCircleOutlined />
                    <span>{{ formatDate(alert.created_at) }}</span>
                  </div>
                </div>
                <div class="timeline-content">
                  <div class="file-info">
                    <FileOutlined />
                    <span class="filename">{{ alert.detection_info.original_filename }}</span>
                  </div>
                  <div class="detection-stats">
                    <div class="stat-item">
                      <span class="stat-label">检测目标:</span>
                      <span class="stat-value">{{ alert.detection_info.object_count }}个</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">置信度:</span>
                      <span class="stat-value"
                        >{{ (alert.detection_info.avg_confidence * 100).toFixed(1) }}%</span
                      >
                    </div>
                  </div>
                </div>
                <div class="timeline-actions">
                  <a-button size="small" type="primary" @click="viewAlertDetail(alert)">
                    <template #icon>
                      <EyeOutlined />
                    </template>
                    查看详情
                  </a-button>
                </div>
              </a-card>
            </a-timeline-item>
          </a-timeline>
        </div>
        <div class="pagination-wrapper">
          <a-pagination
            v-model:current="paginationState.current"
            v-model:pageSize="paginationState.pageSize"
            :total="filteredAlerts.length"
            :showSizeChanger="true"
            :showQuickJumper="true"
            :showTotal="(total: number) => `共 ${total} 条记录`"
            @change="
              (page: number, pageSize: number) => {
                paginationState.current = page;
                paginationState.pageSize = pageSize;
              }
            "
            @showSizeChange="
              (current: number, size: number) => {
                paginationState.current = 1;
                paginationState.pageSize = size;
              }
            "
          />
        </div>
      </a-spin>
    </div>

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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import {
  BellOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  EyeOutlined,
  FileOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons-vue';
import { alertApi, type AlertRecord } from '@/api/yolo';
import { useUserStore } from '@/stores/hertz_user';
import { getFullFileUrl } from '@/utils/hertz_url';
import dayjs from 'dayjs';

// 布局模式
const layoutMode = ref<'table' | 'card' | 'timeline'>('table');
const layoutKey = ref(0);

// 加载布局模式
const loadLayout = async () => {
  const saved = localStorage.getItem('alertCenterLayout');
  if (saved && ['table', 'card', 'timeline'].includes(saved)) {
    layoutMode.value = saved as 'table' | 'card' | 'timeline';
  } else {
    layoutMode.value = 'table';
  }
  layoutKey.value++;
  await nextTick();
};

// 监听布局变化事件
const handleLayoutChange = async () => {
  await loadLayout();
};

// 响应式数据
const loading = ref(false);
const alerts = ref<AlertRecord[]>([]);
const currentAlert = ref<AlertRecord | null>(null);
const detailModalVisible = ref(false);
const searchKeyword = ref('');
const levelFilter = ref('');

const userStore = useUserStore();

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

// 分页状态
const paginationState = reactive({
  current: 1,
  pageSize: 10,
});

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
    width: 120,
  },
  {
    title: '检测信息',
    key: 'detection_info',
    width: 200,
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
    width: 150,
  },
];

// 计算属性
const totalAlerts = computed(() => alerts.value.length);
const highRiskAlerts = computed(
  () => alerts.value.filter((alert) => alert.alert_level === 'high').length
);
const mediumRiskAlerts = computed(
  () => alerts.value.filter((alert) => alert.alert_level === 'medium').length
);

// 过滤后的告警数据（不分页）
const filteredAlerts = computed(() => {
  let filtered = alerts.value;

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
        alert.alert_level_display.toLowerCase().includes(keyword)
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
  };
  return colorMap[status] || 'default';
};

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap = {
    pending: '待处理',
    is_confirm: '已确认',
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

  // 后端现在返回的已经是完整的相对路径，如：media/detection/original/xxx.png
  // 需要确保路径以 / 开头
  const normalizedPath = filePath.startsWith('/') ? filePath : `/${filePath}`;
  const fullUrl = getFullFileUrl(normalizedPath);
  console.log('🖼️ 构建图片URL:', { filePath, normalizedPath, fullUrl });
  return fullUrl;
};

// 处理图片加载错误
const handleImageError = (event: Event) => {
  console.warn('⚠️ 图片加载失败:', event);
  // Ant Design的Image组件会自动使用fallback图片
};

// 获取告警列表
const fetchAlerts = async () => {
  if (!userStore.userInfo?.user_id) {
    message.error('用户信息不存在');
    return;
  }

  try {
    loading.value = true;
    console.log('🔍 获取用户告警记录...', userStore.userInfo.user_id);

    const response = await alertApi.getUserAlerts(userStore.userInfo.user_id.toString());
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

// 处理等级筛选
const handleLevelFilter = () => {
  // 筛选条件改变时重置到第一页
  paginationState.current = 1;
  console.log('🔍 等级筛选变化，重置到第一页');
};

// 处理搜索
const handleSearch = () => {
  // 搜索条件改变时重置到第一页
  paginationState.current = 1;
  console.log('🔍 搜索条件变化，重置到第一页');
};

// 组件挂载时获取数据
onMounted(async () => {
  await loadLayout();
  window.addEventListener('alertCenterLayoutChanged', handleLayoutChange);
  fetchAlerts();
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('alertCenterLayoutChanged', handleLayoutChange);
});
</script>

<style scoped lang="scss">
.alert-center-page {
  padding: 24px;
  background: var(--theme-page-bg, #f5f5f5);
  min-height: 100vh;

  .page-header {
    margin-bottom: 24px;
    text-align: center;

    .page-title {
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 0 8px 0;
      font-size: 2rem;
      font-weight: 600;
      color: var(--theme-text-primary, #1e293b);

      .title-icon {
        margin-right: 12px;
        color: var(--theme-primary, #f59e0b);
      }
    }

    .page-description {
      margin: 0;
      color: var(--theme-text-secondary, #64748b);
      font-size: 14px;
    }
  }

  .stats-cards {
    margin-bottom: 24px;

    .stat-card {
      text-align: center;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }

  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding: 16px;
    background: var(--theme-content-bg, #f8fafc);
    border-radius: 8px;
    border: 1px solid #e2e8f0;

    .action-left {
      display: flex;
      gap: 12px;
    }

    .action-right {
      display: flex;
      align-items: center;
    }
  }

  .alerts-card {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    background: var(--theme-card-bg, #ffffff);
    border: 1px solid var(--theme-card-border, #e5e7eb);

    .alerts-table {
      .detection-info {
        .file-info {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 4px;
          font-weight: 500;
          color: var(--theme-text-primary, #1e293b);
        }

        .detection-stats {
          display: flex;
          gap: 12px;
          font-size: 12px;
          color: var(--theme-text-secondary, #64748b);
        }
      }

      .action-buttons {
        display: flex;
        gap: 8px;
      }
    }
  }

  // 卡片布局样式
  .alerts-card-layout {
    .alerts-card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
      margin-bottom: 24px;

      .alert-card-item {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        background: var(--theme-card-bg, #ffffff);
        border: 2px solid var(--theme-card-border, #e5e7eb);
        overflow: hidden;

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
          border-color: var(--theme-primary, #3b82f6);
        }

        &.alert-level-high {
          border-left: 4px solid #ff4d4f;
        }

        &.alert-level-medium {
          border-left: 4px solid #faad14;
        }

        &.alert-level-low {
          border-left: 4px solid #52c41a;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
          background: var(--theme-content-bg, #f8fafc);

          .card-title-row {
            display: flex;
            align-items: center;
            gap: 12px;

            .level-tag {
              font-weight: 600;
            }

            .alert-category {
              font-weight: 600;
              color: var(--theme-text-primary, #1e293b);
            }
          }

          .status-tag {
            font-weight: 500;
          }
        }

        .card-content {
          padding: 16px;

          .file-info {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            font-weight: 500;
            color: var(--theme-text-primary, #1e293b);

            .filename {
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }

          .detection-stats {
            display: flex;
            flex-direction: column;
            gap: 8px;

            .stat-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 8px;
              background: var(--theme-content-bg, #f8fafc);
              border-radius: 6px;

              .stat-label {
                color: var(--theme-text-secondary, #64748b);
                font-size: 14px;
              }

              .stat-value {
                color: var(--theme-text-primary, #1e293b);
                font-weight: 600;
                font-size: 14px;
              }
            }
          }
        }

        .card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-top: 1px solid var(--theme-card-border, #e5e7eb);
          background: var(--theme-content-bg, #f8fafc);

          .card-time {
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--theme-text-secondary, #64748b);
            font-size: 12px;
          }
        }
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 24px;
      padding: 16px;
      background: var(--theme-card-bg, #ffffff);
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }

  // 时间线布局样式
  .alerts-timeline-layout {
    .timeline-container {
      padding: 24px;
      background: var(--theme-card-bg, #ffffff);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      margin-bottom: 24px;

      .timeline-card {
        margin-left: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        background: var(--theme-card-bg, #ffffff);
        border: 2px solid var(--theme-card-border, #e5e7eb);
        transition: all 0.3s ease;

        &:hover {
          transform: translateX(4px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          border-color: var(--theme-primary, #3b82f6);
        }

        &.alert-level-high {
          border-left: 4px solid #ff4d4f;
        }

        &.alert-level-medium {
          border-left: 4px solid #faad14;
        }

        &.alert-level-low {
          border-left: 4px solid #52c41a;
        }

        .timeline-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
          background: var(--theme-content-bg, #f8fafc);

          .timeline-title-row {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;

            .level-tag {
              font-weight: 600;
            }

            .alert-category {
              font-weight: 600;
              color: var(--theme-text-primary, #1e293b);
            }

            .status-tag {
              font-weight: 500;
            }
          }

          .timeline-time {
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--theme-text-secondary, #64748b);
            font-size: 12px;
          }
        }

        .timeline-content {
          padding: 16px;

          .file-info {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            font-weight: 500;
            color: var(--theme-text-primary, #1e293b);

            .filename {
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }

          .detection-stats {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;

            .stat-item {
              display: flex;
              align-items: center;
              gap: 8px;
              padding: 8px 12px;
              background: var(--theme-content-bg, #f8fafc);
              border-radius: 6px;

              .stat-label {
                color: var(--theme-text-secondary, #64748b);
                font-size: 14px;
              }

              .stat-value {
                color: var(--theme-text-primary, #1e293b);
                font-weight: 600;
                font-size: 14px;
              }
            }
          }
        }

        .timeline-actions {
          padding: 16px;
          border-top: 1px solid var(--theme-card-border, #e5e7eb);
          background: var(--theme-content-bg, #f8fafc);
        }
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 24px;
      padding: 16px;
      background: var(--theme-card-bg, #ffffff);
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }

  .alert-detail {
    .image-comparison {
      margin-top: 24px;

      h4 {
        margin-bottom: 16px;
        color: var(--theme-text-primary, #1e293b);
      }

      .image-container {
        text-align: center;

        h5 {
          margin-bottom: 8px;
          color: var(--theme-text-secondary, #64748b);
        }

        .comparison-image {
          width: 100%;
          max-width: 300px;
          max-height: 200px;
          object-fit: contain;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          background: var(--theme-content-bg, #fafafa);

          // 优化图片加载性能
          image-rendering: -webkit-optimize-contrast;
          image-rendering: crisp-edges;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .alert-center-page {
    padding: 16px;

    .action-bar {
      flex-direction: column;
      gap: 12px;

      .action-right {
        width: 100%;
        justify-content: space-between;
      }
    }

    .alerts-table {
      .action-buttons {
        flex-direction: column;
        gap: 4px;
      }
    }

    // 卡片布局响应式
    .alerts-card-layout {
      .alerts-card-grid {
        grid-template-columns: 1fr;
        gap: 16px;
      }
    }

    // 时间线布局响应式
    .alerts-timeline-layout {
      .timeline-container {
        padding: 16px;

        .timeline-card {
          margin-left: 8px;

          .timeline-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }
        }
      }
    }
  }
}
</style>
