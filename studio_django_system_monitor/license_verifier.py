import platform
import uuid
import hashlib
import requests


# 常量配置
ACTIVATE_URL = "http://hzwike.hzsystems.cn:9999/wikesystem/common/getActivationCode"
PACKAGE_NAME = "studio_django_system_monitor"


def get_machine_id() -> str:
    """生成机器码。

    根据当前系统信息（平台、架构、MAC地址）生成唯一机器码，
    使用 SHA256 取前16位并转大写，前缀为 HERTZ_STUDIO_。
    """
    system_info = f"{platform.platform()}-{platform.machine()}-{uuid.getnode()}"
    return 'HERTZ_STUDIO_' + hashlib.sha256(system_info.encode()).hexdigest()[:16].upper()


def request_verify_machine_code(package_name: str, machine_code: str):
    """请求后端校验机器码。

    向授权服务器提交包名和机器码，返回 JSON 响应；
    如果网络异常，返回 None。
    """
    try:
        url = f"{ACTIVATE_URL}?machine_code={machine_code}"
        resp = requests.get(url, timeout=10)
        return resp.json()
    except requests.RequestException as e:
        print(f"机器码验证请求失败: {e}")
        return None


def verify_machine_license() -> None:
    """运行时验证授权。

    在 Django 应用启动时执行授权验证：生成机器码并请求校验；
    校验失败则抛出 RuntimeError 阻止应用启动。
    """
    machine_id = get_machine_id()
    resp = request_verify_machine_code(PACKAGE_NAME, machine_id)
    if resp and resp.get("ok") is True and resp.get("code") == 0:
        return

    print("=" * 60)
    print("机器码验证失败！请联系作者获取运行权限。")
    print("=" * 60)
    print("Hertz system_monitor license verification failed")