/**
 * 环境变量检查工具
 * 用于在开发环境中检查环境变量配置是否正确
 */

// 检查环境变量配置
export const checkEnvironmentVariables = () => {
  console.log('🔧 环境变量检查');

  // 在Vite中，环境变量可能通过define选项直接定义
  // 或者通过import.meta.env读取
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';
  const appTitle = import.meta.env.VITE_APP_TITLE || 'Hertz Admin';
  const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0';

  // 检查必需的环境变量
  const requiredVars = [
    { key: 'VITE_API_BASE_URL', value: apiBaseUrl },
    { key: 'VITE_APP_TITLE', value: appTitle },
    { key: 'VITE_APP_VERSION', value: appVersion },
  ];

  requiredVars.forEach(({ key, value }) => {
    if (value) {
      console.log(`✅ ${key}: ${value}`);
    } else {
      console.warn(`❌ ${key}: 未设置`);
    }
  });

  // 检查可选的环境变量
  const devServerHost = import.meta.env.VITE_DEV_SERVER_HOST || 'localhost';
  const devServerPort = import.meta.env.VITE_DEV_SERVER_PORT || '3000';

  const optionalVars = [
    { key: 'VITE_DEV_SERVER_HOST', value: devServerHost },
    { key: 'VITE_DEV_SERVER_PORT', value: devServerPort },
  ];

  optionalVars.forEach(({ key, value }) => {
    if (value) {
      console.log(`ℹ️ ${key}: ${value}`);
    } else {
      console.log(`➖ ${key}: 未设置（使用默认值）`);
    }
  });

  console.log('🎉 环境变量检查完成');
};

// 验证环境变量是否有效
export const validateEnvironment = () => {
  // 检查API基础地址
  if (!import.meta.env.VITE_API_BASE_URL) {
    console.warn('⚠️ VITE_API_BASE_URL 未设置，将使用默认值');
  }

  // 检查应用配置
  if (!import.meta.env.VITE_APP_TITLE) {
    console.warn('⚠️ VITE_APP_TITLE 未设置，将使用默认值');
  }

  if (!import.meta.env.VITE_APP_VERSION) {
    console.warn('⚠️ VITE_APP_VERSION 未设置，将使用默认值');
  }

  return {
    isValid: true,
    warnings: [],
  };
};

// 获取API基础地址
export const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';
};

// 获取应用配置
export const getAppConfig = () => {
  return {
    title: import.meta.env.VITE_APP_TITLE || 'Hertz Admin',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    apiBaseUrl: getApiBaseUrl(),
    devServerHost: import.meta.env.VITE_DEV_SERVER_HOST || 'localhost',
    devServerPort: import.meta.env.VITE_DEV_SERVER_PORT || '3000',
  };
};
