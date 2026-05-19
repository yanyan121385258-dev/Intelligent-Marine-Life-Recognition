# Hertz Server Django 主项目配置

## 📋 项目概述

Hertz Server Django 是一个基于 Django 和 Django REST Framework 构建的现代化后端服务框架，提供认证授权、验证码、工具类等核心功能模块。主项目配置模块负责整个项目的全局配置、路由管理和基础设置。

## ✨ 核心特性

- **模块化架构**: 采用微服务架构设计，各功能模块独立开发部署
- **RESTful API**: 基于DRF构建的标准REST API接口
- **OpenAPI 3.0文档**: 自动生成的API文档，支持Swagger UI和ReDoc
- **多数据库支持**: 支持SQLite和MySQL，可配置Redis作为缓存和会话存储
- **跨域支持**: 内置CORS跨域请求处理
- **WebSocket支持**: 基于Channels的实时通信能力
- **环境配置**: 使用python-decouple进行环境变量管理

## 📁 项目结构

```
server_django/              # 项目根目录
├── server_django/          # 主项目配置模块
│   ├── __init__.py              # 包初始化文件
│   ├── settings.py              # 项目全局配置
│   ├── urls.py                  # 主URL路由配置
│   ├── asgi.py                  # ASGI应用配置
│   ├── wsgi.py                  # WSGI应用配置
│   └── views.py                 # 根视图函数
├── demo/                  # 演示模块
├── studio_django_captcha/ # 验证码模块
├── studio_django_auth/    # 认证授权模块
├── studio_django_utils/   # 工具类模块
├── manage.py                    # Django管理脚本
├── requirements.txt             # 项目依赖
├── .env                         # 环境变量配置
└── data/                        # 数据目录（SQLite数据库等）
```

## ⚙️ 核心配置文件

### settings.py - 项目全局配置

#### 基础配置
```python
# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥（从环境变量读取）
SECRET_KEY = config('SECRET_KEY', default='django-insecure-...')

# 调试模式
DEBUG = config('DEBUG', default=True, cast=bool)

# 允许的主机
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1')
```

#### 应用配置
```python
INSTALLED_APPS = [
    # Django核心应用
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',        # Django REST Framework
    'corsheaders',           # CORS跨域支持
    'channels',              # WebSocket支持
    'drf_spectacular',       # OpenAPI文档生成
    
    # 本地应用模块
    'demo',                    # 演示模块
    'studio_django_captcha',   # 验证码模块
    'studio_django_auth',      # 认证授权模块
]
```

#### 数据库配置
```python
# 数据库切换配置
USE_REDIS_AS_DB = config('USE_REDIS_AS_DB', default=True, cast=bool)

if USE_REDIS_AS_DB:
    # 开发环境使用SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'data/db.sqlite3',
        }
    }
else:
    # 生产环境使用MySQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME', default='server'),
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default='root'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }
```

#### Redis缓存配置
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### DRF配置
```python
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
```

#### OpenAPI文档配置
```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Hertz Server API',
    'DESCRIPTION': 'API documentation for Hertz Server Django project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}
```

### urls.py - 主路由配置

```python
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from . import views

urlpatterns = [
    # 首页路由
    path('', views.index, name='index'),
    
    # Hertz Captcha路由
    path('api/captcha/', include('studio_django_captcha.urls')),
    
    # Hertz Auth路由
    path('api/', include('studio_django_auth.urls')),
    
    # Demo应用路由
    path('', include('demo.urls')),
    
    # API文档
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置

创建 `.env` 文件：

```ini
# 基础配置
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
USE_REDIS_AS_DB=True
REDIS_URL=redis://127.0.0.1:6379/0

# MySQL配置（如果USE_REDIS_AS_DB=False）
DB_NAME=server
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
```

### 3. 数据库初始化

```bash
# 创建数据库迁移
python manage.py makemigrations

# 应用数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser
```

### 4. 启动开发服务器

```bash
# 启动Django开发服务器
python manage.py runserver

# 访问应用
# 首页: http://localhost:8000/
# API文档: http://localhost:8000/api/docs/
# 演示页面: http://localhost:8000/demo/captcha/
```

## 🔧 配置详解

### 环境变量管理

项目使用 `python-decouple` 进行环境变量管理，支持：
- 从 `.env` 文件读取配置
- 类型转换和默认值设置
- 开发和生产环境分离

### 数据库配置策略

**开发环境**: 使用SQLite + Redis缓存
- 快速启动和开发测试
- 数据存储在SQLite文件
- 会话和缓存使用Redis

**生产环境**: 使用MySQL + Redis缓存  
- 高性能数据库支持
- 数据持久化存储
- Redis用于缓存和会话

### 中间件配置

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # CORS处理
    'django.middleware.security.SecurityMiddleware',  # 安全中间件
    'django.contrib.sessions.middleware.SessionMiddleware',  # 会话管理
    'django.middleware.common.CommonMiddleware',       # 通用处理
    'django.middleware.csrf.CsrfViewMiddleware',      # CSRF保护
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 认证
    'studio_django_auth.utils.middleware.AuthMiddleware',  # 自定义认证
    'django.contrib.messages.middleware.MessageMiddleware',  # 消息框架
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 点击劫持保护
]
```

## 🌐 API文档访问

项目提供完整的OpenAPI 3.0文档：

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

## 🚢 部署配置

### 生产环境部署

1. **环境变量配置**:
```ini
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
USE_REDIS_AS_DB=False
```

2. **静态文件收集**:
```bash
python manage.py collectstatic
```

3. **WSGI部署**:
```python
# 使用Gunicorn + Nginx
# gunicorn server_django.wsgi:application
```

4. **ASGI部署**:
```python
# 使用Daphne + Nginx  
# daphne server_django.asgi:application
```

## 🔒 安全配置

### 生产环境安全设置

```python
# 强制HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF保护
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# 会话安全
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# 安全头部
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## 📊 性能优化

### 缓存策略

```python
# 数据库查询缓存
from django.core.cache import cache

# 使用缓存
cache.set('key', 'value', timeout=300)
value = cache.get('key')
```

### 数据库优化

```python
# 使用select_related减少查询
users = User.objects.select_related('profile').filter(is_active=True)

# 使用prefetch_related优化多对多关系
users = User.objects.prefetch_related('groups', 'permissions')
```

## 🐛 故障排除

### 常见问题

1. **Redis连接失败**: 检查Redis服务是否启动，配置是否正确
2. **数据库迁移错误**: 删除数据库文件重新迁移，或检查MySQL连接
3. **静态文件404**: 运行 `python manage.py collectstatic`
4. **CORS问题**: 检查CORS配置和中间件顺序

### 日志配置

```python
# settings.py 中添加日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## 🔗 相关链接

- [🎮 演示模块](../demo/README.md) - 功能演示和测试页面
- [🔐 认证授权模块](../studio_django_auth/README.md) - 用户管理和权限控制
- [📸 验证码模块](../studio_django_captcha/README.md) - 验证码生成和验证
- [🛠️ 工具类模块](../studio_django_utils/README.md) - 加密、邮件和验证工具
- [🐍 Django文档](https://docs.djangoproject.com/) - Django官方文档
- [🔌 DRF文档](https://www.django-rest-framework.org/) - Django REST Framework文档

---

💡 **提示**: 此配置模块是整个项目的核心，负责协调各功能模块的协同工作。生产部署前请务必检查所有安全配置。