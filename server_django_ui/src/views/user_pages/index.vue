<template>
  <a-layout class="user-layout">
    <!-- 头部 -->
    <a-layout-header class="user-header">
      <div class="header-left">
        

        <!-- 顶部水平菜单 -->
        <a-menu
          v-model:selectedKeys="selectedKeys"
          mode="horizontal"
          class="top-menu"
          @click="handleMenuClick"
          :style="{ position: 'relative', zIndex: 999999 }"
        >
          <template v-for="item in menuItems" :key="item.key">
            <a-sub-menu v-if="item.children" :key="`sub-${item.key}`">
              <template #title>
                <component :is="getIconComponent(item.icon)" />
                <span>{{ item.label }}</span>
              </template>
              <a-menu-item
                v-for="child in item.children"
                :key="child.key"
                :disabled="child.disabled"
              >
                {{ child.label }}
              </a-menu-item>
            </a-sub-menu>
            <a-menu-item v-else :key="`item-${item.key}`" :disabled="item.disabled">
              <component :is="getIconComponent(item.icon)" />
              <span>{{ item.label }}</span>
            </a-menu-item>
          </template>
        </a-menu>
      </div>

      <div class="header-right">
        <a-breadcrumb class="breadcrumb">
          <a-breadcrumb-item v-for="item in breadcrumbItems" :key="item">
            {{ item }}
          </a-breadcrumb-item>
        </a-breadcrumb>

        <!-- 布局切换按钮 -->
        <a-button
          type="text"
          shape="circle"
          class="header-item layout-btn"
          @click="openLayoutModal"
        >
          <template #icon>
            <AppstoreOutlined />
          </template>
        </a-button>

        <!-- 主题切换按钮 -->
        <a-button type="text" shape="circle" class="header-item theme-btn" @click="openThemeModal">
          <template #icon>
            <BgColorsOutlined />
          </template>
        </a-button>

        <!-- 全屏按钮 -->
        <a-button type="text" shape="circle" class="header-item fullscreen-btn" @click="toggleFullscreen">
          <template #icon>
            <FullscreenOutlined v-if="!isFullscreen" />
            <FullscreenExitOutlined v-else />
          </template>
        </a-button>

        <!-- 用户信息下拉菜单 -->
        <a-dropdown placement="bottomRight" class="header-item">
          <a-button type="text" class="user-info-btn">
            <a-avatar :src="userStore.userInfo?.avatar" :size="32">
              <template #icon>
                <UserOutlined />
              </template>
            </a-avatar>
            <span class="username">{{
              userStore.userInfo?.real_name || userStore.userInfo?.username
            }}</span>
            <DownOutlined />
          </a-button>
          <template #overlay>
            <a-menu @click="handleUserMenuClick">
              <a-menu-item key="profile">
                <UserOutlined />
                个人信息
              </a-menu-item>
              <a-menu-item key="settings">
                <SettingOutlined />
                账户设置
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout">
                <LogoutOutlined />
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </a-layout-header>

    <!-- 主要内容区域 -->
    <a-layout class="main-layout">
      <!-- 内容区域 -->
      <a-layout-content class="user-content">
        <div class="content-wrapper">
          <!-- 动态显示组件内容 -->
          <component :is="currentComponent" v-if="currentComponent" />

          <!-- 默认仪表盘内容 -->
          <div v-else class="dashboard-content">
            <!-- 欢迎横幅 -->
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
                <div class="banner-right">
                  <div class="banner-decor">
                    <component :is="getRandomDecorIcon()" class="decor-icon" />
                  </div>
                </div>
              </div>
            </div>

            <!-- 统计卡片区域 -->
            <div
              class="stats-container"
              :class="`layout-${currentDashboardLayout} ${currentLayoutConfig.statsClass}`"
            >
              <!-- 网格布局和宽屏布局：横向排列 -->
              <a-row
                v-if="currentDashboardLayout !== 'compact'"
                :gutter="[16, 16]"
                class="stats-row"
              >
                <a-col
                  v-for="(stat, index) in dashboardStats"
                  :key="index"
                  :xs="statsLayout.xs"
                  :sm="statsLayout.sm"
                  :lg="statsLayout.lg"
                  :md="statsLayout.md"
                  :xl="statsLayout.xl"
                >
                  <div class="modern-stat-card" :class="`layout-${currentDashboardLayout}`">
                    <div class="stat-icon-wrapper" :class="stat.color">
                      <component :is="stat.icon" class="stat-icon" />
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">
                        {{ stat.value }}
                        <span v-if="stat.trend" :class="['stat-trend', stat.trend]">{{
                          stat.trend === 'up' ? '↑' : '↓'
                        }}</span>
                        <span v-if="stat.badge" class="stat-badge">{{ stat.badge }}</span>
                      </div>
                      <div class="stat-label">{{ stat.label }}</div>
                    </div>
                  </div>
                </a-col>
              </a-row>

              <!-- 列表布局：垂直列表 -->
              <div v-else class="stats-vertical-list">
                <div
                  v-for="(stat, index) in dashboardStats"
                  :key="index"
                  class="modern-stat-card vertical-stat-card"
                >
                  <div class="stat-icon-wrapper" :class="stat.color">
                    <component :is="stat.icon" class="stat-icon" />
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">
                      {{ stat.value }}
                      <span v-if="stat.trend" :class="['stat-trend', stat.trend]">{{
                        stat.trend === 'up' ? '↑' : '↓'
                      }}</span>
                      <span v-if="stat.badge" class="stat-badge">{{ stat.badge }}</span>
                    </div>
                    <div class="stat-label">{{ stat.label }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 快速访问 -->
            <div
              class="quick-access-section"
              :class="`layout-${currentDashboardLayout} ${currentLayoutConfig.quickAccessClass}`"
            >
              <h2 class="section-title">快速访问</h2>

              <!-- 网格布局：4列网格 -->
              <a-row v-if="currentDashboardLayout === 'default'" :gutter="[16, 16]">
                <a-col
                  v-for="(item, index) in quickAccessItems"
                  :key="index"
                  :xs="quickAccessLayout.xs"
                  :sm="quickAccessLayout.sm"
                  :lg="quickAccessLayout.lg"
                >
                  <div class="quick-access-card" @click="handleMenuClick({ key: item.key })">
                    <div class="card-icon" :class="item.color">
                      <component :is="item.icon" />
                    </div>
                    <h3 class="card-title">{{ item.title }}</h3>
                    <p class="card-description">{{ item.description }}</p>
                  </div>
                </a-col>
              </a-row>

              <!-- 列表布局：垂直列表 -->
              <div v-else-if="currentDashboardLayout === 'compact'" class="quick-access-list">
                <div
                  v-for="(item, index) in quickAccessItems"
                  :key="index"
                  class="quick-access-list-item"
                  @click="handleMenuClick({ key: item.key })"
                >
                  <div class="card-icon" :class="item.color">
                    <component :is="item.icon" />
                  </div>
                  <div class="list-item-content">
                    <h3 class="card-title">{{ item.title }}</h3>
                    <p class="card-description">{{ item.description }}</p>
                  </div>
                </div>
              </div>

              <!-- 宽屏布局：多列网格 -->
              <a-row v-else :gutter="[16, 16]">
                <a-col
                  v-for="(item, index) in quickAccessItems"
                  :key="index"
                  :xs="quickAccessLayout.xs"
                  :sm="quickAccessLayout.sm"
                  :md="quickAccessLayout.md"
                  :lg="quickAccessLayout.lg"
                  :xl="quickAccessLayout.xl"
                >
                  <div
                    class="quick-access-card wide-card"
                    @click="handleMenuClick({ key: item.key })"
                  >
                    <div class="card-icon" :class="item.color">
                      <component :is="item.icon" />
                    </div>
                    <h3 class="card-title">{{ item.title }}</h3>
                    <p class="card-description">{{ item.description }}</p>
                  </div>
                </a-col>
              </a-row>
            </div>

            <!-- 功能模块区域 -->
            <div class="features-section">
              <h2 class="features-title">功能模块</h2>
              <a-row :gutter="[20, 20]" class="features-grid">
                <!-- 天气查询模块 -->
                <a-col :xs="24" :sm="12" :lg="8">
                  <div class="weather-section">
                    <h3 class="section-title">天气查询</h3>
                    <div class="weather-card">
                      <div class="weather-search">
                        <a-input
                          v-model:value="weatherCityName"
                          placeholder="请输入城市名称（如：北京、上海、广州）"
                          size="large"
                          class="weather-input"
                          @pressEnter="queryWeather"
                        >
                          <template #prefix>
                            <SearchOutlined />
                          </template>
                        </a-input>
                        <a-button
                          type="primary"
                          size="large"
                          class="weather-search-btn"
                          :loading="weatherLoading"
                          @click="queryWeather"
                        >
                          <template #icon>
                            <SearchOutlined />
                          </template>
                          查询天气
                        </a-button>
                      </div>

                      <div v-if="weatherData" class="weather-display">
                        <div class="weather-header">
                          <h3 class="weather-city">{{ weatherData.city }}</h3>
                          <div class="weather-icon">
                            <CloudOutlined
                              v-if="
                                weatherData.weather?.includes('云') ||
                                weatherData.weather?.includes('阴')
                              "
                            />
                            <span v-else class="sun-emoji">☀️</span>
                          </div>
                        </div>
                        <div class="weather-info">
                          <div class="weather-item">
                            <span class="weather-label">当前温度：</span>
                            <span class="weather-value temperature">{{
                              weatherData.temperature
                            }}</span>
                          </div>
                          <div class="weather-item">
                            <span class="weather-label">湿度：</span>
                            <span class="weather-value">{{ weatherData.humidity }}</span>
                          </div>
                          <div class="weather-item">
                            <span class="weather-label">风力：</span>
                            <span class="weather-value">{{ weatherData.wind }}</span>
                          </div>
                          <div v-if="weatherData.weather" class="weather-item">
                            <span class="weather-label">天气：</span>
                            <span class="weather-value">{{ weatherData.weather }}</span>
                          </div>
                        </div>
                      </div>

                      <div v-else-if="!weatherLoading" class="weather-empty">
                        <CloudOutlined class="empty-icon" />
                        <p class="empty-text">请输入城市名称查询天气</p>
                      </div>
                    </div>
                  </div>
                </a-col>

                <!-- 新闻资讯模块 -->
                <a-col :xs="24" :sm="12" :lg="8">
                  <div class="news-section">
                    <h3 class="section-title">新闻资讯</h3>
                    <div class="news-card">
                      <div v-if="newsLoading" class="news-loading">
                        <a-spin size="large" />
                        <p class="loading-text">正在加载新闻...</p>
                      </div>
                      <div v-else-if="newsList.length > 0" class="news-list">
                        <div
                          v-for="(news, index) in newsList"
                          :key="index"
                          class="news-item"
                          @click="openNewsLink(news.link)"
                        >
                          <div class="news-number">{{ index + 1 }}</div>
                          <div class="news-content">
                            <div class="news-title">{{ news.title }}</div>
                            <div class="news-date">{{ news.date }}</div>
                          </div>
                          <div class="news-arrow">
                            <RightOutlined />
                          </div>
                        </div>
                      </div>
                      <div v-else class="news-empty">
                        <FileTextOutlined class="empty-icon" />
                        <p class="empty-text">暂无新闻数据</p>
                      </div>
                    </div>
                  </div>
                </a-col>

                <!-- 翻译功能模块 -->
                <a-col :xs="24" :sm="12" :lg="8">
                  <div class="translation-section">
                    <h3 class="section-title">翻译功能</h3>
                    <div class="translation-card">
                      <div class="translation-controls">
                        <a-radio-group
                          v-model:value="translationType"
                          class="translation-type-selector"
                          :disabled="translationLoading"
                        >
                          <a-radio-button value="ZH2EN">中译英</a-radio-button>
                          <a-radio-button value="EN2ZH">英译汉</a-radio-button>
                          <a-radio-button value="AUTO">自动识别</a-radio-button>
                        </a-radio-group>
                      </div>
                      <div class="translation-input-area">
                        <a-textarea
                          v-model:value="translationInput"
                          :placeholder="
                            translationType === 'ZH2EN'
                              ? '请输入中文文本'
                              : translationType === 'EN2ZH'
                                ? '请输入英文文本'
                                : '请输入要翻译的文本（支持中文、英文等）'
                          "
                          :rows="4"
                          class="translation-textarea"
                          :disabled="translationLoading"
                          @pressEnter="handleTranslation"
                        />
                        <a-button
                          type="primary"
                          size="large"
                          class="translation-btn"
                          :loading="translationLoading"
                          @click="handleTranslation"
                        >
                          <template #icon>
                            <TranslationOutlined />
                          </template>
                          翻译
                        </a-button>
                      </div>

                      <div v-if="translationResult" class="translation-result">
                        <div class="result-label">翻译结果：</div>
                        <div class="result-content">{{ translationResult }}</div>
                      </div>

                      <div v-if="translationError" class="translation-error">
                        <ExclamationCircleOutlined class="error-icon" />
                        <span class="error-text">{{ translationError }}</span>
                      </div>
                    </div>
                  </div>
                </a-col>

                <!-- 地图模块 -->
                <a-col :xs="24" :sm="12" :lg="12">
                  <div class="map-section">
                    <h3 class="section-title">地图</h3>
                    <div class="map-card">
                      <div class="map-header">
                        <div class="map-search-box">
                          <a-input
                            v-model:value="mapSearchQuery"
                            placeholder="输入地址或地点名称搜索"
                            class="map-search-input"
                            :disabled="mapSearching"
                            @pressEnter="searchLocation"
                          >
                            <template #prefix>
                              <SearchOutlined />
                            </template>
                          </a-input>
                          <a-button
                            type="primary"
                            size="small"
                            class="map-search-btn"
                            :loading="mapSearching"
                            @click="searchLocation"
                          >
                            搜索
                          </a-button>
                        </div>
                        <a-button
                          type="primary"
                          size="small"
                          class="map-locate-btn"
                          :loading="mapLocating"
                          @click="locateToCurrentPosition"
                        >
                          <template #icon>
                            <EnvironmentOutlined />
                          </template>
                          定位到我
                        </a-button>
                      </div>
                      <div id="tencent-map-container" class="tencent-map-container"></div>
                    </div>
                  </div>
                </a-col>

                <!-- OCR 文字识别模块 -->
                <a-col :xs="24" :sm="12" :lg="12">
                  <div class="ocr-section">
                    <h3 class="section-title">OCR 文字识别</h3>
                    <div class="ocr-card">
                      <div class="ocr-upload-area">
                        <div
                          class="ocr-upload-drag-area"
                          :class="{ 'drag-over': isDragOver, processing: ocrProcessing }"
                          @click="triggerFileInput"
                          @dragover.prevent="handleDragOver"
                          @dragleave.prevent="handleDragLeave"
                          @drop.prevent="handleDrop"
                        >
                          <input
                            ref="fileInputRef"
                            type="file"
                            accept="image/*"
                            style="display: none"
                            @change="handleFileInputChange"
                            :disabled="ocrProcessing"
                          />
                          <div class="ocr-upload-content">
                            <FileImageOutlined class="upload-icon" />
                            <p class="upload-text">
                              {{ ocrProcessing ? '正在识别...' : '点击或拖拽图片到此处上传' }}
                            </p>
                            <p class="upload-hint">支持 JPG、PNG 等图片格式</p>
                          </div>
                        </div>
                        <p class="ocr-hint">建议图片大小不超过 5MB</p>
                      </div>

                      <div v-if="ocrImagePreview" class="ocr-preview">
                        <div class="ocr-preview-title">预览图片：</div>
                        <img :src="ocrImagePreview" alt="预览图片" class="ocr-preview-image" />
                      </div>

                      <!-- 识别进度显示 -->
                      <div v-if="ocrProcessing" class="ocr-progress">
                        <div class="ocr-progress-header">
                          <span class="progress-title">正在识别中...</span>
                          <span class="progress-percent">{{ ocrProgress }}%</span>
                        </div>
                        <a-progress
                          :percent="ocrProgress"
                          :status="ocrProcessing ? 'active' : 'success'"
                          :stroke-color="{
                            '0%': '#3b82f6',
                            '100%': '#2563eb',
                          }"
                          class="ocr-progress-bar"
                        />
                        <div v-if="ocrProgressText" class="progress-text">
                          {{ ocrProgressText }}
                        </div>
                      </div>

                      <div v-if="ocrResult" class="ocr-result">
                        <div class="ocr-result-title">识别结果：</div>
                        <div class="ocr-result-content">{{ ocrResult }}</div>
                        <a-button
                          type="text"
                          size="small"
                          class="ocr-copy-btn"
                          @click="copyOcrResult"
                        >
                          复制结果
                        </a-button>
                      </div>

                      <div v-if="ocrError" class="ocr-error">
                        <ExclamationCircleOutlined class="error-icon" />
                        <span class="error-text">{{ ocrError }}</span>
                      </div>
                    </div>
                  </div>
                </a-col>

                <!-- 语音识别模块 -->
                <a-col :xs="24" :sm="12" :lg="12">
                  <div class="speech-recognition-section">
                    <h3 class="section-title">语音识别</h3>
                    <div class="speech-recognition-card">
                      <div v-if="!isSpeechSupported" class="speech-not-supported">
                        <AudioOutlined class="not-supported-icon" />
                        <p class="not-supported-text">您的浏览器不支持语音识别功能</p>
                        <p class="not-supported-hint">请使用 Chrome、Edge 或 Safari 浏览器</p>
                      </div>
                      <div v-else class="speech-recognition-content">
                        <div class="speech-controls">
                          <a-button
                            :type="isListening ? 'danger' : 'primary'"
                            :icon="isListening ? h(StopOutlined) : h(AudioOutlined)"
                            size="large"
                            class="speech-btn"
                            :loading="isInitializing"
                            @click="toggleSpeechRecognition"
                          >
                            {{ isListening ? '停止识别' : '开始识别' }}
                          </a-button>
                          <a-button
                            v-if="recognitionText"
                            type="default"
                            size="large"
                            class="clear-btn"
                            @click="clearRecognitionText"
                          >
                            <template #icon>
                              <ClearOutlined />
                            </template>
                            清空
                          </a-button>
                        </div>
                        <div class="speech-status">
                          <div v-if="isListening" class="listening-indicator">
                            <div class="pulse-dot"></div>
                            <span class="status-text">正在识别中...</span>
                          </div>
                          <div v-else-if="recognitionText" class="status-text idle">识别已停止</div>
                          <div v-else class="status-text idle">点击按钮开始语音识别</div>
                        </div>
                        <div class="speech-result">
                          <div class="result-label">识别结果：</div>
                          <div
                            class="result-text"
                            :class="{ empty: !recognitionText && !interimText }"
                          >
                            <template v-if="recognitionText || interimText">
                              <span v-if="recognitionText" class="final-text">{{
                                recognitionText
                              }}</span>
                              <span v-if="interimText" class="interim-text">{{ interimText }}</span>
                            </template>
                            <span v-else class="empty-text">暂无识别结果</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </a-col>

                <!-- 语音合成模块 -->
                <a-col :xs="24" :sm="12" :lg="12">
                  <div class="speech-synthesis-section">
                    <h3 class="section-title">语音合成</h3>
                    <div class="speech-synthesis-card">
                      <div v-if="!isSynthesisSupported" class="speech-not-supported">
                        <AudioOutlined class="not-supported-icon" />
                        <p class="not-supported-text">您的浏览器不支持语音合成功能</p>
                        <p class="not-supported-hint">请使用 Chrome、Edge 或 Safari 浏览器</p>
                      </div>
                      <div v-else class="speech-synthesis-content">
                        <div class="synthesis-input">
                          <a-textarea
                            v-model:value="synthesisText"
                            placeholder="请输入要朗读的文字..."
                            :rows="4"
                            class="synthesis-textarea"
                            :disabled="isSpeaking"
                          />
                        </div>
                        <div class="synthesis-settings">
                          <div class="setting-item">
                            <div class="setting-label">
                              <span>语速</span>
                              <span class="setting-value">{{ speechRate.toFixed(1) }}</span>
                            </div>
                            <a-slider
                              v-model:value="speechRate"
                              :min="0.5"
                              :max="2.0"
                              :step="0.1"
                              :disabled="isSpeaking"
                              class="setting-slider"
                            />
                          </div>
                          <div class="setting-item">
                            <div class="setting-label">
                              <span>音调</span>
                              <span class="setting-value">{{ speechPitch.toFixed(1) }}</span>
                            </div>
                            <a-slider
                              v-model:value="speechPitch"
                              :min="0.5"
                              :max="2.0"
                              :step="0.1"
                              :disabled="isSpeaking"
                              class="setting-slider"
                            />
                          </div>
                          <div class="setting-item">
                            <div class="setting-label">
                              <span>音量</span>
                              <span class="setting-value"
                                >{{ Math.round(speechVolume * 100) }}%</span
                              >
                            </div>
                            <a-slider
                              v-model:value="speechVolume"
                              :min="0"
                              :max="1"
                              :step="0.1"
                              :disabled="isSpeaking"
                              class="setting-slider"
                            />
                          </div>
                        </div>
                        <div class="synthesis-controls">
                          <a-button
                            :type="isSpeaking ? 'danger' : 'primary'"
                            :icon="isSpeaking ? h(StopOutlined) : h(PlayCircleOutlined)"
                            size="large"
                            class="synthesis-btn"
                            :disabled="!synthesisText.trim()"
                            @click="toggleSpeechSynthesis"
                          >
                            {{ isSpeaking ? '停止播放' : '播放语音' }}
                          </a-button>
                          <a-button
                            v-if="synthesisText"
                            type="default"
                            size="large"
                            class="clear-btn"
                            :disabled="isSpeaking"
                            @click="clearSynthesisText"
                          >
                            <template #icon>
                              <ClearOutlined />
                            </template>
                            清空
                          </a-button>
                        </div>
                        <div class="synthesis-status">
                          <div v-if="isSpeaking" class="speaking-indicator">
                            <div class="pulse-dot"></div>
                            <span class="status-text">正在播放中...</span>
                          </div>
                          <div v-else-if="synthesisText" class="status-text idle">已停止播放</div>
                          <div v-else class="status-text idle">输入文字后点击播放按钮</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </a-col>
              </a-row>
            </div>

            <!-- 数据概览和最近活动 -->
            <a-row
              :gutter="[20, 20]"
              class="overview-section"
              :class="`layout-${currentDashboardLayout}`"
            >
              <a-col
                :xs="contentLayout.side.xs"
                :lg="contentLayout.side.lg"
                :order="contentLayout.side.order"
              >
                <!-- 最近活动 -->
                <div class="recent-activities">
                  <h2 class="section-title">最近活动</h2>
                  <div class="activity-list">
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
                  </div>
                </div>
              </a-col>
            </a-row>
          </div>
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>

  <!-- 主题选择器抽屉 -->
  <a-drawer
    v-model:visible="showThemeModal"
    title="主题设置"
    placement="right"
    :width="400"
    :closable="true"
    :mask-closable="true"
  >
    <div class="theme-editor">
      <!-- 预设主题 -->
      <div class="theme-section">
        <h3 class="section-title">
          预设风格
          <a-button type="link" size="small" @click="showPresetThemes = !showPresetThemes">
            <CaretUpOutlined v-if="showPresetThemes" />
            <CaretDownOutlined v-else />
          </a-button>
        </h3>
        <div v-show="showPresetThemes" class="preset-themes">
          <div
            v-for="preset in presetThemes"
            :key="preset.name"
            class="preset-theme-card"
            :class="{ active: currentPreset === preset.name }"
            @click="applyPresetTheme(preset)"
          >
            <div class="preset-preview" :style="{ background: preset.previewBg }">
              <div
                class="preview-header"
                :style="{ background: preset.headerBg, color: preset.headerText }"
              ></div>
              <div class="preview-content">
                <div
                  class="preview-card"
                  :style="{ background: preset.cardBg, borderColor: preset.cardBorder }"
                ></div>
              </div>
            </div>
            <div class="preset-name">{{ preset.label }}</div>
          </div>
        </div>
      </div>

      <!-- 自定义设置 -->
      <div class="theme-section">
        <h3 class="section-title">
          自定义
          <a-button type="link" size="small" @click="showCustomEditor = !showCustomEditor">
            <CaretUpOutlined v-if="showCustomEditor" />
            <CaretDownOutlined v-else />
          </a-button>
        </h3>

        <div v-show="showCustomEditor" class="custom-editor">
          <a-tabs>
            <a-tab-pane key="header" tab="导航栏">
              <div class="color-group">
                <div class="color-item">
                  <label>背景色</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.headerBg"
                      @input="
                        (e) => {
                          themeConfig.headerBg = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.headerBg"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#ffffff"
                    />
                  </div>
                </div>
                <div class="color-item">
                  <label>文字颜色</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.headerText"
                      @input="
                        (e) => {
                          themeConfig.headerText = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.headerText"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#111827"
                    />
                  </div>
                </div>
                <div class="color-item">
                  <label>边框颜色</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.headerBorder"
                      @input="
                        (e) => {
                          themeConfig.headerBorder = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.headerBorder"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#e5e7eb"
                    />
                  </div>
                </div>
              </div>
            </a-tab-pane>

            <a-tab-pane key="background" tab="背景">
              <div class="color-group">
                <div class="color-item">
                  <label>页面背景</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.pageBg"
                      @input="
                        (e) => {
                          themeConfig.pageBg = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.pageBg"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#ffffff"
                    />
                  </div>
                </div>
                <div class="color-item">
                  <label>内容背景</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.contentBg"
                      @input="
                        (e) => {
                          themeConfig.contentBg = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.contentBg"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#ffffff"
                    />
                  </div>
                </div>
              </div>
            </a-tab-pane>

            <a-tab-pane key="component" tab="组件">
              <div class="color-group">
                <div class="color-item">
                  <label>卡片背景</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.cardBg"
                      @input="
                        (e) => {
                          themeConfig.cardBg = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.cardBg"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#ffffff"
                    />
                  </div>
                </div>
                <div class="color-item">
                  <label>卡片边框</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.cardBorder"
                      @input="
                        (e) => {
                          themeConfig.cardBorder = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.cardBorder"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#e5e7eb"
                    />
                  </div>
                </div>
              </div>
            </a-tab-pane>

            <a-tab-pane key="color" tab="颜色">
              <div class="color-group">
                <div class="color-item">
                  <label>主题色</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.primaryColor"
                      @input="
                        (e) => {
                          themeConfig.primaryColor = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.primaryColor"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#2563eb"
                    />
                  </div>
                </div>
                <div class="color-item">
                  <label>主要文字</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.textPrimary"
                      @input="
                        (e) => {
                          themeConfig.textPrimary = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.textPrimary"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#111827"
                    />
                  </div>
                </div>
                <div class="color-item">
                  <label>次要文字</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      :value="themeConfig.textSecondary"
                      @input="
                        (e) => {
                          themeConfig.textSecondary = (e.target as HTMLInputElement).value;
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-input"
                    />
                    <a-input
                      v-model:value="themeConfig.textSecondary"
                      @change="
                        () => {
                          currentPreset = 'custom';
                          themeStore.updateTheme(themeConfig);
                        }
                      "
                      class="color-text-input"
                      placeholder="#6b7280"
                    />
                  </div>
                </div>
              </div>
            </a-tab-pane>
          </a-tabs>
        </div>
      </div>

      <div class="theme-actions">
        <a-button @click="resetTheme">重置默认</a-button>
        <a-button type="primary" @click="saveTheme">保存</a-button>
      </div>
    </div>
  </a-drawer>

  <!-- 布局选择器抽屉 -->
  <a-drawer
    v-model:visible="showLayoutModal"
    title="布局设置"
    placement="right"
    :width="400"
    :closable="true"
    :mask-closable="true"
  >
    <div class="layout-editor">
      <!-- 布局类型选择 -->
      <div class="layout-type-selector">
        <a-select
          v-model:value="currentLayoutType"
          style="width: 100%"
          size="large"
          placeholder="请选择布局类型"
          @change="switchLayoutType"
        >
          <template #suffixIcon>
            <DownOutlined />
          </template>
          <a-select-option
            v-for="navItem in layoutNavItems"
            :key="navItem.key"
            :value="navItem.key"
            :label="navItem.label"
          >
            <div class="select-nav-item">
              <component :is="navItem.icon" v-if="navItem.icon" class="nav-icon" />
              <span>{{ navItem.label }}</span>
            </div>
          </a-select-option>
        </a-select>
      </div>

      <!-- 首页布局 -->
      <div v-if="currentLayoutType === 'dashboard'" class="layout-section">
        <h3 class="section-title">首页布局</h3>
        <div class="layout-options">
          <div
            v-for="layout in dashboardLayouts"
            :key="layout.name"
            class="layout-option-card"
            :class="{ active: currentDashboardLayout === layout.name }"
            @click="applyDashboardLayout(layout)"
          >
            <div class="layout-preview" :class="`layout-${layout.name}`">
              <div class="preview-stats" :class="layout.statsClass">
                <div class="preview-stat"></div>
                <div class="preview-stat"></div>
                <div class="preview-stat"></div>
                <div class="preview-stat"></div>
              </div>
              <div class="preview-content" :class="layout.contentClass">
                <div class="preview-main"></div>
                <div class="preview-side"></div>
              </div>
            </div>
            <div class="layout-name">{{ layout.label }}</div>
            <div class="layout-desc">{{ layout.description }}</div>
          </div>
        </div>
      </div>

      <!-- 系统监控布局 -->
      <div v-else-if="currentLayoutType === 'system-monitor'" class="layout-section">
        <h3 class="section-title">系统监控布局</h3>
        <div class="layout-options">
          <div
            v-for="layout in systemMonitorLayouts"
            :key="layout.name"
            class="layout-option-card"
            :class="{ active: currentSystemMonitorLayout === layout.name }"
            @click="applySystemMonitorLayout(layout)"
          >
            <div class="layout-preview monitor-preview" :class="`layout-${layout.name}`">
              <div class="preview-overview" :class="layout.overviewClass">
                <div class="preview-card"></div>
                <div class="preview-card"></div>
                <div class="preview-card"></div>
                <div v-if="layout.name === 'wide'" class="preview-card"></div>
              </div>
              <div class="preview-detail" :class="layout.detailClass">
                <div class="preview-main-detail"></div>
                <div v-if="layout.name !== 'compact'" class="preview-side-detail"></div>
              </div>
            </div>
            <div class="layout-name">{{ layout.label }}</div>
            <div class="layout-desc">{{ layout.description }}</div>
          </div>
        </div>
      </div>

      <!-- AI助手布局 -->
      <div v-else-if="currentLayoutType === 'ai-chat'" class="layout-section">
        <h3 class="section-title">AI助手布局</h3>
        <div class="layout-options">
          <div
            v-for="layout in aiChatLayouts"
            :key="layout.name"
            class="layout-option-card"
            :class="{ active: currentAiChatLayout === layout.name }"
            @click="applyAiChatLayout(layout)"
          >
            <div class="layout-preview chat-preview" :class="`layout-${layout.name}`">
              <template v-if="layout.name === 'default'">
                <div class="preview-chat-sidebar">
                  <div class="preview-sidebar-header"></div>
                  <div class="preview-sidebar-item"></div>
                  <div class="preview-sidebar-item"></div>
                  <div class="preview-sidebar-item"></div>
                </div>
                <div class="preview-chat-main">
                  <div class="preview-chat-header"></div>
                  <div class="preview-chat-message user-msg"></div>
                  <div class="preview-chat-message ai-msg"></div>
                  <div class="preview-chat-input"></div>
                </div>
              </template>
              <template v-else-if="layout.name === 'compact'">
                <div class="preview-chat-sidebar">
                  <div class="preview-sidebar-header"></div>
                  <div class="preview-sidebar-item"></div>
                  <div class="preview-sidebar-item"></div>
                  <div class="preview-sidebar-item"></div>
                </div>
                <div class="preview-chat-main">
                  <div class="preview-chat-header"></div>
                  <div class="preview-chat-message user-msg"></div>
                  <div class="preview-chat-message ai-msg"></div>
                  <div class="preview-chat-input"></div>
                </div>
              </template>
              <template v-else-if="layout.name === 'wide'">
                <div class="preview-chat-sidebar"></div>
                <div class="preview-chat-header"></div>
                <div class="preview-chat-message user-msg"></div>
                <div class="preview-chat-message ai-msg"></div>
                <div class="preview-chat-input"></div>
              </template>
            </div>
            <div class="layout-name">{{ layout.label }}</div>
            <div class="layout-desc">{{ layout.description }}</div>
          </div>
        </div>
      </div>

      <!-- YOLO检测布局 -->
      <div v-else-if="currentLayoutType === 'yolo-detection'" class="layout-section">
        <h3 class="section-title">YOLO检测布局</h3>
        <div class="layout-options">
          <div
            v-for="layout in yoloDetectionLayouts"
            :key="layout.name"
            class="layout-option-card"
            :class="{ active: currentYoloDetectionLayout === layout.name }"
            @click="applyYoloDetectionLayout(layout)"
          >
            <div class="layout-preview yolo-preview" :class="`layout-${layout.name}`">
              <template v-if="layout.name === 'classic'">
                <div class="preview-upload-left"></div>
                <div class="preview-result-right"></div>
              </template>
              <template v-else-if="layout.name === 'vertical'">
                <div class="preview-upload-top"></div>
                <div class="preview-result-bottom"></div>
              </template>
              <template v-else-if="layout.name === 'grid'">
                <div class="preview-sidebar-left"></div>
                <div class="preview-sidebar-right"></div>
              </template>
            </div>
            <div class="layout-name">{{ layout.label }}</div>
            <div class="layout-desc">{{ layout.description }}</div>
          </div>
        </div>
      </div>

      <!-- 检测历史布局 -->
      <div v-else-if="currentLayoutType === 'detection-history'" class="layout-section">
        <h3 class="section-title">检测历史布局</h3>
        <div class="layout-options">
          <div
            v-for="layout in detectionHistoryLayouts"
            :key="layout.name"
            class="layout-option-card"
            :class="{ active: currentDetectionHistoryLayout === layout.name }"
            @click="applyDetectionHistoryLayout(layout)"
          >
            <div class="layout-preview history-preview" :class="`layout-${layout.name}`">
              <template v-if="layout.name === 'default'">
                <div class="preview-card-item"></div>
                <div class="preview-card-item"></div>
                <div class="preview-card-item"></div>
                <div class="preview-card-item"></div>
              </template>
              <template v-else-if="layout.name === 'list'">
                <div class="preview-list-item"></div>
                <div class="preview-list-item"></div>
                <div class="preview-list-item"></div>
              </template>
              <template v-else-if="layout.name === 'flow'">
                <div class="preview-flow-item"></div>
                <div class="preview-flow-item"></div>
                <div class="preview-flow-item"></div>
                <div class="preview-flow-item"></div>
                <div class="preview-flow-item"></div>
              </template>
            </div>
            <div class="layout-name">{{ layout.label }}</div>
            <div class="layout-desc">{{ layout.description }}</div>
          </div>
        </div>
      </div>

      <!-- 告警中心布局 -->
      <div v-else-if="currentLayoutType === 'alert-center'" class="layout-section">
        <h3 class="section-title">告警中心布局</h3>
        <div class="layout-options">
          <div
            v-for="layout in alertCenterLayouts"
            :key="layout.name"
            class="layout-option-card"
            :class="{ active: currentAlertCenterLayout === layout.name }"
            @click="applyAlertCenterLayout(layout)"
          >
            <div class="layout-preview alert-preview" :class="`layout-${layout.name}`">
              <template v-if="layout.name === 'table'">
                <div class="preview-table-header"></div>
                <div class="preview-table-row"></div>
                <div class="preview-table-row"></div>
                <div class="preview-table-row"></div>
              </template>
              <template v-else-if="layout.name === 'card'">
                <div class="preview-card-item"></div>
                <div class="preview-card-item"></div>
                <div class="preview-card-item"></div>
              </template>
              <template v-else-if="layout.name === 'timeline'">
                <div class="preview-timeline-item"></div>
                <div class="preview-timeline-item"></div>
                <div class="preview-timeline-item"></div>
              </template>
            </div>
            <div class="layout-name">{{ layout.label }}</div>
            <div class="layout-desc">{{ layout.description }}</div>
          </div>
        </div>
      </div>

      <div class="layout-actions">
        <a-button @click="resetLayout">重置默认</a-button>
        <a-button type="primary" @click="saveLayout">保存</a-button>
      </div>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import {
  ref,
  computed,
  onMounted,
  watch,
  h,
  onUnmounted,
  onActivated,
  nextTick,
} from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import {
  DashboardOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  DownOutlined,
  BellOutlined,
  AppstoreOutlined,
  FileTextOutlined,
  MessageOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  ScanOutlined,
  HistoryOutlined,
  ExclamationCircleOutlined,
  BgColorsOutlined,
  CaretUpOutlined,
  CaretDownOutlined,
  AudioOutlined,
  StopOutlined,
  ClearOutlined,
  PlayCircleOutlined,
  SearchOutlined,
  CloudOutlined,
  RightOutlined,
  EnvironmentOutlined,
  TranslationOutlined,
  FileImageOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
} from '@ant-design/icons-vue';
import {
  getMenuBreadcrumb,
  userComponentMap,
  getFilteredUserMenuItems,
} from '@/router/user_menu_ai';
import { User } from '@/api/user';
import { logoutUser } from '@/api/auth';
import { useUserStore } from '@/stores/user';
import { useThemeStore, ThemeConfig } from '@/stores/theme';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const themeStore = useThemeStore();

// 响应式数据
const selectedKeys = ref<string[]>(['dashboard']);
const currentComponent = ref<any>(null);
const showThemeModal = ref(false);
const showLayoutModal = ref(false);
const showPresetThemes = ref(true);
const showCustomEditor = ref(false);
const themeConfig = ref<ThemeConfig>({ ...themeStore.theme });
const currentPreset = ref<string>('default');
const currentDashboardLayout = ref<string>('default');
const currentSystemMonitorLayout = ref<string>('default');
const currentAiChatLayout = ref<string>('default');
const currentYoloDetectionLayout = ref<string>('classic');
const currentDetectionHistoryLayout = ref<string>('default');
const currentAlertCenterLayout = ref<string>('table');

// 全屏相关状态
const isFullscreen = ref(false);

// 当前显示的布局类型（根据当前页面自动确定）
const currentLayoutType = ref<
  | 'dashboard'
  | 'system-monitor'
  | 'ai-chat'
  | 'detection-history'
  | 'yolo-detection'
  | 'alert-center'
>('dashboard');

// 语音识别相关状态
const isSpeechSupported = ref(false);
const isListening = ref(false);
const isInitializing = ref(false);
const recognitionText = ref('');
const interimText = ref('');
let recognition: any = null;

// 语音合成相关状态
const isSynthesisSupported = ref(false);
const isSpeaking = ref(false);
const synthesisText = ref('');
const speechRate = ref(1.0); // 语速（0.1-10）
const speechPitch = ref(1.0); // 音调（0-2）
const speechVolume = ref(1.0); // 音量（0-1）
let synthesis: SpeechSynthesis | null = null;
let currentUtterance: SpeechSynthesisUtterance | null = null;
let voicesLoaded = ref(false);

// 天气查询相关状态
const weatherCityName = ref('');
const weatherLoading = ref(false);
const weatherData = ref<{
  city: string;
  temperature: string;
  humidity: string;
  wind: string;
  weather?: string;
} | null>(null);
const isAutoDetecting = ref(false); // 是否正在自动检测位置

// 新闻资讯相关状态
const newsLoading = ref(false);
const newsList = ref<
  Array<{
    title: string;
    link: string;
    date: string;
  }>
>([]);

// 翻译功能相关状态
const translationInput = ref('');
const translationLoading = ref(false);
const translationResult = ref('');
const translationError = ref('');
const translationType = ref<'ZH2EN' | 'EN2ZH' | 'AUTO'>('ZH2EN'); // 翻译类型：中译英、英译汉、自动识别（默认中文→英文）

// 地图相关状态
const mapLocating = ref(false);
const mapSearching = ref(false);
const mapSearchQuery = ref('');
let mapInstance: any = null; // Leaflet 地图实例
let markers: any[] = []; // 所有标记点数组

// OCR 文字识别相关状态
const ocrProcessing = ref(false);
const ocrProgress = ref(0); // OCR 识别进度（0-100）
const ocrProgressText = ref(''); // 进度文本描述
const ocrImagePreview = ref('');
const ocrResult = ref('');
const ocrError = ref('');
const isDragOver = ref(false); // 是否正在拖拽
const fileInputRef = ref<HTMLInputElement | null>(null); // 文件输入框引用

// 城市名称到stationid的映射（中国气象局站点ID）
const cityStationIdMap: Record<string, string> = {
  北京: '54511',
  上海: '58367',
  广州: '59287',
  深圳: '59493',
  杭州: '58457',
  南京: '58238',
  成都: '56294',
  武汉: '57494',
  西安: '57036',
  重庆: '57516',
  天津: '54527',
  苏州: '58356',
  长沙: '57687',
  郑州: '57083',
  济南: '54823',
  青岛: '54857',
  大连: '54662',
  厦门: '59134',
  福州: '58847',
  昆明: '56778',
  贵阳: '57816',
  南宁: '59431',
  海口: '59758',
  石家庄: '53698',
  太原: '53772',
  呼和浩特: '53463',
  沈阳: '54342',
  长春: '54161',
  哈尔滨: '50953',
  合肥: '58321',
  南昌: '58606',
  银川: '53614',
  西宁: '52866',
  乌鲁木齐: '51463',
  拉萨: '55591',
};

// 英文城市名到中文城市名的映射
const englishToChineseCityMap: Record<string, string> = {
  Beijing: '北京',
  Shanghai: '上海',
  Guangzhou: '广州',
  Shenzhen: '深圳',
  Hangzhou: '杭州',
  Nanjing: '南京',
  Chengdu: '成都',
  Wuhan: '武汉',
  Xian: '西安',
  "Xi'an": '西安',
  Chongqing: '重庆',
  Tianjin: '天津',
  Suzhou: '苏州',
  Changsha: '长沙',
  Zhengzhou: '郑州',
  Jinan: '济南',
  Qingdao: '青岛',
  Dalian: '大连',
  Xiamen: '厦门',
  Fuzhou: '福州',
  Kunming: '昆明',
  Guiyang: '贵阳',
  Nanning: '南宁',
  Haikou: '海口',
  Shijiazhuang: '石家庄',
  Taiyuan: '太原',
  Hohhot: '呼和浩特',
  Shenyang: '沈阳',
  Changchun: '长春',
  Harbin: '哈尔滨',
  Hefei: '合肥',
  Nanchang: '南昌',
  Yinchuan: '银川',
  Xining: '西宁',
  Urumqi: '乌鲁木齐',
  Lhasa: '拉萨',
};

// 布局类型导航项
const layoutNavItems = [
  {
    key: 'dashboard',
    label: '首页布局',
    icon: DashboardOutlined,
  },
  {
    key: 'alert-center',
    label: '告警中心',
    icon: BellOutlined,
  },
  {
    key: 'system-monitor',
    label: '系统监控',
    icon: DatabaseOutlined,
  },
  {
    key: 'ai-chat',
    label: 'AI助手',
    icon: MessageOutlined,
  },
  {
    key: 'yolo-detection',
    label: 'YOLO检测',
    icon: ScanOutlined,
  },
  {
    key: 'detection-history',
    label: '检测历史',
    icon: HistoryOutlined,
  },
];

// 获取当前选中项
const currentNavItem = computed(() => {
  return layoutNavItems.find((item) => item.key === currentLayoutType.value) || layoutNavItems[0];
});

// 切换布局类型
const switchLayoutType = (
  newType:
    | 'dashboard'
    | 'system-monitor'
    | 'ai-chat'
    | 'detection-history'
    | 'yolo-detection'
    | 'alert-center'
) => {
  currentLayoutType.value = newType;
};

// 首页统计数据
const dashboardStats = ref([
  {
    icon: AppstoreOutlined,
    color: 'blue',
    value: '12',
    trend: 'up',
    label: '活跃项目',
  },
  {
    icon: CheckCircleOutlined,
    color: 'green',
    value: '28',
    trend: 'up',
    label: '已完成任务',
  },
  {
    icon: FileTextOutlined,
    color: 'purple',
    value: '156',
    trend: 'up',
    label: '文档资料',
  },
  {
    icon: MessageOutlined,
    color: 'orange',
    value: '3',
    badge: '新',
    label: '未读消息',
  },
]);

// 快速访问项
const quickAccessItems = ref([
  {
    key: 'system-monitor',
    icon: DatabaseOutlined,
    color: 'blue',
    title: '系统监控',
    description: '实时查看系统运行状态和性能指标',
  },
  {
    key: 'ai-chat',
    icon: MessageOutlined,
    color: 'green',
    title: 'AI助手',
    description: '智能对话，快速解答问题',
  },
  {
    key: 'yolo-detection',
    icon: ScanOutlined,
    color: 'purple',
    title: 'YOLO检测',
    description: '图像目标检测与分析',
  },
  {
    key: 'knowledge-center',
    icon: FileTextOutlined,
    color: 'orange',
    title: '知识库中心',
    description: '浏览技术文档和资料库',
  },
  {
    key: 'notice-center',
    icon: BellOutlined,
    color: 'pink',
    title: '通知中心',
    description: '查看系统通知和消息提醒',
  },
  {
    key: 'detection-history',
    icon: HistoryOutlined,
    color: 'cyan',
    title: '检测历史',
    description: '查看历史检测记录和结果',
  },
  {
    key: 'alert-center',
    icon: ExclamationCircleOutlined,
    color: 'red',
    title: '告警中心',
    description: '管理告警信息和处理状态',
  },
  {
    key: 'profile',
    icon: UserOutlined,
    color: 'indigo',
    title: '个人信息',
    description: '查看和编辑个人资料设置',
  },
]);

// 布局配置
const dashboardLayouts = [
  {
    name: 'default',
    label: '网格布局',
    description: '统计卡片横向4列，快速访问网格显示，内容左右分栏',
    statsClass: 'stats-4col',
    contentClass: 'content-split',
    quickAccessClass: 'grid-4col',
    statsLayout: { xs: 24, sm: 12, md: 8, lg: 6 },
    quickAccessLayout: { xs: 24, sm: 12, lg: 6 },
    contentLayout: {
      main: { xs: 24, lg: 16, order: 1 },
      side: { xs: 24, lg: 8, order: 2 },
    },
  },
  {
    name: 'compact',
    label: '列表布局',
    description: '统计卡片垂直列表，快速访问列表显示，适合小屏',
    statsClass: 'stats-vertical',
    contentClass: 'content-stack',
    quickAccessClass: 'list-style',
    statsLayout: { xs: 24, sm: 24, lg: 24 },
    quickAccessLayout: { xs: 24, sm: 24, lg: 24 },
    contentLayout: {
      main: { xs: 24, lg: 24, order: 1 },
      side: { xs: 24, lg: 24, order: 2 },
    },
  },
  {
    name: 'wide',
    label: '宽屏布局',
    description: '统计卡片大卡片，快速访问6列网格，充分利用宽屏空间',
    statsClass: 'stats-wide',
    contentClass: 'content-wide',
    quickAccessClass: 'grid-6col',
    statsLayout: { xs: 24, sm: 12, lg: 6, xl: 6 },
    quickAccessLayout: { xs: 24, sm: 12, md: 8, lg: 6, xl: 4 },
    contentLayout: {
      main: { xs: 24, lg: 20, order: 1 },
      side: { xs: 24, lg: 4, order: 2 },
    },
  },
];

// 系统监控布局配置
const systemMonitorLayouts = [
  {
    name: 'default',
    label: '标准布局',
    description: '概览卡片3列，详细信息2列，标准展示',
    overviewClass: 'overview-3col',
    detailClass: 'detail-2col',
    overviewLayout: { xs: 24, md: 12, lg: 8 },
    detailLayout: { xs: 24, lg: 12 },
    overviewGutter: [16, 16],
    detailGutter: [16, 16],
  },
  {
    name: 'compact',
    label: '紧凑布局',
    description: '概览卡片2列，详细信息全宽，适合小屏',
    overviewClass: 'overview-2col',
    detailClass: 'detail-full',
    overviewLayout: { xs: 24, sm: 12, lg: 12 },
    detailLayout: { xs: 24, lg: 24 },
    overviewGutter: [12, 12],
    detailGutter: [12, 12],
  },
  {
    name: 'wide',
    label: '宽屏布局',
    description: '概览卡片4列，详细信息并排，充分利用宽屏',
    overviewClass: 'overview-4col',
    detailClass: 'detail-side',
    overviewLayout: { xs: 24, sm: 12, lg: 6, xl: 6 },
    detailLayout: { xs: 24, lg: 12 },
    overviewGutter: [20, 20],
    detailGutter: [20, 20],
  },
];

// AI助手布局配置（三种完全不同的排版样式）
const aiChatLayouts = [
  {
    name: 'default',
    label: '标准布局',
    description: '左右分栏布局，左侧会话列表，右侧消息区，经典聊天界面',
    sidebarClass: 'sidebar-standard',
    mainClass: 'main-standard',
  },
  {
    name: 'compact',
    label: '上下分割布局',
    description: '上部分横向展示会话卡片，下部分消息区，适合需要快速浏览多个会话的场景',
    sidebarClass: 'sidebar-compact',
    mainClass: 'main-compact',
  },
  {
    name: 'wide',
    label: '全屏消息布局',
    description: '全屏显示消息区，侧边栏可折叠悬浮，最大化消息展示区域，专注对话体验',
    sidebarClass: 'sidebar-wide',
    mainClass: 'main-wide',
  },
];

// YOLO检测布局配置（三种完全不同的排版样式）
const yoloDetectionLayouts = [
  {
    name: 'classic',
    label: '经典两列',
    description: '左侧上传区域，右侧检测结果，左右并列展示，适合对比查看',
    uploadClass: 'upload-left',
    resultClass: 'result-right',
  },
  {
    name: 'vertical',
    label: '上下布局',
    description: '上方上传区域，下方检测结果，上下堆叠展示，适合大屏查看',
    uploadClass: 'upload-top',
    resultClass: 'result-bottom',
  },
  {
    name: 'grid',
    label: '侧边栏详情',
    description: '左侧检测结果列表，右侧详细对比，适合逐个查看和对比分析',
    uploadClass: 'upload-sidebar',
    resultClass: 'result-sidebar',
  },
];

// 检测历史布局配置（三种完全不同的排版样式）
const detectionHistoryLayouts = [
  {
    name: 'default',
    label: '网格布局',
    description: '两列网格布局，卡片式展示，适合快速浏览和对比',
    cardClass: 'card-grid',
  },
  {
    name: 'list',
    label: '列表布局',
    description: '垂直列表布局，紧凑显示详细信息，适合详细查看',
    cardClass: 'card-list',
  },
  {
    name: 'flow',
    label: '卡片流布局',
    description: '瀑布流式卡片布局，全屏展示，适合大量记录浏览',
    cardClass: 'card-flow',
  },
];

// 告警中心布局配置（三种完全不同的排版样式）
const alertCenterLayouts = [
  {
    name: 'table',
    label: '表格布局',
    description: '传统表格布局，清晰展示告警信息，适合快速查看和筛选',
    listClass: 'alert-table',
  },
  {
    name: 'card',
    label: '卡片布局',
    description: '卡片式展示告警信息，视觉效果好，适合详细查看',
    listClass: 'alert-card',
  },
  {
    name: 'timeline',
    label: '时间线布局',
    description: '时间线式展示告警信息，按时间顺序排列，适合追踪告警流程',
    listClass: 'alert-timeline',
  },
];

// 全屏功能
const toggleFullscreen = () => {
  if (!isFullscreen.value) {
    const element = document.documentElement as any;
    if (element.requestFullscreen) {
      element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {
      element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) {
      element.msRequestFullscreen();
    }
  } else {
    const doc = document as any;
    if (doc.exitFullscreen) {
      doc.exitFullscreen();
    } else if (doc.webkitExitFullscreen) {
      doc.webkitExitFullscreen();
    } else if (doc.msExitFullscreen) {
      doc.msExitFullscreen();
    }
  }
};

// 监听全屏状态变化
const handleFullscreenChange = () => {
  const doc = document as any;
  isFullscreen.value = !!(doc.fullscreenElement || doc.webkitFullscreenElement || doc.msFullscreenElement);
};

// 生命周期钩子
onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange);
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
  document.addEventListener('MSFullscreenChange', handleFullscreenChange);
});

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange);
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
});

// 计算当前布局配置
const currentLayoutConfig = computed(() => {
  return (
    dashboardLayouts.find((l) => l.name === currentDashboardLayout.value) || dashboardLayouts[0]
  );
});

const statsLayout = computed(() => {
  return currentLayoutConfig.value.statsLayout;
});

const quickAccessLayout = computed(() => {
  return currentLayoutConfig.value.quickAccessLayout;
});

const contentLayout = computed(() => {
  return currentLayoutConfig.value.contentLayout;
});

// 预设主题配置
const presetThemes = [
  {
    name: 'default',
    label: '默认风格',
    previewBg: '#ffffff',
    headerBg: '#ffffff',
    headerText: '#111827',
    cardBg: '#ffffff',
    cardBorder: '#e5e7eb',
    config: {
      headerBg: '#ffffff',
      headerText: '#111827',
      headerBorder: '#e5e7eb',
      pageBg: '#ffffff',
      contentBg: '#ffffff',
      cardBg: '#ffffff',
      cardBorder: '#e5e7eb',
      primaryColor: '#2563eb',
      textPrimary: '#111827',
      textSecondary: '#6b7280',
    },
  },
  {
    name: 'dark',
    label: '深色模式',
    previewBg: '#1f2937',
    headerBg: '#111827',
    headerText: '#f9fafb',
    cardBg: '#1f2937',
    cardBorder: '#374151',
    config: {
      headerBg: '#111827',
      headerText: '#f9fafb',
      headerBorder: '#374151',
      pageBg: '#111827',
      contentBg: '#1f2937',
      cardBg: '#1f2937',
      cardBorder: '#374151',
      primaryColor: '#3b82f6',
      textPrimary: '#f9fafb',
      textSecondary: '#d1d5db',
    },
  },
  {
    name: 'blue',
    label: '蓝色主题',
    previewBg: '#f0f7ff',
    headerBg: '#2563eb',
    headerText: '#ffffff',
    cardBg: '#ffffff',
    cardBorder: '#93c5fd',
    config: {
      headerBg: '#2563eb',
      headerText: '#ffffff',
      headerBorder: '#3b82f6',
      pageBg: '#f0f7ff',
      contentBg: '#ffffff',
      cardBg: '#ffffff',
      cardBorder: '#93c5fd',
      primaryColor: '#2563eb',
      textPrimary: '#1e40af',
      textSecondary: '#3b82f6',
    },
  },
  {
    name: 'green',
    label: '绿色主题',
    previewBg: '#f0fdf4',
    headerBg: '#10b981',
    headerText: '#ffffff',
    cardBg: '#ffffff',
    cardBorder: '#86efac',
    config: {
      headerBg: '#10b981',
      headerText: '#ffffff',
      headerBorder: '#059669',
      pageBg: '#f0fdf4',
      contentBg: '#ffffff',
      cardBg: '#ffffff',
      cardBorder: '#86efac',
      primaryColor: '#10b981',
      textPrimary: '#047857',
      textSecondary: '#059669',
    },
  },
  {
    name: 'purple',
    label: '紫色主题',
    previewBg: '#faf5ff',
    headerBg: '#8b5cf6',
    headerText: '#ffffff',
    cardBg: '#ffffff',
    cardBorder: '#c4b5fd',
    config: {
      headerBg: '#8b5cf6',
      headerText: '#ffffff',
      headerBorder: '#7c3aed',
      pageBg: '#faf5ff',
      contentBg: '#ffffff',
      cardBg: '#ffffff',
      cardBorder: '#c4b5fd',
      primaryColor: '#8b5cf6',
      textPrimary: '#6d28d9',
      textSecondary: '#7c3aed',
    },
  },
  {
    name: 'orange',
    label: '橙色主题',
    previewBg: '#fff7ed',
    headerBg: '#f59e0b',
    headerText: '#ffffff',
    cardBg: '#ffffff',
    cardBorder: '#fcd34d',
    config: {
      headerBg: '#f59e0b',
      headerText: '#ffffff',
      headerBorder: '#d97706',
      pageBg: '#fff7ed',
      contentBg: '#ffffff',
      cardBg: '#ffffff',
      cardBorder: '#fcd34d',
      primaryColor: '#f59e0b',
      textPrimary: '#92400e',
      textSecondary: '#d97706',
    },
  },
];

// 主题相关方法
const openThemeModal = () => {
  themeConfig.value = { ...themeStore.theme };
  // 检查当前主题是否匹配预设
  const matchedPreset = presetThemes.find(
    (preset) => JSON.stringify(preset.config) === JSON.stringify(themeStore.theme)
  );
  currentPreset.value = matchedPreset ? matchedPreset.name : 'custom';
  showThemeModal.value = true;
};

const applyPresetTheme = (preset: (typeof presetThemes)[0]) => {
  currentPreset.value = preset.name;
  themeConfig.value = { ...preset.config };
  themeStore.updateTheme(themeConfig.value);
  showCustomEditor.value = false;
};

const handleColorChange = (key: keyof ThemeConfig, color: any) => {
  // ColorPicker 可能返回字符串或对象，需要处理不同格式
  let colorValue: string = '';

  if (typeof color === 'string') {
    colorValue = color;
  } else if (color?.toHexString) {
    colorValue = color.toHexString();
  } else if (color?.hex) {
    colorValue = color.hex;
  } else if (color?.value) {
    colorValue = color.value;
  }

  if (colorValue) {
    themeConfig.value[key] = colorValue;
    currentPreset.value = 'custom';
    themeStore.updateTheme(themeConfig.value);
  }
};

const onThemeChange = () => {
  currentPreset.value = 'custom';
  themeStore.updateTheme(themeConfig.value);
};

const saveTheme = () => {
  themeStore.updateTheme(themeConfig.value);
  showThemeModal.value = false;
  message.success('主题已保存');
};

const resetTheme = () => {
  const defaultPreset = presetThemes.find((p) => p.name === 'default');
  if (defaultPreset) {
    applyPresetTheme(defaultPreset);
  } else {
    themeStore.resetTheme();
    themeConfig.value = { ...themeStore.theme };
  }
  currentPreset.value = 'default';
  message.success('已重置为默认主题');
};

// 布局相关方法
const openLayoutModal = () => {
  const savedLayout = localStorage.getItem('dashboardLayout');
  if (savedLayout) {
    currentDashboardLayout.value = savedLayout;
  }
  const savedMonitorLayout = localStorage.getItem('systemMonitorLayout');
  if (savedMonitorLayout) {
    currentSystemMonitorLayout.value = savedMonitorLayout;
  }
  const savedAiChatLayout = localStorage.getItem('aiChatLayout');
  if (savedAiChatLayout) {
    currentAiChatLayout.value = savedAiChatLayout;
  }

  // 根据当前页面确定要显示的布局类型
  const currentMenu = route.query.menu as string;
  if (currentMenu === 'system-monitor') {
    currentLayoutType.value = 'system-monitor';
  } else if (currentMenu === 'ai-chat') {
    currentLayoutType.value = 'ai-chat';
  } else if (currentMenu === 'yolo-detection') {
    currentLayoutType.value = 'yolo-detection';
    const savedYoloDetectionLayout = localStorage.getItem('yoloDetectionLayout');
    if (savedYoloDetectionLayout) {
      currentYoloDetectionLayout.value = savedYoloDetectionLayout;
    }
  } else if (currentMenu === 'detection-history') {
    currentLayoutType.value = 'detection-history';
    const savedDetectionHistoryLayout = localStorage.getItem('detectionHistoryLayout');
    if (savedDetectionHistoryLayout) {
      currentDetectionHistoryLayout.value = savedDetectionHistoryLayout;
    }
  } else if (currentMenu === 'alert-center') {
    currentLayoutType.value = 'alert-center';
    const savedAlertCenterLayout = localStorage.getItem('alertCenterLayout');
    if (savedAlertCenterLayout) {
      currentAlertCenterLayout.value = savedAlertCenterLayout;
    }
  } else {
    // 默认首页或其他页面都显示首页布局
    currentLayoutType.value = 'dashboard';
  }

  showLayoutModal.value = true;
};

const applyDashboardLayout = (layout: (typeof dashboardLayouts)[0]) => {
  currentDashboardLayout.value = layout.name;
  localStorage.setItem('dashboardLayout', layout.name);
};

const applySystemMonitorLayout = (layout: (typeof systemMonitorLayouts)[0]) => {
  currentSystemMonitorLayout.value = layout.name;
  localStorage.setItem('systemMonitorLayout', layout.name);
  window.dispatchEvent(new CustomEvent('systemMonitorLayoutChanged'));
};

const applyAiChatLayout = (layout: (typeof aiChatLayouts)[0]) => {
  currentAiChatLayout.value = layout.name;
  localStorage.setItem('aiChatLayout', layout.name);
  window.dispatchEvent(new CustomEvent('aiChatLayoutChanged'));
};

const applyYoloDetectionLayout = (layout: (typeof yoloDetectionLayouts)[0]) => {
  currentYoloDetectionLayout.value = layout.name;
  localStorage.setItem('yoloDetectionLayout', layout.name);
  window.dispatchEvent(new CustomEvent('yoloDetectionLayoutChanged'));
};

const applyDetectionHistoryLayout = (layout: (typeof detectionHistoryLayouts)[0]) => {
  currentDetectionHistoryLayout.value = layout.name;
  localStorage.setItem('detectionHistoryLayout', layout.name);
  window.dispatchEvent(new CustomEvent('detectionHistoryLayoutChanged'));
};

const applyAlertCenterLayout = (layout: (typeof alertCenterLayouts)[0]) => {
  currentAlertCenterLayout.value = layout.name;
  localStorage.setItem('alertCenterLayout', layout.name);
  window.dispatchEvent(new CustomEvent('alertCenterLayoutChanged'));
};

const saveLayout = () => {
  if (currentLayoutType.value === 'dashboard') {
    localStorage.setItem('dashboardLayout', currentDashboardLayout.value);
    message.success('首页布局已保存');
  } else if (currentLayoutType.value === 'system-monitor') {
    localStorage.setItem('systemMonitorLayout', currentSystemMonitorLayout.value);
    window.dispatchEvent(new CustomEvent('systemMonitorLayoutChanged'));
    message.success('系统监控布局已保存');
  } else if (currentLayoutType.value === 'ai-chat') {
    localStorage.setItem('aiChatLayout', currentAiChatLayout.value);
    window.dispatchEvent(new CustomEvent('aiChatLayoutChanged'));
    message.success('AI助手布局已保存');
  } else if (currentLayoutType.value === 'yolo-detection') {
    localStorage.setItem('yoloDetectionLayout', currentYoloDetectionLayout.value);
    window.dispatchEvent(new CustomEvent('yoloDetectionLayoutChanged'));
    message.success('YOLO检测布局已保存');
  } else if (currentLayoutType.value === 'detection-history') {
    localStorage.setItem('detectionHistoryLayout', currentDetectionHistoryLayout.value);
    window.dispatchEvent(new CustomEvent('detectionHistoryLayoutChanged'));
    message.success('检测历史布局已保存');
  } else if (currentLayoutType.value === 'alert-center') {
    localStorage.setItem('alertCenterLayout', currentAlertCenterLayout.value);
    window.dispatchEvent(new CustomEvent('alertCenterLayoutChanged'));
    message.success('告警中心布局已保存');
  }
  showLayoutModal.value = false;
};

const resetLayout = () => {
  if (currentLayoutType.value === 'dashboard') {
    currentDashboardLayout.value = 'default';
    localStorage.removeItem('dashboardLayout');
    message.success('首页布局已重置为默认');
  } else if (currentLayoutType.value === 'system-monitor') {
    currentSystemMonitorLayout.value = 'default';
    localStorage.removeItem('systemMonitorLayout');
    window.dispatchEvent(new CustomEvent('systemMonitorLayoutChanged'));
    message.success('系统监控布局已重置为默认');
  } else if (currentLayoutType.value === 'ai-chat') {
    currentAiChatLayout.value = 'default';
    localStorage.removeItem('aiChatLayout');
    window.dispatchEvent(new CustomEvent('aiChatLayoutChanged'));
    message.success('AI助手布局已重置为默认');
  } else if (currentLayoutType.value === 'yolo-detection') {
    currentYoloDetectionLayout.value = 'classic';
    localStorage.removeItem('yoloDetectionLayout');
    window.dispatchEvent(new CustomEvent('yoloDetectionLayoutChanged'));
    message.success('YOLO检测布局已重置为默认');
  } else if (currentLayoutType.value === 'detection-history') {
    currentDetectionHistoryLayout.value = 'default';
    localStorage.removeItem('detectionHistoryLayout');
    window.dispatchEvent(new CustomEvent('detectionHistoryLayoutChanged'));
    message.success('检测历史布局已重置为默认');
  } else if (currentLayoutType.value === 'alert-center') {
    currentAlertCenterLayout.value = 'table';
    localStorage.removeItem('alertCenterLayout');
    window.dispatchEvent(new CustomEvent('alertCenterLayoutChanged'));
    message.success('告警中心布局已重置为默认');
  }
};

// 🎯 动态菜单数据 - 根据用户权限过滤
const menuItems = computed(() => {
  if (!userStore.userInfo) {
    return [];
  }

  const userRoles = userStore.userInfo.roles?.map((role) => role.role_code) || [];
  const userPermissions = userStore.userInfo.permissions || [];

  return getFilteredUserMenuItems(userRoles, userPermissions);
});

// 使用集中化配置的组件映射
const componentMap = userComponentMap;

// 计算属性
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  });
});

const breadcrumbItems = computed(() => {
  const currentKey = selectedKeys.value[0];
  return getMenuBreadcrumb(currentKey);
});

// 获取图标组件
const getIconComponent = (iconName?: string) => {
  const iconMap: Record<string, any> = {
    DashboardOutlined,
    UserOutlined,
    AppstoreOutlined,
    FileTextOutlined,
    MessageOutlined,
    BellOutlined,
    DatabaseOutlined,
  };
  return iconMap[iconName || 'DashboardOutlined'] || DashboardOutlined;
};

// 获取随机装饰图标
const getRandomDecorIcon = () => {
  const decorIcons = [
    DashboardOutlined,
    AppstoreOutlined,
    DatabaseOutlined,
    FileTextOutlined,
    MessageOutlined,
    BellOutlined,
  ];
  const randomIndex = Math.floor(Math.random() * decorIcons.length);
  return decorIcons[randomIndex];
};

// 根据路由 query 同步菜单选中与组件
const applyMenuQuery = () => {
  const key = route.query.menu as string | undefined;
  if (key && componentMap[key]) {
    selectedKeys.value = [key];
    currentComponent.value = componentMap[key];
  } else {
    // 没有 menu 参数或 menu 为 dashboard，显示首页
    selectedKeys.value = ['dashboard'];
    currentComponent.value = null;
    // 延迟检查地图初始化，确保 DOM 已更新
    setTimeout(() => {
      checkAndInitMap();
    }, 300);
  }
};

// 初始化语音识别
const initSpeechRecognition = () => {
  // 检查浏览器是否支持 Web Speech API
  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

  if (!SpeechRecognition) {
    isSpeechSupported.value = false;
    return;
  }

  try {
    recognition = new SpeechRecognition();
    recognition.lang = 'zh-CN'; // 设置中文识别
    recognition.continuous = true; // 持续识别
    recognition.interimResults = true; // 返回临时结果

    // 识别开始
    recognition.onstart = () => {
      isListening.value = true;
      isInitializing.value = false;
      message.success('语音识别已开始');
    };

    // 识别结果
    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      // 更新识别结果
      if (finalTranscript) {
        recognitionText.value += finalTranscript + ' ';
        interimText.value = ''; // 清空临时文本
      } else if (interimTranscript) {
        // 显示临时结果
        interimText.value = interimTranscript;
      }
    };

    // 识别错误
    recognition.onerror = (event: any) => {
      console.error('语音识别错误:', event.error);
      isListening.value = false;
      isInitializing.value = false;

      switch (event.error) {
        case 'no-speech':
          message.warning('未检测到语音，请重试');
          break;
        case 'audio-capture':
          message.error('无法访问麦克风，请检查权限设置');
          break;
        case 'not-allowed':
          message.error('麦克风权限被拒绝，请在浏览器设置中允许麦克风访问');
          break;
        default:
          message.error('语音识别出错: ' + event.error);
      }
    };

    // 识别结束
    recognition.onend = () => {
      isListening.value = false;
      isInitializing.value = false;
      interimText.value = ''; // 清空临时文本
      // 如果用户没有手动停止，自动重新开始（可选）
      // if (shouldContinueListening) {
      //   recognition.start()
      // }
    };

    isSpeechSupported.value = true;
  } catch (error) {
    console.error('初始化语音识别失败:', error);
    isSpeechSupported.value = false;
    message.error('初始化语音识别失败');
  }
};

// 切换语音识别
const toggleSpeechRecognition = () => {
  if (!recognition) {
    message.error('语音识别未初始化');
    return;
  }

  if (isListening.value) {
    // 停止识别
    try {
      recognition.stop();
      isListening.value = false;
      message.info('语音识别已停止');
    } catch (error) {
      console.error('停止语音识别失败:', error);
      message.error('停止语音识别失败');
    }
  } else {
    // 开始识别
    try {
      isInitializing.value = true;
      recognitionText.value = ''; // 清空之前的结果（可选）
      interimText.value = ''; // 清空临时文本
      recognition.start();
    } catch (error) {
      console.error('启动语音识别失败:', error);
      isInitializing.value = false;
      message.error('启动语音识别失败，请重试');
    }
  }
};

// 清空识别结果
const clearRecognitionText = () => {
  recognitionText.value = '';
  interimText.value = '';
  message.info('识别结果已清空');
};

// 数字转中文
const numberToChinese = (num: string): string => {
  const digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
  let result = '';

  for (let i = 0; i < num.length; i++) {
    const char = num[i];
    if (char >= '0' && char <= '9') {
      result += digits[parseInt(char)];
    } else {
      result += char;
    }
  }

  return result;
};

// 处理文本，将数字转换为中文（可选）
const processTextForSynthesis = (text: string, convertNumbers: boolean = false): string => {
  if (!convertNumbers) {
    return text;
  }
  return text;
};

// 获取中文语音
const getChineseVoice = (): SpeechSynthesisVoice | null => {
  if (!synthesis) return null;

  const voices = synthesis.getVoices();
  // 优先选择 zh-CN，其次选择包含 zh 的语音
  const chineseVoice =
    voices.find((voice) => voice.lang === 'zh-CN' || voice.lang.startsWith('zh-CN')) ||
    voices.find((voice) => voice.lang.startsWith('zh'));

  return chineseVoice || null;
};

// 初始化语音合成
const initSpeechSynthesis = () => {
  // 检查浏览器是否支持 SpeechSynthesis API
  if (!('speechSynthesis' in window)) {
    isSynthesisSupported.value = false;
    return;
  }

  try {
    synthesis = window.speechSynthesis;
    isSynthesisSupported.value = true;

    // 加载语音列表
    const loadVoices = () => {
      const voices = synthesis?.getVoices() || [];
      if (voices.length > 0) {
        voicesLoaded.value = true;
        console.log('语音列表已加载，可用语音数量:', voices.length);
      }
    };

    // 监听语音合成状态变化
    synthesis.onvoiceschanged = loadVoices;

    // 如果语音列表已经加载，立即触发一次
    loadVoices();

    // 某些浏览器需要延迟加载
    setTimeout(() => {
      loadVoices();
    }, 100);
  } catch (error) {
    console.error('初始化语音合成失败:', error);
    isSynthesisSupported.value = false;
    message.error('初始化语音合成失败');
  }
};

// 切换语音合成
const toggleSpeechSynthesis = async () => {
  if (!synthesis) {
    message.error('语音合成未初始化');
    return;
  }

  if (isSpeaking.value) {
    // 停止播放
    try {
      synthesis.cancel();
      isSpeaking.value = false;
      currentUtterance = null;
      message.info('语音播放已停止');
    } catch (error) {
      console.error('停止语音播放失败:', error);
      message.error('停止语音播放失败');
    }
  } else {
    // 开始播放
    const text = synthesisText.value.trim();
    if (!text) {
      message.warning('请输入要朗读的文字');
      return;
    }

    // 检查文本长度（某些浏览器对文本长度有限制）
    if (text.length > 200) {
      message.warning('文本过长，建议分段播放（每次不超过200字）');
      // 仍然尝试播放，但可能会失败
    }

    try {
      // 确保语音列表已加载
      if (!voicesLoaded.value) {
        const voices = synthesis.getVoices();
        if (voices.length > 0) {
          voicesLoaded.value = true;
        } else {
          // 等待语音列表加载
          message.warning('正在加载语音列表，请稍候...');
          setTimeout(() => {
            const retryVoices = synthesis.getVoices();
            if (retryVoices.length > 0) {
              voicesLoaded.value = true;
              toggleSpeechSynthesis(); // 重试
            } else {
              message.error('无法加载语音列表，请刷新页面重试');
            }
          }, 500);
          return;
        }
      }

      // 再次确认语音列表已加载（某些浏览器需要多次检查）
      const voices = synthesis.getVoices();
      if (voices.length === 0) {
        message.warning('语音列表未加载，请稍候再试');
        return;
      }

      // 检查是否有可用的中文语音（用于诊断）
      const chineseVoices = voices.filter((voice) => voice.lang.startsWith('zh'));
      const englishVoices = voices.filter((voice) => voice.lang.startsWith('en'));
      console.log('语音诊断信息:', {
        总语音数: voices.length,
        中文语音数: chineseVoices.length,
        英文语音数: englishVoices.length,
        中文语音列表: chineseVoices.map((v) => `${v.name} (${v.lang})`),
        所有语音: voices.map((v) => `${v.name} (${v.lang})`),
      });

      // 如果没有中文语音，提前警告用户
      if (chineseVoices.length === 0) {
        console.warn('警告: 未找到可用的中文语音，可能会使用英文语音或失败');
        message.warning('未找到可用的中文语音，将尝试使用其他语音');
      }

      // 停止当前播放（如果有）
      if (synthesis.speaking || synthesis.pending) {
        synthesis.cancel();
        // 等待一小段时间确保停止完成
        await new Promise((resolve) => setTimeout(resolve, 50));
      }

      // 处理文本：检测纯数字并转换为中文
      let processedText = text;
      const isPureNumbers = /^\d+$/.test(text.trim());
      if (isPureNumbers) {
        processedText = numberToChinese(text.trim());
        console.log('检测到纯数字，转换为中文:', text, '->', processedText);
      }

      // 创建语音合成实例的函数
      const createAndPlayUtterance = (
        textToSpeak: string,
        isRetry: boolean = false,
        useEnglish: boolean = false
      ) => {
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.rate = speechRate.value; // 语速（0.1-10）
        utterance.pitch = speechPitch.value; // 音调（0-2）
        utterance.volume = speechVolume.value; // 音量（0-1）

        // 选择语音（如果可用）
        if (useEnglish) {
          // 使用英文语音
          utterance.lang = 'en-US';
          const englishVoice = synthesis?.getVoices().find((voice) => voice.lang.startsWith('en'));
          if (englishVoice) {
            utterance.voice = englishVoice;
            console.log('使用英文语音:', englishVoice.name, englishVoice.lang);
          } else {
            console.log('未找到英文语音，使用浏览器自动选择');
          }
        } else {
          // 使用中文语音
          // 重要：为了最大兼容性，默认不设置 voice，只设置 lang
          // 某些浏览器（如 Edge、Chrome）在指定 voice 时会出现 synthesis-failed
          // 让浏览器自动选择最合适的中文语音是最可靠的方式
          utterance.lang = 'zh-CN';

          // 不设置 voice，让浏览器自动选择（这是最兼容的方式）
          // 浏览器会自动选择系统中可用的中文语音
          console.log('使用浏览器自动选择中文语音（lang=zh-CN）');
        }

        // 播放开始
        utterance.onstart = () => {
          isSpeaking.value = true;
          console.log('语音播放已开始');
        };

        // 播放结束
        utterance.onend = () => {
          isSpeaking.value = false;
          currentUtterance = null;
          console.log('语音播放已结束');
        };

        // 播放错误
        utterance.onerror = (event: any) => {
          console.error('语音播放错误:', event.error, event);
          isSpeaking.value = false;
          currentUtterance = null;

          // 从 utterance 获取额外信息
          const utteranceInfo = event.utterance as any;
          const isPureNumbersValue = utteranceInfo?.isPureNumbers || isPureNumbers;
          const originalTextValue = utteranceInfo?.originalText || textToSpeak;
          const retryCount = utteranceInfo?.retryCount || 0;

          // 如果是 synthesis-failed，尝试不同的恢复策略
          if (
            (event.error === 'synthesis' || event.error === 'synthesis-failed') &&
            !isRetry &&
            !useEnglish &&
            retryCount < 3
          ) {
            console.warn(`语音合成失败，尝试恢复策略 ${retryCount + 1}/3...`);

            // 策略1: 检查是否有可用的中文语音，如果没有，尝试使用英文
            const voices = synthesis?.getVoices() || [];
            const hasChineseVoice = voices.some((voice) => voice.lang.startsWith('zh'));
            const hasEnglishVoice = voices.some((voice) => voice.lang.startsWith('en'));

            console.log('可用语音检查:', {
              total: voices.length,
              hasChinese: hasChineseVoice,
              hasEnglish: hasEnglishVoice,
              chineseVoices: voices
                .filter((v) => v.lang.startsWith('zh'))
                .map((v) => `${v.name} (${v.lang})`),
            });

            // 如果没有中文语音，尝试使用英文语音
            if (!hasChineseVoice && hasEnglishVoice && retryCount === 0) {
              console.warn('未找到中文语音，尝试使用英文语音...');
              const englishVoice = voices.find((voice) => voice.lang.startsWith('en'));
              if (englishVoice) {
                const retryUtterance = new SpeechSynthesisUtterance(textToSpeak);
                retryUtterance.lang = 'en-US';
                retryUtterance.rate = speechRate.value;
                retryUtterance.pitch = speechPitch.value;
                retryUtterance.volume = speechVolume.value;
                (retryUtterance as any).isPureNumbers = isPureNumbersValue;
                (retryUtterance as any).originalText = originalTextValue;
                (retryUtterance as any).retryCount = retryCount + 1;

                retryUtterance.onstart = () => {
                  isSpeaking.value = true;
                  console.log('使用英文语音播放已开始');
                };

                retryUtterance.onend = () => {
                  isSpeaking.value = false;
                  currentUtterance = null;
                  console.log('英文语音播放已结束');
                };

                retryUtterance.onerror = (retryEvent: any) => {
                  console.error('英文语音播放也失败:', retryEvent.error);
                  isSpeaking.value = false;
                  currentUtterance = null;
                  message.error(
                    '语音合成失败，系统可能没有可用的语音。建议：1. 检查系统语音设置 2. 安装中文语音包 3. 使用 Chrome 浏览器'
                  );
                };

                currentUtterance = retryUtterance;
                setTimeout(() => {
                  synthesis?.speak(retryUtterance);
                }, 100);
                return;
              }
            }

            // 策略2: 尝试不同的中文语言代码（zh-TW, zh-HK 等）
            if (hasChineseVoice && retryCount < 2) {
              const chineseLangCodes = ['zh-TW', 'zh-HK', 'zh'];
              const nextLangCode = chineseLangCodes[retryCount];

              if (nextLangCode) {
                console.warn(`尝试使用不同的中文语言代码: ${nextLangCode}`);
                const retryUtterance = new SpeechSynthesisUtterance(textToSpeak);
                retryUtterance.lang = nextLangCode;
                retryUtterance.rate = speechRate.value;
                retryUtterance.pitch = speechPitch.value;
                retryUtterance.volume = speechVolume.value;
                (retryUtterance as any).isPureNumbers = isPureNumbersValue;
                (retryUtterance as any).originalText = originalTextValue;
                (retryUtterance as any).retryCount = retryCount + 1;

                retryUtterance.onstart = () => {
                  isSpeaking.value = true;
                  console.log(`使用 ${nextLangCode} 语音播放已开始`);
                };

                retryUtterance.onend = () => {
                  isSpeaking.value = false;
                  currentUtterance = null;
                  console.log('语音播放已结束');
                };

                retryUtterance.onerror = (retryEvent: any) => {
                  console.error(`使用 ${nextLangCode} 也失败:`, retryEvent.error);
                  isSpeaking.value = false;
                  currentUtterance = null;

                  // 如果还有更多策略，继续尝试
                  if (retryCount + 1 < 2) {
                    const nextRetryUtterance = new SpeechSynthesisUtterance(textToSpeak);
                    const nextLangCode2 = chineseLangCodes[retryCount + 1];
                    nextRetryUtterance.lang = nextLangCode2;
                    nextRetryUtterance.rate = speechRate.value;
                    nextRetryUtterance.pitch = speechPitch.value;
                    nextRetryUtterance.volume = speechVolume.value;
                    (nextRetryUtterance as any).isPureNumbers = isPureNumbersValue;
                    (nextRetryUtterance as any).originalText = originalTextValue;
                    (nextRetryUtterance as any).retryCount = retryCount + 2;

                    nextRetryUtterance.onstart = () => {
                      isSpeaking.value = true;
                      console.log(`使用 ${nextLangCode2} 语音播放已开始`);
                    };

                    nextRetryUtterance.onend = () => {
                      isSpeaking.value = false;
                      currentUtterance = null;
                      console.log('语音播放已结束');
                    };

                    nextRetryUtterance.onerror = () => {
                      console.error(`所有策略都失败`);
                      isSpeaking.value = false;
                      currentUtterance = null;
                      message.error(
                        '语音合成失败，可能是系统没有可用的中文语音。建议：1. 检查系统语音设置 2. 安装中文语音包 3. 使用 Chrome 浏览器 4. 刷新页面重试'
                      );
                    };

                    currentUtterance = nextRetryUtterance;
                    setTimeout(() => {
                      synthesis?.speak(nextRetryUtterance);
                    }, 100);
                  } else {
                    // 所有策略都失败
                    message.error(
                      '语音合成失败，可能是系统没有可用的中文语音。建议：1. 检查系统语音设置 2. 安装中文语音包 3. 使用 Chrome 浏览器 4. 刷新页面重试'
                    );
                  }
                };

                currentUtterance = retryUtterance;
                setTimeout(() => {
                  synthesis?.speak(retryUtterance);
                }, 100);
                return;
              }
            }

            // 策略3: 如果所有策略都失败，显示详细错误信息
            console.error('所有恢复策略都失败');
            const voicesInfo =
              voices.length > 0
                ? `可用语音: ${voices.map((v) => `${v.name}(${v.lang})`).join(', ')}`
                : '未找到可用语音';
            console.error('语音列表:', voicesInfo);
            message.error(
              '语音合成失败，可能是系统没有可用的中文语音。建议：1. 检查系统语音设置 2. 安装中文语音包 3. 使用 Chrome 浏览器 4. 刷新页面重试'
            );
            return;
          }

          // 更详细的错误处理
          let errorMessage = '语音播放出错';
          switch (event.error) {
            case 'network':
              errorMessage = '网络错误，无法播放语音，请检查网络连接';
              break;
            case 'synthesis':
            case 'synthesis-failed':
              if (isPureNumbersValue) {
                errorMessage = '纯数字文本合成失败，已尝试转换，如仍失败请尝试输入中文文本';
              } else {
                errorMessage =
                  '语音合成失败，可能是文本过长或包含特殊字符，请尝试缩短文本或使用更简单的文字';
              }
              break;
            case 'synthesis-unavailable':
              errorMessage = '语音合成服务不可用，请刷新页面重试';
              break;
            case 'audio-busy':
              errorMessage = '音频设备忙碌，请稍候再试';
              break;
            case 'not-allowed':
              errorMessage = '没有权限使用语音合成，请检查浏览器设置';
              break;
            case 'interrupted':
              // 用户中断，不显示错误
              console.log('语音播放被中断');
              return;
            default:
              errorMessage = `语音播放出错: ${event.error || '未知错误'}`;
          }

          // 只有非中断错误才显示消息
          if (event.error !== 'interrupted') {
            message.error(errorMessage);
          }
        };

        return utterance;
      };

      // 创建并播放（将 isPureNumbers 和 text 传递给错误处理函数）
      const utterance = createAndPlayUtterance(processedText);
      // 在 utterance 上添加额外信息，供错误处理使用
      (utterance as any).isPureNumbers = isPureNumbers;
      (utterance as any).originalText = text;
      (utterance as any).retryCount = 0; // 初始化重试次数
      currentUtterance = utterance;

      // 确保语音引擎就绪后再播放
      // 某些浏览器需要等待一小段时间，特别是 Edge 浏览器
      if (synthesis.pending || synthesis.speaking) {
        // 如果正在播放，先停止
        synthesis.cancel();
        await new Promise((resolve) => setTimeout(resolve, 150));
      }

      // 额外等待一小段时间，确保语音引擎完全就绪（特别是 Edge 浏览器）
      // 这对于避免 synthesis-failed 错误很重要
      await new Promise((resolve) => setTimeout(resolve, 50));

      // 使用 speak 方法播放
      try {
        synthesis.speak(utterance);
        console.log('已调用 speak 方法，等待播放开始...');
      } catch (speakError) {
        console.error('speak 方法调用失败:', speakError);
        // 如果 speak 失败，尝试延迟重试
        setTimeout(() => {
          try {
            synthesis.speak(utterance);
            console.log('重试调用 speak 方法');
          } catch (retryError) {
            console.error('重试 speak 也失败:', retryError);
            isSpeaking.value = false;
            message.error('无法启动语音播放，请刷新页面重试');
          }
        }, 200);
      }

      // 如果 speak 方法没有触发 onstart，可能是浏览器问题，尝试延迟检查
      setTimeout(() => {
        if (!isSpeaking.value && synthesis.speaking) {
          isSpeaking.value = true;
          console.log('检测到播放已开始（延迟检查）');
        }
      }, 150);
    } catch (error) {
      console.error('启动语音播放失败:', error);
      isSpeaking.value = false;
      message.error('启动语音播放失败，请重试');
    }
  }
};

// 清空合成文本
const clearSynthesisText = () => {
  if (isSpeaking.value) {
    message.warning('请先停止播放');
    return;
  }
  synthesisText.value = '';
  message.info('文本已清空');
};

// 根据IP获取城市名称（使用免费的IP定位API）
const getCityByIP = async (): Promise<string | null> => {
  const apis = [
    { url: 'http://ip-api.com/json/?lang=zh-CN', type: 'ip-api' },
    { url: 'https://ipapi.co/json/', type: 'ipapi' },
  ];

  for (const api of apis) {
    try {
      const response = await fetch(api.url, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        continue;
      }

      const data = await response.json();
      console.log('IP定位数据:', data);

      if (api.type === 'ip-api' && data.city) {
        return data.city;
      } else if (api.type === 'ipapi' && data.city) {
        const city = data.city;
        if (/[\u4e00-\u9fa5]/.test(city)) {
          return city;
        }
        if (data.region && /[\u4e00-\u9fa5]/.test(data.region)) {
          return data.region;
        }
        return city;
      }
    } catch (error) {
      console.log(`${api.url} 访问失败，尝试下一个API...`);
      continue;
    }
  }

  console.log('所有IP定位API都失败，使用默认城市');
  return null;
};

// 根据地理位置获取城市名称
const getCityByGeolocation = async (): Promise<string | null> => {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      console.warn('浏览器不支持地理位置API');
      resolve(null);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          console.log('获取到位置:', latitude, longitude);

          // 使用免费的逆地理编码API（OpenStreetMap Nominatim）
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&accept-language=zh-CN`,
            {
              method: 'GET',
              headers: {
                Accept: 'application/json',
                'User-Agent': 'WeatherApp/1.0',
              },
            }
          );

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          console.log('逆地理编码数据:', data);

          // 提取城市名称
          const address = data.address || {};
          // 优先使用city，其次使用town、village、county
          const city =
            address.city || address.town || address.village || address.county || address.state;

          if (city) {
            resolve(city);
          } else {
            resolve(null);
          }
        } catch (error) {
          console.error('逆地理编码失败:', error);
          resolve(null);
        }
      },
      (error) => {
        console.warn('获取地理位置失败:', error);
        resolve(null);
      },
      {
        timeout: 5000,
        enableHighAccuracy: false,
      }
    );
  });
};

// 自动检测并查询天气（直接使用IP定位，速度更快）
const autoDetectAndQueryWeather = async () => {
  if (isAutoDetecting.value || weatherLoading.value) {
    return;
  }

  isAutoDetecting.value = true;

  try {
    // 直接使用IP定位，速度更快
    console.log('正在使用IP定位获取城市信息...');
    const cityName = await getCityByIP();

    if (cityName) {
      console.log('检测到城市:', cityName);

      // 首先尝试将英文城市名转换为中文
      let chineseCityName = cityName;
      if (englishToChineseCityMap[cityName]) {
        chineseCityName = englishToChineseCityMap[cityName];
        console.log('转换为中文城市名:', chineseCityName);
      }

      // 检查城市是否在支持列表中
      if (cityStationIdMap[chineseCityName]) {
        weatherCityName.value = chineseCityName;
        await queryWeather();
      } else {
        // 尝试匹配城市名称（去除"市"、"区"等后缀）
        const cityNameWithoutSuffix = chineseCityName.replace(/[市区县]$/, '');
        if (cityStationIdMap[cityNameWithoutSuffix]) {
          weatherCityName.value = cityNameWithoutSuffix;
          await queryWeather();
        } else {
          console.warn('检测到的城市不在支持列表中:', cityName, '->', chineseCityName);
          // 可以提示用户手动输入
        }
      }
    } else {
      console.warn('无法自动检测城市位置');
    }
  } catch (error) {
    console.error('自动检测位置失败:', error);
  } finally {
    isAutoDetecting.value = false;
  }
};

// 获取新闻资讯（使用国内可访问的新闻源）
const fetchNews = async () => {
  newsLoading.value = true;
  newsList.value = [];

  try {
    // 使用百度新闻RSS源，通过代理访问
    // 优先使用代理，避免CORS问题
    const rssSources = [
      // 方法1: 使用代理访问百度新闻国内新闻（开发环境）
      import.meta.env.DEV
        ? '/api/rss/domestic'
        : 'https://news.baidu.com/n?cmd=1&class=civilnews&tn=rss',
      // 方法2: 备选 - 国际新闻
      import.meta.env.DEV
        ? '/api/rss/world'
        : 'https://news.baidu.com/n?cmd=1&class=internet&tn=rss',
      // 方法3: 备选 - 科技新闻
      import.meta.env.DEV ? '/api/rss/tech' : 'https://news.baidu.com/n?cmd=1&class=technic&tn=rss',
    ].filter(Boolean) as string[];

    let xmlText = '';
    let lastError: Error | null = null;

    // 依次尝试每个RSS源，设置超时避免长时间等待
    for (const rssUrl of rssSources) {
      try {
        console.log('正在尝试获取RSS新闻:', rssUrl);

        // 使用Promise.race设置超时（5秒）
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('请求超时')), 5000);
        });

        const fetchPromise = fetch(rssUrl, {
          method: 'GET',
          headers: {
            Accept: 'application/xml, text/xml, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          },
          redirect: 'follow',
        });

        const response = await Promise.race([fetchPromise, timeoutPromise]);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        xmlText = await response.text();
        console.log('RSS XML数据长度:', xmlText.length);

        // 如果成功获取数据，跳出循环
        if (xmlText && xmlText.length > 0) {
          break;
        }
      } catch (error: any) {
        console.warn(`RSS源 ${rssUrl} 获取失败:`, error.message);
        lastError = error;
        // 继续尝试下一个源
        continue;
      }
    }

    // 如果所有源都失败，抛出错误
    if (!xmlText || xmlText.length === 0) {
      throw lastError || new Error('所有RSS源都获取失败，请检查网络连接或稍后重试');
    }

    // 使用DOMParser解析XML
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, 'text/xml');

    // 检查解析错误
    const parserError = xmlDoc.querySelector('parsererror');
    if (parserError) {
      throw new Error('XML解析失败: ' + parserError.textContent);
    }

    // 获取所有item元素
    const items = xmlDoc.querySelectorAll('item');
    console.log('找到新闻条目数:', items.length);

    // 解析所有新闻
    const allNews: Array<{ title: string; link: string; date: string }> = [];

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const titleElement = item.querySelector('title');
      const linkElement = item.querySelector('link');
      const pubDateElement = item.querySelector('pubDate');

      if (titleElement && linkElement) {
        const title = titleElement.textContent || '';
        const link = linkElement.textContent || '';
        let date = '';

        // 解析日期
        if (pubDateElement) {
          const pubDate = pubDateElement.textContent || '';
          try {
            const dateObj = new Date(pubDate);
            if (!isNaN(dateObj.getTime())) {
              date = dateObj.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
              });
            } else {
              date = pubDate;
            }
          } catch (e) {
            date = pubDate;
          }
        }

        allNews.push({
          title: title.trim(),
          link: link.trim(),
          date: date || '未知日期',
        });
      }
    }

    console.log('解析到的所有新闻数量:', allNews.length);

    // 从所有新闻中随机选择5条
    const news: Array<{ title: string; link: string; date: string }> = [];
    const maxItems = Math.min(5, allNews.length);

    if (allNews.length > 0) {
      // 创建索引数组并打乱顺序
      const indices = Array.from({ length: allNews.length }, (_, i) => i);
      // Fisher-Yates 洗牌算法
      for (let i = indices.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [indices[i], indices[j]] = [indices[j], indices[i]];
      }

      // 从打乱后的索引中选择前5条
      for (let i = 0; i < maxItems; i++) {
        news.push(allNews[indices[i]]);
      }
    }

    newsList.value = news;
    console.log('随机选择的新闻:', news);

    if (news.length === 0) {
      message.warning('未找到新闻数据');
    } else {
      message.success(`成功加载 ${news.length} 条新闻`);
    }
  } catch (error: any) {
    console.error('获取新闻失败:', error);

    // 提供更详细的错误信息
    let errorMessage = '获取新闻失败，请稍后重试';
    if (error.message) {
      if (error.message.includes('CORS') || error.message.includes('跨域')) {
        errorMessage = '跨域请求失败，请检查代理配置或刷新页面重试';
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = '网络请求失败，可能是代理配置问题，请重启开发服务器后重试';
      } else if (error.message.includes('XML解析')) {
        errorMessage = 'XML解析失败，请稍后重试';
      } else {
        errorMessage = `获取新闻失败: ${error.message}`;
      }
    }

    message.error(errorMessage);
    newsList.value = [];
  } finally {
    newsLoading.value = false;
  }
};

// 打开新闻链接
const openNewsLink = (link: string) => {
  if (link) {
    window.open(link, '_blank');
  }
};

// 检测文本是否为中文
const detectChinese = (text: string): boolean => {
  // 检测是否包含中文字符（包括中文标点）
  const chineseRegex = /[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]/;
  return chineseRegex.test(text);
};

// 翻译功能
const handleTranslation = async () => {
  const text = translationInput.value.trim();
  if (!text) {
    message.warning('请输入要翻译的文本');
    return;
  }

  translationLoading.value = true;
  translationResult.value = '';
  translationError.value = '';

  try {
    // 根据选择的翻译类型确定语言方向
    // ZH2EN: 中文到英文, EN2ZH: 英文到中文, AUTO: 自动识别
    let langpair = 'zh-CN|en-GB'; // 默认中文→英文

    if (translationType.value === 'ZH2EN') {
      langpair = 'zh-CN|en-GB';
    } else if (translationType.value === 'EN2ZH') {
      langpair = 'en-GB|zh-CN';
    } else {
      // 自动识别：根据输入内容判断方向
      const isChinese = detectChinese(text);
      if (isChinese) {
        langpair = 'zh-CN|en-GB'; // 中文→英文
      } else {
        langpair = 'en-GB|zh-CN'; // 英文→中文
      }
    }

    // 使用 MyMemory 免费翻译 API
    // API: https://api.mymemory.translated.net/get
    // 参数: q=文本&langpair=源语言|目标语言
    const apiUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langpair}`;

    console.log('正在翻译:', text, '类型:', translationType.value, '语言对:', langpair);
    console.log('翻译URL:', apiUrl);

    try {
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('翻译API返回数据:', data);

      // 检查是否有错误响应
      if (data && data.responseStatus && data.responseStatus !== 200) {
        const errorMsg = data.responseDetails || '翻译服务异常';
        console.error('翻译API返回错误:', data.responseStatus, errorMsg);
        throw new Error(`翻译失败: ${errorMsg}`);
      }

      // 解析 MyMemory 返回结果
      // MyMemory 返回格式: { responseData: { translatedText: "译文", ... }, ... }
      if (data && data.responseData && data.responseData.translatedText) {
        translationResult.value = data.responseData.translatedText;
        message.success('翻译成功');
      } else {
        throw new Error('翻译结果格式不正确');
      }
    } catch (fetchError: any) {
      // 如果是网络错误，提供更详细的错误信息
      if (
        fetchError.message.includes('Failed to fetch') ||
        fetchError.message.includes('NetworkError')
      ) {
        console.error('翻译网络请求失败:', fetchError);
        throw new Error('网络请求失败，请检查网络连接');
      }
      throw fetchError;
    }
  } catch (error: any) {
    console.error('翻译失败:', error);
    translationError.value = '翻译失败，请稍后重试';
    message.error('翻译失败，请稍后重试');
  } finally {
    translationLoading.value = false;
  }
};

// 加载 Leaflet 地图库（免费开源，无需 key）
const loadLeafletScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 检查是否已经加载
    if (window.L && window.L.map) {
      console.log('Leaflet 地图库已加载');
      resolve();
      return;
    }

    console.log('开始加载 Leaflet 地图库...');

    // 加载 Leaflet CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    link.crossOrigin = '';
    document.head.appendChild(link);

    // 加载 Leaflet JS
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    script.crossOrigin = '';
    script.async = false;

    script.onload = () => {
      console.log('Leaflet 地图库加载完成');
      if (window.L && window.L.map) {
        resolve();
      } else {
        reject(new Error('Leaflet 地图库初始化失败'));
      }
    };

    script.onerror = (error) => {
      console.error('Leaflet 地图库加载失败:', error);
      reject(new Error('Leaflet 地图库加载失败，请检查网络连接'));
    };

    document.head.appendChild(script);
    console.log('已添加 Leaflet 脚本标签到页面');
  });
};

// 初始化地图
const initMap = async () => {
  try {
    console.log('开始初始化地图...');
    // 等待 Leaflet 地图库加载完成
    await loadLeafletScript();

    // 检查容器是否存在
    const container = document.getElementById('tencent-map-container');
    if (!container) {
      // 在非仪表盘或容器尚未渲染时，静默跳过初始化，避免在其他页面弹出错误
      console.warn('地图容器不存在，跳过地图初始化');
      return;
    }

    console.log('地图容器找到，开始创建地图实例...');

    // 如果地图已经初始化，先清除
    if (mapInstance) {
      // 清除所有标记点
      markers.forEach((marker) => {
        mapInstance.removeLayer(marker);
      });
      markers = [];
      mapInstance.remove();
      mapInstance = null;
    }

    // 创建地图实例，默认显示北京（116.39, 39.9），缩放级别 10
    // Leaflet 使用 [纬度, 经度] 格式
    console.log('创建地图实例...');

    // 确保容器有正确的大小
    const containerRect = container.getBoundingClientRect();
    console.log('地图容器大小:', containerRect.width, 'x', containerRect.height);

    if (containerRect.width === 0 || containerRect.height === 0) {
      console.warn('地图容器大小为0，等待容器渲染...');
      // 延迟重试
      setTimeout(() => {
        initMap();
      }, 500);
      return;
    }

    mapInstance = window.L.map(container, {
      zoomControl: true,
      attributionControl: true,
    }).setView([39.9, 116.39], 10);

    // 添加地图图层（使用国内可访问的地图源，支持多个备用源）
    // 优先使用高德地图（国内访问速度快）
    const gaodeLayer = window.L.tileLayer(
      'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
      {
        subdomains: ['1', '2', '3', '4'],
        attribution: '© 高德地图',
        maxZoom: 18,
        tileSize: 256,
        zoomOffset: 0,
        errorTileUrl:
          'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', // 加载失败时显示空白图
      }
    );

    // 备用：OpenStreetMap（如果高德地图加载失败）
    const osmLayer = window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      subdomains: ['a', 'b', 'c'],
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
      errorTileUrl:
        'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
    });

    // 备用2：使用天地图（国内备用源）
    const tiandituLayer = window.L.tileLayer(
      'https://t{s}.tianditu.gov.cn/DataServer?T=vec_w&x={x}&y={y}&l={z}&tk=您的key',
      {
        subdomains: ['0', '1', '2', '3', '4', '5', '6', '7'],
        attribution: '© 天地图',
        maxZoom: 18,
        errorTileUrl:
          'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
      }
    );

    // 尝试添加高德地图图层，如果失败则使用 OpenStreetMap
    let currentLayer = gaodeLayer;
    try {
      gaodeLayer.addTo(mapInstance);
      console.log('使用高德地图图层');

      // 监听瓦片加载错误，自动切换到备用源
      let errorCount = 0;
      gaodeLayer.on('tileerror', (error: any) => {
        errorCount++;
        console.warn(`高德地图瓦片加载失败 (${errorCount}次):`, error);

        // 如果连续失败多次，切换到备用源
        if (errorCount >= 3) {
          console.warn('高德地图瓦片连续加载失败，切换到 OpenStreetMap');
          mapInstance.removeLayer(gaodeLayer);
          currentLayer = osmLayer;
          osmLayer.addTo(mapInstance);

          // 如果 OpenStreetMap 也失败，尝试其他源
          osmLayer.on('tileerror', () => {
            console.warn('OpenStreetMap 也加载失败，地图可能无法正常显示');
          });
        }
      });

      // 监听瓦片加载成功，重置错误计数
      gaodeLayer.on('tileload', () => {
        if (errorCount > 0) {
          console.log('高德地图瓦片加载成功，重置错误计数');
          errorCount = 0;
        }
      });
    } catch (error) {
      console.warn('高德地图图层添加失败，使用 OpenStreetMap:', error);
      currentLayer = osmLayer;
      osmLayer.addTo(mapInstance);
    }

    // 确保地图大小正确
    setTimeout(() => {
      if (mapInstance) {
        mapInstance.invalidateSize();
        console.log('地图大小已重新计算');
      }
    }, 100);

    console.log('地图实例创建成功');

    // 添加地图点击事件，点击任意处添加标记
    console.log('添加地图点击事件...');
    mapInstance.on('click', (e: any) => {
      const lat = e.latlng.lat;
      const lng = e.latlng.lng;

      // 控制台打印点击处的经纬度
      console.log(`点击位置 - 经度: ${lng}, 纬度: ${lat}`);

      // 添加标记点
      const marker = window.L.marker([lat, lng]).addTo(mapInstance);
      markers.push(marker);
    });

    console.log('Leaflet 地图初始化成功');

    // 自动定位到设备当前位置（实时获取）
    if (navigator.geolocation) {
      console.log('开始自动定位到设备当前位置（实时获取）...');

      // 使用 watchPosition 实时跟踪位置变化
      const watchId = navigator.geolocation.watchPosition(
        (position) => {
          const { longitude, latitude, accuracy } = position.coords;
          console.log(
            `获取到实时位置 - 经度: ${longitude}, 纬度: ${latitude}, 精度: ${accuracy}米`
          );

          if (mapInstance) {
            // Leaflet 使用 [纬度, 经度] 格式
            const center: [number, number] = [latitude, longitude];

            // 清除之前的标记点
            markers.forEach((marker) => {
              mapInstance.removeLayer(marker);
            });
            markers = [];

            // 确保地图大小正确（重要：解决白屏问题）
            mapInstance.invalidateSize();

            // 移动到当前位置
            mapInstance.setView(center, 15); // 设置合适的缩放级别

            // 再次确保地图大小正确（定位后）
            setTimeout(() => {
              if (mapInstance) {
                mapInstance.invalidateSize();
                console.log('定位后地图大小已重新计算');
              }
            }, 200);

            // 添加当前位置标记点（带精度圆圈）
            const marker = window.L.marker(center).addTo(mapInstance);
            marker
              .bindPopup(
                `当前位置<br>经度: ${longitude.toFixed(6)}<br>纬度: ${latitude.toFixed(6)}<br>精度: ${Math.round(accuracy)}米`
              )
              .openPopup();
            markers.push(marker);

            // 如果有精度信息且精度合理（小于50公里），添加精度圆圈
            if (accuracy && accuracy < 50000) {
              const circle = window.L.circle(center, {
                radius: accuracy,
                color: '#3b82f6',
                fillColor: '#3b82f6',
                fillOpacity: 0.1,
              }).addTo(mapInstance);
              markers.push(circle as any);
            } else if (accuracy && accuracy >= 50000) {
              console.warn(`定位精度较低: ${Math.round(accuracy)}米，不显示精度圆圈`);
            }

            console.log('实时定位成功');

            // 获取一次位置后停止跟踪（避免频繁更新）
            navigator.geolocation.clearWatch(watchId);
          }
        },
        (error) => {
          console.warn('自动定位失败，使用默认位置（北京）:', error);
          navigator.geolocation.clearWatch(watchId);
          // 定位失败时，保持默认的北京位置
        },
        {
          enableHighAccuracy: true, // 高精度定位（使用GPS）
          timeout: 20000, // 超时时间 20 秒（给GPS更多时间）
          maximumAge: 0, // 不使用缓存，强制获取最新位置
        }
      );
    } else {
      console.warn('浏览器不支持地理定位，使用默认位置（北京）');
    }
  } catch (error) {
    console.error('地图初始化失败:', error);
    message.error('地图加载失败，请稍后重试');
  }
};

// 检查地图是否需要重新初始化
const checkAndInitMap = async () => {
  // 检查是否在首页（currentComponent 为 null）
  if (currentComponent.value !== null) {
    return;
  }

  // 检查地图容器是否存在
  const container = document.getElementById('tencent-map-container');
  if (!container) {
    console.log('地图容器不存在，等待 DOM 渲染...');
    // 延迟重试
    setTimeout(() => {
      checkAndInitMap();
    }, 500);
    return;
  }

  // 检查容器是否可见且有大小
  const containerRect = container.getBoundingClientRect();
  if (containerRect.width === 0 || containerRect.height === 0) {
    console.log('地图容器大小为0，等待容器渲染...');
    // 延迟重试
    setTimeout(() => {
      checkAndInitMap();
    }, 500);
    return;
  }

  // 检查地图是否已初始化
  if (mapInstance) {
    // 更严格地检查地图实例是否有效
    try {
      // 检查地图实例是否有有效的方法
      if (typeof mapInstance.getCenter !== 'function') {
        console.warn('地图实例方法无效，重新初始化');
        mapInstance = null;
      } else {
        // 尝试获取中心点
        const center = mapInstance.getCenter();
        if (center && center.lat && center.lng) {
          // 检查地图容器内是否有瓦片元素（更严格的检查）
          const tiles = container.querySelectorAll('.leaflet-tile-container img');
          if (tiles.length === 0) {
            console.warn('地图已初始化但瓦片未加载，强制重新初始化');
            // 清除旧实例
            try {
              mapInstance.remove();
            } catch (e) {
              console.warn('清除旧地图实例失败:', e);
            }
            mapInstance = null;
          } else {
            console.log('地图已初始化且瓦片正常，仅更新大小');
            // 即使地图已初始化，也触发一次无效化检查，确保地图正常显示
            mapInstance.invalidateSize();
            // 强制刷新地图
            setTimeout(() => {
              if (mapInstance) {
                mapInstance.invalidateSize();
                // 尝试重新加载瓦片
                mapInstance.eachLayer((layer: any) => {
                  if (layer && typeof layer.redraw === 'function') {
                    try {
                      layer.redraw();
                    } catch (e) {
                      console.warn('重绘图层失败:', e);
                    }
                  }
                });
              }
            }, 100);
            return;
          }
        } else {
          console.warn('地图中心点无效，重新初始化');
          mapInstance = null;
        }
      }
    } catch (error) {
      console.warn('地图实例检查失败，重新初始化:', error);
      // 清除旧实例
      try {
        if (mapInstance) {
          mapInstance.remove();
        }
      } catch (e) {
        console.warn('清除旧地图实例失败:', e);
      }
      mapInstance = null;
    }
  }

  // 地图未初始化或已失效，重新初始化
  console.log('检测到需要初始化地图，开始初始化...');
  await nextTick(); // 等待 DOM 更新
  setTimeout(() => {
    initMap();
  }, 300); // 延迟一点确保容器完全渲染
};

// 定位到当前位置（实时获取最新位置）
const locateToCurrentPosition = () => {
  if (!navigator.geolocation) {
    message.error('您的浏览器不支持地理定位功能');
    return;
  }

  mapLocating.value = true;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { longitude, latitude, accuracy } = position.coords;
      console.log(`获取到实时位置 - 经度: ${longitude}, 纬度: ${latitude}, 精度: ${accuracy}米`);

      if (mapInstance) {
        // Leaflet 使用 [纬度, 经度] 格式
        const center: [number, number] = [latitude, longitude];

        // 清除之前的标记点
        markers.forEach((marker) => {
          mapInstance.removeLayer(marker);
        });
        markers = [];

        // 确保地图大小正确（重要：解决白屏问题）
        mapInstance.invalidateSize();

        // 移动到当前位置
        mapInstance.setView(center, 15); // 设置合适的缩放级别

        // 再次确保地图大小正确（定位后）
        setTimeout(() => {
          if (mapInstance) {
            mapInstance.invalidateSize();
            console.log('手动定位后地图大小已重新计算');
          }
        }, 200);

        // 添加当前位置标记点（带精度圆圈）
        const marker = window.L.marker(center).addTo(mapInstance);
        marker
          .bindPopup(
            `当前位置<br>经度: ${longitude.toFixed(6)}<br>纬度: ${latitude.toFixed(6)}<br>精度: ${Math.round(accuracy)}米`
          )
          .openPopup();
        markers.push(marker);

        // 如果有精度信息且精度合理（小于50公里），添加精度圆圈
        if (accuracy && accuracy < 50000) {
          const circle = window.L.circle(center, {
            radius: accuracy,
            color: '#3b82f6',
            fillColor: '#3b82f6',
            fillOpacity: 0.1,
          }).addTo(mapInstance);
          markers.push(circle as any);
          message.success(`定位成功（精度: ${Math.round(accuracy)}米）`);
        } else if (accuracy && accuracy >= 50000) {
          message.warning(
            `定位成功，但精度较低（${Math.round(accuracy / 1000)}公里），建议在室外使用GPS定位`
          );
        } else {
          message.success('定位成功');
        }
      } else {
        message.error('地图未初始化');
      }

      mapLocating.value = false;
    },
    (error) => {
      console.error('定位失败:', error);
      let errorMsg = '无法获取当前位置';
      if (error.code === 1) {
        errorMsg = '定位被拒绝，请允许浏览器访问位置信息';
      } else if (error.code === 2) {
        errorMsg = '定位失败，位置信息不可用';
      } else if (error.code === 3) {
        errorMsg = '定位超时，请稍后重试';
      }
      message.error(errorMsg);
      mapLocating.value = false;
    },
    {
      enableHighAccuracy: true, // 高精度定位（使用GPS）
      timeout: 20000, // 超时时间 20 秒（给GPS更多时间）
      maximumAge: 0, // 不使用缓存，强制获取最新位置
    }
  );
};

// 搜索位置并定位
const searchLocation = async () => {
  const query = mapSearchQuery.value.trim();
  if (!query) {
    message.warning('请输入要搜索的地址或地点名称');
    return;
  }

  if (!mapInstance) {
    message.error('地图未初始化');
    return;
  }

  mapSearching.value = true;

  try {
    // 使用 OpenStreetMap 的 Nominatim 地理编码服务（免费，无需 key）
    // API: https://nominatim.openstreetmap.org/search
    const apiUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;

    console.log('搜索位置:', query);
    console.log('搜索URL:', apiUrl);

    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', // Nominatim 要求设置 User-Agent
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('搜索结果:', data);

    if (data && data.length > 0) {
      const result = data[0];
      const lat = parseFloat(result.lat);
      const lng = parseFloat(result.lon);
      const displayName = result.display_name;

      console.log(`找到位置: ${displayName} - 经度: ${lng}, 纬度: ${lat}`);

      // 确保地图大小正确
      mapInstance.invalidateSize();

      // 定位到搜索结果
      const center: [number, number] = [lat, lng];
      mapInstance.setView(center, 15); // 设置合适的缩放级别

      // 再次确保地图大小正确（搜索后）
      setTimeout(() => {
        if (mapInstance) {
          mapInstance.invalidateSize();
        }
      }, 200);

      // 清除之前的标记点
      markers.forEach((marker) => {
        mapInstance.removeLayer(marker);
      });
      markers = [];

      // 添加搜索结果标记点
      const marker = window.L.marker(center).addTo(mapInstance);

      // 添加弹出窗口显示位置信息
      marker.bindPopup(`<b>${displayName}</b><br/>经度: ${lng}<br/>纬度: ${lat}`).openPopup();

      markers.push(marker);

      message.success(`已定位到: ${displayName}`);
    } else {
      message.warning('未找到相关位置，请尝试其他关键词');
    }
  } catch (error) {
    console.error('搜索位置失败:', error);
    message.error('搜索失败，请稍后重试');
  } finally {
    mapSearching.value = false;
  }
};

// 加载 Tesseract.js 库
const loadTesseractScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 检查是否已经加载
    if (window.Tesseract && window.Tesseract.recognize) {
      console.log('Tesseract.js 已加载');
      resolve();
      return;
    }

    console.log('开始加载 Tesseract.js...');

    // 加载 Tesseract.js（从 CDN）
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js';
    script.async = true;

    script.onload = () => {
      console.log('Tesseract.js 加载完成');
      if (window.Tesseract && window.Tesseract.recognize) {
        resolve();
      } else {
        reject(new Error('Tesseract.js 初始化失败'));
      }
    };

    script.onerror = (error) => {
      console.error('Tesseract.js 加载失败:', error);
      reject(new Error('Tesseract.js 加载失败，请检查网络连接'));
    };

    document.head.appendChild(script);
    console.log('已添加 Tesseract.js 脚本标签到页面');
  });
};

// 触发文件选择
const triggerFileInput = () => {
  if (ocrProcessing.value) return;
  fileInputRef.value?.click();
};

// 处理文件输入框变化
const handleFileInputChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    handleImageUpload(file);
    // 清空输入框，以便下次选择同一文件时也能触发 change 事件
    target.value = '';
  }
};

// 处理拖拽悬停
const handleDragOver = (event: DragEvent) => {
  if (ocrProcessing.value) return;
  event.preventDefault();
  isDragOver.value = true;
};

// 处理拖拽离开
const handleDragLeave = (event: DragEvent) => {
  if (ocrProcessing.value) return;
  event.preventDefault();
  isDragOver.value = false;
};

// 处理拖拽放下
const handleDrop = (event: DragEvent) => {
  if (ocrProcessing.value) return;
  event.preventDefault();
  isDragOver.value = false;

  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    const file = files[0];
    handleImageUpload(file);
  }
};

// 处理图片上传和 OCR 识别
const handleImageUpload = (file: File) => {
  // 检查文件类型
  const isImage = file.type.startsWith('image/');
  if (!isImage) {
    message.error('请上传图片文件');
    return;
  }

  // 检查图片大小（5MB = 5 * 1024 * 1024 字节）
  const maxSize = 5 * 1024 * 1024;
  if (file.size > maxSize) {
    message.warning('图片过大，建议压缩后再上传（建议大小不超过 5MB）');
    // 仍然允许上传，但提醒用户
  }

  // 异步处理 OCR 识别
  processOCR(file);
};

// 处理 OCR 识别
const processOCR = async (file: File) => {
  ocrProcessing.value = true;
  ocrProgress.value = 0;
  ocrProgressText.value = '初始化中...';
  ocrResult.value = '';
  ocrError.value = '';

  try {
    // 显示图片预览
    ocrProgress.value = 5;
    ocrProgressText.value = '加载图片预览...';
    const reader = new FileReader();
    reader.onload = (e) => {
      ocrImagePreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);

    // 等待图片预览加载完成
    await new Promise((resolve) => setTimeout(resolve, 100));

    // 加载 Tesseract.js
    ocrProgress.value = 15;
    ocrProgressText.value = '加载 OCR 引擎...';
    await loadTesseractScript();

    ocrProgress.value = 25;
    ocrProgressText.value = '准备识别...';
    console.log('开始 OCR 识别...');

    // 使用 Tesseract.js 进行 OCR 识别（中文简体：chi_sim）
    const {
      data: { text },
    } = await window.Tesseract.recognize(file, 'chi_sim', {
      logger: (m: any) => {
        // 更新识别进度
        if (m.status === 'loading tesseract core') {
          ocrProgress.value = 30;
          ocrProgressText.value = '加载核心引擎...';
        } else if (m.status === 'initializing tesseract') {
          ocrProgress.value = 40;
          ocrProgressText.value = '初始化引擎...';
        } else if (m.status === 'loading language traineddata') {
          ocrProgress.value = 50;
          ocrProgressText.value = '加载中文语言包...';
        } else if (m.status === 'initializing api') {
          ocrProgress.value = 60;
          ocrProgressText.value = '初始化 API...';
        } else if (m.status === 'recognizing text') {
          // 识别进度从 60% 到 95%
          const progress = Math.round(60 + m.progress * 35);
          ocrProgress.value = progress;
          ocrProgressText.value = `识别文字中... ${Math.round(m.progress * 100)}%`;
        }
      },
    });

    ocrProgress.value = 100;
    ocrProgressText.value = '识别完成';
    console.log('OCR 识别完成');

    // 短暂延迟后显示结果
    await new Promise((resolve) => setTimeout(resolve, 300));

    ocrResult.value = text.trim();

    if (ocrResult.value) {
      message.success('识别成功');
    } else {
      message.warning('未识别到文字，请确保图片中包含清晰的文字');
    }
  } catch (error: any) {
    console.error('OCR 识别失败:', error);
    ocrError.value = '识别失败，请稍后重试';
    message.error('识别失败，请稍后重试');
  } finally {
    ocrProcessing.value = false;
    ocrProgress.value = 0;
    ocrProgressText.value = '';
  }
};

// 复制 OCR 识别结果
const copyOcrResult = async () => {
  if (!ocrResult.value) {
    message.warning('没有可复制的内容');
    return;
  }

  try {
    await navigator.clipboard.writeText(ocrResult.value);
    message.success('已复制到剪贴板');
  } catch (error) {
    console.error('复制失败:', error);
    // 降级方案：使用传统方法
    const textArea = document.createElement('textarea');
    textArea.value = ocrResult.value;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      message.success('已复制到剪贴板');
    } catch (e) {
      message.error('复制失败，请手动复制');
    }
    document.body.removeChild(textArea);
  }
};

// 查询天气
const queryWeather = async () => {
  const cityName = weatherCityName.value.trim();
  if (!cityName) {
    message.warning('请输入城市名称');
    return;
  }

  // 查找城市对应的stationid
  const stationId = cityStationIdMap[cityName];
  if (!stationId) {
    message.warning(`暂不支持查询"${cityName}"的天气，请尝试其他城市（如：北京、上海、广州等）`);
    return;
  }

  weatherLoading.value = true;
  weatherData.value = null;

  try {
    // 使用代理路径，避免CORS问题
    // 在开发环境中通过Vite代理，在生产环境中需要后端代理
    const apiUrl = import.meta.env.DEV
      ? `/api/weather/view?stationid=${stationId}`
      : `https://weather.cma.cn/api/weather/view?stationid=${stationId}`;

    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        Accept: 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      },
      // 不设置mode，使用默认的cors模式
      credentials: 'omit',
    });

    if (!response.ok) {
      // 403错误可能是API的反爬虫机制
      if (response.status === 403) {
        throw new Error(
          'API访问被拒绝，可能是反爬虫机制。建议：1. 稍后重试 2. 检查网络连接 3. 使用其他天气服务'
        );
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // 解析返回的JSON数据
    // 根据中国气象局API的实际返回结构解析
    console.log('天气API返回数据:', data);

    if (data && data.code === 0) {
      const weatherInfo = data.data || {};

      // 检查数据是否为空
      if (!weatherInfo || Object.keys(weatherInfo).length === 0) {
        throw new Error('API返回的数据为空，可能是该站点暂时没有数据');
      }

      const now = weatherInfo.now || {};
      const location = weatherInfo.location || {};

      // 提取城市名称（优先使用location中的名称）
      const displayCity = location.name || cityName;

      // 提取温度信息
      let temperature = '--';
      if (now.temperature !== undefined && now.temperature !== null) {
        temperature = `${now.temperature}℃`;
      } else if (now.temp !== undefined && now.temp !== null) {
        temperature = `${now.temp}℃`;
      } else if (now.feelst !== undefined && now.feelst !== null) {
        temperature = `${now.feelst}℃`;
      }

      // 提取湿度信息
      let humidity = '--';
      if (now.humidity !== undefined && now.humidity !== null) {
        humidity = `${now.humidity}%`;
      } else if (now.rh !== undefined && now.rh !== null) {
        humidity = `${now.rh}%`;
      }

      // 提取风力信息
      let wind = '--';
      if (now.windDirection && now.windSpeed !== undefined) {
        wind = `${now.windDirection} ${now.windSpeed}级`;
      } else if (now.windDirection) {
        wind = now.windDirection;
      } else if (now.windSpeed !== undefined) {
        wind = `${now.windSpeed}级`;
      } else if (now.wind) {
        wind = now.wind;
      }

      // 提取天气状况
      let weather = '';
      if (now.weather) {
        weather = now.weather;
      } else if (now.condition) {
        weather = now.condition;
      } else if (now.text) {
        weather = now.text;
      }

      // 检查是否至少有一个有效数据
      if (temperature === '--' && humidity === '--' && wind === '--') {
        throw new Error('API返回的数据不完整，请稍后重试');
      }

      weatherData.value = {
        city: displayCity,
        temperature,
        humidity,
        wind,
        weather,
      };

      message.success('天气查询成功');
    } else {
      throw new Error('返回数据格式不正确');
    }
  } catch (error: any) {
    console.error('查询天气失败:', error);

    // 提供更详细的错误信息
    let errorMessage = '查询天气失败，请稍后重试';
    if (error.message) {
      if (error.message.includes('403') || error.message.includes('访问被拒绝')) {
        errorMessage = '天气API访问被拒绝，可能是反爬虫机制。建议稍后重试或使用其他天气服务';
      } else if (error.message.includes('CORS') || error.message.includes('跨域')) {
        errorMessage = '跨域请求失败，请检查代理配置';
      } else if (error.message.includes('网络')) {
        errorMessage = '网络连接失败，请检查网络设置';
      } else {
        errorMessage = `查询失败: ${error.message}`;
      }
    }

    message.error(errorMessage);
    weatherData.value = null;
  } finally {
    weatherLoading.value = false;
  }
};

onMounted(() => {
  applyMenuQuery();
  themeStore.loadTheme();
  themeConfig.value = { ...themeStore.theme };

  // 加载保存的布局
  const savedLayout = localStorage.getItem('dashboardLayout');
  if (savedLayout) {
    currentDashboardLayout.value = savedLayout;
  }

  // 初始化语音识别
  initSpeechRecognition();

  // 初始化语音合成
  initSpeechSynthesis();

  // 初始化地图（延迟执行，确保 DOM 已渲染，仅在首页生效）
  setTimeout(() => {
    checkAndInitMap();
  }, 500);

  // 自动检测位置并查询天气（延迟执行，避免影响页面加载）
  setTimeout(() => {
    // 检查是否已经有天气数据，如果没有则自动检测
    if (!weatherData.value) {
      autoDetectAndQueryWeather();
    }
  }, 1000);

  // 加载新闻资讯
  fetchNews();
});

// 组件卸载时清理
onUnmounted(() => {
  // 清理语音识别
  if (recognition && isListening.value) {
    try {
      recognition.stop();
    } catch (error) {
      console.error('清理语音识别失败:', error);
    }
  }

  // 清理语音合成
  if (synthesis && isSpeaking.value) {
    try {
      synthesis.cancel();
    } catch (error) {
      console.error('清理语音合成失败:', error);
    }
  }
});

watch(
  () => route.query.menu,
  () => {
    applyMenuQuery();
  }
);

// 监听 currentComponent 变化，当回到首页时重新初始化地图
watch(
  () => currentComponent.value,
  (newVal, oldVal) => {
    // 当从其他组件返回到首页（currentComponent 变为 null）时
    if (newVal === null && oldVal !== null) {
      console.log('检测到返回首页，检查地图初始化状态...');
      // 延迟一点确保 DOM 已更新
      setTimeout(() => {
        checkAndInitMap();
      }, 300);
    }
  },
  { immediate: false }
);

// 使用 onActivated 生命周期钩子（如果使用了 keep-alive）
onActivated(() => {
  console.log('组件激活，检查地图初始化状态...');
  // 延迟一点确保 DOM 已更新
  setTimeout(() => {
    checkAndInitMap();
  }, 300);
});

// 菜单点击处理
const handleMenuClick = ({ key }: { key: string }) => {
  console.log('🎯 菜单点击事件触发, key:', key);
  console.log('🔧 componentMap 包含的key:', Object.keys(componentMap));
  selectedKeys.value = [key];

  let actualKey = key;
  if (key.startsWith('item-')) {
    actualKey = key.replace('item-', '');
  } else if (key.startsWith('sub-')) {
    actualKey = key.replace('sub-', '');
  }

  console.log('🔧 解析后的实际key:', actualKey);

  if (actualKey === 'dashboard') {
    console.log('🚀 跳转到仪表盘');
    currentComponent.value = null;
    router.push({ path: '/dashboard' });
  } else if (componentMap[actualKey]) {
    console.log('🚀 跳转到组件:', actualKey);
    currentComponent.value = componentMap[actualKey];
    router.push({ path: '/dashboard', query: { menu: actualKey } });
  } else if (componentMap[key]) {
    console.log('🚀 跳转到组件(原始key):', key);
    currentComponent.value = componentMap[key];
    router.push({ path: '/dashboard', query: { menu: key } });
  } else {
    console.log('❌ 未找到组件:', actualKey, '原始key:', key);
  }
};

// 用户菜单点击处理
const handleUserMenuClick = ({ key }: { key: string }) => {
  switch (key) {
    case 'profile':
      selectedKeys.value = ['profile'];
      if (componentMap['profile']) {
        currentComponent.value = componentMap['profile'];
        router.push({ path: '/dashboard', query: { menu: 'profile' } });
      } else {
        console.error('Profile component not found in componentMap:', Object.keys(componentMap));
        message.error('个人信息组件未找到，请刷新页面重试');
      }
      break;
    case 'settings':
      selectedKeys.value = ['settings'];
      if (componentMap['settings']) {
        currentComponent.value = componentMap['settings'];
        router.push({ path: '/dashboard', query: { menu: 'settings' } });
      }
      break;
    case 'logout':
      handleLogout();
      break;
  }
};

// 登出处理
const handleLogout = () => {
  Modal.confirm({
    title: '确认退出',
    content: '您确定要退出登录吗？',
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        // 调用后端登出接口
        await logoutUser();
        // 清除用户信息
        userStore.clearAuth();
        // 跳转到登录页
        await router.push('/login');
        message.success('退出登录成功');
      } catch (error) {
        console.error('退出登录失败:', error);
        // 即使后端接口失败，也要清除本地数据
        userStore.clearAuth();
        await router.push('/login');
        message.error('退出登录失败，但已清除本地数据');
      }
    },
  });
};

// 获取用户信息
// const fetchUserInfo = async () => {
//   try {
//     const response = await userApi.getUserInfo()
//     if (response.success) {
//       userInfo.value = response.data
//     }
//   } catch (error) {
//     console.error('获取用户信息失败:', error)
//     message.error('获取用户信息失败')
//   }
// }

// 组件挂载时初始化
// onMounted(() => {
//   selectedKeys.value = ['dashboard']
//   currentComponent.value = null
//   fetchUserInfo()
// })
</script>

<style scoped lang="scss">
// 确保菜单可点击的全局重置
.user-layout {
  min-height: 100vh;
  background: #0f172a;
  position: relative;
  z-index: 1;
  width: 100%;
  overflow-x: hidden;
}

// 确保所有元素都不会阻止菜单点击（仅针对菜单相关元素）
:deep(.top-menu *),
:deep(.ant-menu-item *),
:deep(.ant-menu-submenu *) {
  &::before,
  &::after {
    pointer-events: auto;
  }
}

// 专门针对菜单的保护
:deep(.top-menu *) {
  pointer-events: auto !important;
  cursor: pointer !important;
}

.main-layout {
  min-height: calc(100vh - 68px);
  position: relative;
  z-index: 1;
  pointer-events: auto;
  animation: mainFadeIn 0.5s ease-out;
}

@keyframes mainFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.user-content {
  position: relative;
  z-index: 1;
  pointer-events: auto;
}

.user-header {
  background: #1e293b;
  color: #e2e8f0;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  position: relative !important;
  top: 0;
  z-index: 99999;
  height: 64px;
  border-bottom: 1px solid #334155;
  pointer-events: auto !important;

  &::before,
  &::after {
    content: none !important;
  }

  .header-left {
    display: flex;
    align-items: center;
    flex: 1;
    position: relative;
    z-index: 99999;
    pointer-events: auto !important;

    &::before,
    &::after {
      content: none !important;
    }

    .logo {
      display: flex;
      align-items: center;
      margin-right: 32px;

      .logo-img {
        width: 32px;
        height: 32px;
      }

      .logo-text {
        margin-left: 12px;
        color: #60a5fa;
        font-size: 18px;
        font-weight: 600;
      }
    }

    .top-menu {
      flex: 1;
      border-bottom: none;
      line-height: 62px;
      background: transparent;
      position: relative;
      z-index: 999999;
      pointer-events: auto !important;
      overflow-x: auto;
      white-space: nowrap;

      &::-webkit-scrollbar {
        height: 4px;
      }

      &::-webkit-scrollbar-track {
        background: #1e293b;
      }

      &::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 2px;
      }

      &::-webkit-scrollbar-thumb:hover {
        background: #64748b;
      }

      &::before,
      &::after {
        content: none !important;
      }

      :deep(.ant-menu) {
        background: transparent;
        position: relative;
        z-index: 999999;
        pointer-events: auto !important;
        width: auto;
        min-width: 100%;

        &::before,
        &::after {
          content: none !important;
        }
      }

      :deep(.ant-menu-item),
      :deep(.ant-menu-submenu) {
        border-bottom: 2px solid transparent;
        color: #cbd5e1;
        position: relative;
        z-index: 999999;
        pointer-events: auto !important;
        cursor: pointer !important;
        margin: 0 4px;
        transition: all 0.2s ease;

        &::before,
        &::after {
          content: none !important;
        }

        &:hover {
          color: #60a5fa;
          background: rgba(96, 165, 250, 0.08);
        }

        &.ant-menu-item-selected {
          color: #60a5fa;
          border-bottom-color: #60a5fa;
          background: rgba(96, 165, 250, 0.12);
        }
      }

      :deep(.ant-menu-submenu-selected) {
        color: #60a5fa;
        border-bottom-color: #60a5fa;
      }

      :deep(.ant-menu-item > span),
      :deep(.ant-menu-submenu-title > span) {
        pointer-events: auto !important;
        cursor: pointer !important;
      }

      :deep(.ant-menu-item > *),
      :deep(.ant-menu-submenu-title > *) {
        pointer-events: auto !important;
        cursor: pointer !important;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .breadcrumb {
      margin: 0;

      :deep(.ant-breadcrumb-link) {
        color: #90e0ef;
      }

      :deep(.ant-breadcrumb-separator) {
        color: rgba(0, 212, 255, 0.3);
      }
    }

    .header-item {
      display: flex;
      align-items: center;
    }

    .theme-btn {
      color: #90e0ef;

      &:hover {
        background: rgba(0, 212, 255, 0.1);
        color: #00d4ff;
      }
    }

    .user-info-btn {
      display: flex;
      align-items: center;
      gap: 10px;
      height: auto;
      padding: 6px 14px;
      background: rgba(100, 255, 218, 0.06);
      border: 1px solid rgba(100, 255, 218, 0.2);
      border-radius: 24px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        background: rgba(100, 255, 218, 0.12);
        border-color: rgba(100, 255, 218, 0.4);
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.15);
        transform: translateY(-2px);
      }

      .username {
        font-size: 14px;
        color: #caf0f8;
        font-weight: 500;
      }
    }
  }
}

// 主题编辑器样式
.theme-editor {
  .theme-section {
    margin-bottom: 32px;

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #111827;
      margin: 0 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .preset-themes {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }

    .preset-theme-card {
      cursor: pointer;
      border: 2px solid #e5e7eb;
      border-radius: 8px;
      padding: 8px;
      transition: all 0.2s ease;

      &:hover {
        border-color: #2563eb;
        transform: translateY(-2px);
      }

      &.active {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
      }

      .preset-preview {
        width: 100%;
        height: 80px;
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 8px;

        .preview-header {
          height: 20px;
          width: 100%;
        }

        .preview-content {
          padding: 8px;
          height: 60px;

          .preview-card {
            height: 40px;
            border-radius: 4px;
            border: 1px solid;
          }
        }
      }

      .preset-name {
        font-size: 13px;
        font-weight: 500;
        color: #111827;
        text-align: center;
      }
    }

    .custom-editor {
      margin-top: 16px;
    }

    .color-group {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .color-item {
      display: flex;
      flex-direction: column;
      gap: 8px;

      label {
        font-size: 13px;
        color: #6b7280;
        font-weight: 500;
      }

      .color-picker-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;

        .color-input {
          width: 60px;
          height: 36px;
          border: 1px solid #e5e7eb;
          border-radius: 6px;
          cursor: pointer;
          padding: 2px;
          background: transparent;

          &::-webkit-color-swatch-wrapper {
            padding: 0;
          }

          &::-webkit-color-swatch {
            border: none;
            border-radius: 4px;
          }

          &:hover {
            border-color: #3b82f6;
          }
        }

        .color-text-input {
          flex: 1;
          font-family: 'Monaco', 'Menlo', monospace;
          font-size: 13px;
        }
      }
    }
  }

  .theme-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #e5e7eb;
    position: sticky;
    bottom: 0;
    background: white;
    z-index: 10;
  }
}

// 布局编辑器样式
.layout-editor {
  // 布局类型导航栏
  .layout-type-selector {
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;

    .select-nav-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .nav-icon {
        font-size: 16px;
        color: #6b7280;
      }

      span {
        font-size: 14px;
        font-weight: 500;
        color: #111827;
      }
    }

    :deep(.ant-select-selector) {
      border-radius: 8px;
      border: 1px solid #e5e7eb;

      &:hover {
        border-color: #2563eb;
      }
    }

    :deep(.ant-select-focused .ant-select-selector) {
      border-color: #2563eb;
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    :deep(.ant-select-selection-item) {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 500;
      color: #111827;
    }
  }

  .layout-section {
    margin-bottom: 32px;

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #111827;
      margin: 0 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid #e5e7eb;
    }

    .layout-options {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .layout-option-card {
      cursor: pointer;
      border: 2px solid #e5e7eb;
      border-radius: 12px;
      padding: 16px;
      transition: all 0.2s ease;

      &:hover {
        border-color: #2563eb;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }

      &.active {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        background: #f0f7ff;
      }

      .layout-preview {
        width: 100%;
        height: 120px;
        border-radius: 8px;
        background: #f8fafc;
        padding: 8px;
        margin-bottom: 12px;

        .preview-stats {
          display: flex;
          gap: 6px;
          margin-bottom: 8px;

          .preview-stat {
            height: 24px;
            background: #dbeafe;
            border-radius: 4px;
            flex: 1;
          }

          &.stats-4col {
            .preview-stat {
              flex: 1;
            }
          }

          &.stats-vertical {
            flex-direction: column;
            height: auto;

            .preview-stat {
              width: 100%;
              height: 18px;
              margin-bottom: 4px;

              &:last-child {
                margin-bottom: 0;
              }
            }
          }

          &.stats-wide {
            .preview-stat {
              flex: 1;
              height: 32px;
            }
          }
        }

        .preview-content {
          display: flex;
          gap: 6px;
          height: 60px;

          .preview-main {
            background: #dbeafe;
            border-radius: 4px;
            flex: 2;
          }

          .preview-side {
            background: #e0e7ff;
            border-radius: 4px;
            flex: 1;
          }

          &.content-split {
            // 左右分栏（已通过 flex 实现）
          }

          &.content-stack {
            flex-direction: column;

            .preview-main,
            .preview-side {
              flex: 1;
            }
          }

          &.content-wide {
            // 宽屏布局：主内容更宽
            .preview-main {
              flex: 5;
            }

            .preview-side {
              flex: 1;
            }
          }
        }

        // 检测历史预览样式
        &.yolo-preview {
          height: 140px;

          // 经典两列布局
          &.layout-classic {
            display: flex;
            gap: 6px;

            .preview-upload-left {
              flex: 1;
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              height: 100%;
            }

            .preview-result-right {
              flex: 1;
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              border-radius: 4px;
              height: 100%;
            }
          }

          // 上下布局
          &.layout-vertical {
            display: flex;
            flex-direction: column;
            gap: 6px;

            .preview-upload-top {
              flex: 1;
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              height: 45%;
            }

            .preview-result-bottom {
              flex: 1;
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              border-radius: 4px;
              height: 45%;
            }
          }

          // 侧边栏详情布局
          &.layout-grid {
            display: flex;
            gap: 6px;

            .preview-sidebar-left {
              flex: 0 0 35%;
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              height: 100%;
              position: relative;

              &::after {
                content: '';
                position: absolute;
                top: 8px;
                left: 8px;
                right: 8px;
                bottom: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
              }
            }

            .preview-sidebar-right {
              flex: 1;
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              border-radius: 4px;
              height: 100%;
              position: relative;

              &::before {
                content: '';
                position: absolute;
                top: 8px;
                left: 8px;
                right: 8px;
                height: 45%;
                background: rgba(255, 255, 255, 0.15);
                border-radius: 2px;
              }

              &::after {
                content: '';
                position: absolute;
                bottom: 8px;
                left: 8px;
                right: 8px;
                height: 45%;
                background: rgba(255, 255, 255, 0.15);
                border-radius: 2px;
              }
            }
          }
        }

        &.history-preview {
          height: 140px;

          // 网格布局
          &.layout-default {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;

            .preview-card-item {
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              display: flex;
              flex-direction: column;
              padding: 4px;
              gap: 3px;

              &::before {
                content: '';
                flex: 1;
                background: rgba(255, 255, 255, 0.25);
                border-radius: 2px;
              }

              &::after {
                content: '';
                height: 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
              }
            }
          }

          // 列表布局
          &.layout-list {
            display: flex;
            flex-direction: column;
            gap: 4px;

            .preview-list-item {
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              height: 28px;
              display: flex;
              align-items: center;
              padding: 0 4px;
              gap: 4px;

              &::before {
                content: '';
                width: 20px;
                height: 20px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
              }

              &::after {
                content: '';
                flex: 1;
                height: 12px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
              }
            }
          }

          // 卡片流布局
          &.layout-flow {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 4px;

            .preview-flow-item {
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              padding: 4px;
              display: flex;
              flex-direction: column;
              gap: 3px;

              &:nth-child(1),
              &:nth-child(4) {
                grid-row: span 2;
              }

              &::before {
                content: '';
                flex: 1;
                background: rgba(255, 255, 255, 0.25);
                border-radius: 2px;
              }

              &::after {
                content: '';
                height: 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
              }
            }
          }
        }

        // 告警中心布局预览
        &.alert-preview {
          height: 140px;

          // 表格布局
          &.layout-table {
            display: flex;
            flex-direction: column;
            gap: 3px;
            padding: 4px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 4px;

            .preview-table-header {
              height: 16px;
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 3px;
              display: flex;
              gap: 4px;
              padding: 2px 4px;

              &::before,
              &::after {
                content: '';
                flex: 1;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
              }
            }

            .preview-table-row {
              height: 12px;
              background: rgba(59, 130, 246, 0.1);
              border-radius: 2px;
              display: flex;
              gap: 4px;
              padding: 2px 4px;

              &::before {
                content: '';
                width: 20px;
                background: rgba(59, 130, 246, 0.3);
                border-radius: 2px;
              }

              &::after {
                content: '';
                flex: 1;
                background: rgba(59, 130, 246, 0.2);
                border-radius: 2px;
              }
            }
          }

          // 卡片布局
          &.layout-card {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
            padding: 4px;

            .preview-card-item {
              background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
              border-radius: 4px;
              padding: 4px;
              display: flex;
              flex-direction: column;
              gap: 3px;

              &::before {
                content: '';
                height: 8px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
              }

              &::after {
                content: '';
                height: 6px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
              }
            }
          }

          // 时间线布局
          &.layout-timeline {
            display: flex;
            flex-direction: column;
            gap: 4px;
            padding: 4px;
            position: relative;

            &::before {
              content: '';
              position: absolute;
              left: 8px;
              top: 0;
              bottom: 0;
              width: 2px;
              background: linear-gradient(180deg, #3b82f6 0%, #8b5cf6 100%);
              border-radius: 1px;
            }

            .preview-timeline-item {
              background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
              border-radius: 4px;
              padding: 4px;
              margin-left: 16px;
              display: flex;
              flex-direction: column;
              gap: 3px;
              position: relative;

              &::before {
                content: '';
                position: absolute;
                left: -12px;
                top: 50%;
                transform: translateY(-50%);
                width: 8px;
                height: 8px;
                background: #3b82f6;
                border-radius: 50%;
                border: 2px solid white;
              }

              &::after {
                content: '';
                height: 6px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
              }
            }
          }
        }

        // 系统监控预览样式
        &.monitor-preview {
          height: 140px;

          .preview-overview {
            display: flex;
            gap: 4px;
            margin-bottom: 8px;
            height: 40px;

            .preview-card {
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              flex: 1;
              height: 40px;
            }

            &.overview-3col {
              .preview-card {
                flex: 1;
              }
            }

            &.overview-2col {
              .preview-card {
                flex: 1;

                &:nth-child(3) {
                  display: none;
                }
              }
            }

            &.overview-4col {
              .preview-card {
                flex: 1;
              }
            }
          }

          .preview-detail {
            display: flex;
            gap: 6px;
            height: 60px;

            .preview-main-detail {
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              border-radius: 4px;
              flex: 1;
              height: 60px;
            }

            .preview-side-detail {
              background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
              border-radius: 4px;
              flex: 1;
              height: 60px;
            }

            &.detail-2col {
              // 2列布局
            }

            &.detail-full {
              .preview-side-detail {
                display: none;
              }

              .preview-main-detail {
                width: 100%;
              }
            }

            &.detail-side {
              // 并排布局
            }
          }
        }

        // AI助手预览样式
        &.chat-preview {
          height: 140px;

          // 标准布局：左右分栏
          &.layout-default {
            display: flex;
            gap: 6px;

            .preview-chat-sidebar {
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              display: flex;
              flex-direction: column;
              padding: 4px;
              flex: 0.41;

              .preview-sidebar-header {
                height: 12px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
                margin-bottom: 4px;
              }

              .preview-sidebar-item {
                height: 8px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
                margin-bottom: 2px;

                &:last-child {
                  margin-bottom: 0;
                }
              }
            }

            .preview-chat-main {
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              border-radius: 4px;
              display: flex;
              flex-direction: column;
              padding: 4px;
              gap: 3px;
              flex: 2.43;

              .preview-chat-header {
                height: 12px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
              }

              .preview-chat-message {
                height: 10px;
                border-radius: 2px;

                &.user-msg {
                  background: rgba(255, 255, 255, 0.4);
                  align-self: flex-end;
                  width: 60%;
                }

                &.ai-msg {
                  background: rgba(255, 255, 255, 0.2);
                  align-self: flex-start;
                  width: 70%;
                }
              }

              .preview-chat-input {
                height: 10px;
                background: rgba(255, 255, 255, 0.25);
                border-radius: 2px;
                margin-top: auto;
              }
            }
          }

          // 上下分割布局
          &.layout-compact {
            display: flex;
            flex-direction: column;
            gap: 6px;

            .preview-chat-sidebar {
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              border-radius: 4px;
              padding: 4px;
              height: 40px;
              display: flex;
              gap: 4px;

              .preview-sidebar-header {
                width: 60px;
                height: 100%;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
              }

              .preview-sidebar-item {
                flex: 1;
                height: 100%;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
              }
            }

            .preview-chat-main {
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              border-radius: 4px;
              flex: 1;
              padding: 4px;
              display: flex;
              flex-direction: column;
              gap: 3px;

              .preview-chat-header {
                height: 12px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 2px;
              }

              .preview-chat-message {
                height: 10px;
                border-radius: 2px;

                &.user-msg {
                  background: rgba(255, 255, 255, 0.4);
                  align-self: flex-end;
                  width: 60%;
                }

                &.ai-msg {
                  background: rgba(255, 255, 255, 0.2);
                  align-self: flex-start;
                  width: 70%;
                }
              }

              .preview-chat-input {
                height: 10px;
                background: rgba(255, 255, 255, 0.25);
                border-radius: 2px;
                margin-top: auto;
              }
            }
          }

          // 全屏消息布局
          &.layout-wide {
            position: relative;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 4px;
            padding: 4px;
            display: flex;
            flex-direction: column;
            gap: 3px;

            .preview-chat-sidebar {
              position: absolute;
              left: 4px;
              top: 4px;
              width: 40px;
              height: 40px;
              background: rgba(59, 130, 246, 0.8);
              border-radius: 4px;
              display: flex;
              align-items: center;
              justify-content: center;

              &::before {
                content: '';
                width: 20px;
                height: 20px;
                background: rgba(255, 255, 255, 0.6);
                border-radius: 2px;
              }
            }

            .preview-chat-header {
              height: 12px;
              background: rgba(255, 255, 255, 0.3);
              border-radius: 2px;
              margin-top: 8px;
            }

            .preview-chat-message {
              height: 10px;
              border-radius: 2px;

              &.user-msg {
                background: rgba(255, 255, 255, 0.4);
                align-self: flex-end;
                width: 60%;
              }

              &.ai-msg {
                background: rgba(255, 255, 255, 0.2);
                align-self: flex-start;
                width: 70%;
              }
            }

            .preview-chat-input {
              height: 10px;
              background: rgba(255, 255, 255, 0.25);
              border-radius: 2px;
              margin-top: auto;
            }
          }
        }
      }

      .layout-name {
        font-size: 15px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 4px;
      }

      .layout-desc {
        font-size: 12px;
        color: #6b7280;
      }
    }
  }

  .layout-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #e5e7eb;
    position: sticky;
    bottom: 0;
    background: white;
    z-index: 10;
  }
}

.user-content {
  margin: 0;
  padding: 0;
  min-height: calc(100vh - 64px);
  width: 100%;
  position: relative;

  .content-wrapper {
    background: transparent;
    border-radius: 0;
    min-height: 100%;
    width: 100%;
    position: relative;
    z-index: 1;
  }

  .dashboard-content {
    padding: 28px 32px;
    background: transparent;
    min-height: 100%;
    width: 100%;
    box-sizing: border-box;
    position: relative;
    z-index: 1;
  }

  // 欢迎横幅 - 现代科技风格
  .welcome-banner {
    background: 
      linear-gradient(135deg, rgba(100, 255, 218, 0.08) 0%, rgba(59, 130, 246, 0.05) 50%, rgba(17, 34, 64, 0.98) 100%);
    border-radius: 24px;
    padding: 36px 40px;
    margin-bottom: 32px;
    border: 1px solid rgba(100, 255, 218, 0.25);
    box-shadow: 
      0 0 40px rgba(100, 255, 218, 0.1),
      0 0 80px rgba(59, 130, 246, 0.05),
      0 20px 60px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);

    &::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: conic-gradient(
        from 0deg,
        transparent 0deg,
        rgba(100, 255, 218, 0.03) 90deg,
        transparent 180deg,
        rgba(59, 130, 246, 0.03) 270deg,
        transparent 360deg
      );
      animation: rotateGlow 20s linear infinite;
      z-index: 0;
      pointer-events: none;
    }

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent, #64ffda, #3b82f6, transparent);
      z-index: 1;
      pointer-events: none;
    }

    .banner-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      z-index: 2;

      .banner-left {
        display: flex;
        align-items: center;
        flex: 1;

        .user-greeting {
          .greeting-title {
            font-size: 36px;
            font-weight: 800;
            margin: 0 0 8px 0;
            background: linear-gradient(135deg, #ccd6f6 0%, #64ffda 50%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.5px;
            text-shadow: 0 0 40px rgba(100, 255, 218, 0.3);
            animation: titleGlow 3s ease-in-out infinite alternate;
          }

          .greeting-subtitle {
            font-size: 16px;
            margin: 0;
            color: #a8b2d1;
            font-weight: 500;
            letter-spacing: 0.5px;
            opacity: 0.9;
          }
        }
      }

      .banner-right {
        display: flex;
        align-items: center;
        gap: 16px;

        .banner-decor {
          width: 80px;
          height: 80px;
          border-radius: 20px;
          background: 
            linear-gradient(135deg, rgba(100, 255, 218, 0.15) 0%, rgba(59, 130, 246, 0.12) 100%);
          border: 1px solid rgba(100, 255, 218, 0.35);
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 
            0 0 30px rgba(100, 255, 218, 0.2),
            inset 0 0 20px rgba(100, 255, 218, 0.05);
          animation: floatDecor 4s ease-in-out infinite;

          .decor-icon {
            font-size: 36px;
            color: #64ffda;
            filter: drop-shadow(0 0 10px rgba(100, 255, 218, 0.5));
          }
        }
      }
    }
  }

  @keyframes rotateGlow {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  @keyframes titleGlow {
    from {
      filter: brightness(1) drop-shadow(0 0 20px rgba(100, 255, 218, 0.3));
    }
    to {
      filter: brightness(1.1) drop-shadow(0 0 40px rgba(100, 255, 218, 0.6));
    }
  }

  @keyframes floatDecor {
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-8px);
    }
  }

  .dashboard-content {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.6s ease-out;
}

@keyframes contentFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 欢迎横幅优化 - 护眼配色
.welcome-banner {
  padding: 24px;
  margin-bottom: 24px;
  background: rgba(15, 30, 60, 0.55);
  border: 1px solid rgba(100, 180, 255, 0.12);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 4px 24px rgba(0, 10, 30, 0.25);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(100, 200, 255, 0.06) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(120, 160, 255, 0.05) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }
}

  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  @keyframes float {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-20px, 20px); }
  }

  @keyframes titleGlow {
    0%, 100% { filter: drop-shadow(0 0 20px rgba(100, 255, 218, 0.3)); }
    50% { filter: drop-shadow(0 0 30px rgba(100, 255, 218, 0.5)); }
  }

  @keyframes iconPulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.9; }
  }

  @keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  // 功能模块区域
  .features-section {
    margin-bottom: 24px;

    .features-title {
      font-size: 20px;
      font-weight: 600;
      color: #ccd6f6;
      margin: 0 0 16px 0;
      letter-spacing: -0.2px;
    }

    .features-grid {
      .weather-section,
      .news-section,
      .translation-section,
      .map-section,
      .ocr-section,
      .speech-recognition-section,
      .speech-synthesis-section {
        margin-bottom: 0;
        height: 100%;
        display: flex;
        flex-direction: column;

        .section-title {
          font-size: 15px;
          font-weight: 600;
          color: #a8b2d1;
          margin: 0 0 12px 0;
          letter-spacing: -0.1px;
        }

        .weather-card,
        .news-card,
        .translation-card,
        .map-card,
        .ocr-card,
        .speech-recognition-card,
        .speech-synthesis-card {
          height: 100%;
          min-height: 280px;
          display: flex;
          flex-direction: column;
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          border-radius: 16px;
          border: 1px solid rgba(100, 255, 218, 0.2);
          padding: 20px;
          background: 
            linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
          box-shadow: 
            0 0 20px rgba(100, 255, 218, 0.05),
            0 8px 32px rgba(0, 0, 0, 0.3);
          position: relative;
          overflow: hidden;
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #64ffda, #3b82f6, transparent);
            opacity: 0;
            transition: opacity 0.4s ease;
            z-index: 1;
            pointer-events: none;
          }

          &:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 
              0 0 40px rgba(100, 255, 218, 0.15),
              0 16px 48px rgba(0, 0, 0, 0.4);
            border-color: rgba(100, 255, 218, 0.5);

            &::before {
              opacity: 1;
            }
          }
        }
      }

      // 地图和OCR模块需要更大的高度
      .map-section,
      .ocr-section {
        .map-card,
        .ocr-card {
          min-height: 360px;
        }
      }
    }
  }

  // 统计容器
  .stats-container {
    margin-bottom: 24px;

    // 垂直列表布局
    &.stats-vertical {
      .stats-vertical-list {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .vertical-stat-card {
          display: flex;
          align-items: center;
          padding: 16px;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
          background: #ffffff;

          .stat-icon-wrapper {
            width: 48px;
            height: 48px;
            font-size: 20px;
            margin-right: 16px;
          }

          .stat-info {
            flex: 1;

            .stat-value {
              font-size: 32px;
              margin-bottom: 4px;
            }

            .stat-label {
              font-size: 13px;
            }
          }
        }
      }
    }

    // 宽屏布局：大卡片
    &.stats-wide {
      .stats-row {
        .modern-stat-card.layout-wide {
          padding: 24px;
          border-radius: 8px;
          border: 1px solid #e5e7eb;
          background: #ffffff;

          .stat-icon-wrapper {
            width: 56px;
            height: 56px;
            font-size: 24px;
          }

          .stat-info {
            .stat-value {
              font-size: 36px;
            }

            .stat-label {
              font-size: 14px;
            }
          }
        }
      }
    }
  }

  // 统计卡片行
  .stats-row {
    margin-bottom: 24px;
  }

  // 现代化统计卡片
  .modern-stat-card {
    background: 
      linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 50%, rgba(10, 25, 47, 0.98) 100%);
    border-radius: 20px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    border: 1px solid rgba(100, 255, 218, 0.2);
    box-shadow: 
      0 0 20px rgba(100, 255, 218, 0.05),
      0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: radial-gradient(ellipse at top left, rgba(100, 255, 218, 0.1), transparent 50%);
      opacity: 0;
      transition: opacity 0.4s ease;
      z-index: 0;
      pointer-events: none;
    }

    &:hover {
      transform: translateY(-6px) scale(1.02);
      border-color: rgba(100, 255, 218, 0.5);
      box-shadow: 
        0 0 40px rgba(100, 255, 218, 0.15),
        0 16px 48px rgba(0, 0, 0, 0.4);

      &::before {
        opacity: 1;
      }
    }

    .stat-icon-wrapper {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      flex-shrink: 0;
      position: relative;
      z-index: 1;
      box-shadow: 
        0 0 20px rgba(100, 255, 218, 0.1),
        inset 0 0 20px rgba(255, 255, 255, 0.05);

      &.blue {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.35) 100%);
        color: #60a5fa;
        box-shadow: 
          0 0 20px rgba(59, 130, 246, 0.2),
          inset 0 0 20px rgba(255, 255, 255, 0.05);
      }

      &.green {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.35) 100%);
        color: #34d399;
        box-shadow: 
          0 0 20px rgba(16, 185, 129, 0.2),
          inset 0 0 20px rgba(255, 255, 255, 0.05);
      }

      &.purple {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(124, 58, 237, 0.35) 100%);
        color: #a78bfa;
        box-shadow: 
          0 0 20px rgba(139, 92, 246, 0.2),
          inset 0 0 20px rgba(255, 255, 255, 0.05);
      }

      &.orange {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.35) 100%);
        color: #fbbf24;
        box-shadow: 
          0 0 20px rgba(245, 158, 11, 0.2),
          inset 0 0 20px rgba(255, 255, 255, 0.05);
      }
    }

    .stat-info {
      flex: 1;
      min-width: 0;
      position: relative;
      z-index: 1;

      .stat-value {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #ccd6f6 0%, #64ffda 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -1px;

        .stat-trend {
          font-size: 14px;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 6px;
          background: rgba(100, 255, 218, 0.1);

          &.up {
            color: #64ffda;
            background: rgba(100, 255, 218, 0.15);
          }

          &.down {
            color: #ff6b6b;
            background: rgba(255, 107, 107, 0.15);
          }
        }

        .stat-badge {
          font-size: 11px;
          font-weight: 600;
          background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
          color: white;
          padding: 3px 8px;
          border-radius: 8px;
          margin-left: 6px;
          box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
        }
      }

      .stat-label {
        font-size: 14px;
        color: #a8b2d1;
        font-weight: 500;
        letter-spacing: 0.3px;
      }
    }
  }

  // 概览区域
  .overview-section {
    margin-bottom: 24px;
  }

  // 快速访问区域
  .quick-access-section {
    margin-bottom: 32px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    // 列表样式
    &.list-style {
      .quick-access-list {
        display: flex;
        flex-direction: column;
        gap: 14px;

        .quick-access-list-item {
          display: flex;
          align-items: center;
          gap: 20px;
          padding: 20px 24px;
          background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
          border: 1px solid rgba(100, 255, 218, 0.2);
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          overflow: hidden;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 10% 20%, rgba(100, 255, 218, 0.06) 0%, transparent 50%);
            opacity: 0;
            transition: opacity 0.4s ease;
          }

          &:hover {
            border-color: rgba(100, 255, 218, 0.4);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2),
                        0 0 40px rgba(100, 255, 218, 0.08);
            transform: translateX(8px) translateY(-2px);

            &::before {
              opacity: 1;
            }
          }

          .card-icon {
            width: 56px;
            height: 56px;
            flex-shrink: 0;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.3) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #60a5fa;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            font-size: 24px;
          }

          .list-item-content {
            flex: 1;
            position: relative;
            z-index: 1;

            .card-title {
              font-size: 18px;
              font-weight: 600;
              color: #ccd6f6;
              margin: 0 0 6px 0;
              letter-spacing: -0.2px;
            }

            .card-description {
              font-size: 14px;
              color: #a8b2d1;
              margin: 0;
              line-height: 1.6;
            }
          }
        }
      }
    }

    // 宽屏布局样式
    &.grid-6col {
      .wide-card {
        padding: 24px;

        .card-icon {
          width: 56px;
          height: 56px;
          font-size: 24px;
          margin-bottom: 16px;
        }

        .card-title {
          font-size: 16px;
          margin-bottom: 8px;
        }

        .card-description {
          font-size: 13px;
          line-height: 1.5;
        }
      }
    }
  }

  // 天气查询模块
  .weather-section {
    margin-bottom: 40px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    .weather-card {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(100, 255, 218, 0.2);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15),
                  0 0 40px rgba(100, 255, 218, 0.05),
                  inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 60px rgba(100, 255, 218, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
      }

      .weather-search {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;

        .weather-input {
          flex: 1;
          border-radius: 12px;
        }

        .weather-search-btn {
          border-radius: 12px;
          font-weight: 500;
          transition: all 0.25s ease;

          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
          }
        }
      }

      .weather-display {
        padding: 24px;
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(100, 255, 218, 0.15);
        border-radius: 12px;
        color: #ccd6f6;

        .weather-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
          padding-bottom: 16px;
          border-bottom: 1px solid rgba(100, 255, 218, 0.15);

          .weather-city {
            font-size: 20px;
            font-weight: 600;
            margin: 0;
            color: #ccd6f6;
          }

          .weather-icon {
            font-size: 40px;
            color: #64ffda;

            .sun-emoji {
              font-size: 40px;
              display: inline-block;
              line-height: 1;
            }
          }
        }

        .weather-info {
          display: flex;
          flex-direction: column;
          gap: 16px;

          .weather-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;

            .weather-label {
              font-size: 14px;
              color: #a8b2d1;
              font-weight: 500;
            }

            .weather-value {
              font-size: 16px;
              font-weight: 600;
              color: #ccd6f6;

              &.temperature {
                font-size: 24px;
                color: #64ffda;
                font-weight: 700;
              }
            }
          }
        }
      }

      .weather-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        text-align: center;

        .empty-icon {
          font-size: 64px;
          color: #64ffda;
          margin-bottom: 20px;
          opacity: 0.5;
        }

        .empty-text {
          font-size: 16px;
          color: #a8b2d1;
          margin: 0;
        }
      }
    }
  }

  // 新闻资讯模块
  .news-section {
    margin-bottom: 40px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    .news-card {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(100, 255, 218, 0.2);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15),
                  0 0 40px rgba(100, 255, 218, 0.05),
                  inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 60px rgba(100, 255, 218, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
      }

      .news-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        text-align: center;

        .loading-text {
          margin-top: 16px;
          font-size: 14px;
          color: #a8b2d1;
        }
      }

      .news-list {
        display: flex;
        flex-direction: column;
        gap: 14px;

        .news-item {
          display: flex;
          align-items: center;
          gap: 18px;
          padding: 18px 20px;
          border-radius: 12px;
          border: 1px solid rgba(100, 255, 218, 0.15);
          background: rgba(30, 41, 59, 0.5);
          cursor: pointer;
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          overflow: hidden;

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 10% 20%, rgba(100, 255, 218, 0.06) 0%, transparent 50%);
            opacity: 0;
            transition: opacity 0.4s ease;
          }

          &:hover {
            background: rgba(30, 41, 59, 0.7);
            border-color: rgba(100, 255, 218, 0.4);
            transform: translateX(8px) translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2),
                        0 0 40px rgba(100, 255, 218, 0.08);

            &::before {
              opacity: 1;
            }
          }

          .news-number {
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, rgba(100, 255, 218, 0.2) 0%, rgba(59, 130, 246, 0.3) 100%);
            color: #64ffda;
            border-radius: 10px;
            font-weight: 700;
            font-size: 14px;
            flex-shrink: 0;
            box-shadow: 0 0 15px rgba(100, 255, 218, 0.2);
          }

          .news-content {
            flex: 1;
            min-width: 0;
            position: relative;
            z-index: 1;

            .news-title {
              font-size: 15px;
              font-weight: 500;
              color: #ccd6f6;
              margin-bottom: 6px;
              line-height: 1.5;
              overflow: hidden;
              text-overflow: ellipsis;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
            }

            .news-date {
              font-size: 12px;
              color: #a8b2d1;
            }
          }

          .news-arrow {
            color: #a8b2d1;
            font-size: 16px;
            flex-shrink: 0;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 1;
          }

          &:hover .news-arrow {
            color: #64ffda;
            transform: translateX(6px);
          }
        }
      }

      .news-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        text-align: center;

        .empty-icon {
          font-size: 64px;
          color: #64ffda;
          margin-bottom: 20px;
          opacity: 0.5;
        }

        .empty-text {
          font-size: 16px;
          color: #a8b2d1;
          margin: 0;
        }
      }
    }
  }

  // 翻译功能模块
  .translation-section {
    margin-bottom: 40px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    .translation-card {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(100, 255, 218, 0.2);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15),
                  0 0 40px rgba(100, 255, 218, 0.05),
                  inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 60px rgba(100, 255, 218, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
      }

      .translation-controls {
        margin-bottom: 20px;

        .translation-type-selector {
          width: 100%;
          display: flex;
          gap: 8px;

          .ant-radio-button-wrapper {
            flex: 1;
            text-align: center;
            height: 40px;
            line-height: 38px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 8px;
            transition: all 0.2s ease;

            &:hover {
              color: #3b82f6;
              border-color: #3b82f6;
            }

            &.ant-radio-button-wrapper-checked {
              background: #3b82f6;
              border-color: #3b82f6;
              color: #ffffff;

              &:hover {
                background: #2563eb;
                border-color: #2563eb;
              }
            }
          }
        }
      }

      .translation-input-area {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-bottom: 20px;

        .translation-textarea {
          width: 100%;
          font-size: 15px;
          line-height: 1.6;
          resize: vertical;
          min-height: 100px;

          &:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
          }
        }

        .translation-btn {
          align-self: flex-start;
          height: 44px;
          padding: 0 24px;
          font-size: 15px;
          font-weight: 500;
          border-radius: 8px;
          transition: all 0.2s ease;

          &:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
          }
        }
      }

      .translation-result {
        margin-top: 20px;
        padding: 20px;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(100, 255, 218, 0.15);

        .result-label {
          font-size: 14px;
          font-weight: 500;
          color: #a8b2d1;
          margin-bottom: 12px;
        }

        .result-content {
          font-size: 16px;
          line-height: 1.8;
          color: #ccd6f6;
          word-break: break-word;
          white-space: pre-wrap;
        }
      }

      .translation-error {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 20px;
        padding: 16px;
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 12px;
        color: #ff6b6b;

        .error-icon {
          font-size: 20px;
          flex-shrink: 0;
        }

        .error-text {
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
  }

  // 地图模块
  .map-section {
    margin-bottom: 40px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    .map-card {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(100, 255, 218, 0.2);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15),
                  0 0 40px rgba(100, 255, 218, 0.05),
                  inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 60px rgba(100, 255, 218, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
      }

      .map-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;

        .map-search-box {
          display: flex;
          flex: 1;
          gap: 8px;
          max-width: 400px;

          .map-search-input {
            flex: 1;
          }

          .map-search-btn {
            flex-shrink: 0;
          }
        }

        .map-locate-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
        }
      }

      .tencent-map-container {
        width: 100%;
        height: 400px;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(100, 255, 218, 0.15);
      }
    }
  }

  // OCR 文字识别模块
  .ocr-section {
    margin-bottom: 40px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    .ocr-card {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(100, 255, 218, 0.2);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15),
                  0 0 40px rgba(100, 255, 218, 0.05),
                  inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 60px rgba(100, 255, 218, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
      }

      .ocr-upload-area {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;

        .ocr-upload-drag-area {
          width: 100%;
          min-height: 200px;
          border: 2px dashed rgba(100, 255, 218, 0.3);
          border-radius: 12px;
          background: rgba(30, 41, 59, 0.3);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;

          &:hover {
            border-color: rgba(100, 255, 218, 0.6);
            background: rgba(30, 41, 59, 0.5);
          }

          &.drag-over {
            border-color: #64ffda;
            background: rgba(100, 255, 218, 0.1);
            border-style: solid;
          }

          &.processing {
            cursor: not-allowed;
            opacity: 0.7;
          }
        }

        .ocr-upload-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          padding: 40px 20px;
          width: 100%;
          height: 100%;
          user-select: none;
          pointer-events: none;

          .upload-icon {
            font-size: 56px;
            color: #64ffda;
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          }

          .upload-text {
            font-size: 16px;
            font-weight: 500;
            color: #ccd6f6;
            margin: 0;
          }

          .upload-hint {
            font-size: 13px;
            color: #a8b2d1;
            margin: 0;
          }
        }

        .ocr-upload-drag-area:hover .ocr-upload-content .upload-icon {
          transform: scale(1.1);
        }

        .ocr-hint {
          font-size: 14px;
          color: #a8b2d1;
          margin: 0;
          text-align: center;
        }
      }

      .ocr-preview {
        margin-bottom: 20px;

        .ocr-preview-title {
          font-size: 14px;
          font-weight: 500;
          color: #a8b2d1;
          margin-bottom: 12px;
        }

        .ocr-preview-image {
          max-width: 100%;
          max-height: 300px;
          border-radius: 12px;
          border: 1px solid rgba(100, 255, 218, 0.15);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          object-fit: contain;
          background: rgba(30, 41, 59, 0.3);
        }
      }

      .ocr-progress {
        margin: 20px 0;
        padding: 20px;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(100, 255, 218, 0.15);

        .ocr-progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .progress-title {
            font-size: 15px;
            font-weight: 500;
            color: #ccd6f6;
          }

          .progress-percent {
            font-size: 15px;
            font-weight: 600;
            color: #64ffda;
          }
        }

        .ocr-progress-bar {
          margin-bottom: 8px;

          :deep(.ant-progress-bg) {
            background: linear-gradient(90deg, #64ffda 0%, #3b82f6 100%);
          }
        }

        .progress-text {
          font-size: 13px;
          color: #a8b2d1;
          text-align: center;
          margin-top: 8px;
        }
      }

      .ocr-result {
        margin-top: 20px;
        padding: 20px;
        background: linear-gradient(135deg, rgba(100, 255, 218, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border-radius: 12px;
        border: 1px solid rgba(100, 255, 218, 0.3);
        box-shadow: 0 2px 8px rgba(100, 255, 218, 0.1);

        .ocr-result-title {
          font-size: 14px;
          font-weight: 600;
          color: #64ffda;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 8px;

          &::before {
            content: '';
            width: 4px;
            height: 16px;
            background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
            border-radius: 2px;
          }
        }

        .ocr-result-content {
          font-size: 16px;
          line-height: 1.8;
          color: #ccd6f6;
          word-break: break-word;
          white-space: pre-wrap;
          margin-bottom: 12px;
          padding: 16px;
          background: rgba(30, 41, 59, 0.5);
          border-radius: 8px;
          border: 1px solid rgba(100, 255, 218, 0.2);
          min-height: 60px;
        }

        .ocr-copy-btn {
          color: #64ffda;
          font-weight: 500;

          &:hover {
            color: #3b82f6;
            background: rgba(100, 255, 218, 0.1);
          }
        }
      }

      .ocr-error {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 20px;
        padding: 16px;
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 12px;
        color: #ff6b6b;

        .error-icon {
          font-size: 20px;
          flex-shrink: 0;
        }

        .error-text {
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
  }

  // 语音识别模块
  .speech-recognition-section {
    margin-bottom: 40px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    .speech-recognition-card {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(100, 255, 218, 0.2);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15),
                  0 0 40px rgba(100, 255, 218, 0.05),
                  inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 60px rgba(100, 255, 218, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
      }

      .speech-not-supported {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        text-align: center;

        .not-supported-icon {
          font-size: 64px;
          color: #64ffda;
          margin-bottom: 20px;
          opacity: 0.5;
        }

        .not-supported-text {
          font-size: 16px;
          font-weight: 500;
          color: #ccd6f6;
          margin: 0 0 8px 0;
        }

        .not-supported-hint {
          font-size: 14px;
          color: #a8b2d1;
          margin: 0;
        }
      }

      .speech-recognition-content {
        display: flex;
        flex-direction: column;
        gap: 20px;

        .speech-controls {
          display: flex;
          gap: 12px;
          align-items: center;

          .speech-btn {
            flex: 1;
            height: 48px;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.25s ease;

            &:hover {
              transform: translateY(-1px);
              box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            }
          }

          .clear-btn {
            height: 48px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 400;
            transition: all 0.25s ease;

            &:hover {
              background: rgba(100, 255, 218, 0.1);
              transform: translateY(-1px);
            }
          }
        }

        .speech-status {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background: rgba(30, 41, 59, 0.5);
          border-radius: 10px;
          border: 1px solid rgba(100, 255, 218, 0.15);

          .listening-indicator {
            display: flex;
            align-items: center;
            gap: 10px;

            .pulse-dot {
              width: 10px;
              height: 10px;
              border-radius: 50%;
              background: #64ffda;
              animation: pulse 2s infinite;
              box-shadow: 0 0 12px rgba(100, 255, 218, 0.5);
            }

            .status-text {
              font-size: 14px;
              font-weight: 500;
              color: #ccd6f6;
            }
          }

          .status-text {
            font-size: 14px;
            font-weight: 400;
            color: #a8b2d1;

            &.idle {
              color: #a8b2d1;
            }
          }
        }

        .speech-result {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 20px;
          background: rgba(30, 41, 59, 0.5);
          border-radius: 12px;
          border: 1px solid rgba(100, 255, 218, 0.15);
          min-height: 120px;

          .result-label {
            font-size: 13px;
            font-weight: 500;
            color: #a8b2d1;
            margin-bottom: 8px;
          }

          .result-text {
            font-size: 15px;
            font-weight: 400;
            color: #ccd6f6;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            min-height: 60px;
            padding: 12px;
            background: rgba(30, 41, 59, 0.3);
            border-radius: 8px;
            border: 1px solid rgba(100, 255, 218, 0.2);
            transition: all 0.2s ease;

            &.empty {
              color: #a8b2d1;
              font-style: italic;
            }

            .final-text {
              color: #ccd6f6;
            }

            .interim-text {
              color: #a8b2d1;
              opacity: 0.7;
              font-style: italic;
            }

            .empty-text {
              color: #a8b2d1;
              font-style: italic;
            }
          }
        }
      }
    }
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.5;
      transform: scale(1.1);
    }
  }

  // 语音合成模块
  .speech-synthesis-section {
    margin-bottom: 40px;

    .section-title {
      font-size: 20px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 20px 0;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 10px;

      &::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, #64ffda 0%, #3b82f6 100%);
        border-radius: 2px;
      }
    }

    .speech-synthesis-card {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 34, 64, 0.95) 100%);
      border-radius: 16px;
      padding: 24px;
      border: 1px solid rgba(100, 255, 218, 0.2);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15),
                  0 0 40px rgba(100, 255, 218, 0.05),
                  inset 0 1px 0 rgba(255, 255, 255, 0.05);
      transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 60px rgba(100, 255, 218, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: rgba(100, 255, 218, 0.4);
        transform: translateY(-2px);
      }

      .speech-not-supported {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        text-align: center;

        .not-supported-icon {
          font-size: 64px;
          color: #64ffda;
          margin-bottom: 20px;
          opacity: 0.5;
        }

        .not-supported-text {
          font-size: 16px;
          font-weight: 500;
          color: #ccd6f6;
          margin: 0 0 8px 0;
        }

        .not-supported-hint {
          font-size: 14px;
          color: #a8b2d1;
          margin: 0;
        }
      }

      .speech-synthesis-content {
        display: flex;
        flex-direction: column;
        gap: 20px;

        .synthesis-input {
          .synthesis-textarea {
            border-radius: 12px;
            border: 1px solid rgba(100, 255, 218, 0.2);
            background: rgba(30, 41, 59, 0.3);
            transition: all 0.2s ease;

            &:focus {
              border-color: #64ffda;
              box-shadow: 0 0 0 3px rgba(100, 255, 218, 0.1);
            }

            &:disabled {
              background: rgba(30, 41, 59, 0.2);
              color: #a8b2d1;
              cursor: not-allowed;
            }

            &::placeholder {
              color: #a8b2d1;
              opacity: 0.6;
            }
          }
        }

        .synthesis-settings {
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding: 16px;
          background: rgba(30, 41, 59, 0.5);
          border-radius: 12px;
          border: 1px solid rgba(100, 255, 218, 0.15);

          .setting-item {
            display: flex;
            flex-direction: column;
            gap: 8px;

            .setting-label {
              display: flex;
              justify-content: space-between;
              align-items: center;
              font-size: 14px;
              font-weight: 500;
              color: #ccd6f6;

              .setting-value {
                font-size: 13px;
                font-weight: 600;
                color: #64ffda;
                min-width: 50px;
                text-align: right;
              }
            }

            .setting-slider {
              margin: 0;

              :deep(.ant-slider-track) {
                background: linear-gradient(90deg, #64ffda 0%, #3b82f6 100%);
              }

              :deep(.ant-slider-handle) {
                border-color: #64ffda;
                box-shadow: 0 0 0 2px rgba(100, 255, 218, 0.2);

                &:hover {
                  border-color: #3b82f6;
                  box-shadow: 0 0 0 4px rgba(100, 255, 218, 0.2);
                }
              }

              :deep(.ant-slider-handle:focus) {
                border-color: #64ffda;
                box-shadow: 0 0 0 4px rgba(100, 255, 218, 0.2);
              }

              :deep(.ant-slider-dot-active) {
                border-color: #64ffda;
              }

              :deep(.ant-slider-rail) {
                background: rgba(100, 255, 218, 0.15);
              }

              &:disabled {
                :deep(.ant-slider-track),
                :deep(.ant-slider-handle) {
                  opacity: 0.5;
                  cursor: not-allowed;
                }
              }
            }
          }
        }

        .synthesis-controls {
          display: flex;
          gap: 12px;
          align-items: center;

          .synthesis-btn {
            flex: 1;
            height: 48px;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 500;
            transition: all 0.25s ease;

            &:hover:not(:disabled) {
              transform: translateY(-1px);
              box-shadow: 0 4px 12px rgba(100, 255, 218, 0.3);
            }

            &:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
          }

          .clear-btn {
            height: 48px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 400;
            transition: all 0.25s ease;

            &:hover:not(:disabled) {
              background: rgba(100, 255, 218, 0.1);
              transform: translateY(-1px);
            }

            &:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
          }
        }

        .synthesis-status {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background: rgba(30, 41, 59, 0.5);
          border-radius: 10px;
          border: 1px solid rgba(100, 255, 218, 0.15);

          .speaking-indicator {
            display: flex;
            align-items: center;
            gap: 10px;

            .pulse-dot {
              width: 10px;
              height: 10px;
              border-radius: 50%;
              background: #64ffda;
              animation: pulse 2s infinite;
              box-shadow: 0 0 12px rgba(100, 255, 218, 0.5);
            }

            .status-text {
              font-size: 14px;
              font-weight: 500;
              color: #ccd6f6;
            }
          }

          .status-text {
            font-size: 14px;
            font-weight: 400;
            color: #a8b2d1;

            &.idle {
              color: #a8b2d1;
            }
          }
        }
      }
    }
  }

  // 最近活动
  .recent-activities {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(17, 34, 64, 0.98) 100%);
    border-radius: 14px;
    padding: 20px;
    border: 1px solid rgba(100, 255, 218, 0.15);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    height: 100%;

    .section-title {
      font-size: 18px;
      font-weight: 700;
      color: #ccd6f6;
      margin: 0 0 16px 0;
      letter-spacing: -0.2px;
    }

    .activity-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .activity-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px;
      border-radius: 8px;
      transition: all 0.2s ease;
      cursor: pointer;

      &:hover {
        background: rgba(30, 41, 59, 0.6);
        transform: translateX(2px);
      }

      .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;

        &.blue {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(37, 99, 235, 0.2) 100%);
          color: #60a5fa;
        }

        &.green {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.2) 100%);
          color: #34d399;
        }

        &.purple {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(124, 58, 237, 0.2) 100%);
          color: #a78bfa;
        }

        &.orange {
          background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(217, 119, 6, 0.2) 100%);
          color: #fbbf24;
        }
      }

      .activity-content {
        flex: 1;
        min-width: 0;

        .activity-title {
          font-size: 14px;
          font-weight: 500;
          color: #ccd6f6;
          margin-bottom: 2px;
        }

        .activity-time {
          font-size: 12px;
          color: #a8b2d1;
        }
      }
    }
  }

  // 快速访问卡片 - 简洁清晰风格
  .quick-access-card {
    background: #1e3a5f;
    border-radius: 16px;
    padding: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid rgba(100, 180, 255, 0.2);
    height: 100%;
    width: 100%;
    box-sizing: border-box;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;

    &:hover {
      border-color: rgba(100, 180, 255, 0.4);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
      transform: translateY(-4px);
    }

    .card-icon {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      margin-bottom: 16px;
      position: relative;
      z-index: 1;

      &.blue {
        background: #2563eb;
        color: #ffffff;
      }

      &.green {
        background: #059669;
        color: #ffffff;
      }

      &.purple {
        background: #7c3aed;
        color: #ffffff;
      }

      &.orange {
        background: #d97706;
        color: #ffffff;
      }

      &.pink {
        background: #db2777;
        color: #ffffff;
      }

      &.cyan {
        background: #0891b2;
        color: #ffffff;
      }

      &.red {
        background: #dc2626;
        color: #ffffff;
      }

      &.indigo {
        background: #4f46e5;
        color: #ffffff;
      }
    }

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #ffffff;
      margin: 0 0 8px 0;
    }

    .card-description {
      font-size: 13px;
      color: #cbd5e1;
      margin: 0;
      line-height: 1.5;
    }
  }
}
</style>

<script lang="ts">
// Leaflet 地图类型声明
declare global {
  interface Window {
    L: any;
    Tesseract: any;
  }
}
</script>
