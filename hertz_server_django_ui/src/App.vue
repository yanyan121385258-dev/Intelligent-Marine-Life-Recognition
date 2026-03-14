<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useUserStore } from './stores/hertz_user';
import { useThemeStore } from './stores/hertz_theme';
import { RouterView } from 'vue-router';
import { ConfigProvider } from 'ant-design-vue';
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import enUS from 'ant-design-vue/es/locale/en_US';

const userStore = useUserStore();
const themeStore = useThemeStore();

// 主题配置 - 海洋科技风格
const theme = ref({
  algorithm: 'dark' as 'default' | 'dark' | 'compact',
  token: {
    colorPrimary: '#00d4ff',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    borderRadius: 16,
    fontSize: 14,
    colorBgBase: '#001d3d',
    colorBgContainer: 'rgba(0, 29, 61, 0.9)',
    colorBgElevated: 'rgba(0, 29, 61, 0.95)',
    colorBorder: 'rgba(0, 212, 255, 0.4)',
    colorText: '#caf0f8',
    colorTextSecondary: '#90e0ef',
    colorTextPlaceholder: 'rgba(202, 240, 248, 0.5)',
  },
});

// 语言配置
const locale = ref(zhCN);

const showLayout = computed(() => {
  return userStore.isLoggedIn;
});

// 初始化主题
onMounted(() => {
  themeStore.loadTheme();
  document.documentElement.setAttribute('data-theme', 'ocean');
});
</script>

<template>
  <div id="app">
    <ConfigProvider :theme="theme" :locale="locale">
      <RouterView />
    </ConfigProvider>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100%;
}

body {
  margin: 0;
  padding: 0;
  height: 100%;
  background: linear-gradient(180deg, #000814 0%, #001d3d 30%, #003566 60%, #00509d 100%);
  color: #caf0f8;
}
</style>
