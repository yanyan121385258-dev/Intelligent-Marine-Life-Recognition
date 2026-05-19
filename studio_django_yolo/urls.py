from django.urls import path
from . import views

app_name = 'studio_django_yolo'

urlpatterns = [

    # ==============模型上传接口==============
    path('upload/', views.model_upload, name='model-upload'),
    path('onnx/upload/', views.upload_pt_convert_onnx, name='onnx-upload'),

    # ==============数据集管理接口==============
    path('datasets/upload/', views.dataset_upload, name='dataset-upload'),  #  上传数据集
    path('datasets/', views.dataset_list, name='dataset-list'),  #  获取数据集列表
    path('datasets/<int:pk>/', views.dataset_detail, name='dataset-detail'),     #  获取数据集详情
    path('datasets/<int:pk>/delete/', views.dataset_delete, name='dataset-delete'),  # 删除数据集
    path('datasets/<int:pk>/samples/', views.dataset_samples, name='dataset-samples'),  # 获取数据集样本

    #============== 模型管理接口===============
    path('models/', views.model_list, name='model-list'),
    path('models/create/', views.model_create, name='model-create'),
    path('models/<int:pk>/', views.model_detail, name='model-detail'),
    path('models/<int:pk>/update/', views.model_update, name='model-update'),
    path('models/<int:pk>/delete/', views.model_delete, name='model-delete'),
    path('models/<int:pk>/enable/', views.model_enable, name='model-enable'),
    path('models/enabled/', views.model_enabled, name='model-enabled'),

    # ==============模型类别管理接口==============
    path('categories/', views.category_list, name='category-list'),
    path('categories/create/', views.category_create, name='category-create'),      #建议不使用，类别通过上传模型获取
    path('categories/<int:pk>/', views.category_detail, name='category-detail'),
    path('categories/<int:pk>/update/', views.category_update, name='category-update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),     #建议不使用，否则会导致检测框中展示英文
    path('categories/<int:pk>/toggle-status/', views.category_toggle_status, name='category-toggle-status'),
    path('categories/active/', views.category_active_list, name='category-active-list'),

    # ==============检测接口==============
    path('detect/', views.yolo_detection, name='detect'),

    # ==============检测记录接口==============
    path('detections/', views.detection_list, name='detection-list'),
    path('detections/<int:pk>/', views.detection_detail, name='detection-detail'),
    path('detections/<int:pk>/delete/', views.detection_delete, name='detection-delete'),
    path('detections/batch-delete/', views.detection_batch_delete, name='detection-batch-delete'),
    path('stats/', views.detection_stats, name='detection-stats'),    # 统计接口
    path('detections/<int:user_id>/user/', views.user_detection_records, name='user-detection-records'),    # 用户检测记录接口

    # ==============告警记录接口==============
    path('alerts/', views.alert_list, name='alert-list'),    # 管理员查询所有告警记录
    path('alerts/<int:pk>/update-status/', views.alert_update_status, name='alert-update-status'),      #更新告警记录
    path('users/<int:user_id>/alerts/', views.user_alert_records, name='user-alert-records'),    # 用户查询自己的告警记录

]