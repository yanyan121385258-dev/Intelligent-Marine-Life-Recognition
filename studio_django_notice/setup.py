from setuptools import setup, find_packages
import sys
import platform
import uuid
import hashlib
import urllib.request
import json

ACTIVATE_URL = "http://hzwike.hzsystems.cn:9999/wikesystem/common/getActivationCode"

def get_machine_id() -> str:
    system_info = f"{platform.platform()}-{platform.machine()}-{uuid.getnode()}"
    return 'HERTZ_STUDIO_' + hashlib.sha256(system_info.encode()).hexdigest()[:16].upper()

def verify_install_permission():
    bypass_commands = ['sdist', 'clean', '--help', '-h', '--version', 'egg_info']
    if len(sys.argv) > 1:
        for cmd in sys.argv[1:]:
            if cmd in bypass_commands:
                return

    print("正在验证安装授权...")
    machine_id = get_machine_id()
    print(f"当前机器码: {machine_id}")
    
    try:
        url = f"{ACTIVATE_URL}?machine_code={machine_id}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("ok") is True and data.get("code") == 0:
                print("授权验证成功，继续安装...")
                return
    except Exception as e:
        print(f"验证请求失败 (可能是网络问题): {e}")
        pass
    
    print("\n" + "=" * 60)
    print(f"安装失败！机器码 {machine_id} 未激活。")
    print("请联系作者获取授权，并提供上述机器码。")
    print("=" * 60 + "\n")
    sys.exit(1)

verify_install_permission()

try:
    with open("../README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

def read_requirements():
    with open("../requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="studio_django_notice",
    version="1.0.0",
    author="yang kunhao",
    author_email="563161210@qq.com",
    description="通知管理模块",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_dir={'': '..'},
    package_data={
        'studio_django_notice': [
            'migrations/*.py',
            'serializers/*.py',
            'views/*.py',
        ],
    },
    include_package_data=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    license="MIT",
    python_requires=">=3.10",
    install_requires=read_requirements(),
)
