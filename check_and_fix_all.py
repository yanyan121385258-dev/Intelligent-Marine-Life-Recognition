import os
import re

def check_file_structure(file_path):
    """检查文件是否有正确的template/script/style结构"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    template_count = content.count('<template>')
    script_count = content.count('<script setup')
    style_count = content.count('<style')
    
    template_end_count = content.count('</template>')
    script_end_count = content.count('</script>')
    style_end_count = content.count('</style>')
    
    has_issues = False
    
    if template_count != 1 or template_end_count != 1:
        has_issues = True
        print(f"  ❌ template标签异常: 开始={template_count}, 结束={template_end_count}")
    
    if script_count != 1:
        has_issues = True
        print(f"  ❌ script标签异常: {script_count}")
    
    if style_count < 1:
        has_issues = True
        print(f"  ❌ style标签异常: {style_count}")
    
    # 检查标签顺序
    template_pos = content.find('<template>')
    script_pos = content.find('<script setup')
    style_pos = content.find('<style')
    
    if template_pos == -1 or script_pos == -1:
        has_issues = True
    else:
        if not (template_pos < script_pos):
            has_issues = True
            print(f"  ❌ 标签顺序错误: template应该在script之前")
    
    if style_pos != -1 and script_pos != -1:
        if not (script_pos < style_pos):
            has_issues = True
            print(f"  ❌ 标签顺序错误: script应该在style之前")
    
    return has_issues

def find_affected_files(directory):
    """查找所有受影响的Vue文件"""
    affected_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.vue'):
                file_path = os.path.join(root, file)
                print(f"\n检查: {file_path}")
                if check_file_structure(file_path):
                    affected_files.append(file_path)
    
    return affected_files

def main():
    print("=" * 60)
    print("检查Vue文件结构")
    print("=" * 60)
    
    admin_dir = r'd:\django\server_django_ui\src\views\admin_page'
    user_dir = r'd:\django\server_django_ui\src\views\user_pages'
    
    print(f"\n检查管理员页面: {admin_dir}")
    admin_affected = find_affected_files(admin_dir)
    
    print(f"\n检查用户页面: {user_dir}")
    user_affected = find_affected_files(user_dir)
    
    all_affected = admin_affected + user_affected
    
    print("\n" + "=" * 60)
    print(f"总共发现 {len(all_affected)} 个有问题的文件:")
    print("=" * 60)
    for f in all_affected:
        print(f"  - {f}")

if __name__ == '__main__':
    main()
