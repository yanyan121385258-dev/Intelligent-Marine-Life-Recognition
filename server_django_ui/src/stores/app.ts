import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { i18n } from '@/locales';

// 主题类型
export type Theme = 'light' | 'dark' | 'auto';

// 语言类型
export type Language = 'zh-CN' | 'en-US';

export const useAppStore = defineStore('app', () => {
  // 状态
  const theme = ref<Theme>('light');
  const language = ref<Language>('zh-CN');
  const collapsed = ref<boolean>(false);
  const loading = ref<boolean>(false);

  // 计算属性
  const isDark = computed(() => {
    if (theme.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return theme.value === 'dark';
  });

  const currentLanguage = computed(() => language.value);

  // 方法
  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme;
    localStorage.setItem('theme', newTheme);

    // 应用主题到HTML
    const html = document.documentElement;
    if (newTheme === 'dark' || (newTheme === 'auto' && isDark.value)) {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  };

  const setLanguage = (newLanguage: Language) => {
    language.value = newLanguage;
    localStorage.setItem('language', newLanguage);

    // 设置i18n语言
    i18n.global.locale.value = newLanguage;
  };

  const toggleCollapsed = () => {
    collapsed.value = !collapsed.value;
  };

  const setLoading = (state: boolean) => {
    loading.value = state;
  };

  const initAppSettings = () => {
    // 从本地存储恢复设置
    const savedTheme = localStorage.getItem('theme') as Theme;
    const savedLanguage = localStorage.getItem('language') as Language;

    if (savedTheme) {
      setTheme(savedTheme);
    }

    if (savedLanguage) {
      setLanguage(savedLanguage);
    } else {
      // 根据浏览器语言自动设置
      const browserLang = navigator.language;
      if (browserLang.startsWith('zh')) {
        setLanguage('zh-CN');
      } else {
        setLanguage('en-US');
      }
    }
  };

  return {
    // 状态
    theme,
    language,
    collapsed,
    loading,

    // 计算属性
    isDark,
    currentLanguage,

    // 方法
    setTheme,
    setLanguage,
    toggleCollapsed,
    setLoading,
    initAppSettings,
  };
});
