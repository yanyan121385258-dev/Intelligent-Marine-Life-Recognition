import { request } from '@/utils/request';

import type { ApiResponse } from '@/types/api_response';

// 用户端通知模块 API 类型定义
export interface UserNoticeListItem {
  notice: number;
  title: string;
  notice_type_display: string;
  priority_display: string;
  is_top: boolean;
  publish_time: string;
  is_read: boolean;
  read_time: string | null;
  is_starred: boolean;
  starred_time: string | null;
  is_expired: boolean;
  created_at: string;
}

export interface UserNoticeListData {
  notices: UserNoticeListItem[];
  pagination: {
    current_page: number;
    page_size: number;
    total_pages: number;
    total_count: number;
    has_next: boolean;
    has_previous: boolean;
  };
  statistics: {
    total_count: number;
    unread_count: number;
    starred_count: number;
  };
}

export interface UserNoticeDetailData {
  notice: number;
  title: string;
  content: string;
  notice_type_display: string;
  priority_display: string;
  attachment_url: string | null;
  publish_time: string;
  expire_time: string;
  is_top: boolean;
  is_expired: boolean;
  publisher_name: string | null;
  is_read: boolean;
  read_time: string;
  is_starred: boolean;
  starred_time: string | null;
  created_at: string;
  updated_at: string;
}

export const noticeUserApi = {
  // 查看通知列表
  list: (params?: {
    page?: number;
    page_size?: number;
  }): Promise<ApiResponse<UserNoticeListData>> => request.get('/api/notice/user/list/', { params }),

  // 查看通知详情
  detail: (notice_id: number | string): Promise<ApiResponse<UserNoticeDetailData>> =>
    request.get(`/api/notice/user/detail/${notice_id}/`),

  // 标记通知已读
  markRead: (notice_id: number | string): Promise<ApiResponse<null>> =>
    request.post('/api/notice/user/mark-read/', { notice_id }),

  // 批量标记通知已读
  batchMarkRead: (
    notice_ids: Array<number | string>
  ): Promise<ApiResponse<{ updated_count: number }>> =>
    request.post('/api/notice/user/batch-mark-read/', { notice_ids }),

  // 用户获取通知统计
  statistics: (): Promise<
    ApiResponse<{
      total_count: number;
      unread_count: number;
      read_count: number;
      starred_count: number;
      type_statistics?: Record<string, number>;
      priority_statistics?: Record<string, number>;
    }>
  > => request.get('/api/notice/user/statistics/'),

  // 收藏/取消收藏通知
  toggleStar: (notice_id: number | string, is_starred: boolean): Promise<ApiResponse<null>> =>
    request.post('/api/notice/user/toggle-star/', { notice_id, is_starred }),
};
