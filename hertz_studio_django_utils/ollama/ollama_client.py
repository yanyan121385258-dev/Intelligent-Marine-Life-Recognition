import json
import asyncio
import aiohttp
import requests
from typing import List, Dict, Any, AsyncGenerator, Optional
from django.conf import settings


class OllamaClient:
    """
    Ollama API客户端
    用于与Ollama服务通信，获取LLM响应
    """
    
    def __init__(self, base_url: str = None):
        """
        初始化Ollama客户端
        
        Args:
            base_url: Ollama服务地址，默认从settings中获取
        """
        self.base_url = base_url or getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
        self.generate_url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"
    
    async def generate_stream(
        self, 
        model: str, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """
        生成文本流
        
        Args:
            model: 模型名称，如deepseek-r1:1.5b
            prompt: 用户输入的提示
            system_prompt: 系统提示
            temperature: 温度参数
            top_p: top-p采样参数
            top_k: top-k采样参数
            max_tokens: 最大生成token数
            
        Yields:
            生成的文本片段
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.generate_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                # 流式读取响应
                async for line in response.content:
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        
                        # 如果接收到完成标志，退出
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
    
    async def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天接口
        
        Args:
            model: 模型名称
            messages: 消息历史，格式为[{"role": "user", "content": "..."}, ...]
            temperature: 温度参数
            top_p: top-p采样参数
            top_k: top-k采样参数
            max_tokens: 最大生成token数
            
        Yields:
            生成的文本片段
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.chat_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                # 流式读取响应
                async for line in response.content:
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                        
                        # 如果接收到完成标志，退出
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
    
    async def check_model_availability(self, model: str) -> bool:
        """
        检查模型是否可用
        
        Args:
            model: 模型名称
            
        Returns:
            模型是否可用
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    return False
                
                data = await response.json()
                models = data.get("models", [])
                return any(m["name"] == model for m in models)
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048
    ) -> str:
        """
        同步聊天接口，用于REST API
        
        Args:
            model: 模型名称
            messages: 消息历史，格式为[{"role": "user", "content": "..."}, ...]
            temperature: 温度参数
            top_p: top-p采样参数
            top_k: top-k采样参数
            max_tokens: 最大生成token数
            
        Returns:
            生成的完整回复文本
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,  # 非流式
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(self.chat_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        
        data = response.json()
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        
        raise Exception("Unexpected response format from Ollama API")