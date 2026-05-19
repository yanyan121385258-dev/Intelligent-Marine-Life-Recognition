import { message } from 'ant-design-vue';
import { useI18n } from 'vue-i18n';

// 错误类型枚举
export enum ErrorType {
  // 网络错误
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',

  // 认证错误
  UNAUTHORIZED = 'UNAUTHORIZED',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  TOKEN_INVALID = 'TOKEN_INVALID',

  // 权限错误
  FORBIDDEN = 'FORBIDDEN',
  ACCESS_DENIED = 'ACCESS_DENIED',

  // 业务错误
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  BUSINESS_ERROR = 'BUSINESS_ERROR',

  // 系统错误
  SERVER_ERROR = 'SERVER_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
}

// 错误信息接口
export interface ErrorInfo {
  code: number;
  message: string;
  type: ErrorType;
  details?: any;
  field?: string;
}

// 错误处理器类
export class HertzErrorHandler {
  private static instance: HertzErrorHandler;
  private i18n: any;

  constructor() {
    // 在组件中使用时需要传入i18n实例
  }

  static getInstance(): HertzErrorHandler {
    if (!HertzErrorHandler.instance) {
      HertzErrorHandler.instance = new HertzErrorHandler();
    }
    return HertzErrorHandler.instance;
  }

  // 设置i18n实例
  setI18n(i18n: any) {
    this.i18n = i18n;
  }

  // 获取翻译文本
  private t(key: string, fallback?: string): string {
    if (this.i18n && this.i18n.t) {
      return this.i18n.t(key);
    }
    return fallback || key;
  }

  // 处理HTTP错误
  handleHttpError(error: any): void {
    const status = error?.response?.status;
    const data = error?.response?.data;

    console.error('🚨 HTTP错误详情:', {
      status,
      data,
      url: error?.config?.url,
      method: error?.config?.method,
      requestData: error?.config?.data,
    });

    switch (status) {
      case 400:
        this.handleBadRequestError(data);
        break;
      case 401:
        this.handleUnauthorizedError(data);
        break;
      case 403:
        this.handleForbiddenError(data);
        break;
      case 404:
        this.handleNotFoundError(data);
        break;
      case 422:
        this.handleValidationError(data);
        break;
      case 429:
        this.handleTooManyRequestsError(data);
        break;
      case 500:
        this.handleServerError(data);
        break;
      case 502:
      case 503:
      case 504:
        this.handleServiceUnavailableError(data);
        break;
      default:
        this.handleUnknownError(error);
    }
  }

  // 处理400错误
  private handleBadRequestError(data: any): void {
    const message = data?.message || data?.detail || '';

    // 检查是否是验证码相关错误
    if (this.isMessageContains(message, ['验证码', 'captcha', 'Captcha'])) {
      if (this.isMessageContains(message, ['过期', 'expired', 'expire'])) {
        this.showError(this.t('error.captchaExpired', '验证码已过期，请刷新后重新输入'));
      } else {
        this.showError(this.t('error.captchaError', '验证码错误，请重新输入（区分大小写）'));
      }
      return;
    }

    // 检查是否是用户名或密码错误
    if (
      this.isMessageContains(message, ['用户名', 'username', '密码', 'password', '登录', 'login'])
    ) {
      this.showError(this.t('error.loginFailed', '登录失败，请检查用户名和密码'));
      return;
    }

    // 检查是否是注册相关错误
    if (this.isMessageContains(message, ['用户名已存在', 'username exists', 'username already'])) {
      this.showError(this.t('error.usernameExists', '用户名已存在，请选择其他用户名'));
      return;
    }

    if (this.isMessageContains(message, ['邮箱已注册', 'email exists', 'email already'])) {
      this.showError(this.t('error.emailExists', '邮箱已被注册，请使用其他邮箱'));
      return;
    }

    if (this.isMessageContains(message, ['手机号已注册', 'phone exists', 'phone already'])) {
      this.showError(this.t('error.phoneExists', '手机号已被注册，请使用其他手机号'));
      return;
    }

    // 默认400错误处理
    this.showError(data?.message || this.t('error.invalidInput', '输入数据格式不正确'));
  }

  // 处理401错误
  private handleUnauthorizedError(data: any): void {
    const message = data?.message || data?.detail || '';

    if (this.isMessageContains(message, ['token', 'Token', '令牌', '过期', 'expired'])) {
      this.showError(this.t('error.tokenExpired', '登录已过期，请重新登录'));
      // 可以在这里添加自动跳转到登录页的逻辑
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } else if (this.isMessageContains(message, ['账户锁定', 'account locked', 'locked'])) {
      this.showError(this.t('error.accountLocked', '账户已被锁定，请联系管理员'));
    } else if (this.isMessageContains(message, ['账户禁用', 'account disabled', 'disabled'])) {
      this.showError(this.t('error.accountDisabled', '账户已被禁用，请联系管理员'));
    } else {
      this.showError(this.t('error.loginFailed', '登录失败，请检查用户名和密码'));
    }
  }

  // 处理403错误
  private handleForbiddenError(data: any): void {
    const message = data?.message || data?.detail || '';

    if (this.isMessageContains(message, ['权限不足', 'permission denied', 'access denied'])) {
      this.showError(this.t('error.permissionDenied', '权限不足，无法执行此操作'));
    } else {
      this.showError(this.t('error.accessDenied', '访问被拒绝，您没有执行此操作的权限'));
    }
  }

  // 处理404错误
  private handleNotFoundError(data: any): void {
    const message = data?.message || data?.detail || '';

    if (this.isMessageContains(message, ['用户', 'user'])) {
      this.showError(this.t('error.userNotFound', '用户不存在或已被删除'));
    } else if (this.isMessageContains(message, ['部门', 'department'])) {
      this.showError(this.t('error.departmentNotFound', '部门不存在或已被删除'));
    } else if (this.isMessageContains(message, ['角色', 'role'])) {
      this.showError(this.t('error.roleNotFound', '角色不存在或已被删除'));
    } else {
      this.showError(this.t('error.404', '页面未找到'));
    }
  }

  // 处理422验证错误
  private handleValidationError(data: any): void {
    console.log('🔍 422验证错误详情:', data);

    // 处理FastAPI风格的验证错误
    if (data?.detail && Array.isArray(data.detail)) {
      const errors = data.detail;
      const errorMessages: string[] = [];

      errors.forEach((error: any) => {
        const field = error.loc?.[error.loc.length - 1] || 'unknown';
        const msg = error.msg || error.message || '验证失败';

        // 根据字段和错误类型提供更具体的提示
        if (field === 'username') {
          if (msg.includes('required') || msg.includes('必填')) {
            errorMessages.push(this.t('error.usernameRequired', '请输入用户名'));
          } else if (msg.includes('length') || msg.includes('长度')) {
            errorMessages.push('用户名长度不符合要求');
          } else {
            errorMessages.push(`用户名: ${msg}`);
          }
        } else if (field === 'password') {
          if (msg.includes('required') || msg.includes('必填')) {
            errorMessages.push(this.t('error.passwordRequired', '请输入密码'));
          } else if (msg.includes('weak') || msg.includes('强度')) {
            errorMessages.push(
              this.t('error.passwordTooWeak', '密码强度不足，请包含大小写字母、数字和特殊字符')
            );
          } else {
            errorMessages.push(`密码: ${msg}`);
          }
        } else if (field === 'email') {
          if (msg.includes('format') || msg.includes('格式')) {
            errorMessages.push(
              this.t('error.emailFormatError', '邮箱格式不正确，请输入有效的邮箱地址')
            );
          } else {
            errorMessages.push(`邮箱: ${msg}`);
          }
        } else if (field === 'phone') {
          if (msg.includes('format') || msg.includes('格式')) {
            errorMessages.push(
              this.t('error.phoneFormatError', '手机号格式不正确，请输入11位手机号')
            );
          } else {
            errorMessages.push(`手机号: ${msg}`);
          }
        } else if (field === 'captcha' || field === 'captcha_code') {
          errorMessages.push(this.t('error.captchaError', '验证码错误，请重新输入（区分大小写）'));
        } else {
          errorMessages.push(`${field}: ${msg}`);
        }
      });

      if (errorMessages.length > 0) {
        this.showError(errorMessages.join('；'));
        return;
      }
    }

    // 处理其他格式的验证错误
    if (data?.errors) {
      const errors = data.errors;
      const errorMessages = [];
      for (const field in errors) {
        if (errors[field] && Array.isArray(errors[field])) {
          errorMessages.push(`${field}: ${errors[field].join(', ')}`);
        } else if (errors[field]) {
          errorMessages.push(`${field}: ${errors[field]}`);
        }
      }
      if (errorMessages.length > 0) {
        this.showError(`验证失败: ${errorMessages.join('; ')}`);
        return;
      }
    }

    // 默认验证错误处理
    this.showError(data?.message || this.t('error.invalidInput', '输入数据格式不正确'));
  }

  // 处理429错误（请求过多）
  private handleTooManyRequestsError(data: any): void {
    this.showError(this.t('error.loginAttemptsExceeded', '登录尝试次数过多，账户已被临时锁定'));
  }

  // 处理500错误
  private handleServerError(data: any): void {
    this.showError(this.t('error.500', '服务器内部错误，请稍后重试'));
  }

  // 处理服务不可用错误
  private handleServiceUnavailableError(data: any): void {
    this.showError(this.t('error.serviceUnavailable', '服务暂时不可用，请稍后重试'));
  }

  // 处理网络错误
  handleNetworkError(error: any): void {
    if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error')) {
      this.showError(this.t('error.networkError', '网络连接失败，请检查网络设置'));
    } else if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
      this.showError(this.t('error.timeout', '请求超时，请稍后重试'));
    } else {
      this.showError(this.t('error.networkError', '网络连接失败，请检查网络设置'));
    }
  }

  // 处理未知错误
  private handleUnknownError(error: any): void {
    console.error('🚨 未知错误:', error);
    this.showError(this.t('error.operationFailed', '操作失败，请稍后重试'));
  }

  // 显示错误消息
  showError(msg: string): void {
    message.error(msg);
  }

  // 显示成功消息
  showSuccess(msg: string): void {
    message.success(msg);
  }

  // 显示警告消息
  showWarning(msg: string): void {
    message.warning(msg);
  }

  // 检查消息是否包含指定关键词
  private isMessageContains(message: string, keywords: string[]): boolean {
    if (!message) return false;
    const lowerMessage = message.toLowerCase();
    return keywords.some((keyword) => lowerMessage.includes(keyword.toLowerCase()));
  }

  // 处理业务操作成功
  handleSuccess(operation: string, customMessage?: string): void {
    if (customMessage) {
      this.showSuccess(customMessage);
      return;
    }

    switch (operation) {
      case 'save':
        this.showSuccess(this.t('error.saveSuccess', '保存成功'));
        break;
      case 'delete':
        this.showSuccess(this.t('error.deleteSuccess', '删除成功'));
        break;
      case 'update':
        this.showSuccess(this.t('error.updateSuccess', '更新成功'));
        break;
      case 'create':
        this.showSuccess('创建成功');
        break;
      case 'login':
        this.showSuccess('登录成功');
        break;
      case 'register':
        this.showSuccess('注册成功');
        break;
      default:
        this.showSuccess('操作成功');
    }
  }
}

// 导出单例实例
export const errorHandler = HertzErrorHandler.getInstance();

// 导出便捷方法
export const handleError = (error: any) => {
  if (error?.response) {
    errorHandler.handleHttpError(error);
  } else if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error')) {
    errorHandler.handleNetworkError(error);
  } else {
    console.error('🚨 处理错误:', error);
    errorHandler.showError('操作失败，请稍后重试');
  }
};

export const handleSuccess = (operation: string, customMessage?: string) => {
  errorHandler.handleSuccess(operation, customMessage);
};
