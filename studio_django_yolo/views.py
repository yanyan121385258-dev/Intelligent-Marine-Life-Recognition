import os
import time
import uuid
import zipfile
import shutil
import subprocess
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
from urllib.parse import quote

from studio_django_auth.utils.decorators import login_required
from .models import YoloModel, DetectionRecord, Alert, ModelCategory, Dataset
from .serializers import (
    YoloModelSerializer, YoloModelListSerializer, DetectionRecordSerializer,
    DetectionRequestSerializer, DetectionResponseSerializer, ModelEnableSerializer,
    AlertSerializer, AlertStatusUpdateSerializer, ModelCategorySerializer, ModelCategoryListSerializer,
    DatasetUploadSerializer, DatasetSerializer, DatasetListSerializer
)
from studio_django_utils.responses.HertzResponse import HertzResponse


def _get_category_aliases(categories, yolo_model):
    """获取类别的别名"""
    aliases = []
    for category in categories:
        try:
            # 查找对应的ModelCategory记录
            model_category = ModelCategory.objects.filter(
                model=yolo_model,
                name=category
            ).first()
            
            if model_category and model_category.alias:
                aliases.append(model_category.alias)
            else:
                aliases.append(category)  # 如果没有别名，使用原始类别名
        except Exception:
            aliases.append(category)  # 出错时使用原始类别名
    
    return aliases


def _draw_boxes_with_aliases(image, result, class_names, yolo_model):
    """绘制带中文别名的检测框（支持中文显示）"""
    if result.boxes is None or len(result.boxes) == 0:
        return image

    annotated_image = image.copy()
    boxes = result.boxes.xyxy.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    class_ids = result.boxes.cls.cpu().numpy().astype(int)

    # 将 OpenCV 图像转换为 PIL 格式
    img_pil = Image.fromarray(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # 选择字体（Windows 推荐使用 SimHei.ttf 或 Arial Unicode MS）
    font_path = "C:/Windows/Fonts/simhei.ttf"  # 修改为系统存在的字体路径
    font = ImageFont.truetype(font_path, 20)

    for (box, conf, class_id) in zip(boxes, confidences, class_ids):
        x1, y1, x2, y2 = box.astype(int)
        class_name = class_names[class_id]

        # 获取别名
        try:
            model_category = ModelCategory.objects.filter(
                model=yolo_model,
                name=class_name
            ).first()
            display_name = model_category.alias if (model_category and model_category.alias) else class_name
        except Exception:
            display_name = class_name

        label = f"{display_name} {conf:.2f}"

        # 绘制边框（使用 PIL 绘制也可以）
        draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=3)

        # 绘制标签背景
        text_size = draw.textbbox((x1, y1), label, font=font)
        text_w = text_size[2] - text_size[0]
        text_h = text_size[3] - text_size[1]
        draw.rectangle([x1, y1 - text_h - 4, x1 + text_w + 2, y1], fill=(0, 255, 0))
        draw.text((x1 + 1, y1 - text_h - 2), label, font=font, fill=(0, 0, 0))

    # 转回 OpenCV 格式
    annotated_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return annotated_image


# YOLO模型管理接口

@api_view(['GET'])
def model_list(request):
    """获取模型列表"""
    try:
        models = YoloModel.objects.all()
        serializer = YoloModelListSerializer(models, many=True)
        return HertzResponse.success(data=serializer.data, message="获取模型列表成功")
    except Exception as e:
        return HertzResponse.error(message="获取模型列表失败", error=str(e))


# YOLO目标检测接口

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def model_create(request):
    """创建模型（通过model_upload接口实现）"""
    return HertzResponse.fail(message="请使用 /api/upload/ 接口上传模型", code=405)


@api_view(['GET'])
def model_detail(request, pk):
    """获取模型详情"""
    try:
        model = YoloModel.objects.get(pk=pk)
        serializer = YoloModelSerializer(model)
        return HertzResponse.success(data=serializer.data, message="获取模型详情成功")
    except YoloModel.DoesNotExist:
        return HertzResponse.not_found(message="模型不存在")
    except Exception as e:
        return HertzResponse.error(message="获取模型详情失败", error=str(e))


@api_view(['PUT', 'PATCH'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def model_update(request, pk):
    """更新模型"""
    try:
        model = YoloModel.objects.get(pk=pk)
        serializer = YoloModelSerializer(model, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return HertzResponse.success(data=serializer.data, message="模型更新成功")
        else:
            return HertzResponse.validation_error(message="参数验证失败", errors=serializer.errors)
    except YoloModel.DoesNotExist:
        return HertzResponse.not_found(message="模型不存在")
    except Exception as e:
        return HertzResponse.error(message="模型更新失败", error=str(e))


@api_view(['DELETE'])
def model_delete(request, pk):
    """删除模型"""
    try:
        model = YoloModel.objects.get(pk=pk)
        model.delete()
        return HertzResponse.success(message="模型删除成功")
    except YoloModel.DoesNotExist:
        return HertzResponse.not_found(message="模型不存在")
    except Exception as e:
        return HertzResponse.error(message="模型删除失败", error=str(e))


@api_view(['POST'])
def model_enable(request, pk):
    """启用指定模型"""
    try:
        model = YoloModel.objects.get(pk=pk)
        # 禁用所有其他模型
        YoloModel.objects.exclude(pk=model.pk).update(is_enabled=False)
        # 启用当前模型
        model.is_enabled = True
        model.save()
        
        return HertzResponse.success(
            data=YoloModelSerializer(model).data,
            message=f'模型 {model.name} 已启用'
        )
    except YoloModel.DoesNotExist:
        return HertzResponse.not_found(message="模型不存在")
    except Exception as e:
        return HertzResponse.error(message="启用模型失败", error=str(e))


@api_view(['GET'])
def model_enabled(request):
    """获取当前启用的模型"""
    try:
        enabled_model = YoloModel.get_enabled_model()
        if enabled_model:
            return HertzResponse.success(
                data=YoloModelSerializer(enabled_model).data,
                message="获取启用模型成功"
            )
        else:
            return HertzResponse.not_found(message="没有启用的模型")
    except Exception as e:
        return HertzResponse.error(message="获取启用模型失败", error=str(e))


# 检测记录管理接口

@api_view(['GET'])
def detection_list(request):
    """获取检测记录列表"""
    try:
        queryset = DetectionRecord.objects.all()
        
        # 按检测类型过滤
        detection_type = request.GET.get('type', None)
        if detection_type:
            queryset = queryset.filter(detection_type=detection_type)
        
        # 按模型过滤
        model_id = request.GET.get('model_id', None)
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        
        # 按用户过滤
        user_id = request.GET.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        serializer = DetectionRecordSerializer(queryset, many=True)
        return HertzResponse.success(data=serializer.data, message="获取检测记录列表成功")
    except Exception as e:
        return HertzResponse.error(message="获取检测记录列表失败", error=str(e))

@api_view(['GET'])
def user_detection_records(request, user_id):
    """获取指定用户的检测记录"""
    try:
        queryset = DetectionRecord.objects.filter(user_id=user_id)
        
        # 按检测类型过滤
        detection_type = request.GET.get('type', None)
        if detection_type:
            queryset = queryset.filter(detection_type=detection_type)
        
        # 按模型过滤
        model_id = request.GET.get('model_id', None)
        if model_id:
            queryset = queryset.filter(model_id=model_id)
        
        serializer = DetectionRecordSerializer(queryset, many=True)
        return HertzResponse.success(data=serializer.data, message="获取用户检测记录成功")
    except Exception as e:
        return HertzResponse.error(message="获取用户检测记录失败", error=str(e))


@api_view(['GET'])
def detection_detail(request, pk):
    """获取检测记录详情"""
    try:
        detection = DetectionRecord.objects.get(pk=pk)
        serializer = DetectionRecordSerializer(detection)
        return HertzResponse.success(data=serializer.data, message="获取检测记录详情成功")
    except DetectionRecord.DoesNotExist:
        return HertzResponse.not_found(message="检测记录不存在")
    except Exception as e:
        return HertzResponse.error(message="获取检测记录详情失败", error=str(e))


@api_view(['DELETE'])
def detection_delete(request, pk):
    """删除单个检测记录"""
    try:
        detection = DetectionRecord.objects.get(pk=pk)
        
        # 删除关联的文件
        if detection.original_file:
            original_file_path = os.path.join(settings.MEDIA_ROOT, detection.original_file.name)
            if os.path.exists(original_file_path):
                os.remove(original_file_path)
        
        if detection.result_file:
            result_file_path = os.path.join(settings.MEDIA_ROOT, detection.result_file.name)
            if os.path.exists(result_file_path):
                os.remove(result_file_path)
        
        # 如果存在关联的告警记录，标记为已删除
        try:
            alert = Alert.objects.get(detection_record=detection)
            alert.delete()  # 使用软删除方法
        except Alert.DoesNotExist:
            pass  # 没有关联的告警记录，不需要处理
        
        # 删除数据库记录
        detection.delete()
        
        return HertzResponse.success(message="检测记录删除成功")
    except DetectionRecord.DoesNotExist:
        return HertzResponse.not_found(message="检测记录不存在")
    except Exception as e:
        return HertzResponse.error(message="检测记录删除失败", error=str(e))


@api_view(['POST'])
@parser_classes([JSONParser])
def detection_batch_delete(request):
    """批量删除检测记录"""
    try:
        # 验证请求数据
        if not request.data or not isinstance(request.data.get('ids', []), list):
            return HertzResponse.validation_error(message="请提供有效的记录ID列表")
        
        record_ids = request.data.get('ids', [])
        if not record_ids:
            return HertzResponse.validation_error(message="记录ID列表不能为空")
        
        # 获取所有要删除的记录
        records = DetectionRecord.objects.filter(id__in=record_ids)
        found_ids = [str(record.id) for record in records]
        not_found_ids = [str(id) for id in record_ids if str(id) not in found_ids]
        
        # 删除关联的文件
        for record in records:
            # 删除关联的文件
            if record.original_file:
                original_file_path = os.path.join(settings.MEDIA_ROOT, record.original_file.name)
                if os.path.exists(original_file_path):
                    os.remove(original_file_path)
            
            # 删除结果文件
            if record.result_file:
                result_file_path = os.path.join(settings.MEDIA_ROOT, record.result_file.name)
                if os.path.exists(result_file_path):
                    os.remove(result_file_path)
            
            # 如果存在关联的告警记录，标记为已删除
            try:
                alert = Alert.objects.get(detection_record=record)
                alert.delete()  # 使用软删除方法
            except Alert.DoesNotExist:
                pass  # 没有关联的告警记录，不需要处理
        
        # 批量删除记录
        delete_count = records.count()
        records.delete()
        
        response_data = {
            "deleted_count": delete_count,
            "found_ids": found_ids,
            "not_found_ids": not_found_ids
        }
        
        return HertzResponse.success(
            data=response_data,
            message=f"成功删除 {delete_count} 条检测记录"
        )
    except Exception as e:
        return HertzResponse.error(message="批量删除检测记录失败", error=str(e))


# 告警记录管理接口

@api_view(['GET'])
def alert_list(request):
    """管理员获取所有告警记录列表"""
    try:
        # 默认只获取活跃状态的告警
        status_filter = request.GET.get('status', 'pending')
        queryset = Alert.objects.all()
        
        # 按状态过滤
        if status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # 按告警等级过滤
        alert_level = request.GET.get('level', None)
        if alert_level is not None:
            queryset = queryset.filter(alert_level=alert_level)
        
        # 按用户过滤
        user_id = request.GET.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 按告警类别过滤
        category = request.GET.get('alter_category', None)
        if category:
            queryset = queryset.filter(alert_category__icontains=category)
        
        serializer = AlertSerializer(queryset, many=True)
        return HertzResponse.success(data=serializer.data, message="获取告警记录列表成功")
    except Exception as e:
        return HertzResponse.error(message="获取告警记录列表失败", error=str(e))


@api_view(['GET'])
@login_required
def user_alert_records(request, user_id):
    """获取指定用户的告警记录"""
    try:
        # 验证当前用户是否有权限查看该用户的告警记录
        current_user = request.user
        if not current_user.is_staff and str(current_user.user_id) != str(user_id):
            return HertzResponse.forbidden(message="您没有权限查看其他用户的告警记录")
        
        # 默认只获取活跃状态的告警
        status_filter = request.GET.get('status', None)
        queryset = Alert.objects.filter(user_id=user_id)
        
        # 按状态过滤
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # 按告警等级过滤
        alert_level = request.GET.get('level', None)
        if alert_level is not None:
            queryset = queryset.filter(alert_level=alert_level)
        
        # 按告警类别过滤
        category = request.GET.get('category', None)
        if category:
            queryset = queryset.filter(alert_category__icontains=category)
        
        serializer = AlertSerializer(queryset, many=True)
        return HertzResponse.success(data=serializer.data, message="获取用户告警记录成功")
    except Exception as e:
        return HertzResponse.error(message="获取用户告警记录失败", error=str(e))



@api_view(['PUT', 'PATCH'])
@parser_classes([JSONParser])
def alert_update_status(request, pk):
    """更新告警记录状态"""
    try:
        alert = Alert.objects.get(pk=pk)
        serializer = AlertStatusUpdateSerializer(alert, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            alert = serializer.save()
            return HertzResponse.success(
                data=AlertSerializer(alert).data,
                message="更新告警状态成功"
            )
        return HertzResponse.validation_error(message="数据验证失败", errors=serializer.errors)
    except Alert.DoesNotExist:
        return HertzResponse.not_found(message="告警记录不存在")
    except Exception as e:
        return HertzResponse.error(message="更新告警状态失败", error=str(e))


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@login_required
def yolo_detection(request):
    """执行目标检测"""
    serializer = DetectionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(
            message='请求参数错误',
            errors=serializer.errors
        )

    try:
        # 获取参数
        uploaded_file = serializer.validated_data['file']
        model_id = serializer.validated_data.get('model_id')
        confidence_threshold = serializer.validated_data.get('confidence_threshold', 0.5)

        # 获取要使用的模型
        if model_id:
            yolo_model = YoloModel.objects.get(id=model_id)
        else:
            yolo_model = YoloModel.get_enabled_model()
            if not yolo_model:
                return HertzResponse.fail(
                    message='没有可用的模型，请先上传并启用一个模型'
                )

        # 确定检测类型
        file_name = uploaded_file.name.lower()
        is_video = any(file_name.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'])
        detection_type = 'video' if is_video else 'image'

        # 保存原始文件
        original_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        original_path = default_storage.save(f'detection/original/{original_filename}', uploaded_file)
        original_full_path = os.path.join(settings.MEDIA_ROOT, original_path)

        # 执行检测
        start_time = time.time()
        result_path, object_count, detected_categories, confidence_scores, avg_confidence = _perform_detection(
            original_full_path, yolo_model.model_path, confidence_threshold, detection_type, yolo_model
        )
        processing_time = time.time() - start_time

        # 保存检测结果文件
        result_filename = f"result_{uuid.uuid4()}_{os.path.splitext(uploaded_file.name)[0]}"
        if detection_type == 'image':
            result_filename += '.jpg'
        else:
            result_filename += '.mp4'
        
        # 使用os.path.join确保路径分隔符一致性
        result_relative_path = os.path.join('detection', 'result', result_filename)
        
        # 移动结果文件到正确位置
        final_result_path = os.path.join(settings.MEDIA_ROOT, result_relative_path)
        os.makedirs(os.path.dirname(final_result_path), exist_ok=True)
        
        # 确保临时文件存在
        if os.path.exists(result_path):
            shutil.copy2(result_path, final_result_path)
            os.remove(result_path)
        else:
            raise FileNotFoundError(f"临时视频文件不存在: {result_path}")

        # 获取当前用户信息
        user = request.user if request.user.is_authenticated else None
        user_name = user.username if user else None

        # 初始化告警等级，默认为none（未检测到目标时）
        alert_level = 'none'

        # 创建检测记录
        detection_record = DetectionRecord.objects.create(
            original_file=original_path,
            result_file=result_relative_path,
            detection_type=detection_type,
            model_name=f"{yolo_model.name} {yolo_model.version}",
            model=yolo_model,
            user=user,
            user_name=user_name,
            object_count=object_count,
            detected_categories=detected_categories,
            confidence_threshold=confidence_threshold,
            confidence_scores=confidence_scores,
            avg_confidence=avg_confidence,
            processing_time=processing_time
        )
        
        # 如果检测到目标，创建告警记录并设置告警等级
        if object_count > 0 and detected_categories:
            # 获取告警类别
            alert_category = detected_categories[0] if detected_categories else "未知类别"
            
            # 设置默认告警等级
            alert_level = 'medium'  # 默认中等级别
            model_category = None
            
            # 尝试从ModelCategory中获取告警等级
            try:
                # alert_category 就是别名，直接根据别名查找ModelCategory
                model_category = ModelCategory.objects.filter(
                    model=yolo_model,
                    alias=alert_category,
                    is_active=True
                ).first()
                
                # 如果根据别名没找到，尝试根据类别名称查找
                if not model_category:
                    model_category = ModelCategory.objects.filter(
                        model=yolo_model,
                        name=alert_category,
                        is_active=True
                    ).first()
                
                # 如果找到了对应的ModelCategory，使用其alert_level
                if model_category:
                    alert_level = model_category.alert_level
                else:
                    # 如果没有找到对应的ModelCategory，记录日志并使用默认等级
                    print(f"未找到类别 '{alert_category}' 对应的ModelCategory记录，使用默认告警等级")
                    
            except Exception as e:
                # 如果查找过程中出现异常，使用默认等级
                print(f"获取告警等级失败: {str(e)}")
                alert_level = 'medium'
            
            # 创建告警记录
            Alert.objects.create(
                detection_record=detection_record,
                user=user,
                user_name=user_name,
                alert_level=alert_level,
                alert_category=alert_category,
                category=model_category,  # 关联ModelCategory
                status='pending'
            )
        # 如果没有检测到目标，alert_level保持为'none'，不创建告警记录

        return HertzResponse.success(
            data={
                'detection_id': detection_record.id,
                'result_file_url': detection_record.result_file.url,
                'original_file_url': detection_record.original_file.url,
                'object_count': object_count,
                'detected_categories': detected_categories,
                'confidence_scores': confidence_scores,
                'avg_confidence': round(avg_confidence, 4) if avg_confidence is not None else None,
                'processing_time': round(processing_time, 2),
                'model_used': f"{yolo_model.name} {yolo_model.version}",
                'confidence_threshold': confidence_threshold,
                'user_id': user.user_id if user else None,
                'user_name': user_name,
                'alert_level': alert_level,
            },
            message="检测完成"
        )

    except YoloModel.DoesNotExist:
        return HertzResponse.not_found(message="指定的模型不存在")
    except Exception as e:
        return HertzResponse.error(message="检测失败", error=str(e))

def _perform_detection(input_path, model_path, confidence_threshold, detection_type, yolo_model=None):
    """执行YOLO检测"""
    try:
        # 加载YOLO模型
        model = YOLO(model_path)
        
        if detection_type == 'image':
            return _detect_image(model, input_path, confidence_threshold, yolo_model)
        else:
            return _detect_video(model, input_path, confidence_threshold, yolo_model)
            
    except Exception as e:
        raise Exception(f"YOLO检测失败: {str(e)}")


def _detect_image(model, image_path, confidence_threshold, yolo_model=None):
    """检测图片"""
    # 执行检测
    results = model(image_path, conf=confidence_threshold)
    
    # 获取检测结果
    result = results[0]
    
    # 统计检测到的对象
    object_count = len(result.boxes) if result.boxes is not None else 0
    detected_categories = []
    detected_aliases = []  # 存储别名
    confidence_scores = []
    avg_confidence = None
    
    if result.boxes is not None and len(result.boxes) > 0:
        # 获取类别名称
        class_names = model.names
        detected_class_ids = result.boxes.cls.cpu().numpy().astype(int)
        detected_categories = [class_names[class_id] for class_id in detected_class_ids]
        detected_categories = list(set(detected_categories))  # 去重
        
        # 获取别名
        if yolo_model:
            detected_aliases = _get_category_aliases(detected_categories, yolo_model)
        else:
            detected_aliases = detected_categories  # 如果没有模型信息，使用原始类别名
        
        # 获取置信度分数
        confidence_scores = result.boxes.conf.cpu().numpy().tolist()
        avg_confidence = float(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else None

    # 读取原始图片
    image = cv2.imread(image_path)
    
    # 使用自定义绘制函数绘制带别名的检测框
    if yolo_model:
        annotated_image = _draw_boxes_with_aliases(image, result, model.names, yolo_model)
    else:
        annotated_image = result.plot()  # 如果没有模型信息，使用默认绘制
    
    # 生成临时结果文件路径（稍后会移动到正确位置）
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'detection', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # 生成唯一的临时文件名
    temp_filename = f"temp_{uuid.uuid4()}.jpg"
    result_path = os.path.join(temp_dir, temp_filename)
    
    # 保存结果图片
    cv2.imwrite(result_path, annotated_image)
    
    return result_path, object_count, detected_aliases, confidence_scores, avg_confidence


def _detect_video(model, video_path, confidence_threshold, yolo_model=None):
    """检测视频"""
    # 打开视频
    cap = cv2.VideoCapture(video_path)

    # 获取视频属性
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 生成临时结果文件路径（稍后会移动到正确位置）
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'detection', 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    # 生成唯一的临时文件名
    temp_filename = f"temp_{uuid.uuid4()}.mp4"
    result_path = os.path.join(temp_dir, temp_filename)

    # 创建视频写入器 - 使用更兼容的编码方式
    # 尝试多种编码器，避免OpenH264依赖问题
    fourcc_options = [
        cv2.VideoWriter.fourcc(*'mp4v'),    # MPEG-4编码，兼容性好
        cv2.VideoWriter.fourcc(*'XVID'),    # Xvid编码
        cv2.VideoWriter.fourcc(*'MJPG'),    # Motion JPEG编码
        cv2.VideoWriter.fourcc(*'X264'),    # x264编码
    ]
    
    out = None
    for fourcc in fourcc_options:
        out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))
        if out.isOpened():
            print(f"使用编码器: {fourcc}")
            break
        else:
            out.release()
    
    if not out or not out.isOpened():
        raise Exception("无法创建视频写入器，所有编码器都失败")

    total_objects = 0
    all_detected_categories = set()
    all_detected_aliases = set()  # 存储别名
    all_confidence_scores = []
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 执行检测
            results = model(frame, conf=confidence_threshold)
            result = results[0]
            
            # 统计当前帧的检测结果
            if result.boxes is not None and len(result.boxes) > 0:
                frame_object_count = len(result.boxes)
                total_objects = max(total_objects, frame_object_count)  # 取最大值
                
                # 获取类别
                class_names = model.names
                detected_class_ids = result.boxes.cls.cpu().numpy().astype(int)
                frame_categories = [class_names[class_id] for class_id in detected_class_ids]
                all_detected_categories.update(frame_categories)
                
                # 获取别名
                if yolo_model:
                    frame_aliases = _get_category_aliases(frame_categories, yolo_model)
                    all_detected_aliases.update(frame_aliases)
                else:
                    all_detected_aliases.update(frame_categories)
                
                # 获取置信度分数
                frame_confidence_scores = result.boxes.conf.cpu().numpy().tolist()
                all_confidence_scores.extend(frame_confidence_scores)
            
            # 使用自定义绘制函数绘制带别名的检测框
            if yolo_model:
                annotated_frame = _draw_boxes_with_aliases(frame, result, model.names, yolo_model)
            else:
                annotated_frame = result.plot()  # 如果没有模型信息，使用默认绘制
            
            # 写入视频
            out.write(annotated_frame)
            
    finally:
        cap.release()
        out.release()
    
    # FFmpeg转码步骤 - 确保浏览器兼容性（可选）
    final_filename = f"final_{uuid.uuid4()}.mp4"
    final_path = os.path.join(temp_dir, final_filename)

    try:
        # 尝试多个可能的ffmpeg路径
        ffmpeg_paths = [
            'ffmpeg',  # 系统PATH中的ffmpeg
            'D:\\Devlop\\ffmpeg-7.1.1-essentials_build\\bin\\ffmpeg.exe',  # 用户指定路径
            'C:\\ffmpeg\\bin\\ffmpeg.exe',  # 常见安装路径1
            'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',  # 常见安装路径2
            'D:\\ffmpeg\\bin\\ffmpeg.exe',  # 常见安装路径3
        ]

        ffmpeg_found = False
        for ffmpeg_path in ffmpeg_paths:
            try:
                # 测试ffmpeg是否可用
                subprocess.run([ffmpeg_path, '-version'],
                               capture_output=True, check=True, timeout=5)
                ffmpeg_found = True
                break
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue

        if ffmpeg_found:
            # 使用subprocess直接调用FFmpeg进行转码
            cmd = [
                ffmpeg_path,
                '-i', result_path,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', 'faststart',
                '-profile:v', 'baseline',
                '-level', '3.0',
                '-r', '30',
                '-c:a', 'aac',
                '-y',  # 覆盖输出文件
                final_path
            ]
            
            # 执行命令
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 删除原始临时文件
            if os.path.exists(result_path):
                os.remove(result_path)
                
            # 使用转码后的文件作为最终结果
            result_path = final_path
            print(f"FFmpeg转码成功: {result_path}")
        else:
            print("FFmpeg未找到，使用OpenCV生成的原始视频文件")

    except Exception as e:
        # 如果FFmpeg转码失败，使用原始文件
        print(f"FFmpeg转码失败: {e}")
        if os.path.exists(final_path):
            os.remove(final_path)
        print("使用OpenCV生成的原始视频文件")

    detected_aliases = list(all_detected_aliases)
    
    # 计算平均置信度
    avg_confidence = sum(all_confidence_scores) / len(all_confidence_scores) if all_confidence_scores else None

    return result_path, total_objects, detected_aliases, all_confidence_scores, avg_confidence


@api_view(['GET'])
def detection_stats(request):
    """获取检测统计信息"""
    try:
        total_detections = DetectionRecord.objects.count()
        image_detections = DetectionRecord.objects.filter(detection_type='image').count()
        video_detections = DetectionRecord.objects.filter(detection_type='video').count()
        
        # 最近7天的检测数量
        from django.utils import timezone
        from datetime import timedelta
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_detections = DetectionRecord.objects.filter(created_at__gte=seven_days_ago).count()
        
        # 最常用的模型
        from django.db.models import Count
        popular_models = DetectionRecord.objects.values('model_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return HertzResponse.success(
            data={
                'total_detections': total_detections,
                'image_detections': image_detections,
                'video_detections': video_detections,
                'recent_detections': recent_detections,
                'popular_models': list(popular_models)
            },
            message="获取统计信息成功"
        )
    except Exception as e:
        return HertzResponse.error(message="获取统计信息失败", error=str(e))




@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_pt_convert_onnx(request):
    """
    上传 .pt 文件，转换为 ONNX 并保存到 media/yolo/ONNX 下，返回保存路径与下载链接。

    请求：multipart/form-data
    - file: .pt 模型文件
    - imgsz: 可选，导出图像尺寸（单值或"640,640"），默认 640
    - opset: 可选，ONNX opset 版本，默认 12
    - simplify: 可选，是否简化 ONNX，默认 False

    响应：
    {
      "onnx_relative_path": "yolo/ONNX/<file>.onnx",
      "download_url": "http://host/media/yolo/ONNX/<file>.onnx"
    }
    """
    try:
        uploaded = request.FILES.get('file')
        if not uploaded:
            return HertzResponse.validation_error(message='请上传 .pt 文件，字段名为 file')

        filename = uploaded.name
        if not filename.lower().endswith('.pt'):
            return HertzResponse.validation_error(message='文件格式错误，仅支持 .pt')

        # 保存到临时位置
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'yolo', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_filename = f"{uuid.uuid4()}_{filename}"
        temp_pt_path = os.path.join(temp_dir, temp_filename)

        with open(temp_pt_path, 'wb') as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        # 解析导出参数
        imgsz_param = request.data.get('imgsz', 640)
        if isinstance(imgsz_param, str) and ',' in imgsz_param:
            try:
                w, h = imgsz_param.split(',')
                imgsz = (int(w.strip()), int(h.strip()))
            except Exception:
                imgsz = 640
        else:
            try:
                imgsz = int(imgsz_param)
            except Exception:
                imgsz = 640

        try:
            opset = int(request.data.get('opset', 12))
        except Exception:
            opset = 12

        simplify = str(request.data.get('simplify', 'false')).lower() in ['1', 'true', 'yes']

        # 加载并导出为 ONNX（需要安装 ultralytics 及 onnx 相关依赖）
        model = YOLO(temp_pt_path)
        onnx_path = model.export(format='onnx', imgsz=imgsz, opset=opset, simplify=simplify, dynamic=True, nms=True)
        # ultralytics 返回导出文件的路径；如相对路径则转换为绝对路径
        if not os.path.isabs(onnx_path):
            onnx_path = os.path.join(os.getcwd(), onnx_path)

        # 移动到目标目录 media/yolo/ONNX
        target_dir = os.path.join(settings.MEDIA_ROOT, 'yolo', 'ONNX')
        os.makedirs(target_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(filename))[0]
        target_name = f"{base_name}_{uuid.uuid4().hex}.onnx"
        final_path = os.path.join(target_dir, target_name)
        shutil.copy2(onnx_path, final_path)

        # 保存类别名称到同目录，供前端/推理端正确映射，避免默认COCO标签造成误判
        try:
            names_obj = getattr(model, 'names', None)
            if isinstance(names_obj, dict):
                names_list = [names_obj[i] for i in range(len(names_obj))]
            elif isinstance(names_obj, (list, tuple)):
                names_list = list(names_obj)
            else:
                names_list = []

            labels_name = f"{base_name}_{uuid.uuid4().hex}.labels.json"
            labels_path = os.path.join(target_dir, labels_name)
            with open(labels_path, 'w', encoding='utf-8') as lf:
                json.dump({
                    'names': names_list,
                    'nc': len(names_list)
                }, lf, ensure_ascii=False)

            # 尝试把labels写入ONNX metadata，若onnx库不可用则忽略
            try:
                import onnx
                m = onnx.load(final_path)
                # metadata_props是List[StringStringEntryProto]
                entry = onnx.onnx_ml_pb2.StringStringEntryProto()
                entry.key = 'names'
                entry.value = json.dumps(names_list, ensure_ascii=False)
                # 清理已有同名项
                m.metadata_props[:] = [p for p in m.metadata_props if p.key != 'names']
                m.metadata_props.append(entry)
                onnx.save(m, final_path)
            except Exception:
                pass
        except Exception:
            labels_path = None

        # 生成返回值
        relative_path = os.path.join('yolo', 'ONNX', target_name)
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        download_url = request.build_absolute_uri(os.path.join(media_url, relative_path).replace('\\', '/'))

        labels_relative_path = None
        labels_download_url = None
        if labels_path and os.path.exists(labels_path):
            labels_relative_path = os.path.join('yolo', 'ONNX', os.path.basename(labels_path))
            labels_download_url = request.build_absolute_uri(os.path.join(media_url, labels_relative_path).replace('\\', '/'))

        # 清理临时文件
        try:
            os.remove(temp_pt_path)
        except Exception:
            pass
        try:
            os.remove(onnx_path)
        except Exception:
            pass

        return HertzResponse.success(
            data={
                'onnx_relative_path': relative_path.replace('\\', '/'),
                'download_url': download_url,
                'labels_relative_path': (labels_relative_path or '').replace('\\', '/'),
                'labels_download_url': labels_download_url
            },
            message='ONNX 导出成功'
        )
    except Exception as e:
        return HertzResponse.error(message='ONNX 导出失败', error=str(e))

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def model_upload(request):
    """
    模型上传接口 - 支持压缩包和文件夹上传
    
    参数:
    - zip_file: 压缩包文件 (与folder_files互斥)
    - folder_files: 文件夹中的多个文件 (与zip_file互斥)
    - name: 模型名称
    - version: 模型版本 (可选，默认1.0)
    - description: 模型描述 (可选)
    """
    try:
        # 验证必需参数
        if 'name' not in request.data:
            return HertzResponse.fail(message='请提供模型名称')

        model_name = request.data['name']
        model_version = request.data.get('version', '1.0')
        description = request.data.get('description', '')

        # 检测上传类型：压缩包或文件夹
        is_zip_upload = 'zip_file' in request.FILES
        is_folder_upload = len([key for key in request.FILES.keys() if key.startswith('folder_files')]) > 0

        if not is_zip_upload and not is_folder_upload:
            return HertzResponse.fail(message='请上传压缩包文件或文件夹')

        if is_zip_upload and is_folder_upload:
            return HertzResponse.fail(message='请选择压缩包上传或文件夹上传，不能同时使用')

        # 创建 media/models 目录
        models_dir = os.path.join(settings.MEDIA_ROOT, 'models')
        os.makedirs(models_dir, exist_ok=True)

        # 生成唯一的文件夹名称
        folder_name = f"{model_name}_{uuid.uuid4().hex[:8]}"
        extract_path = os.path.join(models_dir, folder_name)

        if is_zip_upload:
            # 处理压缩包上传
            zip_file = request.FILES['zip_file']
            
            # 验证文件类型
            if not zip_file.name.lower().endswith('.zip'):
                return HertzResponse.fail(message='只支持 ZIP 格式的压缩包')
            
            return _handle_zip_upload(zip_file, extract_path, model_name, model_version, description)
        
        else:
            # 处理文件夹上传
            folder_files = [request.FILES[key] for key in request.FILES.keys() if key.startswith('folder_files')]
            return _handle_folder_upload(folder_files, extract_path, model_name, model_version, description)

    except Exception as e:
        # 清理可能创建的文件夹
        if 'extract_path' in locals() and os.path.exists(extract_path):
            shutil.rmtree(extract_path, ignore_errors=True)
        
        return HertzResponse.error(message="上传失败", error=str(e))


def _handle_zip_upload(zip_file, extract_path, model_name, model_version, description):
    """处理压缩包上传"""
    # 临时保存压缩包
    temp_zip_path = os.path.join(os.path.dirname(extract_path), f"temp_{uuid.uuid4().hex}.zip")
    
    try:
        # 保存上传的压缩包到临时位置
        with open(temp_zip_path, 'wb') as temp_file:
            for chunk in zip_file.chunks():
                temp_file.write(chunk)

        # 解压文件
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # 检查是否有多余顶层文件夹
        subdirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]
        if len(subdirs) == 1:
            top_subdir = os.path.join(extract_path, subdirs[0])
            if os.path.exists(os.path.join(top_subdir, 'weights')):
                # 将子目录内容移动到 extract_path 下
                for item in os.listdir(top_subdir):
                    shutil.move(os.path.join(top_subdir, item), extract_path)
                # 删除空的顶层文件夹
                os.rmdir(top_subdir)

        # 验证解压后的文件结构
        weights_dir = os.path.join(extract_path, 'weights')
        if not os.path.exists(weights_dir):
            # 如果没有 weights 目录，检查是否有 .pt 文件在根目录
            pt_files = [f for f in os.listdir(extract_path) if f.endswith('.pt')]
            if pt_files:
                # 创建 weights 目录并移动 .pt 文件
                os.makedirs(weights_dir, exist_ok=True)
                for pt_file in pt_files:
                    shutil.move(
                        os.path.join(extract_path, pt_file),
                        os.path.join(weights_dir, pt_file)
                    )

        return _validate_and_create_model(extract_path, zip_file, model_name, model_version, description)

    finally:
        # 删除临时压缩包文件
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)


def _handle_folder_upload(folder_files, extract_path, model_name, model_version, description):
    """处理文件夹上传"""
    try:
        # 创建目标目录
        os.makedirs(extract_path, exist_ok=True)
        
        # 处理上传的文件
        for file_key, uploaded_file in folder_files.items():
            # 获取文件的相对路径
            # 文件键格式通常是 'folder_files[path/to/file.ext]'
            if file_key.startswith('folder_files[') and file_key.endswith(']'):
                relative_path = file_key[13:-1]  # 去掉 'folder_files[' 和 ']'
            else:
                # 如果格式不符合预期，使用文件名
                relative_path = uploaded_file.name
            
            # 构建完整的文件路径
            file_path = os.path.join(extract_path, relative_path)
            
            # 确保目录存在
            file_dir = os.path.dirname(file_path)
            if file_dir:
                os.makedirs(file_dir, exist_ok=True)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        
        # 验证文件夹结构
        weights_dir = os.path.join(extract_path, 'weights')
        if not os.path.exists(weights_dir):
            # 检查根目录是否有.pt文件
            pt_files = [f for f in os.listdir(extract_path) if f.endswith('.pt')]
            if pt_files:
                # 创建weights目录并移动.pt文件
                os.makedirs(weights_dir, exist_ok=True)
                for pt_file in pt_files:
                    shutil.move(
                        os.path.join(extract_path, pt_file),
                        os.path.join(weights_dir, pt_file)
                    )
        
        # 使用通用验证和创建函数
        return _validate_and_create_model(extract_path, None, model_name, model_version, description)
        
    except Exception as e:
        # 清理可能创建的文件夹
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path, ignore_errors=True)
        return HertzResponse.error(message="文件夹上传失败", error=str(e))


def _validate_and_create_model(extract_path, uploaded_file, model_name, model_version, description):
    """验证模型结构并创建模型记录"""
    try:
        # 检查权重文件路径
        weights_dir = os.path.join(extract_path, 'weights')
        if not os.path.exists(weights_dir) or not any(f.endswith('.pt') for f in os.listdir(weights_dir)):
            # 清理文件夹
            shutil.rmtree(extract_path, ignore_errors=True)
            return HertzResponse.fail(message='文件夹中未找到有效的 YOLO 权重文件 (.pt)')

        # 尝试读取类别信息
        categories = {}
        data_yaml_path = os.path.join(extract_path, 'data.yaml')
        if os.path.exists(data_yaml_path):
            try:
                import yaml
                with open(data_yaml_path, 'r', encoding='utf-8') as f:
                    data_config = yaml.safe_load(f)
                    if 'names' in data_config:
                        categories = data_config['names']
            except Exception:
                pass  # 如果读取失败，使用空的类别信息

        # 计算相对路径（相对于 MEDIA_ROOT）
        model_folder_relative = os.path.relpath(extract_path, settings.MEDIA_ROOT)
        
        best_pt_relative = None
        last_pt_relative = None
        
        if os.path.exists(weights_dir):
            best_pt_file = os.path.join(weights_dir, 'best.pt')
            last_pt_file = os.path.join(weights_dir, 'last.pt')
            
            if os.path.exists(best_pt_file):
                # 保存相对路径
                best_pt_relative = os.path.relpath(best_pt_file, settings.MEDIA_ROOT)
            if os.path.exists(last_pt_file):
                # 保存相对路径
                last_pt_relative = os.path.relpath(last_pt_file, settings.MEDIA_ROOT)

        # 创建模型记录（使用相对路径）
        yolo_model = YoloModel.objects.create(
            name=model_name,
            version=model_version,
            model_file=uploaded_file,  # 对于文件夹上传，这里可能是None
            model_folder_path=model_folder_relative,  # 相对路径
            best_model_path=best_pt_relative,  # 相对路径
            last_model_path=last_pt_relative,  # 相对路径
            categories=categories,
            description=description
        )

        # 自动创建模型类别记录
        if categories:
            try:
                # 处理不同格式的categories
                if isinstance(categories, dict):
                    # 字典格式: {0: 'person', 1: 'bicycle', ...}
                    for category_id, category_name in categories.items():
                        try:
                            # 确保category_id是整数
                            if isinstance(category_id, str) and category_id.isdigit():
                                category_id = int(category_id)
                            elif not isinstance(category_id, int):
                                continue  # 跳过无效的category_id
                            
                            ModelCategory.objects.create(
                                model=yolo_model,
                                name=category_name,
                                category_id=category_id,
                                description=f"从模型 {model_name} 自动导入的类别",
                                alert_level='medium',  # 默认中等告警级别
                                is_active=True
                            )
                        except Exception as e:
                            # 记录错误但不影响整体流程
                            print(f"创建类别 {category_name} 失败: {str(e)}")
                            continue
                elif isinstance(categories, list):
                    # 列表格式: ['person', 'bicycle', ...]
                    for category_id, category_name in enumerate(categories):
                        try:
                            ModelCategory.objects.create(
                                model=yolo_model,
                                name=category_name,
                                category_id=category_id,
                                description=f"从模型 {model_name} 自动导入的类别",
                                alert_level='medium',  # 默认中等告警级别
                                is_active=True
                            )
                        except Exception as e:
                            # 记录错误但不影响整体流程
                            print(f"创建类别 {category_name} 失败: {str(e)}")
                            continue
            except Exception as e:
                # 记录错误但不影响整体流程
                print(f"处理类别信息失败: {str(e)}")
                pass

        return HertzResponse.success(
            data={
                'id': yolo_model.id,
                'name': yolo_model.name,
                'version': yolo_model.version,
                'folder_path': yolo_model.model_folder_path,  # 返回相对路径
                'weights_path': yolo_model.weights_folder_path,  # 返回绝对路径(用于显示)
                'model_path': yolo_model.model_path,  # 返回绝对路径(用于加载模型)
                'best_model_path': yolo_model.best_model_path,  # 返回相对路径
                'last_model_path': yolo_model.last_model_path,  # 返回相对路径
                'categories': yolo_model.categories,
                'created_at': yolo_model.created_at
            },
            message="模型上传成功"
        )

    except Exception as e:
        # 清理可能创建的文件夹
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path, ignore_errors=True)
        raise e


# 模型类别管理接口

@api_view(['GET'])
def category_list(request):
    """获取模型类别列表"""
    try:
        categories = ModelCategory.objects.all()
        serializer = ModelCategoryListSerializer(categories, many=True)
        return HertzResponse.success(data=serializer.data, message="获取类别列表成功")
    except Exception as e:
        return HertzResponse.error(message="获取类别列表失败", error=str(e))


@api_view(['POST'])
@parser_classes([JSONParser])
def category_create(request):
    """创建模型类别"""
    try:
        serializer = ModelCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return HertzResponse.success(
                data=ModelCategorySerializer(category).data,
                message="创建类别成功"
            )
        return HertzResponse.validation_error(message="数据验证失败", errors=serializer.errors)
    except Exception as e:
        return HertzResponse.error(message="创建类别失败", error=str(e))


@api_view(['GET'])
def category_detail(request, pk):
    """获取模型类别详情"""
    try:
        category = ModelCategory.objects.get(pk=pk)
        serializer = ModelCategorySerializer(category)
        return HertzResponse.success(data=serializer.data, message="获取类别详情成功")
    except ModelCategory.DoesNotExist:
        return HertzResponse.not_found(message="类别不存在")
    except Exception as e:
        return HertzResponse.error(message="获取类别详情失败", error=str(e))


@api_view(['PUT', 'PATCH'])
@parser_classes([JSONParser])
def category_update(request, pk):
    """更新模型类别"""
    try:
        category = ModelCategory.objects.get(pk=pk)
        serializer = ModelCategorySerializer(category, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            category = serializer.save()
            return HertzResponse.success(
                data=ModelCategorySerializer(category).data,
                message="更新类别成功"
            )
        return HertzResponse.validation_error(message="数据验证失败", errors=serializer.errors)
    except ModelCategory.DoesNotExist:
        return HertzResponse.not_found(message="类别不存在")
    except Exception as e:
        return HertzResponse.error(message="更新类别失败", error=str(e))


@api_view(['DELETE'])
def category_delete(request, pk):
    """删除模型类别"""
    try:
        category = ModelCategory.objects.get(pk=pk)
        
        # 检查是否有关联的告警记录
        alert_count = Alert.objects.filter(category=category).count()
        if alert_count > 0:
            return HertzResponse.fail(
                message=f"无法删除类别，存在 {alert_count} 条关联的告警记录",
                code=400
            )
        
        category_name = category.name
        category.delete()
        return HertzResponse.success(message=f"删除类别 '{category_name}' 成功")
    except ModelCategory.DoesNotExist:
        return HertzResponse.fail(message="类别不存在", code=404)
    except Exception as e:
        return HertzResponse.error(message="删除类别失败", error=str(e))


@api_view(['POST'])
@parser_classes([JSONParser])
def category_toggle_status(request, pk):
    """切换类别启用状态"""
    try:
        category = ModelCategory.objects.get(pk=pk)
        category.is_active = not category.is_active
        category.save()
        
        status_text = "启用" if category.is_active else "禁用"
        return HertzResponse.success(
            data={'is_active': category.is_active},
            message=f"类别 '{category.name}' {status_text}成功"
        )
    except ModelCategory.DoesNotExist:
        return HertzResponse.fail(message="类别不存在", code=404)
    except Exception as e:
        return HertzResponse.error(message="切换类别状态失败", error=str(e))


@api_view(['GET'])
def category_active_list(request):
    """获取启用的模型类别列表"""
    try:
        categories = ModelCategory.objects.filter(is_active=True)
        serializer = ModelCategoryListSerializer(categories, many=True)
        return HertzResponse.success(data=serializer.data, message="获取启用类别列表成功")
    except Exception as e:
        return HertzResponse.error(message="获取启用类别列表失败", error=str(e))


# 数据集管理接口

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def dataset_upload(request):
    serializer = DatasetUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return HertzResponse.validation_error(message='请求参数错误', errors=serializer.errors)

    try:
        name = serializer.validated_data['name']
        version = serializer.validated_data.get('version', '1.0')
        description = serializer.validated_data.get('description', '')
        zip_file = serializer.validated_data['zip_file']

        base_dir = os.path.join(settings.MEDIA_ROOT, 'yolo_dataset')
        os.makedirs(base_dir, exist_ok=True)
        folder_name = f"{name}_{uuid.uuid4().hex[:8]}"
        extract_path = os.path.join(base_dir, folder_name)

        temp_zip_path = os.path.join(base_dir, f"temp_{uuid.uuid4().hex}.zip")
        with open(temp_zip_path, 'wb') as f:
            for chunk in zip_file.chunks():
                f.write(chunk)

        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            subdirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]
            if len(subdirs) == 1 and not os.path.exists(os.path.join(extract_path, 'train')):
                top_subdir = os.path.join(extract_path, subdirs[0])
                for item in os.listdir(top_subdir):
                    shutil.move(os.path.join(top_subdir, item), extract_path)
                try:
                    os.rmdir(top_subdir)
                except Exception:
                    pass

            train_images = os.path.join(extract_path, 'train', 'images')
            train_labels = os.path.join(extract_path, 'train', 'labels')
            # 支持 val 或 valid 作为验证集目录
            val_root = os.path.join(extract_path, 'val')
            if not os.path.isdir(val_root):
                val_root = os.path.join(extract_path, 'valid')
            val_images = os.path.join(val_root, 'images')
            val_labels = os.path.join(val_root, 'labels')
            test_images = os.path.join(extract_path, 'test', 'images')
            test_labels = os.path.join(extract_path, 'test', 'labels')

            # 最低要求：必须存在训练集 images 与 labels
            if not (os.path.isdir(train_images) and os.path.isdir(train_labels)):
                shutil.rmtree(extract_path, ignore_errors=True)
                return HertzResponse.fail(message='数据集结构不符合要求')

            def _count_files(path, exts):
                if not os.path.isdir(path):
                    return 0
                files = [f for f in os.listdir(path) if any(f.lower().endswith(e) for e in exts)]
                return len(files)

            train_images_count = _count_files(train_images, ['.jpg', '.jpeg', '.png', '.bmp', '.webp'])
            train_labels_count = _count_files(train_labels, ['.txt'])
            val_images_count = _count_files(val_images, ['.jpg', '.jpeg', '.png', '.bmp', '.webp'])
            val_labels_count = _count_files(val_labels, ['.txt'])
            test_images_count = _count_files(test_images, ['.jpg', '.jpeg', '.png', '.bmp', '.webp'])
            test_labels_count = _count_files(test_labels, ['.txt'])

            data_yaml_path = None
            names = []
            nc = 0
            yaml_file = os.path.join(extract_path, 'data.yaml')
            if os.path.exists(yaml_file):
                data_yaml_path = yaml_file
                try:
                    import yaml
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data_cfg = yaml.safe_load(f)
                        nm = data_cfg.get('names')
                        if isinstance(nm, dict):
                            names = [nm[i] for i in sorted(nm.keys(), key=lambda x: int(x))]
                        elif isinstance(nm, (list, tuple)):
                            names = list(nm)
                        nc = int(data_cfg.get('nc', len(names)))
                except Exception:
                    pass

            # 仅存相对路径，避免不同服务器的绝对路径差异
            root_folder_rel = os.path.join('yolo_dataset', folder_name)
            data_yaml_rel = os.path.join(root_folder_rel, 'data.yaml') if data_yaml_path else None

            dataset = Dataset.objects.create(
                name=name,
                version=version,
                zip_file=zip_file,
                root_folder_path=root_folder_rel,
                data_yaml_path=data_yaml_rel,
                names=names,
                nc=nc,
                train_images_count=train_images_count,
                train_labels_count=train_labels_count,
                val_images_count=val_images_count,
                val_labels_count=val_labels_count,
                test_images_count=test_images_count,
                test_labels_count=test_labels_count,
                description=description
            )

            return HertzResponse.success(
                data=DatasetSerializer(dataset).data,
                message='数据集上传成功'
            )
        finally:
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
    except Exception as e:
        if 'extract_path' in locals() and os.path.exists(extract_path):
            shutil.rmtree(extract_path, ignore_errors=True)
        return HertzResponse.error(message='数据集上传失败', error=str(e))


@api_view(['GET'])
def dataset_list(request):
    try:
        datasets = Dataset.objects.all().order_by('-created_at')
        serializer = DatasetListSerializer(datasets, many=True)
        return HertzResponse.success(data=serializer.data, message='获取数据集列表成功')
    except Exception as e:
        return HertzResponse.error(message='获取数据集列表失败', error=str(e))


@api_view(['GET'])
def dataset_detail(request, pk):
    try:
        ds = Dataset.objects.get(pk=pk)
        serializer = DatasetSerializer(ds)
        return HertzResponse.success(data=serializer.data, message='获取数据集详情成功')
    except Dataset.DoesNotExist:
        return HertzResponse.not_found(message='数据集不存在')
    except Exception as e:
        return HertzResponse.error(message='获取数据集详情失败', error=str(e))


@api_view(['POST'])
def dataset_delete(request, pk):
    try:
        ds = Dataset.objects.get(pk=pk)
        root_rel = ds.root_folder_path or ''
        if root_rel:
            folder = os.path.join(settings.MEDIA_ROOT, root_rel)
            if os.path.isdir(folder):
                shutil.rmtree(folder, ignore_errors=True)

        # 删除可能存在的压缩包文件
        for field_name in ['zip_file', 'tar_file']:
            f = getattr(ds, field_name, None)
            if f:
                fpath = os.path.join(settings.MEDIA_ROOT, f.name)
                if os.path.exists(fpath):
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass

        ds.delete()
        return HertzResponse.success(message='数据集删除成功')
    except Dataset.DoesNotExist:
        return HertzResponse.not_found(message='数据集不存在')
    except Exception as e:
        return HertzResponse.error(message='删除数据集失败', error=str(e))

@api_view(['GET'])
def dataset_samples(request, pk):
    try:
        split = request.GET.get('split', 'train')
        limit = int(request.GET.get('limit', 2))
        offset = int(request.GET.get('offset', 0))

        if split not in ['train', 'val', 'test']:
            return HertzResponse.validation_error(message='split 参数必须为 train/val/test')

        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        datasets = []
        if pk and pk > 0:
            try:
                datasets = [Dataset.objects.get(pk=pk)]
            except Dataset.DoesNotExist:
                return HertzResponse.not_found(message='数据集不存在')
        else:
            datasets = list(Dataset.objects.all())

        exts = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
        all_items = []

        for ds in datasets:
            root_abs = os.path.join(settings.MEDIA_ROOT, ds.root_folder_path)
            relative_root = ds.root_folder_path if not os.path.isabs(ds.root_folder_path) else os.path.relpath(ds.root_folder_path, settings.MEDIA_ROOT)
            actual_split = split
            if split == 'val' and not os.path.isdir(os.path.join(root_abs, 'val')):
                if os.path.isdir(os.path.join(root_abs, 'valid')):
                    actual_split = 'valid'
            images_dir = os.path.join(root_abs, actual_split, 'images')
            labels_dir = os.path.join(root_abs, actual_split, 'labels')
            if not os.path.isdir(images_dir):
                continue
            for fname in os.listdir(images_dir):
                if not any(fname.lower().endswith(e) for e in exts):
                    continue
                img_rel = os.path.join(relative_root, actual_split, 'images', fname).replace('\\', '/')
                img_url = f"{media_url.rstrip('/')}" + "/" + quote(img_rel, safe='/')
                img_path = os.path.join(images_dir, fname)
                try:
                    image_size = os.path.getsize(img_path)
                except Exception:
                    image_size = None
                label_base = os.path.splitext(fname)[0] + '.txt'
                lbl_path = os.path.join(labels_dir, label_base)
                label_content = None
                if os.path.exists(lbl_path):
                    try:
                        with open(lbl_path, 'r', encoding='utf-8') as lf:
                            label_content = lf.read()
                    except Exception:
                        label_content = None
                all_items.append({
                    'image': img_url,
                    'image_size': image_size,
                    'label': label_content,
                    'filename': fname,
                })

        total = len(all_items)
        items = all_items[offset:offset+limit]
        return HertzResponse.success(data={'items': items, 'total': total}, message='获取数据样本成功')
    except Dataset.DoesNotExist:
        return HertzResponse.not_found(message='数据集不存在')
    except Exception as e:
        return HertzResponse.error(message='获取数据样本失败', error=str(e))