import re

file_path = r'd:\hertz_django\hertz_server_django_ui\src\views\user_pages\index.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 template 标签
template_match = re.search(r'<template>([\s\S]*?)</template>', content)
if template_match:
    template_content = template_match.group(1)
    print('✓ 找到 template 标签')
    
    # 简单检查标签平衡
    open_tags = []
    tag_pattern = re.compile(r'<(/?)([\w-]+)([^>]*)>')
    
    lines = template_content.split('\n')
    for i, line in enumerate(lines, 1):
        matches = tag_pattern.findall(line)
        for match in matches:
            is_close, tag_name, attrs = match
            if tag_name and not tag_name.startswith('!') and not tag_name.startswith('?'):
                if is_close == '/':
                    # 关闭标签
                    if open_tags and open_tags[-1] == tag_name:
                        open_tags.pop()
                else:
                    # 开启标签，检查是否是自闭合
                    if not attrs.endswith('/'):
                        open_tags.append(tag_name)
    
    if open_tags:
        print(f'⚠️ 未闭合的标签: {open_tags}')
    else:
        print('✓ 所有标签都已闭合')
else:
    print('❌ 未找到 template 标签')

print('\n检查完成！')
