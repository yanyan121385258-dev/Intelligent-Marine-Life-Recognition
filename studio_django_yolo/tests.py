from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from .models import YoloModel, DetectionRecord


class YoloModelTestCase(TestCase):
    """YOLO模型测试"""
    
    def setUp(self):
        self.model_data = {
            'name': 'Test YOLO Model',
            'version': '1.0',
            'description': 'Test model for unit testing'
        }
    
    def test_model_creation(self):
        """测试模型创建"""
        model = YoloModel.objects.create(**self.model_data)
        self.assertEqual(model.name, 'Test YOLO Model')
        self.assertEqual(model.version, '1.0')
        self.assertFalse(model.is_enabled)
    
    def test_model_enable_disable(self):
        """测试模型启用/禁用"""
        model1 = YoloModel.objects.create(name='Model 1', version='1.0')
        model2 = YoloModel.objects.create(name='Model 2', version='1.0')
        
        # 启用第一个模型
        model1.is_enabled = True
        model1.save()
        
        # 启用第二个模型，应该自动禁用第一个
        model2.is_enabled = True
        model2.save()
        
        model1.refresh_from_db()
        self.assertFalse(model1.is_enabled)
        self.assertTrue(model2.is_enabled)


class DetectionRecordTestCase(TestCase):
    """检测记录测试"""
    
    def setUp(self):
        self.model = YoloModel.objects.create(
            name='Test Model',
            version='1.0',
            is_enabled=True
        )
    
    def test_detection_record_creation(self):
        """测试检测记录创建"""
        record = DetectionRecord.objects.create(
            detection_type='image',
            model_name='Test Model v1.0',
            model=self.model,
            object_count=5,
            detected_categories=['person', 'car'],
            confidence_threshold=0.5
        )
        
        self.assertEqual(record.detection_type, 'image')
        self.assertEqual(record.object_count, 5)
        self.assertEqual(len(record.detected_categories), 2)


class YoloAPITestCase(APITestCase):
    """YOLO API 测试"""
    
    def setUp(self):
        self.model = YoloModel.objects.create(
            name='Test Model',
            version='1.0',
            is_enabled=True
        )
    
    def test_model_list_api(self):
        """测试模型列表API"""
        response = self.client.get('/api/models/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_detection_records_api(self):
        """测试检测记录API"""
        response = self.client.get('/api/detections/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_detection_stats_api(self):
        """测试统计API"""
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_detections', response.data['data'])