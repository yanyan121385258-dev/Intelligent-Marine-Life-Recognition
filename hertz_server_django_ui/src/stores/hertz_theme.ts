import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

// 主题配置接口
export interface ThemeConfig {
  // 导航栏
  headerBg: string;
  headerText: string;
  headerBorder: string;

  // 背景
  pageBg: string;
  contentBg: string;

  // 组件背景
  cardBg: string;
  cardBorder: string;

  // 主色调
  primaryColor: string;
  textPrimary: string;
  textSecondary: string;
}

// 海洋科技主题
const oceanTheme: ThemeConfig = {
  headerBg: 'rgba(0, 29, 61, 0.95)',
  headerText: '#90e0ef',
  headerBorder: 'rgba(0, 212, 255, 0.3)',
  pageBg: 'linear-gradient(180deg, #000814 0%, #001d3d 30%, #003566 60%, #00509d 100%)',
  contentBg: 'transparent',
  cardBg: 'rgba(0, 29, 61, 0.9)',
  cardBorder: 'rgba(0, 212, 255, 0.4)',
  primaryColor: '#00d4ff',
  textPrimary: '#caf0f8',
  textSecondary: '#90e0ef',
};

// 默认主题
const defaultTheme: ThemeConfig = {
  headerBg: '#ffffff',
  headerText: '#111827',
  headerBorder: '#e5e7eb',
  pageBg: '#ffffff',
  contentBg: '#ffffff',
  cardBg: '#ffffff',
  cardBorder: '#e5e7eb',
  primaryColor: '#2563eb',
  textPrimary: '#111827',
  textSecondary: '#6b7280',
};

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<ThemeConfig>({ ...oceanTheme });

  // 从 localStorage 加载主题
  const loadTheme = () => {
    const savedTheme = localStorage.getItem('customTheme');
    if (savedTheme) {
      try {
        theme.value = { ...defaultTheme, ...JSON.parse(savedTheme) };
        applyTheme(theme.value);
      } catch (e) {
        console.error('Failed to load theme:', e);
      }
    } else {
      applyTheme(theme.value);
    }
  };

  // 应用主题
  const applyTheme = (config: ThemeConfig) => {
    const root = document.documentElement;

    // 设置 CSS 变量
    root.style.setProperty('--theme-header-bg', config.headerBg);
    root.style.setProperty('--theme-header-text', config.headerText);
    root.style.setProperty('--theme-header-border', config.headerBorder);
    root.style.setProperty('--theme-page-bg', config.pageBg);
    root.style.setProperty('--theme-content-bg', config.contentBg);
    root.style.setProperty('--theme-card-bg', config.cardBg);
    root.style.setProperty('--theme-card-border', config.cardBorder);
    root.style.setProperty('--theme-primary', config.primaryColor);
    root.style.setProperty('--theme-text-primary', config.textPrimary);
    root.style.setProperty('--theme-text-secondary', config.textSecondary);
  };

  // 更新主题
  const updateTheme = (newTheme: Partial<ThemeConfig>) => {
    theme.value = { ...theme.value, ...newTheme };
    applyTheme(theme.value);
    localStorage.setItem('customTheme', JSON.stringify(theme.value));
  };

  // 重置主题
  const resetTheme = () => {
    theme.value = { ...defaultTheme };
    applyTheme(theme.value);
    localStorage.removeItem('customTheme');
  };

  // 监听主题变化，自动应用
  watch(
    theme,
    (newTheme) => {
      applyTheme(newTheme);
    },
    { deep: true }
  );

  return {
    theme,
    loadTheme,
    updateTheme,
    resetTheme,
    applyTheme,
  };
});
