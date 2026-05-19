<template>
  <div class="yolo-train-page">
    <!-- 顶部导航：训练任务 / 任务详情 / 创建任务 -->
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <ThunderboltOutlined class="title-icon" />
        </div>
        <div class="text-wrapper">
          <h2 class="page-title">YOLO 训练管理</h2>
          <p class="page-description">配置训练参数并管理 YOLO 模型训练任务</p>
        </div>
      </div>
      <div class="header-tabs">
        <a-space>
          <a-button
            :type="viewMode === 'list' ? 'primary' : 'default'"
            class="tab-btn"
            @click="switchToList"
          >
            训练任务
          </a-button>
          <a-button
            :type="viewMode === 'create' ? 'primary' : 'default'"
            class="tab-btn"
            @click="switchToCreate"
          >
            创建任务
          </a-button>
        </a-space>
      </div>
    </div>

    <div class="page-body">
      <!-- 训练任务列表视图 -->
      <template v-if="viewMode === 'list'">
        <div class="task-list-view">
          <div class="task-list-header">
            <div class="left">
              <a-radio-group v-model:value="statusFilter" button-style="solid">
                <a-radio-button value="all">全部任务</a-radio-button>
                <a-radio-button value="running">进行中</a-radio-button>
                <a-radio-button value="completed">已完成</a-radio-button>
              </a-radio-group>
            </div>
            <div class="right">
              <a-button @click="fetchJobs" :loading="loadingJobs">
                <template #icon>
                  <ReloadOutlined />
                </template>
                刷新任务
              </a-button>
            </div>
          </div>

          <a-spin :spinning="loadingJobs">
            <div v-if="jobs.length === 0" class="empty-state">
              <p class="empty-title">还没有训练任务</p>
              <p class="empty-desc">点击右上角“创建任务”开始一次新的模型训练</p>
            </div>

            <div v-else class="task-cards">
              <div v-for="job in filteredJobs" :key="job.id" class="task-card">
                <div class="task-card-header">
                  <div class="title-block">
                    <div class="title-row">
                      <span class="task-name"> 训练任务 #{{ job.id }} </span>
                      <a-tag :color="statusColor(job.status)" class="status-tag">
                        {{ statusText(job.status) }}
                      </a-tag>
                    </div>
                    <div class="subtitle-row">
                      <span class="dataset-name">{{ job.dataset_name }}</span>
                      <span class="dot">•</span>
                      <span class="model-info"
                        >YOLO{{ (job.model_family || '').toUpperCase() }}
                        {{ job.model_size ? job.model_size.toUpperCase() : '' }}</span
                      >
                      <span class="dot">•</span>
                      <span class="created-time">{{ formatDateTime(job.created_at) }}</span>
                    </div>
                  </div>
                  <div class="progress-value">{{ displayProgress(job).toFixed(0) }}%</div>
                </div>

                <div class="task-progress-bar">
                  <a-progress
                    :percent="displayProgress(job)"
                    :show-info="false"
                    stroke-color="#020617"
                  />
                </div>

                <div class="task-meta-grid">
                  <div class="meta-item">
                    <div class="label">训练轮数</div>
                    <div class="value">{{ job.epochs }} epochs</div>
                  </div>
                  <div class="meta-item">
                    <div class="label">图像尺寸</div>
                    <div class="value">{{ job.imgsz }}px</div>
                  </div>
                  <div class="meta-item">
                    <div class="label">批次大小</div>
                    <div class="value">{{ job.batch }}</div>
                  </div>
                  <div class="meta-item">
                    <div class="label">优化器</div>
                    <div class="value">{{ job.optimizer }}</div>
                  </div>
                </div>

                <div class="task-footer">
                  <div class="duration-text">
                    {{ renderDuration(job.started_at, job.finished_at) }}
                  </div>
                  <div class="actions">
                    <a-button size="small" class="dark-btn" @click="openDetail(job.id)">
                      <template #icon>
                        <EyeOutlined />
                      </template>
                      查看详情
                    </a-button>
                    <a-popconfirm
                      v-if="job.status === 'queued' || job.status === 'running'"
                      title="确认取消该训练任务？"
                      ok-text="确认"
                      cancel-text="取消"
                      @confirm="() => handleCancel(job.id)"
                    >
                      <a-button size="small">取消训练</a-button>
                    </a-popconfirm>
                    <a-popconfirm
                      v-else
                      title="确认删除该训练任务及其输出文件？"
                      ok-text="删除"
                      cancel-text="取消"
                      @confirm="() => handleDelete(job.id)"
                    >
                      <a-button size="small" danger>
                        <template #icon>
                          <DeleteOutlined />
                        </template>
                      </a-button>
                    </a-popconfirm>
                  </div>
                </div>
              </div>
            </div>
          </a-spin>
        </div>
      </template>

      <!-- 训练任务详情视图 -->
      <template v-else-if="viewMode === 'detail' && currentJob">
        <div class="task-detail-view">
          <div class="detail-header">
            <a-button type="link" class="back-btn" @click="switchToList">
              <template #icon>
                <ArrowLeftOutlined />
              </template>
              返回列表
            </a-button>
            <div class="detail-title-block">
              <div class="top-row">
                <span class="detail-title">训练任务 #{{ currentJob.id }}</span>
                <a-tag :color="statusColor(currentJob.status)" class="status-tag">
                  {{ statusText(currentJob.status) }}
                </a-tag>
              </div>
              <div class="sub-row">
                <span>{{ currentJob.dataset_name }}</span>
                <span class="dot">•</span>
                <span
                  >YOLO{{ (currentJob.model_family || '').toUpperCase() }}
                  {{ currentJob.model_size ? currentJob.model_size.toUpperCase() : '' }}</span
                >
                <span class="dot">•</span>
                <span>创建于 {{ formatDateTime(currentJob.created_at) }}</span>
              </div>
            </div>
            <div class="detail-actions">
              <a-button
                v-if="currentJob.status === 'queued' || currentJob.status === 'running'"
                @click="handleCancel(currentJob.id)"
              >
                取消训练
              </a-button>
              <a-button
                v-if="currentJob.status === 'completed'"
                type="primary"
                @click="handleDownload(currentJob.id)"
              >
                下载结果
              </a-button>
              <a-popconfirm
                title="确认删除该训练任务及其输出文件？"
                ok-text="删除"
                cancel-text="取消"
                @confirm="() => handleDelete(currentJob.id)"
              >
                <a-button danger>删除任务</a-button>
              </a-popconfirm>
            </div>
          </div>

          <!-- 状态卡片 -->
          <div class="status-cards">
            <div class="status-card">
              <div class="label">任务状态</div>
              <div class="value">{{ statusText(currentJob.status) }}</div>
            </div>
            <div class="status-card">
              <div class="label">训练进度</div>
              <div class="value">{{ detailDisplayProgress.toFixed(0) }}%</div>
            </div>
            <div class="status-card">
              <div class="label">运行时长</div>
              <div class="value">
                {{ renderDuration(currentJob.started_at, currentJob.finished_at) }}
              </div>
            </div>
          </div>

          <!-- 配置信息 -->
          <div class="detail-sections">
            <div class="config-section">
              <div class="section-title">配置信息</div>
              <div class="config-grid">
                <div class="config-item">
                  <div class="label">模型版本</div>
                  <div class="value">YOLO{{ (currentJob.model_family || '').toUpperCase() }}</div>
                </div>
                <div class="config-item">
                  <div class="label">模型尺寸</div>
                  <div class="value">{{ currentJob.model_size?.toUpperCase() || '-' }}</div>
                </div>
                <div class="config-item">
                  <div class="label">训练轮数</div>
                  <div class="value">{{ currentJob.epochs }}</div>
                </div>
                <div class="config-item">
                  <div class="label">图像尺寸</div>
                  <div class="value">{{ currentJob.imgsz }}</div>
                </div>
                <div class="config-item">
                  <div class="label">批次大小</div>
                  <div class="value">{{ currentJob.batch }}</div>
                </div>
                <div class="config-item">
                  <div class="label">设备</div>
                  <div class="value">GPU {{ currentJob.device }}</div>
                </div>
                <div class="config-item">
                  <div class="label">优化器</div>
                  <div class="value">{{ currentJob.optimizer }}</div>
                </div>
                <div class="config-item">
                  <div class="label">数据集</div>
                  <div class="value">{{ currentJob.dataset_name }}</div>
                </div>
              </div>
              <div class="config-path">
                <div class="label">配置文件</div>
                <a-input :value="currentJob.config_path" readonly />
              </div>
            </div>

            <div class="logs-section">
              <div class="section-title">
                <span>训练日志</span>
              </div>
              <div class="logs-box" ref="logsBoxRef">
                <pre class="logs-content">{{ logsContent || '暂时没有日志输出' }}</pre>
              </div>
            </div>
          </div>

          <!-- 时间信息 -->
          <div class="time-section">
            <div class="section-title">时间信息</div>
            <div class="time-grid">
              <div class="time-item">
                <div class="label">创建时间</div>
                <div class="value">{{ formatDateTime(currentJob.created_at) }}</div>
              </div>
              <div class="time-item">
                <div class="label">开始时间</div>
                <div class="value">
                  {{ currentJob.started_at ? formatDateTime(currentJob.started_at) : '未开始' }}
                </div>
              </div>
              <div class="time-item">
                <div class="label">结束时间</div>
                <div class="value">
                  {{ currentJob.finished_at ? formatDateTime(currentJob.finished_at) : '未结束' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 创建训练任务视图 -->
      <template v-else-if="viewMode === 'create'">
        <div class="create-view">
          <div class="create-header">
            <a-button type="link" class="back-btn" @click="switchToList">
              <template #icon>
                <ArrowLeftOutlined />
              </template>
              返回列表
            </a-button>
            <div class="create-title-block">
              <div class="primary">创建训练任务</div>
              <div class="secondary">配置训练参数并启动 YOLO 模型训练</div>
            </div>
          </div>

          <div class="create-body">
            <a-form :model="form" layout="vertical" class="form-card">
              <div class="section-title">基础配置</div>
              <a-row :gutter="[24, 0]">
                <a-col :xs="24" :md="12">
                  <a-form-item label="数据集" required>
                    <a-select
                      v-model:value="form.dataset_id"
                      placeholder="选择训练数据集"
                      :options="datasetOptions.map((d) => ({ label: d.name, value: d.id }))"
                    />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :md="12">
                  <a-form-item label="模型版本" required>
                    <a-select
                      v-model:value="form.model_family"
                      placeholder="选择 YOLO 版本"
                      :options="
                        versionOptions.map((v) => ({
                          label: 'YOLO' + v.family.toUpperCase(),
                          value: v.family,
                        }))
                      "
                    />
                  </a-form-item>
                </a-col>
              </a-row>

              <div class="section-title">训练参数</div>
              <a-row :gutter="[24, 0]">
                <a-col :xs="24" :md="12">
                  <a-form-item label="训练轮数 (Epochs)">
                    <a-input-number
                      v-model:value="form.epochs"
                      :min="1"
                      :max="500"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :md="12">
                  <a-form-item label="图像尺寸 (Image Size)">
                    <a-input-number
                      v-model:value="form.imgsz"
                      :min="64"
                      :max="2048"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :md="12">
                  <a-form-item label="批次大小 (Batch Size)">
                    <a-input-number
                      v-model:value="form.batch"
                      :min="1"
                      :max="256"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :md="12">
                  <a-form-item label="设备 (Device)">
                    <a-input v-model:value="form.device" placeholder="例如: 0 或 cpu" />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :md="12">
                  <a-form-item label="优化器 (Optimizer)">
                    <a-select v-model:value="form.optimizer" :options="optimizerOptions" />
                  </a-form-item>
                </a-col>
              </a-row>

              <div class="form-actions">
                <a-space>
                  <a-button @click="resetForm">取消</a-button>
                  <a-button type="primary" :loading="creating" @click="handleCreate">
                    开始训练
                  </a-button>
                </a-space>
              </div>
            </a-form>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import {
  ThunderboltOutlined,
  ReloadOutlined,
  EyeOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons-vue';
import {
  yoloApi,
  type YoloTrainingJob,
  type YoloTrainDatasetOption,
  type YoloTrainVersionOption,
  type StartTrainingPayload,
} from '@/api/yolo';

const viewMode = ref<'list' | 'detail' | 'create'>('list');
const jobs = ref<YoloTrainingJob[]>([]);
const loadingJobs = ref(false);
const currentJob = ref<YoloTrainingJob | null>(null);
const loadingLogs = ref(false);
const logsContent = ref('');
const logsOffset = ref(0);

const logsBoxRef = ref<HTMLDivElement | null>(null);
const logsFinished = ref(false);
let logsTimer: number | null = null;

// 进度条前端显示值（做平滑动画，不直接跳到后端值）
const jobDisplayProgress = ref<Record<number, number>>({});
const detailDisplayProgress = ref(0);
let progressTimer: number | null = null;

const datasetOptions = ref<YoloTrainDatasetOption[]>([]);
const versionOptions = ref<YoloTrainVersionOption[]>([]);

const statusFilter = ref<'all' | 'running' | 'completed'>('all');

const filteredJobs = computed(() => {
  if (statusFilter.value === 'all') return jobs.value;
  if (statusFilter.value === 'running') {
    return jobs.value.filter(
      (j) => j.status === 'queued' || j.status === 'running' || j.status === 'canceling'
    );
  }
  if (statusFilter.value === 'completed') {
    return jobs.value.filter((j) => j.status === 'completed');
  }
  return jobs.value;
});

const form = reactive<StartTrainingPayload>({
  dataset_id: 0,
  model_family: 'v8',
  model_size: 'n',
  epochs: 100,
  imgsz: 640,
  batch: 16,
  device: '0',
  optimizer: 'SGD',
});

const optimizerOptions = [
  { label: 'SGD (推荐)', value: 'SGD' },
  { label: 'Adam', value: 'Adam' },
  { label: 'AdamW', value: 'AdamW' },
  { label: 'RMSProp', value: 'RMSProp' },
];

const switchToList = () => {
  viewMode.value = 'list';
  currentJob.value = null;
  stopLogsPolling();
};

const switchToCreate = () => {
  viewMode.value = 'create';
  stopLogsPolling();
};

const statusText = (status: YoloTrainingJob['status']) => {
  switch (status) {
    case 'queued':
      return '排队中';
    case 'running':
      return '训练中';
    case 'canceling':
      return '取消中';
    case 'completed':
      return '已完成';
    case 'failed':
      return '失败';
    case 'canceled':
      return '已取消';
    default:
      return status;
  }
};

// 根据 job 获取前端展示的进度值
const displayProgress = (job: YoloTrainingJob) => {
  const real = job.progress ?? 0;
  const display = jobDisplayProgress.value[job.id];
  if (display == null) return real;
  return display;
};

// 启动一个定时器，让显示进度逐步追上真实进度
const startProgressTimer = () => {
  if (progressTimer != null) return;
  progressTimer = window.setInterval(() => {
    const updated: Record<number, number> = { ...jobDisplayProgress.value };
    let changed = false;

    jobs.value.forEach((job) => {
      const target = job.progress ?? 0;
      const id = job.id;
      const current = updated[id] ?? target;
      if (Math.abs(current - target) < 0.5) {
        updated[id] = target;
      } else if (current < target) {
        updated[id] = current + 1;
        changed = true;
      } else if (current > target) {
        updated[id] = current - 1;
        changed = true;
      }
    });

    if (changed) {
      jobDisplayProgress.value = updated;
    }

    // 详情页进度同步
    if (currentJob.value) {
      const targetDetail = currentJob.value.progress ?? 0;
      const curDetail = detailDisplayProgress.value;
      if (Math.abs(curDetail - targetDetail) < 0.5) {
        detailDisplayProgress.value = targetDetail;
      } else if (curDetail < targetDetail) {
        detailDisplayProgress.value = curDetail + 1;
      } else if (curDetail > targetDetail) {
        detailDisplayProgress.value = curDetail - 1;
      }
    }
  }, 200);
};

const stopProgressTimer = () => {
  if (progressTimer != null) {
    window.clearInterval(progressTimer);
    progressTimer = null;
  }
};

const statusColor = (status: YoloTrainingJob['status']) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'running':
    case 'queued':
      return 'processing';
    case 'failed':
      return 'error';
    case 'canceling':
    case 'canceled':
      return 'default';
    default:
      return 'default';
  }
};

const formatDateTime = (val?: string) => {
  if (!val) return '-';
  const d = new Date(val);
  if (Number.isNaN(d.getTime())) return val;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  return `${y}/${m}/${day} ${hh}:${mm}`;
};

const renderDuration = (start?: string | null, end?: string | null) => {
  if (!start) return '未开始';
  const s = new Date(start).getTime();
  const e = end ? new Date(end).getTime() : Date.now();
  if (Number.isNaN(s) || Number.isNaN(e)) return '-';
  const diff = Math.max(0, e - s) / 1000;
  const hours = Math.floor(diff / 3600);
  const minutes = Math.floor((diff % 3600) / 60);
  if (hours === 0 && minutes === 0) return '不到 1 分钟';
  if (hours === 0) return `${minutes} 分钟`;
  return `${hours}h ${minutes}m`;
};

const fetchOptions = async () => {
  try {
    const res = await yoloApi.getTrainOptions();
    if (res.success && res.data) {
      datasetOptions.value = res.data.datasets || [];
      versionOptions.value = res.data.versions || [];
      if (datasetOptions.value.length && !form.dataset_id) {
        form.dataset_id = datasetOptions.value[0].id;
      }
    } else {
      message.error(res.message || '获取训练配置失败');
    }
  } catch (e) {
    console.error(e);
    message.error('获取训练配置失败，请检查网络连接');
  }
};

const fetchJobs = async () => {
  loadingJobs.value = true;
  try {
    const res = await yoloApi.getTrainJobs();
    if (res.success && res.data) {
      const sorted = [...res.data].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      jobs.value = sorted;
      // 初始化/更新显示进度
      sorted.forEach((job) => {
        const real = job.progress ?? 0;
        if (jobDisplayProgress.value[job.id] == null) {
          jobDisplayProgress.value[job.id] = real;
        }
      });
    } else {
      message.error(res.message || '获取训练任务失败');
    }
  } catch (e) {
    console.error(e);
    message.error('获取训练任务失败，请检查网络连接');
  } finally {
    loadingJobs.value = false;
  }
};

const openDetail = async (id: number) => {
  try {
    const res = await yoloApi.getTrainJobDetail(id);
    if (res.success && res.data) {
      currentJob.value = res.data;
      viewMode.value = 'detail';
      logsContent.value = '';
      logsOffset.value = 0;
      detailDisplayProgress.value = res.data.progress ?? 0;
      startLogsPolling();
    } else {
      message.error(res.message || '获取任务详情失败');
    }
  } catch (e) {
    console.error(e);
    message.error('获取任务详情失败，请检查网络连接');
  }
};

const scrollLogsToBottom = async () => {
  await nextTick();
  const box = logsBoxRef.value;
  if (box) {
    box.scrollTop = box.scrollHeight;
  }
};

const reloadLogs = async () => {
  if (!currentJob.value) return;
  try {
    const res = await yoloApi.getTrainJobLogs(currentJob.value.id, {
      offset: logsOffset.value,
      max: 65536,
    });
    if (res.success && res.data) {
      const { content, next_offset, finished } = res.data;
      if (content) {
        logsContent.value += content;
        logsOffset.value = next_offset ?? logsOffset.value;
        await scrollLogsToBottom();
      } else if (typeof next_offset === 'number') {
        logsOffset.value = next_offset;
      }
      logsFinished.value = !!finished;
    } else {
      console.error('获取日志失败', res.message);
    }
  } catch (e) {
    console.error('获取日志失败', e);
  }

  // 同步最新任务进度和状态
  try {
    if (!currentJob.value) return;
    const detailRes = await yoloApi.getTrainJobDetail(currentJob.value.id);
    if (detailRes.success && detailRes.data) {
      const job = detailRes.data;
      currentJob.value = job;

      // 更新详情视图进度的目标值（动画由进度定时器控制）
      // 不直接覆盖 detailDisplayProgress，而是只更新 currentJob.progress

      // 同时更新列表中的对应任务
      const idx = jobs.value.findIndex((j) => j.id === job.id);
      if (idx !== -1) {
        jobs.value[idx] = job;
      }

      // 如果任务已完成，强制进度显示为 100%
      if (job.status === 'completed') {
        const finalProgress = job.progress ?? 100;
        jobDisplayProgress.value[job.id] = finalProgress >= 100 ? 100 : finalProgress;
        detailDisplayProgress.value = finalProgress >= 100 ? 100 : finalProgress;
      }
    }
  } catch (e) {
    console.error('获取任务详情失败（同步进度）', e);
  }
};

const LOG_POLL_INTERVAL = 2000;

const startLogsPolling = () => {
  stopLogsPolling();
  logsFinished.value = false;
  logsContent.value = '';
  logsOffset.value = 0;
  if (!currentJob.value) return;
  // 先拉取一次
  reloadLogs();
  logsTimer = window.setInterval(async () => {
    if (!currentJob.value || logsFinished.value) {
      stopLogsPolling();
      return;
    }
    await reloadLogs();
  }, LOG_POLL_INTERVAL);
};

const stopLogsPolling = () => {
  if (logsTimer != null) {
    window.clearInterval(logsTimer);
    logsTimer = null;
  }
};

const handleCancel = async (id: number) => {
  try {
    const res = await yoloApi.cancelTrainJob(id);
    if (res.success) {
      message.success('已提交取消请求');
      fetchJobs();
      if (currentJob.value && currentJob.value.id === id) {
        openDetail(id);
      }
    } else {
      message.error(res.message || '取消训练失败');
    }
  } catch (e) {
    console.error(e);
    message.error('取消训练失败，请检查网络连接');
  }
};

const handleDelete = async (id: number) => {
  try {
    const res = await yoloApi.deleteTrainJob(id);
    if (res.success) {
      message.success('训练任务删除成功');
      if (currentJob.value && currentJob.value.id === id) {
        switchToList();
      }
      fetchJobs();
    } else {
      message.error(res.message || '删除训练任务失败');
    }
  } catch (e) {
    console.error(e);
    message.error('删除训练任务失败，请检查网络连接');
  }
};

const handleDownload = async (id: number) => {
  try {
    const res = await yoloApi.downloadTrainJobResult(id);
    if (res.success && res.data && res.data.url) {
      const a = document.createElement('a');
      a.href = res.data.url;
      a.target = '_blank';
      a.click();
    } else {
      message.error(res.message || '暂未生成可下载结果');
    }
  } catch (e) {
    console.error(e);
    message.error('下载结果失败，请检查网络连接');
  }
};

const creating = ref(false);

const resetForm = () => {
  form.epochs = 100;
  form.imgsz = 640;
  form.batch = 16;
  form.device = '0';
  form.optimizer = 'SGD';
};

const handleCreate = async () => {
  if (!form.dataset_id) {
    message.warning('请选择数据集');
    return;
  }
  if (!form.model_family) {
    message.warning('请选择模型版本');
    return;
  }

  creating.value = true;
  try {
    const payload: StartTrainingPayload = { ...form };
    const res = await yoloApi.startTrainJob(payload);
    if (res.success && res.data) {
      message.success('训练任务创建成功');
      switchToList();
      fetchJobs();
    } else {
      message.error(res.message || '创建训练任务失败');
    }
  } catch (e) {
    console.error(e);
    message.error('创建训练任务失败，请检查网络连接');
  } finally {
    creating.value = false;
  }
};

onMounted(() => {
  fetchOptions();
  fetchJobs();
  startProgressTimer();
});

onBeforeUnmount(() => {
  stopProgressTimer();
  stopLogsPolling();
});
</script>

<style scoped lang="scss">
.yolo-train-page {
  padding: 0;
  background: #f5f5f7;
  min-height: 100vh;

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 28px 16px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    box-shadow: 0 0.5px 0 rgba(0, 0, 0, 0.08);
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      .icon-wrapper {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: #eef2ff;
        display: flex;
        align-items: center;
        justify-content: center;

        .title-icon {
          font-size: 22px;
          color: #4f46e5;
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

    .header-tabs {
      .tab-btn {
        border-radius: 999px;
      }
    }
  }

  .page-body {
    padding: 0 28px 28px;
  }

  .task-list-view {
    .task-list-header {
      margin: 12px 0 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

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

    .task-cards {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .task-card {
      background: #ffffff;
      border-radius: 20px;
      padding: 18px 20px 16px;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);

      .task-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;

        .title-block {
          .title-row {
            display: flex;
            align-items: center;
            gap: 8px;

            .task-name {
              font-size: 16px;
              font-weight: 600;
              color: #111827;
            }

            .status-tag {
              border-radius: 999px;
            }
          }

          .subtitle-row {
            margin-top: 4px;
            font-size: 12px;
            color: #6b7280;

            .dot {
              margin: 0 4px;
            }
          }
        }

        .progress-value {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
        }
      }

      .task-progress-bar {
        margin-top: 8px;
      }

      .task-meta-grid {
        margin-top: 10px;
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 8px;

        .meta-item {
          padding: 8px 10px;
          border-radius: 12px;
          background: #f9fafb;

          .label {
            font-size: 11px;
            color: #9ca3af;
            margin-bottom: 2px;
          }

          .value {
            font-size: 13px;
            font-weight: 500;
            color: #111827;
          }
        }
      }

      .task-footer {
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .duration-text {
          font-size: 12px;
          color: #6b7280;
        }

        .actions {
          display: flex;
          align-items: center;
          gap: 8px;

          .dark-btn {
            background: #020617;
            color: #f9fafb;
            border-radius: 999px;

            &:hover {
              background: #020617;
              color: #ffffff;
            }
          }
        }
      }
    }
  }

  .task-detail-view {
    margin-top: 16px;

    .detail-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;

      .back-btn {
        padding-left: 0;
      }

      .detail-title-block {
        flex: 1;
        margin: 0 24px;

        .top-row {
          display: flex;
          align-items: center;
          gap: 8px;

          .detail-title {
            font-size: 18px;
            font-weight: 600;
            color: #111827;
          }
        }

        .sub-row {
          margin-top: 4px;
          font-size: 12px;
          color: #6b7280;

          .dot {
            margin: 0 4px;
          }
        }
      }

      .detail-actions {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .status-cards {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;

      .status-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 12px 14px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);

        .label {
          font-size: 12px;
          color: #9ca3af;
          margin-bottom: 4px;
        }

        .value {
          font-size: 15px;
          font-weight: 600;
          color: #111827;
        }
      }
    }

    .detail-sections {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
      gap: 16px;

      .config-section,
      .logs-section {
        background: #ffffff;
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);

        .section-title {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 14px;
          font-weight: 600;
          color: #111827;
          margin-bottom: 12px;
        }
      }

      .config-section {
        .config-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px 16px;

          .config-item {
            .label {
              font-size: 12px;
              color: #9ca3af;
              margin-bottom: 2px;
            }

            .value {
              font-size: 13px;
              color: #111827;
            }
          }
        }

        .config-path {
          margin-top: 14px;

          .label {
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 4px;
          }
        }
      }

      .logs-section {
        .logs-box {
          border-radius: 12px;
          background: #020617;
          color: #e5e7eb;
          padding: 10px 12px;
          min-height: 180px;
          max-height: 260px;
          overflow: auto;

          .logs-content {
            margin: 0;
            font-family:
              ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
              'Courier New', monospace;
            font-size: 12px;
            line-height: 1.5;
            white-space: pre-wrap;
          }
        }
      }
    }

    .time-section {
      margin-top: 16px;
      background: #ffffff;
      border-radius: 18px;
      padding: 14px 18px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);

      .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 10px;
      }

      .time-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px 16px;

        .time-item {
          .label {
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 2px;
          }

          .value {
            font-size: 13px;
            color: #111827;
          }
        }
      }
    }
  }

  .create-view {
    margin-top: 16px;

    .create-header {
      display: flex;
      align-items: center;
      margin-bottom: 16px;

      .back-btn {
        padding-left: 0;
      }

      .create-title-block {
        margin-left: 12px;

        .primary {
          font-size: 18px;
          font-weight: 600;
          color: #111827;
        }

        .secondary {
          margin-top: 4px;
          font-size: 13px;
          color: #6b7280;
        }
      }
    }

    .create-body {
      .form-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 18px 20px 20px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);

        .section-title {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
          margin-bottom: 12px;
        }

        .form-actions {
          margin-top: 16px;
          text-align: right;
        }
      }
    }
  }
}

@media (max-width: 992px) {
  .yolo-train-page {
    .task-detail-view {
      .detail-sections {
        grid-template-columns: 1fr;
      }

      .status-cards {
        grid-template-columns: 1fr;
      }

      .time-section {
        .time-grid {
          grid-template-columns: 1fr;
        }
      }
    }
  }
}
</style>
