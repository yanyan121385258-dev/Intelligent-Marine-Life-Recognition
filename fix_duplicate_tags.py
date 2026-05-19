import re

def fix_duplicate_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    import shutil
    shutil.copy(file_path, file_path + '.bak2')
    
    # 模式1: 修复欢迎横幅
    old1 = '''                </div>
                  </div>
                  </div>'''
    new1 = '''                </div>
              </div>
            </div>'''
    content = content.replace(old1, new1)
    
    # 模式2: 修复功能模块后的重复结束标签 (天气查询)
    old2 = '''                  </div>
                </div>
                </a-col>'''
    new2 = '''                  </div>
                </a-col>'''
    
    # 需要小心地替换，避免影响其他地方
    # 让我们逐个修复每个模块
    
    # 1. 修复欢迎横幅结束标签
    welcome_pattern = re.compile(
        r'(<div class="welcome-banner">.*?</div>\s*?</div>\s*?</div>)\s*?</div>\s*?</div>',
        re.DOTALL
    )
    
    # 2. 修复天气查询模块
    weather_old = '''                  </div>
                </div>
                </a-col>'''
    weather_new = '''                  </div>
                </a-col>'''
    
    # 让我们用一个更安全的方法 - 直接读取内容，逐行处理
    lines = content.split('\n')
    new_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        
        # 检查是否是重复的结束标签模式
        current_line = line.rstrip()
        
        # 检测模式: 一行是 </div>, 下一行也是 </div>, 再下一行是 </a-col>
        if (i + 2 < len(lines) and 
            current_line.strip() == '</div>' and 
            lines[i+1].strip() == '</div>' and 
            lines[i+2].strip() == '</a-col>'):
            # 只保留 </div> 和 </a-col>
            new_lines.append(line)
            new_lines.append(lines[i+2])
            skip_next = True  # 跳过中间的 </div>
            continue
        
        # 检测另一种模式: 一行是 </div>, 下一行是 </a-col>, 再下一行也是 </a-col>
        if (i + 2 < len(lines) and 
            current_line.strip() == '</div>' and 
            lines[i+1].strip() == '</a-col>' and 
            lines[i+2].strip() == '</a-col>'):
            new_lines.append(line)
            new_lines.append(lines[i+1])
            skip_next = True  # 跳过重复的 </a-col>
            continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # 现在修复欢迎横幅部分的具体问题
    old_welcome = '''                <div class="banner-left">
                  <div class="user-greeting">
                    <h1 class="greeting-title">
                      你好，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
                    </h1>
                    <p class="greeting-subtitle">{{ currentDate }}</p>
                  </div>
                </div>
                  </div>
                  </div>'''
    
    new_welcome = '''                <div class="banner-left">
                  <div class="user-greeting">
                    <h1 class="greeting-title">
                      你好，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
                    </h1>
                    <p class="greeting-subtitle">{{ currentDate }}</p>
                  </div>
                </div>
              </div>
            </div>'''
    
    content = content.replace(old_welcome, new_welcome)
    
    # 写入修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("标签修复完成！原文件已备份为 .bak2")

if __name__ == '__main__':
    fix_duplicate_tags(r'd:\django\server_django_ui\src\views\user_pages\index.vue')
