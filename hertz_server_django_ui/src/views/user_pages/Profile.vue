<template>
  <div class="profile-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        <UserOutlined class="title-icon" />
        个人资料
      </h1>
      <p class="page-description">管理您的个人信息和账户设置</p>
    </div>

    <!-- 用户信息卡片 -->
    <div class="user-info-section">
      <div class="user-info-card">
        <div class="user-avatar-section">
          <a-upload :show-upload-list="false" :before-upload="handleAvatarBeforeUpload">
            <a-avatar
              :size="100"
              class="avatar"
              :src="userForm.avatar || userStore.userInfo?.avatar"
            >
              <template #icon>
                <UserOutlined />
              </template>
            </a-avatar>
          </a-upload>
          <div class="avatar-info">
            <div class="username">{{ userForm.username || '用户' }}</div>
            <div class="user-role">普通用户</div>
            <div class="avatar-hint">点击头像更换图片</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 资料表单区域 -->
    <div class="profile-container">
      <div class="profile-wrapper">
        <div class="panel-header">
          <div class="header-left">
            <div class="panel-icon">
              <SettingOutlined />
            </div>
            <div class="title-group">
              <h3 class="panel-title">基本信息</h3>
              <span class="panel-subtitle">更新您的个人资料信息</span>
            </div>
          </div>
        </div>

        <div class="panel-content">
          <a-form :model="userForm" layout="vertical" @finish="handleSubmit" class="profile-form">
            <div class="form-grid">
              <div class="form-section">
                <h4 class="section-title">
                  <UserOutlined />
                  账户信息
                </h4>
                <a-row :gutter="24">
                  <a-col :span="12">
                    <a-form-item label="用户名" name="username" class="form-item">
                      <a-input v-model:value="userForm.username" disabled class="form-input">
                        <template #prefix>
                          <UserOutlined />
                        </template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                  <a-col :span="12">
                    <a-form-item label="邮箱地址" name="email" class="form-item">
                      <a-input
                        v-model:value="userForm.email"
                        class="form-input"
                        placeholder="请输入邮箱地址"
                      >
                        <template #prefix>
                          <MailOutlined />
                        </template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                </a-row>
              </div>

              <div class="form-section">
                <h4 class="section-title">
                  <IdcardOutlined />
                  个人信息
                </h4>
                <a-row :gutter="24">
                  <a-col :span="12">
                    <a-form-item label="真实姓名" name="real_name" class="form-item">
                      <a-input
                        v-model:value="userForm.real_name"
                        class="form-input"
                        placeholder="请输入真实姓名"
                      >
                        <template #prefix>
                          <IdcardOutlined />
                        </template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                  <a-col :span="12">
                    <a-form-item label="手机号码" name="phone" class="form-item">
                      <a-input
                        v-model:value="userForm.phone"
                        class="form-input"
                        placeholder="请输入手机号码"
                      >
                        <template #prefix>
                          <PhoneOutlined />
                        </template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                </a-row>
              </div>

              <div class="form-section">
                <h4 class="section-title">
                  <CalendarOutlined />
                  其他信息
                </h4>
                <a-row :gutter="24">
                  <a-col :span="12">
                    <a-form-item label="性别" name="gender" class="form-item">
                      <a-select
                        v-model:value="userForm.gender"
                        class="form-select"
                        placeholder="请选择性别"
                      >
                        <a-select-option :value="0">未知</a-select-option>
                        <a-select-option :value="1">男</a-select-option>
                        <a-select-option :value="2">女</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                  <a-col :span="12">
                    <a-form-item label="生日" name="birthday" class="form-item">
                      <a-date-picker
                        v-model:value="userForm.birthday"
                        class="form-date-picker"
                        placeholder="请选择生日"
                        style="width: 100%"
                      />
                    </a-form-item>
                  </a-col>
                </a-row>
              </div>
            </div>

            <div class="form-actions">
              <a-button
                type="primary"
                html-type="submit"
                :loading="loading"
                class="submit-btn"
                size="large"
              >
                <template #icon>
                  <SaveOutlined />
                </template>
                保存更改
              </a-button>
              <a-button @click="resetForm" class="reset-btn" size="large">
                <template #icon>
                  <ReloadOutlined />
                </template>
                重置表单
              </a-button>
            </div>
          </a-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  UserOutlined,
  SettingOutlined,
  IdcardOutlined,
  CalendarOutlined,
  SaveOutlined,
  ReloadOutlined,
  MailOutlined,
  PhoneOutlined,
} from '@ant-design/icons-vue';
import { userApi, type User } from '@/api/user';
import { useUserStore } from '@/stores/hertz_user';
import dayjs from 'dayjs';

const loading = ref(false);
const avatarUploading = ref(false);
const userStore = useUserStore();

const userForm = ref<Partial<User>>({
  username: '',
  email: '',
  real_name: '',
  phone: '',
  avatar: '',
  gender: 0,
  birthday: '',
});

const fetchUserInfo = async () => {
  try {
    const response = await userApi.getUserInfo();
    if (response.success) {
      userForm.value = {
        ...response.data,
        birthday: response.data.birthday ? dayjs(response.data.birthday) : undefined,
      };
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
    message.error('获取用户信息失败');
  }
};

const handleSubmit = async () => {
  loading.value = true;
  try {
    const submitData: any = {
      ...userForm.value,
      birthday: userForm.value.birthday
        ? dayjs(userForm.value.birthday as any).format('YYYY-MM-DD')
        : undefined,
    };

    // 头像通过单独的上传接口处理，这里不再提交 avatar 字段，避免 URL 校验报错
    if ('avatar' in submitData) {
      delete submitData.avatar;
    }

    const response = await userApi.updateUserInfo(submitData);
    if (response.success) {
      message.success('个人信息更新成功！');
      await fetchUserInfo();
    }
  } catch (error) {
    console.error('更新失败:', error);
    message.error('更新失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

const resetForm = async () => {
  try {
    await fetchUserInfo();
    message.success('表单已重置为最新数据');
  } catch (error) {
    console.error('重置失败:', error);
    message.error('重置失败，请刷新页面');
  }
};

const handleAvatarBeforeUpload = async (file: File) => {
  const isImage = file.type.startsWith('image/');
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isImage) {
    message.error('只能上传图片文件作为头像');
    return false;
  }
  if (!isLt2M) {
    message.error('头像图片大小不能超过 2MB');
    return false;
  }

  avatarUploading.value = true;
  try {
    const res: any = await userApi.uploadAvatar(file);

    // 兼容两种返回结构：
    // 1) 标准 { success, message, data: { avatar, ... } }
    // 2) 直接返回用户对象 { avatar, ... }
    const updatedUser = res?.data ?? res;
    // 后端返回字段为 data.avatar_url，这里兼容 avatar 和 avatar_url
    const newAvatar = updatedUser?.avatar || updatedUser?.avatar_url;

    if (newAvatar) {
      // 更新当前页面表单
      userForm.value.avatar = newAvatar;

      // 更新全局用户 store，导航栏头像立即刷新
      if (userStore.userInfo) {
        userStore.userInfo.avatar = newAvatar;
        localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo));
      }

      const ok = typeof res?.success === 'boolean' ? res.success : true;
      if (ok) {
        message.success(res?.message || '头像上传成功');
      } else {
        message.error(res?.message || '头像上传失败');
      }
    } else {
      message.error(res?.message || '头像上传失败：未返回头像地址');
    }
  } catch (error: any) {
    message.error(error?.message || '头像上传失败，请稍后重试');
  } finally {
    avatarUploading.value = false;
  }

  // 阻止 a-upload 自己提交，由我们手动处理
  return false;
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped lang="scss">
.profile-page {
  padding: 24px;
  background: var(--theme-page-bg, #f5f5f5);
  min-height: 100vh;

  .page-header {
    margin-bottom: 24px;
    text-align: center;

    .page-title {
      font-size: 2rem;
      font-weight: 700;
      color: var(--theme-text-primary, #1e293b);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;

      .title-icon {
        color: var(--theme-primary, #3b82f6);
      }
    }

    .page-description {
      color: var(--theme-text-secondary, #64748b);
      font-size: 1.1rem;
      margin: 0;
    }
  }

  .user-info-section {
    max-width: 1200px;
    margin: 0 auto 24px;

    .user-info-card {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      padding: 32px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      border: 1px solid var(--theme-card-border, #e5e7eb);

      .user-avatar-section {
        display: flex;
        align-items: center;
        gap: 24px;

        .avatar {
          background: linear-gradient(
            135deg,
            var(--theme-primary, #3b82f6) 0%,
            var(--theme-primary, #2563eb) 100%
          );
          border: 3px solid var(--theme-card-border, #e5e7eb);
          cursor: pointer;
        }

        .avatar-info {
          .username {
            font-size: 24px;
            font-weight: 700;
            color: var(--theme-text-primary, #1e293b);
            margin-bottom: 8px;
          }

          .user-role {
            color: var(--theme-text-secondary, #64748b);
            font-size: 14px;
            font-weight: 500;
          }

          .avatar-hint {
            margin-top: 4px;
            font-size: 12px;
            color: var(--theme-text-secondary, #94a3b8);
          }
        }
      }
    }
  }

  .profile-container {
    max-width: 1200px;
    margin: 0 auto;

    .profile-wrapper {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      border: 1px solid var(--theme-card-border, #e5e7eb);
      display: flex;
      flex-direction: column;

      .panel-header {
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
        flex-shrink: 0;
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;

          .panel-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(
              135deg,
              var(--theme-primary, #3b82f6) 0%,
              var(--theme-primary, #2563eb) 100%
            );
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
          }

          .title-group {
            .panel-title {
              color: var(--theme-text-primary, #1e293b);
              font-size: 16px;
              font-weight: 600;
              margin: 0 0 4px 0;
            }

            .panel-subtitle {
              color: var(--theme-text-secondary, #64748b);
              font-size: 14px;
            }
          }
        }
      }

      .panel-content {
        flex: 1;
        padding: 24px;

        .profile-form {
          .form-grid {
            display: flex;
            flex-direction: column;
            gap: 32px;

            .form-section {
              .section-title {
                font-size: 16px;
                font-weight: 600;
                color: var(--theme-text-primary, #1e293b);
                margin: 0 0 20px 0;
                display: flex;
                align-items: center;
                gap: 8px;
                padding-bottom: 12px;
                border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
              }

              .form-item {
                margin-bottom: 20px;
              }
            }
          }

          .form-actions {
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid var(--theme-card-border, #e5e7eb);

            .submit-btn,
            .reset-btn {
              border-radius: 8px;
              height: 44px;
              padding: 0 32px;
              font-weight: 500;
              font-size: 15px;
            }
          }
        }
      }
    }
  }
}
</style>
