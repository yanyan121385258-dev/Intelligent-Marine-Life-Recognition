#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量移除项目中的  前缀脚本
使用方法: python remove_prefix.py
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple

class HertzPrefixRemover:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.changes_log = []
        self.errors_log = []
        
        # 需要排除的目录
        self.exclude_dirs = {
            '.git', '.idea', 'node_modules', '__pycache__', 
            'venv', '.venv', 'build', 'dist', '.trae',
            'migrations', '.npm-cache'
        }
        
        # 需要处理的文件扩展名
        self.include_extensions = {
            '.py', '.js', '.ts', '.vue', '.json', '.md',
            '.bat', '.sh', '.txt', '.yml', '.yaml', '.mako',
            '.scss', '.css', '.html'
        }
    
    def should_process_file(self, file_path: Path) -> bool:
        """判断是否应该处理该文件"""
        # 检查是否在排除目录中
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False
        
        # 检查文件扩展名
        if file_path.suffix.lower() in self.include_extensions:
            return True
        
        # 检查文件名是否包含 
        if '' in file_path.name.lower():
            return True
        
        return False
    
    def should_process_dir(self, dir_path: Path) -> bool:
        """判断是否应该处理该目录"""
        # 检查是否在排除目录中
        for part in dir_path.parts:
            if part in self.exclude_dirs:
                return False
        return True
    
    def replace_in_file(self, file_path: Path) -> Tuple[int, List[str]]:
        """替换文件内容中的 """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # 替换规则
            replacements = [
                # 文件夹名称
                ('server_django_ui', 'server_django_ui'),
                ('server_django', 'server_django'),
                ('studio_django_utils', 'studio_django_utils'),
                ('demo', 'demo'),
                
                # Python 模块名称
                ('studio_django_auth', 'studio_django_auth'),
                ('studio_django_captcha', 'studio_django_captcha'),
                ('studio_django_notice', 'studio_django_notice'),
                ('studio_django_log', 'studio_django_log'),
                ('studio_django_wiki', 'studio_django_wiki'),
                ('studio_django_system_monitor', 'studio_django_system_monitor'),
                ('studio_django_ai', 'studio_django_ai'),
                ('studio_django_codegen', 'studio_django_codegen'),
                ('studio_django_sklearn', 'studio_django_sklearn'),
                ('studio_django_yolo', 'studio_django_yolo'),
                ('studio_django_yolo_train', 'studio_django_yolo_train'),
                ('studio_django_kb', 'studio_django_kb'),
                
                # 前端文件名
                ('modules', 'modules'),
                ('request', 'request'),
                ('utils', 'utils'),
                ('permission', 'permission'),
                ('user', 'user'),
                ('theme', 'theme'),
                ('app', 'app'),
                ('types', 'types'),
                ('captcha', 'captcha'),
                ('env', 'env'),
                ('error_handler', 'error_handler'),
                ('router_utils', 'router_utils'),
                ('url', 'url'),
                ('frontend', 'frontend'),
                
                # API 路径
                ('/', '/'),
                ('studio', 'studio'),
                
                # 其他通用替换
                ('', ''),
            ]
            
            changes = []
            for old, new in replacements:
                if old in content:
                    count = content.count(old)
                    content = content.replace(old, new)
                    changes.append(f"  替换 '{old}' -> '{new}' ({count} 次)")
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return len(changes), changes
            
            return 0, []
            
        except Exception as e:
            self.errors_log.append(f"处理文件 {file_path} 时出错: {str(e)}")
            return 0, []
    
    def rename_file(self, file_path: Path) -> bool:
        """重命名文件"""
        if '' not in file_path.name:
            return False
        
        new_name = file_path.name.replace('', '')
        new_path = file_path.parent / new_name
        
        try:
            file_path.rename(new_path)
            self.changes_log.append(f"重命名文件: {file_path} -> {new_path}")
            return True
        except Exception as e:
            self.errors_log.append(f"重命名文件 {file_path} 失败: {str(e)}")
            return False
    
    def rename_dir(self, dir_path: Path) -> bool:
        """重命名目录"""
        if '' not in dir_path.name:
            return False
        
        new_name = dir_path.name.replace('', '')
        new_path = dir_path.parent / new_name
        
        try:
            dir_path.rename(new_path)
            self.changes_log.append(f"重命名目录: {dir_path} -> {new_path}")
            return True
        except Exception as e:
            self.errors_log.append(f"重命名目录 {dir_path} 失败: {str(e)}")
            return False
    
    def process_files(self):
        """处理所有文件"""
        print("=" * 80)
        print("开始处理文件内容...")
        print("=" * 80)
        
        file_count = 0
        change_count = 0
        
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                count, changes = self.replace_in_file(file_path)
                if count > 0:
                    file_count += 1
                    change_count += count
                    print(f"\n处理文件: {file_path.relative_to(self.root_dir)}")
                    for change in changes:
                        print(change)
        
        print(f"\n共处理 {file_count} 个文件，进行了 {change_count} 处替换")
    
    def process_filenames(self):
        """处理文件名"""
        print("\n" + "=" * 80)
        print("开始重命名文件...")
        print("=" * 80)
        
        renamed_count = 0
        
        # 先处理文件，再处理目录（从深到浅）
        files_to_rename = []
        dirs_to_rename = []
        
        for file_path in self.root_dir.rglob('*'):
            if '' in file_path.name:
                if file_path.is_file():
                    files_to_rename.append(file_path)
                elif file_path.is_dir() and self.should_process_dir(file_path):
                    dirs_to_rename.append(file_path)
        
        # 重命名文件
        for file_path in files_to_rename:
            if self.rename_file(file_path):
                renamed_count += 1
        
        # 重命名目录（从深到浅）
        dirs_to_rename.sort(key=lambda x: len(x.parts), reverse=True)
        for dir_path in dirs_to_rename:
            if dir_path.exists():  # 可能已经被重命名
                if self.rename_dir(dir_path):
                    renamed_count += 1
        
        print(f"\n共重命名 {renamed_count} 个文件/目录")
    
    def save_log(self):
        """保存日志"""
        log_file = self.root_dir / 'remove_prefix.log'
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("移除  前缀操作日志\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("变更记录:\n")
            f.write("-" * 80 + "\n")
            for change in self.changes_log:
                f.write(f"{change}\n")
            
            if self.errors_log:
                f.write("\n错误记录:\n")
                f.write("-" * 80 + "\n")
                for error in self.errors_log:
                    f.write(f"{error}\n")
        
        print(f"\n日志已保存到: {log_file}")
    
    def run(self):
        """执行完整的移除流程"""
        print("开始移除  前缀...")
        print(f"项目根目录: {self.root_dir}")
        print()
        
        # 1. 处理文件内容
        self.process_files()
        
        # 2. 处理文件名和目录名
        self.process_filenames()
        
        # 3. 保存日志
        self.save_log()
        
        print("\n" + "=" * 80)
        print("操作完成！")
        print("=" * 80)
        print("\n注意事项:")
        print("1. 请检查项目是否可以正常运行")
        print("2. 可能需要手动修复一些导入路径")
        print("3. 建议运行测试确保功能正常")
        print("4. 查看日志文件了解详细变更")


if __name__ == '__main__':
    # 获取项目根目录
    current_dir = Path(__file__).parent
    
    # 创建移除器实例
    remover = HertzPrefixRemover(str(current_dir))
    
    # 执行移除操作
    remover.run()
