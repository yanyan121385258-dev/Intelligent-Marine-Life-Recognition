#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量修改虚拟环境中包的 apps.py 文件中的 name 属性
"""

import os
from pathlib import Path

# 虚拟环境 site-packages 目录
site_packages = Path(r"d:\hertz_django\venv\Lib\site-packages")

# 需要修改的包列表
packages = [
    "studio_django_ai",
    "studio_django_auth",
    "studio_django_captcha",
    "studio_django_kb",
    "studio_django_log",
    "studio_django_notice",
    "studio_django_system_monitor",
    "studio_django_wiki",
    "studio_django_yolo",
    "studio_django_yolo_train",
]

# 替换规则
replacements = [
    ("name = 'hertz_studio_django_ai'", "name = 'studio_django_ai'"),
    ("name = 'hertz_studio_django_auth'", "name = 'studio_django_auth'"),
    ("name = 'hertz_studio_django_captcha'", "name = 'studio_django_captcha'"),
    ("name = 'hertz_studio_django_kb'", "name = 'studio_django_kb'"),
    ("name = 'hertz_studio_django_log'", "name = 'studio_django_log'"),
    ("name = 'hertz_studio_django_notice'", "name = 'studio_django_notice'"),
    ("name = 'hertz_studio_django_system_monitor'", "name = 'studio_django_system_monitor'"),
    ("name = 'hertz_studio_django_wiki'", "name = 'studio_django_wiki'"),
    ("name = 'hertz_studio_django_yolo'", "name = 'studio_django_yolo'"),
    ("name = 'hertz_studio_django_yolo_train'", "name = 'studio_django_yolo_train'"),
]

def modify_apps_py(package_name):
    """修改包的 apps.py 文件"""
    apps_file = site_packages / package_name / "apps.py"
    
    if not apps_file.exists():
        print(f"[WARNING] {package_name}/apps.py 不存在")
        return False
    
    try:
        with open(apps_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"  [OK] 替换: {old} -> {new}")
        
        if content != original_content:
            with open(apps_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[SUCCESS] 已修改 {package_name}/apps.py")
            return True
        else:
            print(f"[INFO] {package_name}/apps.py 无需修改")
            return False
            
    except Exception as e:
        print(f"[ERROR] 修改 {package_name}/apps.py 失败: {str(e)}")
        return False

def main():
    print("=" * 80)
    print("开始修改虚拟环境中包的 apps.py 文件")
    print("=" * 80)
    
    modified_count = 0
    
    for package in packages:
        print(f"\n处理: {package}")
        if modify_apps_py(package):
            modified_count += 1
    
    print("\n" + "=" * 80)
    print(f"完成！共修改了 {modified_count} 个文件")
    print("=" * 80)

if __name__ == '__main__':
    main()
