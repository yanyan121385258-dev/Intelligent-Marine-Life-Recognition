import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import AIChat, AIChatMessage
from unittest.mock import patch
from studio_django_auth.utils.decorators.auth_decorators import no_login_required

User = get_user_model()


class AIChatAPITestCase(TestCase):
    """
    AI聊天API测试用例
    """
    
    def setUp(self):
        """
        测试前准备工作
        创建测试用户和测试数据
        """
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # 添加认证头
        self.client.credentials(HTTP_AUTHORIZATION='Bearer fake_test_token')
        
        # 创建测试聊天
        self.chat = AIChat.objects.create(
            user=self.user,
            title='测试聊天'
        )
        
        # 创建测试消息
        self.message = AIChatMessage.objects.create(
            chat=self.chat,
            role='user',
            content='测试消息'
        )
        
        # API路径
        self.list_url = reverse('studio_django_ai:chat_list')
        self.create_url = reverse('studio_django_ai:chat_create')
        self.detail_url = reverse('studio_django_ai:chat_detail', args=[self.chat.id])
        self.update_url = reverse('studio_django_ai:chat_update', args=[self.chat.id])
        self.delete_url = reverse('studio_django_ai:chat_delete')
        self.send_message_url = reverse('studio_django_ai:chat_send_message', args=[self.chat.id])
    
    def test_chat_list(self):
        """
        测试获取聊天列表
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['data']['total'], 1)
        self.assertEqual(len(data['data']['chats']), 1)
        self.assertEqual(data['data']['chats'][0]['title'], '测试聊天')
    
    def test_chat_create(self):
        """
        测试创建聊天
        """
        response = self.client.post(
            self.create_url,
            {'title': '新测试聊天'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], '创建成功')
        self.assertIn('chat_id', data['data'])
        self.assertEqual(data['data']['title'], '新测试聊天')
        
        # 验证数据库中是否创建成功
        self.assertTrue(AIChat.objects.filter(title='新测试聊天').exists())
    
    def test_chat_detail(self):
        """
        测试获取聊天详情
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], self.chat.id)
        self.assertEqual(data['data']['title'], '测试聊天')
        self.assertEqual(len(data['data']['messages']), 1)
        self.assertEqual(data['data']['messages'][0]['content'], '测试消息')
    
    def test_chat_update(self):
        """
        测试更新聊天
        """
        response = self.client.put(
            self.update_url,
            {'title': '更新后的标题'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], '更新成功')
        
        # 验证数据库中是否更新成功
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.title, '更新后的标题')
    
    def test_chat_delete(self):
        """
        测试删除聊天
        """
        response = self.client.post(
            self.delete_url,
            {'chat_ids': [self.chat.id]},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], '成功删除1个聊天')
        
        # 验证数据库中是否删除成功
        self.assertFalse(AIChat.objects.filter(id=self.chat.id).exists())
        self.assertFalse(AIChatMessage.objects.filter(chat_id=self.chat.id).exists())
    
    @patch('studio_django_utils.ollama.ollama_client.OllamaClient.chat_completion')
    def test_send_message(self, mock_chat_completion):
        """
        测试发送消息
        使用mock模拟AI回复
        """
        # 模拟AI回复
        mock_chat_completion.return_value = "这是AI的回复"
        
        response = self.client.post(
            self.send_message_url,
            {'content': '你好，AI'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['user_message']['content'], '你好，AI')
        self.assertEqual(data['data']['ai_message']['content'], '这是AI的回复')
        
        # 验证数据库中是否创建了新消息
        self.assertEqual(AIChatMessage.objects.filter(chat=self.chat).count(), 3)  # 原有1条 + 用户1条 + AI回复1条
    
    def test_unauthorized_access(self):
        """
        测试未授权访问
        """
        # 创建未认证的客户端
        client = APIClient()
        
        # 测试访问聊天列表
        response = client.get(self.list_url)
        self.assertEqual(response.status_code, 401)
        
        # 测试创建聊天
        response = client.post(self.create_url, {'title': '未授权聊天'}, format='json')
        self.assertEqual(response.status_code, 401)