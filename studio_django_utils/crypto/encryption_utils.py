import base64
import hashlib
import secrets
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionUtils:
    """
    加密工具类
    提供各种加密解密功能
    """
    
    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """
        生成随机盐值
        
        Args:
            length: 盐值长度
            
        Returns:
            str: Base64编码的盐值
        """
        salt = secrets.token_bytes(length)
        return base64.b64encode(salt).decode('utf-8')
    
    @staticmethod
    def md5_hash(data: str, salt: str = '') -> str:
        """
        MD5哈希加密
        
        Args:
            data: 待加密数据
            salt: 盐值
            
        Returns:
            str: MD5哈希值
        """
        combined = data + salt
        md5_hash = hashlib.md5(combined.encode('utf-8'))
        return md5_hash.hexdigest()
    
    @staticmethod
    def sha256_hash(data: str, salt: str = '') -> str:
        """
        SHA256哈希加密
        
        Args:
            data: 待加密数据
            salt: 盐值
            
        Returns:
            str: SHA256哈希值
        """
        combined = data + salt
        sha256_hash = hashlib.sha256(combined.encode('utf-8'))
        return sha256_hash.hexdigest()
    
    @staticmethod
    def generate_key_from_password(password: str, salt: bytes) -> bytes:
        """
        从密码生成加密密钥
        
        Args:
            password: 密码
            salt: 盐值
            
        Returns:
            bytes: 加密密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def encrypt_data(data: str, password: str) -> Optional[str]:
        """
        使用密码加密数据
        
        Args:
            data: 待加密数据
            password: 加密密码
            
        Returns:
            Optional[str]: 加密后的数据（Base64编码），失败返回None
        """
        try:
            # 生成随机盐值
            salt = secrets.token_bytes(16)
            
            # 从密码生成密钥
            key = EncryptionUtils.generate_key_from_password(password, salt)
            
            # 创建Fernet实例
            fernet = Fernet(key)
            
            # 加密数据
            encrypted_data = fernet.encrypt(data.encode('utf-8'))
            
            # 将盐值和加密数据组合
            combined = salt + encrypted_data
            
            # 返回Base64编码的结果
            return base64.b64encode(combined).decode('utf-8')
        
        except Exception:
            return None
    
    @staticmethod
    def decrypt_data(encrypted_data: str, password: str) -> Optional[str]:
        """
        使用密码解密数据
        
        Args:
            encrypted_data: 加密后的数据（Base64编码）
            password: 解密密码
            
        Returns:
            Optional[str]: 解密后的数据，失败返回None
        """
        try:
            # Base64解码
            combined = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 分离盐值和加密数据
            salt = combined[:16]
            encrypted_bytes = combined[16:]
            
            # 从密码生成密钥
            key = EncryptionUtils.generate_key_from_password(password, salt)
            
            # 创建Fernet实例
            fernet = Fernet(key)
            
            # 解密数据
            decrypted_data = fernet.decrypt(encrypted_bytes)
            
            return decrypted_data.decode('utf-8')
        
        except Exception:
            return None
    
    @staticmethod
    def generate_random_key() -> str:
        """
        生成随机加密密钥
        
        Returns:
            str: Base64编码的随机密钥
        """
        key = Fernet.generate_key()
        return key.decode('utf-8')