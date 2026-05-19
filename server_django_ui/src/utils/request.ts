import axios from 'axios';
import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';
import { handleError } from './error_handler';

// 请求配置接口
interface RequestConfig extends AxiosRequestConfig {
  showLoading?: boolean;
  showError?: boolean;
  metadata?: {
    requestId: string;
    timestamp: string;
  };
}

// 响应数据接口
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  success?: boolean;
}

// 请求拦截器配置
const requestInterceptor = {
  onFulfilled: (config: RequestConfig) => {
    const timestamp = new Date().toISOString();
    const requestId = Math.random().toString(36).substr(2, 9);

    // 简化日志，只在开发环境显示关键信息
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`);
    }

    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 如果是FormData，删除Content-Type让浏览器自动设置
    if (config.data instanceof FormData) {
      if (config.headers && 'Content-Type' in config.headers) {
        delete config.headers['Content-Type'];
      }
      console.log('📦 检测到FormData，移除Content-Type让浏览器自动设置');
    }

    // 显示loading
    if (config.showLoading !== false) {
      // 这里可以添加loading显示逻辑
    }

    // 将requestId添加到config中，用于响应时匹配
    config.metadata = { requestId, timestamp };
    return config as InternalAxiosRequestConfig;
  },
  onRejected: (error: any) => {
    console.error('❌ 请求错误:', error.message);
    return Promise.reject(error);
  },
};

// 响应拦截器配置
const responseInterceptor = {
  onFulfilled: (response: AxiosResponse) => {
    const requestTimestamp = (response.config as any).metadata?.timestamp;
    const duration = requestTimestamp ? Date.now() - new Date(requestTimestamp).getTime() : 0;

    // 简化日志，只在开发环境显示关键信息
    if (import.meta.env.DEV) {
      console.log(
        `✅ ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`
      );
    }

    // 统一处理响应数据
    if (response.data && typeof response.data === 'object') {
      // 如果后端返回的是标准格式 {code, message, data}
      if ('code' in response.data) {
        // 标准API响应格式处理
      }
    }

    return response;
  },
  onRejected: (error: any) => {
    const requestTimestamp = (error.config as any)?.metadata?.timestamp;
    const duration = requestTimestamp ? Date.now() - new Date(requestTimestamp).getTime() : 0;

    // 简化错误日志
    console.error(
      `❌ ${error.response?.status || 'Network'} ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`
    );
    console.error('错误信息:', error.response?.data?.message || error.message);

    // 使用统一错误处理器（支持按请求关闭全局错误提示）
    const showError = (error.config as any)?.showError;
    if (showError !== false) {
      handleError(error);
    }

    // 特殊处理401错误
    if (error.response?.status === 401) {
      console.warn('🔒 未授权，清除token');
      localStorage.removeItem('token');
      // 可以在这里跳转到登录页
    }

    return Promise.reject(error);
  },
};

class HertzRequest {
  private instance: AxiosInstance;

  constructor(config: AxiosRequestConfig) {
    // 在开发环境中使用空字符串以便Vite代理正常工作
    // 在生产环境中使用完整的API地址
    const isDev = import.meta.env.DEV;
    const baseURL = isDev ? '' : import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    console.log('🔧 创建axios实例 - isDev:', isDev);
    console.log('🔧 创建axios实例 - baseURL:', baseURL);
    console.log('🔧 环境变量 VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);

    this.instance = axios.create({
      baseURL,
      timeout: 60000, // 60 秒超时，适应 AI 模型响应时间
      // 不设置默认 Content-Type，让每个请求根据数据类型自动设置
      ...config,
    });

    // 添加请求拦截器
    this.instance.interceptors.request.use(
      requestInterceptor.onFulfilled,
      requestInterceptor.onRejected
    );

    // 添加响应拦截器
    this.instance.interceptors.response.use(
      responseInterceptor.onFulfilled,
      responseInterceptor.onRejected
    );
  }

  // GET请求
  get<T = any>(url: string, config?: RequestConfig): Promise<T> {
    return this.instance.get(url, config).then((res) => res.data);
  }

  // POST请求
  post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    // 如果不是FormData，设置Content-Type为application/json
    const finalConfig = { ...config };
    if (!(data instanceof FormData)) {
      finalConfig.headers = {
        'Content-Type': 'application/json',
        ...finalConfig.headers,
      };
    }
    return this.instance.post(url, data, finalConfig).then((res) => res.data);
  }

  // PUT请求
  put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    // 如果不是FormData，设置Content-Type为application/json
    const finalConfig = { ...config };
    if (!(data instanceof FormData)) {
      finalConfig.headers = {
        'Content-Type': 'application/json',
        ...finalConfig.headers,
      };
    }
    return this.instance.put(url, data, finalConfig).then((res) => res.data);
  }

  // DELETE请求
  delete<T = any>(url: string, config?: RequestConfig): Promise<T> {
    return this.instance.delete(url, config).then((res) => res.data);
  }

  // PATCH请求
  patch<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.instance.patch(url, data, config).then((res) => res.data);
  }

  // 上传文件
  upload<T = any>(url: string, formData: FormData, config?: RequestConfig): Promise<T> {
    // 不要手动设置Content-Type，让浏览器自动设置，这样会包含正确的boundary
    return this.instance
      .post(url, formData, {
        ...config,
        headers: {
          // 不设置Content-Type，让浏览器自动设置multipart/form-data的header
          ...config?.headers,
        },
      })
      .then((res) => res.data);
  }
}

// 创建默认实例
export const request = new HertzRequest({});

// 导出类和配置接口
export { HertzRequest };
export type { RequestConfig, ApiResponse };
