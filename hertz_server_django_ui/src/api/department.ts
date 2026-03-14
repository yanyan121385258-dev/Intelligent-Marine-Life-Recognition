import { request } from '@/utils/hertz_request';

import type { ApiResponse } from '@/types/api_response';

// 部门数据类型定义
export interface Department {
  dept_id: number;
  parent_id: number | null;
  dept_name: string;
  dept_code: string;
  leader: string;
  phone: string | null;
  email: string | null;
  status: number;
  sort_order: number;
  created_at: string;
  updated_at: string;
  children?: Department[];
  user_count?: number;
}

// 部门列表数据类型
export interface DepartmentListData {
  list: Department[];
  total: number;
  page: number;
  page_size: number;
}

export type DepartmentListResponse = ApiResponse<DepartmentListData>;

// 部门列表查询参数
export interface DepartmentListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: number;
  parent_id?: number;
}

// 创建部门参数
export interface CreateDepartmentParams {
  parent_id: number | null;
  dept_name: string;
  dept_code: string;
  leader: string;
  phone: string;
  email: string;
  status: number;
  sort_order: number;
}

// 更新部门参数
export type UpdateDepartmentParams = Partial<CreateDepartmentParams>;

// 部门API接口
export const departmentApi = {
  // 获取部门列表
  getDepartmentList: (params?: DepartmentListParams): Promise<ApiResponse<Department[]>> => {
    return request.get('/api/departments/', { params });
  },

  // 获取部门详情
  getDepartment: (id: number): Promise<ApiResponse<Department>> => {
    return request.get(`/api/departments/${id}/`);
  },

  // 创建部门
  createDepartment: (data: CreateDepartmentParams): Promise<ApiResponse<Department>> => {
    return request.post('/api/departments/create/', data);
  },

  // 更新部门
  updateDepartment: (
    id: number,
    data: UpdateDepartmentParams
  ): Promise<ApiResponse<Department>> => {
    return request.put(`/api/departments/${id}/update/`, data);
  },

  // 删除部门
  deleteDepartment: (id: number): Promise<ApiResponse<any>> => {
    return request.delete(`/api/departments/${id}/delete/`);
  },

  // 获取部门树
  getDepartmentTree: (): Promise<ApiResponse<Department[]>> => {
    return request.get('/api/departments/tree/');
  },
};
