import re

def fix_template_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到template和script之间的部分
    template_start = content.find('<template>')
    script_start = content.find('<script setup')
    
    if template_start == -1 or script_start == -1:
        print("未找到template或script标签")
        return
    
    template_content = content[template_start:script_start]
    
    # 修复欢迎横幅部分
    # 找到第102-115行的问题并修复
    fixed_template = template_content
    
    # 修复欢迎横幅的结束标签
    # 原问题：第114-115行有多余的</div>
    welcome_banner_fix = '''            <!-- 欢迎横幅 -->
            <div class="welcome-banner">
              <div class="banner-content">
                <div class="banner-left">
                  <div class="user-greeting">
                    <h1 class="greeting-title">
                      你好，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
                    </h1>
                    <p class="greeting-subtitle">{{ currentDate }}</p>
                  </div>
                </div>
              </div>
            </div>'''
    
    # 替换有问题的欢迎横幅部分
    old_welcome_banner = '''            <!-- 欢迎横幅 -->
            <div class="welcome-banner">
              <div class="banner-content">
                <div class="banner-left">
                  <div class="user-greeting">
                    <h1 class="greeting-title">
                      你好，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
                    </h1>
                    <p class="greeting-subtitle">{{ currentDate }}</p>
                  </div>
                </div>
                  </div>
                  </div>'''
    
    fixed_template = fixed_template.replace(old_welcome_banner, welcome_banner_fix)
    
    # 现在修复统计卡片部分的缩进和结束标签
    # 修复第136-148行的统计卡片
    stats_card_fix = '''                  <div class="modern-stat-card" :class="`layout-${currentDashboardLayout}`">
                    <div class="stat-icon-wrapper" :class="stat.color">
                      <component :is="stat.icon" class="stat-icon" />
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">
                        {{ stat.value }}
                        <span v-if="stat.trend" :class="['stat-trend', stat.trend]">{{ stat.trend === 'up' ? '↑' : '↓' }}</span>
                        <span v-if="stat.badge" class="stat-badge">{{ stat.badge }}</span>
                      </div>
                      <div class="stat-label">{{ stat.label }}</div>
                    </div>
                  </div>'''
    
    old_stats_card = '''                  <div class="modern-stat-card" :class="`layout-${currentDashboardLayout}`">
                    <div class="stat-icon-wrapper" :class="stat.color">
                      <component :is="stat.icon" class="stat-icon" />
                  </div>
                    <div class="stat-info">
                      <div class="stat-value">
                        {{ stat.value }}
                        <span v-if="stat.trend" :class="['stat-trend', stat.trend]">{{ stat.trend === 'up' ? '↑' : '↓' }}</span>
                        <span v-if="stat.badge" class="stat-badge">{{ stat.badge }}</span>
                </div>
                      <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>'''
    
    fixed_template = fixed_template.replace(old_stats_card, stats_card_fix)
    
    # 修复统计容器结束标签
    old_stats_container_end = '''                </div>'''
    new_stats_container_end = '''              </div>'''
    # 需要更精确地匹配
    stats_container_end_pattern = re.compile(r'\s+</div>\s+</div>\s+<!-- 快速访问 -->', re.DOTALL)
    fixed_template = re.sub(stats_container_end_pattern, '''              </div>
            </div>
            
            <!-- 快速访问 -->''', fixed_template)
    
    # 修复快速访问卡片部分
    quick_access_card_fix = '''                      <div class="quick-access-card" @click="handleMenuClick({ key: item.key })">
                        <div class="card-icon" :class="item.color">
                          <component :is="item.icon" />
                        </div>
                        <h3 class="card-title">{{ item.title }}</h3>
                        <p class="card-description">{{ item.description }}</p>
                      </div>'''
    
    old_quick_access_card = '''                      <div class="quick-access-card" @click="handleMenuClick({ key: item.key })">
                        <div class="card-icon" :class="item.color">
                          <component :is="item.icon" />
                  </div>
                        <h3 class="card-title">{{ item.title }}</h3>
                        <p class="card-description">{{ item.description }}</p>
                  </div>'''
    
    fixed_template = fixed_template.replace(old_quick_access_card, quick_access_card_fix)
    
    # 修复列表布局结束标签
    old_list_layout_end = '''                </div>'''
    new_list_layout_end = '''                  </div>'''
    
    # 修复最近活动部分
    recent_activities_fix = '''                  <div class="activity-list">
                    <div class="activity-item">
                      <div class="activity-icon blue">
                        <ScanOutlined />
                      </div>
                      <div class="activity-content">
                        <div class="activity-title">完成YOLO检测</div>
                        <div class="activity-time">2分钟前</div>
                      </div>
                    </div>
                    <div class="activity-item">
                      <div class="activity-icon green">
                        <MessageOutlined />
                      </div>
                      <div class="activity-content">
                        <div class="activity-title">AI助手对话</div>
                        <div class="activity-time">15分钟前</div>
                      </div>
                    </div>
                    <div class="activity-item">
                      <div class="activity-icon purple">
                        <FileTextOutlined />
                      </div>
                      <div class="activity-content">
                        <div class="activity-title">查看知识文档</div>
                        <div class="activity-time">1小时前</div>
                      </div>
                    </div>
                    <div class="activity-item">
                      <div class="activity-icon orange">
                        <BellOutlined />
                      </div>
                      <div class="activity-content">
                        <div class="activity-title">收到新通知</div>
                        <div class="activity-time">2小时前</div>
                      </div>
                    </div>
                  </div>'''
    
    old_recent_activities = '''                  <div class="activity-list">
                    <div class="activity-item">
                      <div class="activity-icon blue">
                    <ScanOutlined />
                  </div>
                      <div class="activity-content">
                        <div class="activity-title">完成YOLO检测</div>
                        <div class="activity-time">2分钟前</div>
                  </div>
                </div>
                    <div class="activity-item">
                      <div class="activity-icon green">
                        <MessageOutlined />
                  </div>
                      <div class="activity-content">
                        <div class="activity-title">AI助手对话</div>
                        <div class="activity-time">15分钟前</div>
                  </div>
                </div>
                    <div class="activity-item">
                      <div class="activity-icon purple">
                    <FileTextOutlined />
                  </div>
                      <div class="activity-content">
                        <div class="activity-title">查看知识文档</div>
                        <div class="activity-time">1小时前</div>
                  </div>
                </div>
                    <div class="activity-item">
                      <div class="activity-icon orange">
                    <BellOutlined />
                  </div>
                      <div class="activity-content">
                        <div class="activity-title">收到新通知</div>
                        <div class="activity-time">2小时前</div>
                  </div>
                </div>
              </div>'''
    
    fixed_template = fixed_template.replace(old_recent_activities, recent_activities_fix)
    
    # 修复最近活动结束标签
    old_overview_end = '''            </div>
              </a-col>
            </a-row>
            </div>
        </div>'''
    
    new_overview_end = '''            </div>
              </a-col>
            </a-row>
          </div>
        </div>'''
    
    fixed_template = fixed_template.replace(old_overview_end, new_overview_end)
    
    # 修复主题预设部分
    preset_theme_fix = '''          <div v-show="showPresetThemes" class="preset-themes">
            <div 
              v-for="preset in presetThemes" 
              :key="preset.name"
              class="preset-theme-card"
              :class="{ active: currentPreset === preset.name }"
              @click="applyPresetTheme(preset)"
            >
              <div class="preset-preview" :style="{ background: preset.previewBg }">
                <div class="preview-header" :style="{ background: preset.headerBg, color: preset.headerText }"></div>
                <div class="preview-content">
                  <div class="preview-card" :style="{ background: preset.cardBg, borderColor: preset.cardBorder }"></div>
                </div>
              </div>
              <div class="preset-name">{{ preset.label }}</div>
            </div>
          </div>'''
    
    old_preset_theme = '''          <div v-show="showPresetThemes" class="preset-themes">
            <div 
              v-for="preset in presetThemes" 
              :key="preset.name"
              class="preset-theme-card"
              :class="{ active: currentPreset === preset.name }"
              @click="applyPresetTheme(preset)"
            >
              <div class="preset-preview" :style="{ background: preset.previewBg }">
                <div class="preview-header" :style="{ background: preset.headerBg, color: preset.headerText }"></div>
                <div class="preview-content">
                  <div class="preview-card" :style="{ background: preset.cardBg, borderColor: preset.cardBorder }"></div>
                    </div>
                  </div>
            <div class="preset-name">{{ preset.label }}</div>
                </div>
                  </div>'''
    
    fixed_template = fixed_template.replace(old_preset_theme, preset_theme_fix)
    
    # 合并回完整内容
    new_content = fixed_template + content[script_start:]
    
    # 备份原文件
    import shutil
    shutil.copy(file_path, file_path + '.bak')
    
    # 写入修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("标签修复完成！原文件已备份为 .bak")

if __name__ == '__main__':
    fix_template_tags(r'd:\hertz_django\hertz_server_django_ui\src\views\user_pages\index.vue')
