# Hertz Studio Django Wiki 接口文档

- 基础路径: `/api/wiki/`
- 统一响应: 使用 `HertzResponse`，结构如下（参考 `hertz_studio_django_utils/responses/HertzResponse.py`）
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {}
  }
  ```
- 路由挂载: 项目主路由中已通过 `path('api/wiki/', include('hertz_studio_django_wiki.urls'))` 挂载（`hertz_server_django/urls.py:29`）。
- 认证说明: 标注“需要登录”的接口需在请求头携带 `Authorization: Bearer <token>`（`hertz_studio_django_auth/utils/decorators/auth_decorators.py:1`）。


## 一、知识分类管理

### （1）获取分类列表
- 方法: `GET`
- 路径: `/api/wiki/categories/`
- 认证: 不需要
- 查询参数:
  - `page`: 页码，默认 `1`
  - `page_size`: 每页数量，默认 `10`
  - `name`: 分类名称关键字
  - `parent_id`: 父分类ID（`0` 表示顶级）
  - `is_active`: `true/false`
- 实现: `wiki_category_list`（`hertz_studio_django_wiki/views.py:41`）
- 请求示例:
  ```bash
  curl "http://localhost:8000/api/wiki/categories/?page=1&page_size=10&name=技术"
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {
      "list": [
        {
          "id": 1,
          "name": "技术文档",
          "description": "技术相关文档",
          "parent": null,
          "parent_name": null,
          "sort_order": 1,
          "is_active": true,
          "created_at": "2024-01-01T10:00:00Z",
          "updated_at": "2024-01-01T10:00:00Z",
          "children_count": 3,
          "articles_count": 15,
          "full_path": "技术文档"
        }
      ],
      "total": 1,
      "page": 1,
      "page_size": 10
    }
  }
  ```

### （2）获取树形分类
- 方法: `GET`
- 路径: `/api/wiki/categories/tree/`
- 认证: 不需要
- 实现: `wiki_category_tree`（`hertz_studio_django_wiki/views.py:101`）
- 请求示例:
  ```bash
  curl "http://localhost:8000/api/wiki/categories/tree/"
  ```
- 返回示例:
  ```json
  [
    {
      "id": 1,
      "name": "技术文档",
      "description": "技术相关文档",
      "sort_order": 1,
      "is_active": true,
      "articles_count": 15,
      "children": [
        {"id": 2, "name": "后端", "children": []}
      ]
    }
  ]
  ```

### （3）创建分类
- 方法: `POST`
- 路径: `/api/wiki/categories/create/`
- 认证: 不需要
- 请求体: `application/json`
- 字段: `name`, `description`, `parent`, `sort_order`, `is_active`
- 实现: `wiki_category_create`（`hertz_studio_django_wiki/views.py:136`）
- 请求示例:
  ```http
  POST /api/wiki/categories/create/
  Content-Type: application/json
  
  {
    "name": "新分类",
    "description": "分类描述",
    "parent": null,
    "sort_order": 10,
    "is_active": true
  }
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "知识分类创建成功",
    "data": {
      "id": 5,
      "name": "新分类",
      "description": "分类描述",
      "parent": null,
      "parent_name": null,
      "sort_order": 10,
      "is_active": true,
      "created_at": "2025-11-17T10:00:00Z",
      "updated_at": "2025-11-17T10:00:00Z",
      "children_count": 0,
      "articles_count": 0,
      "full_path": "新分类"
    }
  }
  ```

### （4）分类详情
- 方法: `GET`
- 路径: `/api/wiki/categories/{category_id}/`
- 认证: 不需要
- 实现: `wiki_category_detail`（`hertz_studio_django_wiki/views.py:178`）
- 请求示例:
  ```bash
  curl "http://localhost:8000/api/wiki/categories/1/"
  ```
- 返回示例: 同“获取分类列表”中的单项结构。

### （5）更新分类
- 方法: `PUT`（支持部分更新）
- 路径: `/api/wiki/categories/{category_id}/update/`
- 认证: 不需要
- 请求体: `application/json`
- 可更新字段: `name`, `description`, `parent`, `sort_order`, `is_active`
- 实现: `wiki_category_update`（`hertz_studio_django_wiki/views.py:220`）
- 请求示例:
  ```http
  PUT /api/wiki/categories/1/update/
  Content-Type: application/json
  
  {
    "name": "更新后的分类名",
    "description": "更新后的描述",
    "sort_order": 20
  }
  ```
- 返回示例:
  ```json
  {"success": true, "code": 200, "message": "知识分类更新成功", "data": {"id": 1, "name": "更新后的分类名"}}
  ```

### （6）删除分类
- 方法: `DELETE`
- 路径: `/api/wiki/categories/{category_id}/delete/`
- 认证: 不需要
- 行为: 软删除（将 `is_active=false`）；若存在子分类或文章将返回错误
- 实现: `wiki_category_delete`（`hertz_studio_django_wiki/views.py:270`）
- 请求示例:
  ```bash
  curl -X DELETE "http://localhost:8000/api/wiki/categories/1/delete/"
  ```
- 返回示例:
  ```json
  {"success": true, "code": 200, "message": "知识分类删除成功"}
  ```


## 二、知识文章管理

### （1）获取文章列表
- 方法: `GET`
- 路径: `/api/wiki/articles/`
- 认证: 不需要
- 查询参数:
  - `page`, `page_size`
  - `title`: 标题关键字
  - `category_id`: 分类ID
  - `author_id`: 作者ID
  - `status`: `draft|published|archived`
- 实现: `wiki_article_list`（`hertz_studio_django_wiki/views.py:318`）
- 请求示例:
  ```bash
  curl "http://localhost:8000/api/wiki/articles/?page=1&page_size=10&category_id=1&status=published"
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {
      "list": [
        {
          "id": 101,
          "title": "如何部署Django",
          "summary": "部署流程概览",
          "image": null,
          "category_name": "技术文档",
          "author_name": "alice",
          "status": "published",
          "status_display": "已发布",
          "view_count": 42,
          "created_at": "2025-11-01T09:00:00Z",
          "updated_at": "2025-11-10T09:00:00Z",
          "published_at": "2025-11-10T09:00:00Z"
        }
      ],
      "total": 1,
      "page": 1,
      "page_size": 10
    }
  }
  ```

### （2）创建文章（需要登录）
- 方法: `POST`
- 路径: `/api/wiki/articles/create/`
- 认证: 需要登录（`Authorization: Bearer <token>`）
- 请求体: `application/json`
- 字段: `title`, `content`, `summary`, `image`, `category`, `status`, `tags`, `sort_order`
- 实现: `wiki_article_create`（`hertz_studio_django_wiki/views.py:384`）
- 请求示例:
  ```http
  POST /api/wiki/articles/create/
  Authorization: Bearer <token>
  Content-Type: application/json
  
  {
    "title": "新文章",
    "content": "文章内容...",
    "summary": "文章摘要...",
    "image": null,
    "category": 1,
    "status": "draft",
    "tags": "django,部署",
    "sort_order": 10
  }
  ```
- 返回示例:
  ```json
  {
    "success": true,
    "code": 200,
    "message": "知识文章创建成功",
    "data": {
      "id": 102,
      "title": "新文章",
      "content": "文章内容...",
      "summary": "文章摘要...",
      "image": null,
      "category": 1,
      "category_name": "技术文档",
      "author": 2,
      "author_name": "alice",
      "status": "draft",
      "status_display": "草稿",
      "tags": "django,部署",
      "tags_list": ["django", "部署"],
      "view_count": 0,
      "sort_order": 10,
      "created_at": "2025-11-17T11:00:00Z",
      "updated_at": "2025-11-17T11:00:00Z",
      "published_at": null
    }
  }
  ```

### （3）文章详情
- 方法: `GET`
- 路径: `/api/wiki/articles/{article_id}/`
- 认证: 不需要
- 行为: 获取详情并增加浏览量
- 实现: `wiki_article_detail`（`hertz_studio_django_wiki/views.py:426`）
- 请求示例:
  ```bash
  curl "http://localhost:8000/api/wiki/articles/102/"
  ```
- 返回示例: 同“创建文章”中的完整字段结构，`view_count` 将递增。

### （4）更新文章
- 方法: `PUT`（支持部分更新）
- 路径: `/api/wiki/articles/{article_id}/update/`
- 认证: 不需要
- 请求体: `application/json`
- 可更新字段: `title`, `content`, `summary`, `image`, `category`, `status`, `tags`, `sort_order`
- 实现: `wiki_article_update`（`hertz_studio_django_wiki/views.py:472`）
- 请求示例:
  ```http
  PUT /api/wiki/articles/102/update/
  Content-Type: application/json
  
  {
    "status": "published",
    "summary": "更新后的摘要"
  }
  ```
- 返回示例:
  ```json
  {"success": true, "code": 200, "message": "知识文章更新成功", "data": {"id": 102, "status": "published"}}
  ```

### （5）删除文章
- 方法: `DELETE`
- 路径: `/api/wiki/articles/{article_id}/delete/`
- 认证: 不需要
- 实现: `wiki_article_delete`（`hertz_studio_django_wiki/views.py:518`）
- 请求示例:
  ```bash
  curl -X DELETE "http://localhost:8000/api/wiki/articles/102/delete/"
  ```
- 返回示例:
  ```json
  {"success": true, "code": 200, "message": "知识文章删除成功"}
  ```

### （6）发布文章
- 方法: `POST`
- 路径: `/api/wiki/articles/{article_id}/publish/`
- 认证: 不需要
- 实现: `wiki_article_publish`（`hertz_studio_django_wiki/views.py:561`）
- 请求示例:
  ```bash
  curl -X POST "http://localhost:8000/api/wiki/articles/102/publish/"
  ```
- 返回示例:
  ```json
  {"success": true, "code": 200, "message": "知识文章发布成功"}
  ```
- 失败示例（已发布再次发布）:
  ```json
  {"success": false, "code": 500, "message": "系统错误", "error": "文章已经是发布状态"}
  ```

### （7）归档文章
- 方法: `POST`
- 路径: `/api/wiki/articles/{article_id}/archive/`
- 认证: 不需要
- 实现: `wiki_article_archive`（`hertz_studio_django_wiki/views.py:609`）
- 请求示例:
  ```bash
  curl -X POST "http://localhost:8000/api/wiki/articles/102/archive/"
  ```
- 返回示例:
  ```json
  {"success": true, "code": 200, "message": "知识文章归档成功"}
  ```


## 三、备注
- 文章状态枚举: `draft|published|archived`（`hertz_studio_django_wiki/models.py:35`）。
- 分类软删除通过 `is_active=false` 实现；删除校验会阻止删除存在子分类或文章的分类（`views.py:270`）。
- 文章详情接口会递增 `view_count`（`hertz_studio_django_wiki/models.py:70` 和 `views.py:431`）。