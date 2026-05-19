"""
Hertz Captcha - 一个功能强大的Django验证码应用
"""

__version__ = "1.0.2"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "一个功能强大的Django验证码应用"

# 导出主要类和函数
from .captcha_generator import HertzCaptchaGenerator

__all__ = [
    'HertzCaptchaGenerator',
    '__version__',
]
