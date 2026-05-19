import re

def find_unclosed_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到template部分
    in_template = False
    template_lines = []
    
    for line_num, line in enumerate(lines, 1):
        if '<template>' in line:
            in_template = True
            continue
        if '</template>' in line:
            break
        if in_template:
            template_lines.append((line_num, line))
    
    # 解析标签
    stack = []
    
    # 匹配标签的正则表达式
    tag_pattern = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*?)(/?)>')
    
    for line_num, line in template_lines:
        # 查找所有标签
        matches = tag_pattern.finditer(line)
        for match in matches:
            is_closing = match.group(1) == '/'
            tag_name = match.group(2)
            attrs = match.group(3)
            is_self_closing = match.group(4) == '/'
            
            # 跳过自闭合标签
            if is_self_closing:
                continue
            
            # 跳过一些不需要闭合的标签（虽然HTML5中这些也需要闭合，但在Vue中都需要）
            # 这里我们处理所有标签
            if is_closing:
                # 结束标签
                if stack:
                    last_tag, last_line = stack.pop()
                    if last_tag != tag_name:
                        print(f"第{line_num}行: 结束标签 </{tag_name}> 不匹配, 期望 </{last_tag}> (来自第{last_line}行)")
                        # 把last_tag放回去，继续查找
                        stack.append((last_tag, last_line))
                else:
                    print(f"第{line_num}行: 多余的结束标签 </{tag_name}>")
            else:
                # 开始标签
                stack.append((tag_name, line_num))
    
    if stack:
        print("\n未闭合的标签:")
        for tag, line in stack:
            print(f"  <{tag}> 在第{line}行")
    else:
        print("\n所有标签都已正确闭合!")

if __name__ == '__main__':
    find_unclosed_tags(r'd:\django\server_django_ui\src\views\user_pages\index.vue')
