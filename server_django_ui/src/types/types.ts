// 通用响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  success?: boolean;
  timestamp?: string;
}

// 分页请求参数
export interface PageParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// 分页响应
export interface PageResponse<T> {
  list: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// 用户相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  role: string;
  permissions: string[];
  status: 'active' | 'inactive' | 'banned';
  createTime: string;
  updateTime: string;
}

export interface LoginParams {
  username: string;
  password: string;
  remember?: boolean;
}

export interface LoginResponse {
  token: string;
  user: User;
  expiresIn: number;
}

// 菜单相关类型
export interface MenuItem {
  id: number;
  name: string;
  path: string;
  icon?: string;
  children?: MenuItem[];
  permission?: string;
  hidden?: boolean;
  meta?: {
    title: string;
    requiresAuth?: boolean;
  };
}

// 表格相关类型
export interface TableColumn<T = any> {
  key: string;
  title: string;
  width?: number;
  fixed?: 'left' | 'right';
  sortable?: boolean;
  render?: (record: T, index: number) => any;
}

export interface TableProps<T = any> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    showSizeChanger?: boolean;
    showQuickJumper?: boolean;
  };
  rowSelection?: {
    selectedRowKeys: (string | number)[];
    onChange: (selectedRowKeys: (string | number)[], selectedRows: T[]) => void;
  };
}

// 表单相关类型
export interface FormField {
  name: string;
  label: string;
  type: 'input' | 'select' | 'textarea' | 'date' | 'switch' | 'radio' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: any }[];
  rules?: any[];
}

export interface FormProps {
  fields: FormField[];
  initialValues?: Record<string, any>;
  onSubmit: (values: Record<string, any>) => Promise<void>;
  loading?: boolean;
}

// 弹窗相关类型
export interface ModalProps {
  title: string;
  visible: boolean;
  onCancel: () => void;
  onOk?: () => void;
  width?: number;
  children: any;
}

// 消息相关类型
export type MessageType = 'success' | 'error' | 'warning' | 'info';

export interface MessageConfig {
  type: MessageType;
  content: string;
  duration?: number;
}

// 主题相关类型
export type Theme = 'light' | 'dark' | 'auto';

// 语言相关类型
export type Language = 'zh-CN' | 'en-US';

// 路由相关类型
export interface RouteMeta {
  title?: string;
  requiresAuth?: boolean;
  permission?: string;
  hidden?: boolean;
  icon?: string;
}

// 组件属性类型
export interface ComponentProps {
  className?: string;
  style?: Record<string, any>;
  children?: any;
}

// 工具函数类型
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// API 相关类型
export interface RequestConfig {
  showLoading?: boolean;
  showError?: boolean;
  timeout?: number;
}

// 文件相关类型
export interface FileInfo {
  name: string;
  size: number;
  type: string;
  url?: string;
  lastModified: number;
}

export interface UploadProps {
  accept?: string;
  multiple?: boolean;
  maxSize?: number;
  onUpload: (files: File[]) => Promise<void>;
  onRemove?: (file: FileInfo) => void;
}
