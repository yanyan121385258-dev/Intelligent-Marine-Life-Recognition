<template>
  <div class="module-setup">
    <a-card title="功能模块配置" class="module-setup-card">
      <div class="module-setup-intro">
        <p class="intro-title">使用说明</p>
        <p>
          1）本页面用于功能模块
          DIY：勾选需要启用的模块，未勾选的模块将在菜单和路由中隐藏，仅作为运行时屏蔽，不影响源码文件。
        </p>
        <p>
          2）配置保存成功后，选择结果会以 <code>hertz_enabled_modules</code> 的形式保存在浏览器
          Local Storage 中，下次执行
          <code>npm run dev</code> 时如果存在该记录，将直接进入系统而不再展示本配置页。
        </p>
        <p>
          3）如需重新调整模块，请打开浏览器开发者工具 → <strong>Application</strong> →
          <strong>Local Storage</strong> → 选择当前站点，删除键
          <code>hertz_enabled_modules</code>，然后刷新页面即可重新回到本页重新选择。
        </p>
        <a-alert
          type="warning"
          show-icon
          message="一键裁剪（可选）"
          description="在本页确认模块选择并关闭运行环境后，可在终端运行 npm run prune，按提示对未勾选模块进行一键裁剪（支持仅屏蔽或直接删除相关页面）。"
        />
      </div>
      <a-tabs v-model:activeKey="activeKey">
        <a-tab-pane key="admin" tab="管理端模块">
          <a-checkbox-group v-model:value="adminSelected" class="module-group">
            <div v-for="m in adminModules" :key="m.key" class="module-item">
              <a-checkbox :value="m.key">
                <span class="module-label">{{ m.label }}</span>
              </a-checkbox>
            </div>
          </a-checkbox-group>
        </a-tab-pane>
        <a-tab-pane key="user" tab="用户端模块">
          <a-checkbox-group v-model:value="userSelected" class="module-group">
            <div v-for="m in userModules" :key="m.key" class="module-item">
              <a-checkbox :value="m.key">
                <span class="module-label">{{ m.label }}</span>
              </a-checkbox>
            </div>
          </a-checkbox-group>
        </a-tab-pane>
      </a-tabs>
      <div class="module-setup-actions">
        <a-button style="margin-right: 8px" @click="resetToDefault">恢复默认</a-button>
        <a-button style="margin-right: 8px" @click="saveModules">保存配置并刷新</a-button>
        <a-button type="primary" @click="saveModulesAndGoLogin">保存并跳转登录</a-button>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  HERTZ_MODULES,
  getEnabledModuleKeys,
  getModulesByGroup,
  setEnabledModuleKeys,
  type HertzModuleGroup,
} from '@/config/hertz_modules';

const activeKey = ref<HertzModuleGroup>('admin');

const adminModules = computed(() => getModulesByGroup('admin'));
const userModules = computed(() => getModulesByGroup('user'));

const adminSelected = ref<string[]>([]);
const userSelected = ref<string[]>([]);

const loadCurrentSelection = () => {
  const enabled = getEnabledModuleKeys();
  adminSelected.value = enabled.filter((k) => k.indexOf('admin.') === 0);
  userSelected.value = enabled.filter((k) => k.indexOf('user.') === 0);
};

const resetToDefault = () => {
  const defaultEnabled = HERTZ_MODULES.filter((m) => m.defaultEnabled).map((m) => m.key);
  setEnabledModuleKeys(defaultEnabled);
  loadCurrentSelection();
};

const saveModules = () => {
  const merged = adminSelected.value.concat(userSelected.value);
  setEnabledModuleKeys(merged);
  if (typeof window !== 'undefined') {
    window.location.reload();
  }
};

const saveModulesAndGoLogin = () => {
  const merged = adminSelected.value.concat(userSelected.value);
  setEnabledModuleKeys(merged);
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
};

onMounted(() => {
  loadCurrentSelection();
});
</script>

<style scoped lang="scss">
.module-setup {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 48px 16px;
  background: #f5f5f5;
}

.module-setup-card {
  width: 100%;
  max-width: 960px;
}

.module-setup-intro {
  margin-bottom: 16px;
  color: #666;
  font-size: 14px;
}

.intro-title {
  margin-bottom: 4px;
  font-weight: 600;
  color: #333;
}

.module-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-item {
  padding: 8px 0;
}

.module-label {
  margin-left: 4px;
}

.module-setup-actions {
  margin-top: 16px;
  text-align: right;
}
</style>
