import { request } from '@/utils/hertz_request';
import { logApi, type OperationLogItem } from './log';
import {
  systemMonitorApi,
  type SystemInfo,
  type CpuInfo,
  type MemoryInfo,
  type DiskInfo,
} from './system_monitor';
import { noticeUserApi } from './notice_user';
import { knowledgeApi } from './knowledge';

// 仪表盘统计数据类型定义
export interface DashboardStats {
  totalUsers: number;
  totalNotifications: number;
  totalLogs: number;
  totalKnowledge: number;
  userGrowthRate: number;
  notificationGrowthRate: number;
  logGrowthRate: number;
  knowledgeGrowthRate: number;
}

// 最近活动数据类型
export interface RecentActivity {
  id: number;
  action: string;
  time: string;
  user: string;
  type: 'login' | 'create' | 'update' | 'system' | 'register';
}

// 系统状态数据类型
export interface SystemStatus {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  networkStatus: 'normal' | 'warning' | 'error';
}

// 访问趋势数据类型
export interface VisitTrend {
  date: string;
  visits: number;
  users: number;
}

// 仪表盘数据汇总类型
export interface DashboardData {
  stats: DashboardStats;
  recentActivities: RecentActivity[];
  systemStatus: SystemStatus;
  visitTrends: VisitTrend[];
}

// API响应类型
export interface ApiResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T;
}

// 仪表盘API接口
export const dashboardApi = {
  // 获取仪表盘统计数据
  getStats: (): Promise<ApiResponse<DashboardStats>> => {
    return request.get('/api/dashboard/stats/');
  },

  // 获取真实统计数据
  getRealStats: async (): Promise<ApiResponse<DashboardStats>> => {
    try {
      // 并行获取各种统计数据
      const [notificationStats, logStats, knowledgeStats] = await Promise.all([
        noticeUserApi
          .statistics()
          .catch(() => ({ success: false, data: { total_count: 0, unread_count: 0 } })),
        logApi
          .getList({ page: 1, page_size: 1 })
          .catch(() => ({ success: false, data: { count: 0 } })),
        knowledgeApi
          .getArticles({ page: 1, page_size: 1 })
          .catch(() => ({ success: false, data: { total: 0 } })),
      ]);

      // 计算统计数据
      const totalNotifications = notificationStats.success
        ? notificationStats.data.total_count || 0
        : 0;

      // 处理日志数据 - 兼容多种返回结构
      let totalLogs = 0;
      if (logStats.success && logStats.data) {
        const logData = logStats.data as any;
        console.log('日志API响应数据:', logData);
        // 兼容DRF标准结构：{ count, next, previous, results }
        if ('count' in logData) {
          totalLogs = Number(logData.count) || 0;
        } else if ('total' in logData) {
          totalLogs = Number(logData.total) || 0;
        } else if ('total_count' in logData) {
          totalLogs = Number(logData.total_count) || 0;
        } else if (logData.pagination && logData.pagination.total_count) {
          totalLogs = Number(logData.pagination.total_count) || 0;
        }
        console.log('解析出的日志总数:', totalLogs);
      } else {
        console.log('日志API调用失败:', logStats);
      }

      const totalKnowledge = knowledgeStats.success ? knowledgeStats.data.total || 0 : 0;

      console.log('统计数据汇总:', { totalNotifications, totalLogs, totalKnowledge });

      // 模拟增长率（实际项目中应该从后端获取）
      const stats: DashboardStats = {
        totalUsers: 0, // 暂时设为0，需要用户管理API
        totalNotifications,
        totalLogs,
        totalKnowledge,
        userGrowthRate: 0,
        notificationGrowthRate: Math.floor(Math.random() * 20) - 10, // 模拟 -10% 到 +10%
        logGrowthRate: Math.floor(Math.random() * 30) - 15, // 模拟 -15% 到 +15%
        knowledgeGrowthRate: Math.floor(Math.random() * 25) - 12, // 模拟 -12% 到 +13%
      };

      return {
        success: true,
        code: 200,
        message: 'success',
        data: stats,
      };
    } catch (error) {
      console.error('获取真实统计数据失败:', error);
      return {
        success: false,
        code: 500,
        message: '获取统计数据失败',
        data: {
          totalUsers: 0,
          totalNotifications: 0,
          totalLogs: 0,
          totalKnowledge: 0,
          userGrowthRate: 0,
          notificationGrowthRate: 0,
          logGrowthRate: 0,
          knowledgeGrowthRate: 0,
        },
      };
    }
  },

  // 获取最近活动（从日志接口）
  getRecentActivities: async (limit: number = 10): Promise<ApiResponse<RecentActivity[]>> => {
    try {
      const response = await logApi.getList({ page: 1, page_size: limit });
      if (response.success && response.data) {
        // 根据实际API响应结构，数据可能在data.logs或data.results中
        const logs = (response.data as any).logs || (response.data as any).results || [];
        const activities: RecentActivity[] = logs.map((log: any) => ({
          id: log.log_id || log.id,
          action:
            log.description ||
            log.operation_description ||
            `${log.action_type_display || log.operation_type} - ${log.module || log.operation_module}`,
          time: formatTimeAgo(log.created_at),
          user: log.username || log.user?.username || '未知用户',
          type: mapLogTypeToActivityType(log.action_type || log.operation_type),
        }));
        return {
          success: true,
          code: 200,
          message: 'success',
          data: activities,
        };
      }
      // API调用成功但返回失败时，返回空数组而不是失败响应
      console.warn('日志API返回失败，返回空活动数组:', response?.message);
      return {
        success: true,
        code: 200,
        message: 'success',
        data: [],
      };
    } catch (error) {
      // API调用失败时，返回空数组而不是失败响应
      console.warn('获取日志数据失败，返回空活动数组:', error);
      return {
        success: true,
        code: 200,
        message: 'success',
        data: [],
      };
    }
  },

  // 获取系统状态（从系统监控接口）
  getSystemStatus: async (): Promise<ApiResponse<SystemStatus>> => {
    try {
      const [cpuResponse, memoryResponse, disksResponse] = await Promise.all([
        systemMonitorApi.getCpu(),
        systemMonitorApi.getMemory(),
        systemMonitorApi.getDisks(),
      ]);

      if (cpuResponse.success && memoryResponse.success && disksResponse.success) {
        // 根据实际API响应结构映射数据
        const systemStatus: SystemStatus = {
          // CPU使用率：从 cpu_percent 字段获取
          cpuUsage: Math.round(cpuResponse.data.cpu_percent || 0),
          // 内存使用率：从 percent 字段获取
          memoryUsage: Math.round(memoryResponse.data.percent || 0),
          // 磁盘使用率：从磁盘数组的第一个磁盘的 percent 字段获取
          diskUsage:
            disksResponse.data.length > 0 ? Math.round(disksResponse.data[0].percent || 0) : 0,
          networkStatus: 'normal' as const,
        };

        return {
          success: true,
          code: 200,
          message: 'success',
          data: systemStatus,
        };
      }

      return {
        success: false,
        code: 500,
        message: '获取系统状态失败',
        data: {
          cpuUsage: 0,
          memoryUsage: 0,
          diskUsage: 0,
          networkStatus: 'error' as const,
        },
      };
    } catch (error) {
      console.error('获取系统状态失败:', error);
      return {
        success: false,
        code: 500,
        message: '获取系统状态失败',
        data: {
          cpuUsage: 0,
          memoryUsage: 0,
          diskUsage: 0,
          networkStatus: 'error' as const,
        },
      };
    }
  },

  // 获取访问趋势
  getVisitTrends: (
    period: 'week' | 'month' | 'year' = 'week'
  ): Promise<ApiResponse<VisitTrend[]>> => {
    return request.get('/api/dashboard/visit-trends/', { params: { period } });
  },

  // 获取完整仪表盘数据
  getDashboardData: (): Promise<ApiResponse<DashboardData>> => {
    return request.get('/api/dashboard/overview/');
  },

  // 模拟数据方法（用于开发阶段）
  getMockStats: (): Promise<DashboardStats> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          totalUsers: 1128,
          totalNotifications: 234,
          totalLogs: 893,
          totalKnowledge: 156,
          userGrowthRate: 12,
          notificationGrowthRate: 8,
          logGrowthRate: -3,
          knowledgeGrowthRate: 15,
        });
      }, 500);
    });
  },

  getMockActivities: (): Promise<RecentActivity[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            id: 1,
            action: '用户 张三 登录了系统',
            time: '2分钟前',
            user: '张三',
            type: 'login',
          },
          {
            id: 2,
            action: '管理员 李四 创建了新部门',
            time: '5分钟前',
            user: '李四',
            type: 'create',
          },
          {
            id: 3,
            action: '用户 王五 修改了个人信息',
            time: '10分钟前',
            user: '王五',
            type: 'update',
          },
          {
            id: 4,
            action: '系统自动备份完成',
            time: '1小时前',
            user: '系统',
            type: 'system',
          },
          {
            id: 5,
            action: '新用户 赵六 注册成功',
            time: '2小时前',
            user: '赵六',
            type: 'register',
          },
        ]);
      }, 300);
    });
  },

  getMockSystemStatus: (): Promise<SystemStatus> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          cpuUsage: 45,
          memoryUsage: 67,
          diskUsage: 32,
          networkStatus: 'normal',
        });
      }, 200);
    });
  },

  getMockVisitTrends: (period: 'week' | 'month' | 'year' = 'week'): Promise<VisitTrend[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const data = {
          week: [
            { date: '周一', visits: 120, users: 80 },
            { date: '周二', visits: 150, users: 95 },
            { date: '周三', visits: 180, users: 110 },
            { date: '周四', visits: 200, users: 130 },
            { date: '周五', visits: 250, users: 160 },
            { date: '周六', visits: 180, users: 120 },
            { date: '周日', visits: 160, users: 100 },
          ],
          month: [
            { date: '第1周', visits: 800, users: 500 },
            { date: '第2周', visits: 950, users: 600 },
            { date: '第3周', visits: 1100, users: 700 },
            { date: '第4周', visits: 1200, users: 750 },
          ],
          year: [
            { date: '1月', visits: 3200, users: 2000 },
            { date: '2月', visits: 3800, users: 2400 },
            { date: '3月', visits: 4200, users: 2600 },
            { date: '4月', visits: 3900, users: 2300 },
            { date: '5月', visits: 4500, users: 2800 },
            { date: '6月', visits: 5000, users: 3100 },
          ],
        };
        resolve(data[period]);
      }, 400);
    });
  },
};

// 辅助函数：格式化时间为相对时间
function formatTimeAgo(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return `${diffInSeconds}秒前`;
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes}分钟前`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours}小时前`;
  } else {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days}天前`;
  }
}

// 辅助函数：将日志操作类型映射为活动类型
function mapLogTypeToActivityType(operationType: string): RecentActivity['type'] {
  if (!operationType) return 'system';

  const lowerType = operationType.toLowerCase();

  if (lowerType.includes('login') || lowerType.includes('登录')) {
    return 'login';
  } else if (
    lowerType.includes('create') ||
    lowerType.includes('创建') ||
    lowerType.includes('add') ||
    lowerType.includes('新增')
  ) {
    return 'create';
  } else if (
    lowerType.includes('update') ||
    lowerType.includes('修改') ||
    lowerType.includes('edit') ||
    lowerType.includes('更新')
  ) {
    return 'update';
  } else if (lowerType.includes('register') || lowerType.includes('注册')) {
    return 'register';
  } else if (
    lowerType.includes('view') ||
    lowerType.includes('查看') ||
    lowerType.includes('get') ||
    lowerType.includes('获取')
  ) {
    return 'system';
  } else {
    return 'system';
  }
}
