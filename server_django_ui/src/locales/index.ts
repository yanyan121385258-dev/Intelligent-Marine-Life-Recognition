import { createI18n } from 'vue-i18n';
import zhCN from './zh-CN';
import enUS from './en-US';

const messages = {
  'zh-CN': zhCN,
  'en-US': enUS,
};

export const i18n = createI18n({
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages,
  legacy: false,
  globalInjection: true,
});

export default i18n;
