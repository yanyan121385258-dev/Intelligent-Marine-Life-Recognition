<template>
  <div class="detection-history-management">
    <div class="page-header">
      <h2 class="page-title">
        <HistoryOutlined class="title-icon" />
        检测历史管理
      </h2>
      <p class="page-description">管理所有用户的YOLO检测历史记录</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="总检测次数"
              :value="stats.total_detections"
              :value-style="{ color: '#3f8600' }"
            >
              <template #prefix>
                <ScanOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="图片检测"
              :value="stats.image_detections"
              :value-style="{ color: '#1890ff' }"
            >
              <template #prefix>
                <FileImageOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="视频检测"
              :value="stats.video_detections"
              :value-style="{ color: '#722ed1' }"
            >
              <template #prefix>
                <PlayCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="最近检测"
              :value="stats.recent_detections"
              :value-style="{ color: '#fa8c16' }"
            >
              <template #prefix>
                <ClockCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <a-button @click="refreshHistory">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
        <a-button
          type="primary"
          danger
          :disabled="selectedRowKeys.length === 0"
          @click="showBatchDeleteConfirm"
        >
          <template #icon>
            <DeleteOutlined />
          </template>
          批量删除 ({{ selectedRowKeys.length }})
        </a-button>
      </div>
      <div class="action-right">
        <a-range-picker
          v-model:value="dateRange"
          @change="handleDateRangeChange"
          style="margin-right: 12px"
        />
        <a-select
          v-model:value="selectedModel"
          placeholder="选择模型"
          style="width: 150px; margin-right: 12px"
          allow-clear
          @change="handleModelChange"
        >
          <a-select-option value="">全部模型</a-select-option>
          <a-select-option v-for="model in models" :key="model.id" :value="model.id">
            {{ model.name }}
          </a-select-option>
        </a-select>
        <a-input-search
          v-model:value="searchKeyword"
          placeholder="搜索文件名或用户"
          style="width: 250px"
          @search="handleSearch"
        />
      </div>
    </div>

    <!-- 历史记录表格 -->
    <a-table
      :columns="columns"
      :data-source="paginatedRecords"
      :loading="loading"
      :pagination="pagination"
      :row-selection="rowSelection"
      row-key="id"
      class="history-table"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'file_info'">
          <div class="file-info">
            <div class="file-icon">
              <FileImageOutlined v-if="record.detection_type === 'image'" />
              <PlayCircleOutlined v-else />
            </div>
            <div class="file-details">
              <div class="filename">{{ record.original_filename }}</div>
              <div class="file-type">{{ record.detection_type === 'image' ? '图片' : '视频' }}</div>
            </div>
          </div>
        </template>

        <template v-if="column.key === 'detection_results'">
          <div class="detection-results">
            <div class="object-count">
              <a-tag color="blue">{{ record.object_count }} 个目标</a-tag>
            </div>
            <div class="categories">
              <a-tag
                v-for="category in record.detected_categories"
                :key="category"
                color="green"
                size="small"
              >
                {{ category }}
              </a-tag>
            </div>
          </div>
        </template>

        <template v-if="column.key === 'model_info'">
          <div class="model-info">
            <div class="model-name">{{ record.model_name }}</div>
            <div class="model-version" v-if="record.model_info">
              v{{ record.model_info.version }}
            </div>
          </div>
        </template>

        <template v-if="column.key === 'performance'">
          <div class="performance">
            <div class="processing-time">
              <ClockCircleOutlined />
              {{ record.processing_time }}s
            </div>
            <div class="confidence">
              <AimOutlined />
              {{ record.avg_confidence ? (record.avg_confidence * 100).toFixed(1) + '%' : '-' }}
            </div>
          </div>
        </template>

        <template v-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>

        <template v-if="column.key === 'actions'">
          <div class="action-buttons">
            <a-button size="small" @click="viewDetails(record)">
              <template #icon>
                <EyeOutlined />
              </template>
              查看详情
            </a-button>
            <a-popconfirm title="确定要删除这条记录吗？" @confirm="deleteRecord(record)">
              <a-button size="small" danger>
                <template #icon>
                  <DeleteOutlined />
                </template>
                删除
              </a-button>
            </a-popconfirm>
          </div>
        </template>
      </template>
    </a-table>

    <!-- 详情弹窗 -->
    <a-modal
      v-model:visible="detailModalVisible"
      title="检测详情"
      :footer="null"
      width="1200px"
      :centered="true"
    >
      <div v-if="currentRecord" class="detection-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="文件名">
            {{ currentRecord.original_filename }}
          </a-descriptions-item>
          <a-descriptions-item label="检测类型">
            <a-tag :color="currentRecord.detection_type === 'image' ? 'blue' : 'purple'">
              {{ currentRecord.detection_type === 'image' ? '图片' : '视频' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="使用模型">
            {{ currentRecord.model_name }}
          </a-descriptions-item>
          <a-descriptions-item label="检测时间">
            {{ formatDate(currentRecord.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="目标数量">
            {{ currentRecord.object_count }} 个
          </a-descriptions-item>
          <a-descriptions-item label="处理时间">
            {{ currentRecord.processing_time }} 秒
          </a-descriptions-item>
          <a-descriptions-item label="置信度阈值">
            {{
              currentRecord.avg_confidence
                ? (currentRecord.avg_confidence * 100).toFixed(1) + '%'
                : '-'
            }}
          </a-descriptions-item>
          <a-descriptions-item label="检测类别" :span="2">
            <div class="categories">
              <a-tag
                v-for="category in currentRecord.detected_categories"
                :key="category"
                color="green"
              >
                {{ category }}
              </a-tag>
            </div>
          </a-descriptions-item>
        </a-descriptions>

        <!-- 图片对比 -->
        <div class="image-comparison" v-if="currentRecord.detection_type === 'image'">
          <h4>检测结果对比</h4>
          <div
            class="images-container"
            style="display: flex; flex-direction: row; gap: 20px; width: 100%"
          >
            <div class="image-section" style="width: 45%; flex: 0 0 45%">
              <h5>原图</h5>
              <div
                class="image-wrapper"
                style="
                  width: 100%;
                  height: 200px;
                  border: 1px solid #e5e7eb;
                  border-radius: 8px;
                  overflow: hidden;
                  background: #f8fafc;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  cursor: pointer;
                "
              >
                <img
                  :src="getImageUrl(currentRecord.original_file)"
                  :alt="currentRecord.original_filename"
                  @error="handleImageError"
                  @click="previewImage(getImageUrl(currentRecord.original_file))"
                  style="
                    max-width: 100%;
                    max-height: 100%;
                    width: auto;
                    height: auto;
                    object-fit: contain;
                    display: block;
                  "
                />
              </div>
            </div>
            <div class="image-section" style="width: 45%; flex: 0 0 45%">
              <h5>检测结果</h5>
              <div
                class="image-wrapper"
                style="
                  width: 100%;
                  height: 200px;
                  border: 1px solid #e5e7eb;
                  border-radius: 8px;
                  overflow: hidden;
                  background: #f8fafc;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  cursor: pointer;
                "
              >
                <img
                  :src="getImageUrl(currentRecord.result_file)"
                  :alt="currentRecord.result_filename"
                  @error="handleImageError"
                  @click="previewImage(getImageUrl(currentRecord.result_file))"
                  style="
                    max-width: 100%;
                    max-height: 100%;
                    width: auto;
                    height: auto;
                    object-fit: contain;
                    display: block;
                  "
                />
              </div>
            </div>
          </div>
        </div>

        <!-- 视频对比 -->
        <div class="video-comparison" v-if="currentRecord.detection_type === 'video'">
          <h4>检测结果对比</h4>
          <div
            class="videos-container"
            style="display: flex; flex-direction: row; gap: 20px; width: 100%"
          >
            <div class="video-section" style="width: 45%; flex: 0 0 45%">
              <h5>原视频</h5>
              <div
                class="video-wrapper"
                style="
                  width: 100%;
                  height: 250px;
                  border: 1px solid #e5e7eb;
                  border-radius: 8px;
                  overflow: hidden;
                  background: #f8fafc;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                "
              >
                <video
                  :src="getImageUrl(currentRecord.original_file)"
                  controls
                  style="max-width: 100%; max-height: 100%; width: auto; height: auto"
                  @error="handleVideoError"
                >
                  您的浏览器不支持视频播放
                </video>
              </div>
            </div>
            <div class="video-section" style="width: 45%; flex: 0 0 45%">
              <h5>检测结果</h5>
              <div
                class="video-wrapper"
                style="
                  width: 100%;
                  height: 250px;
                  border: 1px solid #e5e7eb;
                  border-radius: 8px;
                  overflow: hidden;
                  background: #f8fafc;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                "
              >
                <video
                  :src="getImageUrl(currentRecord.result_file)"
                  controls
                  style="max-width: 100%; max-height: 100%; width: auto; height: auto"
                  @error="handleVideoError"
                >
                  您的浏览器不支持视频播放
                </video>
              </div>
            </div>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import {
  HistoryOutlined,
  ScanOutlined,
  FileImageOutlined,
  PlayCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  AimOutlined,
} from '@ant-design/icons-vue';
import { yoloApi, type DetectionHistoryRecord, type YoloModel } from '@/api/yolo';
import dayjs from 'dayjs';
import { getFullFileUrl } from '@/utils/hertz_url';

// 响应式数据
const loading = ref(false);
const records = ref<DetectionHistoryRecord[]>([]);
const models = ref<YoloModel[]>([]);
const searchKeyword = ref('');
const dateRange = ref<[dayjs.Dayjs, dayjs.Dayjs] | null>(null);
const selectedModel = ref('');
const selectedRowKeys = ref<number[]>([]);

// 弹窗状态
const detailModalVisible = ref(false);
const currentRecord = ref<DetectionHistoryRecord | null>(null);

// 统计数据
const stats = ref({
  total_detections: 0,
  image_detections: 0,
  video_detections: 0,
  recent_detections: 0,
});

// 分页状态
const paginationState = reactive({
  current: 1,
  pageSize: 10,
});

// 分页配置
const pagination = computed(() => ({
  current: paginationState.current,
  pageSize: paginationState.pageSize,
  total: filteredRecords.value.length,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`,
  onChange: (page: number, size: number) => {
    paginationState.current = page;
    paginationState.pageSize = size;
  },
  onShowSizeChange: (current: number, size: number) => {
    paginationState.current = 1;
    paginationState.pageSize = size;
  },
}));

// 表格列配置
const columns = [
  {
    title: '文件信息',
    key: 'file_info',
    width: 200,
  },
  {
    title: '检测结果',
    key: 'detection_results',
    width: 250,
  },
  {
    title: '使用模型',
    key: 'model_info',
    width: 150,
  },
  {
    title: '性能指标',
    key: 'performance',
    width: 150,
  },
  {
    title: '检测时间',
    key: 'created_at',
    width: 150,
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
  },
];

// 行选择配置
const rowSelection = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys: number[]) => {
    selectedRowKeys.value = keys;
  },
};

// 过滤后的记录列表
const filteredRecords = computed(() => {
  let filtered = records.value;

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    filtered = filtered.filter(
      (record) =>
        record.original_filename.toLowerCase().includes(keyword) ||
        record.model_name.toLowerCase().includes(keyword)
    );
  }

  // 模型过滤
  if (selectedModel.value) {
    filtered = filtered.filter((record) => record.model_info?.id === selectedModel.value);
  }

  // 日期过滤
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value;
    filtered = filtered.filter((record) => {
      const recordDate = dayjs(record.created_at);
      return recordDate.isAfter(start) && recordDate.isBefore(end);
    });
  }

  return filtered;
});

// 分页后的记录列表
const paginatedRecords = computed(() => {
  const start = (paginationState.current - 1) * paginationState.pageSize;
  const end = start + paginationState.pageSize;
  return filteredRecords.value.slice(start, end);
});

// 格式化日期
const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss');
};

// 获取图片URL
const getImageUrl = (filePath: string) => {
  if (!filePath) return '';
  return getFullFileUrl(filePath);
};

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.src = '/placeholder-image.png';
};

// 处理视频加载错误
const handleVideoError = (event: Event) => {
  const video = event.target as HTMLVideoElement;
  console.error('视频加载失败:', video.src);
  // 可以在这里添加错误提示
};

// 图片预览功能
const previewImage = (imageUrl: string) => {
  if (!imageUrl) return;

  // 创建预览弹窗
  const previewModal = document.createElement('div');
  previewModal.className = 'image-preview-modal';
  previewModal.innerHTML = `
    <div class="preview-overlay">
      <div class="preview-container">
        <div class="preview-header">
          <span class="preview-title">图片预览</span>
          <button class="preview-close" onclick="this.closest('.image-preview-modal').remove()">×</button>
        </div>
        <div class="preview-content">
          <img src="${imageUrl}" alt="预览图片" class="preview-image" />
        </div>
      </div>
    </div>
  `;

  // 添加样式
  const style = document.createElement('style');
  style.textContent = `
    .image-preview-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 2000;
    }
    .preview-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .preview-container {
      background: white;
      border-radius: 8px;
      max-width: 90vw;
      max-height: 90vh;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .preview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid #e8e8e8;
      background: #fafafa;
    }
    .preview-title {
      font-weight: 600;
      color: #333;
    }
    .preview-close {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: #666;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
    }
    .preview-close:hover {
      background: #f0f0f0;
      color: #333;
    }
    .preview-content {
      padding: 16px;
      text-align: center;
    }
    .preview-image {
      max-width: 100%;
      max-height: 70vh;
      object-fit: contain;
      border-radius: 4px;
    }
  `;

  document.head.appendChild(style);
  document.body.appendChild(previewModal);

  // 点击遮罩层关闭
  previewModal.addEventListener('click', (e) => {
    if (e.target === previewModal || e.target === previewModal.querySelector('.preview-overlay')) {
      previewModal.remove();
      style.remove();
    }
  });

  // ESC键关闭
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      previewModal.remove();
      style.remove();
      document.removeEventListener('keydown', handleKeyDown);
    }
  };
  document.addEventListener('keydown', handleKeyDown);
};

// 获取历史记录列表
const fetchHistory = async () => {
  try {
    loading.value = true;
    console.log('🔍 开始获取检测历史记录...');

    // 获取所有历史记录（不分页）
    const response = await yoloApi.getDetectionHistory({
      page: 1,
      page_size: 1000, // 获取大量数据，由前端进行分页
    });
    console.log('📋 历史记录API响应:', response);

    if (response.success && response.data) {
      records.value = response.data;
      console.log('✅ 历史记录获取成功:', records.value);
    } else {
      console.error('❌ 获取历史记录失败:', response.message);
      message.error(response.message || '获取历史记录失败');
    }
  } catch (error) {
    console.error('❌ 获取历史记录异常:', error);
    message.error('获取历史记录失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await yoloApi.getDetectionStats();
    if (response.success && response.data) {
      stats.value = response.data;
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

// 获取模型列表
const fetchModels = async () => {
  try {
    const response = await yoloApi.getModels();
    if (response.success && response.data) {
      models.value = response.data;
    }
  } catch (error) {
    console.error('获取模型列表失败:', error);
  }
};

// 刷新历史记录
const refreshHistory = () => {
  fetchHistory();
  fetchStats();
};

// 查看详情
const viewDetails = (record: DetectionHistoryRecord) => {
  currentRecord.value = record;
  detailModalVisible.value = true;
};

// 删除记录
const deleteRecord = async (record: DetectionHistoryRecord) => {
  try {
    const response = await yoloApi.deleteDetection(record.id.toString());
    if (response.success) {
      message.success('记录删除成功');
      fetchHistory();
    } else {
      message.error(response.message || '删除失败');
    }
  } catch (error) {
    console.error('删除记录失败:', error);
    message.error('删除失败');
  }
};

// 批量删除确认
const showBatchDeleteConfirm = () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要删除的记录');
    return;
  }

  message.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 条记录吗？`,
    onOk: handleBatchDelete,
  });
};

// 批量删除
const handleBatchDelete = async () => {
  try {
    const response = await yoloApi.batchDeleteDetections(selectedRowKeys.value);
    if (response.success) {
      message.success(`成功删除 ${selectedRowKeys.value.length} 条记录`);
      selectedRowKeys.value = [];
      fetchHistory();
    } else {
      message.error(response.message || '批量删除失败');
    }
  } catch (error) {
    console.error('批量删除失败:', error);
    message.error('批量删除失败');
  }
};

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
  // 重置分页到第一页
  paginationState.current = 1;
};

// 日期范围变化
const handleDateRangeChange = () => {
  // 日期过滤逻辑已在computed中处理
  // 重置分页到第一页
  paginationState.current = 1;
};

// 模型选择变化
const handleModelChange = () => {
  // 模型过滤逻辑已在computed中处理
  // 重置分页到第一页
  paginationState.current = 1;
};

// 组件挂载时获取数据
onMounted(() => {
  fetchHistory();
  fetchStats();
  fetchModels();
});
</script>

<style scoped lang="scss">
.detection-history-management {
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
        background: rgba(16, 185, 129, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        color: #10b981;
        font-size: 24px;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(16, 185, 129, 0.15);
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

  // 统计卡片 - 毛玻璃
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

      :deep(.ant-picker) {
        border-radius: 10px;
      }

      .ant-select {
        margin-right: 12px;
      }
      .ant-select .ant-select-selector {
        border-radius: 10px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        height: 40px;
        &:hover {
          border-color: #3b82f6;
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

  // 表格容器 - 苹果风格
  .history-table {
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

    .file-info {
      display: flex;
      align-items: center;
      .file-icon {
        font-size: 22px;
        color: #3b82f6;
        margin-right: 12px;
      }
      .file-details {
        .filename {
          font-weight: 600;
          color: #1d1d1f;
          margin-bottom: 2px;
        }
        .file-type {
          font-size: 12px;
          color: #86868b;
        }
      }
    }

    .detection-results {
      .object-count {
        margin-bottom: 8px;
      }
      .categories {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
      }
    }

    .model-info {
      .model-name {
        font-weight: 600;
        color: #1d1d1f;
        margin-bottom: 2px;
      }
      .model-version {
        font-size: 12px;
        color: #86868b;
      }
    }

    .performance {
      .processing-time,
      .confidence {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #86868b;
        margin-bottom: 4px;
      }
    }

    .action-buttons {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
  }

  // 详情区
  .detection-detail {
    :deep(.ant-descriptions-item-label) {
      font-weight: 500;
      color: #1d1d1f;
      background: rgba(0, 0, 0, 0.02);
    }
    :deep(.ant-descriptions-item-content) {
      color: #86868b;
    }

    .categories {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .image-comparison,
    .video-comparison {
      margin-top: 24px;
      h4 {
        margin-bottom: 16px;
        color: #1d1d1f;
        font-weight: 600;
      }
      .image-section,
      .video-section {
        width: 45% !important;
        flex: 0 0 45% !important;
        text-align: center;
        h5 {
          margin-bottom: 10px;
          color: #86868b;
          font-size: 14px;
          font-weight: 600;
        }
        .image-wrapper,
        .video-wrapper {
          width: 100%;
          height: 220px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          border-radius: 12px;
          overflow: hidden;
          background: rgba(255, 255, 255, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          &:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
          }
          img,
          video {
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
            display: block;
            border-radius: 6px;
          }
        }
      }
    }
  }

  // 标签统一
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

// 响应式
@media (max-width: 768px) {
  .detection-history-management {
    .page-header {
      padding: 24px 16px;
    }
    .stats-cards,
    .action-bar,
    .history-table {
      margin: 0 16px 20px 16px;
    }
    .history-table {
      border-radius: 12px;
    }
  }
}
</style>
