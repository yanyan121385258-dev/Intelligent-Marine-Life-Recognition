/**
 * 路由工具函数
 * 用于动态路由相关的辅助功能
 */

// 获取views目录下的所有Vue文件
export const getViewFiles = () => {
  const viewsContext = import.meta.glob('@/views/*.vue');
  return Object.keys(viewsContext).map((path) => path.split('/').pop());
};

// 从文件名生成路由名称
export const generateRouteName = (fileName: string): string => {
  return fileName.replace('.vue', '');
};

// 从文件名生成路由路径
export const generateRoutePath = (fileName: string): string => {
  const routeName = generateRouteName(fileName);
  let routePath = `/${routeName.toLowerCase()}`;

  // 处理特殊命名（驼峰转短横线）
  if (routeName !== routeName.toLowerCase()) {
    routePath = `/${routeName
      .replace(/([A-Z])/g, '-$1')
      .toLowerCase()
      .replace(/^-/, '')}`;
  }

  return routePath;
};

// 生成路由标题
export const generateRouteTitle = (routeName: string): string => {
  const titleMap: Record<string, string> = {
    Dashboard: '仪表板',
    User: '用户管理',
    Profile: '个人资料',
    Settings: '系统设置',
    Test: '样式测试',
    WebSocketTest: 'WebSocket测试',
    NotFound: '页面未找到',
  };

  return titleMap[routeName] || routeName;
};

// 判断路由是否需要认证
export const shouldRequireAuth = (routeName: string): boolean => {
  const publicRoutes = ['Test', 'WebSocketTest'];
  return !(
    publicRoutes.includes(routeName) || // 公开路由列表
    routeName.startsWith('Demo') // Demo开头的页面不需要认证
  );
};

// 获取公开路由列表
export const getPublicRoutes = (): string[] => {
  return ['Test', 'WebSocketTest', 'Demo']; // 可以添加更多公开路由
};

// 打印路由调试信息
export const debugRoutes = () => {
  const viewFiles = getViewFiles();
  const fixedFiles = ['Home.vue', 'Login.vue'];
  const dynamicFiles = viewFiles.filter(
    (file) => !fixedFiles.includes(file) && file !== 'NotFound.vue'
  );

  console.log('🔍 路由调试信息:');
  console.log('📁 所有视图文件:', viewFiles);
  console.log('🔒 固定路由文件:', fixedFiles);
  console.log('🚀 动态路由文件:', dynamicFiles);

  const publicRoutes = getPublicRoutes();
  console.log('🔓 公开路由 (不需要认证):', publicRoutes);

  console.log('\n📋 动态路由配置:');
  dynamicFiles.forEach((file) => {
    const routeName = generateRouteName(file);
    const routePath = generateRoutePath(file);
    const title = generateRouteTitle(routeName);
    const requiresAuth = shouldRequireAuth(routeName);
    const isPublic = !requiresAuth;

    console.log(`  ${file} → ${routePath} (${title}) ${isPublic ? '🔓' : '🔒'}`);
  });

  console.log('\n🎯 Demo页面特殊说明:');
  console.log('  - Demo开头的页面不需要认证 (Demo.vue, DemoPage.vue等)');
  console.log('  - 可以直接访问 /demo 路径');
};

// 在开发环境中自动调用调试函数
if (import.meta.env.DEV) {
  debugRoutes();
}

// 提供全局访问的路由信息查看函数
export const showRoutesInfo = () => {
  console.log('🚀 Hertz Admin 路由配置信息:');
  console.log('📋 完整路由列表:');

  // 注意: 这里需要从路由实例中获取真实数据
  // 由于路由工具函数在路由配置之前加载，这里提供的是示例数据
  // 实际的动态路由信息会在项目启动时通过logRouteInfo()函数显示

  console.log('\n🔒 固定路由 (需要手动配置):');
  console.log('  🔒 / → Home (首页)');
  console.log('  🔓 /login → Login (登录)');

  console.log('\n🚀 动态路由 (自动生成):');
  console.log('  🔒 /dashboard → Dashboard (仪表板)');
  console.log('  🔒 /user → User (用户管理)');
  console.log('  🔒 /profile → Profile (个人资料)');
  console.log('  🔒 /settings → Settings (系统设置)');
  console.log('  🔓 /test → Test (样式测试)');
  console.log('  🔓 /websocket-test → WebSocketTest (WebSocket测试)');
  console.log('  🔓 /demo → Demo (动态路由演示)');

  console.log('\n❓ 404路由:');
  console.log('  ❓ /:pathMatch(.*)* → NotFound (页面未找到)');

  console.log('\n📖 访问说明:');
  console.log('  🔓 公开路由: 可以直接访问，不需要登录');
  console.log('  🔒 私有路由: 需要登录后才能访问');
  console.log('  💡 提示: 可以在浏览器中直接访问这些路径');

  console.log('\n🌐 可用链接:');
  console.log('  http://localhost:3000/ - 首页 (需要登录)');
  console.log('  http://localhost:3000/login - 登录页面');
  console.log('  http://localhost:3000/dashboard - 仪表板 (需要登录)');
  console.log('  http://localhost:3000/user - 用户管理 (需要登录)');
  console.log('  http://localhost:3000/profile - 个人资料 (需要登录)');
  console.log('  http://localhost:3000/settings - 系统设置 (需要登录)');
  console.log('  http://localhost:3000/test - 样式测试 (公开)');
  console.log('  http://localhost:3000/websocket-test - WebSocket测试 (公开)');
  console.log('  http://localhost:3000/demo - 动态路由演示 (公开)');
  console.log('  http://localhost:3000/any-other-path - 404页面 (公开)');

  console.log('\n✅ 路由配置加载完成!');
  console.log('💡 提示: 启动项目后会在控制台看到真正的动态路由信息');
};
