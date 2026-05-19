import re

file_path = r'd:\django\server_django_ui\src\views\user_pages\index.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 template 部分
template_match = re.search(r'<template>([\s\S]*?)</template>', content)
if template_match:
    template_content = template_match.group(1)
    
    open_tags = []
    tag_pattern = re.compile(r'<(/?)([\w-]+)([^>]*)>')
    
    lines = template_content.split('\n')
    print('逐行检查标签:\n')
    
    for line_num, line in enumerate(lines, 1):
        matches = tag_pattern.findall(line)
        for match in matches:
            is_close, tag_name, attrs = match
            if tag_name and not tag_name.startswith('!') and not tag_name.startswith('?'):
                if is_close == '/':
                    # 关闭标签
                    if open_tags and open_tags[-1] == tag_name:
                        closed_tag = open_tags.pop()
                        print(f'✓ 第 {line_num} 行: 关闭 </{closed_tag}>')
                    elif open_tags:
                        print(f'⚠️ 第 {line_num} 行: 尝试关闭 </{tag_name}>，但当前打开的是 <{open_tags[-1]}>')
                    else:
                        print(f'⚠️ 第 {line_num} 行: 关闭 </{tag_name}>，但没有打开的标签')
                else:
                    # 开启标签，检查是否是自闭合
                    is_self_closing = attrs.endswith('/') or tag_name in ['br', 'hr', 'img', 'input', 'meta', 'link']
                    if not is_self_closing:
                        open_tags.append(tag_name)
                        print(f'○ 第 {line_num} 行: 打开 <{tag_name}>')
    
    print(f'\n未闭合的标签: {open_tags}')
else:
    print('未找到 template 标签')
