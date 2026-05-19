from django.urls import resolve
from django.conf import settings
import re
from studio_django_auth.utils.auth.token_utils import TokenUtils
from studio_django_utils.responses.HertzResponse import HertzResponse


class AuthMiddleware:
    """
    权限认证中间件
    自动处理需要登录的接口的token验证
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # 不需要登录验证的URL模式（支持正则表达式）
        # 优先使用settings中的配置，如果没有则使用默认值
        self.no_auth_patterns = getattr(settings, 'NO_AUTH_PATTERNS', [
            r'^/api/auth/login/?$',
            r'^/api/auth/register/?$', 
            r'^/api/auth/email/code/?$',
            r'^/api/auth/send-email-code/?$',
            r'^/api/auth/password/reset/?$',
            r'^/api/captcha/.*$',
            r'^/api/docs/.*$',
            r'^/api/redoc/.*$', 
            r'^/api/schema/.*$',
            r'^/admin/.*$',
            r'^/static/.*$',
            r'^/media/.*$',
            r'^/demo/.*$',
            r'^/websocket/.*$'
        ])
        
        # 编译正则表达式模式以提高性能
        self.compiled_patterns = [re.compile(pattern) for pattern in self.no_auth_patterns]
    
    def __call__(self, request):
        # 检查是否需要跳过认证
        if self._should_skip_auth(request):
            return self.get_response(request)
        
        # 检查视图函数是否标记为不需要登录
        try:
            resolver_match = resolve(request.path_info)
            view_func = resolver_match.func
            
            # 检查视图函数或类是否有no_login_required标记
            if hasattr(view_func, '_no_login_required'):
                return self.get_response(request)
            
            # 检查类视图的方法是否有no_login_required标记
            if hasattr(view_func, 'view_class'):
                view_class = view_func.view_class
                method_name = request.method.lower()
                if hasattr(view_class, method_name):
                    method = getattr(view_class, method_name)
                    if hasattr(method, '_no_login_required'):
                        return self.get_response(request)
        except:
            # 如果解析URL失败，继续执行认证检查
            pass
        
        # 执行token验证
        auth_result = self._authenticate_request(request)
        if auth_result:
            return auth_result
        
        return self.get_response(request)
    
    def _should_skip_auth(self, request):
        """
        检查是否应该跳过认证
        
        Args:
            request: HTTP请求对象
            
        Returns:
            bool: 是否跳过认证
        """
        path = request.path_info
        
        # 使用正则表达式匹配路径
        for pattern in self.compiled_patterns:
            if pattern.match(path):
                return True
        
        return False
    
    def _authenticate_request(self, request):
        """
        认证请求
        
        Args:
            request: HTTP请求对象
            
        Returns:
            JsonResponse or None: 认证失败时返回错误响应，成功时返回None
        """
        # 从请求头获取token
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return HertzResponse.unauthorized("未提供认证令牌")
        
        # 移除Bearer前缀
        if token.startswith('Bearer '):
            token = token[7:]
        elif token.startswith('Token '):
            token = token[6:]
        
        # 验证token
        payload = TokenUtils.verify_token(token)
        if not payload:
            return HertzResponse.unauthorized("认证令牌无效或已过期")
        
        # 将用户信息添加到request中
        request.user_id = payload.get('user_id')
        request.username = payload.get('username')
        request.user_roles = payload.get('roles', [])
        request.user_permissions = payload.get('permissions', [])
        request.token_payload = payload
        
        return None