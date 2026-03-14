import hashlib
from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare


class MD5PasswordHasher(BasePasswordHasher):
    """
    MD5密码哈希器
    用于兼容旧系统的MD5密码加密
    """
    algorithm = 'md5'
    library = 'hashlib'
    
    def encode(self, password, salt):
        """
        编码密码
        
        Args:
            password: 原始密码
            salt: 盐值
            
        Returns:
            str: 编码后的密码
        """
        hash_obj = hashlib.md5((salt + password).encode('utf-8'))
        hash_value = hash_obj.hexdigest()
        return f'{self.algorithm}${salt}${hash_value}'
    
    def verify(self, password, encoded):
        """
        验证密码
        
        Args:
            password: 原始密码
            encoded: 编码后的密码
            
        Returns:
            bool: 验证结果
        """
        algorithm, salt, hash_value = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)
    
    def safe_summary(self, encoded):
        """
        返回密码的安全摘要信息
        
        Args:
            encoded: 编码后的密码
            
        Returns:
            dict: 摘要信息
        """
        algorithm, salt, hash_value = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return {
            'algorithm': algorithm,
            'salt': salt[:6] + '...',
            'hash': hash_value[:6] + '...',
        }
    
    def harden_runtime(self, password, encoded):
        """
        硬化运行时间（MD5不需要）
        """
        pass
    
    def must_update(self, encoded):
        """
        检查是否需要更新密码编码
        
        Args:
            encoded: 编码后的密码
            
        Returns:
            bool: 是否需要更新
        """
        return False