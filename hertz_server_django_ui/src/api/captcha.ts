import { request } from '@/utils/hertz_request';

// 验证码相关接口类型定义
export interface CaptchaResponse {
  captcha_id: string;
  image_data: string; // base64编码的图片
  expires_in: number; // 过期时间（秒）
}

export interface CaptchaRefreshResponse {
  captcha_id: string;
  image_data: string; // base64编码的图片
  expires_in: number; // 过期时间（秒）
}

/**
 * 生成验证码
 */
export const generateCaptcha = async (): Promise<CaptchaResponse> => {
  console.log('🚀 开始发送验证码生成请求...');
  console.log('📍 请求URL:', `${import.meta.env.VITE_API_BASE_URL}/api/captcha/generate/`);
  console.log('🌐 环境变量 VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);

  try {
    const response = await request.post<{
      code: number;
      message: string;
      data: CaptchaResponse;
    }>('/api/captcha/generate/');

    console.log('✅ 验证码生成请求成功:', response);
    return response.data;
  } catch (error: any) {
    console.error('❌ 验证码生成请求失败 - 完整错误信息:');
    console.error('错误对象:', error);
    console.error('错误类型:', typeof error);
    console.error('错误消息:', error?.message);
    console.error('错误代码:', error?.code);
    console.error('错误状态:', error?.status);
    console.error('错误响应:', error?.response);
    console.error('错误请求:', error?.request);
    console.error('错误配置:', error?.config);

    // 检查是否是网络错误
    if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error')) {
      console.error('🌐 网络连接错误 - 可能的原因:');
      console.error('1. 后端服务器未启动');
      console.error('2. API地址不正确');
      console.error('3. CORS配置问题');
      console.error('4. 防火墙阻止连接');
    }

    throw error;
  }
};

/**
 * 刷新验证码
 */
export const refreshCaptcha = async (captcha_id: string): Promise<CaptchaRefreshResponse> => {
  console.log('🔄 开始发送验证码刷新请求...');
  console.log('📍 请求URL:', `${import.meta.env.VITE_API_BASE_URL}/api/captcha/refresh/`);
  console.log('📦 请求数据:', { captcha_id });

  try {
    const response = await request.post<{
      code: number;
      message: string;
      data: CaptchaRefreshResponse;
    }>('/api/captcha/refresh/', {
      captcha_id,
    });

    console.log('✅ 验证码刷新请求成功:', response);
    return response.data;
  } catch (error: any) {
    console.error('❌ 验证码刷新请求失败 - 完整错误信息:');
    console.error('错误对象:', error);
    console.error('错误类型:', typeof error);
    console.error('错误消息:', error?.message);
    console.error('错误代码:', error?.code);
    console.error('错误状态:', error?.status);
    console.error('错误响应:', error?.response);
    console.error('错误请求:', error?.request);
    console.error('错误配置:', error?.config);

    throw error;
  }
};
