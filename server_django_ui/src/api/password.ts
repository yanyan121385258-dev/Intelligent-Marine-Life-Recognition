import { request } from '@/utils/request';

// 修改密码接口参数
export interface ChangePasswordParams {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

// 重置密码接口参数
export interface ResetPasswordParams {
  email: string;
  email_code: string;
  new_password: string;
  confirm_password: string;
}

// 修改密码
export const changePassword = (params: ChangePasswordParams) => {
  return request.post('/api/auth/password/change/', params);
};

// 重置密码
export const resetPassword = (params: ResetPasswordParams) => {
  return request.post('/api/auth/password/reset/', params);
};

// 发送重置密码邮箱验证码
export const sendResetPasswordCode = (email: string) => {
  return request.post('/api/auth/password/reset/code/', { email });
};
