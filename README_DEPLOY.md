# Hertz Studio Django 项目部署指南

## 环境要求

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 16+ | 前端运行环境 |
| Redis | 6.0+ | 缓存服务（可选） |

---

## 快速开始

### 方式一：一键启动（推荐）

1. **双击运行 `run.bat`**
2. 等待自动安装依赖（首次运行）
3. 浏览器访问 http://localhost:3001

### 方式二：手动启动

```bash
# 1. 安装后端依赖
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# 2. 安装前端依赖
cd server_django_ui
npm install
cd ..

# 3. 启动后端
venv\Scripts\python.exe start_server.py

# 4. 启动前端（另开一个终端）
cd server_django_ui
npm run dev
```

---

## 登录账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | hertz | hertz |
| 普通用户 | demo | 123456 |

---

## 服务地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3001 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/api/schema/swagger/ |

---

## 常见问题

### 1. Python 未找到
确保已安装 Python 3.10+，并添加到系统 PATH 环境变量。

### 2. npm 安装失败
确保已安装 Node.js 16+，可以使用以下命令检查：
```bash
node --version
npm --version
```

### 3. 端口被占用
- 8000 端口被占用：修改 `start_server.py` 中的端口
- 3001 端口被占用：修改 `server_django_ui/vite.config.ts` 中的端口

### 4. Redis 连接失败
Redis 是可选服务，若未安装 Redis，系统会使用内存缓存，不影响基本功能。

---

## 项目结构

```
HertzStudioDjango/
├── run.bat                 # 一键启动脚本
├── package_project.bat     # 打包部署脚本
├── manage.py               # Django 管理脚本
├── requirements.txt        # Python 依赖
├── server_django/          # Django 后端
├── server_django_ui/       # Vue 前端
├── studio_django_utils/    # 工具模块
├── static/                 # 静态资源
└── docs/                  # 项目文档
```

---

## 功能模块

- [x] 用户认证与权限管理 (JWT)
- [x] 图形验证码
- [x] 通知公告
- [x] 操作日志
- [x] 知识库
- [x] 系统监控
- [x] AI 对话 (Ollama)
- [x] YOLO 目标检测
- [x] 代码生成器

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 5 + DRF + Channels |
| 前端 | Vue 3 + TypeScript + Ant Design Vue |
| 数据库 | SQLite (默认) / MySQL |
| 缓存 | Redis |
| AI | YOLO + Ollama |

---

如有疑问，请查阅 `docs/` 目录下的详细文档。
