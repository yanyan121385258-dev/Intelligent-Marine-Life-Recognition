import { request } from '@/utils/request';

import type { ApiResponse } from '@/types/api_response';

// 权限接口类型定义
export interface Permission {
  permission_id: number;
  permission_name: string;
  permission_code: string;
  permission_type: 'menu' | 'button' | 'api';
  parent_id?: number;
  path?: string;
  icon?: string;
  sort_order?: number;
  description?: string;
  status?: number;
  children?: Permission[];
}

// 角色接口类型定义
export interface Role {
  role_id: number;
  role_name: string;
  role_code: string;
  description?: string;
  status?: number;
  created_at?: string;
  updated_at?: string;
  permissions?: Permission[];
}

// 角色列表数据结构
export interface RoleListData {
  list: Role[];
  total: number;
  page: number;
  page_size: number;
}

// 角色列表响应类型
export type RoleListResponse = ApiResponse<RoleListData>;

// 角色列表查询参数
export interface RoleListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: number;
}

// 创建角色参数
export interface CreateRoleParams {
  role_name: string;
  role_code: string;
  description?: string;
  status?: number;
}

// 更新角色参数
export type UpdateRoleParams = Partial<CreateRoleParams>;

// 角色权限分配参数
export interface AssignRolePermissionsParams {
  role_id: number;
  menu_ids: number[];
  user_type?: number;
  department_id?: number;
}

// 权限列表响应类型
export type PermissionListResponse = ApiResponse<Permission[]>;

// 角色API
export const roleApi = {
  // 获取角色列表
  getRoleList: (params?: RoleListParams): Promise<RoleListResponse> => {
    return request.get('/api/roles/', { params });
  },

  // 获取单个角色
  getRole: (id: number): Promise<ApiResponse<Role>> => {
    return request.get(`/api/roles/${id}/`);
  },

  // 创建角色
  createRole: (data: CreateRoleParams): Promise<ApiResponse<Role>> => {
    return request.post('/api/roles/create/', data);
  },

  // 更新角色
  updateRole: (id: number, data: UpdateRoleParams): Promise<ApiResponse<Role>> => {
    return request.put(`/api/roles/${id}/update/`, data);
  },

  // 删除角色
  deleteRole: (id: number): Promise<ApiResponse<any>> => {
    return request.delete(`/api/roles/${id}/delete/`);
  },

  // 批量删除角色
  batchDeleteRoles: (ids: number[]): Promise<ApiResponse<any>> => {
    return request.post('/api/roles/batch-delete/', { role_ids: ids });
  },

  // 获取角色权限
  getRolePermissions: (id: number): Promise<ApiResponse<Permission[]>> => {
    return request.get(`/api/roles/${id}/menus/`);
  },

  // 分配角色权限
  assignRolePermissions: (data: AssignRolePermissionsParams): Promise<ApiResponse<any>> => {
    return request.post(`/api/roles/assign-menus/`, data);
  },

  // 获取所有权限列表
  getPermissionList: (): Promise<PermissionListResponse> => {
    return request.get('/api/menus/');
  },

  // 获取权限树
  getPermissionTree: (): Promise<PermissionListResponse> => {
    return request.get('/api/menus/tree/');
  },
};
