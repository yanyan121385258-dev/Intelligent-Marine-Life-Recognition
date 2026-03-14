def simple_fix(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份
    import shutil
    shutil.copy(file_path, file_path + '.bak')
    
    # 列表保存所有替换
    replacements = [
        # 修复欢迎横幅
        ('''                <div class="banner-left">
                  <div class="user-greeting">
                    <h1 class="greeting-title">
                      你好，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
                    </h1>
                    <p class="greeting-subtitle">{{ currentDate }}</p>
                  </div>
                </div>
                  </div>
                  </div>''',
         '''                <div class="banner-left">
                  <div class="user-greeting">
                    <h1 class="greeting-title">
                      你好，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
                    </h1>
                    <p class="greeting-subtitle">{{ currentDate }}</p>
                  </div>
                </div>
              </div>
            </div>'''),
        
        # 修复天气查询模块
        ('''                  </div>
                </div>
                </a-col>''',
         '''                  </div>
                </a-col>'''),
        
        # 修复新闻资讯模块
        ('''                  </div>
                </div>
                </a-col>''',
         '''                  </div>
                </a-col>'''),
        
        # 修复翻译功能模块
        ('''                  </div>
                </div>
                </a-col>''',
         '''                  </div>
                </a-col>'''),
        
        # 修复地图模块
        ('''                  </div>
                </div>
                </a-col>''',
         '''                  </div>
                </a-col>'''),
        
        # 修复OCR模块
        ('''                  </div>
                </div>
                </a-col>''',
         '''                  </div>
                </a-col>'''),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # 写入
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("简单修复完成！")

if __name__ == '__main__':
    simple_fix(r'd:\hertz_django\hertz_server_django_ui\src\views\user