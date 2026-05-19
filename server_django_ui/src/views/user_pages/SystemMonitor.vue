<template>
  <div class="system-monitor">
    <div class="page-header">
      <h1 class="page-title">
        <DatabaseOutlined class="title-icon" />
        系统监控
      </h1>
      <p class="page-description">实时监控系统运行状态和性能指标</p>
    </div>

    <div class="monitor-content">
      <a-spin :spinning="loading">
        <!-- 刷新按钮 -->
        <div class="refresh-actions">
          <a-button :loading="loading" @click="fetchAll" type="primary" size="large">
            <template #icon>
              <ReloadOutlined />
            </template>
            刷新数据
          </a-button>
        </div>

        <!-- 系统概览卡片 -->
        <div class="overview-cards" :class="currentLayoutConfig.overviewClass">
          <a-row :gutter="currentLayoutConfig.overviewGutter">
            <!-- 系统信息 -->
            <a-col
              :xs="currentLayoutConfig.overviewLayout.xs"
              :sm="currentLayoutConfig.overviewLayout.sm"
              :md="currentLayoutConfig.overviewLayout.md"
              :lg="currentLayoutConfig.overviewLayout.lg"
              :xl="currentLayoutConfig.overviewLayout.xl"
            >
              <div class="monitor-card system-card">
                <div class="card-header">
                  <div class="card-icon">
                    <DesktopOutlined />
                  </div>
                  <h3 class="card-title">系统信息</h3>
                </div>
                <div class="card-content">
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">主机名</span>
                      <span class="info-value">{{ system?.hostname || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">平台</span>
                      <span class="info-value">{{ system?.platform || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">架构</span>
                      <span class="info-value">{{ system?.architecture || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">启动时间</span>
                      <span class="info-value">{{ system?.boot_time || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">运行时长</span>
                      <span class="info-value">{{ system?.uptime || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </a-col>

            <!-- CPU信息 -->
            <a-col
              :xs="currentLayoutConfig.overviewLayout.xs"
              :sm="currentLayoutConfig.overviewLayout.sm"
              :md="currentLayoutConfig.overviewLayout.md"
              :lg="currentLayoutConfig.overviewLayout.lg"
              :xl="currentLayoutConfig.overviewLayout.xl"
            >
              <div class="monitor-card cpu-card">
                <div class="card-header">
                  <div class="card-icon">
                    <DesktopOutlined />
                  </div>
                  <h3 class="card-title">CPU 信息</h3>
                </div>
                <div class="card-content">
                  <div class="cpu-stats">
                    <div class="stat-item">
                      <div class="stat-value">{{ toNum(cpu?.cpu_count) ?? '-' }}</div>
                      <div class="stat-label">核心数</div>
                    </div>
                    <div class="stat-item">
                      <div class="stat-value cpu-usage">{{ toNum(cpu?.cpu_percent) ?? '-' }}%</div>
                      <div class="stat-label">使用率</div>
                    </div>
                  </div>
                  <div class="cpu-details">
                    <div class="detail-item">
                      <span class="detail-label">当前频率</span>
                      <span class="detail-value"
                        >{{ toNum(cpu?.cpu_freq?.current) ?? '-' }} MHz</span
                      >
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">频率范围</span>
                      <span class="detail-value"
                        >{{ toNum(cpu?.cpu_freq?.min) ?? '-' }} -
                        {{ toNum(cpu?.cpu_freq?.max) ?? '-' }} MHz</span
                      >
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">负载均值</span>
                      <span class="detail-value">{{
                        Array.isArray(cpu?.load_avg) ? cpu?.load_avg?.join(', ') : '-'
                      }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </a-col>

            <!-- 内存信息 -->
            <a-col
              :xs="currentLayoutConfig.overviewLayout.xs"
              :sm="currentLayoutConfig.overviewLayout.sm"
              :md="currentLayoutConfig.overviewLayout.md"
              :lg="currentLayoutConfig.overviewLayout.lg"
              :xl="currentLayoutConfig.overviewLayout.xl"
            >
              <div class="monitor-card memory-card">
                <div class="card-header">
                  <div class="card-icon">
                    <DatabaseOutlined />
                  </div>
                  <h3 class="card-title">内存使用</h3>
                </div>
                <div class="card-content">
                  <div class="memory-progress">
                    <a-progress
                      :percent="toNum(memory?.percent) ?? 0"
                      :stroke-color="getMemoryColor(toNum(memory?.percent) ?? 0)"
                      :show-info="false"
                      stroke-width="8"
                    />
                    <div class="progress-text">{{ toNum(memory?.percent) ?? 0 }}%</div>
                  </div>
                  <div class="memory-details">
                    <div class="memory-item">
                      <span class="memory-label">总量</span>
                      <span class="memory-value">{{ formatBytesMaybe(memory?.total) }}</span>
                    </div>
                    <div class="memory-item">
                      <span class="memory-label">已用</span>
                      <span class="memory-value">{{ formatBytesMaybe(memory?.used) }}</span>
                    </div>
                    <div class="memory-item">
                      <span class="memory-label">可用</span>
                      <span class="memory-value">{{ formatBytesMaybe(memory?.available) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </a-col>
          </a-row>
        </div>

        <!-- 详细监控数据 -->
        <div class="detail-sections" :class="currentLayoutConfig.detailClass">
          <a-row :gutter="currentLayoutConfig.detailGutter">
            <!-- GPU信息 -->
            <a-col
              :xs="currentLayoutConfig.detailLayout.xs"
              :sm="currentLayoutConfig.detailLayout.sm"
              :md="currentLayoutConfig.detailLayout.md"
              :lg="currentLayoutConfig.detailLayout.lg"
              :xl="currentLayoutConfig.detailLayout.xl"
            >
              <div class="monitor-card gpu-card">
                <div class="card-header">
                  <div class="card-icon">
                    <DatabaseOutlined />
                  </div>
                  <h3 class="card-title">GPU 信息</h3>
                </div>
                <div class="card-content">
                  <div v-if="gpu?.gpu_available" class="gpu-table">
                    <a-table
                      :data-source="gpu?.gpu_info || []"
                      :columns="gpuColumns"
                      row-key="id"
                      size="small"
                      :pagination="false"
                    />
                  </div>
                  <div v-else class="gpu-unavailable">
                    <a-alert :message="gpu?.message || '未检测到GPU设备'" type="info" show-icon />
                  </div>
                  <div class="gpu-timestamp">更新时间：{{ gpu?.timestamp }}</div>
                </div>
              </div>
            </a-col>

            <!-- 磁盘信息 -->
            <a-col
              :xs="currentLayoutConfig.detailLayout.xs"
              :sm="currentLayoutConfig.detailLayout.sm"
              :md="currentLayoutConfig.detailLayout.md"
              :lg="currentLayoutConfig.detailLayout.lg"
              :xl="currentLayoutConfig.detailLayout.xl"
            >
              <div class="monitor-card disk-card">
                <div class="card-header">
                  <div class="card-icon">
                    <DatabaseOutlined />
                  </div>
                  <h3 class="card-title">磁盘使用</h3>
                </div>
                <div class="card-content">
                  <a-table
                    :data-source="disks"
                    :columns="diskColumns"
                    row-key="device"
                    size="small"
                    :pagination="false"
                  />
                </div>
              </div>
            </a-col>
          </a-row>

          <a-row :gutter="currentLayoutConfig.detailGutter" style="margin-top: 24px">
            <!-- 网络信息 -->
            <a-col
              :xs="currentLayoutConfig.detailLayout.xs"
              :sm="currentLayoutConfig.detailLayout.sm"
              :md="currentLayoutConfig.detailLayout.md"
              :lg="currentLayoutConfig.detailLayout.lg"
              :xl="currentLayoutConfig.detailLayout.xl"
            >
              <div class="monitor-card network-card">
                <div class="card-header">
                  <div class="card-icon">
                    <WifiOutlined />
                  </div>
                  <h3 class="card-title">网络接口</h3>
                </div>
                <div class="card-content">
                  <a-table
                    :data-source="network"
                    :columns="networkColumns"
                    row-key="interface"
                    size="small"
                    :pagination="false"
                  />
                </div>
              </div>
            </a-col>

            <!-- 进程信息 -->
            <a-col
              :xs="currentLayoutConfig.detailLayout.xs"
              :sm="currentLayoutConfig.detailLayout.sm"
              :md="currentLayoutConfig.detailLayout.md"
              :lg="currentLayoutConfig.detailLayout.lg"
              :xl="currentLayoutConfig.detailLayout.xl"
            >
              <div class="monitor-card process-card">
                <div class="card-header">
                  <div class="card-icon">
                    <CodeOutlined />
                  </div>
                  <h3 class="card-title">进程监控 (Top 10)</h3>
                </div>
                <div class="card-content">
                  <a-table
                    :data-source="processes"
                    :columns="processColumns"
                    row-key="pid"
                    size="small"
                    :pagination="false"
                  />
                </div>
              </div>
            </a-col>
          </a-row>
        </div>
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue';
import {
  ReloadOutlined,
  DesktopOutlined,
  DatabaseOutlined,
  WifiOutlined,
  CodeOutlined,
} from '@ant-design/icons-vue';
import {
  systemMonitorApi,
  type SystemInfo,
  type CpuInfo,
  type MemoryInfo,
  type DiskInfo,
  type NetworkInfo,
  type ProcessInfo,
  type GpuInfoResponse,
} from '@/api/system_monitor';
import { message } from 'ant-design-vue';

const loading = ref(false);

// 系统监控布局配置
const systemMonitorLayouts = [
  {
    name: 'default',
    label: '标准布局',
    description: '概览卡片3列，详细信息2列，标准展示',
    overviewClass: 'overview-3col',
    detailClass: 'detail-2col',
    overviewLayout: { xs: 24, md: 12, lg: 8 },
    detailLayout: { xs: 24, lg: 12 },
    overviewGutter: [16, 16],
    detailGutter: [16, 16],
  },
  {
    name: 'compact',
    label: '紧凑布局',
    description: '概览卡片2列，详细信息全宽，适合小屏',
    overviewClass: 'overview-2col',
    detailClass: 'detail-full',
    overviewLayout: { xs: 24, sm: 12, lg: 12 },
    detailLayout: { xs: 24, lg: 24 },
    overviewGutter: [12, 12],
    detailGutter: [12, 12],
  },
  {
    name: 'wide',
    label: '宽屏布局',
    description: '概览卡片4列，详细信息并排，充分利用宽屏',
    overviewClass: 'overview-4col',
    detailClass: 'detail-side',
    overviewLayout: { xs: 24, sm: 12, lg: 6, xl: 6 },
    detailLayout: { xs: 24, lg: 12 },
    overviewGutter: [20, 20],
    detailGutter: [20, 20],
  },
];

// 当前布局
const currentLayout = ref<string>('default');

// 计算当前布局配置
const currentLayoutConfig = computed(() => {
  return (
    systemMonitorLayouts.find((l) => l.name === currentLayout.value) || systemMonitorLayouts[0]
  );
});

// 加载布局配置
const loadLayout = () => {
  const savedLayout = localStorage.getItem('systemMonitorLayout');
  if (savedLayout && systemMonitorLayouts.find((l) => l.name === savedLayout)) {
    currentLayout.value = savedLayout;
  } else {
    currentLayout.value = 'default';
  }
};

// 监听布局变化事件
const handleLayoutChange = () => {
  loadLayout();
};

onMounted(() => {
  loadLayout();
  window.addEventListener('systemMonitorLayoutChanged', handleLayoutChange);
  fetchAll();
});

onUnmounted(() => {
  window.removeEventListener('systemMonitorLayoutChanged', handleLayoutChange);
});

const system = ref<SystemInfo | null>(null);
const cpu = ref<CpuInfo | null>(null);
const memory = ref<MemoryInfo | null>(null);
const disks = ref<DiskInfo[]>([]);
const network = ref<NetworkInfo[]>([]);
const processes = ref<ProcessInfo[]>([]);
const gpu = ref<GpuInfoResponse | null>(null);

const fetchAll = async () => {
  loading.value = true;
  try {
    const res = await systemMonitorApi.getMonitor();
    if (res.success) {
      system.value = res.data?.system ?? null;
      cpu.value = res.data?.cpu ?? null;
      memory.value = res.data?.memory ?? null;
      disks.value = res.data?.disks ?? [];
      network.value = res.data?.network ?? [];
      processes.value = res.data?.processes ?? [];

      // 若综合接口缺少关键数据，回退单项接口
      const fallbacks: Promise<any>[] = [];
      if (!cpu.value || typeof cpu.value.cpu_percent !== 'number') {
        fallbacks.push(
          systemMonitorApi.getCpu().then((r) => {
            if (r.success) cpu.value = r.data;
          })
        );
      }
      if (!memory.value || typeof memory.value.percent !== 'number') {
        fallbacks.push(
          systemMonitorApi.getMemory().then((r) => {
            if (r.success) memory.value = r.data;
          })
        );
      }
      if (!disks.value || disks.value.length === 0) {
        fallbacks.push(
          systemMonitorApi.getDisks().then((r) => {
            if (r.success) disks.value = r.data;
          })
        );
      }
      if (!network.value || network.value.length === 0) {
        fallbacks.push(
          systemMonitorApi.getNetwork().then((r) => {
            if (r.success) network.value = r.data;
          })
        );
      }
      if (!processes.value || processes.value.length === 0) {
        fallbacks.push(
          systemMonitorApi.getProcesses().then((r) => {
            if (r.success) processes.value = r.data;
          })
        );
      }

      // GPU：始终尝试获取详细信息
      const gpuRes = await systemMonitorApi.getGpu();
      if (gpuRes.success) {
        gpu.value = gpuRes.data;
      } else {
        const g =
          Array.isArray(res.data?.gpus) && res.data.gpus.length > 0 ? res.data.gpus[0] : undefined;
        if (g) {
          gpu.value = {
            gpu_available: g.gpu_available,
            message: g.message,
            timestamp: g.timestamp,
            gpu_info: undefined,
          };
        }
      }

      if (fallbacks.length) await Promise.allSettled(fallbacks);
    } else {
      message.error(res.message || '获取监控数据失败');
    }
  } catch (err: any) {
    message.error(err?.message || '网络错误');
  } finally {
    loading.value = false;
  }
};

// 表格列定义
const diskColumns = [
  { title: '设备', dataIndex: 'device', key: 'device' },
  { title: '挂载点', dataIndex: 'mountpoint', key: 'mountpoint' },
  { title: '类型', dataIndex: 'fstype', key: 'fstype' },
  {
    title: '总容量',
    dataIndex: 'total',
    key: 'total',
    customRender: ({ text }: any) => formatBytes(text),
  },
  {
    title: '已用',
    dataIndex: 'used',
    key: 'used',
    customRender: ({ text }: any) => formatBytes(text),
  },
  {
    title: '空闲',
    dataIndex: 'free',
    key: 'free',
    customRender: ({ text }: any) => formatBytes(text),
  },
  {
    title: '使用率',
    dataIndex: 'percent',
    key: 'percent',
    customRender: ({ text }: any) => `${text}%`,
  },
];

const networkColumns = [
  { title: '接口', dataIndex: 'interface', key: 'interface' },
  {
    title: '发送',
    dataIndex: 'bytes_sent',
    key: 'bytes_sent',
    customRender: ({ text }: any) => formatBytes(text),
  },
  {
    title: '接收',
    dataIndex: 'bytes_recv',
    key: 'bytes_recv',
    customRender: ({ text }: any) => formatBytes(text),
  },
  { title: '发送包', dataIndex: 'packets_sent', key: 'packets_sent' },
  { title: '接收包', dataIndex: 'packets_recv', key: 'packets_recv' },
];

const processColumns = [
  { title: 'PID', dataIndex: 'pid', key: 'pid' },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: 'CPU%', dataIndex: 'cpu_percent', key: 'cpu_percent' },
  { title: '内存%', dataIndex: 'memory_percent', key: 'memory_percent' },
  {
    title: 'RSS',
    dataIndex: ['memory_info', 'rss'],
    key: 'rss',
    customRender: ({ text }: any) => formatBytes(text),
  },
  {
    title: 'VMS',
    dataIndex: ['memory_info', 'vms'],
    key: 'vms',
    customRender: ({ text }: any) => formatBytes(text),
  },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time' },
];

const gpuColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '负载%', dataIndex: 'load', key: 'load' },
  { title: '总显存(MB)', dataIndex: 'memory_total', key: 'memory_total' },
  { title: '已用(MB)', dataIndex: 'memory_used', key: 'memory_used' },
  { title: '显存利用率%', dataIndex: 'memory_util', key: 'memory_util' },
  { title: '温度(℃)', dataIndex: 'temperature', key: 'temperature' },
];

function formatBytes(val?: number) {
  if (!val && val !== 0) return '-';
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(val) / Math.log(1024));
  const v = val / Math.pow(1024, i);
  return `${v.toFixed(2)} ${sizes[i]}`;
}

function toNum(v: any): number | undefined {
  if (typeof v === 'number') return v;
  if (typeof v === 'string') {
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : undefined;
  }
  return undefined;
}

function formatBytesMaybe(v: any): string {
  const n = toNum(v);
  if (n === undefined) return '-';
  return formatBytes(n);
}

function getMemoryColor(percent: number): string {
  if (percent < 50) return '#52c41a';
  if (percent < 80) return '#faad14';
  return '#ff4d4f';
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.system-monitor {
  padding: 24px;
  background: var(--theme-page-bg, #f5f5f5);
  min-height: 100vh;

  .page-header {
    margin-bottom: 24px;
    text-align: center;

    .page-title {
      font-size: 2rem;
      font-weight: 700;
      color: var(--theme-text-primary, #1e293b);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;

      .title-icon {
        color: var(--theme-primary, #3b82f6);
      }
    }

    .page-description {
      color: var(--theme-text-secondary, #64748b);
      font-size: 1.1rem;
      margin: 0;
    }
  }

  // 监控内容
  .monitor-content {
    // 刷新按钮
    .refresh-actions {
      display: flex;
      justify-content: flex-end;
      margin-bottom: 24px;
    }

    // 概览卡片
    .overview-cards {
      margin-bottom: 24px;

      // 布局类
      &.overview-3col {
        // 3列布局（默认）
      }

      &.overview-2col {
        // 2列布局
      }

      &.overview-4col {
        // 4列布局
      }

      .monitor-card {
        background: var(--theme-card-bg, white);
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--theme-card-border, #e5e7eb);
        display: flex;
        flex-direction: column;
        height: 100%;
        min-height: 300px;

        .card-header {
          border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
          flex-shrink: 0;
          padding: 16px 20px;
          display: flex;
          align-items: center;
          gap: 12px;

          .card-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(
              135deg,
              var(--theme-primary, #3b82f6) 0%,
              var(--theme-primary, #2563eb) 100%
            );
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
          }

          .card-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin: 0;
          }
        }

        .card-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding: 20px;
          overflow: hidden;

          // 系统信息样式
          .info-grid {
            display: flex;
            flex-direction: column;
            gap: 16px;

            .info-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 12px 16px;
              background: var(--theme-content-bg, #f8fafc);
              border-radius: 8px;
              border-left: 4px solid var(--theme-primary, #3b82f6);

              .info-label {
                font-size: 14px;
                color: var(--theme-text-secondary, #64748b);
                font-weight: 500;
              }

              .info-value {
                font-size: 14px;
                color: var(--theme-text-primary, #1e293b);
                font-weight: 600;
              }
            }
          }

          // CPU统计样式
          .cpu-stats {
            display: flex;
            gap: 24px;
            margin-bottom: 20px;

            .stat-item {
              text-align: center;
              flex: 1;

              .stat-value {
                font-size: 2rem;
                font-weight: 700;
                color: var(--theme-text-primary, #1e293b);
                margin-bottom: 4px;

                &.cpu-usage {
                  color: var(--theme-primary, #3b82f6);
                }
              }

              .stat-label {
                font-size: 14px;
                color: var(--theme-text-secondary, #64748b);
                font-weight: 500;
              }
            }
          }

          .cpu-details {
            display: flex;
            flex-direction: column;
            gap: 12px;

            .detail-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 8px 12px;
              background: var(--theme-content-bg, #f8fafc);
              border-radius: 6px;

              .detail-label {
                font-size: 13px;
                color: var(--theme-text-secondary, #64748b);
              }

              .detail-value {
                font-size: 13px;
                color: var(--theme-text-primary, #1e293b);
                font-weight: 600;
              }
            }
          }

          // 内存进度样式
          .memory-progress {
            position: relative;
            margin-bottom: 20px;

            .progress-text {
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              font-size: 16px;
              font-weight: 700;
              color: var(--theme-text-primary, #1e293b);
            }
          }

          .memory-details {
            display: flex;
            flex-direction: column;
            gap: 12px;

            .memory-item {
              display: flex;
              justify-content: space-between;
              align-items: center;
              padding: 8px 12px;
              background: var(--theme-content-bg, #f8fafc);
              border-radius: 6px;

              .memory-label {
                font-size: 13px;
                color: var(--theme-text-secondary, #64748b);
              }

              .memory-value {
                font-size: 13px;
                color: var(--theme-text-primary, #1e293b);
                font-weight: 600;
              }
            }
          }

          // GPU不可用样式
          .gpu-unavailable {
            margin-bottom: 16px;
          }

          .gpu-timestamp {
            font-size: 12px;
            color: var(--theme-text-secondary, #64748b);
            text-align: center;
            margin-top: 12px;
          }
        }
      }
    }

    // 详细监控区域
    .detail-sections {
      // 布局类
      &.detail-2col {
        // 2列布局（默认）
      }

      &.detail-full {
        // 全宽布局
      }

      &.detail-side {
        // 并排布局
      }

      .monitor-card {
        background: var(--theme-card-bg, white);
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--theme-card-border, #e5e7eb);
        display: flex;
        flex-direction: column;
        min-height: 400px;
        height: 100%;

        .card-header {
          border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
          flex-shrink: 0;
          padding: 16px 20px;
          display: flex;
          align-items: center;
          gap: 12px;

          .card-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(
              135deg,
              var(--theme-primary, #3b82f6) 0%,
              var(--theme-primary, #2563eb) 100%
            );
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
          }

          .card-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin: 0;
          }
        }

        .card-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding: 20px;
          overflow: hidden;

          // 表格样式优化
          :deep(.ant-table) {
            .ant-table-thead > tr > th {
              background: var(--theme-content-bg, #f8fafc);
              border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
              font-weight: 600;
              color: var(--theme-text-primary, #1e293b);
            }

            .ant-table-tbody > tr > td {
              border-bottom: 1px solid var(--theme-card-border, #f1f5f9);
            }

            .ant-table-tbody > tr:hover > td {
              background: var(--theme-content-bg, #f8fafc);
            }
          }
        }
      }
    }
  }
}
</style>
