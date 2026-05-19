import re
from typing import Tuple


class PhoneValidator:
    """
    手机号验证器
    提供手机号格式验证功能
    """
    
    # 中国大陆手机号正则表达式
    CHINA_MOBILE_PATTERN = re.compile(
        r'^1[3-9]\d{9}$'
    )
    
    # 国际手机号正则表达式（简化版）
    INTERNATIONAL_PATTERN = re.compile(
        r'^\+?[1-9]\d{1,14}$'
    )
    
    @staticmethod
    def is_valid_china_mobile(phone: str) -> bool:
        """
        验证中国大陆手机号格式是否正确
        
        Args:
            phone: 手机号
            
        Returns:
            bool: 手机号格式是否正确
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # 去除空格和连字符
        phone = phone.replace(' ', '').replace('-', '')
        
        return bool(PhoneValidator.CHINA_MOBILE_PATTERN.match(phone))
    
    @staticmethod
    def is_valid_international_phone(phone: str) -> bool:
        """
        验证国际手机号格式是否正确
        
        Args:
            phone: 手机号
            
        Returns:
            bool: 手机号格式是否正确
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # 去除空格和连字符
        phone = phone.replace(' ', '').replace('-', '')
        
        return bool(PhoneValidator.INTERNATIONAL_PATTERN.match(phone))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        验证手机号格式是否正确（默认使用中国大陆手机号验证）
        
        Args:
            phone: 手机号
            
        Returns:
            bool: 手机号格式是否正确
        """
        return PhoneValidator.is_valid_china_mobile(phone)
    
    @staticmethod
    def validate_china_mobile(phone: str) -> Tuple[bool, str]:
        """
        验证中国大陆手机号并返回详细信息
        
        Args:
            phone: 手机号
            
        Returns:
            Tuple[bool, str]: (是否有效, 提示信息)
        """
        if not phone:
            return False, "手机号不能为空"
        
        if not isinstance(phone, str):
            return False, "手机号必须是字符串"
        
        # 去除空格和连字符
        phone = phone.replace(' ', '').replace('-', '')
        
        if len(phone) == 0:
            return False, "手机号不能为空"
        
        if len(phone) != 11:
            return False, "手机号长度必须为11位"
        
        if not phone.isdigit():
            return False, "手机号只能包含数字"
        
        if not phone.startswith('1'):
            return False, "手机号必须以1开头"
        
        if phone[1] not in '3456789':
            return False, "手机号第二位必须是3-9之间的数字"
        
        return True, "手机号格式正确"
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        标准化手机号
        
        Args:
            phone: 手机号
            
        Returns:
            str: 标准化后的手机号
        """
        if not phone or not isinstance(phone, str):
            return ''
        
        # 去除空格、连字符和括号
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # 如果是中国大陆手机号且以+86开头，去除+86
        if phone.startswith('+86') and len(phone) == 14:
            phone = phone[3:]
        elif phone.startswith('86') and len(phone) == 13:
            phone = phone[2:]
        
        return phone
    
    @staticmethod
    def get_mobile_carrier(phone: str) -> str:
        """
        获取手机号运营商（仅支持中国大陆）
        
        Args:
            phone: 手机号
            
        Returns:
            str: 运营商名称
        """
        if not PhoneValidator.is_valid_china_mobile(phone):
            return '未知'
        
        phone = PhoneValidator.normalize_phone(phone)
        prefix = phone[:3]
        
        # 中国移动
        china_mobile_prefixes = {
            '134', '135', '136', '137', '138', '139',
            '147', '150', '151', '152', '157', '158', '159',
            '172', '178', '182', '183', '184', '187', '188',
            '195', '197', '198'
        }
        
        # 中国联通
        china_unicom_prefixes = {
            '130', '131', '132', '145', '155', '156',
            '166', '171', '175', '176', '185', '186', '196'
        }
        
        # 中国电信
        china_telecom_prefixes = {
            '133', '149', '153', '173', '174', '177',
            '180', '181', '189', '191', '193', '199'
        }
        
        if prefix in china_mobile_prefixes:
            return '中国移动'
        elif prefix in china_unicom_prefixes:
            return '中国联通'
        elif prefix in china_telecom_prefixes:
            return '中国电信'
        else:
            return '未知运营商'