import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { i18n } from './locales';
import { checkEnvironmentVariables, validateEnvironment } from './utils/env';
import './styles/index.scss';

// 导入Ant Design Vue
import 'ant-design-vue/dist/antd.css';

// 开发环境检查
if (import.meta.env.DEV) {
  checkEnvironmentVariables();
  validateEnvironment();
}

// 创建Vue应用实例
const app = createApp(App);

// 使用Pinia状态管理
const pinia = createPinia();
app.use(pinia);

// 使用路由
app.use(router);

// 使用国际化
app.use(i18n);

// 初始化应用设置
import { useAppStore } from './stores/app';
const appStore = useAppStore();
appStore.initAppSettings();

// 检查用户认证状态
import { useUserStore } from './stores/user';
const userStore = useUserStore();
userStore.checkAuth();

// 初始化主题（必须在挂载前加载）
import { useThemeStore } from './stores/theme';
const themeStore = useThemeStore();
themeStore.loadTheme();

// 挂载应用
app.mount('#app');
