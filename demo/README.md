# Hertz Demo 演示模块

## 📋 模块概述

Hertz Demo 模块是一个功能演示和测试模块，提供了完整的示例代码和交互式演示页面，帮助开发者快速了解和使用 Hertz Server Django 框架的各项功能特性。

## ✨ 功能特性

- **验证码演示**: 展示多种验证码类型的生成、刷新和验证功能
- **邮件系统演示**: 提供邮件模板预览和发送测试功能
- **WebSocket演示**: 实时通信功能演示和测试
- **交互式界面**: 美观的Web界面，支持实时操作和反馈
- **完整示例代码**: 提供可直接参考的实现代码

## 📁 模块结构

```
demo/
├── __init__.py          # 模块初始化
├── apps.py              # Django应用配置
├── models.py            # 数据模型（预留）
├── views.py             # 视图函数和业务逻辑
├── urls.py              # URL路由配置
├── tests.py             # 单元测试
├── consumers.py          # WebSocket消费者
├── routing.py           # WebSocket路由
└── templates/           # 模板文件
    ├── captcha_demo.html    # 验证码演示页面
    ├── email_demo.html      # 邮件系统演示页面
    └── websocket_demo.html   # WebSocket演示页面
```

## 🎯 核心功能详解

### 1. 验证码演示功能

验证码演示页面提供三种验证码类型：
- **随机字符验证码**: 随机生成的字母数字组合
- **数学运算验证码**: 简单的数学计算验证
- **单词验证码**: 英文单词验证

**主要功能**:
- 验证码实时生成和刷新
- 前端Ajax验证
- 后端表单验证
- 验证码类型切换

### 2. 邮件系统演示功能

邮件演示页面提供多种邮件模板：
- **欢迎邮件**: 用户注册欢迎邮件模板
- **系统通知**: 系统消息通知模板
- **邮箱验证**: 邮箱验证邮件模板
- **自定义邮件**: 支持自定义主题和内容

**主要功能**:
- 邮件模板实时预览
- 邮件发送测试
- 收件人邮箱验证
- 发送状态反馈

### 3. WebSocket演示功能

WebSocket演示页面提供实时通信功能：
- **连接状态管理**: 显示WebSocket连接状态
- **消息发送接收**: 实时消息通信
- **广播功能**: 消息广播演示
- **错误处理**: 连接异常处理

## 🚀 API接口

### 演示页面路由

| 路由 | 方法 | 描述 |
|------|------|------|
| `/demo/captcha/` | GET | 验证码演示页面 |
| `/demo/email/` | GET | 邮件系统演示页面 |
| `/demo/websocket/` | GET | WebSocket演示页面 |
| `/websocket/test/` | GET | WebSocket测试页面 |

### Ajax接口

**验证码相关**:
- `POST /demo/captcha/` (Ajax): 验证码刷新和验证
- 请求体: `{"action": "refresh/verify", "captcha_id": "...", "user_input": "..."}`

**邮件发送**:
- `POST /demo/email/` (Ajax): 发送演示邮件
- 请求体: 邮件类型、收件人邮箱、自定义内容等

## ⚙️ 配置参数

### 邮件配置（settings.py）
```python
# 邮件服务器配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

### WebSocket配置
```python
# ASGI配置
ASGI_APPLICATION = 'server_django.asgi.application'

# Channel layers配置
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

## 🛠️ 快速开始

### 1. 访问演示页面

启动开发服务器后，访问以下URL：

```bash
# 验证码演示
http://localhost:8000/demo/captcha/

# 邮件系统演示  
http://localhost:8000/demo/email/

# WebSocket演示
http://localhost:8000/demo/websocket/
```

### 2. 测试验证码功能

1. 打开验证码演示页面
2. 选择验证码类型
3. 点击验证码图片可刷新
4. 输入验证码进行验证
5. 观察验证结果反馈

### 3. 测试邮件功能

1. 打开邮件演示页面
2. 选择邮件模板类型
3. 输入收件人邮箱
4. 点击发送测试邮件
5. 查看发送状态

### 4. 测试WebSocket功能

1. 打开WebSocket演示页面
2. 点击"连接"按钮建立连接
3. 在输入框中发送消息
4. 观察消息接收和广播
5. 测试断开重连功能

## 🔧 高级用法

### 自定义邮件模板

在 `views.py` 中的 `generate_email_content` 函数中添加新的邮件模板：

```python
def generate_email_content(email_type, recipient_name, custom_subject='', custom_message=''):
    email_templates = {
        'your_template': {
            'subject': '您的邮件主题',
            'html_template': '''
            <html>
            <!-- 您的HTML模板内容 -->
            </html>
            '''
        }
    }
    # ...
```

### 扩展验证码类型

在验证码演示中扩展新的验证码类型：

```python
# 在 captcha_demo 函数中添加新的验证码类型
captcha_types = {
    'random_char': '随机字符验证码',
    'math': '数学运算验证码',
    'word': '单词验证码',
    'new_type': '您的新验证码类型'  # 新增类型
}
```

### WebSocket消息处理

在 `consumers.py` 中扩展WebSocket消息处理逻辑：

```python
class DemoConsumer(WebsocketConsumer):
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'custom_message':
            # 处理自定义消息类型
            await self.handle_custom_message(data)
```

## 🧪 测试

### 运行单元测试

```bash
python manage.py test demo
```

### 测试覆盖范围

- 验证码功能测试
- 邮件发送测试
- WebSocket连接测试
- 页面渲染测试

## 🔒 安全考虑

### 验证码安全
- 验证码有效期限制
- 验证次数限制
- 防止暴力破解

### 邮件安全
- 收件人邮箱验证
- 发送频率限制
- 防止邮件滥用

### WebSocket安全
- 连接认证
- 消息内容过滤
- 防止DDoS攻击

## ❓ 常见问题

### Q: 邮件发送失败怎么办？
A: 检查邮件服务器配置，确保SMTP设置正确，邮箱密码为应用专用密码。

### Q: WebSocket连接失败怎么办？
A: 检查Redis服务是否运行，确保CHANNEL_LAYERS配置正确。

### Q: 验证码验证总是失败？
A: 检查验证码存储后端（Redis）是否正常运行。

### Q: 如何添加新的演示功能？
A: 在views.py中添加新的视图函数，在urls.py中配置路由，在templates中添加模板文件。

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 包含验证码、邮件、WebSocket演示功能
- 提供完整的示例代码和文档

## 🔗 相关链接

- [🏠 返回主项目](../README.md) - Hertz Server Django 主项目文档
- [🔐 认证授权模块](../studio_django_auth/README.md) - 用户管理和权限控制
- [🛠️ 工具类模块](../studio_django_utils/README.md) - 加密、邮件和验证工具
- [📋 代码风格指南](../docs/CODING_STYLE.md) - 开发规范和最佳实践

---

💡 **提示**: 此模块主要用于功能演示和学习参考，生产环境请根据实际需求进行适当调整和优化。