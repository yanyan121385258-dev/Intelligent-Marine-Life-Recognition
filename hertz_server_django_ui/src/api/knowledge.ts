import { request } from '@/utils/hertz_request';

import type { ApiResponse } from '@/types/api_response';

// 分类类型
export interface KnowledgeCategory {
  id: number;
  name: string;
  description?: string;
  parent?: number | null;
  parent_name?: string | null;
  sort_order?: number;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  children_count?: number;
  articles_count?: number;
  full_path?: string;
  children?: KnowledgeCategory[];
}

export interface CategoryListData {
  list: KnowledgeCategory[];
  total: number;
  page: number;
  page_size: number;
}

export interface CategoryListParams {
  page?: number;
  page_size?: number;
  name?: string;
  parent_id?: number;
  is_active?: boolean;
}

// 文章类型
export interface KnowledgeArticleListItem {
  id: number;
  title: string;
  summary?: string | null;
  image?: string | null;
  category_name: string;
  author_name: string;
  status: 'draft' | 'published' | 'archived';
  status_display: string;
  view_count?: number;
  created_at: string;
  updated_at: string;
  published_at?: string | null;
  tags?: string;
  tags_list?: string[];
}

export interface KnowledgeArticleDetail extends KnowledgeArticleListItem {
  content: string;
  category: number;
  author: number;
  tags?: string;
  tags_list?: string[];
  sort_order?: number;
}

export interface ArticleListData {
  list: KnowledgeArticleListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface ArticleListParams {
  page?: number;
  page_size?: number;
  title?: string;
  category_id?: number;
  author_id?: number;
  status?: 'draft' | 'published' | 'archived';
  tags?: string;
}

export interface CreateArticlePayload {
  title: string;
  content: string;
  summary?: string;
  image?: string;
  category: number;
  status?: 'draft' | 'published';
  tags?: string;
  sort_order?: number;
}

export interface UpdateArticlePayload {
  title?: string;
  content?: string;
  summary?: string;
  image?: string;
  category?: number;
  status?: 'draft' | 'published' | 'archived';
  tags?: string;
  sort_order?: number;
}

// 知识库 API
export const knowledgeApi = {
  // 分类：列表
  getCategories: (params?: CategoryListParams): Promise<ApiResponse<CategoryListData>> => {
    return request.get('/api/wiki/categories/', { params });
  },

  // 分类：树形
  getCategoryTree: (): Promise<ApiResponse<KnowledgeCategory[]>> => {
    return request.get('/api/wiki/categories/tree/');
  },

  // 分类：详情
  getCategory: (id: number): Promise<ApiResponse<KnowledgeCategory>> => {
    return request.get(`/api/wiki/categories/${id}/`);
  },

  // 分类：创建
  createCategory: (data: Partial<KnowledgeCategory>): Promise<ApiResponse<KnowledgeCategory>> => {
    return request.post('/api/wiki/categories/create/', data);
  },

  // 分类：更新
  updateCategory: (
    id: number,
    data: Partial<KnowledgeCategory>
  ): Promise<ApiResponse<KnowledgeCategory>> => {
    return request.put(`/api/wiki/categories/${id}/update/`, data);
  },

  // 分类：删除
  deleteCategory: (id: number): Promise<ApiResponse<null>> => {
    return request.delete(`/api/wiki/categories/${id}/delete/`);
  },

  // 文章：列表
  getArticles: (params?: ArticleListParams): Promise<ApiResponse<ArticleListData>> => {
    return request.get('/api/wiki/articles/', { params });
  },

  // 文章：详情
  getArticle: (id: number): Promise<ApiResponse<KnowledgeArticleDetail>> => {
    return request.get(`/api/wiki/articles/${id}/`);
  },

  // 文章：创建
  createArticle: (data: CreateArticlePayload): Promise<ApiResponse<KnowledgeArticleDetail>> => {
    return request.post('/api/wiki/articles/create/', data);
  },

  // 文章：更新
  updateArticle: (
    id: number,
    data: UpdateArticlePayload
  ): Promise<ApiResponse<KnowledgeArticleDetail>> => {
    return request.put(`/api/wiki/articles/${id}/update/`, data);
  },

  // 文章：删除
  deleteArticle: (id: number): Promise<ApiResponse<null>> => {
    return request.delete(`/api/wiki/articles/${id}/delete/`);
  },

  // 文章：发布
  publishArticle: (id: number): Promise<ApiResponse<null>> => {
    return request.post(`/api/wiki/articles/${id}/publish/`);
  },

  // 文章：归档
  archiveArticle: (id: number): Promise<ApiResponse<null>> => {
    return request.post(`/api/wiki/articles/${id}/archive/`);
  },
};
