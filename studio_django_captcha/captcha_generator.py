import random
import string
import hashlib
import uuid
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from django.conf import settings
from django.core.cache import cache
import redis
import json
from datetime import datetime, timedelta


class HertzCaptchaGenerator:
    """Hertz验证码生成器"""
    
    def __init__(self):
        self.length = getattr(settings, 'HERTZ_CAPTCHA_LENGTH', 4)
        self.width = getattr(settings, 'HERTZ_CAPTCHA_WIDTH', 120)
        self.height = getattr(settings, 'HERTZ_CAPTCHA_HEIGHT', 50)
        self.font_size = getattr(settings, 'HERTZ_CAPTCHA_FONT_SIZE', 30)
        self.timeout = getattr(settings, 'HERTZ_CAPTCHA_TIMEOUT', 300)
        self.bg_color = getattr(settings, 'HERTZ_CAPTCHA_BACKGROUND_COLOR', '#ffffff')
        self.fg_color = getattr(settings, 'HERTZ_CAPTCHA_FOREGROUND_COLOR', '#000000')
        self.noise_level = getattr(settings, 'HERTZ_CAPTCHA_NOISE_LEVEL', 0.3)
        self.redis_prefix = getattr(settings, 'HERTZ_CAPTCHA_REDIS_KEY_PREFIX', 'hertz_captcha:')
        
        # 初始化Redis连接
        self.redis_client = self._get_redis_client()
    
    def _get_redis_client(self):
        """获取Redis客户端"""
        try:
            # 使用Django的缓存配置
            redis_config = settings.CACHES.get('default', {})
            if redis_config.get('BACKEND') == 'django_redis.cache.RedisCache':
                location = redis_config.get('LOCATION', 'redis://127.0.0.1:6379/1')
                # 解析Redis URL
                if location.startswith('redis://'):
                    parts = location.replace('redis://', '').split('/')
                    host_port = parts[0].split(':')
                    host = host_port[0] if host_port else '127.0.0.1'
                    port = int(host_port[1]) if len(host_port) > 1 else 6379
                    db = int(parts[1]) if len(parts) > 1 else 0
                    return redis.Redis(host=host, port=port, db=db, decode_responses=True)
            
            # 默认配置
            return redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)
        except Exception as e:
            print(f"Redis连接失败: {e}")
            return None
    
    def generate_code(self):
        """生成验证码字符串"""
        characters = string.ascii_uppercase + string.digits
        # 移除容易混淆的字符
        characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
        return ''.join(random.choice(characters) for _ in range(self.length))
    
    @staticmethod
    def generate_numeric_code(length=6):
        """生成纯数字验证码"""
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    def create_image(self, code):
        """创建验证码图片"""
        # 创建图片
        image = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            # Windows系统字体路径
            font_paths = [
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/calibri.ttf',
                'C:/Windows/Fonts/times.ttf'
            ]
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, self.font_size)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 绘制验证码文字
        char_width = self.width // self.length
        for i, char in enumerate(code):
            x = i * char_width + random.randint(5, 15)
            y = random.randint(5, 15)
            # 随机颜色
            color = (
                random.randint(0, 100),
                random.randint(0, 100),
                random.randint(0, 100)
            )
            draw.text((x, y), char, font=font, fill=color)
        
        # 添加噪声
        self._add_noise(draw)
        
        return image
    
    def _add_noise(self, draw):
        """添加噪声"""
        # 添加随机点
        for _ in range(int(self.width * self.height * self.noise_level)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            draw.point((x, y), fill=color)
        
        # 添加随机线条
        for _ in range(random.randint(3, 8)):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            color = (
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200)
            )
            draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
    
    def image_to_base64(self, image):
        """将图片转换为base64字符串"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def generate_captcha(self):
        """生成完整的验证码数据"""
        # 生成验证码
        code = self.generate_code()
        captcha_id = str(uuid.uuid4())
        
        # 创建图片
        image = self.create_image(code)
        image_data = self.image_to_base64(image)
        
        # 存储到Redis
        captcha_data = {
            'code': code,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(seconds=self.timeout)).isoformat()
        }
        
        if self.redis_client:
            try:
                redis_key = f"{self.redis_prefix}{captcha_id}"
                self.redis_client.setex(
                    redis_key,
                    self.timeout,
                    json.dumps(captcha_data)
                )
            except Exception as e:
                print(f"Redis存储失败: {e}")
                # 如果Redis失败，使用Django缓存作为备选
                cache.set(f"{self.redis_prefix}{captcha_id}", captcha_data, self.timeout)
        else:
            # 使用Django缓存作为备选
            cache.set(f"{self.redis_prefix}{captcha_id}", captcha_data, self.timeout)
        
        return {
            'captcha_id': captcha_id,
            'image_data': image_data,
            'expires_in': self.timeout
        }
    
    def verify_captcha(self, captcha_id, user_input):
        """验证验证码"""
        if not captcha_id or not user_input:
            return False
        
        redis_key = f"{self.redis_prefix}{captcha_id}"
        
        # 从Redis获取数据
        captcha_data = None
        if self.redis_client:
            try:
                data = self.redis_client.get(redis_key)
                if data:
                    captcha_data = json.loads(data)
            except Exception as e:
                print(f"Redis读取失败: {e}")
        
        # 如果Redis失败，尝试从Django缓存获取
        if not captcha_data:
            captcha_data = cache.get(redis_key)
        
        if not captcha_data:
            return False
        
        # 检查是否过期
        expires_at = datetime.fromisoformat(captcha_data['expires_at'])
        if datetime.now() > expires_at:
            self._delete_captcha(captcha_id)
            return False
        
        # 验证码比较（不区分大小写）
        is_valid = captcha_data['code'].upper() == user_input.upper()
        
        # 验证后删除验证码（无论成功失败）
        self._delete_captcha(captcha_id)
        
        return is_valid
    
    def _delete_captcha(self, captcha_id):
        """删除验证码数据"""
        redis_key = f"{self.redis_prefix}{captcha_id}"
        
        if self.redis_client:
            try:
                self.redis_client.delete(redis_key)
            except Exception as e:
                print(f"Redis删除失败: {e}")
        
        # 同时从Django缓存删除
        cache.delete(redis_key)
    
    def refresh_captcha(self, old_captcha_id):
        """刷新验证码"""
        # 删除旧验证码
        if old_captcha_id:
            self._delete_captcha(old_captcha_id)
        
        # 生成新验证码
        return self.generate_captcha()