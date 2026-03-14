import re
from typing import Tuple, List


class PasswordValidator:
    """
    密码验证器
    提供密码强度验证功能
    """

    """
    生产环境
    """
    # @staticmethod
    # def validate_password_strength(password: str, min_length: int = 8, max_length: int = 128) -> Tuple[bool, List[str]]:
    #     """
    #     验证密码强度
    #
    #     Args:
    #         password: 密码
    #         min_length: 最小长度
    #         max_length: 最大长度
    #
    #     Returns:
    #         Tuple[bool, List[str]]: (是否通过验证, 错误信息列表)
    #     """
    #     errors = []
    #
    #     if not password:
    #         errors.append("密码不能为空")
    #         return False, errors
    #
    #     if not isinstance(password, str):
    #         errors.append("密码必须是字符串")
    #         return False, errors
    #
    #     # 检查长度
    #     if len(password) < min_length:
    #         errors.append(f"密码长度至少{min_length}位")
    #
    #     if len(password) > max_length:
    #         errors.append(f"密码长度不能超过{max_length}位")
    #
    #     # 检查是否包含数字
    #     if not re.search(r'\d', password):
    #         errors.append("密码必须包含至少一个数字")
    #
    #     # 检查是否包含小写字母
    #     if not re.search(r'[a-z]', password):
    #         errors.append("密码必须包含至少一个小写字母")
    #
    #     # 检查是否包含大写字母
    #     if not re.search(r'[A-Z]', password):
    #         errors.append("密码必须包含至少一个大写字母")
    #
    #     return len(errors) == 0, errors




    """
    开发环境
    """
    # 默认使用下面开发环境，在生产环境中请使用上面的校验规则！
    @staticmethod
    def validate_password_strength(password: str,
                                 min_length: int = 6,
                                 max_length: int = 128) -> Tuple[bool, List[str]]:
        """
        验证密码强度（仅检查长度，不少于 6 位即可）

        Args:
            password: 密码
            min_length: 最小长度（默认 6）
            max_length: 最大长度（默认 128）

        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 错误信息列表)
        """
        errors = []

        if not password:
            errors.append("密码不能为空")
            return False, errors

        if not isinstance(password, str):
            errors.append("密码必须是字符串")
            return False, errors

        # 仅长度检查
        if len(password) < min_length:
            errors.append(f"密码长度至少{min_length}位")

        if len(password) > max_length:
            errors.append(f"密码长度不能超过{max_length}位")

        return len(errors) == 0, errors


    @staticmethod
    def validate_simple_password(password: str, min_length: int = 6, max_length: int = 128) -> Tuple[bool, str]:
        """
        简单密码验证（只检查长度和基本字符）

        Args:
            password: 密码
            min_length: 最小长度
            max_length: 最大长度

        Returns:
            Tuple[bool, str]: (是否通过验证, 错误信息)
        """
        if not password:
            return False, "密码不能为空"

        if not isinstance(password, str):
            return False, "密码必须是字符串"

        if len(password) < min_length:
            return False, f"密码长度至少{min_length}位"

        if len(password) > max_length:
            return False, f"密码长度不能超过{max_length}位"

        # 检查是否包含数字或字母
        if not re.search(r'[a-zA-Z0-9]', password):
            return False, "密码必须包含字母或数字"

        return True, "密码格式正确"

    @staticmethod
    def check_common_passwords(password: str) -> bool:
        """
        检查是否为常见弱密码

        Args:
            password: 密码

        Returns:
            bool: 是否为常见弱密码
        """
        common_passwords = {
            '123456', 'password', '123456789', '12345678', '12345',
            '1234567', '1234567890', 'qwerty', 'abc123', '111111',
            '123123123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234', 'dragon', 'pass', 'master', 'hello',
            'freedom', 'whatever', 'qazwsx', 'trustno1', 'jordan23'
        }

        return password.lower() in common_passwords

    @staticmethod
    def calculate_password_score(password: str) -> int:
        """
        计算密码强度分数（0-100）

        Args:
            password: 密码

        Returns:
            int: 密码强度分数
        """
        if not password:
            return 0

        score = 0

        # 长度分数（最多30分）
        length_score = min(len(password) * 2, 30)
        score += length_score

        # 字符类型分数
        if re.search(r'[a-z]', password):  # 小写字母
            score += 10

        if re.search(r'[A-Z]', password):  # 大写字母
            score += 10

        if re.search(r'\d', password):  # 数字
            score += 10

        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # 特殊字符
            score += 15

        # 字符多样性分数
        unique_chars = len(set(password))
        diversity_score = min(unique_chars * 2, 25)
        score += diversity_score

        # 扣分项
        if PasswordValidator.check_common_passwords(password):
            score -= 30

        # 重复字符扣分
        if re.search(r'(.)\1{2,}', password):  # 连续3个相同字符
            score -= 10

        # 连续数字或字母扣分
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            score -= 5

        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            score -= 5

        return max(0, min(100, score))

    @staticmethod
    def get_password_strength_level(password: str) -> str:
        """
        获取密码强度等级

        Args:
            password: 密码

        Returns:
            str: 密码强度等级
        """
        score = PasswordValidator.calculate_password_score(password)

        if score >= 80:
            return "很强"
        elif score >= 60:
            return "强"
        elif score >= 40:
            return "中等"
        elif score >= 20:
            return "弱"
        else:
            return "很弱"