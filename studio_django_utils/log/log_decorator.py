from functools import wraps
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

def operation_log(action_type, module, description=None, target_model=None):
    """
    操作日志装饰器
    
    Args:
        action_type (str): 操作类型，如 'create', 'update', 'delete' 等
        module (str): 操作模块，如 '用户管理', '通知管理' 等
        description (str, optional): 操作描述，如果不提供则自动生成
        target_model (str, optional): 目标模型名称
    
    Usage:
        @operation_log('create', '用户管理', '创建新用户', 'User')
        def create_user(request):
            # 视图函数逻辑
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # 检查是否是类视图方法（第一个参数是self，第二个是request）
            if len(args) >= 2 and hasattr(args[0], '__class__') and hasattr(args[1], 'META'):
                # 类视图方法
                self_instance = args[0]
                request = args[1]
                print(f"\n=== 类视图装饰器被调用 ===")
                print(f"类名: {self_instance.__class__.__name__}")
                print(f"函数名: {view_func.__name__}")
            elif len(args) >= 1 and hasattr(args[0], 'META'):
                # 函数视图
                request = args[0]
                print(f"\n=== 函数视图装饰器被调用 ===")
                print(f"函数名: {view_func.__name__}")
            else:
                # 无法识别的调用方式，直接执行原函数
                return view_func(*args, **kwargs)
            
            print(f"操作类型: {action_type}")
            print(f"模块: {module}")
            print(f"请求方法: {request.method}")
            print(f"请求路径: {request.path}")
            print(f"=== 装饰器调用信息结束 ===\n")
            # 延迟导入避免循环导入
            from studio_django_log.models import OperationLog
            
            # 获取用户信息
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            
            # 获取请求信息
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # 限制长度
            
            # 获取请求数据
            request_data = get_request_data(request)
            
            response = None
            response_status = 200
            target_id = None
            
            try:
                # 执行原始视图函数
                if len(args) >= 2 and hasattr(args[0], '__class__') and hasattr(args[1], 'META'):
                    # 类视图方法，去掉self参数
                    response = view_func(args[0], request, *args[2:], **kwargs)
                else:
                    # 函数视图
                    response = view_func(request, *args[1:], **kwargs)
                
                # 获取响应状态码
                if hasattr(response, 'status_code'):
                    response_status = response.status_code
                
                # 尝试获取目标ID
                target_id = extract_target_id(response, kwargs)
                
            except Exception as e:
                response_status = 500
                logger.error(f"视图函数执行错误: {str(e)}")
                # 打印详细的错误信息到控制台
                import traceback
                print(f"\n=== 装饰器捕获到异常 ===")
                print(f"异常类型: {type(e).__name__}")
                print(f"异常信息: {str(e)}")
                print(f"异常堆栈:")
                traceback.print_exc()
                print(f"=== 装饰器异常信息结束 ===\n")
                # 重新抛出异常，让Django处理
                raise
            
            # 异步记录操作日志
            try:
                print(f"\n=== 开始记录操作日志 ===")
                print(f"用户: {user}")
                print(f"操作类型: {action_type}")
                print(f"模块: {module}")
                print(f"描述: {description or f'{action_type}操作 - {module}'}")
                print(f"目标模型: {target_model}")
                print(f"目标ID: {target_id}")
                print(f"IP地址: {ip_address}")
                print(f"请求数据: {request_data}")
                print(f"响应状态: {response_status}")
                
                log_operation(
                    user=user,
                    action_type=action_type,
                    module=module,
                    description=description or f"{action_type}操作 - {module}",
                    target_model=target_model,
                    target_id=target_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_data=request_data,
                    response_status=response_status
                )
                print(f"操作日志记录成功")
                print(f"=== 操作日志记录结束 ===\n")
            except Exception as log_error:
                # 日志记录失败不应该影响正常业务
                print(f"\n=== 操作日志记录失败 ===")
                print(f"错误类型: {type(log_error).__name__}")
                print(f"错误信息: {str(log_error)}")
                import traceback
                traceback.print_exc()
                print(f"=== 操作日志记录失败信息结束 ===\n")
                logger.error(f"操作日志记录失败: {log_error}")
            
            return response
        
        return wrapper
    return decorator

def get_client_ip(request):
    """
    获取客户端真实IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_request_data(request):
    """
    安全地获取请求数据
    """
    request_data = {}
    try:
        if request.method == 'GET':
            request_data = dict(request.GET)
        elif request.method == 'POST':
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' in content_type:
                if hasattr(request, 'body') and request.body:
                    request_data = json.loads(request.body.decode('utf-8'))
            else:
                request_data = dict(request.POST)
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            if hasattr(request, 'body') and request.body:
                request_data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
        logger.warning(f"解析请求数据失败: {str(e)}")
        request_data = {}
    
    # 过滤敏感信息
    sensitive_fields = ['password', 'token', 'secret', 'key', 'csrf_token']
    if isinstance(request_data, dict):
        for field in sensitive_fields:
            if field in request_data:
                request_data[field] = '***'
    
    return request_data

def extract_target_id(response, kwargs):
    """
    从响应或URL参数中提取目标ID
    """
    target_id = None
    
    # 从响应中获取ID
    try:
        if hasattr(response, 'data') and isinstance(response.data, dict):
            if 'id' in response.data:
                target_id = response.data['id']
            elif 'data' in response.data and isinstance(response.data['data'], dict):
                if 'id' in response.data['data']:
                    target_id = response.data['data']['id']
    except (AttributeError, TypeError):
        pass
    
    # 从URL参数中获取ID
    if not target_id and kwargs:
        for key, value in kwargs.items():
            if key.endswith('_id') or key == 'pk' or key == 'id':
                try:
                    target_id = int(value)
                    break
                except (ValueError, TypeError):
                    pass
    
    return target_id

def log_operation(user, action_type, module, description, target_model=None, 
                 target_id=None, ip_address=None, user_agent=None, 
                 request_data=None, response_status=None):
    """
    记录操作日志
    """
    from studio_django_log.models import OperationLog
    
    # 如果用户未登录，记录为匿名用户操作（可选择是否记录）
    if user is None:
        # 对于某些重要操作，即使是匿名用户也要记录
        # 可以通过配置决定是否记录匿名用户操作
        logger.info(f"记录匿名用户的操作日志: {action_type} - {module} - {description}")
        # 为匿名用户创建一个临时用户对象或跳过用户字段
        # 这里我们选择跳过匿名用户的日志记录，保持原有逻辑
        # 如果需要记录匿名用户操作，可以注释掉下面的return语句
        return
    
    # 限制数据长度避免数据库错误
    if user_agent and len(user_agent) > 500:
        user_agent = user_agent[:500]
    
    if description and len(description) > 255:
        description = description[:255]
    
    # 限制请求数据大小
    if request_data and len(str(request_data)) > 5000:
        request_data = {'message': '请求数据过大，已省略'}
    
    # 使用模型的create_log方法来创建日志
    OperationLog.create_log(
        user=user,
        action_type=action_type,
        module=module,
        description=description,
        target_model=target_model,
        target_id=target_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_data=request_data,
        response_status=response_status
    )

def auto_log(action_type, module=None):
    """
    自动日志装饰器，根据视图类名和方法名自动推断模块和描述
    
    Args:
        action_type (str): 操作类型
        module (str, optional): 模块名称，如果不提供则从视图类名推断
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # 延迟导入避免循环导入
            from studio_django_log.models import OperationLog
            
            # 获取request对象
            request = None
            if args and hasattr(args[0], '__class__') and hasattr(args[0], '__module__'):
                # 这是类方法，request是第二个参数
                request = args[1] if len(args) > 1 else None
                view_instance = args[0]
                class_name = view_instance.__class__.__name__
            else:
                # 这是函数视图，request是第一个参数
                request = args[0] if args else None
                class_name = view_func.__name__
            
            # 检查request对象是否有效
            if not request or not hasattr(request, 'META'):
                return view_func(*args, **kwargs)
            
            # 获取用户信息
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            
            # 自动推断模块名称
            auto_module = module
            if not auto_module:
                if 'User' in class_name:
                    auto_module = '用户管理'
                elif 'Notification' in class_name:
                    auto_module = '通知管理'
                elif 'Config' in class_name:
                    auto_module = '系统配置'
                elif 'File' in class_name:
                    auto_module = '文件管理'
                elif 'AI' in class_name or 'Chat' in class_name:
                    auto_module = 'AI助手'
                elif 'Wiki' in class_name:
                    auto_module = '知识管理'
                else:
                    auto_module = '系统管理'
            
            # 自动生成描述
            action_map = {
                'create': '创建',
                'update': '更新',
                'delete': '删除',
                'view': '查看',
                'list': '列表查看',
                'login': '登录',
                'logout': '登出'
            }
            auto_description = f"{action_map.get(action_type, action_type)} - {auto_module}"
            
            # 获取请求信息
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            request_data = get_request_data(request)
            
            response = None
            response_status = 200
            target_id = None
            
            try:
                # 执行原始视图函数
                response = view_func(*args, **kwargs)
                
                # 获取响应状态码
                if hasattr(response, 'status_code'):
                    response_status = response.status_code
                
                # 尝试获取目标ID
                target_id = extract_target_id(response, kwargs)
                
            except Exception as e:
                response_status = 500
                logger.error(f"视图函数执行错误: {str(e)}")
                # 重新抛出异常，让Django处理
                raise
            
            # 异步记录操作日志
            try:
                log_operation(
                    user=user,
                    action_type=action_type,
                    module=auto_module,
                    description=auto_description,
                    target_model=auto_module,
                    target_id=target_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_data=request_data,
                    response_status=response_status
                )
            except Exception as log_error:
                # 日志记录失败不应该影响正常业务
                logger.error(f"操作日志记录失败: {log_error}")
            
            return response
        
        return wrapper
    return decorator