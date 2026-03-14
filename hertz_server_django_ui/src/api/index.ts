// API 统一出口文件
export * from './captcha';
export * from './auth';
// 单独导出user模块，避免与role模块的Role命名冲突
export { userApi } from './user';
export type {
  User,
  UserListData,
  UserListResponse,
  UserListParams,
  AssignRolesParams,
} from './user';
export * from './department';
export * from './menu';
export * from './role';
export * from './password';
export * from './system_monitor';
export * from './dashboard';

export * from './ai';
// 这里可以继续添加其它 API 模块的导出，例如：
// export * from './admin'
export * from './log';
export * from './knowledge';
export * from './kb';
