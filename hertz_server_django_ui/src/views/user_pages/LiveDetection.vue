<template>
  <div class="live-detection-page">
    <div class="page-header">
      <h1 class="page-title">
        <VideoCameraOutlined class="title-icon" />
        实时检测
      </h1>
      <p class="page-description">实时接收并显示YOLO检测结果</p>
    </div>

    <div class="detection-controls">
      <a-row :gutter="[16, 16]">
        <!-- 摄像头控制 -->
        <a-col :xs="24" :sm="24" :md="12" :lg="12">
          <a-card title="摄像头控制" class="control-card">
            <a-space direction="vertical" style="width: 100%">
              <div class="camera-preview">
                <video
                  ref="videoElement"
                  autoplay
                  playsinline
                  class="camera-video"
                  :class="{ 'camera-active': isCameraActive }"
                ></video>
                <canvas ref="overlayCanvas" class="overlay-canvas"></canvas>
                <div v-if="inferenceMode === 'onnx' && isCameraActive" class="overlay-hud">
                  <span class="hud-chip">FPS: {{ onnxFps > 0 ? onnxFps.toFixed(1) : '--' }}</span>
                  <span class="hud-chip">Detections: {{ latestResult?.object_count || 0 }}</span>
                </div>
                <div v-if="!isCameraActive" class="camera-placeholder">
                  <VideoCameraOutlined />
                  <p>摄像头未开启</p>
                </div>
              </div>
              <a-space>
                <a-button
                  type="primary"
                  :loading="cameraLoading"
                  :disabled="isCameraActive"
                  @click="startCamera"
                  size="large"
                >
                  <VideoCameraOutlined />
                  开启摄像头
                </a-button>
                <a-button danger :disabled="!isCameraActive" @click="stopCamera" size="large">
                  <StopOutlined />
                  关闭摄像头
                </a-button>
              </a-space>
              <div class="camera-status">
                <a-tag :color="isCameraActive ? 'success' : 'default'" class="status-tag">
                  {{ isCameraActive ? '摄像头已开启' : '摄像头已关闭' }}
                </a-tag>
              </div>
            </a-space>
          </a-card>
        </a-col>

        <!-- 检测控制 -->
        <a-col :xs="24" :sm="24" :md="12" :lg="12">
          <a-card title="检测控制" class="control-card">
            <a-space direction="vertical" style="width: 100%">
              <a-form :model="detectionConfig" layout="vertical" size="small">
                <a-form-item label="推理模式">
                  <a-radio-group v-model:value="inferenceMode" @change="handleInferenceModeChange">
                    <a-radio value="pt">
                      <RobotOutlined style="margin-right: 4px" />
                      PT推理（后端）
                    </a-radio>
                    <a-radio value="onnx">
                      <ThunderboltOutlined style="margin-right: 4px" />
                      ONNX推理（前端）
                    </a-radio>
                  </a-radio-group>
                </a-form-item>

                <!-- PT推理模式配置 -->
                <template v-if="inferenceMode === 'pt'">
                  <a-form-item label="检测模式">
                    <a-radio-group v-model:value="detectionConfig.mode">
                      <a-radio value="webcam">摄像头检测</a-radio>
                      <a-radio value="push">推送模式</a-radio>
                    </a-radio-group>
                  </a-form-item>
                  <a-form-item label="返回带框图像">
                    <a-switch v-model:checked="detectionConfig.sendFrame" />
                  </a-form-item>
                </template>

                <!-- ONNX推理模式配置 -->
                <template v-if="inferenceMode === 'onnx'">
                  <a-form-item label="ONNX模型">
                    <div class="onnx-controls">
                      <div class="row">
                        <a-input-group compact style="width: 100%">
                          <a-select
                            v-model:value="selectedOnnxModel"
                            placeholder="选择ONNX模型"
                            :disabled="onnxModels.length === 0"
                            style="width: calc(100% - 200px)"
                          >
                            <a-select-option
                              v-for="model in onnxModels"
                              :key="model.path"
                              :value="model.path"
                            >
                              {{ model.name }} ({{ model.path }})
                            </a-select-option>
                          </a-select>
                          <a-button
                            style="width: 100px"
                            :loading="modelLoading"
                            :disabled="!selectedOnnxModel"
                            type="primary"
                            ghost
                            @click="loadOnnxModel"
                          >
                            <ThunderboltOutlined />
                            {{ onnxModelLoaded ? '重新加载' : '加载模型' }}
                          </a-button>
                          <a-button style="width: 100px" @click="handleShowUploadModal">
                            <UploadOutlined /> 上传转换
                          </a-button>
                        </a-input-group>
                      </div>
                      <div class="row">
                        <a-button style="width: 80px" @click="loadOnnxModelList">
                          <ReloadOutlined /> 刷新
                        </a-button>
                      </div>
                      <div class="row status">
                        <a-tag :color="onnxModelLoaded ? 'success' : 'error'">
                          {{ onnxModelLoaded ? '模型已加载' : '模型未加载' }}
                        </a-tag>
                        <span v-if="selectedOnnxModel" class="path-text">{{
                          selectedOnnxModel
                        }}</span>
                      </div>
                    </div>
                  </a-form-item>
                  <a-form-item label="NMS阈值">
                    <a-slider
                      v-model:value="detectionConfig.nmsThreshold"
                      :min="0.1"
                      :max="1"
                      :step="0.05"
                      :marks="{ 0.45: '0.45' }"
                    />
                    <span style="margin-left: 8px">{{ detectionConfig.nmsThreshold }}</span>
                  </a-form-item>
                </template>

                <a-form-item label="置信度阈值">
                  <a-slider
                    v-model:value="detectionConfig.confidence"
                    :min="0.1"
                    :max="1"
                    :step="0.05"
                    :marks="{ 0.5: '0.5' }"
                  />
                  <span style="margin-left: 8px">{{ detectionConfig.confidence }}</span>
                </a-form-item>
              </a-form>
              <a-space>
                <a-button
                  type="primary"
                  :loading="connecting || isDetecting || modelLoading"
                  :disabled="
                    !isCameraActive || isDetecting || (inferenceMode === 'onnx' && !onnxModelLoaded)
                  "
                  @click="startDetection"
                  size="large"
                >
                  <PlayCircleOutlined />
                  开始检测
                </a-button>
                <a-button danger :disabled="!isDetecting" @click="stopDetection" size="large">
                  <StopOutlined />
                  停止检测
                </a-button>
                <a-button @click="openLivePreview" :disabled="!isCameraActive"> 放大预览 </a-button>
                <a-button @click="clearResults" :disabled="detectionResults.length === 0">
                  <ClearOutlined />
                  清空结果
                </a-button>
              </a-space>
              <div class="connection-status">
                <a-tag
                  v-if="inferenceMode === 'pt'"
                  :color="isConnected ? 'success' : 'error'"
                  class="status-tag"
                >
                  {{ isConnected ? '已连接' : '未连接' }}
                </a-tag>
                <a-tag
                  v-if="inferenceMode === 'onnx'"
                  :color="onnxModelLoaded ? 'success' : 'error'"
                  class="status-tag"
                >
                  {{ onnxModelLoaded ? '模型已加载' : '模型未加载' }}
                </a-tag>
                <a-tag :color="isDetecting ? 'processing' : 'default'" class="status-tag">
                  {{ isDetecting ? '检测中' : '未检测' }}
                </a-tag>
                <span class="status-text">
                  检测结果: {{ detectionResults.length > 0 ? '1' : '0' }}
                </span>
              </div>
            </a-space>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <div class="detection-results" v-if="inferenceMode === 'pt'">
      <a-spin :spinning="loading">
        <div v-if="detectionResults.length === 0" class="no-data">
          <VideoCameraOutlined class="no-data-icon" />
          <p>暂无检测结果</p>
          <p class="no-data-hint">点击"开始检测"接收实时检测数据</p>
        </div>

        <div v-else-if="latestResult" class="latest-result-container">
          <a-card class="latest-result-card" @click="viewDetails(latestResult)">
            <template #title>
              <div class="result-card-header">
                <div class="header-left">
                  <span class="new-badge">最新</span>
                  <span class="result-title-text">实时检测结果</span>
                </div>
                <a-tag color="success" class="status-badge">
                  <CheckCircleOutlined />
                  检测完成
                </a-tag>
              </div>
            </template>

            <div class="latest-result-content">
              <div class="result-image-wrapper">
                <div class="result-image">
                  <img
                    v-if="latestResult?.frame"
                    :src="latestResult.frame"
                    alt="最新检测结果"
                    @error="handleImageError"
                  />
                  <div v-else class="image-placeholder">
                    <FileImageOutlined />
                    <p>无图像数据</p>
                  </div>
                  <div class="image-overlay-info">
                    <div class="overlay-stats">
                      <div class="stat-item">
                        <span class="stat-icon">🎯</span>
                        <div class="stat-content">
                          <span class="stat-number">{{ latestResult?.object_count || 0 }}</span>
                          <span class="stat-label">检测目标</span>
                        </div>
                      </div>
                      <div
                        class="stat-item"
                        v-if="
                          latestResult?.avg_confidence !== null &&
                          latestResult?.avg_confidence !== undefined
                        "
                      >
                        <span class="stat-icon">📊</span>
                        <div class="stat-content">
                          <span class="stat-number"
                            >{{ (latestResult.avg_confidence * 100).toFixed(1) }}%</span
                          >
                          <span class="stat-label">平均置信度</span>
                        </div>
                      </div>
                      <div class="stat-item" v-if="latestResult?.timestamp">
                        <span class="stat-icon">⏰</span>
                        <div class="stat-content">
                          <span class="stat-number">{{ latestResult.timestamp }}</span>
                          <span class="stat-label">检测时间</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="result-details">
                <div class="detection-summary">
                  <h4 class="summary-title">
                    <FileSearchOutlined />
                    检测详情
                  </h4>
                  <div
                    class="detection-tags"
                    v-if="latestResult?.categories && latestResult.categories.length > 0"
                  >
                    <a-tag
                      v-for="(category, idx) in latestResult.categories"
                      :key="idx"
                      :color="getTagColor(category)"
                      class="detection-tag"
                    >
                      <span class="tag-category">{{ category }}</span>
                      <span
                        v-if="
                          latestResult?.confidence_scores && latestResult.confidence_scores[idx]
                        "
                        class="tag-score"
                      >
                        {{ (latestResult.confidence_scores[idx] * 100).toFixed(1) }}%
                      </span>
                    </a-tag>
                  </div>
                  <div v-else class="no-detections">
                    <span>本次检测未发现目标</span>
                  </div>
                </div>
              </div>
            </div>
          </a-card>
        </div>
      </a-spin>
    </div>

    <!-- 详情模态框 -->
    <a-modal v-model:visible="detailModalVisible" title="检测详情" width="800px" :footer="null">
      <div v-if="selectedResult" class="detail-content">
        <div class="detail-image">
          <img v-if="selectedResult.frame" :src="selectedResult.frame" alt="检测详情" />
          <div v-else class="image-placeholder">
            <FileImageOutlined />
            <p>无图像数据</p>
          </div>
        </div>
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="检测时间">
            {{ selectedResult.timestamp || '未知' }}
          </a-descriptions-item>
          <a-descriptions-item label="目标数量">
            {{ selectedResult.object_count || 0 }}
          </a-descriptions-item>
          <a-descriptions-item label="平均置信度" :span="2">
            {{
              selectedResult.avg_confidence !== null
                ? (selectedResult.avg_confidence * 100).toFixed(2) + '%'
                : 'N/A'
            }}
          </a-descriptions-item>
          <a-descriptions-item label="检测类别" :span="2">
            <div class="detail-detections">
              <a-tag
                v-for="(category, idx) in selectedResult.categories"
                :key="idx"
                :color="getTagColor(category)"
                class="detail-tag"
              >
                {{ category }}:
                <span
                  v-if="selectedResult.confidence_scores && selectedResult.confidence_scores[idx]"
                >
                  {{ (selectedResult.confidence_scores[idx] * 100).toFixed(1) }}%
                </span>
              </a-tag>
            </div>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>

    <!-- ONNX模型上传和转换弹窗 -->
    <a-modal
      v-model:visible="onnxUploadModalVisible"
      title="上传并转换ONNX模型"
      :confirm-loading="onnxUploading || onnxConverting"
      :ok-button-props="{ disabled: onnxUploading || onnxConverting }"
      @ok="handleOnnxUpload"
      @cancel="handleOnnxUploadCancel"
      width="600px"
      :mask-closable="!onnxUploading && !onnxConverting"
      :z-index="10000"
    >
      <a-form layout="vertical">
        <a-form-item label="模型文件（.pt格式）" required>
          <a-upload
            v-model:file-list="onnxFileList"
            :before-upload="beforeOnnxUpload"
            accept=".pt"
            :max-count="1"
            :show-upload-list="true"
            @change="handleFileChange"
            list-type="text"
          >
            <a-button>
              <UploadOutlined />
              选择.pt文件
            </a-button>
          </a-upload>
          <div style="margin-top: 8px; color: #999; font-size: 12px">
            支持上传.pt格式的PyTorch模型文件，系统将自动转换为ONNX格式
          </div>
          <div v-if="onnxFileList.length > 0" style="margin-top: 8px; color: #52c41a">
            ✅ 已选择文件: {{ onnxFileList[0].name || '未知文件' }}
            <span v-if="onnxFileList[0].size">
              ({{ ((onnxFileList[0].size || 0) / 1024 / 1024).toFixed(2) }} MB)
            </span>
          </div>
          <div v-if="fileError" style="margin-top: 8px; color: #ff4d4f">❌ {{ fileError }}</div>
        </a-form-item>

        <a-form-item label="模型名称" required>
          <a-input v-model:value="onnxUploadForm.name" placeholder="请输入模型名称" />
        </a-form-item>

        <a-form-item label="模型版本">
          <a-input v-model:value="onnxUploadForm.version" placeholder="如：v1.0" />
        </a-form-item>

        <a-form-item label="模型描述">
          <a-textarea
            v-model:value="onnxUploadForm.description"
            placeholder="请输入模型描述"
            :rows="3"
          />
        </a-form-item>

        <!-- 转换状态显示 -->
        <a-form-item v-if="onnxConverting || onnxConversionStatus">
          <div
            style="
              padding: 16px;
              background: #f0f9ff;
              border-radius: 8px;
              border: 1px solid #91d5ff;
            "
          >
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px">
              <a-spin :spinning="onnxConverting" />
              <span style="font-weight: 600; color: #1890ff">{{
                onnxConversionStatus || '准备转换...'
              }}</span>
            </div>
            <a-progress
              v-if="onnxConverting"
              :percent="onnxConversionProgress"
              :status="onnxConversionProgress === 100 ? 'success' : 'active'"
              :show-info="true"
            />
            <div
              v-if="onnxConversionStatus && !onnxConverting"
              style="color: #52c41a; font-size: 14px"
            >
              ✅ {{ onnxConversionStatus }}
            </div>
          </div>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 直播预览放大 -->
    <a-modal
      v-model:visible="livePreviewVisible"
      title="摄像头预览"
      width="80%"
      :footer="null"
      @cancel="closeLivePreview"
    >
      <div style="display: flex; justify-content: center; align-items: center; background: #000">
        <video
          ref="modalVideo"
          style="width: 100%; max-height: 70vh; object-fit: contain"
          autoplay
          playsinline
        ></video>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import {
  VideoCameraOutlined,
  PlayCircleOutlined,
  StopOutlined,
  ClearOutlined,
  FileImageOutlined,
  CheckCircleOutlined,
  FileSearchOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  UploadOutlined,
  ReloadOutlined,
} from '@ant-design/icons-vue';
import { getFullFileUrl, getWsBaseUrl, getBackendBaseUrl } from '@/utils/hertz_url';
import { yoloDetector, type YOLODetectionResult } from '@/utils/yolo_frontend';
import { yoloApi } from '@/api/yolo';

// 推理模式
const inferenceMode = ref<'pt' | 'onnx'>('pt');

// WebSocket连接（PT推理模式使用）
let ws: WebSocket | null = null;
const wsUrl = `${getWsBaseUrl()}/ws/yolo/live/`;

// 响应式数据
const loading = ref(false);
const connecting = ref(false);
const isConnected = ref(false);
const detectionResults = ref<any[]>([]);
const detailModalVisible = ref(false);
const selectedResult = ref<any>(null);
const livePreviewVisible = ref(false);
const modalVideo = ref<HTMLVideoElement | null>(null);

// ONNX推理相关
const onnxModelLoaded = ref(false);
const modelLoading = ref(false);
const selectedOnnxModel = ref<string>('');
const onnxModels = ref<Array<{ name: string; path: string }>>([]);
// ONNX模型配置（类别名称会根据模型自动调整）
const onnxModelConfig = ref({
  classNames: [] as string[], // 初始为空，加载模型时从后端获取或使用默认值
});

// 摄像头相关
const videoElement = ref<HTMLVideoElement | null>(null);
const overlayCanvas = ref<HTMLCanvasElement | null>(null);
const isCameraActive = ref(false);
const cameraLoading = ref(false);
let stream: MediaStream | null = null;

// 检测状态
const isDetecting = ref(false);
const onnxFps = ref(0);

// 计算最新检测结果
const latestResult = computed(() => {
  return detectionResults.value.length > 0 ? detectionResults.value[0] : null;
});

// ONNX上传相关
const onnxUploadModalVisible = ref(false);
const onnxUploading = ref(false);
const onnxConverting = ref(false);
const onnxConversionProgress = ref(0);
const onnxConversionStatus = ref('');
const onnxUploadForm = ref({
  name: '',
  version: 'v1',
  description: '',
});
const onnxFileList = ref<any[]>([]);
const fileError = ref<string>('');

// 检测配置
const detectionConfig = ref({
  mode: 'push', // 'webcam' | 'push' (PT推理模式使用)
  confidence: 0.5,
  nmsThreshold: 0.45, // ONNX推理模式使用
  sendFrame: true,
  deviceIndex: 0,
  modelId: null as number | null,
});

// PT推理模式定时器
let pushFrameInterval: number | null = null;
const pushFrameRate = 1000 / 10; // 10 FPS

// ONNX推理模式调度（单次完成后再调度下一次，避免重叠）
let onnxDetectionInterval: number | null = null;
const onnxDetectionFrameRate = 1000 / 3; // 约 3 FPS，降低频率减少卡顿
let onnxBusy = false;

// 开启摄像头
const startCamera = async () => {
  if (isCameraActive.value) {
    message.warning('摄像头已经开启');
    return;
  }

  cameraLoading.value = true;

  try {
    // 请求摄像头权限
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'environment', // 优先使用后置摄像头
      },
      audio: false,
    });

    if (videoElement.value && stream) {
      videoElement.value.srcObject = stream;
      // 等待元数据以获取分辨率
      videoElement.value.onloadedmetadata = () => {
        updateOverlaySize();
      };
      isCameraActive.value = true;
      message.success('摄像头已开启');
    }
  } catch (error: any) {
    console.error('❌ 开启摄像头失败:', error);
    let errorMsg = '无法访问摄像头';
    if (error.name === 'NotAllowedError') {
      errorMsg = '请允许访问摄像头权限';
    } else if (error.name === 'NotFoundError') {
      errorMsg = '未找到摄像头设备';
    } else if (error.name === 'NotReadableError') {
      errorMsg = '摄像头被其他应用占用';
    }
    message.error(errorMsg);
  } finally {
    cameraLoading.value = false;
  }
};

// 关闭摄像头
const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach((track) => {
      track.stop();
    });
    stream = null;
  }

  if (videoElement.value) {
    videoElement.value.srcObject = null;
  }
  // 清空覆盖层
  if (overlayCanvas.value) {
    const ctx = overlayCanvas.value.getContext('2d');
    ctx?.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height);
  }

  isCameraActive.value = false;

  // 如果正在检测，停止检测
  if (isDetecting.value) {
    stopDetection();
  }

  message.info('摄像头已关闭');
};

// 打开/关闭 直播预览
const openLivePreview = () => {
  livePreviewVisible.value = true;
  if (modalVideo.value && stream) {
    try {
      // @ts-ignore
      modalVideo.value.srcObject = stream;
      modalVideo.value.play?.();
    } catch {}
  }
};
const closeLivePreview = () => {
  if (modalVideo.value) {
    try {
      modalVideo.value.pause?.();
    } catch {}
  }
};

// 连接WebSocket
const connectWebSocket = () => {
  if (isConnected.value) {
    message.warning('已经连接，请先断开');
    return;
  }

  connecting.value = true;

  try {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('✅ WebSocket连接成功');
      isConnected.value = true;
      connecting.value = false;
      message.success('连接成功');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📥 收到服务器消息:', data);

        // 根据消息类型处理
        if (data.type === 'detection') {
          // 检测结果
          handleDetectionData(data);
        } else if (data.type === 'error') {
          // 错误消息
          message.error(data.message || '检测出错');
          console.error('❌ 服务器错误:', data.message);
        } else {
          // 其他类型消息
          console.warn('⚠️ 未知消息类型:', data);
        }
      } catch (error) {
        console.error('❌ 解析数据失败:', error);
        message.error('数据格式错误');
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket错误:', error);
      connecting.value = false;
      message.error('连接失败，请检查网络或服务器状态');
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket连接关闭');
      isConnected.value = false;
      connecting.value = false;
      isDetecting.value = false;
      ws = null;
    };
  } catch (error) {
    console.error('❌ 创建WebSocket连接失败:', error);
    connecting.value = false;
    message.error('无法创建连接，请检查URL是否正确');
  }
};

// 推理模式切换处理
const handleInferenceModeChange = () => {
  // 如果正在检测，先停止
  if (isDetecting.value) {
    stopDetection();
  }

  // 如果切换到ONNX模式，加载已保存的模型列表
  if (inferenceMode.value === 'onnx') {
    loadOnnxModelList();
  }
};

// 开始检测（根据推理模式选择）
const startDetection = async () => {
  if (!isCameraActive.value) {
    message.warning('请先开启摄像头');
    return;
  }

  if (inferenceMode.value === 'onnx') {
    // ONNX推理模式
    if (!onnxModelLoaded.value) {
      message.warning('请先加载ONNX模型');
      return;
    }
    startOnnxDetection();
  } else {
    // PT推理模式（后端）
    // 先连接WebSocket（如果未连接）
    if (!isConnected.value) {
      connectWebSocket();
      // 等待连接成功
      let retryCount = 0;
      const checkConnection = setInterval(() => {
        retryCount++;
        if (isConnected.value && ws) {
          clearInterval(checkConnection);
          // 连接成功后开始检测
          if (detectionConfig.value.mode === 'push') {
            startPushMode();
          } else {
            startWebcamMode();
          }
        } else if (retryCount > 50) {
          // 5秒超时
          clearInterval(checkConnection);
          message.error('连接超时，请重试');
        }
      }, 100);
      return;
    }

    // 已连接，直接开始检测
    if (detectionConfig.value.mode === 'push') {
      startPushMode();
    } else {
      startWebcamMode();
    }
  }
};

// 开始ONNX推理检测
const startOnnxDetection = async () => {
  if (!videoElement.value || !onnxModelLoaded.value) {
    message.error('视频元素或模型未初始化');
    return;
  }

  isDetecting.value = true;
  message.success('开始ONNX实时检测');

  // 以递归计时的方式调度，保证不会重叠
  const loop = async () => {
    if (!isDetecting.value) return;
    await performOnnxDetection();
    onnxDetectionInterval = window.setTimeout(loop, onnxDetectionFrameRate);
  };
  await performOnnxDetection();
  onnxDetectionInterval = window.setTimeout(loop, onnxDetectionFrameRate);
};

// 执行ONNX单次检测
const performOnnxDetection = async () => {
  if (!videoElement.value || !isDetecting.value || !onnxModelLoaded.value || onnxBusy) {
    return;
  }

  try {
    onnxBusy = true;
    const video = videoElement.value;

    // 确保视频已准备好
    if (video.readyState < video.HAVE_CURRENT_DATA) {
      return;
    }

    // 使用前端ONNX检测
    const result: YOLODetectionResult = await yoloDetector.detect(
      video,
      detectionConfig.value.confidence,
      detectionConfig.value.nmsThreshold
    );

    // 处理检测结果
    handleOnnxDetectionResult(result);
    // 在视频覆盖层上绘制
    drawOnOverlay(result);
  } catch (error: any) {
    console.error('❌ ONNX检测失败:', error);
    // 不显示错误消息，避免频繁弹窗
  } finally {
    onnxBusy = false;
  }
};

// 处理ONNX检测结果
const handleOnnxDetectionResult = (result: YOLODetectionResult) => {
  const detectionResult = {
    timestamp: new Date().toLocaleTimeString('zh-CN'),
    object_count: result.object_count,
    categories: result.detected_categories,
    confidence_scores: result.confidence_scores,
    avg_confidence: result.avg_confidence,
    frame: null,
    detections: result.detections.map((det) => ({
      class: det.class_name,
      confidence: det.confidence,
      bbox: det.bbox,
    })),
    status: 'success',
    processing_time: result.processing_time,
  };

  // 只保留最新的一条结果，直接替换
  detectionResults.value = [detectionResult];
  // 更新 FPS
  if (typeof result.processing_time === 'number' && result.processing_time > 0) {
    onnxFps.value = 1 / result.processing_time;
  }
};

// 计算并更新覆盖层尺寸
const updateOverlaySize = () => {
  if (!videoElement.value || !overlayCanvas.value) return;
  const vw = videoElement.value.clientWidth;
  const vh = videoElement.value.clientHeight;
  if (vw && vh) {
    overlayCanvas.value.width = vw;
    overlayCanvas.value.height = vh;
  }
};

// 在覆盖层上绘制检测框
const drawOnOverlay = (result: YOLODetectionResult) => {
  if (!videoElement.value || !overlayCanvas.value) return;
  updateOverlaySize();
  const ctx = overlayCanvas.value.getContext('2d');
  if (!ctx) return;
  ctx.clearRect(0, 0, overlayCanvas.value.width, overlayCanvas.value.height);

  const vw = videoElement.value.videoWidth || overlayCanvas.value.width;
  const vh = videoElement.value.videoHeight || overlayCanvas.value.height;
  const scaleX = overlayCanvas.value.width / vw;
  const scaleY = overlayCanvas.value.height / vh;

  // 颜色表
  const colors: Record<string, string> = {};
  const palette = ['#00FF88', '#FF6B6B', '#4ECDC4', '#45B7D1', '#F7DC6F', '#BB8FCE', '#85C1E2'];

  result.detections.forEach((d, i) => {
    const key = d.class_name;
    if (!colors[key]) colors[key] = palette[i % palette.length];
    const { x, y, width, height } = d.bbox;
    const sx = x * scaleX;
    const sy = y * scaleY;
    const sw = width * scaleX;
    const sh = height * scaleY;
    ctx.strokeStyle = colors[key];
    ctx.lineWidth = 2;
    ctx.strokeRect(sx, sy, sw, sh);
    const label = `${key} ${(d.confidence * 100).toFixed(1)}%`;
    ctx.fillStyle = colors[key];
    ctx.font = '14px Arial';
    const w = ctx.measureText(label).width + 8;
    const h = 18;
    ctx.fillRect(sx, Math.max(0, sy - h), w, h);
    ctx.fillStyle = '#fff';
    ctx.fillText(label, sx + 4, Math.max(12, sy - 4));
  });
};

// 监听窗口尺寸变化，保持叠加层对齐
window.addEventListener('resize', () => updateOverlaySize());

// 开始摄像头检测模式（后端取流）
const startWebcamMode = () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    message.error('WebSocket未连接');
    return;
  }

  try {
    const commandData = JSON.stringify({
      action: 'start',
      source: 'webcam',
      device_index: detectionConfig.value.deviceIndex,
      confidence: detectionConfig.value.confidence,
      send_frame: detectionConfig.value.sendFrame,
    });
    ws.send(commandData);
    console.log('📤 发送开始检测命令（摄像头模式）:', commandData);
    isDetecting.value = true;
    message.success('开始检测（摄像头模式）');
  } catch (error) {
    console.error('❌ 发送命令失败:', error);
    message.error('发送命令失败');
  }
};

// 开始推送模式（前端推送帧）
const startPushMode = () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    message.error('WebSocket未连接');
    return;
  }

  try {
    // 发送开启推送模式命令
    const commandData = JSON.stringify({
      type: 'start_detection',
      confidence: detectionConfig.value.confidence,
      send_frame: detectionConfig.value.sendFrame,
    });
    ws.send(commandData);
    console.log('📤 开启推送模式:', commandData);

    isDetecting.value = true;

    // 开始定时推送帧
    pushFrameInterval = window.setInterval(() => {
      captureAndSendFrame();
    }, pushFrameRate);

    message.success('开始检测（推送模式）');
  } catch (error) {
    console.error('❌ 开启推送模式失败:', error);
    message.error('开启推送模式失败');
  }
};

// 捕获摄像头帧并发送
const captureAndSendFrame = () => {
  if (!videoElement.value || !ws || ws.readyState !== WebSocket.OPEN) {
    return;
  }

  try {
    const canvas = document.createElement('canvas');
    const video = videoElement.value;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // 转换为base64
      const imageData = canvas.toDataURL('image/jpeg', 0.8);

      // 发送检测帧
      const frameData = JSON.stringify({
        type: 'detect_frame',
        image: imageData,
        confidence: detectionConfig.value.confidence,
        send_frame: detectionConfig.value.sendFrame,
      });

      ws.send(frameData);
    }
  } catch (error) {
    console.error('❌ 捕获帧失败:', error);
  }
};

// 停止检测
const stopDetection = () => {
  if (inferenceMode.value === 'onnx') {
    // 停止ONNX检测定时器
    if (onnxDetectionInterval) {
      clearTimeout(onnxDetectionInterval);
      onnxDetectionInterval = null;
    }
  } else {
    // 停止PT推理模式的定时器
    if (pushFrameInterval) {
      clearInterval(pushFrameInterval);
      pushFrameInterval = null;
    }

    if (ws && isConnected.value) {
      if (detectionConfig.value.mode === 'push') {
        // 停止推送模式
        try {
          const commandData = JSON.stringify({
            type: 'stop_detection',
          });
          ws.send(commandData);
          console.log('📤 停止推送模式');
        } catch (error) {
          console.error('❌ 发送停止命令失败:', error);
        }
      } else {
        // 停止摄像头检测模式
        try {
          const commandData = JSON.stringify({
            action: 'stop',
          });
          ws.send(commandData);
          console.log('📤 停止摄像头检测模式');
        } catch (error) {
          console.error('❌ 发送停止命令失败:', error);
        }
      }
    }
  }

  isDetecting.value = false;
  message.info('已停止检测');
};

// 断开WebSocket连接
const disconnectWebSocket = () => {
  if (ws) {
    ws.close();
    ws = null;
    isConnected.value = false;
    isDetecting.value = false;
    message.info('已断开连接');
  }
};

// 处理检测数据
const handleDetectionData = (data: any) => {
  // 解析后端返回的真实数据格式
  const detectionResult = {
    timestamp: data.timestamp || new Date().toLocaleTimeString('zh-CN'),
    object_count: data.object_count || 0,
    categories: data.categories || [],
    confidence_scores: data.confidence_scores || [],
    avg_confidence: data.avg_confidence || null,
    frame: data.frame || null, // base64 图像
    // 为了兼容显示，转换为检测列表格式
    detections: (data.categories || []).map((category: string, index: number) => ({
      class: category,
      confidence: data.confidence_scores?.[index] || 0,
    })),
    status: 'success',
  };

  // 只保留最新的一条结果，直接替换
  detectionResults.value = [detectionResult];
};

// 清空结果
const clearResults = () => {
  detectionResults.value = [];
  message.success('已清空所有结果');
};

// 查看详情
const viewDetails = (result: any) => {
  if (result) {
    selectedResult.value = result;
    detailModalVisible.value = true;
  }
};

// 格式化时间（后端返回的是 HH:MM:SS 格式）
const formatTime = (timestamp: string) => {
  if (!timestamp) return '未知时间';
  // 如果已经是时间格式，直接返回
  if (timestamp.includes(':')) {
    return timestamp;
  }
  // 否则尝试解析为日期
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN');
  } catch {
    return timestamp;
  }
};

// 获取标签颜色
const getTagColor = (className: string) => {
  const colorMap: Record<string, string> = {
    person: 'blue',
    car: 'cyan',
    bicycle: 'green',
    motorcycle: 'orange',
    bus: 'purple',
    truck: 'red',
  };
  return colorMap[className?.toLowerCase()] || 'default';
};

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';
  console.error('❌ 图片加载失败:', target.src);
};

// ONNX上传前处理（验证文件，但不自动上传）
const beforeOnnxUpload = (file: any) => {
  console.log('📁 beforeOnnxUpload 被调用:', file.name, file.size);
  fileError.value = '';

  // 验证文件格式
  const isPt = /\.pt$/i.test(file.name);
  if (!isPt) {
    fileError.value = '只支持.pt格式的模型文件';
    message.error('只支持.pt格式的模型文件');
    return false; // 阻止添加文件
  }

  // 验证文件大小
  const fileSizeMB = file.size / 1024 / 1024;
  if (fileSizeMB > 500) {
    fileError.value = `文件大小不能超过500MB，当前文件大小为 ${fileSizeMB.toFixed(2)} MB`;
    message.error(`文件大小不能超过500MB，当前文件大小为 ${fileSizeMB.toFixed(2)} MB`);
    return false; // 阻止添加文件
  }

  console.log('✅ 文件验证通过，返回false以阻止自动上传');
  // 返回 false 阻止自动上传，但在新版本的ant-design-vue中，文件仍会被添加到列表
  return false;
};

// 处理文件列表变化
const handleFileChange = (info: any) => {
  console.log('📋 handleFileChange 被调用:', info);
  const { fileList, file } = info;

  // 更新文件列表
  onnxFileList.value = fileList;

  // 如果文件被移除，清空错误
  if (fileList.length === 0) {
    fileError.value = '';
    console.log('📋 文件列表已清空');
    return;
  }

  // 验证当前文件
  if (fileList.length > 0) {
    const fileItem = fileList[0];
    const actualFile = fileItem.originFileObj || fileItem || file;

    if (actualFile) {
      console.log('📋 验证文件:', {
        name: actualFile.name,
        size: actualFile.size,
        type: actualFile.type,
      });

      const isPt = /\.pt$/i.test(actualFile.name);
      if (!isPt) {
        fileError.value = '只支持.pt格式的模型文件';
        onnxFileList.value = [];
        message.error('只支持.pt格式的模型文件');
        return;
      }

      const fileSizeMB = actualFile.size / 1024 / 1024;
      if (fileSizeMB > 500) {
        fileError.value = `文件大小不能超过500MB，当前文件大小为 ${fileSizeMB.toFixed(2)} MB`;
        onnxFileList.value = [];
        message.error(`文件大小不能超过500MB，当前文件大小为 ${fileSizeMB.toFixed(2)} MB`);
        return;
      }

      fileError.value = '';
      console.log('✅ 文件验证通过并已添加到列表:', actualFile.name, `${fileSizeMB.toFixed(2)} MB`);
      message.success(`文件已选择: ${actualFile.name} (${fileSizeMB.toFixed(2)} MB)`);
    } else {
      console.warn('⚠️ 无法获取实际文件对象');
    }
  }
};

// 处理显示上传弹窗（包装函数，用于调试）
const handleShowUploadModal = () => {
  console.log('🔴🔴🔴 按钮点击事件触发！');
  console.log('🔴 showOnnxUploadModal 函数是否存在:', typeof showOnnxUploadModal);
  showOnnxUploadModal();
};

// 显示ONNX上传弹窗
const showOnnxUploadModal = () => {
  console.log('🔵 showOnnxUploadModal 被调用');
  console.log('🔵 当前 onnxUploadModalVisible:', onnxUploadModalVisible.value);

  try {
    onnxUploadModalVisible.value = true;
    onnxFileList.value = [];
    fileError.value = '';
    onnxUploadForm.value = {
      name: '',
      version: 'v1',
      description: '',
    };

    console.log('✅ 弹窗状态已更新:', onnxUploadModalVisible.value);
    console.log('✅ 弹窗应该已经显示');

    // 强制触发响应式更新
    nextTick(() => {
      console.log('✅ nextTick 后弹窗状态:', onnxUploadModalVisible.value);
    });
  } catch (error) {
    console.error('❌ 打开弹窗失败:', error);
    message.error('打开上传弹窗失败，请检查控制台');
  }
};

// 处理ONNX上传和转换
const handleOnnxUpload = async () => {
  console.log('🚀 handleOnnxUpload 被调用');
  console.log('📋 当前文件列表:', onnxFileList.value);
  console.log('📋 表单数据:', onnxUploadForm.value);

  if (onnxFileList.value.length === 0) {
    message.error('请选择.pt模型文件');
    console.error('❌ 文件列表为空');
    return;
  }

  if (!onnxUploadForm.value.name) {
    message.error('请输入模型名称');
    console.error('❌ 模型名称为空');
    return;
  }

  // 获取文件对象
  const fileItem = onnxFileList.value[0];
  console.log('📋 文件项:', fileItem);

  // 尝试多种方式获取文件对象
  let file = fileItem.originFileObj || fileItem;

  // 如果是File对象，直接使用
  if (file instanceof File) {
    // 已经是File对象
  } else if (fileItem.file) {
    file = fileItem.file;
  } else if (fileItem.fileList && fileItem.fileList.length > 0) {
    file = fileItem.fileList[0].originFileObj || fileItem.fileList[0];
  }

  if (!file || !(file instanceof File)) {
    message.error('无法获取文件对象，请重新选择文件');
    console.error('❌ 无法获取文件对象:', file);
    return;
  }

  console.log('📤 准备上传文件:', {
    name: file.name,
    size: file.size,
    type: file.type,
  });

  onnxUploading.value = true;
  onnxConverting.value = true;
  onnxConversionProgress.value = 0;
  onnxConversionStatus.value = '正在上传.pt文件并准备转换...';

  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_file', file);
    formData.append('name', onnxUploadForm.value.name);
    formData.append('version', onnxUploadForm.value.version);
    formData.append('description', onnxUploadForm.value.description || '');

    console.log('📋 FormData内容:');
    for (const [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`  ${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
      } else {
        console.log(`  ${key}:`, value);
      }
    }

    console.log('🔄 开始上传.pt文件并调用转换接口...');

    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (onnxConversionProgress.value < 90) {
        onnxConversionProgress.value += 2;
      }
    }, 200);

    // 调用后端转换接口
    const convertResponse = await yoloApi.uploadAndConvertToOnnx(formData);

    clearInterval(progressInterval);
    onnxConversionProgress.value = 95;

    console.log('📋 转换接口响应:', convertResponse);

    if (convertResponse.success && convertResponse.data) {
      onnxConversionStatus.value = '转换完成！正在下载文件...';
      onnxConversionProgress.value = 95;

      // 获取转换后的文件信息
      const onnxUrl =
        convertResponse.data.download_url ||
        convertResponse.data.onnx_url ||
        convertResponse.data.onnx_path ||
        convertResponse.data.onnx_relative_path;
      const onnxFileName =
        convertResponse.data.file_name ||
        `${onnxUploadForm.value.name}_${onnxUploadForm.value.version}.onnx`;

      // 获取labels.json的URL
      const labelsUrl =
        convertResponse.data.labels_download_url || convertResponse.data.labels_relative_path;

      console.log('📥 准备下载文件:', { onnxUrl, onnxFileName, labelsUrl });

      let modelClasses: string[] = [];

      // 1. 先下载并解析labels.json（如果存在）
      if (labelsUrl) {
        try {
          onnxConversionStatus.value = '正在下载类别信息...';
          onnxConversionProgress.value = 96;

          let labelsDownloadUrl = labelsUrl;

          // 如果URL不是完整路径，构建完整URL
          if (!labelsDownloadUrl.startsWith('http')) {
            const baseUrl = getBackendBaseUrl();
            labelsDownloadUrl = labelsDownloadUrl.startsWith('/')
              ? `${baseUrl}${labelsDownloadUrl}`
              : `${baseUrl}/${labelsDownloadUrl}`;
          }

          console.log('🔗 类别文件下载URL:', labelsDownloadUrl);

          // 下载labels.json
          const labelsResponse = await fetch(labelsDownloadUrl);
          if (labelsResponse.ok) {
            const labelsData = await labelsResponse.json();
            console.log('📋 类别文件内容:', labelsData);

            // 解析类别信息（可能是数组或对象）
            if (Array.isArray(labelsData)) {
              modelClasses = labelsData;
            } else if (labelsData.labels && Array.isArray(labelsData.labels)) {
              modelClasses = labelsData.labels;
            } else if (labelsData.names && Array.isArray(labelsData.names)) {
              modelClasses = labelsData.names;
            } else if (labelsData.classes && Array.isArray(labelsData.classes)) {
              modelClasses = labelsData.classes;
            } else if (labelsData.categories && Array.isArray(labelsData.categories)) {
              modelClasses = labelsData.categories;
            } else if (typeof labelsData === 'object') {
              // 如果是对象，尝试提取值
              modelClasses = Object.values(labelsData).filter(
                (v) => typeof v === 'string'
              ) as string[];
            }

            console.log('✅ 解析到的类别:', modelClasses);
            if (modelClasses.length === 0) {
              console.warn('⚠️ 未能从labels.json中解析出类别信息');
            }
          } else {
            console.warn('⚠️ 下载类别文件失败:', labelsResponse.status);
          }
        } catch (labelsError: any) {
          console.error('❌ 下载或解析类别文件失败:', labelsError);
          // 不阻止后续流程，继续下载ONNX文件
        }
      }

      // 如果解析到了类别，先生成本地 labels.json 供手动放入 models 目录
      const triggerDownload = (data: string, filename: string) => {
        const blob = new Blob([data], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      };
      if (modelClasses.length > 0) {
        try {
          const labelsJson = JSON.stringify({ names: modelClasses }, null, 2);
          // 通用名
          triggerDownload(labelsJson, 'labels.json');
          // 以模型名为前缀，便于旁路部署
          const safeName = (onnxFileName || 'model.onnx').replace(/\.onnx$/i, '');
          triggerDownload(labelsJson, `${safeName}.labels.json`);
        } catch {}
      }

      // 2. 下载转换后的.onnx文件到指定文件夹（public/models/）
      try {
        onnxConversionStatus.value = '正在下载.onnx文件...';
        onnxConversionProgress.value = 98;

        let downloadUrl = onnxUrl;

        // 如果URL不是完整路径，构建完整URL
        if (!downloadUrl.startsWith('http')) {
          const baseUrl = getBackendBaseUrl();
          downloadUrl = downloadUrl.startsWith('/')
            ? `${baseUrl}${downloadUrl}`
            : `${baseUrl}/${downloadUrl}`;
        }

        console.log('🔗 完整下载URL:', downloadUrl);

        // 下载文件
        const fileResponse = await fetch(downloadUrl);
        if (!fileResponse.ok) {
          throw new Error(`下载失败: ${fileResponse.status} ${fileResponse.statusText}`);
        }

        const blob = await fileResponse.blob();

        // 保存到public/models/目录（通过创建下载链接）
        // 注意：浏览器无法直接写入文件系统，我们仅提示用户把文件放入 public/models/
        const modelPath = `/models/${onnxFileName}`;
        // 只保存元数据到 localStorage，避免超出配额
        const models = JSON.parse(localStorage.getItem('onnx_models') || '[]');
        models.push({
          name: onnxUploadForm.value.name,
          version: onnxUploadForm.value.version,
          description: onnxUploadForm.value.description,
          fileName: onnxFileName,
          path: modelPath,
          classes: modelClasses,
          createdAt: new Date().toISOString(),
        });
        localStorage.setItem('onnx_models', JSON.stringify(models));

        // 触发浏览器下载
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = onnxFileName;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        onnxConversionProgress.value = 100;
        onnxConversionStatus.value = '转换完成！文件已下载';

        message.success({
          content: `模型转换成功！已下载 ${onnxFileName} 文件。\n请将文件放到项目的 public/models/ 目录，然后点击"加载模型"按钮。\n${modelClasses.length > 0 ? `检测到 ${modelClasses.length} 个类别。` : ''}`,
          duration: 8,
        });

        // 刷新模型列表
        loadOnnxModelList();

        // 延迟关闭弹窗
        setTimeout(() => {
          onnxUploadModalVisible.value = false;
          onnxFileList.value = [];
          onnxUploadForm.value = {
            name: '',
            version: 'v1',
            description: '',
          };
        }, 2000);
      } catch (downloadError: any) {
        console.error('❌ 下载文件失败:', downloadError);
        onnxConversionStatus.value = '转换成功，但下载失败';
        message.warning({
          content: `模型转换成功，但下载失败。请手动访问: ${onnxUrl}`,
          duration: 8,
        });
      }
    } else {
      throw new Error(convertResponse.message || '转换失败');
    }
  } catch (error: any) {
    console.error('❌ 转换过程出错:', error);
    onnxConversionStatus.value = '转换失败';
    message.error(error.message || '转换失败，请检查网络连接或后端服务');
  } finally {
    onnxUploading.value = false;
    onnxConverting.value = false;
    setTimeout(() => {
      onnxConversionProgress.value = 0;
      onnxConversionStatus.value = '';
    }, 2000);
  }
};

// 取消ONNX上传
const handleOnnxUploadCancel = () => {
  if (onnxConverting.value) {
    message.warning('转换进行中，请稍候...');
    return;
  }
  onnxUploadModalVisible.value = false;
  onnxFileList.value = [];
  onnxUploadForm.value = {
    name: '',
    version: 'v1',
    description: '',
  };
};

// 扫描 public/models 目录下的 ONNX 模型（以 manifest 为准，避免缓存残留）
const loadOnnxModelList = async () => {
  try {
    // 先读取 manifest，仅以 manifest 中的文件作为权威列表
    const manifestRes = await fetch('/models/manifest.json', { method: 'GET', cache: 'no-store' });
    let files: string[] = [];
    if (manifestRes.ok) {
      const manifest = await manifestRes.json();
      files = Array.isArray(manifest)
        ? manifest
        : Array.isArray(manifest?.files)
          ? manifest.files
          : [];
    }

    // 组装模型列表
    const aggregated: Array<{ name: string; path: string; classes?: string[] }> = [];
    const savedModels = JSON.parse(localStorage.getItem('onnx_models') || '[]');
    const savedMap = new Map<string, any>(savedModels.map((m: any) => [m.path || m.onnxPath, m]));

    for (const file of files) {
      const path = file.startsWith('/models/') ? file : `/models/${file}`;
      const fileName = path.split('/').pop() || path;
      const name = savedMap.get(path)?.name || fileName.replace(/\.onnx$/i, '');
      aggregated.push({ name, path, classes: savedMap.get(path)?.classes });
    }

    onnxModels.value = aggregated;

    // 把本地缓存中不存在于 manifest 的条目清理掉
    try {
      const validSet = new Set(files.map((f) => (f.startsWith('/models/') ? f : `/models/${f}`)));
      const cleaned = savedModels.filter((m: any) => validSet.has(m.path || m.onnxPath));
      localStorage.setItem('onnx_models', JSON.stringify(cleaned));
    } catch {}

    // 自动选择
    if (onnxModels.value.length === 1 && !selectedOnnxModel.value) {
      selectedOnnxModel.value = onnxModels.value[0].path;
    }

    console.log('📦 已加载ONNX模型列表:', onnxModels.value);
  } catch (error) {
    console.error('加载ONNX模型列表失败:', error);
    onnxModels.value = [];
  }
};

// 加载ONNX模型
const loadOnnxModel = async () => {
  if (!selectedOnnxModel.value) {
    message.warning('请先选择ONNX模型');
    return;
  }

  // 验证模型路径是否有效
  if (!selectedOnnxModel.value.endsWith('.onnx')) {
    message.error('模型路径无效：必须以 .onnx 结尾');
    return;
  }

  if (yoloDetector.isLoaded() && selectedOnnxModel.value === yoloDetector.getModelPath()) {
    message.info('模型已加载');
    return;
  }

  modelLoading.value = true;
  try {
    console.log('🔄 开始加载模型:', selectedOnnxModel.value);

    // 先验证文件是否存在
    try {
      const testResponse = await fetch(selectedOnnxModel.value, { method: 'HEAD' });
      if (!testResponse.ok) {
        throw new Error(
          `模型文件不存在 (状态码: ${testResponse.status})。请确保文件在 public/models/ 目录下。`
        );
      }
      console.log('✅ 模型文件存在，开始加载...');
    } catch (fetchError: any) {
      console.error('❌ 模型文件验证失败:', fetchError);
      throw new Error(`模型文件验证失败: ${fetchError.message || '无法访问模型文件'}`);
    }

    // 获取类别信息：localStorage → 同目录 labels.json/xxx.labels.json → 保持为空由模型推断
    let classNames: string[] = [];
    try {
      const savedModels = JSON.parse(localStorage.getItem('onnx_models') || '[]');
      const modelInfo = savedModels.find((m: any) => m.path === selectedOnnxModel.value);
      if (modelInfo?.classes?.length) classNames = modelInfo.classes;
    } catch {}

    if (classNames.length === 0) {
      const path = selectedOnnxModel.value;
      const dir = path.substring(0, path.lastIndexOf('/'));
      const base = (path.split('/').pop() || '').replace(/\.onnx$/i, '');
      const candidates = [
        `${dir}/labels.json`,
        `${dir}/classes.json`,
        `${dir}/${base}.labels.json`,
        `${dir}/${base}_labels.json`,
      ];
      for (const url of candidates) {
        try {
          const r = await fetch(url);
          if (r.ok) {
            const data = await r.json();
            if (Array.isArray(data)) classNames = data;
            else if (Array.isArray((data as any).labels)) classNames = (data as any).labels;
            else if (Array.isArray((data as any).names)) classNames = (data as any).names;
            else if (Array.isArray((data as any).classes)) classNames = (data as any).classes;
            else if (typeof data === 'object')
              classNames = Object.values(data).filter((v) => typeof v === 'string') as string[];
            if (classNames.length) {
              console.log('📦 从同目录加载类别:', classNames.length);
              break;
            }
          }
        } catch {}
      }
      if (classNames.length) {
        // 写回localStorage
        try {
          const models = JSON.parse(localStorage.getItem('onnx_models') || '[]');
          const idx = models.findIndex((m: any) => m.path === path);
          if (idx >= 0) {
            models[idx].classes = classNames;
            localStorage.setItem('onnx_models', JSON.stringify(models));
          }
        } catch {}
      }
    }

    if (classNames.length > 0) {
      onnxModelConfig.value.classNames = classNames;
    }

    // 加载模型
    await yoloDetector.loadModel(selectedOnnxModel.value, onnxModelConfig.value.classNames);

    onnxModelLoaded.value = true;
    message.success({
      content: `ONNX模型加载成功${classNames.length > 0 ? `（${classNames.length}个类别）` : ''}`,
      duration: 3,
    });
  } catch (error: any) {
    console.error('模型加载失败:', error);

    let errorMsg = error.message || '请确保模型文件存在且格式正确';

    if (errorMsg.includes('protobuf')) {
      errorMsg =
        '模型文件格式错误。请确保：\n1. 模型文件是有效的ONNX格式\n2. 文件未损坏\n3. 文件已正确转换';
    } else if (errorMsg.includes('404') || errorMsg.includes('不存在')) {
      errorMsg = `模型文件不存在。请检查：\n1. 文件是否在 public/models/ 目录下\n2. 路径是否正确: ${selectedOnnxModel.value}`;
    }

    message.error({
      content: `模型加载失败: ${errorMsg}`,
      duration: 8,
    });
    onnxModelLoaded.value = false;
  } finally {
    modelLoading.value = false;
  }
};

// 组件挂载时加载ONNX模型列表
onMounted(() => {
  loadOnnxModelList();
});

// 组件卸载时断开连接和关闭摄像头
onUnmounted(() => {
  // 停止检测
  if (isDetecting.value) {
    stopDetection();
  }
  // 断开WebSocket
  if (ws) {
    ws.close();
    ws = null;
  }
  // 释放ONNX模型资源
  if (onnxModelLoaded.value) {
    yoloDetector.dispose();
  }
  // 关闭摄像头
  stopCamera();
});
</script>

<style scoped lang="scss">
.live-detection-page {
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

  .detection-controls {
    margin-bottom: 24px;

    .control-card {
      .camera-preview {
        width: 100%;
        height: 420px; // 16:9 近似高度，提升可视面积
        background: var(--theme-content-bg, #000);
        border-radius: 8px;
        position: relative;
        overflow: hidden;
        margin-bottom: 16px;

        .camera-video {
          width: 100%;
          height: 100%;
          object-fit: contain;
          display: block;

          &.camera-active {
            display: block;
          }

          &:not(.camera-active) {
            display: none;
          }
        }
        .overlay-canvas {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
        }
        .overlay-hud {
          position: absolute;
          top: 10px;
          left: 10px;
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        .hud-chip {
          background: rgba(0, 0, 0, 0.6);
          color: var(--theme-text-primary, #fff);
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 12px;
          line-height: 1;
          border: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
        }

        .camera-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: var(--theme-text-secondary, #9ca3af);

          .anticon {
            font-size: 4rem;
            margin-bottom: 12px;
          }

          p {
            margin: 0;
            font-size: 1rem;
          }
        }
      }

      .camera-status {
        margin-top: 12px;
      }

      .connection-status {
        margin-top: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;

        .status-tag {
          font-size: 0.9rem;
          padding: 4px 12px;
        }

        .status-text {
          color: var(--theme-text-secondary, #64748b);
          font-size: 0.9rem;
        }
      }
    }
  }

  .detection-results {
    .no-data {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 400px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      color: #9ca3af;

      .no-data-icon {
        font-size: 4rem;
        margin-bottom: 16px;
      }

      p {
        margin: 4px 0;
        font-size: 1.1rem;
      }

      .no-data-hint {
        font-size: 0.9rem;
        color: var(--theme-text-secondary, #d1d5db);
      }
    }

    .latest-result-container {
      .latest-result-card {
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        cursor: pointer;
        overflow: hidden;

        &:hover {
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
          transform: translateY(-4px);
        }

        .result-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 4px 0;

          .header-left {
            display: flex;
            align-items: center;
            gap: 12px;

            .new-badge {
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
              padding: 4px 12px;
              border-radius: 12px;
              font-size: 0.75rem;
              font-weight: 600;
              box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            }

            .result-title-text {
              font-size: 1.1rem;
              font-weight: 600;
              color: var(--theme-text-primary, #1e293b);
            }
          }

          .status-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.9rem;
          }
        }

        .latest-result-content {
          margin-top: 20px;

          .result-image-wrapper {
            margin-bottom: 24px;

            .result-image {
              position: relative;
              width: 100%;
              height: 450px;
              background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
              border-radius: 12px;
              overflow: hidden;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

              img {
                width: 100%;
                height: 100%;
                object-fit: contain;
                background: var(--theme-content-bg, #000);
              }

              .image-placeholder {
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-size: 3rem;
                color: var(--theme-text-secondary, #9ca3af);

                p {
                  margin-top: 12px;
                  font-size: 1rem;
                }
              }

              .image-overlay-info {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(
                  to top,
                  rgba(0, 0, 0, 0.85),
                  rgba(0, 0, 0, 0.6),
                  transparent
                );
                padding: 20px;

                .overlay-stats {
                  display: flex;
                  gap: 20px;
                  justify-content: center;
                  flex-wrap: wrap;

                  .stat-item {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 12px 20px;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                    min-width: 120px;

                    .stat-icon {
                      font-size: 1.5rem;
                    }

                    .stat-content {
                      display: flex;
                      flex-direction: column;

                      .stat-number {
                        font-weight: 700;
                        font-size: 1.1rem;
                        color: #1890ff;
                        line-height: 1.2;
                      }

                      .stat-label {
                        font-size: 0.75rem;
                        color: var(--theme-text-secondary, #64748b);
                        margin-top: 2px;
                      }
                    }
                  }
                }
              }
            }
          }

          .result-details {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 20px;

            .detection-summary {
              .summary-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 1.05rem;
                font-weight: 600;
                color: var(--theme-text-primary, #1e293b);
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 2px solid #e2e8f0;
              }

              .detection-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;

                .detection-tag {
                  display: inline-flex;
                  align-items: center;
                  gap: 6px;
                  padding: 8px 16px;
                  border-radius: 20px;
                  font-size: 0.9rem;
                  font-weight: 500;
                  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                  transition: all 0.2s ease;

                  &:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
                  }

                  .tag-category {
                    font-weight: 600;
                  }

                  .tag-score {
                    opacity: 0.9;
                    font-size: 0.85rem;
                  }
                }
              }

              .no-detections {
                text-align: center;
                padding: 20px;
                color: #94a3b8;
                font-size: 0.95rem;
              }
            }
          }
        }
      }
    }
  }

  /* ONNX 控件区域排版优化 */
  .onnx-controls {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .onnx-controls .row {
    width: 100%;
  }
  .onnx-controls .row.status {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .onnx-controls .path-text {
    color: #64748b;
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .detail-content {
    .detail-image {
      margin-bottom: 20px;
      text-align: center;

      img {
        max-width: 100%;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      .image-placeholder {
        width: 100%;
        height: 300px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: var(--theme-page-bg, #f5f5f5);
        border-radius: 8px;
        color: #9ca3af;

        .anticon {
          font-size: 3rem;
          margin-bottom: 12px;
        }

        p {
          margin: 0;
        }
      }
    }

    .detail-detections {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .detail-tag {
        border-radius: 12px;
        padding: 4px 12px;
      }
    }
  }
}

@media (max-width: 768px) {
  .live-detection-page {
    padding: 16px;

    .detection-results {
      .latest-result-container {
        .latest-result-card {
          .result-card-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;

            .header-left {
              width: 100%;
            }
          }

          .latest-result-content {
            .result-image-wrapper {
              .result-image {
                height: 300px;

                .image-overlay-info {
                  .overlay-stats {
                    flex-direction: column;
                    gap: 12px;

                    .stat-item {
                      width: 100%;
                      min-width: auto;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    .detection-controls .control-card .camera-preview {
      height: 300px; // 移动端回落
    }
  }
}
</style>
