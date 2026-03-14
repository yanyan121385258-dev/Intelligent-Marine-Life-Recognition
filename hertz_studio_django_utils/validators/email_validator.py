import re
from typing import Tuple


class EmailValidator:
    """
    邮箱验证器
    提供邮箱格式验证功能
    """
    
    # 邮箱正则表达式
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        验证邮箱格式是否正确
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 邮箱格式是否正确
        """
        if not email or not isinstance(email, str):
            return False
        
        return bool(EmailValidator.EMAIL_PATTERN.match(email.strip()))
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        验证邮箱并返回详细信息
        
        Args:
            email: 邮箱地址
            
        Returns:
            Tuple[bool, str]: (是否有效, 提示信息)
        """
        if not email:
            return False, "邮箱地址不能为空"
        
        if not isinstance(email, str):
            return False, "邮箱地址必须是字符串"
        
        email = email.strip()
        
        if len(email) == 0:
            return False, "邮箱地址不能为空"
        
        if len(email) > 254:
            return False, "邮箱地址长度不能超过254个字符"
        
        if not EmailValidator.EMAIL_PATTERN.match(email):
            return False, "邮箱地址格式不正确"
        
        # 检查本地部分长度（@符号前的部分）
        local_part = email.split('@')[0]
        if len(local_part) > 64:
            return False, "邮箱用户名部分长度不能超过64个字符"
        
        return True, "邮箱地址格式正确"
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        标准化邮箱地址
        
        Args:
            email: 邮箱地址
            
        Returns:
            str: 标准化后的邮箱地址
        """
        if not email or not isinstance(email, str):
            return ''
        
        # 去除首尾空格并转换为小写
        return email.strip().lower()
    
    @staticmethod
    def get_email_domain(email: str) -> str:
        """
        获取邮箱域名
        
        Args:
            email: 邮箱地址
            
        Returns:
            str: 邮箱域名
        """
        if not EmailValidator.is_valid_email(email):
            return ''
        
        return email.split('@')[1].lower()
    
    @staticmethod
    def is_common_email_provider(email: str) -> bool:
        """
        检查是否为常见邮箱服务商
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 是否为常见邮箱服务商
        """
        common_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            '163.com', '126.com', 'qq.com', 'sina.com', 'sohu.com'
        }
        
        domain = EmailValidator.get_email_domain(email)
        return domain in common_providers