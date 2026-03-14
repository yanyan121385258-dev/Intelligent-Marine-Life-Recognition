<template>
  <div class="dataset-management">
    <!-- 顶部页头 -->
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <FolderOpenOutlined class="title-icon" />
        </div>
        <div class="text-wrapper">
          <h2 class="page-title">YOLO 数据集管理</h2>
          <p class="page-description">管理项目训练用的检测数据集</p>
        </div>
      </div>
      <div class="header-right">
        <a-badge :count="datasets.length" show-zero>
          <span class="dataset-count">数据集数：{{ datasets.length }}</span>
        </a-badge>
        <a-button type="primary" class="upload-btn" @click="openUploadModal">
          <template #icon>
            <UploadOutlined />
          </template>
          上传数据集
        </a-button>
      </div>
    </div>

    <!-- 视图容器 -->
    <div class="page-body">
      <!-- 列表视图 -->
      <template v-if="viewMode === 'list'">
        <!-- 操作栏 -->
        <div class="action-bar">
          <div class="action-left">
            <a-button @click="fetchDatasets" :loading="loading">
              <template #icon>
                <ReloadOutlined />
              </template>
              刷新列表
            </a-button>
          </div>
          <div class="action-right">
            <a-input-search
              v-model:value="searchKeyword"
              placeholder="搜索数据集名称或描述..."
              style="width: 360px"
              allow-clear
              @search="handleSearch"
            />
          </div>
        </div>

        <!-- 数据集卡片列表 -->
        <div class="dataset-list">
          <a-spin :spinning="loading">
            <div v-if="filteredDatasets.length === 0" class="empty-state">
              <p class="empty-title">还没有任何数据集</p>
              <p class="empty-desc">点击右上角的“上传数据集”开始管理你的训练数据</p>
            </div>

            <a-row v-else :gutter="[20, 20]">
              <a-col
                v-for="item in filteredDatasets"
                :key="item.id"
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
              >
                <div class="dataset-card">
                  <div class="card-header">
                    <div class="card-title-row">
                      <FolderOutlined class="card-icon" />
                      <div class="card-title-text">
                        <div class="name" :title="item.name">{{ item.name }}</div>
                        <div class="meta">
                          <span class="version">v{{ item.version || '1.0' }}</span>
                          <span class="dot">•</span>
                          <span class="date">{{ formatDate(item.created_at) }}</span>
                        </div>
                      </div>
                    </div>
                    <a-tag color="blue" class="nc-tag">{{ item.nc || 0 }} 个类别</a-tag>
                  </div>

                  <div class="card-description" :title="item.description || '暂无描述'">
                    {{ item.description || '暂无描述' }}
                  </div>

                  <div class="card-stats">
                    <div class="stat-item">
                      <span class="label">训练集</span>
                      <span class="value">{{ item.train_images_count ?? '-' }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="label">验证集</span>
                      <span class="value">{{ item.val_images_count ?? '-' }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="label">测试集</span>
                      <span class="value">{{ item.test_images_count ?? '-' }}</span>
                    </div>
                  </div>

                  <div class="card-footer">
                    <a-button type="primary" class="view-btn" @click="openDetail(item)">
                      <template #icon>
                        <EyeOutlined />
                      </template>
                      立即查看
                    </a-button>
                    <a-popconfirm
                      title="确认删除该数据集？删除后不可恢复"
                      ok-text="删除"
                      cancel-text="取消"
                      @confirm="() => handleDelete(item)"
                    >
                      <a-button danger class="delete-btn">
                        <template #icon>
                          <DeleteOutlined />
                        </template>
                      </a-button>
                    </a-popconfirm>
                  </div>
                </div>
              </a-col>
            </a-row>
          </a-spin>
        </div>
      </template>

      <!-- 详情视图 -->
      <template v-else-if="viewMode === 'detail' && currentDataset">
        <div class="detail-view">
          <div class="detail-header">
            <a-button type="link" class="back-btn" @click="backToList">
              <template #icon>
                <ArrowLeftOutlined />
              </template>
              返回列表
            </a-button>
            <div class="detail-main">
              <FolderOpenOutlined class="detail-icon" />
              <div class="detail-text">
                <div class="name-row">
                  <span class="name">{{ currentDataset.name }}</span>
                  <a-tag class="version-tag">版本 {{ currentDataset.version || '1.0' }}</a-tag>
                </div>
                <div class="meta">
                  <span>创建时间：{{ formatDate(currentDataset.created_at) }}</span>
                  <span class="dot">•</span>
                  <span>ID：{{ currentDataset.id }}</span>
                </div>
                <div class="desc" :title="currentDataset.description || '暂无描述'">
                  {{ currentDataset.description || '暂无描述' }}
                </div>
              </div>
            </div>
            <div class="detail-actions">
              <a-button type="primary" class="samples-btn" @click="enterSamples">
                样本浏览
              </a-button>
              <a-button danger style="margin-left: 12px" @click="handleDelete(currentDataset)">
                <template #icon>
                  <DeleteOutlined />
                </template>
                删除数据集
              </a-button>
            </div>
          </div>

          <!-- 统计概览卡片 -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="label">类别数量</div>
              <div class="value">{{ currentDataset.nc || 0 }}</div>
            </div>
            <div class="stat-card">
              <div class="label">总图片数</div>
              <div class="value">{{ totalImages }}</div>
            </div>
            <div class="stat-card">
              <div class="label">训练集</div>
              <div class="value">{{ currentDataset.train_images_count ?? 0 }}</div>
            </div>
            <div class="stat-card">
              <div class="label">验证集</div>
              <div class="value">{{ currentDataset.val_images_count ?? 0 }}</div>
            </div>
          </div>

          <div class="detail-sections">
            <div class="left-column">
              <div class="section-card">
                <div class="section-title">类别信息</div>
                <p class="section-subtitle">
                  数据集包含 {{ currentDataset.names?.length || 0 }} 个检测类别
                </p>
                <div class="class-tags">
                  <a-tag
                    v-for="(name, index) in currentDataset.names || []"
                    :key="index"
                    color="blue"
                  >
                    {{ index }} {{ name }}
                  </a-tag>
                </div>
              </div>
            </div>
            <div class="right-column">
              <div class="section-card">
                <div class="section-title">文件路径</div>
                <p class="section-subtitle">数据集存储位置和配置文件</p>
                <div class="path-item">
                  <div class="label">根目录</div>
                  <a-input :value="currentDataset.root_folder_path" readonly />
                </div>
                <div class="path-item">
                  <div class="label">配置文件</div>
                  <a-input :value="currentDataset.data_yaml_path" readonly />
                </div>
              </div>
            </div>
          </div>

          <!-- 数据集分布 -->
          <div class="distribution-section">
            <div class="section-card full">
              <div class="section-title">数据集分布详情</div>
              <p class="section-subtitle">训练集、验证集和测试集的图片及标注文件数量</p>

              <div class="dist-row" v-for="item in distribution" :key="item.key">
                <div class="dist-label">
                  <span class="name">{{ item.label }}</span>
                  <span class="meta">图片：{{ item.images }}，标注：{{ item.labels }}</span>
                </div>
                <div class="dist-bar">
                  <a-progress
                    :percent="item.percent"
                    :stroke-color="item.color"
                    :show-info="false"
                  />
                  <span class="percent-text">{{ item.percent.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 样本浏览视图 -->
      <template v-else-if="viewMode === 'samples' && currentDataset">
        <div class="samples-view">
          <div class="samples-header">
            <div class="left">
              <a-button type="link" class="back-btn" @click="backToDetail">
                <template #icon>
                  <ArrowLeftOutlined />
                </template>
                返回详情
              </a-button>
              <div class="breadcrumbs">
                <span>样本浏览</span>
                <span class="dot">•</span>
                <span class="dataset-name">{{ currentDataset.name }}</span>
              </div>
            </div>
            <div class="right">
              <a-select v-model:value="currentSplit" style="width: 140px" @change="reloadSamples">
                <a-select-option value="train">训练集</a-select-option>
                <a-select-option value="val">验证集</a-select-option>
                <a-select-option value="test">测试集</a-select-option>
              </a-select>
            </div>
          </div>

          <div class="samples-grid">
            <a-spin :spinning="samplesLoading">
              <a-row :gutter="[20, 20]">
                <a-col
                  v-for="item in samples"
                  :key="itemKey(item)"
                  :xs="24"
                  :sm="12"
                  :md="8"
                  :lg="6"
                >
                  <div class="sample-card">
                    <div class="thumb-wrapper" @click="openSamplePreview(item)">
                      <img :src="resolveImageUrl(item.image)" class="thumb" alt="sample" />
                    </div>
                    <div class="sample-info">
                      <div class="file-row">
                        <span class="filename" :title="item.filename">{{ item.filename }}</span>
                        <span class="size">{{ formatFileSize(item.image_size || 0) }}</span>
                      </div>
                      <div class="label-header">
                        <span>标注信息</span>
                        <span class="target-count">{{ parsedLabels(item).length }} 个目标</span>
                      </div>
                      <div class="label-tags">
                        <a-tag v-for="(cls, idx) in aggregatedLabels(item)" :key="idx" color="blue">
                          {{ classNameByIndex(cls.classIndex)
                          }}<span v-if="cls.count > 1">*{{ cls.count }}</span>
                        </a-tag>
                      </div>
                    </div>
                  </div>
                </a-col>
              </a-row>
            </a-spin>
          </div>

          <div class="samples-pagination">
            <a-pagination
              :current="samplesPagination.current"
              :page-size="samplesPagination.pageSize"
              :total="samplesPagination.total"
              :show-size-changer="true"
              :page-size-options="['6', '12', '24']"
              :show-total="renderSamplesTotal"
              @change="handleSamplesPageChange"
              @showSizeChange="handleSamplesSizeChange"
            />
          </div>
        </div>
      </template>
    </div>

    <!-- 样本大图预览 -->
    <a-modal
      v-model:visible="previewVisible"
      title="样本预览"
      :footer="null"
      width="80%"
      centered
      :body-style="{ padding: '16px 24px' }"
    >
      <div class="image-preview-wrapper">
        <div class="image-preview-columns">
          <!-- 原图 -->
          <div class="image-preview-main">
            <div class="preview-subtitle">原图</div>
            <img :src="previewImage" alt="sample original" />
          </div>

          <!-- 标注结果 -->
          <div class="image-preview-main">
            <div class="preview-subtitle">标注结果</div>
            <div class="annotated-wrapper">
              <img :src="previewImage" alt="sample annotated" />
              <div
                v-for="(box, idx) in previewBoxes"
                :key="idx"
                class="bbox"
                :style="bboxStyle(box)"
              >
                <span class="bbox-label">{{ classNameByIndex(box.classIndex) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="image-preview-meta" v-if="previewTitle">
          <span class="filename" :title="previewTitle">{{ previewTitle }}</span>
        </div>
      </div>
    </a-modal>

    <!-- 上传数据集弹窗 -->
    <a-modal
      v-model:visible="uploadVisible"
      title="上传数据集"
      :confirm-loading="uploading"
      @ok="handleUpload"
      @cancel="() => (uploadVisible = false)"
      width="640px"
    >
      <a-form :model="uploadForm" layout="vertical">
        <a-form-item label="数据集名称" required>
          <a-input v-model:value="uploadForm.name" placeholder="请输入数据集名称" />
        </a-form-item>
        <a-form-item label="版本">
          <a-input v-model:value="uploadForm.version" placeholder="例如：1.0" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea
            v-model:value="uploadForm.description"
            :rows="3"
            placeholder="请输入数据集描述"
          />
        </a-form-item>
        <a-form-item label="数据集压缩包 (ZIP)" required>
          <a-upload :before-upload="beforeUpload" :file-list="uploadFileList" :max-count="1">
            <a-button> <UploadOutlined /> 选择 ZIP 文件 </a-button>
          </a-upload>
          <div class="upload-hint">仅支持包含 YOLO 目录结构的 ZIP 压缩包</div>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { message, Upload } from 'ant-design-vue';
import {
  FolderOpenOutlined,
  FolderOutlined,
  UploadOutlined,
  ReloadOutlined,
  EyeOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons-vue';
import { yoloApi, YoloDatasetSummary, YoloDatasetDetail, YoloDatasetSampleItem } from '@/api/yolo';
import { getFullFileUrl, formatFileSize } from '@/utils/hertz_url';

// 视图模式：列表 / 详情 / 样本
const viewMode = ref<'list' | 'detail' | 'samples'>('list');

// 加载状态
const loading = ref(false);
const samplesLoading = ref(false);
const uploading = ref(false);

// 列表和搜索
const datasets = ref<YoloDatasetDetail[]>([]);
const searchKeyword = ref('');

const filteredDatasets = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase();
  if (!kw) return datasets.value;
  return datasets.value.filter((item) => {
    const name = (item.name || '').toLowerCase();
    const desc = (item.description || '').toLowerCase();
    return name.includes(kw) || desc.includes(kw);
  });
});

// 当前数据集
const currentDataset = ref<YoloDatasetDetail | null>(null);

// 样本浏览
const currentSplit = ref<'train' | 'val' | 'test'>('train');
const samples = ref<YoloDatasetSampleItem[]>([]);
const samplesPagination = reactive({ current: 1, pageSize: 8, total: 0 });

// 上传表单
const uploadVisible = ref(false);
const uploadForm = reactive({
  name: '',
  version: '1.0',
  description: '',
});
const uploadFileList = ref<any[]>([]);

const openUploadModal = () => {
  uploadVisible.value = true;
};

const beforeUpload = (file: File) => {
  const isZip = file.name.toLowerCase().endsWith('.zip');
  if (!isZip) {
    message.error('仅支持 ZIP 压缩包');
    return Upload.LIST_IGNORE;
  }
  uploadFileList.value = [file as any];
  return false;
};

const handleUpload = async () => {
  if (!uploadForm.name.trim()) {
    message.warning('请填写数据集名称');
    return;
  }
  if (!uploadFileList.value.length) {
    message.warning('请选择 ZIP 压缩包');
    return;
  }

  const file = uploadFileList.value[0] as any;
  const realFile: File = file.originFileObj || file;

  const formData = new FormData();
  formData.append('name', uploadForm.name);
  if (uploadForm.version) formData.append('version', uploadForm.version);
  if (uploadForm.description) formData.append('description', uploadForm.description);
  formData.append('zip_file', realFile);

  uploading.value = true;
  try {
    const res = await yoloApi.uploadDataset(formData);
    if (res.success) {
      message.success('数据集上传成功');
      uploadVisible.value = false;
      uploadFileList.value = [];
      uploadForm.name = '';
      uploadForm.description = '';
      fetchDatasets();
    } else {
      message.error(res.message || '上传失败');
    }
  } catch (e) {
    console.error(e);
    message.error('上传失败，请检查网络连接');
  } finally {
    uploading.value = false;
  }
};

// 获取数据集列表
const fetchDatasets = async () => {
  loading.value = true;
  try {
    const res = await yoloApi.getDatasets();
    if (res.success && res.data) {
      // 按创建时间倒序排序（如果有）
      const list = [...res.data].sort((a, b) => {
        const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
        const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
        return tb - ta;
      });
      datasets.value = list as YoloDatasetDetail[];
    } else {
      message.error(res.message || '获取数据集失败');
    }
  } catch (e) {
    console.error(e);
    message.error('获取数据集失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  // 过滤逻辑已经在 computed 中处理，这里保留占位
};

const openDetail = async (item: YoloDatasetSummary) => {
  await loadDatasetDetail(item.id);
  if (currentDataset.value) {
    viewMode.value = 'detail';
  }
};

const loadDatasetDetail = async (id: number) => {
  loading.value = true;
  try {
    const res = await yoloApi.getDatasetDetail(id);
    if (res.success && res.data) {
      currentDataset.value = res.data;
    } else {
      message.error(res.message || '获取数据集详情失败');
    }
  } catch (e) {
    console.error(e);
    message.error('获取数据集详情失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

const backToList = () => {
  viewMode.value = 'list';
  currentDataset.value = null;
};

const backToDetail = () => {
  viewMode.value = 'detail';
};

// 删除数据集
const handleDelete = async (item: YoloDatasetSummary | YoloDatasetDetail) => {
  try {
    const res = await yoloApi.deleteDataset(item.id);
    if (res.success) {
      message.success('数据集删除成功');
      if (currentDataset.value && currentDataset.value.id === item.id) {
        backToList();
      }
      fetchDatasets();
    } else {
      message.error(res.message || '删除失败');
    }
  } catch (e) {
    console.error(e);
    message.error('删除失败，请检查网络连接');
  }
};

// 统计与格式化
const totalImages = computed(() => {
  if (!currentDataset.value) return 0;
  const t =
    (currentDataset.value.train_images_count ?? 0) +
    (currentDataset.value.val_images_count ?? 0) +
    (currentDataset.value.test_images_count ?? 0);
  return t;
});

const distribution = computed(() => {
  if (!currentDataset.value) return [];
  const total = totalImages.value || 1;
  const list = [
    {
      key: 'train',
      label: '训练集 (Train)',
      images: currentDataset.value.train_images_count ?? 0,
      labels: currentDataset.value.train_labels_count ?? 0,
      color: '#3b82f6',
    },
    {
      key: 'val',
      label: '验证集 (Validation)',
      images: currentDataset.value.val_images_count ?? 0,
      labels: currentDataset.value.val_labels_count ?? 0,
      color: '#22c55e',
    },
    {
      key: 'test',
      label: '测试集 (Test)',
      images: currentDataset.value.test_images_count ?? 0,
      labels: currentDataset.value.test_labels_count ?? 0,
      color: '#f97316',
    },
  ];
  return list.map((item) => ({
    ...item,
    percent: total ? (item.images / total) * 100 : 0,
  }));
});

const formatDate = (val?: string) => {
  if (!val) return '-';
  try {
    const d = new Date(val);
    if (Number.isNaN(d.getTime())) return val;
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  } catch {
    return val;
  }
};

// 样本浏览
const reloadSamples = () => {
  samplesPagination.current = 1;
  fetchSamples();
};

const fetchSamples = async () => {
  if (!currentDataset.value) return;
  samplesLoading.value = true;
  try {
    const params = {
      split: currentSplit.value,
      limit: samplesPagination.pageSize,
      offset: (samplesPagination.current - 1) * samplesPagination.pageSize,
    };
    const res = await yoloApi.getDatasetSamples(currentDataset.value.id, params);
    if (res.success && res.data) {
      samples.value = res.data.items || [];
      samplesPagination.total = res.data.total || samples.value.length;
    } else {
      message.error(res.message || '获取样本失败');
    }
  } catch (e) {
    console.error(e);
    message.error('获取样本失败，请检查网络连接');
  } finally {
    samplesLoading.value = false;
  }
};

const enterSamples = async () => {
  if (!currentDataset.value) return;
  samplesPagination.current = 1;
  await fetchSamples();
  viewMode.value = 'samples';
};

const handleSamplesPageChange = (page: number, pageSize: number) => {
  samplesPagination.current = page;
  samplesPagination.pageSize = pageSize;
  fetchSamples();
};

const handleSamplesSizeChange = (_: number, size: number) => {
  samplesPagination.current = 1;
  samplesPagination.pageSize = size;
  fetchSamples();
};

const resolveImageUrl = (relative: string) => {
  return getFullFileUrl(relative);
};

const itemKey = (item: YoloDatasetSampleItem) => `${item.filename}-${item.image}`;

// 解析 label 行为 class 索引 + 归一化框
const parsedLabels = (item: YoloDatasetSampleItem) => {
  const lines = (item.label || '')
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean);
  return lines.map((line) => {
    const parts = line.split(/\s+/);
    const classIndex = Number(parts[0]) || 0;
    const x = Number(parts[1]) || 0; // 中心 x (0-1)
    const y = Number(parts[2]) || 0; // 中心 y (0-1)
    const w = Number(parts[3]) || 0; // 宽度 (0-1)
    const h = Number(parts[4]) || 0; // 高度 (0-1)
    return { classIndex, x, y, w, h };
  });
};

// 将同一类别的标注聚合为计数
const aggregatedLabels = (item: YoloDatasetSampleItem) => {
  const list = parsedLabels(item);
  const map: Record<number, number> = {};
  list.forEach((l) => {
    const idx = l.classIndex;
    map[idx] = (map[idx] || 0) + 1;
  });
  return Object.entries(map).map(([index, count]) => ({
    classIndex: Number(index),
    count,
  }));
};

const classNameByIndex = (index: number) => {
  if (!currentDataset.value || !Array.isArray(currentDataset.value.names)) return `类别 ${index}`;
  return currentDataset.value.names[index] ?? `类别 ${index}`;
};

const renderSamplesTotal = (total: number) => `显示 ${total} 个样本`;

// 打开样本预览
const previewVisible = ref(false);
const previewImage = ref('');
const previewTitle = ref('');
const previewBoxes = ref<{ classIndex: number; x: number; y: number; w: number; h: number }[]>([]);

const openSamplePreview = (item: YoloDatasetSampleItem) => {
  previewImage.value = resolveImageUrl(item.image);
  previewTitle.value = item.filename;
  previewBoxes.value = parsedLabels(item);
  previewVisible.value = true;
};

// 将 YOLO 归一化坐标转换为 CSS 百分比样式
const bboxStyle = (box: { x: number; y: number; w: number; h: number }) => {
  const left = (box.x - box.w / 2) * 100;
  const top = (box.y - box.h / 2) * 100;
  const width = box.w * 100;
  const height = box.h * 100;
  return {
    left: `${Math.max(0, left)}%`,
    top: `${Math.max(0, top)}%`,
    width: `${Math.min(100, width)}%`,
    height: `${Math.min(100, height)}%`,
  };
};

onMounted(() => {
  fetchDatasets();
});
</script>

<style scoped lang="scss">
.dataset-management {
  padding: 0;
  background: #f5f5f7;
  min-height: 100vh;

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 28px 20px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    box-shadow: 0 0.5px 0 rgba(0, 0, 0, 0.08);
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      .icon-wrapper {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: #eef4ff;
        display: flex;
        align-items: center;
        justify-content: center;

        .title-icon {
          font-size: 22px;
          color: #3b82f6;
        }
      }

      .text-wrapper {
        .page-title {
          margin: 0 0 4px;
          font-size: 22px;
          font-weight: 600;
          color: #111827;
        }

        .page-description {
          margin: 0;
          font-size: 13px;
          color: #6b7280;
        }
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;

      .dataset-count {
        font-size: 13px;
        color: #6b7280;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.03);
      }

      .upload-btn {
        border-radius: 999px;
      }
    }
  }

  .page-body {
    padding: 0 32px 32px;
  }

  .action-bar {
    margin-top: 8px;
    margin-bottom: 16px;
    padding: 12px 18px;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;

    .action-left {
      display: flex;
      gap: 8px;
    }

    .action-right {
      display: flex;
      align-items: center;
    }
  }

  .dataset-list {
    margin-top: 12px;

    .empty-state {
      padding: 60px 0;
      text-align: center;
      background: #ffffff;
      border-radius: 20px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);

      .empty-title {
        margin: 0 0 8px;
        font-size: 18px;
        font-weight: 600;
        color: #111827;
      }

      .empty-desc {
        margin: 0;
        font-size: 13px;
        color: #6b7280;
      }
    }

    .dataset-card {
      background: #ffffff;
      border-radius: 18px;
      padding: 18px 18px 14px;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
      display: flex;
      flex-direction: column;
      gap: 10px;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;

        .card-title-row {
          display: flex;
          gap: 10px;

          .card-icon {
            font-size: 22px;
            color: #3b82f6;
            margin-top: 2px;
          }

          .card-title-text {
            .name {
              font-size: 15px;
              font-weight: 600;
              color: #111827;
              max-width: 180px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .meta {
              margin-top: 4px;
              font-size: 12px;
              color: #6b7280;

              .dot {
                margin: 0 4px;
              }

              .version {
                font-weight: 500;
              }
            }
          }
        }

        .nc-tag {
          background: #eef4ff;
          border: none;
          color: #1d4ed8;
        }
      }

      .card-description {
        font-size: 13px;
        color: #4b5563;
        min-height: 36px;
      }

      .card-stats {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        margin-top: 4px;

        .stat-item {
          flex: 1;
          padding: 8px 10px;
          border-radius: 10px;
          background: #f9fafb;
          text-align: center;

          .label {
            display: block;
            font-size: 11px;
            color: #9ca3af;
            margin-bottom: 2px;
          }

          .value {
            font-size: 14px;
            font-weight: 600;
            color: #111827;
          }
        }
      }

      .card-footer {
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .view-btn {
          border-radius: 999px;
        }

        .delete-btn {
          border-radius: 999px;
        }
      }
    }
  }

  .detail-view {
    margin-top: 12px;

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: #ffffff;
      border-radius: 18px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);

      .back-btn {
        padding-left: 0;
      }

      .detail-main {
        display: flex;
        align-items: center;
        gap: 14px;

        .detail-icon {
          font-size: 26px;
          color: #3b82f6;
        }

        .detail-text {
          .name-row {
            display: flex;
            align-items: center;
            gap: 8px;

            .name {
              font-size: 18px;
              font-weight: 600;
              color: #111827;
            }

            .version-tag {
              background: #eef4ff;
              border: none;
              color: #1d4ed8;
            }
          }

          .meta {
            margin-top: 4px;
            font-size: 12px;
            color: #6b7280;

            .dot {
              margin: 0 6px;
            }
          }

          .desc {
            margin-top: 6px;
            font-size: 13px;
            color: #4b5563;
          }
        }
      }

      .detail-actions {
        display: flex;
        align-items: center;
      }
    }

    .stats-grid {
      margin-top: 16px;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;

      .stat-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);

        .label {
          font-size: 12px;
          color: #9ca3af;
          margin-bottom: 6px;
        }

        .value {
          font-size: 20px;
          font-weight: 600;
          color: #111827;
        }
      }
    }

    .detail-sections {
      margin-top: 16px;
      display: grid;
      grid-template-columns: 1.4fr 1.6fr;
      gap: 16px;

      .section-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);

        .section-title {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
        }

        .section-subtitle {
          margin-top: 4px;
          font-size: 12px;
          color: #6b7280;
        }

        .class-tags {
          margin-top: 10px;
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .path-item {
          margin-top: 10px;

          .label {
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 4px;
          }
        }
      }
    }

    .distribution-section {
      margin-top: 16px;

      .section-card.full {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);

        .dist-row {
          margin-top: 10px;

          .dist-label {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #6b7280;
          }

          .dist-bar {
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 8px;

            .percent-text {
              font-size: 12px;
              color: #4b5563;
              width: 60px;
              text-align: right;
            }
          }
        }
      }
    }

    .samples-entry {
      margin-top: 18px;
      text-align: right;
    }
  }

  .samples-view {
    margin-top: 12px;

    .samples-header {
      padding: 14px 18px;
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
      display: flex;
      justify-content: space-between;
      align-items: center;

      .left {
        display: flex;
        align-items: center;
        gap: 12px;

        .breadcrumbs {
          font-size: 13px;
          color: #6b7280;

          .dot {
            margin: 0 4px;
          }

          .dataset-name {
            font-weight: 500;
            color: #111827;
          }
        }
      }
    }

    .samples-grid {
      margin-top: 16px;

      .sample-card {
        background: #ffffff;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        overflow: hidden;
        display: flex;
        flex-direction: column;

        .thumb-wrapper {
          background: #f3f4f6;
          min-height: 160px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: zoom-in;
          transition: transform 0.15s ease-out;

          &:hover {
            transform: scale(1.01);
          }

          .thumb {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
        }

        .sample-info {
          padding: 12px 14px 10px;

          .file-row {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: #111827;

            .filename {
              max-width: 160px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .size {
              color: #6b7280;
            }
          }

          .label-header {
            margin-top: 8px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #6b7280;

            .target-count {
              color: #4b5563;
            }
          }

          .label-tags {
            margin-top: 6px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
          }
        }
      }
    }

    .samples-pagination {
      margin-top: 16px;
      padding: 12px 0;
      background: transparent;
      text-align: right;
    }
  }
}

.image-preview-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;

  .image-preview-columns {
    display: flex;
    gap: 16px;
    max-width: 960px;
    width: 100%;

    @media (max-width: 992px) {
      flex-direction: column;
    }
  }

  .image-preview-main {
    flex: 1;
    background: #f3f4f6;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
    padding: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;

    .preview-subtitle {
      font-size: 12px;
      color: #6b7280;
      margin-bottom: 8px;
      align-self: flex-start;
    }

    img {
      max-width: 100%;
      max-height: 76vh;
      border-radius: 12px;
      object-fit: contain;
    }

    .annotated-wrapper {
      position: relative;
      width: 100%;
      max-height: 76vh;

      img {
        display: block;
        width: 100%;
        height: auto;
        max-height: 76vh;
        border-radius: 12px;
        object-fit: contain;
      }

      .bbox {
        position: absolute;
        border: 2px solid rgba(59, 130, 246, 0.95);
        box-sizing: border-box;
        box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.4);

        .bbox-label {
          position: absolute;
          left: 0;
          top: -18px;
          padding: 0 4px;
          font-size: 11px;
          line-height: 18px;
          background: rgba(17, 24, 39, 0.9);
          color: #f9fafb;
          border-radius: 4px;
          white-space: nowrap;
        }
      }
    }
  }

  .image-preview-meta {
    max-width: 960px;
    width: 100%;
    font-size: 12px;
    color: #6b7280;
    text-align: left;
    word-break: break-all;

    .filename {
      display: inline-block;
    }
  }
}

@media (max-width: 992px) {
  .dataset-management {
    .stats-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .detail-sections {
      grid-template-columns: 1fr;
    }
  }
}
</style>
