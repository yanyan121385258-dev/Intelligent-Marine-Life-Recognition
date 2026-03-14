import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        message = text_data_json.get('message', '')
        username = text_data_json.get('username', 'Anonymous')

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': message_type,
                'message': message,
                'username': username,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))

    async def user_join(self, event):
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'user_notification',
            'message': f'{username} 加入了聊天室',
            'username': username,
            'timestamp': timestamp
        }))

    async def user_leave(self, event):
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'type': 'user_notification',
            'message': f'{username} 离开了聊天室',
            'username': username,
            'timestamp': timestamp
        }))


class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            # 解析接收到的JSON数据
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            
            if message:
                # 返回回声消息
                response = {
                    'type': 'echo_message',
                    'original_message': message,
                    'echo_message': f'回声: {message}',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            else:
                # 如果消息为空
                response = {
                    'type': 'error',
                    'message': '消息不能为空',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                
            await self.send(text_data=json.dumps(response, ensure_ascii=False))
            
        except json.JSONDecodeError:
            # JSON解析错误
            error_response = {
                'type': 'error',
                'message': '无效的JSON格式',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            await self.send(text_data=json.dumps(error_response, ensure_ascii=False))