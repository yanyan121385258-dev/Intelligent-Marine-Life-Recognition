# 数据库关系文档

## 1. 认证模块 (hertz_studio_django_auth)

### 1.1 表结构

#### HertzUser (用户表)
- `user_id`: 主键，用户ID
- `username`: 用户名（唯一）
- `password`: 密码
- `email`: 邮箱（唯一）
- `phone`: 手机号
- `real_name`: 真实姓名
- `avatar`: 头像URL
- `gender`: 性别（0=未知，1=男，2=女）
- `birthday`: 生日
- `department_id`: 部门ID（外键）
- `status`: 状态（0=禁用，1=启用）
- `last_login_time`: 最后登录时间
- `last_login_ip`: 最后登录IP
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `is_active`: 是否激活
- `is_staff`: 是否员工
- `is_superuser`: 是否超级用户

#### HertzRole (角色表)
- `role_id`: 主键，角色ID
- `role_name`: 角色名称（唯一）
- `role_code`: 角色代码（唯一）
- `description`: 角色描述
- `status`: 状态（0=禁用，1=启用）
- `sort_order`: 排序
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### HertzMenu (菜单表)
- `menu_id`: 主键，菜单ID
- `parent_id`: 父菜单ID（外键，自关联）
- `menu_name`: 菜单名称
- `menu_code`: 菜单代码（唯一）
- `menu_type`: 菜单类型（1=目录，2=菜单，3=按钮）
- `path`: 路由路径
- `component`: 组件路径
- `icon`: 菜单图标
- `permission`: 权限标识
- `status`: 状态（0=禁用，1=启用）
- `sort_order`: 排序
- `is_external`: 是否外链
- `is_cache`: 是否缓存
- `is_visible`: 是否显示
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### HertzDepartment (部门表)
- `dept_id`: 主键，部门ID
- `parent_id`: 父部门ID（外键，自关联）
- `dept_name`: 部门名称
- `dept_code`: 部门代码（唯一）
- `leader`: 负责人
- `phone`: 联系电话
- `email`: 邮箱
- `status`: 状态（0=禁用，1=启用）
- `sort_order`: 排序
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### HertzUserRole (用户角色关联表)
- `id`: 主键，ID
- `user`: 用户ID（外键 → HertzUser）
- `role`: 角色ID（外键 → HertzRole）
- `created_at`: 创建时间
- **唯一约束**: (user, role)

#### HertzRoleMenu (角色菜单关联表)
- `id`: 主键，ID
- `role`: 角色ID（外键 → HertzRole）
- `menu`: 菜单ID（外键 → HertzMenu）
- `created_at`: 创建时间
- **唯一约束**: (role, menu)

### 1.2 关系图

```
HertzUser (用户表)
    ├── department_id → HertzDepartment (部门表) [多对一]
    ├── HertzUserRole (用户角色关联表) [一对多]
    │   └── role → HertzRole (角色表) [多对一]
    │       └── HertzRoleMenu (角色菜单关联表) [一对多]
    │           └── menu → HertzMenu (菜单表) [多对一]
    │               └── parent_id → HertzMenu (菜单表) [自关联]
    └── HertzUserNotice (用户通知状态表) [一对多]
        └── notice → HertzNotice (通知表) [多对一]

HertzDepartment (部门表)
    └── parent_id → HertzDepartment (部门表) [自关联]
```

### 1.3 关系说明

1. **用户-部门关系**: 一个用户属于一个部门，一个部门可以有多个用户（多对一）
2. **用户-角色关系**: 一个用户可以有多个角色，一个角色可以分配给多个用户（多对多，通过HertzUserRole表）
3. **角色-菜单关系**: 一个角色可以访问多个菜单，一个菜单可以分配给多个角色（多对多，通过HertzRoleMenu表）
4. **菜单-菜单关系**: 菜单可以有子菜单，形成树形结构（自关联）
5. **部门-部门关系**: 部门可以有子部门，形成树形结构（自关联）

## 2. 知识库模块 (hertz_studio_django_kb)

### 2.1 表结构

#### KBItem (知识库条目表)
- `id`: 主键
- `user`: 所属用户（外键 → HertzUser）
- `title`: 条目标题
- `modality`: 内容模态类型（text/code/image/audio/video）
- `source_type`: 内容来源类型（text/file/url）
- `content`: 文本内容
- `file`: 文件内容
- `metadata`: 附加元数据（JSON）
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### KBChunk (知识片段表)
- `id`: 主键
- `item`: 知识库条目ID（外键 → KBItem）
- `index`: 片段序号
- `text`: 片段文本内容
- `embedding`: 片段向量（JSON）
- `created_at`: 片段创建时间

#### KBEntity (知识图谱实体表)
- `id`: 主键
- `name`: 实体名称
- `type`: 实体类型
- `properties`: 额外属性字典（JSON）
- `created_at`: 创建时间

#### KBRelation (知识图谱关系表)
- `id`: 主键
- `source`: 源实体ID（外键 → KBEntity）
- `target`: 目标实体ID（外键 → KBEntity）
- `relation_type`: 关系类型
- `properties`: 关系的附加属性（JSON）
- `source_chunk`: 来源片段ID（外键 → KBChunk，可为空）
- `created_at`: 创建时间

### 2.2 关系图

```
HertzUser (用户表)
    └── KBItem (知识库条目表) [一对多]
        └── KBChunk (知识片段表) [一对多]
            └── KBRelation (知识图谱关系表) [多对一]

KBEntity (知识图谱实体表)
    ├── outgoing_relations → KBRelation (知识图谱关系表) [一对多]
    └── incoming_relations → KBRelation (知识图谱关系表) [一对多]
```

### 2.3 关系说明

1. **用户-知识库条目关系**: 一个用户可以创建多个知识库条目（一对多）
2. **知识库条目-知识片段关系**: 一个知识库条目可以包含多个知识片段（一对多）
3. **知识片段-知识图谱关系关系**: 一个知识片段可以关联多个知识图谱关系（一对多）
4. **实体-知识图谱关系关系**: 实体之间可以有多个关系，一个实体可以作为源实体或目标实体（一对多）

## 3. YOLO模块 (hertz_studio_django_yolo)

### 3.1 表结构

#### Dataset (数据集表)
- `id`: 主键
- `name`: 数据集名称
- `version`: 版本
- `zip_file`: 数据集压缩包
- `root_folder_path`: 数据集根路径
- `data_yaml_path`: 配置文件路径
- `names`: 类别名称（JSON）
- `nc`: 类别数量
- `train_images_count`: 训练集图片数
- `train_labels_count`: 训练集标注数
- `val_images_count`: 验证集图片数
- `val_labels_count`: 验证集标注数
- `test_images_count`: 测试集图片数
- `test_labels_count`: 测试集标注数
- `description`: 描述
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### YoloModel (YOLO模型表)
- `id`: 主键
- `name`: 模型名称
- `version`: 版本
- `model_file`: 模型文件
- `model_folder_path`: 模型文件夹路径
- `best_model_path`: 最佳模型路径
- `last_model_path`: 最后模型路径
- `categories`: 类别信息（JSON）
- `is_enabled`: 是否启用
- `description`: 描述
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### DetectionRecord (检测记录表)
- `id`: 主键
- `original_file`: 原始文件
- `result_file`: 检测结果文件
- `detection_type`: 检测类型（image/video）
- `model_name`: 使用的模型名称
- `model`: 使用的模型ID（外键 → YoloModel）
- `user`: 检测用户ID（外键 → HertzUser）
- `user_name`: 用户名称
- `object_count`: 检测到的对象数量
- `detected_categories`: 检测到的类别列表（JSON）
- `confidence_threshold`: 置信度阈值
- `confidence_scores`: 真实置信度列表（JSON）
- `avg_confidence`: 平均置信度
- `processing_time`: 处理时间（秒）
- `created_at`: 检测时间

#### ModelCategory (模型类别表)
- `id`: 主键
- `model`: 关联模型ID（外键 → YoloModel）
- `name`: 类别名称
- `alias`: 类别别名
- `category_id`: 类别ID
- `description`: 类别描述
- `alert_level`: 告警等级（high/medium/low/none）
- `is_active`: 是否启用
- `created_at`: 创建时间
- `updated_at`: 更新时间
- **唯一约束**: (model, category_id)

#### Alert (告警记录表)
- `id`: 主键
- `detection_record`: 关联的检测记录ID（外键 → DetectionRecord，一对一）
- `user`: 用户ID（外键 → HertzUser）
- `user_name`: 用户名称
- `alert_level`: 告警等级（high/medium/low/none）
- `alert_category`: 告警类别
- `category`: 关联类别ID（外键 → ModelCategory）
- `status`: 状态（pending/is_confirm/false_positive）
- `created_at`: 创建时间
- `deleted_at`: 删除时间

### 3.2 关系图

```
HertzUser (用户表)
    ├── DetectionRecord (检测记录表) [一对多]
    │   ├── model → YoloModel (YOLO模型表) [多对一]
    │   │   └── ModelCategory (模型类别表) [一对多]
    │   └── Alert (告警记录表) [一对一]
    │       └── category → ModelCategory (模型类别表) [多对一]
    └── Alert (告警记录表) [一对多]
```

### 3.3 关系说明

1. **用户-检测记录关系**: 一个用户可以进行多次检测（一对多）
2. **检测记录-模型关系**: 一个检测记录使用一个模型（多对一）
3. **模型-模型类别关系**: 一个模型可以有多个类别（一对多）
4. **检测记录-告警记录关系**: 一个检测记录对应一个告警记录（一对一）
5. **告警记录-模型类别关系**: 一个告警记录关联一个模型类别（多对一）
6. **用户-告警记录关系**: 一个用户可以有多个告警记录（一对多）

## 4. 通知模块 (hertz_studio_django_notice)

### 4.1 表结构

#### HertzNotice (通知表)
- `notice_id`: 主键，通知ID
- `title`: 通知标题
- `content`: 通知内容
- `notice_type`: 通知类型（1=系统通知，2=公告通知，3=活动通知，4=维护通知）
- `priority`: 优先级（1=低，2=中，3=高，4=紧急）
- `status`: 状态（0=草稿，1=已发布，2=已撤回）
- `is_top`: 是否置顶
- `publish_time`: 发布时间
- `expire_time`: 过期时间
- `publisher`: 发布者ID（外键 → HertzUser）
- `attachment_url`: 附件链接
- `view_count`: 查看次数
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### HertzUserNotice (用户通知状态表)
- `id`: 主键，ID
- `user`: 用户ID（外键 → HertzUser）
- `notice`: 通知ID（外键 → HertzNotice）
- `is_read`: 是否已读
- `read_time`: 阅读时间
- `is_starred`: 是否收藏
- `starred_time`: 收藏时间
- `created_at`: 创建时间
- `updated_at`: 更新时间
- **唯一约束**: (user, notice)

### 4.2 关系图

```
HertzUser (用户表)
    └── HertzUserNotice (用户通知状态表) [一对多]
        └── notice → HertzNotice (通知表) [多对一]

HertzNotice (通知表)
    ├── publisher → HertzUser (用户表) [多对一]
    └── HertzUserNotice (用户通知状态表) [一对多]
```

### 4.3 关系说明

1. **用户-用户通知状态关系**: 一个用户可以有多个用户通知状态记录（一对多）
2. **通知-用户通知状态关系**: 一个通知可以有多个用户通知状态记录（一对多）
3. **用户-通知关系**: 多对多关系，通过HertzUserNotice表实现
4. **发布者-通知关系**: 一个用户可以发布多个通知（一对多）

## 5. 完整关系图

```
HertzUser (用户表)
    ├── department_id → HertzDepartment (部门表) [多对一]
    ├── HertzUserRole (用户角色关联表) [一对多]
    │   └── role → HertzRole (角色表) [多对一]
    │       └── HertzRoleMenu (角色菜单关联表) [一对多]
    │           └── menu → HertzMenu (菜单表) [多对一]
    │               └── parent_id → HertzMenu (菜单表) [自关联]
    ├── KBItem (知识库条目表) [一对多]
    │   └── KBChunk (知识片段表) [一对多]
    │       └── KBRelation (知识图谱关系表) [多对一]
    ├── DetectionRecord (检测记录表) [一对多]
    │   ├── model → YoloModel (YOLO模型表) [多对一]
    │   │   └── ModelCategory (模型类别表) [一对多]
    │   └── Alert (告警记录表) [一对一]
    │       └── category → ModelCategory (模型类别表) [多对一]
    ├── Alert (告警记录表) [一对多]
    ├── HertzUserNotice (用户通知状态表) [一对多]
    │   └── notice → HertzNotice (通知表) [多对一]
    │       └── publisher → HertzUser (用户表) [多对一]

HertzDepartment (部门表)
    └── parent_id → HertzDepartment (部门表) [自关联]

KBEntity (知识图谱实体表)
    ├── outgoing_relations → KBRelation (知识图谱关系表) [一对多]
    └── incoming_relations → KBRelation (知识图谱关系表) [一对多]
```

## 6. 使用示例

### 6.1 获取用户的所有角色

```python
from hertz_studio_django_auth.models import HertzUser

user = HertzUser.objects.get(username='test_user')
roles = user.roles.all()  # 通过@property方法获取
```

### 6.2 获取角色的所有菜单

```python
from hertz_studio_django_auth.models import HertzRole

role = HertzRole.objects.get(role_code='admin')
menus = role.menus.all()  # 通过@property方法获取
```

### 6.3 获取用户的检测记录

```python
from hertz_studio_django_auth.models import HertzUser
from hertz_studio_django_yolo.models import DetectionRecord

user = HertzUser.objects.get(username='test_user')
detection_records = user.detection_records.all()
```

### 6.4 获取用户的告警记录

```python
from hertz_studio_django_auth.models import HertzUser
from hertz_studio_django_yolo.models import Alert

user = HertzUser.objects.get(username='test_user')
alerts = user.alerts.all()
```

### 6.5 获取用户的通知

```python
from hertz_studio_django_auth.models import HertzUser

user = HertzUser.objects.get(username='test_user')
user_notices = user.user_notices.all()
unread_notices = user.user_notices.filter(is_read=False)
```

### 6.6 获取知识库条目及其片段

```python
from hertz_studio_django_kb.models import KBItem

item = KBItem.objects.get(id=1)
chunks = item.chunks.all()
```

### 6.7 获取模型的类别

```python
from hertz_studio_django_yolo.models import YoloModel

model = YoloModel.objects.get(id=1)
categories = model.model_categories.all()
```

## 7. 数据库索引

### 7.1 认证模块索引

- `hertz_auth_user`: (username), (email)
- `hertz_auth_role`: (role_name), (role_code)
- `hertz_auth_menu`: (menu_code), (parent_id), (sort_order)
- `hertz_auth_department`: (dept_code), (parent_id), (sort_order)
- `hertz_auth_user_role`: (user, role) - 唯一索引
- `hertz_auth_role_menu`: (role, menu) - 唯一索引

### 7.2 知识库模块索引

- `hertz_kb_item`: (user), (created_at), (updated_at)
- `hertz_kb_chunk`: (item_id, index)
- `hertz_kb_entity`: (name), (type)
- `hertz_kb_relation`: (relation_type)

### 7.3 YOLO模块索引

- `hertz_yolo_dataset`: (created_at)
- `hertz_yolo_yolo_model`: (created_at)
- `hertz_yolo_detection_record`: (created_at)
- `hertz_yolo_model_category`: (model, category_id) - 唯一索引
- `hertz_yolo_alert_record`: (alert_level, created_at)

### 7.4 通知模块索引

- `hertz_notice_notice`: (status, publish_time), (notice_type, status), (is_top, priority)
- `hertz_notice_user_notice`: (user, notice) - 唯一索引, (user, is_read), (user, is_starred), (notice, is_read)

## 8. 数据库约束

### 8.1 唯一约束

- `hertz_auth_user`: username, email
- `hertz_auth_role`: role_name, role_code
- `hertz_auth_menu`: menu_code
- `hertz_auth_department`: dept_code
- `hertz_auth_user_role`: (user, role)
- `hertz_auth_role_menu`: (role, menu)
- `hertz_yolo_model_category`: (model, category_id)
- `hertz_notice_user_notice`: (user, notice)

### 8.2 外键约束

- `hertz_auth_user.department_id` → `hertz_auth_department.dept_id`
- `hertz_auth_menu.parent_id` → `hertz_auth_menu.menu_id`
- `hertz_auth_department.parent_id` → `hertz_auth_department.dept_id`
- `hertz_auth_user_role.user` → `hertz_auth_user.user_id`
- `hertz_auth_user_role.role` → `hertz_auth_role.role_id`
- `hertz_auth_role_menu.role` → `hertz_auth_role.role_id`
- `hertz_auth_role_menu.menu` → `hertz_auth_menu.menu_id`
- `hertz_kb_item.user` → `hertz_auth_user.user_id`
- `hertz_kb_chunk.item` → `hertz_kb_item.id`
- `hertz_kb_relation.source` → `hertz_kb_entity.id`
- `hertz_kb_relation.target` → `hertz_kb_entity.id`
- `hertz_kb_relation.source_chunk` → `hertz_kb_chunk.id`
- `hertz_yolo_detection_record.model` → `hertz_yolo_yolo_model.id`
- `hertz_yolo_detection_record.user` → `hertz_auth_user.user_id`
- `hertz_yolo_model_category.model` → `hertz_yolo_yolo_model.id`
- `hertz_yolo_alert_record.detection_record` → `hertz_yolo_detection_record.id`
- `hertz_yolo_alert_record.user` → `hertz_auth_user.user_id`
- `hertz_yolo_alert_record.category` → `hertz_yolo_model_category.id`
- `hertz_notice_notice.publisher` → `hertz_auth_user.user_id`
- `hertz_notice_user_notice.user` → `hertz_auth_user.user_id`
- `hertz_notice_user_notice.notice` → `hertz_notice_notice.notice_id`

## 9. 数据库迁移

### 9.1 创建迁移文件

```bash
python manage.py makemigrations
```

### 9.2 执行迁移

```bash
python manage.py migrate
```

### 9.3 查看迁移状态

```bash
python manage.py showmigrations
```

### 9.4 回滚迁移

```bash
python manage.py migrate <app_name> <migration_name>
```

## 10. 数据库优化建议

### 10.1 查询优化

1. 使用 `select_related` 优化外键查询
2. 使用 `prefetch_related` 优化多对多查询
3. 合理使用 `only()` 和 `defer()` 减少查询字段
4. 使用 `annotate()` 和 `aggregate()` 进行聚合查询

### 10.2 索引优化

1. 为经常查询的字段添加索引
2. 为经常用于排序的字段添加索引
3. 为经常用于连接的字段添加索引
4. 定期分析索引使用情况，删除无用索引

### 10.3 数据库维护

1. 定期清理过期数据
2. 定期优化表结构
3. 定期备份数据库
4. 监控数据库性能，及时优化慢查询

## 11. 数据库备份与恢复

### 11.1 备份数据库

```bash
python manage.py dumpdata > backup.json
```

### 11.2 恢复数据库

```bash
python manage.py loaddata backup.json
```

### 11.3 备份特定应用

```bash
python manage.py dumpdata hertz_studio_django_auth > auth_backup.json
```

## 12. 常见问题

### 12.1 如何处理外键约束错误？

在删除记录前，先删除或更新相关联的记录，或者使用 `on_delete` 参数设置级联删除行为。

### 12.2 如何处理多对多关系？

使用 Django 的 `ManyToManyField` 或创建中间表来处理多对多关系。

### 12.3 如何优化查询性能？

使用 `select_related` 和 `prefetch_related` 减少查询次数，合理使用索引，避免 N+1 查询问题。

### 12.4 如何处理大数据量？

使用分页查询、批量操作、数据库分区等技术来处理大数据量。

## 13. 总结

本系统数据库设计遵循以下原则：

1. **规范化设计**: 遵循数据库范式，减少数据冗余
2. **关系清晰**: 表之间的关系明确，外键约束完整
3. **性能优化**: 合理使用索引，优化查询性能
4. **扩展性**: 设计具有良好的扩展性，便于后续功能扩展
5. **数据完整性**: 通过外键约束和唯一约束保证数据完整性

系统主要包含以下模块：

- **认证模块**: 用户、角色、菜单、部门管理
- **知识库模块**: 知识库条目、知识片段、知识图谱管理
- **YOLO模块**: 数据集、模型、检测记录、告警管理
- **通知模块**: 通知发布、用户通知状态管理

各模块之间通过外键关联，形成完整的业务数据关系。