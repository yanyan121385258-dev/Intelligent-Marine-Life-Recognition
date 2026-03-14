<div align="center">

<h1>通用大模型模板 · Hertz Admin + AI</h1>

现代化的管理后台前端模板，面向二次开发的前端工程师。内置账号体系、权限路由、主题美化、知识库、YOLO 模型全流程（管理 / 类别 / 告警 / 历史）等典型模块。

<p>
基于 Vite + Vue 3 + TypeScript + Ant Design Vue + Pinia + Vue Router 构建
</p>

</div>

---

## ✨ 特性（面向前端）

- **工程化完善**：TS 强类型、模块化 API、统一请求封装、权限化菜单/路由
- **设计统一**：全局“超现代风格”主题，卡片 / 弹窗 / 按钮 / 输入 / 分页风格一致
- **业务可复用**：
  - 文章管理：分类树 + 列表搜索 + 编辑/发布
  - YOLO 模型：模型管理、模型类别管理、告警处理中心、检测历史管理
  - AI 助手：多会话列表 + 消息记录 + 多布局对话界面（含错误调试信息）
  - 认证体系：登录/注册、验证码
- **可扩展**：清晰的目录划分和命名规范，方便直接加模块或替换现有实现

## 🧩 技术栈

- 构建：Vite
- 语言：TypeScript
- 框架：Vue 3（Composition API）
- UI：Ant Design Vue
- 状态：Pinia
- 路由：Vue Router

## 📦 项目结构与职责

> 根目录：`通用大模型模板/`

```bash
通用大模型模板/
└─ hertz_server_diango_ui_2/              # 前端工程（Vite）
   ├─ public/                             # 公共静态资源（不走打包器）
   ├─ src/
   │  ├─ api/                             # 接口定义（auth / yolo / knowledge / captcha / ai ...）
   │  │   └─ yolo.ts                      # YOLO 模型 & 检测 & 类别相关 API
   │  ├─ locales/                         # 国际化文案
   │  ├─ router/                          # 路由与菜单配置
   │  │   ├─ admin_menu.ts                # 管理端菜单 + 路由映射（权限 key）
   │  │   ├─ user_menu_ai.ts              # 用户端菜单 + 路由映射（含 AI 助手）
   │  │   └─ index.ts                     # Vue Router 实例 + 全局路由守卫
   │  ├─ stores/                          # Pinia Store
   │  │   ├─ hertz_app.ts                 # 全局应用设置（语言、布局、菜单折叠等）
   │  │   ├─ hertz_user.ts                # 用户 / 鉴权状态
   │  │   └─ hertz_theme.ts               # 主题配置与 CSS 变量
   │  ├─ styles/                          # 全局样式与变量
   │  │   ├─ index.scss                   # 全局组件风格覆盖（Button / Table / Modal ...）
   │  │   └─ variables.scss               # 主题色、阴影、圆角等变量
   │  ├─ utils/                           # 工具方法 & 基础设施
   │  │   ├─ hertz_request.ts             # Axios 封装（baseURL、拦截器、错误提示）
   │  │   ├─ hertz_url.ts                 # 统一 URL 构造（API / 媒体 / WebSocket）
   │  │   ├─ hertz_env.ts                 # 读取 & 校验 env 变量
   │  │   └─ hertz_router_utils.ts        # 路由相关工具 & 调试
   │  ├─ views/                           # 所有页面
   │  │   ├─ admin_page/                  # 管理端页面
   │  │   │   ├─ ModelManagement.vue      # YOLO 模型管理
   │  │   │   ├─ AlertLevelManagement.vue # 模型类别管理
   │  │   │   ├─ DetectionHistoryManagement.vue # 检测历史管理
   │  │   │   └─ ...                      # 其他管理端模块
   │  │   ├─ user_pages/                  # 用户端页面（检测端 + AI 助手）
   │  │   │   ├─ index.vue                # 用户端主布局 + 顶部导航
   │  │   │   ├─ AiChat.vue               # AI 助手对话页面
   │  │   │   ├─ YoloDetection.vue        # 离线检测页面
   │  │   │   ├─ LiveDetection.vue        # 实时检测页面（WebSocket）
   │  │   │   └─ ...                      # 告警中心 / 通知中心 / 知识库等
   │  │   ├─ Login.vue                    # 登录页
   │  │   └─ register.vue                 # 注册页
   │  ├─ App.vue                          # 应用根组件
   │  └─ main.ts                          # 入口文件（挂载 Vue / 路由 / Pinia）
   ├─ .env.development                    # 开发环境变量（前端专用）
   ├─ .env.production                     # 生产构建环境变量
   ├─ vite.config.ts                      # Vite 配置（代理、构建、别名等）
   └─ package.json
```

## 📁 文件与命名规范（建议）

- **组件 / 页面**
  - 页面：`src/views/admin_page/FooBarManagement.vue`，以业务 + Management 命名
  - 纯组件：放到 `src/components/`，使用大驼峰命名，如 `UserSelector.vue`
- **接口文件**
  - 同一业务一个文件：`src/api/yolo.ts`、`src/api/auth.ts`
  - 内部导出 `xxxApi` 对象 + TS 类型：`type AlertLevel`, `type YoloModel` 等
- **样式**
  - 全局或主题相关：放 `src/styles/`（注意不要在这里写页面私有样式）
  - 单页面样式：使用 `<style scoped lang="scss">` 写在对应 `.vue` 内
- **工具函数**
  - 通用工具：`src/utils/` 下按领域拆分，如 `hertz_url.ts`、`hertz_env.ts`

## 🌐 后端 IP / 域名配置指引（前端视角最重要）

当前工程已经统一了后端地址配置，只需要 **改 2 个地方**：

1. **环境变量文件**（推荐只改这个）

   - `hertz_server_diango_ui_2/.env.development`
   - `hertz_server_diango_ui_2/.env.production`

   两个文件里都有一行：

   ```bash
   # 示例：开发环境
   VITE_API_BASE_URL=http://localhost:8000
   ```

   约定：

   - **只写协议 + 域名/IP + 端口**，不要包含 `/api`
     - ✅ `http://localhost:8000`
     - ❌ `http://localhost:8000/api`
   - 开发与生产可指向不同后端，只要保证同样的接口路径即可。

2. **Vite 代理 & URL 工具**（已接好，通常不用改）

   - `vite.config.ts`
     - 利用 `loadEnv` 读取 `VITE_API_BASE_URL`，自动去掉末尾 `/`：

       ```ts
       const env = loadEnv(mode, process.cwd(), '')
       const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:3000'
       const backendOrigin = apiBaseUrl.replace(/\/+$/, '')
       ```

     - 开发环境通过代理转发：

       ```ts
       server: {
         proxy: {
           '/api': { target: backendOrigin, changeOrigin: true },
           '/media': { target: backendOrigin, changeOrigin: true }
         }
       }

       define: {
         __VITE_API_BASE_URL__: JSON.stringify(`${backendOrigin}/api`)
       }
       ```

   - `src/utils/hertz_url.ts`

     - 统一获取后端基础地址：

       ```ts
       export function getBackendBaseUrl(): string {
         return import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'
       }
       ```

     - 构造 HTTP / WebSocket / 媒体地址：

       ```ts
       export function getApiBaseUrl() {
         return import.meta.env.DEV ? '' : getBackendBaseUrl()
       }

       export function getMediaBaseUrl() {
         if (import.meta.env.DEV) return ''
         return getBackendBaseUrl().replace('/api', '')
       }

       export function getFullFileUrl(relativePath: string) {
         const baseURL = getBackendBaseUrl()
         return `${baseURL}${relativePath}`
       }
       ```

   - `src/utils/hertz_request.ts`

     - Axios 实例的 `baseURL` 在开发环境为空字符串（走 Vite 代理）；生产环境使用 `VITE_API_BASE_URL`：

       ```ts
       const isDev = import.meta.env.DEV
       const baseURL = isDev ? '' : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000')
       ```

👉 **结论：前端同事只需要改 `.env.development` 和 `.env.production` 里的 `VITE_API_BASE_URL`，其余 URL 都通过工具/代理自动生效，无需到处搜 `localhost`。**

## 🚀 快速开始

```bash
# 进入工程目录
cd hertz_server_diango_ui_2

# 安装依赖
npm i

# 开发启动（默认 http://localhost:3001）
npm run dev
```

## 🔧 关键模块速览

- **主题与 Design System**
  - 入口：`src/styles/index.scss`、`src/styles/variables.scss`
  - 内容：按钮 / 表格 / 弹窗 / 输入框 等统一风格，含毛玻璃、hover、active、focus 细节

- **菜单与路由**
  - `src/router/admin_menu.ts`：单文件维护管理端菜单树 + 路由映射 + 权限标识
  - 面包屑逻辑已整理：不再重复展示“首页/”，只保留当前层级链路

- **YOLO 模块**
  - `ModelManagement.vue`：模型上传 / 列表 / 启用、拖拽上传区
  - `AlertLevelManagement.vue`：模型类别管理，支持单条 & 批量修改告警等级
  - `DetectionHistoryManagement.vue`：检测历史列表、图片/视频预览

- **认证模块**
  - API：`src/api/auth.ts`
  - 页面：`src/views/Login.vue`、`src/views/register.vue`
  - 注册表单字段已与后端约定一致：
    `username, password, confirm_password, email, phone, real_name, captcha, captcha_id`

## 🧪 常见问题（FAQ）

- **需要改哪些地方才能连上新的后端 IP？**
  - 只改：`.env.development` 和 `.env.production` 的 `VITE_API_BASE_URL`
  - 不需要：修改页面内的 `http://localhost:xxxx`，已统一收敛到工具函数

- **接口不走 / 返回字段对不上？**
  - 对比：`src/api/*.ts` 里定义的请求路径与 payload
  - 打开浏览器 Network 看真实请求 URL、body 与响应

- **页面样式和设计稿不一致？**
  - 先看 `src/styles/index.scss` 是否有全局覆盖
  - 再查对应 `.vue` 文件中的 scoped 样式是否有特殊处理

## 🛠️ 二次开发建议

- **新增管理模块**
  - 在 `src/views/admin_page/` 下新增页面，如 `FooBarManagement.vue`
  - 在 `src/router/admin_menu.ts` 中增加菜单配置（path + component + permission）

- **扩展接口**
  - 在 `src/api/` 新增 `xxx.ts`，导出 `xxxApi` 对象
  - 使用统一的 `request` 封装（`hertz_request.ts`），保持错误处理一致

- **改造主题 / 品牌色**
  - 修改 `src/styles/variables.scss` 中的主色、背景色、圆角、阴影
  - 如需大改导航栏、卡片风格，优先在全局样式里做统一，而不是每页重新写

## 🧩 模块选择与模板模式

- **模块配置文件**
  - 路径：`src/config/hertz_modules.ts`
  - 内容：
    - 使用 `HERTZ_MODULES` 统一管理“管理端 / 用户端”各功能模块
    - 每个模块包含：`key`（模块标识）、`label`（展示名称）、`group`（admin/user）、`defaultEnabled`（是否默认启用）
  - 运行时通过 `isModuleEnabled` / `getEnabledModuleKeys` 控制路由和菜单是否展示对应模块。

- **模块选择页面（功能 DIY）**
  - 页面：`src/views/ModuleSetup.vue`
  - 路由：`/template/modules`
  - 说明：
    1. 勾选需要启用的模块，未勾选的模块在菜单和路由中隐藏（仅运行时屏蔽，不改动源码）。
    2. 点击“保存配置并刷新”可多次预览效果；点击“保存并跳转登录”会在保存后跳转到登录页。
    3. 选择结果会以 `hertz_enabled_modules` 的形式保存在浏览器 Local Storage 中。

- **模板模式开关**
  - 通过环境变量控制：`VITE_TEMPLATE_SETUP_MODE`
  - 建议在开发环境 (`.env.development`) 中开启：

    ```bash
    VITE_TEMPLATE_SETUP_MODE=true
    ```

  - 当模板模式开启且浏览器中 **没有** `hertz_enabled_modules` 记录时，路由守卫会在首次进入时自动重定向到 `/template/modules`，强制先完成模块选择。
  - 如果已经配置过模块，下次 `npm run dev` 将直接进入系统。如需重新进入模块选择页：
    1. 打开浏览器开发者工具 → Application → Local Storage
    2. 选择当前站点，删除键 `hertz_enabled_modules`
    3. 刷新页面即可再次进入模块选择流程。

## ✂️ 一键裁剪（npm run prune）

> 适用于已经确定“哪些功能模块不再需要”的场景，用于真正瘦身前端代码体积。建议在执行前先提交一次 Git。

- **脚本位置与命令**
  - 脚本：`scripts/prune-modules.mjs`
  - 命令：

    ```bash
    npm run prune
    ```

- **推荐使用流程**
  1. 启动开发环境：`npm run dev`。
  2. 打开 `/template/modules`，通过勾选确认“需要保留的模块”，用“保存配置并刷新”反复调试菜单/路由效果。
  3. 确认无误后，关闭开发服务器。
  4. 在终端执行 `npm run prune`，按照 CLI 提示：
     - 选择要“裁剪掉”的模块（通常是你在模块选择页面中未勾选的模块）。
     - 选择裁剪模式：
       - **模式 1：仅屏蔽**
         - 修改 `admin_menu.ts` / `user_menu_ai.ts` 中对应模块的 `moduleKey`，加上 `__pruned__` 前缀
         - 注释组件映射行，使这些模块在菜单和路由中完全隐藏
         - **不删除任何 `.vue` 文件**，方便后续恢复
       - **模式 2：删除**
         - 在模式 1 的基础上，额外删除对应模块的视图文件，如 `src/views/admin_page/UserManagement.vue` 等
         - 这是不可逆操作，建议先在模式 1 下验证，再使用模式 2 做最终瘦身

- **影响范围（前端）**
  - 管理端：
    - `src/router/admin_menu.ts` 中对应模块的菜单配置和组件映射
    - `src/views/admin_page/*.vue` 中不需要的页面（仅在删除模式下移除）
  - 用户端：
    - `src/router/user_menu_ai.ts` 中对应模块配置
    - `src/views/user_pages/*.vue` 中不需要的页面（仅在删除模式下移除）

## 📜 NPM 脚本

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview",
    "prune": "node scripts/prune-modules.mjs"
  }
}
```

