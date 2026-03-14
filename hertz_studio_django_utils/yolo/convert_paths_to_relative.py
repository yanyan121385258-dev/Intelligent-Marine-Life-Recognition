"""
将数据库中的绝对路径转换为相对路径的脚本
执行方式: python convert_paths_to_relative.py
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hertz_server_django.settings')
django.setup()

from django.conf import settings
from hertz_studio_django_yolo.models import YoloModel, Dataset


def convert_to_relative_path(absolute_path):
    """将绝对路径转换为相对于MEDIA_ROOT的相对路径"""
    if not absolute_path:
        return None
    
    # 如果已经是相对路径,直接返回
    if not os.path.isabs(absolute_path):
        return absolute_path
    
    try:
        # 计算相对路径
        relative_path = os.path.relpath(absolute_path, settings.MEDIA_ROOT)
        return relative_path
    except ValueError:
        # 如果路径不在MEDIA_ROOT下,返回原路径
        print(f"警告: 路径 {absolute_path} 不在 MEDIA_ROOT 下")
        return absolute_path


def convert_yolo_models():
    """转换YoloModel中的路径"""
    print("开始转换 YoloModel 表中的路径...")
    
    models = YoloModel.objects.all()
    updated_count = 0
    
    for model in models:
        updated = False
        
        # 转换 model_folder_path
        if model.model_folder_path and os.path.isabs(model.model_folder_path):
            old_path = model.model_folder_path
            model.model_folder_path = convert_to_relative_path(old_path)
            print(f"  模型 {model.name}: model_folder_path")
            print(f"    原路径: {old_path}")
            print(f"    新路径: {model.model_folder_path}")
            updated = True
        
        # 转换 best_model_path
        if model.best_model_path and os.path.isabs(model.best_model_path):
            old_path = model.best_model_path
            model.best_model_path = convert_to_relative_path(old_path)
            print(f"  模型 {model.name}: best_model_path")
            print(f"    原路径: {old_path}")
            print(f"    新路径: {model.best_model_path}")
            updated = True
        
        # 转换 last_model_path
        if model.last_model_path and os.path.isabs(model.last_model_path):
            old_path = model.last_model_path
            model.last_model_path = convert_to_relative_path(old_path)
            print(f"  模型 {model.name}: last_model_path")
            print(f"    原路径: {old_path}")
            print(f"    新路径: {model.last_model_path}")
            updated = True
        
        if updated:
            model.save()
            updated_count += 1
    
    print(f"YoloModel 转换完成! 更新了 {updated_count} 个模型记录\n")


def convert_datasets():
    """转换Dataset中的路径"""
    print("开始转换 Dataset 表中的路径...")
    
    datasets = Dataset.objects.all()
    updated_count = 0
    
    for dataset in datasets:
        updated = False
        
        # 转换 root_folder_path
        if dataset.root_folder_path and os.path.isabs(dataset.root_folder_path):
            old_path = dataset.root_folder_path
            dataset.root_folder_path = convert_to_relative_path(old_path)
            print(f"  数据集 {dataset.name}: root_folder_path")
            print(f"    原路径: {old_path}")
            print(f"    新路径: {dataset.root_folder_path}")
            updated = True
        
        # 转换 data_yaml_path
        if dataset.data_yaml_path and os.path.isabs(dataset.data_yaml_path):
            old_path = dataset.data_yaml_path
            dataset.data_yaml_path = convert_to_relative_path(old_path)
            print(f"  数据集 {dataset.name}: data_yaml_path")
            print(f"    原路径: {old_path}")
            print(f"    新路径: {dataset.data_yaml_path}")
            updated = True
        
        if updated:
            dataset.save()
            updated_count += 1
    
    print(f"Dataset 转换完成! 更新了 {updated_count} 个数据集记录\n")


def main():
    print("=" * 80)
    print("路径转换工具 - 将绝对路径转换为相对路径")
    print("=" * 80)
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}\n")
    
    # 确认执行
    confirm = input("是否开始转换? (输入 yes 确认): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    try:
        # 转换YoloModel
        convert_yolo_models()
        
        # 转换Dataset
        convert_datasets()
        
        print("=" * 80)
        print("所有路径转换完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
