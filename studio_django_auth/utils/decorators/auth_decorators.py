from functools import wraps
from studio_django_auth.utils.auth.token_utils import TokenUtils
from studio_django_utils.responses.HertzResponse import HertzResponse

def no_login_required(view_func):
    """
    标记不需要登录的接口装饰器
    
    Args:
        view_func: 视图函数
        
    Returns:
        装饰后的视图函数
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 标记该接口不需要登录验证
        request._no_login_required = True
        return view_func(request, *args, **kwargs)
    
    # 添加属性标记
    wrapper._no_login_required = True
    return wrapper


def login_required(view_func):
    """
    需要登录的接口装饰器
    
    Args:
        view_func: 视图函数
        
    Returns:
        装饰后的视图函数
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断是类方法还是函数视图
        if len(args) >= 2 and hasattr(args[0], '__class__') and hasattr(args[1], 'META'):
            # 类方法：args[0] 是 self，args[1] 是 request
            self, request = args[0], args[1]
            remaining_args = args[2:]
        elif len(args) >= 1 and hasattr(args[0], 'META'):
            # 函数视图：args[0] 是 request
            request = args[0]
            remaining_args = args[1:]
        else:
            return HertzResponse.error("无效的视图函数参数")
        
        # 从请求头获取token
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return HertzResponse.unauthorized("未提供认证令牌")
        
        # 移除Bearer前缀
        if token.startswith('Bearer '):
            token = token[7:]
        
        # 验证token
        payload = TokenUtils.verify_token(token)
        if not payload:
            return HertzResponse.unauthorized("认证令牌无效或已过期")
        
        # 获取用户对象并添加到request中
        try:
            from studio_django_auth.models import HertzUser
            user = HertzUser.objects.get(user_id=payload.get('user_id'), status=1)
            request.user = user
            request.user_id = payload.get('user_id')
            request.username = payload.get('username')
            request.user_roles = payload.get('roles', [])
            request.user_permissions = payload.get('permissions', [])
        except HertzUser.DoesNotExist:
            return HertzResponse.unauthorized("用户不存在或已被禁用")
        
        # 调用原始视图函数
        if 'self' in locals():
            return view_func(self, request, *remaining_args, **kwargs)
        else:
            return view_func(request, *remaining_args, **kwargs)
    
    return wrapper


def permission_required(permission_code):
    """
    需要特定权限的接口装饰器
    
    Args:
        permission_code: 权限代码
        
    Returns:
        装饰器函数
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # 判断是类方法还是函数视图
            if len(args) >= 2 and hasattr(args[0], '__class__') and hasattr(args[1], 'META'):
                # 类方法：args[0] 是 self，args[1] 是 request
                self, request = args[0], args[1]
                remaining_args = args[2:]
            elif len(args) >= 1 and hasattr(args[0], 'META'):
                # 函数视图：args[0] 是 request
                request = args[0]
                remaining_args = args[1:]
            else:
                return HertzResponse.error("无效的视图函数参数")
            
            # 从请求头获取token
            token = request.META.get('HTTP_AUTHORIZATION')
            if not token:
                return HertzResponse.unauthorized("未提供认证令牌")
            
            # 移除Bearer前缀
            if token.startswith('Bearer '):
                token = token[7:]
            
            # 验证token
            payload = TokenUtils.verify_token(token)
            if not payload:
                return HertzResponse.unauthorized("认证令牌无效或已过期")
            
            # 获取用户对象以检查权限
            try:
                from studio_django_auth.models import HertzUser
                user = HertzUser.objects.get(user_id=payload.get('user_id'), status=1)
                
                # 获取用户角色
                user_roles = user.roles.filter(status=1)
                
                # 获取用户权限
                user_permissions = []
                for role in user_roles:
                    # 从角色的菜单中获取权限标识
                    role_menus = role.menus.filter(status=1)  # 只获取启用的菜单
                    for menu in role_menus:
                        if menu.permission:  # 如果菜单有权限标识
                            user_permissions.append(menu.permission)
                
                # 检查权限
                if permission_code not in user_permissions:
                    return HertzResponse.forbidden(f"缺少权限：{permission_code}")
                    
            except HertzUser.DoesNotExist:
                return HertzResponse.unauthorized("用户不存在或已被禁用")
            
            # 添加用户信息到request中
            request.user = user
            request.user_id = payload.get('user_id')
            request.username = payload.get('username')
            request.user_roles = payload.get('roles', [])
            request.user_permissions = user_permissions
            
            # 调用原始视图函数
            if 'self' in locals():
                return view_func(self, request, *remaining_args, **kwargs)
            else:
                return view_func(request, *remaining_args, **kwargs)
        
        return wrapper
    return decorator