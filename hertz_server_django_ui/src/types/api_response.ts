// 统一API响应类型定义
// 与后端 HertzResponse 对齐
export interface ApiResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T;
}
