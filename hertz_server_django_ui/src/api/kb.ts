import { request } from '@/utils/hertz_request';

import type { ApiResponse } from '@/types/api_response';

// 知识库条目
export interface KbItem {
  id: number;
  title: string;
  modality: 'text' | 'code' | 'image' | 'audio' | 'video' | string;
  source_type: 'text' | 'file' | 'url' | string;
  chunk_count?: number;
  created_at?: string;
  updated_at?: string;
  created_chunk_count?: number;
  // 允许后端扩展字段
  [key: string]: any;
}

export interface KbItemListParams {
  query?: string;
  page?: number;
  page_size?: number;
}

export interface KbItemListData {
  total: number;
  page: number;
  page_size: number;
  list: KbItem[];
}

// 语义搜索
export interface KbSearchParams {
  q: string;
  k?: number;
}

// 问答（RAG）
export interface KbQaPayload {
  question: string;
  k?: number;
}

export interface KbQaData {
  answer: string;
  [key: string]: any;
}

// 图谱查询参数（实体 / 关系）
export interface KbGraphListParams {
  query?: string;
  page?: number;
  page_size?: number;
  // 关系检索可选参数
  source?: number;
  target?: number;
  relation_type?: string;
}

export const kbApi = {
  // 知识库条目：列表
  listItems(params?: KbItemListParams): Promise<ApiResponse<KbItemListData>> {
    return request.get('/api/kb/items/list/', { params });
  },

  // 语义搜索
  search(params: KbSearchParams): Promise<ApiResponse<any>> {
    return request.get('/api/kb/search/', { params });
  },

  // 问答（RAG）
  qa(payload: KbQaPayload): Promise<ApiResponse<KbQaData>> {
    return request.post('/api/kb/qa/', payload);
  },

  // 图谱：实体列表
  listEntities(params?: KbGraphListParams): Promise<ApiResponse<any>> {
    return request.get('/api/kb/graph/entities/', { params });
  },

  // 图谱：关系列表
  listRelations(params?: KbGraphListParams): Promise<ApiResponse<any>> {
    return request.get('/api/kb/graph/relations/', { params });
  },

  // 知识库条目：创建（JSON 文本）
  createItemJson(payload: {
    title: string;
    modality?: string;
    source_type?: string;
    content?: string;
    metadata?: any;
  }): Promise<ApiResponse<KbItem>> {
    return request.post('/api/kb/items/create/', payload);
  },

  // 知识库条目：创建（文件上传）
  createItemFile(formData: FormData): Promise<ApiResponse<KbItem>> {
    return request.post('/api/kb/items/create/', formData);
  },

  // 图谱：创建实体
  createEntity(payload: {
    name: string;
    type: string;
    properties?: any;
  }): Promise<ApiResponse<any>> {
    return request.post('/api/kb/graph/entities/', payload);
  },

  // 图谱：更新实体
  updateEntity(
    id: number,
    payload: { name?: string; type?: string; properties?: any }
  ): Promise<ApiResponse<any>> {
    return request.put(`/api/kb/graph/entities/${id}/`, payload);
  },

  // 图谱：删除实体
  deleteEntity(id: number): Promise<ApiResponse<null>> {
    return request.delete(`/api/kb/graph/entities/${id}/`);
  },

  // 图谱：创建关系
  createRelation(payload: {
    source: number;
    target: number;
    relation_type: string;
    properties?: any;
    source_chunk?: number;
  }): Promise<ApiResponse<any>> {
    return request.post('/api/kb/graph/relations/', payload);
  },

  // 图谱：删除关系
  deleteRelation(id: number): Promise<ApiResponse<null>> {
    return request.delete(`/api/kb/graph/relations/${id}/`);
  },

  // 图谱：自动抽取实体与关系
  extractGraph(payload: {
    text?: string;
    item_id?: number;
  }): Promise<ApiResponse<{ entities: number; relations: number }>> {
    return request.post('/api/kb/graph/extract/', payload);
  },
};
