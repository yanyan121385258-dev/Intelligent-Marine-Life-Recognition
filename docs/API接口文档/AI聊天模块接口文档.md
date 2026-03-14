# Hertz Studio Django AI聊天模块接口文档

- 基础路径: `/api/ai/`
- 统一响应: 使用 `HertzResponse`，结构如下
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {}
  }
  ```
- 路由挂载: 项目主路由通过 `path('api/ai/', include('hertz_studio_django_ai.urls'))` 挂载（`hertz_server_django/urls.py:23`）。
- 认证说明: 所有接口需在请求头携带 `Authorization: Bearer <access_token>`（`hertz_studio_django_ai/views.py:34` 使用 `login_required`）。

## 接口列表

### 获取聊天列表
- 方法: `GET`
- 路径: `/api/ai/chats/`
- 查询参数:
  - `query` 可选，按标题模糊搜索
  - `page` 可选，默认 `1`
  - `page_size` 可选，默认 `10`
- 实现: `AIChatListView.get`（`hertz_studio_django_ai/views.py:36`）
- 请求示例:
  ```http
  GET /api/ai/chats/?query=Python&page=1&page_size=10
  Authorization: Bearer <access_token>
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {
      "total": 25,
      "page": 1,
      "page_size": 10,
      "chats": [
        {
          "id": 1,
          "title": "Python编程问题",
          "created_at": "2024-01-15 10:30:00",
          "updated_at": "2024-01-15 10:35:00",
          "latest_message": "如何使用Django创建API接口？..."
        }
      ]
    }
  }
  ```

### 创建聊天
- 方法: `POST`
- 路径: `/api/ai/chats/create/`
- 请求体: `application/json`
- 字段: `title` 可选，默认 `"新对话"`
- 实现: `AIChatCreateView.post`（`hertz_studio_django_ai/views.py:100`）
- 请求示例:
  ```http
  POST /api/ai/chats/create/
  Authorization: Bearer <access_token>
  Content-Type: application/json

  {
    "title": "AI编程助手"
  }
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "创建成功",
    "data": {
      "chat_id": 3,
      "title": "AI编程助手"
    }
  }
  ```

### 聊天详情
- 方法: `GET`
- 路径: `/api/ai/chats/{chat_id}/`
- 路径参数: `chat_id` 聊天ID（整数）
- 实现: `AIChatDetailView.get`（`hertz_studio_django_ai/views.py:137`）
- 请求示例:
  ```http
  GET /api/ai/chats/1/
  Authorization: Bearer <access_token>
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {
      "id": 1,
      "title": "Python编程问题",
      "created_at": "2024-01-15 10:30:00",
      "updated_at": "2024-01-15 10:35:00",
      "messages": [
        {
          "id": 1,
          "role": "user",
          "content": "如何使用Django创建API接口？",
          "created_at": "2024-01-15 10:30:00"
        },
        {
          "id": 2,
          "role": "assistant",
          "content": "使用Django REST Framework可以快速构建API...",
          "created_at": "2024-01-15 10:30:30"
        }
      ]
    }
  }
  ```

### 更新聊天
- 方法: `PUT`
- 路径: `/api/ai/chats/{chat_id}/update/`
- 路径参数: `chat_id` 聊天ID（整数）
- 请求体: `application/json`
- 字段: `title` 新标题
- 实现: `AIChatUpdateView.put`（`hertz_studio_django_ai/views.py:192`）
- 请求示例:
  ```http
  PUT /api/ai/chats/1/update/
  Authorization: Bearer <access_token>
  Content-Type: application/json

  {
    "title": "更新后的标题"
  }
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "更新成功",
    "data": null
  }
  ```

### 删除聊天（批量）
- 方法: `POST`
- 路径: `/api/ai/chats/delete/`
- 请求体: `application/json`
- 字段: `chat_ids` 要删除的聊天ID数组（整数）
- 实现: `AIChatDeleteView.post`（`hertz_studio_django_ai/views.py:231`）
- 请求示例:
  ```http
  POST /api/ai/chats/delete/
  Authorization: Bearer <access_token>
  Content-Type: application/json

  {
    "chat_ids": [1, 2, 3]
  }
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "成功删除3个聊天",
    "data": null
  }
  ```

### 发送消息
- 方法: `POST`
- 路径: `/api/ai/chats/{chat_id}/send/`
- 路径参数: `chat_id` 聊天ID（整数）
- 请求体: `application/json`
- 字段: `content` 必填，消息内容，不能为空
- 实现: `AIChatSendMessageView.post`（`hertz_studio_django_ai/views.py:280`）
- 请求示例:
  ```http
  POST /api/ai/chats/1/send/
  Authorization: Bearer <access_token>
  Content-Type: application/json

  {
    "content": "你好，请介绍一下Python的特点"
  }
  ```
- 成功返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {
      "user_message": {
        "id": 5,
        "role": "user",
        "content": "你好，请介绍一下Python的特点",
        "created_at": "2024-01-15 11:30:00"
      },
      "ai_message": {
        "id": 6,
        "role": "assistant",
        "content": "Python是一种高级编程语言，语法简洁，生态丰富...",
        "created_at": "2024-01-15 11:30:05"
      }
    }
  }
  ```
- 失败返回示例（参数验证失败）:
  ```json
  {
    "success": false,
    "code": 422,
    "message": "参数验证失败",
    "data": {
      "content": ["消息内容不能为空"]
    }
  }
  ```
- 失败返回示例（聊天不存在）:
  ```json
  {
    "success": false,
    "code": 404,
    "message": "聊天不存在或无权访问",
    "data": null
  }
  ```
- 失败返回示例（AI生成失败）:
  ```json
  {
    "success": false,
    "code": 500,
    "message": "AI回复生成失败：服务不可用",
    "data": null
  }
  ```

## 附注
- 列表与详情时间字段为字符串格式 `YYYY-MM-DD HH:mm:ss`（`hertz_studio_django_ai/views.py:65`、`hertz_studio_django_ai/views.py:151`）。
- AI模型名称由配置项 `settings.AI_MODEL_NAME` 控制，默认 `deepseek-r1:1.5b`（`hertz_studio_django_ai/views.py:263`）。