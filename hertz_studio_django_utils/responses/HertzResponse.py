from django.http import JsonResponse
from typing import Any, Dict, Optional


class HertzResponse:
    """
    Hertz统一响应类
    提供标准化的API响应格式
    """
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> JsonResponse:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: HTTP状态码
            
        Returns:
            JsonResponse: 标准化的成功响应
        """
        response_data = {
            'success': True,
            'code': code,
            'message': message,
            'data': data
        }
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})
    
    @staticmethod
    def fail(message: str = "操作失败", data: Any = None, code: int = 400) -> JsonResponse:
        """
        失败响应（业务逻辑失败）
        
        Args:
            message: 失败消息
            data: 响应数据
            code: HTTP状态码
            
        Returns:
            JsonResponse: 标准化的失败响应
        """
        response_data = {
            'success': False,
            'code': code,
            'message': message,
            'data': data
        }
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})
    
    @staticmethod
    def error(message: str = "系统错误", error: str = None, code: int = 500) -> JsonResponse:
        """
        错误响应（系统错误）
        
        Args:
            message: 错误消息
            error: 详细错误信息
            code: HTTP状态码
            
        Returns:
            JsonResponse: 标准化的错误响应
        """
        response_data = {
            'success': False,
            'code': code,
            'message': message
        }
        
        if error:
            response_data['error'] = error
            
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})
    
    @staticmethod
    def unauthorized(message: str = "未授权访问", code: int = 401) -> JsonResponse:
        """
        未授权响应
        
        Args:
            message: 响应消息
            code: HTTP状态码
            
        Returns:
            JsonResponse: 标准化的未授权响应
        """
        response_data = {
            'success': False,
            'code': code,
            'message': message
        }
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})
    
    @staticmethod
    def forbidden(message: str = "禁止访问", code: int = 403) -> JsonResponse:
        """
        禁止访问响应
        
        Args:
            message: 响应消息
            code: HTTP状态码
            
        Returns:
            JsonResponse: 标准化的禁止访问响应
        """
        response_data = {
            'success': False,
            'code': code,
            'message': message
        }
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})
    
    @staticmethod
    def not_found(message: str = "资源未找到", code: int = 404) -> JsonResponse:
        """
        资源未找到响应
        
        Args:
            message: 响应消息
            code: HTTP状态码
            
        Returns:
            JsonResponse: 标准化的资源未找到响应
        """
        response_data = {
            'success': False,
            'code': code,
            'message': message
        }
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})
    
    @staticmethod
    def validation_error(message: str = "参数验证失败", errors: Dict = None, code: int = 422) -> JsonResponse:
        """
        参数验证错误响应
        
        Args:
            message: 响应消息
            errors: 验证错误详情
            code: HTTP状态码
            
        Returns:
            JsonResponse: 标准化的参数验证错误响应
        """
        response_data = {
            'success': False,
            'code': code,
            'message': message
        }
        
        if errors:
            response_data['errors'] = errors
            
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})
    
    @staticmethod
    def custom(success: bool, message: str, data: Any = None, code: int = 200, **kwargs) -> JsonResponse:
        """
        自定义响应
        
        Args:
            success: 是否成功
            message: 响应消息
            data: 响应数据
            code: HTTP状态码
            **kwargs: 其他自定义字段
            
        Returns:
            JsonResponse: 自定义响应
        """
        response_data = {
            'success': success,
            'code': code,
            'message': message
        }
        
        if data is not None:
            response_data['data'] = data
            
        # 添加其他自定义字段
        response_data.update(kwargs)
        
        return JsonResponse(response_data, status=code, json_dumps_params={'ensure_ascii': False})