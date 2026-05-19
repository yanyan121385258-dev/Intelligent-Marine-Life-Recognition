<template>
  <div class="yolo-detection-page">
    <!-- 调试信息 -->
    <div v-if="false" style="background: red; color: white; padding: 10px; margin: 10px">
      调试: YOLO检测页面已加载 - {{ new Date().toLocaleTimeString() }}
    </div>

    <div class="page-header">
      <h1 class="page-title">
        <ScanOutlined class="title-icon" />
        YOLO检测中心
      </h1>
      <p class="page-description">使用AI模型进行智能图像检测</p>
    </div>

    <!-- 经典两列布局 -->
    <div
      v-if="layoutMode === 'classic'"
      class="detection-content classic-layout"
      :key="`classic-${layoutKey}`"
    >
      <a-row :gutter="[16, 16]">
        <!-- 上传区域 -->
        <a-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <a-card title="文件上传" class="upload-card">
            <div class="upload-area">
              <a-upload-dragger
                v-model:fileList="fileList"
                name="file"
                multiple
                :before-upload="beforeUpload"
                @change="handleUploadChange"
                accept="image/*,video/*"
                :show-upload-list="false"
                class="beautiful-upload"
              >
                <div class="upload-icon-wrapper">
                  <InboxOutlined class="upload-main-icon" />
                  <div class="upload-icon-ring"></div>
                </div>
                <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p class="ant-upload-hint">支持单个或批量上传图片和视频文件</p>
                <div class="upload-features">
                  <span class="feature-tag">📷 图片</span>
                  <span class="feature-tag">🎥 视频</span>
                  <span class="feature-tag">📦 批量</span>
                </div>
              </a-upload-dragger>

              <!-- 紧凑的文件预览 -->
              <div v-if="fileList.length > 0" class="compact-preview">
                <div class="preview-header">
                  <span class="preview-title">已上传文件 ({{ fileList.length }})</span>
                </div>
                <div class="preview-grid">
                  <div
                    v-for="(file, index) in fileList"
                    :key="index"
                    class="preview-card"
                    @click="showFilePreview(file)"
                  >
                    <div class="preview-thumb">
                      <img
                        v-if="file.type && file.type.startsWith('image/')"
                        :src="getFilePreviewUrl(file)"
                        :alt="file.name"
                      />
                      <video
                        v-else-if="file.type && file.type.startsWith('video/')"
                        :src="getFilePreviewUrl(file)"
                        preload="metadata"
                        muted
                      ></video>
                      <div v-else class="file-placeholder">
                        <FileImageOutlined />
                      </div>
                      <div class="preview-delete-btn" @click.stop="removeFile(index)">
                        <DeleteOutlined />
                      </div>
                    </div>
                    <div class="preview-name">{{ file.name }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 检测参数配置 -->
            <div class="detection-params" v-if="fileList.length > 0">
              <h4>检测参数配置</h4>
              <a-row :gutter="16">
                <a-col :span="12">
                  <div class="param-item">
                    <label>当前模型：</label>
                    <div class="current-model-info">
                      <span v-if="currentModel" class="model-name">
                        {{ currentModel.name }} (v{{ currentModel.version }})
                      </span>
                      <span v-else class="no-model">暂无可用模型</span>
                    </div>
                  </div>
                </a-col>
                <a-col :span="6">
                  <div class="param-item">
                    <label>置信度阈值：</label>
                    <a-slider
                      v-model:value="confidenceThreshold"
                      :min="0.1"
                      :max="1.0"
                      :step="0.1"
                      :marks="{ 0.1: '0.1', 0.5: '0.5', 1.0: '1.0' }"
                    />
                    <span class="param-value">{{ confidenceThreshold }}</span>
                  </div>
                </a-col>
                <a-col :span="6">
                  <div class="param-item">
                    <label>NMS阈值：</label>
                    <a-slider
                      v-model:value="nmsThreshold"
                      :min="0.1"
                      :max="1.0"
                      :step="0.1"
                      :marks="{ 0.1: '0.1', 0.5: '0.5', 1.0: '1.0' }"
                    />
                    <span class="param-value">{{ nmsThreshold }}</span>
                  </div>
                </a-col>
              </a-row>
            </div>

            <div class="upload-actions" v-if="fileList.length > 0">
              <a-button type="primary" @click="startDetection" :loading="detecting">
                <PlayCircleOutlined />
                开始检测
              </a-button>
              <a-button @click="clearFiles">
                <DeleteOutlined />
                清空文件
              </a-button>
            </div>
          </a-card>
        </a-col>

        <!-- 检测结果 -->
        <a-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <a-card title="检测结果" class="result-card">
            <div v-if="detectionResults.length === 0" class="no-results">
              <div class="no-results-icon">
                <FileImageOutlined />
              </div>
              <p>暂无检测结果</p>
              <p class="no-results-hint">请先上传图片并开始检测</p>
            </div>

            <div v-else class="results-list">
              <div v-if="detectionResults.length > 1" class="scroll-hint">
                <span>共 {{ detectionResults.length }} 个检测结果，可滚动查看</span>
              </div>
              <div class="results-grid">
                <div
                  v-for="(result, index) in sortedDetectionResults"
                  :key="result.timestamp || index"
                  class="result-item"
                >
                  <!-- 图片对比区域 -->
                  <div class="image-comparison">
                    <div class="image-pair">
                      <div class="image-container">
                        <h5>{{ result.fileType === 'video' ? '原视频' : '原图' }}</h5>
                        <div class="image-wrapper">
                          <!-- 图片显示 -->
                          <img
                            v-if="result.fileType === 'image'"
                            :src="result.originalImageUrl"
                            :alt="`原图 ${index + 1}`"
                            @load="onImageLoad"
                            @error="onImageError"
                            @click="showImageModal(result.originalImageUrl, '原图')"
                            :style="{
                              display: result.originalImageLoaded ? 'block' : 'none',
                              cursor: 'pointer',
                            }"
                          />
                          <!-- 视频显示 -->
                          <video
                            v-else-if="result.fileType === 'video'"
                            :src="result.originalImageUrl"
                            controls
                            preload="metadata"
                            @loadeddata="onVideoLoad"
                            @error="onVideoError"
                            @click="showVideoModal(result.originalImageUrl, '原视频')"
                            :style="{
                              display: result.originalImageLoaded ? 'block' : 'none',
                              cursor: 'pointer',
                            }"
                          />
                          <div
                            class="image-loading"
                            v-if="!result.originalImageLoaded && !result.originalImageError"
                          >
                            <a-spin size="large" />
                            <p>加载中...</p>
                          </div>
                          <div class="image-error" v-if="result.originalImageError">
                            <p>❌ {{ result.fileType === 'video' ? '视频' : '图片' }}加载失败</p>
                            <a-button size="small" @click="retryImageLoad(result, 'original')"
                              >重试</a-button
                            >
                          </div>
                        </div>
                      </div>
                      <div class="image-container">
                        <h5>{{ result.fileType === 'video' ? '检测结果视频' : '检测结果' }}</h5>
                        <div class="image-wrapper">
                          <!-- 图片显示 -->
                          <img
                            v-if="result.fileType === 'image'"
                            :src="result.resultImageUrl"
                            :alt="`检测结果 ${index + 1}`"
                            @load="onImageLoad"
                            @error="onImageError"
                            @click="showImageModal(result.resultImageUrl, '检测结果')"
                            :style="{
                              display: result.resultImageLoaded ? 'block' : 'none',
                              cursor: 'pointer',
                            }"
                          />
                          <!-- 视频显示 -->
                          <video
                            v-else-if="result.fileType === 'video'"
                            :src="result.resultImageUrl"
                            controls
                            preload="metadata"
                            playsinline
                            webkit-playsinline
                            muted
                            @loadeddata="onVideoLoad"
                            @canplay="onVideoCanPlay"
                            @error="onVideoError"
                            @click="showVideoModal(result.resultImageUrl, '检测结果视频')"
                            :style="{
                              display: result.resultImageLoaded ? 'block' : 'none',
                              cursor: 'pointer',
                            }"
                          />
                          <div
                            class="image-loading"
                            v-if="!result.resultImageLoaded && !result.resultImageError"
                          >
                            <a-spin size="large" />
                            <p>加载中...</p>
                          </div>
                          <div class="image-error" v-if="result.resultImageError">
                            <p>❌ {{ result.fileType === 'video' ? '视频' : '图片' }}加载失败</p>
                            <div class="error-actions">
                              <a-button size="small" @click="retryImageLoad(result, 'result')"
                                >重试</a-button
                              >
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 检测信息 -->
                  <div class="result-details">
                    <h4>{{ result.filename }}</h4>

                    <!-- 检测统计 -->
                    <div class="detection-stats">
                      <div class="stat-item">
                        <span class="stat-label">检测目标数:</span>
                        <span class="stat-value">{{ result.objectCount }} 个</span>
                      </div>
                      <div class="stat-item">
                        <span class="stat-label">平均置信度:</span>
                        <span class="stat-value"
                          >{{ (result.averageConfidence * 100).toFixed(1) }}%</span
                        >
                      </div>
                      <div class="stat-item">
                        <span class="stat-label">处理时间:</span>
                        <span class="stat-value">{{ result.processingTime }}s</span>
                      </div>
                    </div>

                    <!-- 检测类别 -->
                    <div class="detection-categories" v-if="result.detectedCategories.length > 0">
                      <h5>检测到的类别:</h5>
                      <div class="category-list">
                        <a-tag
                          v-for="(category, idx) in result.detectedCategories"
                          :key="idx"
                          :color="getDetectionColor(category)"
                        >
                          {{ category }} ({{ (result.confidenceScores[idx] * 100).toFixed(1) }}%)
                        </a-tag>
                      </div>
                    </div>

                    <div class="model-info">
                      <small>使用模型: {{ result.modelInfo.model_name }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 上下布局 -->
    <div
      v-if="layoutMode === 'vertical'"
      class="detection-content vertical-layout"
      :key="`vertical-${layoutKey}`"
    >
      <a-card title="文件上传" class="upload-card">
        <div class="upload-area">
          <a-upload-dragger
            v-model:fileList="fileList"
            name="file"
            multiple
            :before-upload="beforeUpload"
            @change="handleUploadChange"
            accept="image/*,video/*"
            class="beautiful-upload"
          >
            <div class="upload-icon-wrapper">
              <InboxOutlined class="upload-main-icon" />
              <div class="upload-icon-ring"></div>
            </div>
            <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p class="ant-upload-hint">支持单个或批量上传图片和视频文件</p>
            <div class="upload-features">
              <span class="feature-tag">📷 图片</span>
              <span class="feature-tag">🎥 视频</span>
              <span class="feature-tag">📦 批量</span>
            </div>
          </a-upload-dragger>
          <div v-if="fileList.length > 0" class="compact-preview">
            <div class="preview-header">
              <span class="preview-title">已上传文件 ({{ fileList.length }})</span>
              <a-button size="small" type="text" @click="clearFiles">
                <DeleteOutlined />
                清空
              </a-button>
            </div>
            <div class="preview-grid">
              <div
                v-for="(file, index) in fileList"
                :key="index"
                class="preview-card"
                @click="showFilePreview(file)"
              >
                <div class="preview-thumb">
                  <img
                    v-if="file.type && file.type.startsWith('image/')"
                    :src="getFilePreviewUrl(file)"
                    :alt="file.name"
                  />
                  <video
                    v-else-if="file.type && file.type.startsWith('video/')"
                    :src="getFilePreviewUrl(file)"
                    preload="metadata"
                    muted
                  ></video>
                  <div v-else class="file-placeholder">
                    <FileImageOutlined />
                  </div>
                  <div class="preview-delete-btn" @click.stop="removeFile(index)">
                    <DeleteOutlined />
                  </div>
                </div>
                <div class="preview-name">{{ file.name }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="detection-params" v-if="fileList.length > 0">
          <h4>检测参数配置</h4>
          <a-row :gutter="16">
            <a-col :span="8">
              <div class="param-item">
                <label>当前模型：</label>
                <div class="current-model-info">
                  <span v-if="currentModel" class="model-name">
                    {{ currentModel.name }} (v{{ currentModel.version }})
                  </span>
                  <span v-else class="no-model">暂无可用模型</span>
                </div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="param-item">
                <label>置信度阈值：</label>
                <a-slider
                  v-model:value="confidenceThreshold"
                  :min="0.1"
                  :max="1.0"
                  :step="0.1"
                  :marks="{ 0.1: '0.1', 0.5: '0.5', 1.0: '1.0' }"
                />
                <span class="param-value">{{ confidenceThreshold }}</span>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="param-item">
                <label>NMS阈值：</label>
                <a-slider
                  v-model:value="nmsThreshold"
                  :min="0.1"
                  :max="1.0"
                  :step="0.1"
                  :marks="{ 0.1: '0.1', 0.5: '0.5', 1.0: '1.0' }"
                />
                <span class="param-value">{{ nmsThreshold }}</span>
              </div>
            </a-col>
          </a-row>
        </div>
        <div class="upload-actions" v-if="fileList.length > 0">
          <a-button type="primary" @click="startDetection" :loading="detecting">
            <PlayCircleOutlined />
            开始检测
          </a-button>
          <a-button @click="clearFiles">
            <DeleteOutlined />
            清空文件
          </a-button>
        </div>
      </a-card>

      <a-card title="检测结果" class="result-card" style="margin-top: 16px">
        <div v-if="detectionResults.length === 0" class="no-results">
          <div class="no-results-icon">
            <FileImageOutlined />
          </div>
          <p>暂无检测结果</p>
          <p class="no-results-hint">请先上传图片并开始检测</p>
        </div>
        <div v-else class="results-list vertical-results">
          <div
            v-for="(result, index) in sortedDetectionResults"
            :key="result.timestamp || index"
            class="result-item"
          >
            <div class="image-comparison">
              <div class="image-pair">
                <div class="image-container">
                  <h5>{{ result.fileType === 'video' ? '原视频' : '原图' }}</h5>
                  <div class="image-wrapper">
                    <img
                      v-if="result.fileType === 'image'"
                      :src="result.originalImageUrl"
                      :alt="`原图 ${index + 1}`"
                      @load="onImageLoad"
                      @error="onImageError"
                      @click="showImageModal(result.originalImageUrl, '原图')"
                      :style="{
                        display: result.originalImageLoaded ? 'block' : 'none',
                        cursor: 'pointer',
                      }"
                    />
                    <video
                      v-else-if="result.fileType === 'video'"
                      :src="result.originalImageUrl"
                      controls
                      preload="metadata"
                      @loadeddata="onVideoLoad"
                      @error="onVideoError"
                      @click="showVideoModal(result.originalImageUrl, '原视频')"
                      :style="{
                        display: result.originalImageLoaded ? 'block' : 'none',
                        cursor: 'pointer',
                      }"
                    />
                    <div
                      class="image-loading"
                      v-if="!result.originalImageLoaded && !result.originalImageError"
                    >
                      <a-spin size="large" />
                      <p>加载中...</p>
                    </div>
                    <div class="image-error" v-if="result.originalImageError">
                      <p>❌ {{ result.fileType === 'video' ? '视频' : '图片' }}加载失败</p>
                      <a-button size="small" @click="retryImageLoad(result, 'original')"
                        >重试</a-button
                      >
                    </div>
                  </div>
                </div>
                <div class="image-container">
                  <h5>{{ result.fileType === 'video' ? '检测结果视频' : '检测结果' }}</h5>
                  <div class="image-wrapper">
                    <img
                      v-if="result.fileType === 'image'"
                      :src="result.resultImageUrl"
                      :alt="`检测结果 ${index + 1}`"
                      @load="onImageLoad"
                      @error="onImageError"
                      @click="showImageModal(result.resultImageUrl, '检测结果')"
                      :style="{
                        display: result.resultImageLoaded ? 'block' : 'none',
                        cursor: 'pointer',
                      }"
                    />
                    <video
                      v-else-if="result.fileType === 'video'"
                      :src="result.resultImageUrl"
                      controls
                      preload="metadata"
                      playsinline
                      webkit-playsinline
                      muted
                      @loadeddata="onVideoLoad"
                      @canplay="onVideoCanPlay"
                      @error="onVideoError"
                      @click="showVideoModal(result.resultImageUrl, '检测结果视频')"
                      :style="{
                        display: result.resultImageLoaded ? 'block' : 'none',
                        cursor: 'pointer',
                      }"
                    />
                    <div
                      class="image-loading"
                      v-if="!result.resultImageLoaded && !result.resultImageError"
                    >
                      <a-spin size="large" />
                      <p>加载中...</p>
                    </div>
                    <div class="image-error" v-if="result.resultImageError">
                      <p>❌ {{ result.fileType === 'video' ? '视频' : '图片' }}加载失败</p>
                      <div class="error-actions">
                        <a-button size="small" @click="retryImageLoad(result, 'result')"
                          >重试</a-button
                        >
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="result-details">
              <h4>{{ result.filename }}</h4>
              <div class="detection-stats">
                <div class="stat-item">
                  <span class="stat-label">检测目标数:</span>
                  <span class="stat-value">{{ result.objectCount }} 个</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均置信度:</span>
                  <span class="stat-value">{{ (result.averageConfidence * 100).toFixed(1) }}%</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">处理时间:</span>
                  <span class="stat-value">{{ result.processingTime }}s</span>
                </div>
              </div>
              <div class="detection-categories" v-if="result.detectedCategories.length > 0">
                <h5>检测到的类别:</h5>
                <div class="category-list">
                  <a-tag
                    v-for="(category, idx) in result.detectedCategories"
                    :key="idx"
                    :color="getDetectionColor(category)"
                  >
                    {{ category }} ({{ (result.confidenceScores[idx] * 100).toFixed(1) }}%)
                  </a-tag>
                </div>
              </div>
              <div class="model-info">
                <small>使用模型: {{ result.modelInfo.model_name }}</small>
              </div>
            </div>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 侧边栏详情布局 -->
    <div
      v-if="layoutMode === 'grid'"
      class="detection-content sidebar-layout"
      :key="`grid-${layoutKey}`"
    >
      <!-- 顶部上传区域 -->
      <a-card title="文件上传" class="upload-card sidebar-upload" style="margin-bottom: 16px">
        <div class="upload-area">
          <a-upload-dragger
            v-model:fileList="fileList"
            name="file"
            multiple
            :before-upload="beforeUpload"
            @change="handleUploadChange"
            accept="image/*,video/*"
            class="beautiful-upload compact-upload"
          >
            <div class="upload-icon-wrapper">
              <InboxOutlined class="upload-main-icon" />
            </div>
            <p class="ant-upload-text">点击或拖拽上传</p>
          </a-upload-dragger>
          <div v-if="fileList.length > 0" class="compact-preview">
            <div class="preview-header">
              <span class="preview-title">已上传 ({{ fileList.length }})</span>
              <a-button size="small" type="text" @click="clearFiles">
                <DeleteOutlined />
              </a-button>
            </div>
            <div class="preview-grid">
              <div
                v-for="(file, index) in fileList"
                :key="index"
                class="preview-card"
                @click="showFilePreview(file)"
              >
                <div class="preview-thumb">
                  <img
                    v-if="file.type && file.type.startsWith('image/')"
                    :src="getFilePreviewUrl(file)"
                    :alt="file.name"
                  />
                  <video
                    v-else-if="file.type && file.type.startsWith('video/')"
                    :src="getFilePreviewUrl(file)"
                    preload="metadata"
                    muted
                  ></video>
                  <div v-else class="file-placeholder">
                    <FileImageOutlined />
                  </div>
                  <div class="preview-delete-btn" @click.stop="removeFile(index)">
                    <DeleteOutlined />
                  </div>
                </div>
                <div class="preview-name">{{ file.name }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="detection-params" v-if="fileList.length > 0">
          <h4>参数配置</h4>
          <a-row :gutter="16">
            <a-col :span="8">
              <div class="param-item">
                <label>模型：</label>
                <div class="current-model-info">
                  <span v-if="currentModel" class="model-name">
                    {{ currentModel.name }}
                  </span>
                  <span v-else class="no-model">暂无模型</span>
                </div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="param-item">
                <label>置信度：{{ confidenceThreshold }}</label>
                <a-slider v-model:value="confidenceThreshold" :min="0.1" :max="1.0" :step="0.1" />
              </div>
            </a-col>
            <a-col :span="8">
              <div class="param-item">
                <label>NMS：{{ nmsThreshold }}</label>
                <a-slider v-model:value="nmsThreshold" :min="0.1" :max="1.0" :step="0.1" />
              </div>
            </a-col>
          </a-row>
        </div>
        <div class="upload-actions" v-if="fileList.length > 0">
          <a-button type="primary" @click="startDetection" :loading="detecting" block>
            <PlayCircleOutlined />
            开始检测
          </a-button>
          <a-button @click="clearFiles" block style="margin-top: 8px">
            <DeleteOutlined />
            清空
          </a-button>
        </div>
      </a-card>

      <!-- 主内容区域：左侧列表 + 右侧详情 -->
      <a-row :gutter="[16, 16]">
        <!-- 左侧：检测结果列表 -->
        <a-col :xs="24" :sm="24" :md="8" :lg="6" :xl="5">
          <a-card title="检测结果列表" class="sidebar-list-card">
            <div v-if="detectionResults.length === 0" class="sidebar-no-results">
              <FileImageOutlined class="sidebar-empty-icon" />
              <p>暂无检测结果</p>
              <p class="sidebar-empty-hint">请先上传并开始检测</p>
            </div>
            <div v-else class="sidebar-results-list">
              <div
                v-for="(result, index) in sortedDetectionResults"
                :key="result.timestamp || index"
                class="sidebar-result-item"
                :class="{ active: selectedResultIndex === index }"
                @click="selectedResultIndex = index"
              >
                <div class="sidebar-thumb">
                  <img
                    v-if="result.fileType === 'image' && result.resultImageUrl"
                    :src="result.resultImageUrl"
                    :alt="result.filename"
                    @load="onImageLoad"
                    @error="onImageError"
                    :style="{ display: result.resultImageLoaded ? 'block' : 'none' }"
                  />
                  <video
                    v-else-if="result.fileType === 'video' && result.resultImageUrl"
                    :src="result.resultImageUrl"
                    preload="metadata"
                    muted
                    @loadeddata="onVideoLoad"
                    @error="onVideoError"
                    :style="{ display: result.resultImageLoaded ? 'block' : 'none' }"
                  />
                  <div v-else-if="!result.resultImageUrl" class="sidebar-placeholder">
                    <FileImageOutlined />
                  </div>
                  <div
                    class="sidebar-loading"
                    v-if="
                      result.resultImageUrl && !result.resultImageLoaded && !result.resultImageError
                    "
                  >
                    <a-spin size="small" />
                  </div>
                  <div class="sidebar-badge" v-if="result.objectCount > 0">
                    <a-tag color="blue" size="small">{{ result.objectCount }}</a-tag>
                  </div>
                </div>
                <div class="sidebar-info">
                  <div class="sidebar-filename">{{ result.filename }}</div>
                  <div class="sidebar-meta">
                    <span class="sidebar-time">{{ formatTime(result.timestamp) }}</span>
                    <a-tag color="green" size="small"
                      >{{ (result.averageConfidence * 100).toFixed(0) }}%</a-tag
                    >
                  </div>
                  <div class="sidebar-categories" v-if="result.detectedCategories.length > 0">
                    <a-tag
                      v-for="(category, idx) in result.detectedCategories.slice(0, 2)"
                      :key="idx"
                      :color="getDetectionColor(category)"
                      size="small"
                    >
                      {{ category }}
                    </a-tag>
                    <a-tag v-if="result.detectedCategories.length > 2" size="small">
                      +{{ result.detectedCategories.length - 2 }}
                    </a-tag>
                  </div>
                </div>
              </div>
            </div>
          </a-card>
        </a-col>

        <!-- 右侧：详细对比 -->
        <a-col :xs="24" :sm="24" :md="16" :lg="18" :xl="19">
          <a-card title="检测详情对比" class="sidebar-detail-card">
            <div v-if="!selectedResult" class="sidebar-detail-empty">
              <FileImageOutlined class="detail-empty-icon" />
              <p>请从左侧列表选择一个检测结果查看详情</p>
            </div>
            <div v-else class="sidebar-detail-content">
              <div class="detail-view">
                <!-- 图片对比区域 -->
                <div class="detail-image-comparison">
                  <div class="detail-image-pair">
                    <div class="detail-image-box">
                      <div class="detail-image-label">
                        <span class="label-icon">📷</span>
                        <span>{{ selectedResult.fileType === 'video' ? '原视频' : '原图' }}</span>
                      </div>
                      <div class="detail-image-wrapper">
                        <img
                          v-if="selectedResult.fileType === 'image'"
                          :src="selectedResult.originalImageUrl"
                          :alt="`原图`"
                          @load="onImageLoad"
                          @error="onImageError"
                          @click="showImageModal(selectedResult.originalImageUrl, '原图')"
                          :style="{
                            display: selectedResult.originalImageLoaded ? 'block' : 'none',
                            cursor: 'pointer',
                          }"
                        />
                        <video
                          v-else-if="selectedResult.fileType === 'video'"
                          :src="selectedResult.originalImageUrl"
                          controls
                          preload="metadata"
                          @loadeddata="onVideoLoad"
                          @error="onVideoError"
                          @click="showVideoModal(selectedResult.originalImageUrl, '原视频')"
                          :style="{
                            display: selectedResult.originalImageLoaded ? 'block' : 'none',
                            cursor: 'pointer',
                          }"
                        />
                        <div
                          class="image-loading"
                          v-if="
                            !selectedResult.originalImageLoaded &&
                            !selectedResult.originalImageError
                          "
                        >
                          <a-spin size="large" />
                          <p>加载中...</p>
                        </div>
                        <div class="image-error" v-if="selectedResult.originalImageError">
                          <p>❌ 加载失败</p>
                          <a-button size="small" @click="retryImageLoad(selectedResult, 'original')"
                            >重试</a-button
                          >
                        </div>
                      </div>
                    </div>
                    <div class="detail-image-box">
                      <div class="detail-image-label">
                        <span class="label-icon">🎯</span>
                        <span>{{
                          selectedResult.fileType === 'video' ? '检测结果视频' : '检测结果'
                        }}</span>
                      </div>
                      <div class="detail-image-wrapper">
                        <img
                          v-if="selectedResult.fileType === 'image'"
                          :src="selectedResult.resultImageUrl"
                          :alt="`检测结果`"
                          @load="onImageLoad"
                          @error="onImageError"
                          @click="showImageModal(selectedResult.resultImageUrl, '检测结果')"
                          :style="{
                            display: selectedResult.resultImageLoaded ? 'block' : 'none',
                            cursor: 'pointer',
                          }"
                        />
                        <video
                          v-else-if="selectedResult.fileType === 'video'"
                          :src="selectedResult.resultImageUrl"
                          controls
                          preload="metadata"
                          playsinline
                          webkit-playsinline
                          muted
                          @loadeddata="onVideoLoad"
                          @canplay="onVideoCanPlay"
                          @error="onVideoError"
                          @click="showVideoModal(selectedResult.resultImageUrl, '检测结果视频')"
                          :style="{
                            display: selectedResult.resultImageLoaded ? 'block' : 'none',
                            cursor: 'pointer',
                          }"
                        />
                        <div
                          class="image-loading"
                          v-if="
                            !selectedResult.resultImageLoaded && !selectedResult.resultImageError
                          "
                        >
                          <a-spin size="large" />
                          <p>加载中...</p>
                        </div>
                        <div class="image-error" v-if="selectedResult.resultImageError">
                          <p>❌ 加载失败</p>
                          <div class="error-actions">
                            <a-button size="small" @click="retryImageLoad(selectedResult, 'result')"
                              >重试</a-button
                            >
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 详细信息 -->
                <div class="detail-info-section">
                  <h3 class="detail-title">{{ selectedResult.filename }}</h3>
                  <div class="detail-stats-grid">
                    <div class="detail-stat-card">
                      <div class="stat-icon">🎯</div>
                      <div class="stat-content">
                        <div class="stat-value">{{ selectedResult.objectCount }}</div>
                        <div class="stat-label">检测目标</div>
                      </div>
                    </div>
                    <div class="detail-stat-card">
                      <div class="stat-icon">📊</div>
                      <div class="stat-content">
                        <div class="stat-value">
                          {{ (selectedResult.averageConfidence * 100).toFixed(1) }}%
                        </div>
                        <div class="stat-label">平均置信度</div>
                      </div>
                    </div>
                    <div class="detail-stat-card">
                      <div class="stat-icon">⏱️</div>
                      <div class="stat-content">
                        <div class="stat-value">{{ selectedResult.processingTime }}s</div>
                        <div class="stat-label">处理时间</div>
                      </div>
                    </div>
                    <div class="detail-stat-card">
                      <div class="stat-icon">🤖</div>
                      <div class="stat-content">
                        <div class="stat-value">{{ selectedResult.modelInfo.model_name }}</div>
                        <div class="stat-label">使用模型</div>
                      </div>
                    </div>
                  </div>
                  <div
                    class="detail-categories-section"
                    v-if="selectedResult.detectedCategories.length > 0"
                  >
                    <h4>检测到的类别</h4>
                    <div class="detail-categories-list">
                      <a-tag
                        v-for="(category, idx) in selectedResult.detectedCategories"
                        :key="idx"
                        :color="getDetectionColor(category)"
                        class="detail-category-tag"
                      >
                        {{ category }}
                        <span
                          v-if="
                            selectedResult.confidenceScores && selectedResult.confidenceScores[idx]
                          "
                        >
                          ({{ (selectedResult.confidenceScores[idx] * 100).toFixed(1) }}%)
                        </span>
                      </a-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 警告框 -->
    <a-modal
      v-model:visible="alertModalVisible"
      :title="alertLevel === 'high' ? '高风险警告' : '中等风险警告'"
      :ok-text="'我知道了'"
      :cancel-text="'关闭'"
      @ok="closeAlertModal"
      @cancel="closeAlertModal"
      :width="520"
      :centered="true"
      :mask-closable="false"
      :keyboard="false"
      class="alert-modal"
    >
      <div class="alert-modal-content">
        <div class="alert-icon-container">
          <div class="alert-icon-wrapper" :class="alertLevel">
            <ExclamationCircleOutlined class="alert-icon" />
            <div class="pulse-ring"></div>
            <div class="pulse-ring-2"></div>
          </div>
        </div>
        <div class="alert-message">
          <div class="alert-title">
            <span class="alert-level-text">{{
              alertLevel === 'high' ? '高风险' : '中等风险'
            }}</span>
            <span class="alert-detected">检测到！</span>
          </div>
          <div class="alert-details">
            <pre>{{ alertMessage }}</pre>
          </div>
        </div>
        <div class="alert-tips" :class="alertLevel">
          <div class="tips-icon">
            <InfoCircleOutlined />
          </div>
          <div class="tips-content">
            <p v-if="alertLevel === 'high'">
              <strong>高风险提示：</strong>请立即关注此检测结果，建议采取相应措施。
            </p>
            <p v-else><strong>中等风险提示：</strong>请关注此检测结果，建议进行进一步检查。</p>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, h, computed, watch, nextTick } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  ScanOutlined,
  InboxOutlined,
  PlayCircleOutlined,
  DeleteOutlined,
  FileImageOutlined,
  ZoomInOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons-vue';
import { yoloApi, detectionHistoryApi, type YoloDetection, type YoloModel } from '@/api/yolo';
import { useUserStore } from '@/stores/user';
import { getFullFileUrl, isImageFile, isVideoFile } from '@/utils/url';

// 布局模式
const layoutMode = ref<'classic' | 'vertical' | 'grid'>('classic');
// 布局切换key，用于强制重新渲染
const layoutKey = ref(0);
// 侧边栏布局选中的结果索引
const selectedResultIndex = ref<number | null>(null);

// 加载布局模式
const loadLayout = async () => {
  const saved = localStorage.getItem('yoloDetectionLayout');
  if (saved && ['classic', 'vertical', 'grid'].includes(saved)) {
    layoutMode.value = saved as 'classic' | 'vertical' | 'grid';
  } else {
    layoutMode.value = 'classic';
  }
  // 强制更新布局key
  layoutKey.value++;
  // 等待DOM更新
  await nextTick();
};

// 监听布局变化事件
const handleLayoutChange = async () => {
  await loadLayout();
};

// 响应式数据
const fileList = ref([]);
const detecting = ref(false);
const detectionResults = ref([]);
const currentModel = ref<YoloModel | null>(null);
const confidenceThreshold = ref(0.5);
const nmsThreshold = ref(0.4);
const userStore = useUserStore();

// 按时间排序的检测结果（最新在前）
const sortedDetectionResults = computed(() => {
  return [...detectionResults.value].sort((a, b) => {
    // 按时间戳降序排列（最新的在前）
    return (b.timestamp || 0) - (a.timestamp || 0);
  });
});

// 当前选中的检测结果（用于侧边栏布局）
const selectedResult = computed(() => {
  if (
    selectedResultIndex.value === null ||
    !sortedDetectionResults.value[selectedResultIndex.value]
  ) {
    return null;
  }
  return sortedDetectionResults.value[selectedResultIndex.value];
});

// 监听检测结果变化，自动选中第一个
watch(
  () => detectionResults.value.length,
  (newLen, oldLen) => {
    if (newLen > 0 && layoutMode.value === 'grid') {
      if (oldLen === 0 || selectedResultIndex.value === null) {
        selectedResultIndex.value = 0;
      }
    } else if (newLen === 0) {
      selectedResultIndex.value = null;
    }
  }
);

// 监听布局模式变化，重置选中状态
watch(
  layoutMode,
  async (newMode, oldMode) => {
    if (newMode !== oldMode) {
      // 布局切换时强制更新
      await nextTick();
      layoutKey.value++;

      // 重置选中状态
      if (newMode === 'grid' && detectionResults.value.length > 0) {
        if (
          selectedResultIndex.value === null ||
          selectedResultIndex.value >= sortedDetectionResults.value.length
        ) {
          selectedResultIndex.value = 0;
        }
      } else if (newMode !== 'grid') {
        selectedResultIndex.value = null;
      }
    }
  },
  { immediate: false }
);

// 警告框相关
const alertModalVisible = ref(false);
const alertLevel = ref<'medium' | 'high'>('medium');
const alertMessage = ref('');

// 检测结果接口
interface DetectionResult {
  filename: string;
  fileType: 'image' | 'video';
  imageUrl: string;
  originalImageUrl: string;
  resultImageUrl: string;
  originalImageLoaded: boolean;
  resultImageLoaded: boolean;
  originalImageError: boolean;
  resultImageError: boolean;
  detections: YoloDetection[];
  averageConfidence: number;
  processingTime: number;
  modelInfo: {
    model_id: string;
    model_name: string;
    version: string;
  };
  objectCount: number;
  detectedCategories: string[];
  confidenceScores: number[];
  alertLevel?: 'low' | 'medium' | 'high';
  timestamp?: number;
}

// 上传前处理
const beforeUpload = (file: any) => {
  const mimeType = file.type || '';
  const fileName = file.name || '';

  const isImageByMime = mimeType.startsWith('image/');
  const isVideoByMime = mimeType.startsWith('video/');
  const isImageByExt = isImageFile(fileName);
  const isVideoByExt = isVideoFile(fileName);

  const isImage = isImageByMime || (!isVideoByMime && isImageByExt);
  const isVideo = isVideoByMime || (!isImageByMime && isVideoByExt);

  if (!isImage && !isVideo) {
    message.error('只能上传图片或视频文件!');
    return false;
  }

  // 如果浏览器没有提供 MIME 类型，根据判断结果补一个，方便后续逻辑使用
  if (!file.type) {
    if (isVideo) {
      file.type = 'video/*';
    } else if (isImage) {
      file.type = 'image/*';
    }
  }

  // 图片文件大小限制
  if (isImage) {
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('图片大小不能超过 10MB!');
      return false;
    }
  }

  // 视频文件大小限制
  if (isVideo) {
    const isLt100M = file.size / 1024 / 1024 < 100;
    if (!isLt100M) {
      message.error('视频大小不能超过 100MB!');
      return false;
    }
  }

  return false; // 阻止自动上传
};

// 处理上传变化
const handleUploadChange = (info: any) => {
  fileList.value = info.fileList;
};

// 获取文件预览URL
const getFilePreviewUrl = (file: any) => {
  if (file.originFileObj) {
    return URL.createObjectURL(file.originFileObj);
  } else if (file.url) {
    return file.url;
  }
  return '';
};

// 显示文件预览
const showFilePreview = (file: any) => {
  const url = getFilePreviewUrl(file);
  if (!url) return;

  if (file.type && file.type.startsWith('image/')) {
    showImageModal(url, file.name);
  } else if (file.type && file.type.startsWith('video/')) {
    showVideoModal(url, file.name);
  }
};

// 开始检测
const startDetection = async () => {
  if (fileList.value.length === 0) {
    message.warning('请先上传图片文件');
    return;
  }

  if (!userStore.userInfo?.user_id) {
    message.error('用户信息不存在，请重新登录');
    return;
  }

  if (!currentModel.value) {
    message.error('当前未启用 YOLO 检测模型，请先在模型管理中启用模型后再使用此功能');
    return;
  }

  detecting.value = true;

  try {
    console.log('开始YOLO检测，文件数量:', fileList.value.length);
    console.log('使用模型:', currentModel.value.name, 'v' + currentModel.value.version);

    // 处理每个文件
    for (const file of fileList.value) {
      console.log('正在处理文件:', file.name);
      console.log('文件对象:', file);

      // 获取实际的文件对象
      const actualFile = file.originFileObj || file;
      console.log('实际文件对象:', actualFile);

      if (!actualFile) {
        console.error('无法获取文件对象');
        message.error(`文件 ${file.name} 无效`);
        continue;
      }

      // 创建图片预览URL
      const imageUrl = URL.createObjectURL(actualFile);

      try {
        // 调用真实的YOLO检测API，使用当前启用的模型
        const response = await yoloApi.detectImage({
          image: actualFile,
          model_id: currentModel.value.id,
          confidence_threshold: confidenceThreshold.value,
          nms_threshold: nmsThreshold.value,
        });

        console.log('检测API响应:', response);

        if (response.data) {
          // 直接使用后端返回的URL地址，不再通过getFullFileUrl处理
          console.log('🔍 原始URL数据:', {
            original_file_url: response.data.original_file_url,
            result_file_url: response.data.result_file_url,
          });

          let originalImageUrl = response.data.original_file_url;
          let resultImageUrl = response.data.result_file_url;

          console.log('🖼️ 直接使用的URL地址:', {
            original: originalImageUrl,
            result: resultImageUrl,
          });

          // 判断文件类型（同时参考 MIME 和文件扩展名，避免视频被识别成图片）
          const actualMimeType = (actualFile as any).type || '';
          const actualName = (actualFile as any).name || file.name || '';
          const isVideoFileType = actualMimeType.startsWith('video/') || isVideoFile(actualName);
          const fileType: 'image' | 'video' = isVideoFileType ? 'video' : 'image';

          // 对于视频文件，使用后端返回的URL；对于图片文件，使用本地预览URL
          const displayImageUrl = fileType === 'video' ? originalImageUrl : imageUrl;

          const result: DetectionResult = {
            filename: file.name,
            fileType,
            imageUrl: displayImageUrl,
            originalImageUrl,
            resultImageUrl,
            originalImageLoaded: false,
            resultImageLoaded: false,
            originalImageError: false,
            resultImageError: false,
            detections: [], // 后端返回的是categories和scores数组，需要转换
            averageConfidence: response.data.avg_confidence || 0,
            processingTime: response.data.processing_time,
            modelInfo: {
              model_id: '',
              model_name: response.data.model_used,
              version: '',
            },
            objectCount: response.data.object_count,
            detectedCategories: response.data.detected_categories || [],
            confidenceScores: response.data.confidence_scores || [],
            alertLevel: response.data.alert_level || 'low',
            timestamp: Date.now(), // 添加时间戳
          };

          // 预加载图片，确保能正确显示（仅针对图片类型，视频不使用 Image 预加载）
          if (fileType === 'image') {
            // 创建Promise数组来等待所有图片加载完成
            const loadPromises: Promise<void>[] = [];

            if (resultImageUrl) {
              const resultPromise = new Promise<void>((resolve) => {
                const img = new Image();
                img.onload = () => {
                  result.resultImageLoaded = true;
                  console.log('✅ 结果图片预加载成功:', resultImageUrl);
                  resolve();
                };
                img.onerror = () => {
                  result.resultImageError = true;
                  console.error('❌ 结果图片预加载失败:', resultImageUrl);
                  resolve();
                };
                img.src = resultImageUrl;
              });
              loadPromises.push(resultPromise);
            }

            if (originalImageUrl) {
              const originalPromise = new Promise<void>((resolve) => {
                const img = new Image();
                img.onload = () => {
                  result.originalImageLoaded = true;
                  console.log('✅ 原图片预加载成功:', originalImageUrl);
                  resolve();
                };
                img.onerror = () => {
                  result.originalImageError = true;
                  console.error('❌ 原图片预加载失败:', originalImageUrl);
                  resolve();
                };
                img.src = originalImageUrl;
              });
              loadPromises.push(originalPromise);
            }

            // 等待所有图片预加载完成后再添加到结果数组
            Promise.all(loadPromises).then(() => {
              console.log('📸 所有图片预加载完成，添加到结果数组');
              detectionResults.value.unshift(result);
            });
          } else if (fileType === 'video') {
            // 对于视频文件，直接设置加载状态为true，让视频元素自己处理加载
            result.originalImageLoaded = true;
            result.resultImageLoaded = true;
            console.log('📹 视频文件，直接设置加载状态为true');
            // 视频直接添加到结果数组
            detectionResults.value.unshift(result);
          }
          console.log('检测结果:', result);

          // 检查警告级别并显示警告框
          console.log('🔍 检查警告级别:', result.alertLevel);
          if (result.alertLevel === 'high' || result.alertLevel === 'medium') {
            const levelText = result.alertLevel === 'high' ? '高' : '中等';
            const alertMsg = `检测到${levelText}风险级别！\n\n文件: ${result.filename}\n检测到的目标: ${result.detectedCategories.join(', ')}\n平均置信度: ${(result.averageConfidence * 100).toFixed(1)}%`;
            console.log('⚠️ 触发警告弹窗:', result.alertLevel, alertMsg);
            showAlertModal(result.alertLevel, alertMsg);
          } else {
            console.log('✅ 警告级别为低风险，不显示警告弹窗');
          }
        } else {
          console.error('检测失败:', response.message);
          message.error(`文件 ${file.name} 检测失败: ${response.message || '未知错误'}`);
        }
      } catch (apiError) {
        console.error('API调用失败:', apiError);
        message.error(`文件 ${file.name} 检测失败，请检查网络连接`);
      }
    }

    if (detectionResults.value.length > 0) {
      const totalObjects = detectionResults.value.reduce(
        (sum, result) => sum + result.objectCount,
        0
      );
      if (totalObjects > 0) {
        message.success(
          `检测完成！成功处理 ${detectionResults.value.length} 张图片，共检测到 ${totalObjects} 个目标`
        );
      } else {
        message.success(
          `检测完成！成功处理 ${detectionResults.value.length} 张图片，但未检测到任何目标`
        );
      }
    } else {
      message.warning('没有成功处理任何图片');
    }
  } catch (error) {
    console.error('检测过程失败:', error);
    message.error('检测失败，请重试');
  } finally {
    detecting.value = false;
  }
};

// 删除单个文件
const removeFile = (index: number) => {
  if (index >= 0 && index < fileList.value.length) {
    const file = fileList.value[index];
    const fileName = file.name || '文件';

    // 释放对象URL，避免内存泄漏
    // 注意：getFilePreviewUrl每次调用都会创建新的URL，所以这里我们直接删除文件
    // 浏览器会在适当的时候自动清理这些URL
    if (file.originFileObj) {
      try {
        const previewUrl = getFilePreviewUrl(file);
        if (previewUrl && previewUrl.startsWith('blob:')) {
          URL.revokeObjectURL(previewUrl);
        }
      } catch (error) {
        console.warn('释放URL时出错:', error);
      }
    }

    fileList.value.splice(index, 1);
    message.success(`已删除文件: ${fileName}`);
  }
};

// 清空文件
const clearFiles = () => {
  // 释放所有文件的对象URL
  fileList.value.forEach((file) => {
    if (file.originFileObj) {
      const url = URL.createObjectURL(file.originFileObj);
      URL.revokeObjectURL(url);
    }
  });
  fileList.value = [];
  detectionResults.value = [];
  message.info('已清空所有文件');
};

// 显示警告框
const showAlertModal = (level: 'medium' | 'high', message: string) => {
  console.log('🚨 显示警告弹窗:', { level, message });
  alertLevel.value = level;
  alertMessage.value = message;
  alertModalVisible.value = true;
  console.log('🔍 弹窗状态已设置:', alertModalVisible.value);
};

// 关闭警告框
const closeAlertModal = () => {
  alertModalVisible.value = false;
};

// 格式化时间
const formatTime = (timestamp: number | string | undefined) => {
  if (!timestamp) return '未知时间';

  // 如果是时间戳（数字）
  if (typeof timestamp === 'number') {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }

  // 如果是字符串且包含时间格式
  if (typeof timestamp === 'string') {
    // 如果已经是时间格式，直接返回
    if (timestamp.includes(':') && timestamp.includes('-')) {
      return timestamp;
    }
    // 尝试解析为日期
    try {
      const date = new Date(timestamp);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        });
      }
    } catch {
      return timestamp;
    }
  }

  return '未知时间';
};

// 获取检测标签颜色
const getDetectionColor = (className: string) => {
  const colorMap: Record<string, string> = {
    person: 'blue',
    car: 'green',
    dog: 'orange',
    cat: 'purple',
    bicycle: 'cyan',
    motorcycle: 'red',
  };
  return colorMap[className] || 'default';
};

// 图片加载成功处理
const onImageLoad = (event: Event) => {
  const img = event.target as HTMLImageElement;
  const src = img.src;

  // 找到对应的检测结果并更新加载状态
  detectionResults.value.forEach((result) => {
    if (result.originalImageUrl === src) {
      result.originalImageLoaded = true;
    } else if (result.resultImageUrl === src) {
      result.resultImageLoaded = true;
    }
  });

  console.log('✅ 图片加载成功:', src);
};

// 图片加载失败处理
const onImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  const src = img.src;

  // 找到对应的检测结果并更新错误状态
  detectionResults.value.forEach((result) => {
    if (result.originalImageUrl === src) {
      result.originalImageLoaded = false;
      result.originalImageError = true;
    } else if (result.resultImageUrl === src) {
      result.resultImageLoaded = false;
      result.resultImageError = true;
    }
  });

  console.error('❌ 图片加载失败:', src);
  message.error('图片加载失败，请检查网络连接');
};

// 视频加载成功处理
const onVideoLoad = (event: Event) => {
  const video = event.target as HTMLVideoElement;
  const src = video.src;

  console.log('🎥 视频加载事件触发:', {
    src,
    readyState: video.readyState,
    networkState: video.networkState,
    duration: video.duration,
    videoWidth: video.videoWidth,
    videoHeight: video.videoHeight,
  });

  // 找到对应的检测结果并更新加载状态
  detectionResults.value.forEach((result) => {
    if (result.originalImageUrl === src) {
      result.originalImageLoaded = true;
      result.originalImageError = false;
      console.log('✅ 原视频加载成功:', src);
    } else if (result.resultImageUrl === src) {
      result.resultImageLoaded = true;
      result.resultImageError = false;
      console.log('✅ 结果视频加载成功:', src);
      message.success('检测结果视频加载成功');
    }
  });
};

// 视频可以播放处理
const onVideoCanPlay = (event: Event) => {
  const video = event.target as HTMLVideoElement;
  const src = video.src;

  console.log('🎬 视频可以播放:', {
    src,
    readyState: video.readyState,
    networkState: video.networkState,
    duration: video.duration,
    videoWidth: video.videoWidth,
    videoHeight: video.videoHeight,
  });

  // 找到对应的检测结果并更新加载状态
  detectionResults.value.forEach((result) => {
    if (result.originalImageUrl === src) {
      result.originalImageLoaded = true;
      result.originalImageError = false;
      console.log('✅ 原视频可以播放:', src);
    } else if (result.resultImageUrl === src) {
      result.resultImageLoaded = true;
      result.resultImageError = false;
      console.log('✅ 结果视频可以播放:', src);
      message.success('检测结果视频可以播放了');
    }
  });
};

// 视频加载失败处理
const onVideoError = (event: Event) => {
  const video = event.target as HTMLVideoElement;
  const src = video.src;

  console.error('❌ 视频加载失败:', {
    src,
    error: video.error,
    networkState: video.networkState,
    readyState: video.readyState,
  });

  // 找到对应的检测结果并更新错误状态
  detectionResults.value.forEach((result) => {
    if (result.originalImageUrl === src) {
      result.originalImageLoaded = false;
      result.originalImageError = true;
      console.error('❌ 原视频加载失败:', src);
    } else if (result.resultImageUrl === src) {
      result.resultImageLoaded = false;
      result.resultImageError = true;
      console.error('❌ 结果视频加载失败:', src);
    }
  });

  message.error('视频加载失败，请检查网络连接或文件是否存在');
};

// 重试媒体加载
const retryImageLoad = (result: DetectionResult, type: 'original' | 'result') => {
  if (type === 'original') {
    result.originalImageError = false;
    result.originalImageLoaded = false;
  } else {
    result.resultImageError = false;
    result.resultImageLoaded = false;
  }

  const url = type === 'original' ? result.originalImageUrl : result.resultImageUrl;

  console.log('🔄 重试加载媒体:', url);

  const img = new Image();

  img.onload = () => {
    if (type === 'original') {
      result.originalImageLoaded = true;
    } else {
      result.resultImageLoaded = true;
    }
    console.log('✅ 图片重试加载成功:', url);
    message.success('图片加载成功');
  };

  img.onerror = () => {
    if (type === 'original') {
      result.originalImageError = true;
    } else {
      result.resultImageError = true;
    }
    console.error('❌ 图片重试加载失败:', url);
    message.error('图片加载失败');
  };

  img.src = url;
};

// 加载当前启用的YOLO模型
const loadCurrentModel = async () => {
  try {
    console.log('正在加载当前启用的YOLO模型...');
    const response: any = await yoloApi.getCurrentEnabledModel();

    console.log('API响应:', response);

    if (response && response.success && response.data) {
      currentModel.value = response.data;
      console.log('加载到的当前模型:', currentModel.value);
      message.success(`已加载模型: ${currentModel.value.name} v${currentModel.value.version}`);
    } else {
      console.warn('当前没有可用的YOLO模型:', response?.message || '未返回模型数据');
      currentModel.value = null;
      message.warning(
        response?.message || '当前未启用 YOLO 检测模型，请先在模型管理中启用模型后再使用此功能'
      );
    }
  } catch (error: any) {
    console.error('加载当前模型时出错:', error);
    currentModel.value = null;
    const status = error?.response?.status;
    const backendMessage = error?.response?.data?.message;
    if (status === 404) {
      message.warning(
        backendMessage || '当前未启用 YOLO 检测模型，请先在模型管理中启用模型后再使用此功能'
      );
    } else {
      message.error(backendMessage || '加载 YOLO 模型失败，请稍后重试');
    }
  }
};

// 显示图片放大模态框
const showImageModal = (imageUrl: string, title: string) => {
  Modal.info({
    title: title,
    content: h('div', { style: 'text-align: center; padding: 20px;' }, [
      h('img', {
        src: imageUrl,
        style:
          'max-width: 100%; max-height: 70vh; object-fit: contain; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);',
        alt: title,
      }),
    ]),
    width: 'auto',
    centered: true,
    okText: '关闭',
    maskClosable: true,
    class: 'image-modal',
  });
};

// 显示视频放大模态框
const showVideoModal = (videoUrl: string, title: string) => {
  Modal.info({
    title: title,
    content: h('div', { style: 'text-align: center; padding: 20px;' }, [
      h('video', {
        src: videoUrl,
        controls: true,
        style:
          'max-width: 100%; max-height: 70vh; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);',
        preload: 'metadata',
      }),
    ]),
    width: 'auto',
    centered: true,
    okText: '关闭',
    maskClosable: true,
    class: 'video-modal',
  });
};

// 组件挂载时初始化
onMounted(async () => {
  console.log('🚀 YOLO检测页面组件已挂载');
  loadLayout();
  window.addEventListener('yoloDetectionLayoutChanged', handleLayoutChange);
  try {
    await loadCurrentModel();
    console.log('✅ 模型加载完成');
  } catch (error) {
    console.error('❌ 组件初始化失败:', error);
    // 即使初始化失败，也要确保页面能正常显示
  }
  console.log('🎯 YOLO检测页面初始化完成');
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('yoloDetectionLayoutChanged', handleLayoutChange);
});
</script>

<style scoped lang="scss">
.yolo-detection-page {
  padding: 24px;
  background: var(--theme-page-bg, #f5f5f5);
  min-height: 100vh;

  .page-header {
    margin-bottom: 24px;
    text-align: center;

    .page-title {
      font-size: 2rem;
      font-weight: 700;
      color: var(--theme-text-primary, #1e293b);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;

      .title-icon {
        color: var(--theme-primary, #3b82f6);
      }
    }

    .page-description {
      color: var(--theme-text-secondary, #64748b);
      font-size: 1.1rem;
      margin: 0;
    }
  }

  .detection-content {
    // 布局切换优化
    min-height: 500px;

    // 经典两列布局（默认）
    &.classic-layout {
      .results-list {
        .results-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;

          .result-item {
            margin-bottom: 0;
            min-height: auto;
            padding: 10px;

            .image-comparison {
              margin-bottom: 10px;

              .image-pair {
                gap: 8px;

                .image-container {
                  .image-wrapper {
                    height: 120px;
                  }

                  h5 {
                    font-size: 0.8rem;
                    margin-bottom: 6px;
                  }
                }
              }
            }

            .result-details {
              h4 {
                font-size: 0.85rem;
                margin-bottom: 6px;
              }

              .detection-stats {
                gap: 8px;
                padding: 6px;
                margin-bottom: 8px;

                .stat-item {
                  .stat-label {
                    font-size: 0.75rem;
                  }

                  .stat-value {
                    font-size: 0.9rem;
                  }
                }
              }

              .detection-categories {
                margin-bottom: 6px;

                h5 {
                  font-size: 0.8rem;
                  margin-bottom: 4px;
                }

                .category-list {
                  gap: 4px;

                  :deep(.ant-tag) {
                    font-size: 0.7rem;
                    padding: 2px 6px;
                  }
                }
              }

              .model-info {
                font-size: 0.7rem;
                margin-top: 4px;
                padding-top: 4px;
              }
            }
          }
        }
      }
    }

    // 上下布局
    &.vertical-layout {
      display: flex;
      flex-direction: column;
      gap: 16px;

      .upload-card {
        margin-bottom: 0;
        flex-shrink: 0;
      }

      .result-card {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;

        :deep(.ant-card-body) {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
          overflow: visible;

          .no-results {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 300px;
          }
        }
      }

      .vertical-results {
        flex: 1;
        overflow-y: auto;
        overflow-x: hidden;
        min-height: 0;
        max-height: none;
        padding-right: 8px;

        /* 自定义滚动条样式 */
        &::-webkit-scrollbar {
          width: 8px;
        }

        &::-webkit-scrollbar-track {
          background: var(--theme-content-bg, #f0f0f0);
          border-radius: 4px;
        }

        &::-webkit-scrollbar-thumb {
          background: var(--theme-primary, #1890ff);
          border-radius: 4px;

          &:hover {
            background: var(--theme-primary, #40a9ff);
          }

          &:active {
            background: var(--theme-primary, #096dd9);
          }
        }

        /* 上下布局中的result-item优化 */
        .result-item {
          width: 100%;
          margin-bottom: 16px;

          .image-comparison {
            .image-pair {
              .image-container {
                .image-wrapper {
                  height: auto;
                  min-height: 200px;
                  max-height: 400px;

                  img,
                  video {
                    object-fit: contain;
                    max-height: 100%;
                  }
                }
              }
            }
          }

          .result-details {
            width: 100%;

            .detection-stats {
              flex-wrap: wrap;
              gap: 12px;
            }

            .detection-categories {
              .category-list {
                flex-wrap: wrap;
              }
            }
          }
        }
      }
    }

    // 侧边栏详情布局
    &.sidebar-layout {
      .sidebar-upload {
        .upload-area {
          margin-bottom: 0;
        }
      }

      .sidebar-list-card {
        height: calc(100vh - 300px);
        min-height: 600px;
        display: flex;
        flex-direction: column;

        :deep(.ant-card-body) {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding: 12px;
          overflow: hidden;
        }
      }

      .sidebar-results-list {
        flex: 1;
        overflow-y: auto;
        padding-right: 4px;

        &::-webkit-scrollbar {
          width: 6px;
        }

        &::-webkit-scrollbar-track {
          background: var(--theme-content-bg, #f0f0f0);
          border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
          background: var(--theme-primary, #1890ff);
          border-radius: 3px;

          &:hover {
            background: var(--theme-primary, #40a9ff);
          }
        }
      }

      .sidebar-result-item {
        display: flex;
        gap: 12px;
        padding: 12px;
        margin-bottom: 8px;
        background: var(--theme-card-bg, #ffffff);
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          border-color: var(--theme-primary, #3b82f6);
          background: var(--theme-content-bg, #f0f7ff);
          transform: translateX(4px);
        }

        &.active {
          border-color: var(--theme-primary, #3b82f6);
          background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        .sidebar-thumb {
          width: 80px;
          height: 80px;
          flex-shrink: 0;
          border-radius: 8px;
          overflow: hidden;
          background: var(--theme-page-bg, #f5f5f5);
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;

          img,
          video {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
          }

          .sidebar-loading {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            top: 0;
            left: 0;
            background: var(--theme-page-bg, #f5f5f5);
            z-index: 1;
          }

          .sidebar-placeholder {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--theme-text-secondary, #9ca3af);
            font-size: 2rem;
          }

          .sidebar-badge {
            position: absolute;
            top: 4px;
            right: 4px;
            z-index: 2;
          }
        }

        .sidebar-info {
          flex: 1;
          min-width: 0;

          .sidebar-filename {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin-bottom: 6px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .sidebar-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;

            .sidebar-time {
              font-size: 0.75rem;
              color: #64748b;
            }
          }

          .sidebar-categories {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
          }
        }
      }

      .sidebar-no-results {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        color: #9ca3af;

        .sidebar-empty-icon {
          font-size: 3rem;
          margin-bottom: 12px;
        }

        p {
          margin: 4px 0;
        }

        .sidebar-empty-hint {
          font-size: 0.85rem;
          color: #d1d5db;
        }
      }

      .sidebar-detail-card {
        min-height: 600px;

        :deep(.ant-card-body) {
          padding: 20px;
        }
      }

      .sidebar-detail-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 500px;
        color: #9ca3af;

        .detail-empty-icon {
          font-size: 4rem;
          margin-bottom: 16px;
        }

        p {
          font-size: 1.1rem;
          color: #64748b;
        }
      }

      .detail-view {
        animation: fadeIn 0.3s ease;
      }

      .detail-image-comparison {
        margin-bottom: 24px;

        .detail-image-pair {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;

          .detail-image-box {
            .detail-image-label {
              display: flex;
              align-items: center;
              gap: 8px;
              margin-bottom: 12px;
              font-weight: 600;
              color: var(--theme-text-primary, #1e293b);
              font-size: 1rem;

              .label-icon {
                font-size: 1.2rem;
              }
            }

            .detail-image-wrapper {
              width: 100%;
              height: 400px;
              border-radius: 12px;
              overflow: hidden;
              background: var(--theme-page-bg, #f5f5f5);
              border: 2px solid var(--theme-card-border, #e5e7eb);
              position: relative;
              display: flex;
              align-items: center;
              justify-content: center;

              img,
              video {
                width: 100%;
                height: 100%;
                object-fit: contain;
                display: block;
              }

              .image-loading {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: var(--theme-page-bg, #f5f5f5);
                z-index: 1;
              }

              .image-error {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: #fef2f2;
                z-index: 1;
              }
            }
          }
        }
      }

      .detail-info-section {
        .detail-title {
          font-size: 1.3rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 20px;
          padding-bottom: 12px;
          border-bottom: 2px solid #e5e7eb;
        }

        .detail-stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
          margin-bottom: 24px;

          .detail-stat-card {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;

            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            .stat-icon {
              font-size: 2rem;
              flex-shrink: 0;
            }

            .stat-content {
              flex: 1;

              .stat-value {
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--theme-text-primary, #1e293b);
                line-height: 1.2;
                margin-bottom: 4px;
              }

              .stat-label {
                font-size: 0.85rem;
                color: #64748b;
              }
            }
          }
        }

        .detail-categories-section {
          h4 {
            font-size: 1rem;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin-bottom: 12px;
          }

          .detail-categories-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;

            .detail-category-tag {
              font-size: 0.9rem;
              padding: 6px 12px;
              border-radius: 8px;
            }
          }
        }
      }
    }

    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .upload-card,
    .result-card {
      min-height: 500px;
      height: auto;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      display: flex;
      flex-direction: column;

      :deep(.ant-card-head) {
        border-bottom: 1px solid #e5e7eb;
        flex-shrink: 0;

        .ant-card-head-title {
          font-weight: 600;
          color: #1e293b;
        }
      }

      :deep(.ant-card-body) {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 16px;
        overflow: hidden;
      }
    }

    .upload-area {
      margin-bottom: 8px;
      flex-shrink: 0;

      // 完全移除默认的文件列表
      :deep(.ant-upload-list) {
        display: none !important;
      }

      :deep(.ant-upload-list-item) {
        display: none !important;
      }

      :deep(.ant-upload-dragger) {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;

        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
          transition: left 0.5s ease;
        }

        &:hover {
          border-color: var(--theme-primary, #3b82f6);
          background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
          transform: translateY(-2px);

          &::before {
            left: 100%;
          }

          .upload-icon-wrapper .upload-main-icon {
            transform: scale(1.1) rotate(5deg);
            color: #3b82f6;
          }

          .upload-icon-ring {
            opacity: 1;
            transform: scale(1.2);
          }
        }

        &.compact-upload {
          padding: 20px;
        }

        .upload-icon-wrapper {
          position: relative;
          display: inline-block;
          margin-bottom: 16px;

          .upload-main-icon {
            font-size: 3.5rem;
            color: #3b82f6;
            transition: all 0.3s ease;
            position: relative;
            z-index: 2;
            display: block;
          }

          .upload-icon-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.8);
            width: 80px;
            height: 80px;
            border: 2px solid rgba(59, 130, 246, 0.3);
            border-radius: 50%;
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1;
          }
        }

        .ant-upload-drag-icon {
          display: none; // 隐藏默认图标，使用自定义图标
        }

        .ant-upload-text {
          font-size: 1.1rem;
          color: #1e293b;
          margin-bottom: 8px;
          font-weight: 600;
        }

        .ant-upload-hint {
          color: #64748b;
          font-size: 0.9rem;
          margin-bottom: 12px;
        }

        .upload-features {
          display: flex;
          gap: 8px;
          justify-content: center;
          margin-top: 12px;
          flex-wrap: wrap;

          .feature-tag {
            padding: 4px 12px;
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
            border: 1px solid rgba(59, 130, 246, 0.2);
            transition: all 0.2s ease;

            &:hover {
              background: rgba(59, 130, 246, 0.15);
              transform: translateY(-1px);
            }
          }
        }
      }

      .compact-preview {
        margin-top: 16px;
        padding: 16px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

        .preview-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 2px solid #e5e7eb;

          .preview-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--theme-text-primary, #1e293b);
            display: flex;
            align-items: center;
            gap: 8px;

            &::before {
              content: '📁';
              font-size: 1.1rem;
            }
          }
        }

        .preview-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
          gap: 12px;
          max-height: 200px;
          overflow-y: auto;
          padding-right: 4px;

          /* 自定义滚动条 */
          &::-webkit-scrollbar {
            width: 6px;
          }

          &::-webkit-scrollbar-track {
            background: var(--theme-content-bg, #f0f0f0);
            border-radius: 3px;
          }

          &::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;

            &:hover {
              background: #94a3b8;
            }
          }

          .preview-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            background: white;
            border-radius: 10px;
            border: 2px solid var(--theme-card-border, #e5e7eb);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;

            &::before {
              content: '';
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              height: 3px;
              background: linear-gradient(90deg, #3b82f6, #8b5cf6);
              transform: scaleX(0);
              transition: transform 0.3s ease;
            }

            &:hover {
              border-color: var(--theme-primary, #3b82f6);
              box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
              transform: translateY(-3px);

              &::before {
                transform: scaleX(1);
              }

              .preview-thumb {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
              }
            }

            .preview-thumb {
              width: 60px;
              height: 60px;
              border-radius: 8px;
              background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
              display: flex;
              align-items: center;
              justify-content: center;
              margin-bottom: 8px;
              position: relative;
              overflow: hidden;
              transition: all 0.3s ease;
              border: 2px solid #f1f5f9;

              img,
              video {
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 6px;
                transition: transform 0.3s ease;
              }

              &:hover img,
              &:hover video {
                transform: scale(1.1);
              }

              .file-placeholder {
                font-size: 28px;
                color: #94a3b8;
              }

              .preview-delete-btn {
                position: absolute;
                top: -4px;
                right: -4px;
                width: 22px;
                height: 22px;
                background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                z-index: 10;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 6px rgba(255, 77, 79, 0.4);
                border: 2px solid white;

                :deep(.anticon) {
                  font-size: 11px;
                  color: white;
                }

                &:hover {
                  background: linear-gradient(135deg, #ff7875 0%, #ff9c9c 100%);
                  transform: scale(1.2) rotate(90deg);
                  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.6);
                }

                &:active {
                  transform: scale(0.95) rotate(90deg);
                }
              }
            }

            .preview-name {
              font-size: 0.75rem;
              color: #475569;
              text-align: center;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
              max-width: 90px;
              font-weight: 500;
              line-height: 1.4;
              padding: 0 4px;
            }
          }
        }
      }
    }

    .detection-params {
      margin: 8px 0;
      padding: 8px;
      background: #f8fafc;
      border-radius: 4px;
      border: 1px solid #e2e8f0;

      h4 {
        margin: 0 0 8px 0;
        color: #1e293b;
        font-size: 0.9rem;
        font-weight: 600;
      }

      .param-item {
        label {
          display: block;
          margin-bottom: 4px;
          color: #374151;
          font-weight: 500;
          font-size: 0.8rem;
        }

        .param-value {
          display: inline-block;
          margin-left: 8px;
          color: #3b82f6;
          font-weight: 600;
          font-size: 0.9rem;
        }

        .current-model-info {
          padding: 8px 12px;
          background: #f0f9ff;
          border: 1px solid #0ea5e9;
          border-radius: 6px;

          .model-name {
            color: #0369a1;
            font-weight: 600;
            font-size: 0.9rem;
          }

          .no-model {
            color: #dc2626;
            font-weight: 500;
            font-size: 0.9rem;
          }
        }
      }
    }

    .upload-actions {
      display: flex;
      gap: 6px;
      justify-content: center;
      margin-top: 4px;
      padding: 4px 0;
    }

    .no-results {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex: 1;
      min-height: 300px;
      color: #9ca3af;

      .no-results-icon {
        font-size: 4rem;
        margin-bottom: 16px;
      }

      p {
        margin: 4px 0;
        font-size: 1.1rem;
      }

      .no-results-hint {
        font-size: 0.9rem;
        color: #d1d5db;
      }
    }

    .results-list {
      flex: 1;
      overflow-y: auto;
      min-height: 0;
      max-height: 400px;
      padding-right: 8px;

      /* 自定义滚动条样式 */
      &::-webkit-scrollbar {
        width: 8px;
      }

      &::-webkit-scrollbar-track {
        background: #f0f0f0;
        border-radius: 4px;
        margin: 4px 0;
      }

      &::-webkit-scrollbar-thumb {
        background: #1890ff;
        border-radius: 4px;
        border: 1px solid #f0f0f0;
        min-height: 20px;

        &:hover {
          background: var(--theme-primary, #40a9ff);
        }

        &:active {
          background: var(--theme-primary, #096dd9);
        }
      }

      /* 强制显示滚动条 */
      overflow-y: scroll !important;

      .scroll-hint {
        position: sticky;
        top: 0;
        background: #e6f7ff;
        color: #1890ff;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 12px;
        z-index: 10;
        border: 1px solid #91d5ff;
      }

      .result-item {
        margin-bottom: 16px;
        padding: 12px;
        background: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        min-height: 250px;

        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          border-color: #d1d5db;
        }

        &:last-child {
          margin-bottom: 0;
        }

        .image-comparison {
          margin-bottom: 12px;

          .image-pair {
            display: flex;
            gap: 16px;

            .image-container {
              flex: 1;

              h5 {
                margin: 0 0 8px 0;
                color: #374151;
                font-size: 0.9rem;
                font-weight: 600;
                text-align: center;
              }

              .image-wrapper {
                position: relative;
                width: 100%;
                height: 160px;
                border-radius: 6px;
                border: 2px solid var(--theme-card-border, #e5e7eb);
                overflow: hidden;

                img,
                video {
                  width: 100%;
                  height: 100%;
                  object-fit: cover;
                  transition: all 0.3s ease;

                  &:hover {
                    transform: scale(1.02);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                  }
                }

                video {
                  background: #000;
                }

                .image-loading {
                  position: absolute;
                  top: 0;
                  left: 0;
                  right: 0;
                  bottom: 0;
                  background: #f8fafc;
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: center;
                  gap: 8px;

                  p {
                    margin: 0;
                    color: #64748b;
                    font-size: 0.9rem;
                  }
                }

                .image-error {
                  position: absolute;
                  top: 0;
                  left: 0;
                  right: 0;
                  bottom: 0;
                  background: #fef2f2;
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: center;
                  gap: 8px;

                  p {
                    margin: 0;
                    color: #dc2626;
                    font-size: 0.9rem;
                    font-weight: 500;
                  }

                  .error-actions {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                    justify-content: center;
                  }
                }

                &:hover {
                  border-color: var(--theme-primary, #3b82f6);
                }
              }
            }
          }
        }

        .result-details {
          h4 {
            margin: 0 0 8px 0;
            color: var(--theme-text-primary, #1e293b);
            font-size: 0.95rem;
            font-weight: 600;
          }

          .detection-stats {
            display: flex;
            gap: 12px;
            margin-bottom: 10px;
            padding: 8px;
            background: #f1f5f9;
            border-radius: 4px;

            .stat-item {
              display: flex;
              flex-direction: column;
              align-items: center;

              .stat-label {
                font-size: 0.8rem;
                color: #64748b;
                margin-bottom: 4px;
              }

              .stat-value {
                font-size: 1rem;
                font-weight: 600;
                color: var(--theme-text-primary, #1e293b);
              }
            }
          }

          .detection-categories {
            margin-bottom: 8px;

            h5 {
              margin: 0 0 6px 0;
              color: #374151;
              font-size: 0.85rem;
              font-weight: 600;
            }

            .category-list {
              display: flex;
              flex-wrap: wrap;
              gap: 6px;
            }
          }

          .model-info {
            color: #64748b;
            font-size: 0.75rem;
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px solid #e2e8f0;
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .yolo-detection-page {
    .detection-content {
      .upload-card,
      .result-card {
        min-height: 450px;
      }

      // 经典布局响应式
      &.classic-layout {
        .results-list {
          .results-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
          }
        }
      }

      // 侧边栏布局响应式
      &.sidebar-layout {
        .detail-stats-grid {
          grid-template-columns: repeat(2, 1fr);
        }

        .detail-image-pair {
          grid-template-columns: 1fr;
          gap: 12px;

          .detail-image-wrapper {
            height: 300px;
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .yolo-detection-page {
    padding: 16px;

    .detection-content {
      :deep(.ant-col) {
        margin-bottom: 16px;
      }

      .upload-card,
      .result-card {
        min-height: 400px;
      }

      // 经典布局小屏幕响应式
      &.classic-layout {
        .results-list {
          .results-grid {
            grid-template-columns: 1fr;
            gap: 12px;
          }
        }
      }

      // 侧边栏布局移动端
      &.sidebar-layout {
        .sidebar-list-card {
          height: auto;
          min-height: 400px;
          max-height: 500px;
        }

        .sidebar-detail-card {
          min-height: auto;
        }

        .detail-stats-grid {
          grid-template-columns: 1fr;
        }

        .detail-image-pair {
          grid-template-columns: 1fr;

          .detail-image-wrapper {
            height: 250px;
          }
        }
      }

      .upload-area {
        .compact-preview {
          .preview-grid {
            grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            max-height: 50px;
          }
        }
      }
    }
  }
}

@media (max-width: 576px) {
  .yolo-detection-page {
    padding: 12px;

    .detection-content {
      .upload-card,
      .result-card {
        min-height: 350px;
      }

      .upload-area {
        .compact-preview {
          .preview-grid {
            grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
            max-height: 40px;
          }

          .preview-card {
            .preview-thumb {
              width: 28px;
              height: 28px;
            }
          }
        }
      }
    }
  }
}

/* 警告框样式 */
.alert-modal-content {
  text-align: center;
  padding: 20px 0;

  .alert-icon {
    margin-bottom: 20px;
  }

  .alert-message {
    margin-bottom: 20px;

    pre {
      background: var(--theme-page-bg, #f5f5f5);
      padding: 16px;
      border-radius: 8px;
      border: 1px solid #d9d9d9;
      font-family: 'Courier New', monospace;
      font-size: 14px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
      text-align: left;
      margin: 0;
    }
  }

  .alert-tips {
    background: #f6ffed;
    border: 1px solid #b7eb8f;
    border-radius: 8px;
    padding: 16px;

    p {
      margin: 0;
      color: #52c41a;
      font-size: 14px;
      line-height: 1.5;

      strong {
        color: #389e0d;
      }
    }
  }
}
</style>

<style>
/* 图片模态框样式 */
.image-modal .ant-modal-body {
  padding: 0 !important;
}

.image-modal .ant-modal-content {
  background: transparent;
  box-shadow: none;
}

.image-modal .ant-modal-header {
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid #e5e7eb;
  border-radius: 8px 8px 0 0;
}

.image-modal .ant-modal-footer {
  background: rgba(255, 255, 255, 0.95);
  border-top: 1px solid #e5e7eb;
  border-radius: 0 0 8px 8px;
}

/* 视频模态框样式 */
.video-modal .ant-modal-body {
  padding: 0 !important;
}

.video-modal .ant-modal-content {
  background: transparent;
  box-shadow: none;
}

.video-modal .ant-modal-header {
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid #e5e7eb;
  border-radius: 8px 8px 0 0;
}

.video-modal .ant-modal-footer {
  background: rgba(255, 255, 255, 0.95);
  border-top: 1px solid #e5e7eb;
  border-radius: 0 0 8px 8px;
}

/* 警告框美化样式 */
.alert-modal {
  .ant-modal-content {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    animation: modalSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .ant-modal-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    padding: 20px 24px;

    .ant-modal-title {
      color: white;
      font-size: 18px;
      font-weight: 600;
      text-align: center;
    }
  }

  .ant-modal-body {
    padding: 30px 24px;
    background: #fafafa;
  }

  .ant-modal-footer {
    background: white;
    border-top: 1px solid #f0f0f0;
    padding: 16px 24px;

    .ant-btn {
      border-radius: 8px;
      font-weight: 500;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
    }

    .ant-btn-primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;

      &:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
      }
    }
  }
}

.alert-modal-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;

  .alert-icon-container {
    margin-bottom: 24px;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;

    .alert-icon-wrapper {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 80px;
      height: 80px;
      border-radius: 50%;
      animation: iconBounce 0.6s ease-out 0.2s both;

      &.high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
      }

      &.medium {
        background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%);
        box-shadow: 0 8px 20px rgba(255, 167, 38, 0.3);
      }

      .alert-icon {
        font-size: 36px;
        color: white;
        animation: iconPulse 2s ease-in-out infinite;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .pulse-ring {
        position: absolute;
        top: -10px;
        left: -10px;
        right: -10px;
        bottom: -10px;
        border: 2px solid;
        border-radius: 50%;
        animation: pulseRing 2s ease-out infinite;

        &.high {
          border-color: rgba(255, 107, 107, 0.4);
        }

        &.medium {
          border-color: rgba(255, 167, 38, 0.4);
        }
      }

      .pulse-ring-2 {
        position: absolute;
        top: -20px;
        left: -20px;
        right: -20px;
        bottom: -20px;
        border: 1px solid;
        border-radius: 50%;
        animation: pulseRing2 2s ease-out infinite 0.5s;

        &.high {
          border-color: rgba(255, 107, 107, 0.2);
        }

        &.medium {
          border-color: rgba(255, 167, 38, 0.2);
        }
      }
    }
  }

  .alert-message {
    margin-bottom: 24px;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;

    .alert-title {
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 8px;

      .alert-level-text {
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: textShine 2s ease-in-out infinite;
        text-align: center;
      }

      .alert-detected {
        font-size: 18px;
        color: #666;
        animation: textFadeIn 0.8s ease-out 0.4s both;
        text-align: center;
      }
    }

    .alert-details {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      animation: slideUp 0.6s ease-out 0.3s both;
      width: 100%;
      max-width: 400px;
      text-align: center;

      pre {
        margin: 0;
        font-family:
          'SF Pro Text',
          -apple-system,
          BlinkMacSystemFont,
          sans-serif;
        font-size: 14px;
        line-height: 1.6;
        color: #333;
        white-space: pre-wrap;
        word-break: break-word;
        text-align: center;
      }
    }
  }

  .alert-tips {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    animation: slideUp 0.6s ease-out 0.5s both;
    width: 100%;
    max-width: 400px;
    text-align: center;

    &.high {
      border-left: 4px solid #ff6b6b;
    }

    &.medium {
      border-left: 4px solid #ffa726;
    }

    .tips-icon {
      flex-shrink: 0;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;

      &.high {
        background: rgba(255, 107, 107, 0.1);
        color: #ff6b6b;
      }

      &.medium {
        background: rgba(255, 167, 38, 0.1);
        color: #ffa726;
      }
    }

    .tips-content {
      flex: 1;
      text-align: center;

      p {
        margin: 0;
        font-size: 14px;
        line-height: 1.6;
        color: #666;
        text-align: center;

        strong {
          color: #333;
        }
      }
    }
  }
}

/* 动画定义 */
@keyframes modalSlideIn {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(-50px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes iconBounce {
  0% {
    opacity: 0;
    transform: scale(0.3) rotate(-10deg);
  }
  50% {
    transform: scale(1.1) rotate(5deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0deg);
  }
}

@keyframes iconPulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

@keyframes pulseRing {
  0% {
    opacity: 1;
    transform: scale(0.8);
  }
  100% {
    opacity: 0;
    transform: scale(1.3);
  }
}

@keyframes pulseRing2 {
  0% {
    opacity: 1;
    transform: scale(0.6);
  }
  100% {
    opacity: 0;
    transform: scale(1.5);
  }
}

@keyframes textShine {
  0%,
  100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

@keyframes textFadeIn {
  0% {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 居中动画增强 */
@keyframes centerScale {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes centerFadeIn {
  0% {
    opacity: 0;
    transform: translateY(15px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .alert-modal {
    .ant-modal {
      width: 90% !important;
      max-width: 400px;
      margin: 0 auto;
    }

    .alert-modal-content {
      .alert-icon-container {
        .alert-icon-wrapper {
          width: 60px;
          height: 60px;

          .alert-icon {
            font-size: 28px;
          }
        }
      }

      .alert-message {
        .alert-title {
          flex-direction: column;
          gap: 4px;

          .alert-level-text {
            font-size: 20px;
          }

          .alert-detected {
            font-size: 16px;
          }
        }

        .alert-details {
          max-width: 100%;
          padding: 16px;

          pre {
            font-size: 13px;
          }
        }
      }

      .alert-tips {
        max-width: 100%;
        padding: 16px;
        flex-direction: column;
        text-align: center;
        gap: 8px;

        .tips-icon {
          align-self: center;
        }

        .tips-content {
          text-align: center;

          p {
            font-size: 13px;
          }
        }
      }
    }
  }
}

/* 超小屏幕适配 */
@media (max-width: 480px) {
  .alert-modal {
    .ant-modal {
      width: 95% !important;
      max-width: 350px;
    }

    .alert-modal-content {
      .alert-icon-container .alert-icon-wrapper {
        width: 50px;
        height: 50px;

        .alert-icon {
          font-size: 24px;
        }
      }

      .alert-message {
        .alert-title {
          .alert-level-text {
            font-size: 18px;
          }

          .alert-detected {
            font-size: 14px;
          }
        }

        .alert-details {
          padding: 12px;

          pre {
            font-size: 12px;
            line-height: 1.4;
          }
        }
      }

      .alert-tips {
        padding: 12px;

        .tips-content p {
          font-size: 12px;
        }
      }
    }
  }
}
</style>
