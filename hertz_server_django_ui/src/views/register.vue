<template>
  <div class="register-container">
    <!-- 左侧区域 -->
    <div class="left-section">
      <div class="welcome-content">
        <h1 class="welcome-title">创建账户</h1>
        <h2 class="system-name">管理系统模板</h2>
        <p class="welcome-description">填写注册信息，开始使用系统</p>
      </div>
    </div>

    <!-- 右侧注册表单 -->
    <div class="right-section">
      <div class="register-card">
        <div class="register-header">
          <h1 class="register-title">{{ $t('register.title') }}</h1>
          <p class="register-subtitle">请填写注册信息</p>
        </div>

        <a-form
          :model="form"
          :rules="rules"
          @finish="handleRegister"
          layout="vertical"
          class="register-form"
        >
          <a-form-item label="用户名" name="username">
            <a-input v-model:value="form.username" placeholder="请输入用户名" size="large">
              <template #prefix>
                <UserOutlined />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item label="邮箱" name="email">
            <a-input v-model:value="form.email" placeholder="请输入邮箱" size="large">
              <template #prefix>
                <MailOutlined />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item label="真实姓名" name="real_name">
            <a-input v-model:value="form.real_name" placeholder="请输入真实姓名" size="large">
              <template #prefix>
                <IdcardOutlined />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item label="手机号" name="phone">
            <a-input v-model:value="form.phone" placeholder="请输入手机号" size="large">
              <template #prefix>
                <PhoneOutlined />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item label="密码" name="password">
            <a-input-password v-model:value="form.password" placeholder="请输入密码" size="large">
              <template #prefix>
                <LockOutlined />
              </template>
            </a-input-password>
          </a-form-item>

          <a-form-item label="确认密码" name="confirmPassword">
            <a-input-password
              v-model:value="form.confirmPassword"
              placeholder="请再次输入密码"
              size="large"
            >
              <template #prefix>
                <LockOutlined />
              </template>
            </a-input-password>
          </a-form-item>

          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              :loading="loading"
              block
              class="register-button"
            >
              注册
            </a-button>
          </a-form-item>

          <div class="login-link">
            已有账户？
            <a @click="goToLogin">立即登录</a>
          </div>
        </a-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { useI18n } from 'vue-i18n';
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  IdcardOutlined,
  PhoneOutlined,
} from '@ant-design/icons-vue';
import { registerUser } from '@/api/auth';

const router = useRouter();
const { t } = useI18n();

const loading = ref(false);

const form = reactive({
  username: '',
  email: '',
  real_name: '',
  phone: '',
  password: '',
  confirmPassword: '',
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string) => {
        if (value !== form.password) {
          return Promise.reject('两次输入的密码不一致');
        }
        return Promise.resolve();
      },
      trigger: 'blur',
    },
  ],
};

const handleRegister = async () => {
  loading.value = true;

  try {
    const payload = {
      username: form.username,
      password: form.password,
      confirm_password: form.confirmPassword,
      email: form.email,
      phone: form.phone,
      real_name: form.real_name,
      // 后端未启用验证码时传空串，保持字段兼容
      captcha: '',
      captcha_id: '',
    };

    await registerUser(payload as any);
    message.success('注册成功');
    router.push('/login');
  } catch (error: any) {
    const detail = error?.response?.data;
    if (detail) {
      const msg = detail.message || detail.detail || '注册失败';
      message.error(msg);
    } else {
      message.error('注册失败');
    }
  } finally {
    loading.value = false;
  }
};

const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
.register-container {
  display: flex;
  min-height: 100vh;
  background: #ffffff;
}

/* 左侧区域 */
.left-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #f9fafb;
}

.welcome-content {
  max-width: 500px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 400;
  color: #6b7280;
  margin-bottom: 16px;
}

.system-name {
  font-size: 48px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 24px;
  line-height: 1.2;
}

.welcome-description {
  font-size: 18px;
  color: #6b7280;
  line-height: 1.6;
}

/* 右侧注册表单 */
.right-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background: #ffffff;
  overflow-y: auto;
}

.register-card {
  background: #ffffff;
  padding: 48px;
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  border: 1px solid #e5e7eb;
}

.register-header {
  text-align: center;
  margin-bottom: 40px;
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.register-subtitle {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.register-form {
  width: 100%;
}

.login-link {
  text-align: center;
  margin-top: 24px;
  color: #6b7280;
  font-size: 14px;
}

.login-link a {
  color: #2563eb;
  text-decoration: none;
  margin-left: 4px;
  cursor: pointer;
  transition: color 0.2s;
}

.login-link a:hover {
  color: #1d4ed8;
}

:deep(.ant-form-item-label > label) {
  font-weight: 600;
  color: #111827;
  font-size: 14px;
}

:deep(.ant-input-affix-wrapper) {
  border-radius: 8px;
  border: 1px solid #d1d5db;
  transition: all 0.2s;
}

:deep(.ant-input-affix-wrapper:focus),
:deep(.ant-input-affix-wrapper-focused) {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

:deep(.ant-input) {
  border: none;
  font-size: 14px;
}

:deep(.ant-input-prefix) {
  color: #9ca3af;
  margin-right: 8px;
}

:deep(.ant-btn-primary) {
  background: #2563eb;
  border-color: #2563eb;
  border-radius: 8px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}

:deep(.ant-btn-primary:hover) {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

:deep(.ant-form-item) {
  margin-bottom: 20px;
}
</style>
