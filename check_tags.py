import re

def check_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取template部分
    template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
    if not template_match:
        print("未找到template标签")
        return
    
    template_content = template_match.group(1)
    
    # 查找所有标签
    open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9-]*)(?:\s|>|/>)', template_content)
    close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9-]*)>', template_content)
    self_closing_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9-]*)\s[^>]*?/>', template_content)
    
    print(f"开始标签数量: {len(open_tags)}")
    print(f"结束标签数量: {len(close_tags)}")
    print(f"自闭合标签数量: {len(self_closing_tags)}")
    print()
    
    # 统计标签出现次数
    from collections import Counter
    open_counter = Counter(open_tags)
    close_counter = Counter(close_tags)
    self_closing_counter = Counter(self_closing_tags)
    
    print("标签统计:")
    all_tags = set(open_counter.keys()).union(set(close_counter.keys()))
    
    for tag in sorted(all_tags):
        open_count = open_counter.get(tag, 0)
        close_count = close_counter.get(tag, 0)
        self_closing_count = self_closing_counter.get(tag, 0)
        diff = open_count - close_count
        if diff != 0:
            print(f"  {tag}: 开始={open_count}, 结束={close_count}, 差异={diff}, 自闭合={self_closing_count}")
    
    print()
    
    # 逐行检查
    lines = template_content.split('\n')
    stack = []
    
    for i, line in enumerate(lines, 1):
        # 查找开始标签
        open_matches = re.finditer(r'<([a-zA-Z][a-zA-Z0-9-]*)(?:\s|>)', line)
        for match in open_matches:
            tag = match.group(1)
            # 检查是否是自闭合标签
            if '/>' not in line[match.start():]:
                stack.append((tag, i))
        
        # 查找结束标签
        close_matches = re.finditer(r'</([a-zA-Z][a-zA-Z0-9-]*)>', line)
        for match in close_matches:
            tag = match.group(1)
            if stack:
                last_tag, last_line = stack.pop()
                if last_tag != tag:
                    print(f"第{i}行: 结束标签 </{tag}> 不匹配, 期望 </{last_tag}> (来自第{last_line}行)")
            else:
                print(f"第{i}行: 多余的结束标签 </{tag}>")
    
    if stack:
        print()
        print("未闭合的标签:")
        for tag, line in stack:
            print(f"  <{tag}> 在第{line}行")

if __name__ == '__main__':
    check_tags(r'd:\hertz_django\hertz_server_django_ui\src\views\user_pages\index.vue')
