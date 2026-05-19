import hashlib
import secrets
from typing import Tuple


class PasswordUtils:
    """
    密码工具类
    提供密码加密、验证等功能
    """
    
    @staticmethod
    def md5_encrypt(password: str) -> str:
        """
        使用MD5加密密码
        
        Args:
            password: 原始密码
            
        Returns:
            str: MD5加密后的密码
        """
        if not password:
            return ''
        
        # 将密码转换为字节串并进行MD5加密
        md5_hash = hashlib.md5(password.encode('utf-8'))
        return md5_hash.hexdigest()
    
    @staticmethod
    def verify_password(password: str, encrypted_password: str) -> bool:
        """
        验证密码是否正确
        
        Args:
            password: 原始密码
            encrypted_password: 加密后的密码
            
        Returns:
            bool: 密码是否正确
        """
        if not password or not encrypted_password:
            return False
        
        return PasswordUtils.md5_encrypt(password) == encrypted_password
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """
        生成随机密码
        
        Args:
            length: 密码长度
            
        Returns:
            str: 随机密码
        """
        import string
        
        # 定义密码字符集
        characters = string.ascii_letters + string.digits + '!@#$%^&*'
        
        # 生成随机密码
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    @staticmethod
    def is_strong_password(password: str) -> Tuple[bool, str]:
        """
        检查密码强度
        
        Args:
            password: 密码
            
        Returns:
            Tuple[bool, str]: (是否强密码, 提示信息)
        """
        if not password:
            return False, "密码不能为空"
        
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        if len(password) > 128:
            return False, "密码长度不能超过128位"
        
        # 检查是否包含数字
        has_digit = any(c.isdigit() for c in password)
        if not has_digit:
            return False, "密码必须包含至少一个数字"
        
        # 检查是否包含字母
        has_letter = any(c.isalpha() for c in password)
        if not has_letter:
            return False, "密码必须包含至少一个字母"
        
        return True, "密码强度符合要求"