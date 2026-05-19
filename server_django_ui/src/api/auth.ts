import { request } from '@/utils/request';

// 注册接口数据类型
export interface RegisterData {
  username: string;
  password: string;
  confirm_password: string;
  email: string;
  phone: string;
  real_name: string;
  captcha: string;
  captcha_id: string;
}

// 发送邮箱验证码数据类型
export interface SendEmailCodeData {
  email: string;
  code_type: string;
}

// 登录接口数据类型
export interface LoginData {
  username: string;
  password: string;
  captcha_code: string;
  captcha_key: string;
}

// 注册API
export const registerUser = (data: RegisterData) => {
  return request.post('/api/auth/register/', data);
};

// 登录API
export const loginUser = (data: LoginData) => {
  return request.post('/api/auth/login/', data);
};

// 发送邮箱验证码API
export const sendEmailCode = (data: SendEmailCodeData) => {
  return request.post('/api/auth/email/code/', data);
};

// 登出API
export const logoutUser = () => {
  return request.post('/api/auth/logout/');
};
