# Hertz Studio Django Utils 模块

## 概述

Hertz Studio Django Utils 是一个功能丰富的工具类模块，为 Hertz Server Django 项目提供核心的工具函数、响应格式、验证器和加密服务。该模块采用模块化设计，便于维护和扩展。

## 功能特性

- 🔐 **加密工具**: 提供多种加密算法和密码哈希功能
- 📧 **邮件服务**: 统一的邮件发送接口和验证码邮件模板
- 📋 **响应格式**: 标准化的API响应格式和错误处理
- ✅ **数据验证**: 邮箱、密码、手机号等格式验证
- 🧩 **模块化设计**: 各功能模块独立，便于按需使用

## 模块结构

```
studio_django_utils/
├── __init__.py              # 模块初始化
├── crypto/                  # 加密工具
│   ├── __init__.py
│   ├── encryption_utils.py # 通用加密工具
│   └── password_hashers.py  # 密码哈希器
├── email/                   # 邮件服务
│   ├── __init__.py
│   └── email_service.py    # 邮件发送服务
├── responses/               # 响应格式
│   ├── __init__.py
│   └── HertzResponse.py    # 统一响应类
└── validators/              # 验证器
    ├── __init__.py
    ├── email_validator.py  # 邮箱验证器
    ├── password_validator.py # 密码验证器
    └── phone_validator.py  # 手机号验证器
```

## 核心类说明

### 1. EncryptionUtils 加密工具类

提供多种加密算法和工具函数：

```python
from studio_django_utils.crypto import EncryptionUtils

# MD5哈希
hash_value = EncryptionUtils.md5_hash("password", "salt")

# SHA256哈希
hash_value = EncryptionUtils.sha256_hash("password", "salt")

# 数据加密解密
encrypted = EncryptionUtils.encrypt_data("敏感数据", "password")
decrypted = EncryptionUtils.decrypt_data(encrypted, "password")

# 生成随机盐值
salt = EncryptionUtils.generate_salt(32)
```

### 2. MD5PasswordHasher MD5密码哈希器

兼容旧系统的MD5密码加密：

```python
from studio_django_utils.crypto import MD5PasswordHasher

hasher = MD5PasswordHasher()
encoded_password = hasher.encode("password", "salt")
is_valid = hasher.verify("password", encoded_password)
```

### 3. EmailService 邮件服务类

提供邮件发送功能：

```python
from studio_django_utils.email import EmailService

# 发送普通邮件
success = EmailService.send_email(
    recipient_email="user@example.com",
    subject="邮件主题",
    html_content="<h1>HTML内容</h1>",
    text_content="纯文本内容"
)

# 发送验证码邮件
success = EmailService.send_verification_code(
    recipient_email="user@example.com",
    recipient_name="用户名",
    verification_code="123456",
    code_type="register"
)
```

### 4. HertzResponse 统一响应类

标准化的API响应格式：

```python
from studio_django_utils.responses import HertzResponse

# 成功响应
return HertzResponse.success(data={"user": user_data}, message="操作成功")

# 失败响应
return HertzResponse.fail(message="操作失败", data={"error": "详情"})

# 错误响应
return HertzResponse.error(message="系统错误", error=str(e))

# 验证错误
return HertzResponse.validation_error(message="参数错误", errors=serializer.errors)

# 自定义响应
return HertzResponse.custom(
    success=True, 
    message="自定义消息", 
    data={"custom": "data"},
    code=200
)
```

### 5. 验证器类

提供数据格式验证功能：

```python
from studio_django_utils.validators import (
    EmailValidator, PasswordValidator, PhoneValidator
)

# 邮箱验证
is_valid, message = EmailValidator.validate_email("test@example.com")
normalized_email = EmailValidator.normalize_email(" Test@Example.COM ")

# 密码强度验证
is_valid, errors = PasswordValidator.validate_password_strength("Password123!")
score = PasswordValidator.calculate_password_score("Password123!")
level = PasswordValidator.get_password_strength_level("Password123!")

# 手机号验证
is_valid = PhoneValidator.is_valid_china_mobile("13800138000")
is_valid, message = PhoneValidator.validate_china_mobile("13800138000")
carrier = PhoneValidator.get_mobile_carrier("13800138000")
```

## 安装和配置

### 1. 依赖安装

确保已安装以下依赖：

```bash
pip install Django>=5.2.6
pip install cryptography>=41.0.0
```

### 2. 配置邮件服务

在 `settings.py` 中配置邮件服务：

```python
# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@example.com'
```

### 3. 配置密码哈希器

在 `settings.py` 中配置密码哈希器：

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'studio_django_utils.crypto.password_hashers.MD5PasswordHasher',  # MD5兼容
]
```

## 快速开始

### 1. 导入模块

```python
# 导入整个工具模块
from studio_django_utils import (
    EncryptionUtils,
    MD5PasswordHasher,
    EmailService,
    HertzResponse,
    EmailValidator,
    PasswordValidator,
    PhoneValidator
)

# 或按需导入特定功能
from studio_django_utils.responses import HertzResponse
from studio_django_utils.email import EmailService
```

### 2. 使用示例

```python
# 在Django视图中使用统一响应
from rest_framework.decorators import api_view
from studio_django_utils.responses import HertzResponse

@api_view(['GET'])
def user_profile(request):
    try:
        user_data = {"username": "testuser", "email": "test@example.com"}
        return HertzResponse.success(data=user_data, message="获取用户信息成功")
    except Exception as e:
        return HertzResponse.error(message="获取用户信息失败", error=str(e))

# 发送验证码邮件
from studio_django_utils.email import EmailService

success = EmailService.send_verification_code(
    recipient_email="user@example.com",
    recipient_name="张三",
    verification_code="654321",
    code_type="register"
)

if success:
    print("验证码邮件发送成功")
else:
    print("验证码邮件发送失败")
```

## API接口

### 加密工具 API

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `md5_hash(data, salt)` | MD5哈希加密 | data: str, salt: str | str |
| `sha256_hash(data, salt)` | SHA256哈希加密 | data: str, salt: str | str |
| `encrypt_data(data, password)` | 加密数据 | data: str, password: str | Optional[str] |
| `decrypt_data(encrypted_data, password)` | 解密数据 | encrypted_data: str, password: str | Optional[str] |
| `generate_salt(length)` | 生成随机盐值 | length: int | str |

### 邮件服务 API

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `send_email()` | 发送邮件 | recipient_email, subject, html_content, text_content, from_email | bool |
| `send_verification_code()` | 发送验证码邮件 | recipient_email, recipient_name, verification_code, code_type | bool |

### 响应格式 API

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `success()` | 成功响应 | data, message, code | JsonResponse |
| `fail()` | 失败响应 | message, data, code | JsonResponse |
| `error()` | 错误响应 | message, error, code | JsonResponse |
| `unauthorized()` | 未授权响应 | message, code | JsonResponse |
| `validation_error()` | 验证错误响应 | message, errors, code | JsonResponse |
| `custom()` | 自定义响应 | success, message, data, code, **kwargs | JsonResponse |

### 验证器 API

| 类 | 方法 | 描述 |
|----|------|------|
| `EmailValidator` | `is_valid_email()` | 验证邮箱格式 |
| | `validate_email()` | 验证邮箱并返回详细信息 |
| | `normalize_email()` | 标准化邮箱地址 |
| `PasswordValidator` | `validate_password_strength()` | 验证密码强度 |
| | `calculate_password_score()` | 计算密码强度分数 |
| | `get_password_strength_level()` | 获取密码强度等级 |
| `PhoneValidator` | `is_valid_china_mobile()` | 验证中国大陆手机号 |
| | `validate_china_mobile()` | 验证手机号并返回详细信息 |
| | `normalize_phone()` | 标准化手机号 |

## 配置参数

### 邮件服务配置

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `EMAIL_HOST` | - | SMTP服务器地址 |
| `EMAIL_PORT` | 587 | SMTP端口 |
| `EMAIL_USE_TLS` | True | 使用TLS加密 |
| `EMAIL_HOST_USER` | - | SMTP用户名 |
| `EMAIL_HOST_PASSWORD` | - | SMTP密码 |
| `DEFAULT_FROM_EMAIL` | - | 默认发件人邮箱 |

### 密码验证配置

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `min_length` | 8 | 密码最小长度 |
| `max_length` | 128 | 密码最大长度 |

## 高级用法

### 自定义邮件模板

```python
from studio_django_utils.email import EmailService

# 自定义邮件内容
custom_html = """
<html>
<body>
    <h1>自定义邮件</h1>
    <p>您好 {name}，这是一封自定义邮件。</p>
</body>
</html>
""".format(name="张三")

success = EmailService.send_email(
    recipient_email="user@example.com",
    subject="自定义邮件",
    html_content=custom_html
)
```

### 扩展响应格式

```python
from studio_django_utils.responses import HertzResponse

# 扩展自定义响应
class CustomResponse(HertzResponse):
    @staticmethod
    def paginated(data, total, page, page_size, message="查询成功"):
        """分页响应"""
        pagination = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
        return HertzResponse.success(
            data={"items": data, "pagination": pagination},
            message=message
        )

# 使用扩展响应
return CustomResponse.paginated(
    data=users, 
    total=100, 
    page=1, 
    page_size=20,
    message="用户列表查询成功"
)
```

## 测试

### 单元测试示例

```python
from django.test import TestCase
from studio_django_utils.validators import EmailValidator

class EmailValidatorTest(TestCase):
    def test_valid_email(self):
        """测试有效邮箱地址"""
        is_valid, message = EmailValidator.validate_email("test@example.com")
        self.assertTrue(is_valid)
        self.assertEqual(message, "邮箱地址格式正确")
    
    def test_invalid_email(self):
        """测试无效邮箱地址"""
        is_valid, message = EmailValidator.validate_email("invalid-email")
        self.assertFalse(is_valid)
        self.assertEqual(message, "邮箱地址格式不正确")
```

### 运行测试

```bash
python manage.py test studio_django_utils.tests
```

## 安全考虑

1. **密码安全**: 使用强密码哈希算法，避免明文存储密码
2. **加密安全**: 使用安全的加密算法和随机盐值
3. **输入验证**: 对所有输入数据进行严格验证
4. **错误处理**: 避免泄露敏感错误信息
5. **邮件安全**: 使用TLS加密邮件传输

## 常见问题

### Q: 邮件发送失败怎么办？
A: 检查邮件配置是否正确，包括SMTP服务器、端口、用户名和密码。

### Q: MD5密码哈希是否安全？
A: MD5被认为是不安全的哈希算法，仅用于兼容旧系统。新系统应使用更安全的算法如bcrypt或Argon2。

### Q: 如何自定义响应格式？
A: 可以继承 `HertzResponse` 类并添加自定义方法。

### Q: 验证器是否支持国际手机号？
A: 目前主要支持中国大陆手机号验证，国际手机号验证功能有限。

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 包含加密工具、邮件服务、响应格式、验证器等核心功能

## 🔗 相关链接

- [🏠 返回主项目](../README.md) - Hertz Server Django 主项目
- [🔐 认证授权模块](../studio_django_auth/README.md) - 用户管理和权限控制
- [🖼️ 验证码模块](../studio_django_captcha/README.md) - 图片和邮箱验证码功能
- [📋 代码风格指南](../CODING_STYLE_GUIDE.md) - 开发规范和最佳实践
- [Django 官方文档](https://docs.djangoproject.com/)
- [Django REST Framework 文档](https://www.django-rest-framework.org/)

## 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如有问题或建议，请提交 [Issue](https://github.com/your-org/hertz-server-django/issues) 或联系开发团队。