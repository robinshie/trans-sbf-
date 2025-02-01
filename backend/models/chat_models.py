import os
from ..utils.async_api_client import AsyncAPIClient
import yaml
from typing import Dict, List, AsyncGenerator
from .chat import ChatMessage
import json
class ModelConfig:
    """模型配置管理类"""
    
    # 加载配置
    _config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    with open(_config_path, 'r', encoding='utf-8') as f:
        _config = yaml.safe_load(f)

    @classmethod
    def get_error(cls, key: str, **kwargs) -> str:
        """获取错误消息"""
        return cls._config['errors'].get(key, "Unknown error.").format(**kwargs)

    @classmethod
    def get_model_config(cls, model_type: str) -> Dict:
        """获取模型配置"""
        return cls._config['models'].get(model_type, {})

class ChatModel(AsyncAPIClient):
    """通用聊天模型基类"""

    def __init__(self, base_url: str, model_name: str):
        super().__init__(base_url)
        self.model_name = model_name

    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """流式请求聊天消息"""
        raise NotImplementedError()


class OpenAIModel(ChatModel):
    """OpenAI Chat Model"""
    
    def __init__(self, model_name: str):
        base_url =  ModelConfig.get_model_config('openai')['api_url']
        super().__init__(base_url, model_name)

    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """调用 OpenAI API 进行流式聊天"""
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": [msg.dict() for msg in messages],
            "stream": True
        }        
        async for chunk in self.async_stream_request("/chat/completions", headers=headers, json=data):
            yield chunk

class OllamaModel(ChatModel):
    """Ollama Chat Model"""
    
    def __init__(self, model_name: str):
        base_url = ModelConfig.get_model_config('ollama')['api_url']
        super().__init__(base_url, model_name)

    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """调用 Ollama API 进行流式聊天"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [msg.dict() for msg in messages],  # ✅ 确保是 Python 字典
            "stream": True
        }
        if messages and messages[-1].role == 'assistant':
            data["prefix"] = True
        
        async for chunk in self.async_stream_request("/chat", headers=headers, json=data):  # ✅ 直接传字典
            yield chunk


class DeepSeekModel(ChatModel):
    """DeepSeek Chat Model"""
    
    def __init__(self, model_name: str):
        base_url = ModelConfig.get_model_config('deepseek')['api_url']
        super().__init__(base_url, model_name)

    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """调用 DeepSeek API 进行流式聊天"""
        headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": [msg.dict() for msg in messages],
            "stream": True
        }
        async for chunk in self.async_stream_request("/chat/completions", headers=headers, json=data):
            yield chunk
