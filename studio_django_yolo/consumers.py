import asyncio
import base64
import json
from datetime import datetime

import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

from django.conf import settings
from .models import YoloModel


class YoloLiveConsumer(AsyncWebsocketConsumer):
    """
    WebSocket实时检测消费者

    客户端协议（JSON）：
    - 开始检测：
      {
        "action": "start",
        "source": "webcam" | "rtsp" | "file",
        "device_index": 0,                 # webcam时使用，可选
        "rtsp_url": "rtsp://...",         # rtsp时使用，可选
        "file_path": "/path/to/video.mp4",# file时使用，可选
        "model_id": 123,                    # 使用指定模型，默认启用模型
        "confidence": 0.5,                  # 置信度阈值，默认0.5
        "send_frame": true,                 # 是否返回带框图像（base64）
      }

    - 停止检测：
      { "action": "stop" }

    支持前端推送帧的协议（无需后端取流）：
    - 开启推送模式：
      { "type": "start_detection", "model_id": 123?, "confidence": 0.5?, "send_frame": true? }
    - 推送单帧进行检测：
      { "type": "detect_frame", "image": "data:image/jpeg;base64,...", "confidence": 0.5?, "send_frame": true? }
    - 停止推送模式：
      { "type": "stop_detection" }

    服务器消息：
    - 检测结果：
      {
        "type": "detection",
        "timestamp": "HH:MM:SS",
        "object_count": int,
        "categories": [str,...],
        "confidence_scores": [float,...],
        "avg_confidence": float | null,
        "frame": "data:image/jpeg;base64,..."  # 可选
      }

    - 错误消息：
      {
        "type": "error",
        "message": str
      }
    """

    async def connect(self):
        self.running = False
        self.detect_task = None
        self._cap = None
        self._yolo_model = None  # 缓存已加载的模型（推送模式复用）
        self._push_mode = False  # 前端推送帧的模式
        self._default_confidence = 0.5
        self._default_send_frame = True
        await self.accept()

    async def disconnect(self, close_code):
        await self._stop_detection()

    async def receive(self, text_data: str):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "无效的JSON格式"
            }, ensure_ascii=False))
            return

        # 兼容两种协议：action（拉流）与 type（前端推送）
        action = data.get("action")
        msg_type = data.get("type")

        if action:
            if action == "start":
                await self._start_detection(data)
                return
            if action == "stop":
                await self._stop_detection()
                return
            if action == "ping":
                await self.send(text_data=json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().strftime('%H:%M:%S')
                }))
                return

        if msg_type:
            if msg_type == "start_detection":
                # 开启推送模式并加载模型
                await self._start_push_mode(data)
                return
            if msg_type == "detect_frame":
                await self._detect_frame_message(data)
                return
            if msg_type == "stop_detection":
                await self._stop_push_mode()
                return

        await self.send(text_data=json.dumps({
            "type": "error",
            "message": "未知的消息格式（需要action或type）"
        }, ensure_ascii=False))

    async def _start_detection(self, params: dict):
        if self.running:
            # 已在运行，忽略重复start
            return

        # 加载模型
        try:
            model_obj = None
            model_id = params.get("model_id")
            if model_id:
                model_obj = await database_sync_to_async(YoloModel.objects.get)(id=model_id)
            else:
                model_obj = await database_sync_to_async(YoloModel.get_enabled_model)()

            model_path = model_obj.model_path if model_obj else None
            if not model_path:
                # 兜底：项目根目录存在best.pt时使用
                fallback = getattr(settings, 'BASE_DIR', None)
                if fallback:
                    fallback_path = str(fallback / 'best.pt')
                    model_path = fallback_path

            if YOLO is None:
                raise RuntimeError("未安装ultralytics库，无法进行YOLO检测")

            # 在执行器中加载模型以避免阻塞事件循环
            loop = asyncio.get_running_loop()
            yolo_model = await loop.run_in_executor(None, lambda: YOLO(model_path))
        except YoloModel.DoesNotExist:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "指定的模型不存在"
            }, ensure_ascii=False))
            return
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"加载模型失败: {str(e)}"
            }, ensure_ascii=False))
            return

        # 打开视频源
        source = params.get("source", "webcam")
        confidence = float(params.get("confidence", 0.5))
        send_frame = bool(params.get("send_frame", True))

        try:
            if source == "webcam":
                device_index = int(params.get("device_index", 0))
                cap = cv2.VideoCapture(device_index)
            elif source == "rtsp":
                rtsp_url = params.get("rtsp_url")
                if not rtsp_url:
                    raise ValueError("缺少rtsp_url参数")
                cap = cv2.VideoCapture(rtsp_url)
            elif source == "file":
                file_path = params.get("file_path")
                if not file_path:
                    raise ValueError("缺少file_path参数")
                cap = cv2.VideoCapture(file_path)
            else:
                raise ValueError("不支持的source类型")

            if not cap or not cap.isOpened():
                raise RuntimeError("视频源打开失败")
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"打开视频源失败: {str(e)}"
            }, ensure_ascii=False))
            return

        # 运行检测任务
        self._cap = cap
        self.running = True
        loop = asyncio.get_running_loop()
        self.detect_task = loop.create_task(self._detect_loop(cap, yolo_model, confidence, send_frame))

    async def _ensure_model(self, model_id=None):
        """确保YOLO模型已加载，推送模式或单帧检测复用。"""
        if self._yolo_model is not None:
            return self._yolo_model

        # 加载模型（与_start_detection一致的策略）
        try:
            model_obj = None
            if model_id:
                model_obj = await database_sync_to_async(YoloModel.objects.get)(id=model_id)
            else:
                model_obj = await database_sync_to_async(YoloModel.get_enabled_model)()

            model_path = model_obj.model_path if model_obj else None
            if not model_path:
                fallback = getattr(settings, 'BASE_DIR', None)
                if fallback:
                    model_path = str(fallback / 'best.pt')

            if YOLO is None:
                raise RuntimeError("未安装ultralytics库，无法进行YOLO检测")

            loop = asyncio.get_running_loop()
            self._yolo_model = await loop.run_in_executor(None, lambda: YOLO(model_path))
            return self._yolo_model
        except YoloModel.DoesNotExist:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "指定的模型不存在"
            }, ensure_ascii=False))
            return None
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"加载模型失败: {str(e)}"
            }, ensure_ascii=False))
            return None

    async def _start_push_mode(self, params: dict):
        """开启推送模式，前端负责发送每帧图像。"""
        # 若已有流式检测在跑，拒绝开启推送模式
        if self.running:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "当前正在进行拉流检测，请先停止后再开启推送模式"
            }, ensure_ascii=False))
            return

        confidence = float(params.get("confidence", self._default_confidence))
        send_frame = bool(params.get("send_frame", self._default_send_frame))
        model_id = params.get("model_id")

        model = await self._ensure_model(model_id)
        if model is None:
            return

        self._push_mode = True
        self._default_confidence = confidence
        self._default_send_frame = send_frame
        await self.send(text_data=json.dumps({
            "type": "ready",
            "message": "推送模式已开启，可开始发送detect_frame",
            "confidence": confidence,
            "send_frame": send_frame
        }, ensure_ascii=False))

    async def _stop_push_mode(self):
        self._push_mode = False
        await self.send(text_data=json.dumps({
            "type": "stopped",
            "message": "推送模式已停止"
        }, ensure_ascii=False))

    async def _detect_frame_message(self, params: dict):
        """处理前端推送的单帧检测消息。"""
        if self.running:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "当前正在进行拉流检测，无法处理推送帧"
            }, ensure_ascii=False))
            return

        if not self._push_mode:
            # 允许无显式start_detection，首次detect_frame时自动加载模型
            confidence = float(params.get("confidence", self._default_confidence))
            send_frame = bool(params.get("send_frame", self._default_send_frame))
            model_id = params.get("model_id")
            model = await self._ensure_model(model_id)
            if model is None:
                return
            self._push_mode = True
        else:
            confidence = float(params.get("confidence", self._default_confidence))
            send_frame = bool(params.get("send_frame", self._default_send_frame))

        image_data = params.get("image")
        if not image_data or not isinstance(image_data, str):
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "缺少有效的image字段（需data:image/jpeg;base64,...）"
            }, ensure_ascii=False))
            return

        await self._detect_image_base64(image_data, confidence, send_frame)

    async def _stop_detection(self):
        if not self.running:
            return
        self.running = False
        try:
            if self.detect_task:
                # 等待任务退出
                await asyncio.wait_for(self.detect_task, timeout=5)
        except asyncio.TimeoutError:
            # 超时则取消任务
            if self.detect_task:
                self.detect_task.cancel()
        finally:
            self.detect_task = None
            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception:
                    pass
                self._cap = None

    async def _detect_loop(self, cap, yolo_model, confidence: float, send_frame: bool):
        loop = asyncio.get_running_loop()
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    # 读帧失败，短暂休眠后继续尝试
                    await asyncio.sleep(0.02)
                    continue

                # 将推理放入执行器，避免阻塞事件循环
                try:
                    results = await loop.run_in_executor(None, lambda: yolo_model(frame, conf=confidence))
                    result = results[0]
                except Exception as e:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": f"推理失败: {str(e)}"
                    }, ensure_ascii=False))
                    await asyncio.sleep(0.05)
                    continue

                # 汇总检测结果
                object_count = len(result.boxes) if getattr(result, 'boxes', None) is not None else 0
                categories = []
                confidence_scores = []
                avg_confidence = None

                try:
                    if result.boxes is not None and len(result.boxes) > 0:
                        class_names = yolo_model.names
                        detected_class_ids = result.boxes.cls.cpu().numpy().astype(int)
                        categories = list(set([class_names[class_id] for class_id in detected_class_ids]))
                        confidence_scores = result.boxes.conf.cpu().numpy().tolist()
                        avg_confidence = float(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else None
                except Exception:
                    # 兼容不同版本ultralytics的字段
                    pass

                payload = {
                    "type": "detection",
                    "timestamp": datetime.now().strftime('%H:%M:%S'),
                    "object_count": object_count,
                    "categories": categories,
                    "confidence_scores": confidence_scores,
                    "avg_confidence": avg_confidence,
                }

                if send_frame:
                    try:
                        # 使用内置plot得到带框图像
                        annotated = result.plot() if hasattr(result, 'plot') else frame
                        # 编码为JPEG并base64
                        success, buffer = cv2.imencode('.jpg', annotated)
                        if success:
                            b64 = base64.b64encode(buffer).decode('utf-8')
                            payload["frame"] = f"data:image/jpeg;base64,{b64}"
                    except Exception:
                        # 忽略绘制失败
                        pass

                await self.send(text_data=json.dumps(payload, ensure_ascii=False))

                # 适当降低发送频率，避免挤压客户端
                await asyncio.sleep(0.03)
        finally:
            try:
                cap.release()
            except Exception:
                pass

    async def _detect_image_base64(self, image_data: str, confidence: float, send_frame: bool):
        """对前端推送的base64图像进行单次检测并返回结果。"""
        try:
            # 去掉可能的data URL头
            if image_data.startswith("data:"):
                header, b64data = image_data.split(",", 1)
            else:
                b64data = image_data

            img_bytes = base64.b64decode(b64data)
            np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("图像解码失败")

            # 运行YOLO推理
            if self._yolo_model is None:
                model = await self._ensure_model(None)
                if model is None:
                    return
            else:
                model = self._yolo_model

            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, lambda: model(frame, conf=confidence))
            result = results[0]

            object_count = len(result.boxes) if getattr(result, 'boxes', None) is not None else 0
            categories = []
            confidence_scores = []
            avg_confidence = None

            try:
                if result.boxes is not None and len(result.boxes) > 0:
                    class_names = model.names
                    detected_class_ids = result.boxes.cls.cpu().numpy().astype(int)
                    categories = list(set([class_names[class_id] for class_id in detected_class_ids]))
                    confidence_scores = result.boxes.conf.cpu().numpy().tolist()
                    avg_confidence = float(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else None
            except Exception:
                pass

            payload = {
                "type": "detection",
                "timestamp": datetime.now().strftime('%H:%M:%S'),
                "object_count": object_count,
                "categories": categories,
                "confidence_scores": confidence_scores,
                "avg_confidence": avg_confidence,
            }

            if send_frame:
                try:
                    annotated = result.plot() if hasattr(result, 'plot') else frame
                    success, buffer = cv2.imencode('.jpg', annotated)
                    if success:
                        b64 = base64.b64encode(buffer).decode('utf-8')
                        payload["frame"] = f"data:image/jpeg;base64,{b64}"
                except Exception:
                    pass

            await self.send(text_data=json.dumps(payload, ensure_ascii=False))
        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"单帧检测失败: {str(e)}"
            }, ensure_ascii=False))