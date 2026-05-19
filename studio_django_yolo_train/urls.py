from django.urls import path
from . import views

app_name = 'studio_django_yolo_train'

urlpatterns = [
    path('options/', views.train_options, name='train-options'),    # 获取可训练的数据集相关信息
    path('jobs/', views.jobs, name='jobs'),     #  获取训练任务列表
    path('jobs/start/', views.start_training, name='start-training'),  #  开启训练
    path('jobs/<int:pk>/', views.job_detail, name='job-detail'),     #  获取训练任务详情
    path('jobs/<int:pk>/logs/', views.job_logs, name='job-logs'),     #  获取训练任务日志
    path('jobs/<int:pk>/cancel/', views.cancel_training, name='cancel-training'),    #  取消训练
    path('jobs/<int:pk>/download/', views.download_training, name='download-training'),  #  下载训练结果
    path('jobs/<int:pk>/delete/', views.delete_training, name='delete-training'),  # 删除训练任务
]