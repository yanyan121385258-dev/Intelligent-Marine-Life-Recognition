import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from django.conf import settings


class TokenUtils:
    """
    Token工具类
    提供JWT令牌的生成、验证等功能
    """
    
    # 默认密钥，实际使用时应从settings中获取
    DEFAULT_SECRET_KEY = 'hertz-auth-secret-key-2025'
    
    @staticmethod
    def get_secret_key() -> str:
        """
        获取JWT密钥
        
        Returns:
            str: JWT密钥
        """
        return getattr(settings, 'JWT_SECRET_KEY', TokenUtils.DEFAULT_SECRET_KEY)
    
    @staticmethod
    def generate_token(user_data, expires_hours: int = 24) -> str:
        """
        生成JWT令牌
        
        Args:
            user_data: 用户数据字典或用户ID字符串
            expires_hours: 过期时间（小时）
            
        Returns:
            str: JWT令牌
        """
        # 兼容旧版本调用方式
        if isinstance(user_data, str):
            # 如果是字符串，假设是user_id
            payload_data = {'user_id': user_data}
        elif isinstance(user_data, dict):
            payload_data = user_data.copy()
        else:
            raise ValueError("user_data must be dict or str")
        
        # 生成唯一的JTI（JWT ID）
        jti = str(uuid.uuid4())
        
        # 设置过期时间（使用timestamp）
        now = datetime.utcnow()
        exp = now + timedelta(hours=expires_hours)
        
        # 构建payload
        payload = {
            **payload_data,
            'jti': jti,
            'iat': int(now.timestamp()),
            'exp': int(exp.timestamp())
        }
        
        # 生成JWT令牌
        token = jwt.encode(payload, TokenUtils.get_secret_key(), algorithm='HS256')
        return token
    
    @staticmethod
    def generate_refresh_token(user_data, expires_hours: int = 24 * 7) -> str:
        """
        生成刷新令牌
        
        Args:
            user_data: 用户数据字典
            expires_hours: 过期时间（小时），默认7天
            
        Returns:
            str: 刷新令牌
        """
        return TokenUtils.generate_token(user_data, expires_hours)
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Optional[Dict[str, Any]]: 解码后的payload，验证失败返回None
        """
        try:
            payload = jwt.decode(token, TokenUtils.get_secret_key(), algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            # 令牌已过期
            return None
        except jwt.InvalidTokenError:
            # 令牌无效
            return None
    
    @staticmethod
    def refresh_token(token: str, expires_hours: int = 24) -> Optional[str]:
        """
        刷新JWT令牌
        
        Args:
            token: 原JWT令牌
            expires_hours: 新令牌过期时间（小时）
            
        Returns:
            Optional[str]: 新的JWT令牌，验证失败返回None
        """
        payload = TokenUtils.verify_token(token)
        if not payload:
            return None
        
        # 提取用户数据（排除JWT标准字段）
        user_data = {k: v for k, v in payload.items() if k not in ['jti', 'iat', 'exp']}
        
        # 生成新令牌
        new_token = TokenUtils.generate_token(user_data, expires_hours)
        
        return new_token
    
    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict[str, str]]:
        """
        从JWT令牌中获取用户信息
        
        Args:
            token: JWT令牌
            
        Returns:
            Optional[Dict[str, str]]: 用户信息，验证失败返回None
        """
        payload = TokenUtils.verify_token(token)
        if not payload:
            return None
        
        return {
            'user_id': payload.get('user_id'),
            'username': payload.get('username')
        }