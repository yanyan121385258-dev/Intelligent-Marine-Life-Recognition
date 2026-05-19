<template>
  <div class="login-container">
    <!-- 左侧区域 -->
    <div class="left-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎使用</h1>
        <h2 class="system-name ocean-gradient-text">智慧海洋生物识别系统</h2>
        <p class="welcome-description">智能海洋生物监测与识别平台</p>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="right-section">
      <div class="login-card">
        <div class="login-header">
          <h1 class="login-title">{{ $t('login.title') }}</h1>
          <p class="login-subtitle">请输入您的登录信息</p>
        </div>

        <a-form
          :model="form"
          :rules="rules"
          @finish="handleLogin"
          layout="vertical"
          class="login-form"
        >
          <a-form-item :label="$t('login.username')" name="username">
            <a-input v-model:value="form.username" :placeholder="$t('login.username')" size="large">
              <template #prefix>
                <UserOutlined />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item :label="$t('login.password')" name="password">
            <a-input-password
              v-model:value="form.password"
              :placeholder="$t('login.password')"
              size="large"
            >
              <template #prefix>
                <LockOutlined />
              </template>
            </a-input-password>
          </a-form-item>

          <a-form-item label="验证码" name="captcha">
            <a-row :gutter="8">
              <a-col :span="14">
                <a-input v-model:value="form.captcha" placeholder="请输入验证码" size="large">
                  <template #prefix>
                    <SafetyOutlined />
                  </template>
                </a-input>
              </a-col>
              <a-col :span="10">
                <div class="captcha-container">
                  <img
                    v-if="captchaData?.image_data"
                    :src="captchaData.image_data"
                    alt="验证码"
                    class="captcha-image"
                    @click="handleRefreshCaptcha"
                  />
                  <a-button
                    v-else
                    size="large"
                    :loading="captchaLoading"
                    @click="handleRefreshCaptcha"
                    block
                  >
                    获取验证码
                  </a-button>
                </div>
              </a-col>
            </a-row>
          </a-form-item>

          <a-form-item>
            <div class="login-options">
              <a-checkbox v-model:checked="form.remember">
                {{ $t('login.rememberMe') }}
              </a-checkbox>
              <a href="#" class="forgot-password">{{ $t('login.forgotPassword') }}</a>
            </div>
          </a-form-item>

          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              :loading="loading"
              block
              class="login-button"
            >
              {{ $t('login.login') }}
            </a-button>
          </a-form-item>

          <div class="register-link">
            还没有账户？
            <a @click="goToRegister">立即注册</a>
          </div>
        </a-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { message } from 'ant-design-vue';
import { useI18n } from 'vue-i18n';
import { UserOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons-vue';
import { useCaptcha } from '@/utils/captcha';
import { loginUser } from '@/api';
import { errorHandler, handleSuccess } from '@/utils/error_handler';

const router = useRouter();
const userStore = useUserStore();
const { t } = useI18n();

// 初始化错误处理器的i18n实例
errorHandler.setI18n({ t });

const loading = ref(false);

// 验证码相关
const { captchaData, captchaLoading, generateCaptcha, refreshCaptcha } = useCaptcha();

const form = reactive({
  username: '',
  password: '',
  captcha: '',
  remember: false,
});

const rules = {
  username: [{ required: true, message: t('error.usernameRequired'), trigger: 'blur' }],
  password: [{ required: true, message: t('error.passwordRequired'), trigger: 'blur' }],
  captcha: [{ required: true, message: t('error.captchaRequired'), trigger: 'blur' }],
};

const handleLogin = async () => {
  if (loading.value) return;

  // 验证表单
  if (!form.username || !form.password || !form.captcha) {
    message.error(t('error.requiredFieldMissing'));
    return;
  }

  // 检查验证码数据是否存在
  if (!captchaData.value?.captcha_id) {
    message.error(t('error.captchaExpired'));
    await handleRefreshCaptcha();
    return;
  }

  loading.value = true;

  try {
    // 构建登录数据 - 严格按照API接口定义
    const loginData = {
      username: form.username,
      password: form.password,
      captcha_code: form.captcha.trim(),
      captcha_key: captchaData.value.captcha_id,
    };

    const response = await loginUser(loginData);

    // 设置用户状态到store
    if (response.data) {
      // 设置token - 使用后端返回的access_token
      if (response.data.access_token) {
        userStore.token = response.data.access_token;
        localStorage.setItem('token', response.data.access_token);
      }

      // 设置用户信息
      if (response.data.user_info) {
        userStore.userInfo = response.data.user_info;
        userStore.isLoggedIn = true;
        localStorage.setItem('userInfo', JSON.stringify(response.data.user_info));
      }
    }

    handleSuccess('login');

    // 根据用户角色跳转到对应首页
    const userRole = response.data?.user_info?.roles?.[0]?.role_code;

    // 仅管理员角色进入管理端，其余（含未定义）进入用户端
    const adminRoles = ['admin', 'system_admin', 'super_admin'];
    const isAdmin = adminRoles.includes(userRole as any);
    if (isAdmin) {
      router.push('/admin');
    } else {
      router.push('/dashboard');
    }
  } catch (error: any) {
    console.error('登录失败:', error);

    // 清除敏感字段
    form.password = '';
    form.captcha = '';

    // 刷新验证码
    await handleRefreshCaptcha();
  } finally {
    loading.value = false;
  }
};

const handleRefreshCaptcha = async () => {
  try {
    await refreshCaptcha();
    // 清空验证码输入
    form.captcha = '';
  } catch (error) {
    message.error('刷新验证码失败');
  }
};

const goToRegister = () => {
  router.push('/register');
};

// 页面加载时生成验证码
onMounted(() => {
  generateCaptcha();
});
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(180deg, #000814 0%, #001d3d 30%, #003566 60%, #00509d 100%);
  overflow: hidden;
}

/* 左侧区域 */
.left-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: transparent;
}

.welcome-content {
  max-width: 500px;
  text-align: center;
}

.welcome-title {
  font-size: 24px;
  font-weight: 400;
  color: #caf0f8;
  margin-bottom: 16px;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.system-name {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 24px;
  line-height: 1.3;
}

.welcome-description {
  font-size: 18px;
  color: #90e0ef;
  line-height: 1.6;
  text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);
}

/* 右侧登录表单 */
.right-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background: transparent;
}

.login-card {
  position: relative;
  background: rgba(0, 29, 61, 0.9);
  padding: 48px;
  border-radius: 24px;
  width: 100%;
  max-width: 420px;
  border: 2px solid rgba(0, 212, 255, 0.4);
  box-shadow:
    0 0 60px rgba(0, 212, 255, 0.3),
    inset 0 0 50px rgba(0, 212, 255, 0.1);
  backdrop-filter: blur(25px);
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: conic-gradient(from 0deg, transparent, rgba(0, 212, 255, 0.4), transparent 30%);
  animation: rotate 8s linear infinite;
  z-index: -1;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #00d4ff;
  margin-bottom: 8px;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.login-subtitle {
  color: #90e0ef;
  font-size: 14px;
  margin: 0;
  text-shadow: 0 0 10px rgba(144, 224, 239, 0.5);
}

.login-form {
  width: 100%;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-password {
  color: #00d4ff;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.forgot-password:hover {
  color: #48cae4;
}

.register-link {
  text-align: center;
  margin-top: 24px;
  color: #90e0ef;
  font-size: 14px;
  text-shadow: 0 0 8px rgba(144, 224, 239, 0.5);
}

.register-link a {
  color: #00d4ff;
  text-decoration: none;
  margin-left: 4px;
  cursor: pointer;
  transition: color 0.2s;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.register-link a:hover {
  color: #48cae4;
}

:deep(.ant-form-item-label > label) {
  font-weight: 600;
  color: #caf0f8;
  font-size: 14px;
}

:deep(.ant-input-affix-wrapper) {
  border-radius: 16px;
  border: 2px solid rgba(0, 212, 255, 0.3);
  background: rgba(0, 29, 61, 0.8);
  transition: all 0.4s ease;
  box-shadow: inset 0 0 20px rgba(0, 212, 255, 0.05);
}

:deep(.ant-input-affix-wrapper:focus),
:deep(.ant-input-affix-wrapper-focused) {
  border-color: #00d4ff;
  box-shadow:
    0 0 30px rgba(0, 212, 255, 0.4),
    inset 0 0 25px rgba(0, 212, 255, 0.1);
}

:deep(.ant-input) {
  border: none;
  font-size: 14px;
  color: #caf0f8;
  background: transparent;
}

:deep(.ant-input::placeholder) {
  color: rgba(202, 240, 248, 0.5);
}

:deep(.ant-input-prefix) {
  color: #00d4ff;
  margin-right: 8px;
}

:deep(.ant-btn-primary) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(72, 202, 228, 0.2)) !important;
  border: 2px solid #00d4ff !important;
  border-radius: 16px;
  height: 54px;
  font-size: 16px;
  font-weight: 900;
  color: #00d4ff !important;
  transition: all 0.4s ease;
  letter-spacing: 4px;
  text-transform: uppercase;
  overflow: hidden;
}

:deep(.ant-btn-primary:hover) {
  background: linear-gradient(135deg, #00d4ff, #48cae4) !important;
  border-color: transparent !important;
  color: #001d3d !important;
  box-shadow:
    0 0 50px rgba(0, 212, 255, 0.7),
    0 0 100px rgba(72, 202, 228, 0.4);
  transform: translateY(-4px) scale(1.02);
}

:deep(.ant-checkbox-wrapper) {
  font-size: 14px;
  color: #90e0ef;
}

:deep(.ant-checkbox-inner) {
  background: rgba(0, 29, 61, 0.8);
  border: 2px solid rgba(0, 212, 255, 0.5);
}

:deep(.ant-checkbox-checked .ant-checkbox-inner) {
  background-color: #00d4ff;
  border-color: #00d4ff;
}

:deep(.ant-form-item) {
  margin-bottom: 20px;
}

.captcha-container {
  height: 40px;
  display: flex;
  align-items: center;
}

.captcha-image {
  width: 100%;
  height: 40px;
  border-radius: 16px;
  border: 2px solid rgba(0, 212, 255, 0.3);
  cursor: pointer;
  transition: border-color 0.2s;
  object-fit: cover;
}

.captcha-image:hover {
  border-color: #00d4ff;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.ocean-gradient-text {
  background: linear-gradient(90deg, #00d4ff, #48cae4, #90e0ef, #caf0f8, #00d4ff);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: oceanGradient 5s ease infinite;
}

@keyframes oceanGradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>
