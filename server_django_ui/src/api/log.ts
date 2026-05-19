import { request } from '@/utils/request';

import type { ApiResponse } from '@/types/api_response';

// 列表查询参数
export interface LogListParams {
  page?: number;
  page_size?: number;
  user_id?: number;
  operation_type?: string;
  operation_module?: string;
  start_date?: string; // YYYY-MM-DD
  end_date?: string; // YYYY-MM-DD
  ip_address?: string;
  status?: number;
  // 新增：按请求方法与路径、关键字筛选（与后端保持可选兼容）
  request_method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | string;
  request_path?: string;
  keyword?: string;
}

// 列表项（精简字段）
export interface OperationLogItem {
  id: number;
  user?: {
    id: number;
    username: string;
    email?: string;
  } | null;
  operation_type: string;
  // 展示字段
  action_type_display?: string;
  operation_module: string;
  operation_description?: string;
  target_model?: string;
  target_object_id?: string;
  ip_address?: string;
  request_method: string;
  request_path: string;
  response_status: number;
  // 结果与状态展示
  status_display?: string;
  is_success?: boolean;
  execution_time?: number;
  created_at: string;
}

// 列表响应 data 结构
export interface LogListData {
  count: number;
  next: string | null;
  previous: string | null;
  results: OperationLogItem[];
}

export type LogListResponse = ApiResponse<LogListData>;

// 详情数据（完整字段）
export interface OperationLogDetail {
  id: number;
  user?: {
    id: number;
    username: string;
    email?: string;
  } | null;
  operation_type: string;
  action_type_display?: string;
  operation_module: string;
  operation_description: string;
  target_model?: string;
  target_object_id?: string;
  ip_address?: string;
  user_agent?: string;
  request_method: string;
  request_path: string;
  request_data?: Record<string, any>;
  response_status: number;
  status_display?: string;
  is_success?: boolean;
  response_data?: Record<string, any>;
  execution_time?: number;
  created_at: string;
  updated_at?: string;
}

export type LogDetailResponse = ApiResponse<OperationLogDetail>;

export const logApi = {
  // 获取操作日志列表
  getList: (
    params: LogListParams,
    options?: { signal?: AbortSignal }
  ): Promise<LogListResponse> => {
    // 关闭统一错误弹窗，由页面自行处理
    return request.get('/api/log/list/', { params, showError: false, signal: options?.signal });
  },

  // 获取操作日志详情
  getDetail: (logId: number): Promise<LogDetailResponse> => {
    return request.get(`/api/log/detail/${logId}/`);
  },

  // 兼容查询参数方式的详情（部分后端实现为 /api/log/detail/?id=xx 或 ?log_id=xx）
  getDetailByQuery: (logId: number): Promise<LogDetailResponse> => {
    return request.get('/api/log/detail/', { params: { id: logId, log_id: logId } });
  },
};
