import {
  generateCaptcha,
  refreshCaptcha,
  type CaptchaResponse,
  type CaptchaRefreshResponse,
} from '@/api/captcha';
import { ref, type Ref } from 'vue';

/**
 * 验证码组合式函数
 */
export function useCaptcha() {
  // 验证码数据
  const captchaData: Ref<CaptchaResponse | null> = ref(null);

  // 加载状态
  const captchaLoading: Ref<boolean> = ref(false);

  // 错误信息
  const captchaError: Ref<string | null> = ref(null);

  /**
   * 生成验证码
   */
  const handleGenerateCaptcha = async (): Promise<void> => {
    try {
      captchaLoading.value = true;
      captchaError.value = null;

      const response = await generateCaptcha();
      captchaData.value = response;
    } catch (error) {
      console.error('生成验证码失败:', error);
      captchaError.value = error instanceof Error ? error.message : '生成验证码失败';
    } finally {
      captchaLoading.value = false;
    }
  };

  /**
   * 刷新验证码
   */
  const handleRefreshCaptcha = async (): Promise<void> => {
    try {
      captchaLoading.value = true;
      captchaError.value = null;

      // 检查是否有当前验证码ID
      if (!captchaData.value?.captcha_id) {
        console.warn('没有当前验证码ID，将生成新的验证码');
        await handleGenerateCaptcha();
        return;
      }

      const response = await refreshCaptcha(captchaData.value.captcha_id);
      captchaData.value = response;
    } catch (error) {
      console.error('刷新验证码失败:', error);
      captchaError.value = error instanceof Error ? error.message : '刷新验证码失败';
    } finally {
      captchaLoading.value = false;
    }
  };

  return {
    captchaData,
    captchaLoading,
    captchaError,
    generateCaptcha: handleGenerateCaptcha,
    refreshCaptcha: handleRefreshCaptcha,
  };
}

// 导出类型
export type { CaptchaResponse, CaptchaRefreshResponse };
