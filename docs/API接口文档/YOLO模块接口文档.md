# Hertz Studio Django YOLO 接口文档

- 基础路径: `/api/yolo/`
- 统一响应: 使用 `HertzResponse` 封装，结构为：
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {}
  }
  ```
  参考 `hertz_studio_django_utils/responses/HertzResponse.py`
- 认证说明: 标注“需要登录”的接口需在请求头携带 `Authorization: Bearer <token>`，验证逻辑参考 `hertz_studio_django_auth/utils/decorators/auth_decorators.py`。


## 一、模型上传与转换

### （1）上传模型（压缩包或文件夹）
- 方法: `POST`
- 路径: `/api/yolo/upload/`
- 认证: 不需要
- 请求类型: `multipart/form-data`
- 参数:
  - `zip_file`: ZIP 压缩包文件，与 `folder_files` 互斥
  - `folder_files[...]`: 文件夹内的多个文件（键名形如 `folder_files[path/to/file]`），与 `zip_file` 互斥
  - `name`: 模型名称（必填）
  - `version`: 模型版本（默认 `1.0`）
  - `description`: 模型描述（可选）
- 参考实现: `views.py` 中 `model_upload`，`_handle_zip_upload`，`_handle_folder_upload`，`_validate_and_create_model`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1018,1058,1129,1182）
- 示例请求（ZIP 上传）:
  ```bash
  curl -X POST "http://localhost:8000/api/yolo/upload/" \
    -F "zip_file=@/path/to/yolo_model.zip" \
    -F "name=MyYolo" \
    -F "version=1.0" \
    -F "description=Demo model"
  ```
- 示例响应:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "模型上传成功",
    "data": {
      "id": 12,
      "name": "MyYolo",
      "version": "1.0",
      "folder_path": "/absolute/path/to/media/models/MyYolo_xxxxxxxx",
      "weights_path": "/absolute/path/to/media/models/MyYolo_xxxxxxxx/weights",
      "model_path": "/absolute/path/to/media/models/MyYolo_xxxxxxxx/weights/best.pt",
      "best_model_path": "/absolute/path/to/media/models/.../weights/best.pt",
      "last_model_path": "/absolute/path/to/media/models/.../weights/last.pt",
      "categories": {"0":"person","1":"bicycle"},
      "created_at": "2025-10-22T03:20:00Z"
    }
  }
  ```

### （2）上传 .pt 并转换为 ONNX
- 方法: `POST`
- 路径: `/api/yolo/onnx/upload/`
- 认证: 不需要
- 请求类型: `multipart/form-data`
- 参数:
  - `file`: `.pt` 模型文件（必填）
  - `imgsz`: 导出图像尺寸（如 `640` 或 `640,640`，默认 `640`）
  - `opset`: ONNX opset 版本（默认 `12`）
  - `simplify`: 是否简化 ONNX（`true/false`，默认 `false`）
- 参考实现: `views.py` 中 `upload_pt_convert_onnx`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:877）
- 示例请求:
  ```bash
  curl -X POST "http://localhost:8000/api/yolo/onnx/upload/" \
    -F "file=@/path/to/best.pt" \
    -F "imgsz=640" \
    -F "opset=12" \
    -F "simplify=true"
  ```
- 示例响应:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "ONNX 导出成功",
    "data": {
      "onnx_relative_path": "yolo/ONNX/best_xxxxxxxx.onnx",
      "download_url": "http://localhost:8000/media/yolo/ONNX/best_xxxxxxxx.onnx",
      "labels_relative_path": "yolo/ONNX/best_xxxxxxxx.labels.json",
      "labels_download_url": "http://localhost:8000/media/yolo/ONNX/best_xxxxxxxx.labels.json"
    }
  }
  ```


## 二、模型管理

### （1）获取模型列表
- 方法: `GET`
- 路径: `/api/yolo/models/`
- 认证: 不需要
- 参考实现: `model_list`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:101）
- 示例响应:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "获取模型列表成功",
    "data": [
      {"id": 1, "name": "ModelA", "version": "1.0", "is_enabled": true, "created_at": "2025-10-22T03:20:00Z"}
    ]
  }
  ```

### （2）获取模型详情
- 方法: `GET`
- 路径: `/api/yolo/models/{pk}/`
- 认证: 不需要
- 参考实现: `model_detail`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:121）
- 示例响应（节选）:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "获取模型详情成功",
    "data": {
      "id": 1,
      "name": "ModelA",
      "version": "1.0",
      "model_file": "/media/yolo/models/modela.pt",
      "model_folder_path": "/abs/path/models/modela_...",
      "model_path": "/abs/path/models/modela_/weights/best.pt",
      "weights_folder_path": "/abs/path/models/modela_/weights",
      "categories": {"0": "person"},
      "is_enabled": true,
      "description": "...",
      "created_at": "...",
      "updated_at": "..."
    }
  }
  ```

### （2）更新模型
- 方法: `PUT` 或 `PATCH`
- 路径: `/api/yolo/models/{pk}/update/`
- 认证: 不需要
- 请求类型: `application/json` 或 `multipart/form-data`
- 可更新字段: `description`, `is_enabled`,（如上传 `model_file` 必须为 `.pt`）
- 参考实现: `model_update`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:134）
- 示例请求（PATCH）:
  ```http
  PATCH /api/yolo/models/1/update/
  Content-Type: application/json
  
  {
    "description": "更新描述",
    "is_enabled": true
  }
  ```
- 示例响应:
  ```json
  {"success": true, "code": 200, "message": "模型更新成功", "data": {"id": 1, "name": "ModelA", "is_enabled": true}}
  ```

### （3）删除模型
- 方法: `DELETE`
- 路径: `/api/yolo/models/{pk}/delete/`
- 认证: 不需要
- 参考实现: `model_delete`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:152）
- 示例响应:
  ```json
  {"success": true, "code": 200, "message": "模型删除成功"}
  ```

### （4）启用指定模型
- 方法: `POST`
- 路径: `/api/yolo/models/{pk}/enable/`
- 认证: 不需要
- 行为: 先禁用其他模型，再启用当前模型
- 参考实现: `model_enable`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:165）
- 示例响应:
  ```json
  {"success": true, "code": 200, "message": "模型 ModelA 已启用", "data": {"id": 1, "is_enabled": true}}
  ```

### （5）获取当前启用的模型
- 方法: `GET`
- 路径: `/api/yolo/models/enabled/`
- 认证: 不需要
- 参考实现: `model_enabled`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:186）
- 示例响应:
  ```json
  {"success": true, "code": 200, "message": "获取启用模型成功", "data": {"id": 1, "name": "ModelA"}}
  ```

### （6）创建模型（占位）
- 方法: `POST`
- 路径: `/api/yolo/models/create/`
- 说明: 返回 405，提示使用 `/api/yolo/upload/`
- 参考实现: `model_create`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:114）


## 三、模型类别管理

> 提示：类别通常随模型上传自动导入。手动创建/删除不推荐，仅保留接口。

### （1）获取类别列表
- 方法: `GET`
- 路径: `/api/yolo/categories/`
- 认证: 不需要
- 参考实现: `category_list`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1301）

### （2）获取类别详情
- 方法: `GET`
- 路径: `/api/yolo/categories/{pk}/`
- 认证: 不需要
- 参考实现: `category_detail`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1329）

### （3）更新类别
- 方法: `PUT` 或 `PATCH`
- 路径: `/api/yolo/categories/{pk}/update/`
- 认证: 不需要
- 请求类型: `application/json`
- 可更新字段: `alias`, `alert_level`（`high|medium|low|none`）, `is_active`
- 参考实现: `category_update`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1342）
- 示例请求（PATCH）:
  ```http
  PATCH /api/yolo/categories/10/update/
  Content-Type: application/json
  
  {"alias": "行人", "alert_level": "high", "is_active": true}
  ```
- 示例响应:
  ```json
  {"success": true, "code": 200, "message": "更新类别成功", "data": {"id": 10, "alias": "行人", "alert_level": "high"}}
  ```

### （4）切换类别启用状态
- 方法: `POST`
- 路径: `/api/yolo/categories/{pk}/toggle-status/`
- 认证: 不需要
- 参考实现: `category_toggle_status`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1385）
- 示例响应:
  ```json
  {"success": true, "code": 200, "message": "类别 'person' 启用成功", "data": {"is_active": true}}
  ```

### （5）获取启用的类别列表
- 方法: `GET`
- 路径: `/api/yolo/categories/active/`
- 认证: 不需要
- 参考实现: `category_active_list`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1405）

### （6）创建类别（不推荐）
- 方法: `POST`
- 路径: `/api/yolo/categories/create/`
- 认证: 不需要
- 请求类型: `application/json`
- 参考实现: `category_create`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1312）

### （7）删除类别（不推荐）
- 方法: `DELETE`
- 路径: `/api/yolo/categories/{pk}/delete/`
- 认证: 不需要
- 参考实现: `category_delete`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:1362）


## 四、目标检测

### 执行检测
- 方法: `POST`
- 路径: `/api/yolo/detect/`
- 认证: 需要登录（`Authorization: Bearer <token>`）
- 请求类型: `multipart/form-data`
- 参数:
  - `file`: 要检测的图片或视频文件（支持图片：`.jpg,.jpeg,.png,.bmp,.tiff,.webp`；视频：`.mp4,.avi,.mov,.mkv,.wmv,.flv`）
  - `model_id`: 指定模型ID（可选，未提供则使用当前启用模型）
  - `confidence_threshold`: 置信度阈值（默认 `0.5`，范围 `0.1-1.0`）
- 参考实现: `yolo_detection`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:446）
- 示例请求:
  ```bash
  curl -X POST "http://localhost:8000/api/yolo/detect/" \
    -H "Authorization: Bearer <token>" \
    -F "file=@/path/to/image.jpg" \
    -F "model_id=1" \
    -F "confidence_threshold=0.5"
  ```
- 示例响应:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "检测完成",
    "data": {
      "detection_id": 1001,
      "result_file_url": "/media/detection/result/result_xxx.jpg",
      "original_file_url": "/media/detection/original/uuid_image.jpg",
      "object_count": 3,
      "detected_categories": ["person"],
      "confidence_scores": [0.91, 0.87, 0.79],
      "avg_confidence": 0.8567,
      "processing_time": 0.43,
      "model_used": "ModelA 1.0",
      "confidence_threshold": 0.5,
      "user_id": 2,
      "user_name": "alice",
      "alert_level": "medium"
    }
  }
  ```


## 五、检测记录

### （1）获取检测记录列表
- 方法: `GET`
- 路径: `/api/yolo/detections/`
- 认证: 不需要
- 查询参数:
  - `type`: `image` 或 `video`
  - `model_id`: 模型ID
  - `user_id`: 用户ID
- 参考实现: `detection_list`（d:\All_template\yolo\hertz_studio_django_yolo\views.py:204）
- 示例响应（节选）:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "获取检测记录列表成功",
    "data": [
      {
        "id": 1001,
        "original_file": "/media/detection/original/uuid_image.jpg",
        "result_file": "/media/detection/result/result_xxx.jpg",
        "original_filename": "uuid_image.jpg",
        "result_filename": "result_xxx.jpg",
        "detection_type": "image",
        "model_name": "ModelA 1.0",
        "model_info": {"id":1, "name":"ModelA", "version":"1.0"},
        "object_count": 3,
        "detected_categories": ["person"],
        "confidence_threshold": 0.5,
        "confidence_scores": [0.91, 0.87, 0.79],
        "avg_confidence": 0.8567,
        "processing_time": 0.43,
        "created_at": "..."
      }
    ]
  }
  ```

### （2）获取指定用户的检测记录
- 方法: `GET`
- 路径: `/api/yolo/detections/{user_id}/user/`
- 认证: 不需要
- 查询参数同上
- 参考实现: `user_detection_records`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:231）

### （3）获取检测记录详情
- 方法: `GET`
- 路径: `/api/yolo/detections/{pk}/`
- 认证: 不需要
- 参考实现: `detection_detail`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:253）

### （4）删除检测记录
- 方法: `DELETE`
- 路径: `/api/yolo/detections/{pk}/delete/`
- 认证: 不需要
- 行为: 同时删除其关联的原始文件、结果文件及关联的告警
- 参考实现: `detection_delete`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:265）
- 示例响应:
  ```json
  {"success": true, "code": 200, "message": "检测记录删除成功"}
  ```

### （5）批量删除检测记录
- 方法: `POST`
- 路径: `/api/yolo/detections/batch-delete/`
- 认证: 不需要
- 请求类型: `application/json`
- 请求体:
  ```json
  {"ids": [1001, 1002, 1003]}
  ```
- 参考实现: `detection_batch_delete`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:299）
- 示例响应:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "成功删除 3 条检测记录",
    "data": {
      "deleted_count": 3,
      "found_ids": ["1001","1002","1003"],
      "not_found_ids": []
    }
  }
  ```

### （6）检测统计
- 方法: `GET`
- 路径: `/api/yolo/stats/`
- 认证: 不需要
- 参考实现: `detection_stats`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:840）


## 六、告警记录

### （1）获取告警记录列表（管理员）
- 方法: `GET`
- 路径: `/api/yolo/alerts/`
- 认证: 不需要
- 查询参数:
  - `status`: 默认 `pending`；传 `all` 表示不过滤
  - `level`: 告警等级（`high|medium|low|none`）
  - `user_id`: 用户ID
  - `alter_category`: 告警类别关键字（注意字段名为 `alter_category`）
- 参考实现: `alert_list`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:358）

### （2）获取用户的告警记录
- 方法: `GET`
- 路径: `/api/yolo/users/{user_id}/alerts/`
- 认证: 需要登录（仅本人或管理员可查）
- 查询参数:
  - `status`: `pending|is_confirm|false_positive|all`
  - `level`: `high|medium|low|none`
  - `category`: 类别关键字
- 参考实现: `user_alert_records`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:391）

### （3）更新告警状态
- 方法: `PUT` 或 `PATCH`
- 路径: `/api/yolo/alerts/{pk}/update-status/`
- 认证: 不需要
- 请求类型: `application/json`
- 请求体:
  ```json
  {"status": "is_confirm"}
  ```
- 可选值: `pending`, `is_confirm`, `false_positive`
- 参考实现: `alert_update_status`（d:\AllTemplate\yolo\hertz_studio_django_yolo\views.py:426）
- 示例响应:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "更新告警状态成功",
    "data": {
      "id": 555,
      "status": "is_confirm",
      "alert_level": "medium",
      "alert_category": "person",
      "alert_level_display": "中"
    }
  }
  ```


## 七、备注
- 所有文件型字段响应通常包含可直接访问的媒体 URL，媒体服务由 `MEDIA_URL=/media/` 提供。
- 分类的告警等级枚举参考 `ModelCategory.ALERT_LEVELS` 与 `Alert.ALERT_LEVELS`（d:\AllTemplate\yolo\hertz_studio_django_yolo\models.py:118,153）。
- 检测请求的文件大小限制：图片 ≤ 50MB，视频 ≤ 500MB（d:\AllTemplate\yolo\hertz_studio_django_yolo\serializers.py:99）。

