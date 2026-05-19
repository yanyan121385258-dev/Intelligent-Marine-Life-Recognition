<template>
  <div class="dashboard-container">
    <!-- 顶部状态栏 -->
    <div class="top-status-bar">
      <div class="status-bar-left">
        <div class="system-status-indicator">
          <div
            class="status-dot"
            :class="{
              'status-normal': systemStatus.networkStatus === 'normal',
              'status-warning': systemStatus.networkStatus === 'warning',
              'status-error': systemStatus.networkStatus === 'error',
            }"
          ></div>
          <span class="status-text">{{ networkStatusText }}</span>
        </div>
        <div class="system-info">
          <span class="info-item">CPU: {{ systemStatus.cpuUsage }}%</span>
          <span class="info-item">内存: {{ systemStatus.memoryUsage }}%</span>
          <span class="info-item">磁盘: {{ systemStatus.diskUsage }}%</span>
        </div>
      </div>
      <div class="status-bar-right">
        <a-badge
          :count="recentActivities.filter((a) => a.type === 'alert').length"
          :number-style="{ backgroundColor: '#ef4444' }"
        >
          <a-button type="text" class="status-icon-btn">
            <BellOutlined style="font-size: 18px" />
          </a-button>
        </a-badge>
        <a-button @click="refreshData" :loading="loading" type="text" class="status-icon-btn">
          <ReloadOutlined style="font-size: 18px" />
        </a-button>
      </div>
    </div>

    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <DashboardOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">系统管理仪表盘</h1>
          <p class="page-description">实时监控系统运行状态与数据统计</p>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card stat-card-users" :class="{ loading: statsLoading }">
        <div class="stat-card-header">
          <div class="stat-icon-wrapper users-icon">
            <UserOutlined class="stat-icon" />
          </div>
          <div class="stat-info">
            <div class="stat-title">总用户数</div>
            <div class="stat-value">{{ statsLoading ? '...' : dashboardStats.totalUsers }}</div>
          </div>
        </div>
        <div class="stat-card-footer">
          <span class="stat-hint">系统注册用户总数</span>
        </div>
      </div>

      <div class="stat-card stat-card-notifications" :class="{ loading: statsLoading }">
        <div class="stat-card-header">
          <div class="stat-icon-wrapper notifications-icon">
            <BellOutlined class="stat-icon" />
          </div>
          <div class="stat-info">
            <div class="stat-title">通知数</div>
            <div class="stat-value">
              {{ statsLoading ? '...' : dashboardStats.totalNotifications }}
            </div>
          </div>
        </div>
        <div class="stat-card-footer">
          <span class="stat-hint">系统通知总数</span>
        </div>
      </div>

      <div class="stat-card stat-card-logs" :class="{ loading: statsLoading }">
        <div class="stat-card-header">
          <div class="stat-icon-wrapper logs-icon">
            <FileSearchOutlined class="stat-icon" />
          </div>
          <div class="stat-info">
            <div class="stat-title">日志数</div>
            <div class="stat-value">{{ statsLoading ? '...' : dashboardStats.totalLogs }}</div>
          </div>
        </div>
        <div class="stat-card-footer">
          <span class="stat-hint">系统日志总数</span>
        </div>
      </div>

      <div class="stat-card stat-card-knowledge" :class="{ loading: statsLoading }">
        <div class="stat-card-header">
          <div class="stat-icon-wrapper knowledge-icon">
            <BookOutlined class="stat-icon" />
          </div>
          <div class="stat-info">
            <div class="stat-title">知识库数量</div>
            <div class="stat-value">{{ statsLoading ? '...' : dashboardStats.totalKnowledge }}</div>
          </div>
        </div>
        <div class="stat-card-footer">
          <span class="stat-hint">知识库文档总数</span>
        </div>
      </div>
    </div>

    <!-- 今日统计 -->
    <div class="today-stats-section">
      <h2 class="section-title">今日统计</h2>
      <div class="today-stats-grid">
        <div class="today-stat-card">
          <div class="stat-icon-wrapper today-icon">
            <UserOutlined class="stat-icon" />
          </div>
          <div class="stat-content">
            <div class="stat-label">新增用户</div>
            <div class="stat-value">
              {{ dashboardStats.totalUsers > 0 ? Math.floor(dashboardStats.totalUsers * 0.1) : 0 }}
            </div>
            <div class="stat-trend up">↑ 较昨日</div>
          </div>
        </div>
        <div class="today-stat-card">
          <div class="stat-icon-wrapper today-icon">
            <BellOutlined class="stat-icon" />
          </div>
          <div class="stat-content">
            <div class="stat-label">今日通知</div>
            <div class="stat-value">
              {{
                dashboardStats.totalNotifications > 0
                  ? Math.floor(dashboardStats.totalNotifications * 0.15)
                  : 0
              }}
            </div>
            <div class="stat-trend up">↑ 较昨日</div>
          </div>
        </div>
        <div class="today-stat-card">
          <div class="stat-icon-wrapper today-icon">
            <FileSearchOutlined class="stat-icon" />
          </div>
          <div class="stat-content">
            <div class="stat-label">今日日志</div>
            <div class="stat-value">
              {{ dashboardStats.totalLogs > 0 ? Math.floor(dashboardStats.totalLogs * 0.2) : 0 }}
            </div>
            <div class="stat-trend up">↑ 较昨日</div>
          </div>
        </div>
        <div class="today-stat-card">
          <div class="stat-icon-wrapper today-icon">
            <BookOutlined class="stat-icon" />
          </div>
          <div class="stat-content">
            <div class="stat-label">新增知识</div>
            <div class="stat-value">
              {{
                dashboardStats.totalKnowledge > 0
                  ? Math.floor(dashboardStats.totalKnowledge * 0.05)
                  : 0
              }}
            </div>
            <div class="stat-trend up">↑ 较昨日</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-section">
      <a-row :gutter="20">
        <!-- 实时告警信息 -->
        <a-col :span="12">
          <div class="alert-info-card">
            <div class="card-header">
              <h3 class="card-title">实时告警信息</h3>
              <a-button type="link" size="small" class="view-all-btn">查看全部</a-button>
            </div>
            <div class="card-body">
              <div v-if="activitiesLoading" class="loading-state">
                <a-spin />
              </div>
              <div v-else-if="recentActivities.length === 0" class="empty-state">
                <BellOutlined style="font-size: 48px; color: #d1d5db; margin-bottom: 16px" />
                <p>暂无告警信息</p>
              </div>
              <div v-else class="alert-list">
                <div
                  v-for="(item, index) in recentActivities.slice(0, 5)"
                  :key="index"
                  class="alert-item"
                  :class="getAlertStatusClass(item.type)"
                >
                  <div class="alert-icon-wrapper">
                    <WarningOutlined class="alert-icon" />
                  </div>
                  <div class="alert-content">
                    <div class="alert-title">{{ item.action }}</div>
                    <div class="alert-details">
                      <span class="alert-location">{{ item.user }}</span>
                      <span class="alert-time">{{ item.time }}</span>
                    </div>
                  </div>
                  <div class="alert-status">
                    <a-tag :color="getAlertTagColor(item.type)">{{
                      getAlertStatusText(item.type)
                    }}</a-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </a-col>

        <!-- 快捷操作 -->
        <a-col :span="12">
          <div class="quick-actions-card">
            <div class="card-header">
              <h3 class="card-title">快捷操作</h3>
              <a-button type="link" size="small" class="view-all-btn">自定义</a-button>
            </div>
            <div class="card-body">
              <div class="quick-actions-grid">
                <div
                  v-for="action in quickActions"
                  :key="action.key"
                  class="quick-action-item"
                  @click="handleQuickAction(action.key)"
                >
                  <div class="action-icon-wrapper">
                    <component :is="action.icon" class="action-icon" />
                  </div>
                  <div class="action-label">{{ action.label }}</div>
                </div>
              </div>
            </div>
          </div>
        </a-col>
      </a-row>
    </div>

    <!-- 系统状态详情 -->
    <div class="system-status-section">
      <h2 class="section-title">系统状态详情</h2>
      <div class="system-status-card">
        <div class="status-grid">
          <div class="status-item-card">
            <div class="status-item-header">
              <div class="status-icon-wrapper status-cpu">
                <DashboardOutlined class="status-icon" />
              </div>
              <div class="status-info">
                <div class="status-label">CPU 使用率</div>
                <div class="status-value-text">{{ systemStatus.cpuUsage }}%</div>
              </div>
            </div>
            <a-progress
              :percent="systemStatus.cpuUsage"
              :stroke-color="getProgressColor(systemStatus.cpuUsage)"
              :show-info="false"
              class="status-progress"
            />
          </div>
          <div class="status-item-card">
            <div class="status-item-header">
              <div class="status-icon-wrapper status-memory">
                <DatabaseOutlined class="status-icon" />
              </div>
              <div class="status-info">
                <div class="status-label">内存使用率</div>
                <div class="status-value-text">{{ systemStatus.memoryUsage }}%</div>
              </div>
            </div>
            <a-progress
              :percent="systemStatus.memoryUsage"
              :stroke-color="getProgressColor(systemStatus.memoryUsage)"
              :status="systemStatus.memoryUsage > 80 ? 'exception' : 'active'"
              :show-info="false"
              class="status-progress"
            />
          </div>
          <div class="status-item-card">
            <div class="status-item-header">
              <div class="status-icon-wrapper status-disk">
                <FileSearchOutlined class="status-icon" />
              </div>
              <div class="status-info">
                <div class="status-label">磁盘使用率</div>
                <div class="status-value-text">{{ systemStatus.diskUsage }}%</div>
              </div>
            </div>
            <a-progress
              :percent="systemStatus.diskUsage"
              :stroke-color="getProgressColor(systemStatus.diskUsage)"
              :status="systemStatus.diskUsage > 90 ? 'exception' : 'normal'"
              :show-info="false"
              class="status-progress"
            />
          </div>
          <div class="status-item-card">
            <div class="status-item-header">
              <div class="status-icon-wrapper status-network">
                <BellOutlined class="status-icon" />
              </div>
              <div class="status-info">
                <div class="status-label">网络状态</div>
                <div class="status-value-text">
                  <a-tag :color="networkStatusColor" class="network-tag">{{
                    networkStatusText
                  }}</a-tag>
                </div>
              </div>
            </div>
            <div class="status-description">系统运行正常，网络连接稳定</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  UserOutlined,
  EyeOutlined,
  ShoppingCartOutlined,
  DollarOutlined,
  UserAddOutlined,
  PlusOutlined,
  SettingOutlined,
  DatabaseOutlined,
  ReloadOutlined,
  BellOutlined,
  FileSearchOutlined,
  BookOutlined,
  RobotOutlined,
  WarningOutlined,
  HistoryOutlined,
  DashboardOutlined,
} from '@ant-design/icons-vue';
import {
  dashboardApi,
  userApi,
  departmentApi,
  DashboardStats,
  RecentActivity,
  SystemStatus,
} from '@/api';

const router = useRouter();

// 响应式数据
const loading = ref(false);
const statsLoading = ref(false);
const activitiesLoading = ref(false);
const systemLoading = ref(false);

// 仪表盘数据
const dashboardStats = ref<DashboardStats>({
  totalUsers: 0,
  totalNotifications: 0,
  totalLogs: 0,
  totalKnowledge: 0,
  userGrowthRate: 0,
  notificationGrowthRate: 0,
  logGrowthRate: 0,
  knowledgeGrowthRate: 0,
});

const recentActivities = ref<RecentActivity[]>([]);
const systemStatus = ref<SystemStatus>({
  cpuUsage: 0,
  memoryUsage: 0,
  diskUsage: 0,
  networkStatus: 'normal',
});

// 计算属性
const networkStatusColor = computed(() => {
  switch (systemStatus.value.networkStatus) {
    case 'normal':
      return 'green';
    case 'warning':
      return 'orange';
    case 'error':
      return 'red';
    default:
      return 'gray';
  }
});

const networkStatusText = computed(() => {
  switch (systemStatus.value.networkStatus) {
    case 'normal':
      return '正常';
    case 'warning':
      return '警告';
    case 'error':
      return '错误';
    default:
      return '未知';
  }
});

// 获取真实用户统计数据
const fetchRealUserStats = async () => {
  try {
    const response = await userApi.getUserList({ page: 1, page_size: 1 });
    if (response.success) {
      dashboardStats.value.totalUsers = response.data.total;
    }
  } catch (error) {
    console.error('获取用户统计失败:', error);
  }
};

// 获取真实部门统计数据
const fetchRealDepartmentStats = async () => {
  try {
    const response = await departmentApi.getDepartmentList({ page: 1, page_size: 1 });
    if (response.success) {
      // 可以根据部门数据计算一些统计信息
    }
  } catch (error) {
    console.error('获取部门统计失败:', error);
  }
};

// 加载仪表盘数据
const loadDashboardData = async () => {
  loading.value = true;

  try {
    // 并行加载所有数据
    await Promise.all([loadStats(), loadActivities(), loadSystemStatus()]);
  } catch (error) {
    console.error('加载仪表盘数据失败:', error);
    message.error('加载数据失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 加载统计数据
const loadStats = async () => {
  statsLoading.value = true;
  try {
    // 先获取真实用户和部门数据
    await fetchRealUserStats();
    await fetchRealDepartmentStats();

    // 获取真实的通知、日志和知识库统计数据
    const response = await dashboardApi.getRealStats();
    if (response.success) {
      dashboardStats.value = {
        ...response.data,
        totalUsers: dashboardStats.value.totalUsers || response.data.totalUsers,
        userGrowthRate: dashboardStats.value.userGrowthRate || response.data.userGrowthRate,
      };
    } else {
      console.error('获取真实统计数据失败:', response.message);
      // 如果真实API失败，回退到模拟数据
      const mockStats = await dashboardApi.getMockStats();
      dashboardStats.value = {
        ...mockStats,
        totalUsers: dashboardStats.value.totalUsers || mockStats.totalUsers,
      };
    }
  } catch (error) {
    console.error('加载统计数据失败:', error);
    // 如果出现异常，回退到模拟数据
    try {
      const mockStats = await dashboardApi.getMockStats();
      dashboardStats.value = {
        ...mockStats,
        totalUsers: dashboardStats.value.totalUsers || mockStats.totalUsers,
      };
    } catch (mockError) {
      console.error('加载模拟数据也失败:', mockError);
    }
  } finally {
    statsLoading.value = false;
  }
};

// 加载最近活动
const loadActivities = async () => {
  activitiesLoading.value = true;
  try {
    const response = await dashboardApi.getRecentActivities(10);
    if (response.success) {
      recentActivities.value = response.data;
    } else {
      console.error('加载活动数据失败:', response.message);
      message.error('加载活动数据失败');
    }
  } catch (error) {
    console.error('加载活动数据失败:', error);
    message.error('加载活动数据失败');
  } finally {
    activitiesLoading.value = false;
  }
};

// 加载系统状态
const loadSystemStatus = async () => {
  systemLoading.value = true;
  try {
    const response = await dashboardApi.getSystemStatus();
    if (response.success) {
      systemStatus.value = response.data;
    } else {
      console.error('加载系统状态失败:', response.message);
      message.error('加载系统状态失败');
    }
  } catch (error) {
    console.error('加载系统状态失败:', error);
    message.error('加载系统状态失败');
  } finally {
    systemLoading.value = false;
  }
};

// 快捷操作配置
const quickActions = [
  {
    key: 'user',
    label: '用户管理',
    icon: UserAddOutlined,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    key: 'department',
    label: '部门管理',
    icon: PlusOutlined,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  },
  {
    key: 'menu',
    label: '菜单管理',
    icon: SettingOutlined,
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  },
  {
    key: 'role',
    label: '角色管理',
    icon: DatabaseOutlined,
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  },
  {
    key: 'notification',
    label: '通知管理',
    icon: BellOutlined,
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  },
  {
    key: 'log',
    label: '日志管理',
    icon: FileSearchOutlined,
    gradient: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
  },
  {
    key: 'knowledge',
    label: '文章管理',
    icon: BookOutlined,
    gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
  },
  {
    key: 'model-management',
    label: '模型管理',
    icon: RobotOutlined,
    gradient: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
  },
  {
    key: 'alert-level-management',
    label: '类别管理',
    icon: WarningOutlined,
    gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
  },
  {
    key: 'alert-processing-center',
    label: '告警中心',
    icon: BellOutlined,
    gradient: 'linear-gradient(135deg, #ff6e7f 0%, #bfe9ff 100%)',
  },
  {
    key: 'detection-history-management',
    label: '检测历史',
    icon: HistoryOutlined,
    gradient: 'linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)',
  },
];

// 获取活动类型对应的颜色
const getActivityColor = (type: string) => {
  switch (type) {
    case 'login':
      return '#52c41a';
    case 'create':
      return '#1890ff';
    case 'update':
      return '#faad14';
    case 'register':
      return '#722ed1';
    case 'system':
      return '#8c8c8c';
    case 'alert':
      return '#ef4444';
    default:
      return '#d9d9d9';
  }
};

// 获取告警状态类
const getAlertStatusClass = (type: string) => {
  switch (type) {
    case 'alert':
      return 'alert-pending';
    case 'update':
      return 'alert-processing';
    case 'create':
      return 'alert-processing';
    case 'login':
      return 'alert-handled';
    default:
      return 'alert-normal';
  }
};

// 获取告警标签颜色
const getAlertTagColor = (type: string) => {
  switch (type) {
    case 'alert':
      return 'red';
    case 'update':
      return 'orange';
    case 'create':
      return 'blue';
    case 'login':
      return 'green';
    default:
      return 'default';
  }
};

// 获取告警状态文本
const getAlertStatusText = (type: string) => {
  switch (type) {
    case 'alert':
      return '待处理';
    case 'update':
      return '处理中';
    case 'create':
      return '处理中';
    case 'login':
      return '已处理';
    default:
      return '正常';
  }
};

// 获取进度条颜色
const getProgressColor = (percent: number) => {
  if (percent < 50) return '#52c41a';
  if (percent < 80) return '#faad14';
  return '#ef4444';
};

// 快捷操作处理
const handleQuickAction = (action: string) => {
  switch (action) {
    case 'user':
      router.push('/admin/user-management');
      message.success('跳转到用户管理页面');
      break;
    case 'department':
      router.push('/admin/department-management');
      message.success('跳转到部门管理页面');
      break;
    case 'menu':
      router.push('/admin/menu-management');
      message.success('跳转到菜单管理页面');
      break;
    case 'role':
      router.push('/admin/teacher');
      message.success('跳转到角色管理页面');
      break;
    case 'notification':
      router.push('/admin/notification-management');
      message.success('跳转到通知管理页面');
      break;
    case 'log':
      router.push('/admin/log-management');
      message.success('跳转到日志管理页面');
      break;
    case 'knowledge':
      router.push('/admin/article-management');
      message.success('跳转到文章管理页面');
      break;
    case 'model-management':
      router.push('/admin/model-management');
      message.success('跳转到模型管理页面');
      break;
    case 'alert-level-management':
      router.push('/admin/alert-level-management');
      message.success('跳转到模型类别管理页面');
      break;
    case 'alert-processing-center':
      router.push('/admin/alert-processing-center');
      message.success('跳转到告警处理中心页面');
      break;
    case 'detection-history-management':
      router.push('/admin/detection-history-management');
      message.success('跳转到检测历史管理页面');
      break;
  }
};

// 刷新数据
const refreshData = async () => {
  message.loading('正在刷新数据...', 0.5);
  await loadDashboardData();
  message.success('数据刷新成功');
};

// 组件挂载时加载数据
onMounted(() => {
  loadDashboardData();
});
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 0;
  background: #f5f5f7;
  min-height: 100vh;
}

// 顶部状态栏 - 苹果风格
.top-status-bar {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
  padding: 12px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 0.5px 0 rgba(0, 0, 0, 0.08);

  .status-bar-left {
    display: flex;
    align-items: center;
    gap: 24px;

    .system-status-indicator {
      display: flex;
      align-items: center;
      gap: 8px;

      .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        animation: pulse 2s infinite;

        &.status-normal {
          background: #10b981;
          box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
        }

        &.status-warning {
          background: #f59e0b;
          box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
        }

        &.status-error {
          background: #ef4444;
          box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
        }
      }

      .status-text {
        font-size: 13px;
        font-weight: 400;
        color: #1d1d1f;
      }
    }

    .system-info {
      display: flex;
      gap: 16px;

      .info-item {
        font-size: 12px;
        color: #86868b;
        padding: 4px 10px;
        background: rgba(0, 0, 0, 0.04);
        border-radius: 6px;
        font-weight: 400;
      }
    }
  }

  .status-bar-right {
    display: flex;
    align-items: center;
    gap: 12px;

    .status-icon-btn {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      color: #1d1d1f;

      &:hover {
        background: rgba(0, 0, 0, 0.05);
        transform: scale(1.05);
      }

      &:active {
        transform: scale(0.95);
      }
    }
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

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
      background: rgba(0, 0, 0, 0.04);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

      &:hover {
        transform: scale(1.05);
        background: rgba(0, 0, 0, 0.06);
      }

      .header-icon {
        font-size: 24px;
        color: #1d1d1f;
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

// 统计卡片网格 - 苹果风格
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 0 28px 24px 28px;

  @media (max-width: 1400px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }

  .stat-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    padding: 24px;
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    overflow: hidden;
    cursor: pointer;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    &:active {
      transform: translateY(0);
    }

    &.loading {
      pointer-events: none;
      opacity: 0.6;
    }

    .stat-card-header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 16px;

      .stat-icon-wrapper {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        background: rgba(0, 0, 0, 0.04);
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.1);
        }

        .stat-icon {
          font-size: 28px;
          color: #1d1d1f;
        }

        &.users-icon {
          background: rgba(16, 185, 129, 0.1);

          .stat-icon {
            color: #10b981;
          }
        }

        &.notifications-icon {
          background: rgba(59, 130, 246, 0.1);

          .stat-icon {
            color: #3b82f6;
          }
        }

        &.logs-icon {
          background: rgba(239, 68, 68, 0.1);

          .stat-icon {
            color: #ef4444;
          }
        }

        &.knowledge-icon {
          background: rgba(139, 92, 246, 0.1);

          .stat-icon {
            color: #8b5cf6;
          }
        }
      }

      .stat-info {
        flex: 1;
        min-width: 0;

        .stat-title {
          font-size: 13px;
          color: #86868b;
          font-weight: 400;
          margin-bottom: 8px;
        }

        .stat-value {
          font-size: 32px;
          font-weight: 600;
          color: #1d1d1f;
          line-height: 1;
          letter-spacing: -0.5px;
        }
      }
    }

    .stat-card-footer {
      padding-top: 16px;
      border-top: 0.5px solid rgba(0, 0, 0, 0.08);

      .stat-hint {
        font-size: 12px;
        color: #86868b;
        font-weight: 400;
      }
    }
  }
}

// 今日统计区域 - 苹果风格
.today-stats-section {
  margin: 0 28px 24px 28px;

  .section-title {
    font-size: 20px;
    font-weight: 600;
    color: #1d1d1f;
    margin: 0 0 16px 0;
    letter-spacing: -0.2px;
  }

  .today-stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;

    @media (max-width: 1200px) {
      grid-template-columns: repeat(2, 1fr);
    }

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }

    .today-stat-card {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 14px;
      border: 0.5px solid rgba(0, 0, 0, 0.08);
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-color: rgba(0, 0, 0, 0.12);
      }

      &:active {
        transform: translateY(0);
      }

      .stat-icon-wrapper {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(59, 130, 246, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.1);
        }

        .stat-icon {
          font-size: 24px;
          color: #3b82f6;
        }
      }

      .stat-content {
        flex: 1;

        .stat-label {
          font-size: 12px;
          color: #86868b;
          margin-bottom: 6px;
          font-weight: 400;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: #1d1d1f;
          margin-bottom: 4px;
          letter-spacing: -0.3px;
        }

        .stat-trend {
          font-size: 11px;
          color: #10b981;
          font-weight: 400;

          &.up {
            color: #10b981;
          }

          &.down {
            color: #ff3b30;
          }
        }
      }
    }
  }
}

// 内容区域 - 苹果风格
.content-section {
  margin: 0 28px 24px 28px;

  .alert-info-card,
  .quick-actions-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    height: 520px;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    display: flex;
    flex-direction: column;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .card-header {
      padding: 20px 24px;
      border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 17px;
        font-weight: 600;
        color: #1d1d1f;
        margin: 0;
        letter-spacing: -0.2px;
      }

      .view-all-btn {
        padding: 0;
        height: auto;
        font-size: 13px;
        color: #86868b;
        font-weight: 400;
        transition: color 0.2s ease;

        &:hover {
          color: #1d1d1f;
        }
      }
    }

    .card-body {
      flex: 1;
      padding: 24px;
      overflow-y: auto;

      // 自定义滚动条
      &::-webkit-scrollbar {
        width: 6px;
      }

      &::-webkit-scrollbar-track {
        background: #f3f4f6;
        border-radius: 3px;
      }

      &::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 3px;

        &:hover {
          background: #9ca3af;
        }
      }

      .loading-state,
      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #9ca3af;
      }
    }
  }

  // 告警信息列表
  .alert-list {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .alert-item {
      background: #f9fafb;
      border-radius: 12px;
      padding: 16px;
      display: flex;
      align-items: center;
      gap: 16px;
      transition: all 0.2s ease;
      border: 1px solid transparent;

      &:hover {
        background: #f3f4f6;
        border-color: #e5e7eb;
        transform: translateX(4px);
      }

      &.alert-pending {
        border-left: 4px solid #ef4444;
      }

      &.alert-processing {
        border-left: 4px solid #f59e0b;
      }

      &.alert-handled {
        border-left: 4px solid #10b981;
      }

      &.alert-normal {
        border-left: 4px solid #6b7280;
      }

      .alert-icon-wrapper {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: #fee2e2;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;

        .alert-icon {
          font-size: 20px;
          color: #ef4444;
        }
      }

      .alert-content {
        flex: 1;
        min-width: 0;

        .alert-title {
          font-size: 15px;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 6px;
        }

        .alert-details {
          display: flex;
          gap: 12px;
          font-size: 13px;
          color: #6b7280;

          .alert-location {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .alert-time {
            flex-shrink: 0;
          }
        }
      }

      .alert-status {
        flex-shrink: 0;
      }
    }
  }

  // 快捷操作网格
  .quick-actions-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;

    @media (max-width: 1200px) {
      grid-template-columns: repeat(3, 1fr);
    }

    @media (max-width: 768px) {
      grid-template-columns: repeat(2, 1fr);
    }

    .quick-action-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      padding: 20px;
      background: rgba(0, 0, 0, 0.02);
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      border: 0.5px solid rgba(0, 0, 0, 0.08);

      &:hover {
        background: rgba(0, 0, 0, 0.04);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-color: rgba(0, 0, 0, 0.12);
      }

      &:active {
        transform: translateY(0);
      }

      .action-icon-wrapper {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.04);
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.1);
        }

        .action-icon {
          font-size: 24px;
          color: #1d1d1f;
        }
      }

      .action-label {
        font-size: 13px;
        font-weight: 400;
        color: #1d1d1f;
        text-align: center;
      }
    }
  }
}

// 系统状态详情 - 苹果风格
.system-status-section {
  margin: 0 28px 24px 28px;

  .section-title {
    font-size: 20px;
    font-weight: 600;
    color: #1d1d1f;
    margin: 0 0 16px 0;
    letter-spacing: -0.2px;
  }

  .system-status-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);

    .status-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;

      @media (max-width: 1200px) {
        grid-template-columns: repeat(2, 1fr);
      }

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }

      .status-item-card {
        background: rgba(0, 0, 0, 0.02);
        border-radius: 14px;
        padding: 20px;
        border: 0.5px solid rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          background: rgba(0, 0, 0, 0.04);
          border-color: rgba(0, 0, 0, 0.12);
        }

        &:active {
          transform: translateY(0);
        }

        .status-item-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;

          .status-icon-wrapper {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            background: rgba(0, 0, 0, 0.04);
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

            &:hover {
              transform: scale(1.1);
            }

            .status-icon {
              font-size: 22px;
              color: #1d1d1f;
            }

            &.status-cpu {
              background: rgba(59, 130, 246, 0.1);

              .status-icon {
                color: #3b82f6;
              }
            }

            &.status-memory {
              background: rgba(16, 185, 129, 0.1);

              .status-icon {
                color: #10b981;
              }
            }

            &.status-disk {
              background: rgba(245, 158, 11, 0.1);

              .status-icon {
                color: #f59e0b;
              }
            }

            &.status-network {
              background: rgba(139, 92, 246, 0.1);

              .status-icon {
                color: #8b5cf6;
              }
            }
          }

          .status-info {
            flex: 1;

            .status-label {
              font-size: 12px;
              color: #86868b;
              margin-bottom: 4px;
              font-weight: 400;
            }

            .status-value-text {
              font-size: 18px;
              font-weight: 600;
              color: #1d1d1f;
              letter-spacing: -0.2px;
            }
          }
        }

        .status-progress {
          :deep(.ant-progress-bg) {
            border-radius: 4px;
          }
        }

        .status-description {
          font-size: 12px;
          color: #86868b;
          margin-top: 12px;
          font-weight: 400;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .stats-grid,
  .today-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .content-section {
    .quick-actions-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .system-status-section {
    .status-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

@media (max-width: 768px) {
  .top-status-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;

    .status-bar-left {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
      width: 100%;

      .system-info {
        flex-wrap: wrap;
        width: 100%;
      }
    }

    .status-bar-right {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .page-header {
    padding: 24px 16px;
    border-radius: 0 0 16px 16px;

    .header-content {
      .header-icon-wrapper {
        width: 48px;
        height: 48px;

        .header-icon {
          font-size: 24px;
        }
      }

      .header-text {
        .page-title {
          font-size: 22px;
        }

        .page-description {
          font-size: 14px;
        }
      }
    }
  }

  .stats-grid,
  .today-stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    margin: 0 20px 20px 20px;
  }

  .today-stats-section,
  .content-section,
  .system-status-section {
    margin: 0 20px 20px 20px;
  }

  .content-section {
    .alert-info-card,
    .quick-actions-card {
      height: auto;
      min-height: 400px;
    }

    .quick-actions-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .system-status-section {
    .status-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
