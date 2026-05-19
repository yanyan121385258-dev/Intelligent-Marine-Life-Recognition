import { request } from '@/utils/request';

// YOLO检测相关接口类型定义
export interface YoloDetectionRequest {
  image: File;
  model_id?: string;
  confidence_threshold?: number;
  nms_threshold?: number;
}

export interface DetectionBbox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface YoloDetection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: DetectionBbox;
}

export interface YoloDetectionResponse {
  message: string;
  data?: {
    detection_id: number;
    result_file_url: string;
    original_file_url: string;
    object_count: number;
    detected_categories: string[];
    confidence_scores: number[];
    avg_confidence: number | null;
    processing_time: number;
    model_used: string;
    confidence_threshold: number;
    user_id: number;
    user_name: string;
    alert_level?: 'low' | 'medium' | 'high';
  };
}

export interface YoloModel {
  id: string;
  name: string;
  version: string;
  description: string;
  classes: string[];
  is_active: boolean;
  is_enabled: boolean;
  model_file: string;
  model_folder_path: string;
  model_path: string;
  weights_folder_path: string;
  categories: { [key: string]: any };
  created_at: string;
  updated_at: string;
}

export interface YoloModelListResponse {
  success: boolean;
  message?: string;
  data?: {
    models: YoloModel[];
    total: number;
  };
}

// 数据集管理相关类型
export interface YoloDatasetSummary {
  id: number;
  name: string;
  version?: string;
  root_folder_path: string;
  data_yaml_path: string;
  nc?: number;
  description?: string;
  created_at?: string;
}

export interface YoloDatasetDetail extends YoloDatasetSummary {
  names?: string[];
  train_images_count?: number;
  train_labels_count?: number;
  val_images_count?: number;
  val_labels_count?: number;
  test_images_count?: number;
  test_labels_count?: number;
}

export interface YoloDatasetSampleItem {
  image: string;
  image_size?: number;
  label?: string;
  filename: string;
}

// YOLO 训练任务相关类型
export type YoloTrainStatus =
  | 'queued'
  | 'running'
  | 'canceling'
  | 'completed'
  | 'failed'
  | 'canceled';

export interface YoloTrainDatasetOption {
  id: number;
  name: string;
  version?: string;
  yaml: string;
}

export interface YoloTrainVersionOption {
  family: 'v8' | '11' | '12';
  config_path: string;
  sizes: string[];
}

export interface YoloTrainOptionsResponse {
  success: boolean;
  code?: number;
  message?: string;
  data?: {
    datasets: YoloTrainDatasetOption[];
    versions: YoloTrainVersionOption[];
  };
}

export interface YoloTrainingJob {
  id: number;
  dataset: number;
  dataset_name: string;
  model_family: 'v8' | '11' | '12';
  model_size?: 'n' | 's' | 'm' | 'l' | 'x';
  weight_path?: string;
  config_path?: string;
  status: YoloTrainStatus;
  logs_path?: string;
  runs_path?: string;
  best_model_path?: string;
  last_model_path?: string;
  progress: number;
  epochs: number;
  imgsz: number;
  batch: number;
  device: string;
  optimizer: 'SGD' | 'Adam' | 'AdamW' | 'RMSProp';
  error_message?: string;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface StartTrainingPayload {
  dataset_id: number;
  model_family: 'v8' | '11' | '12';
  model_size?: 'n' | 's' | 'm' | 'l' | 'x';
  epochs?: number;
  imgsz?: number;
  batch?: number;
  device?: string;
  optimizer?: 'SGD' | 'Adam' | 'AdamW' | 'RMSProp';
}

export interface YoloTrainLogsResponse {
  success: boolean;
  code?: number;
  message?: string;
  data?: {
    content: string;
    next_offset: number;
    finished: boolean;
  };
}

// YOLO检测API
export const yoloApi = {
  // 执行YOLO检测
  async detectImage(detectionRequest: YoloDetectionRequest): Promise<YoloDetectionResponse> {
    console.log('🔍 构建检测请求:', detectionRequest);
    console.log('📁 文件对象详情:', {
      name: detectionRequest.image.name,
      size: detectionRequest.image.size,
      type: detectionRequest.image.type,
      lastModified: detectionRequest.image.lastModified,
    });

    const formData = new FormData();
    formData.append('file', detectionRequest.image);

    if (detectionRequest.model_id) {
      formData.append('model_id', detectionRequest.model_id);
    }
    if (detectionRequest.confidence_threshold) {
      formData.append('confidence_threshold', detectionRequest.confidence_threshold.toString());
    }
    if (detectionRequest.nms_threshold) {
      formData.append('nms_threshold', detectionRequest.nms_threshold.toString());
    }

    // 调试FormData内容
    console.log('📤 FormData内容:');
    for (const [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`  ${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
      } else {
        console.log(`  ${key}:`, value);
      }
    }

    return request.post('/api/yolo/detect/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 获取当前启用的YOLO模型信息
  async getCurrentEnabledModel(): Promise<{
    success: boolean;
    data?: YoloModel;
    message?: string;
  }> {
    // 关闭全局错误提示，由调用方（如 YOLO 检测页面）自行处理“未启用模型”等业务文案
    return request.get('/api/yolo/models/enabled/', { showError: false });
  },

  // 获取模型详情
  async getModelInfo(
    modelId: string
  ): Promise<{ success: boolean; data?: YoloModel; message?: string }> {
    return request.get(`/api/yolo/models/${modelId}`);
  },

  // 批量检测
  async detectBatch(images: File[], modelId?: string): Promise<YoloDetectionResponse[]> {
    const promises = images.map((image) =>
      this.detectImage({
        image,
        model_id: modelId,
        confidence_threshold: 0.5,
        nms_threshold: 0.4,
      })
    );

    return Promise.all(promises);
  },

  // 获取模型列表
  async getModels(): Promise<{ success: boolean; data?: YoloModel[]; message?: string }> {
    return request.get('/api/yolo/models/');
  },

  // 上传模型
  async uploadModel(formData: FormData): Promise<{ success: boolean; message?: string }> {
    // 使用专门的upload方法，它会自动处理Content-Type
    return request.upload('/api/yolo/upload/', formData);
  },

  // 更新模型信息
  async updateModel(
    modelId: string,
    data: { name: string; version: string }
  ): Promise<{ success: boolean; data?: YoloModel; message?: string }> {
    return request.put(`/api/yolo/models/${modelId}/update/`, data);
  },

  // 删除模型
  async deleteModel(modelId: string): Promise<{ success: boolean; message?: string }> {
    return request.delete(`/api/yolo/models/${modelId}/delete/`);
  },

  // 启用模型
  async enableModel(
    modelId: string
  ): Promise<{ success: boolean; data?: YoloModel; message?: string }> {
    return request.post(`/api/yolo/models/${modelId}/enable/`);
  },

  // 获取模型详情
  async getModelDetail(
    modelId: string
  ): Promise<{ success: boolean; data?: YoloModel; message?: string }> {
    return request.get(`/api/yolo/models/${modelId}/`);
  },

  // 获取检测历史记录列表
  async getDetectionHistory(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    start_date?: string;
    end_date?: string;
    model_id?: string;
  }): Promise<{ success: boolean; data?: DetectionHistoryRecord[]; message?: string }> {
    return request.get('/api/yolo/detections/', { params });
  },

  // 获取检测记录详情
  async getDetectionDetail(
    recordId: string
  ): Promise<{ success: boolean; data?: DetectionHistoryRecord; message?: string }> {
    return request.get(`/api/detections/${recordId}/`);
  },

  // 删除检测记录
  async deleteDetection(recordId: string): Promise<{ success: boolean; message?: string }> {
    return request.delete(`/api/yolo/detections/${recordId}/delete/`);
  },

  // 批量删除检测记录
  async batchDeleteDetections(ids: number[]): Promise<{ success: boolean; message?: string }> {
    return request.post('/api/yolo/detections/batch-delete/', { ids });
  },

  // 获取检测统计
  async getDetectionStats(): Promise<{ success: boolean; data?: any; message?: string }> {
    return request.get('/api/yolo/stats/');
  },

  // 数据集管理相关接口
  // 上传数据集
  async uploadDataset(
    formData: FormData
  ): Promise<{ success: boolean; data?: YoloDatasetDetail; message?: string }> {
    return request.upload('/api/yolo/datasets/upload/', formData);
  },

  // 获取数据集列表
  async getDatasets(): Promise<{
    success: boolean;
    data?: YoloDatasetSummary[];
    message?: string;
  }> {
    return request.get('/api/yolo/datasets/');
  },

  // 获取数据集详情
  async getDatasetDetail(
    datasetId: number
  ): Promise<{ success: boolean; data?: YoloDatasetDetail; message?: string }> {
    return request.get(`/api/yolo/datasets/${datasetId}/`);
  },

  // 删除数据集
  async deleteDataset(datasetId: number): Promise<{ success: boolean; message?: string }> {
    return request.post(`/api/yolo/datasets/${datasetId}/delete/`);
  },

  // 获取数据集样本
  async getDatasetSamples(
    datasetId: number,
    params: { split?: 'train' | 'val' | 'test'; limit?: number; offset?: number } = {}
  ): Promise<{
    success: boolean;
    data?: { items: YoloDatasetSampleItem[]; total: number };
    message?: string;
  }> {
    return request.get(`/api/yolo/datasets/${datasetId}/samples/`, { params });
  },

  // YOLO 训练任务相关接口
  // 获取训练选项（可用数据集与模型版本）
  async getTrainOptions(): Promise<YoloTrainOptionsResponse> {
    return request.get('/api/yolo/train/options/');
  },

  // 获取训练任务列表
  async getTrainJobs(): Promise<{
    success: boolean;
    code?: number;
    message?: string;
    data?: YoloTrainingJob[];
  }> {
    return request.get('/api/yolo/train/jobs/');
  },

  // 创建并启动训练任务
  async startTrainJob(payload: StartTrainingPayload): Promise<{
    success: boolean;
    code?: number;
    message?: string;
    data?: YoloTrainingJob;
  }> {
    return request.post('/api/yolo/train/jobs/start/', payload);
  },

  // 获取训练任务详情
  async getTrainJobDetail(id: number): Promise<{
    success: boolean;
    code?: number;
    message?: string;
    data?: YoloTrainingJob;
  }> {
    return request.get(`/api/yolo/train/jobs/${id}/`);
  },

  // 获取训练任务日志（分页读取）
  async getTrainJobLogs(
    id: number,
    params: { offset?: number; max?: number } = {}
  ): Promise<YoloTrainLogsResponse> {
    return request.get(`/api/yolo/train/jobs/${id}/logs/`, { params });
  },

  // 取消训练任务
  async cancelTrainJob(id: number): Promise<{
    success: boolean;
    code?: number;
    message?: string;
    data?: YoloTrainingJob;
  }> {
    return request.post(`/api/yolo/train/jobs/${id}/cancel/`);
  },

  // 下载训练结果（ZIP）
  async downloadTrainJobResult(id: number): Promise<{
    success: boolean;
    code?: number;
    message?: string;
    data?: { url: string; size: number };
  }> {
    return request.get(`/api/yolo/train/jobs/${id}/download/`);
  },

  // 删除训练任务
  async deleteTrainJob(id: number): Promise<{
    success: boolean;
    code?: number;
    message?: string;
  }> {
    return request.post(`/api/yolo/train/jobs/${id}/delete/`);
  },

  // 警告等级管理相关接口
  // 获取警告等级列表
  async getAlertLevels(): Promise<{ success: boolean; data?: AlertLevel[]; message?: string }> {
    return request.get('/api/yolo/categories/');
  },

  // 获取警告等级详情
  async getAlertLevelDetail(
    levelId: string
  ): Promise<{ success: boolean; data?: AlertLevel; message?: string }> {
    return request.get(`/api/yolo/categories/${levelId}/`);
  },

  // 更新警告等级
  async updateAlertLevel(
    levelId: string,
    data: { alert_level?: 'low' | 'medium' | 'high'; alias?: string }
  ): Promise<{ success: boolean; data?: AlertLevel; message?: string }> {
    return request.put(`/api/yolo/categories/${levelId}/update/`, data);
  },

  // 切换警告等级状态
  async toggleAlertLevelStatus(
    levelId: string
  ): Promise<{ success: boolean; data?: AlertLevel; message?: string }> {
    return request.post(`/api/yolo/categories/${levelId}/toggle-status/`);
  },

  // 获取活跃的警告等级列表
  async getActiveAlertLevels(): Promise<{
    success: boolean;
    data?: AlertLevel[];
    message?: string;
  }> {
    return request.get('/api/yolo/categories/active/');
  },

  // 上传并转换PT模型为ONNX格式
  async uploadAndConvertToOnnx(formData: FormData): Promise<{
    success: boolean;
    message?: string;
    data?: {
      onnx_path?: string;
      onnx_url?: string;
      download_url?: string;
      onnx_relative_path?: string;
      file_name?: string;
      labels_download_url?: string;
      labels_relative_path?: string;
      classes?: string[];
    };
  }> {
    // 适配后端 @views.py 中的 upload_pt_convert_onnx 实现
    // 统一走 /api/upload_pt_convert_onnx
    // 按你的后端接口：/yolo/onnx/upload/
    // 注意带上结尾斜杠，避免 404
    return request.upload('/api/yolo/onnx/upload/', formData);
  },
};

// 警告等级管理相关接口
export interface AlertLevel {
  id: number;
  model: number;
  model_name: string;
  name: string;
  alias: string;
  display_name: string;
  category_id: number;
  alert_level: 'low' | 'medium' | 'high';
  alert_level_display: string;
  is_active: boolean;
  // 前端编辑状态字段
  editingAlias?: boolean;
  tempAlias?: string;
}

// 用户检测历史相关接口
export interface DetectionHistoryRecord {
  id: number;
  user_id: number;
  original_filename: string;
  result_filename: string;
  original_file: string;
  result_file: string;
  detection_type: 'image' | 'video';
  object_count: number;
  detected_categories: string[];
  confidence_scores: number[];
  avg_confidence: number | null;
  processing_time: number;
  model_name: string;
  model_info: any;
  created_at: string;
  confidence_threshold?: number; // 置信度阈值（原始设置值）
  // 为了兼容前端显示，添加计算字段
  filename?: string;
  image_url?: string;
  detections?: YoloDetection[];
}

export interface DetectionHistoryParams {
  page?: number;
  page_size?: number;
  search?: string;
  class_filter?: string;
  start_date?: string;
  end_date?: string;
  model_id?: string;
}

export interface DetectionHistoryResponse {
  success?: boolean;
  message?: string;
  data?:
    | {
        records: DetectionHistoryRecord[];
        total: number;
        page: number;
        page_size: number;
      }
    | DetectionHistoryRecord[];
  // 支持直接返回数组的情况
  results?: DetectionHistoryRecord[];
  count?: number;
  // 支持Django REST framework的分页格式
  next?: string;
  previous?: string;
}

// 用户检测历史API
export const detectionHistoryApi = {
  // 获取用户检测历史
  async getUserDetectionHistory(
    userId: number,
    params: DetectionHistoryParams = {}
  ): Promise<DetectionHistoryResponse> {
    return request.get('/api/yolo/detections/', {
      params: {
        user_id: userId,
        ...params,
      },
    });
  },

  // 获取检测记录详情
  async getDetectionRecordDetail(recordId: number): Promise<{
    success?: boolean;
    code?: number;
    message?: string;
    data?: DetectionHistoryRecord;
  }> {
    return request.get(`/api/yolo/detections/${recordId}/`);
  },

  // 删除检测记录
  async deleteDetectionRecord(
    userId: number,
    recordId: string
  ): Promise<{ success: boolean; message?: string }> {
    return request.delete(`/api/yolo/detections/${recordId}/delete/`);
  },

  // 批量删除检测记录
  async batchDeleteDetectionRecords(
    userId: number,
    recordIds: string[]
  ): Promise<{ success: boolean; message?: string }> {
    return request.post('/api/yolo/detections/batch-delete/', { ids: recordIds });
  },

  // 导出检测历史
  async exportDetectionHistory(userId: number, params: DetectionHistoryParams = {}): Promise<Blob> {
    const response = await request.get('/api/yolo/detections/export/', {
      params: {
        user_id: userId,
        ...params,
      },
      responseType: 'blob',
    });
    return response;
  },

  // 获取检测统计信息
  async getDetectionStats(userId: number): Promise<{
    success: boolean;
    data?: {
      total_detections: number;
      total_images: number;
      class_counts: Record<string, number>;
      recent_activity: Array<{
        date: string;
        count: number;
      }>;
    };
    message?: string;
  }> {
    return request.get('/api/yolo/detections/stats/', {
      params: { user_id: userId },
    });
  },
};

// 告警相关接口类型定义
export interface AlertRecord {
  id: number;
  detection_record: number;
  detection_info: {
    id: number;
    detection_type: string;
    original_filename: string;
    result_filename: string;
    object_count: number;
    avg_confidence: number;
  };
  user: number;
  user_name: string;
  alert_level: string;
  alert_level_display: string;
  alert_category: string;
  category: number;
  category_info: {
    id: number;
    name: string;
    alert_level: string;
    alert_level_display: string;
  };
  status: string;
  created_at: string;
  deleted_at: string | null;
}

// 告警管理API
export const alertApi = {
  // 获取所有告警记录
  async getAllAlerts(): Promise<{ success: boolean; data?: AlertRecord[]; message?: string }> {
    return request.get('/api/yolo/alerts/');
  },

  // 获取当前用户的告警记录
  async getUserAlerts(
    userId: string
  ): Promise<{ success: boolean; data?: AlertRecord[]; message?: string }> {
    return request.get(`/api/yolo/users/${userId}/alerts/`);
  },

  // 处理告警（更新状态）
  async updateAlertStatus(
    alertId: string,
    status: string
  ): Promise<{ success: boolean; data?: AlertRecord; message?: string }> {
    return request.put(`/api/yolo/alerts/${alertId}/update-status/`, { status });
  },
};

// 默认导出
export default yoloApi;
