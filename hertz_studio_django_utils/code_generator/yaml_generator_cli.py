#!/usr/bin/env python
"""
YAML Django代码生成器命令行工具

该脚本提供命令行接口，用于从YAML配置文件生成Django应用代码。

使用示例:
    python yaml_generator_cli.py generate app_config.yaml
    python yaml_generator_cli.py template --output my_app.yaml
    python yaml_generator_cli.py validate app_config.yaml
"""

import argparse
import sys
import os
from pathlib import Path
from django_code_generator import DjangoCodeGenerator


def generate_from_yaml(yaml_file_path: str, output_dir: str = None) -> bool:
    """
    从YAML文件生成Django应用代码
    
    Args:
        yaml_file_path: YAML配置文件路径
        output_dir: 输出目录（可选）
        
    Returns:
        bool: 生成是否成功
    """
    try:
        generator = DjangoCodeGenerator()
        
        # 解析YAML配置
        config = generator.yaml_parser.parse_yaml_file(yaml_file_path)
        
        # 如果指定了输出目录，覆盖配置中的设置
        if output_dir:
            config['output_dir'] = output_dir
        
        print(f"正在从 {yaml_file_path} 生成Django应用代码...")
        print(f"应用名称: {config['app_name']}")
        print(f"输出目录: {config['output_dir']}")
        print(f"模型数量: {len(config['models'])}")
        
        # 生成代码
        generated_files = generator.generate_from_yaml_config(config)
        
        print(f"\n✅ 成功生成 {len(generated_files)} 个文件:")
        for file_path in sorted(generated_files.keys()):
            print(f"  📄 {file_path}")
        
        print(f"\n🎉 Django应用 '{config['app_name']}' 生成完成!")
        print(f"📁 输出目录: {os.path.abspath(config['output_dir'])}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False


def generate_template(output_path: str = 'app_template.yaml') -> bool:
    """
    生成YAML配置文件模板
    
    Args:
        output_path: 输出文件路径
        
    Returns:
        bool: 生成是否成功
    """
    try:
        generator = DjangoCodeGenerator()
        template_content = generator.generate_yaml_template(output_path)
        
        print(f"✅ YAML配置模板已生成: {os.path.abspath(output_path)}")
        print("\n📝 模板内容预览:")
        print("-" * 50)
        # 显示前20行
        lines = template_content.split('\n')
        for i, line in enumerate(lines[:20]):
            print(f"{i+1:2d}: {line}")
        if len(lines) > 20:
            print(f"... (还有 {len(lines) - 20} 行)")
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 模板生成失败: {e}")
        return False


def validate_yaml(yaml_file_path: str) -> bool:
    """
    验证YAML配置文件
    
    Args:
        yaml_file_path: YAML配置文件路径
        
    Returns:
        bool: 验证是否通过
    """
    try:
        generator = DjangoCodeGenerator()
        config = generator.yaml_parser.parse_yaml_file(yaml_file_path)
        
        print(f"✅ YAML配置文件验证通过: {yaml_file_path}")
        print(f"📋 配置摘要:")
        print(f"  应用名称: {config['app_name']}")
        print(f"  版本: {config.get('version', 'N/A')}")
        print(f"  描述: {config.get('description', 'N/A')}")
        print(f"  作者: {config.get('author', 'N/A')}")
        print(f"  输出目录: {config['output_dir']}")
        print(f"  模型数量: {len(config['models'])}")
        
        print(f"\n📊 模型详情:")
        for i, model in enumerate(config['models'], 1):
            print(f"  {i}. {model['name']} ({len(model['fields'])} 个字段)")
            operations = model.get('operations', [])
            if operations:
                print(f"     操作: {', '.join(operations)}")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML配置验证失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='YAML Django代码生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s generate app_config.yaml                    # 从YAML生成代码
  %(prog)s generate app_config.yaml -o ./my_app       # 指定输出目录
  %(prog)s template                                    # 生成默认模板
  %(prog)s template -o my_template.yaml               # 生成自定义模板
  %(prog)s validate app_config.yaml                   # 验证YAML配置
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # generate 子命令
    generate_parser = subparsers.add_parser('generate', help='从YAML文件生成Django应用代码')
    generate_parser.add_argument('yaml_file', help='YAML配置文件路径')
    generate_parser.add_argument('-o', '--output', help='输出目录')
    
    # template 子命令
    template_parser = subparsers.add_parser('template', help='生成YAML配置文件模板')
    template_parser.add_argument('-o', '--output', default='app_template.yaml', help='输出文件路径')
    
    # validate 子命令
    validate_parser = subparsers.add_parser('validate', help='验证YAML配置文件')
    validate_parser.add_argument('yaml_file', help='YAML配置文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    success = False
    
    if args.command == 'generate':
        success = generate_from_yaml(args.yaml_file, args.output)
    elif args.command == 'template':
        success = generate_template(args.output)
    elif args.command == 'validate':
        success = validate_yaml(args.yaml_file)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())