import os
import yaml
import httpx
from typing import Dict, List, AsyncGenerator
from pydantic import BaseModel
from .CausalPromptFactory import ChatMessage
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

class ChatModel:
    """基础聊天模型类"""
    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        raise NotImplementedError()

class OpenAIModel(ChatModel):
    """OpenAI模型类"""
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = ModelConfig.get_model_config('openai')
        self.client = httpx.AsyncClient()
        
    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [msg.dict() for msg in messages],
            "stream": True
        }
        
        async with self.client.stream(
            "POST",
            self.config['api_url'],
            headers=headers,
            json=data,
            timeout=30.0
        ) as response:
            if response.status_code != 200:
                error_msg = await response.text()
                raise Exception(f"OpenAI API error: {error_msg}")
                
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line.strip() == "data: [DONE]":
                        break
                    try:
                        chunk = json.loads(line[6:])
                        if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                            yield chunk["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue

class OllamaModel(ChatModel):
    """Ollama模型类"""
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = ModelConfig.get_model_config('ollama')
        self.client = httpx.AsyncClient()
        
    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        data = {
            "model": self.model_name,
            "messages": [msg.dict() for msg in messages],
            "stream": True
        }
        
        async with self.client.stream(
            "POST",
            f"{self.config['api_url']}/chat",
            json=data,
            timeout=30.0
        ) as response:
            if response.status_code != 200:
                error_msg = await response.text()
                raise Exception(f"Ollama API error: {error_msg}")
                
            async for line in response.aiter_lines():
                try:
                    chunk = json.loads(line)
                    if chunk.get("message", {}).get("content"):
                        yield chunk["message"]["content"]
                except json.JSONDecodeError:
                    continue

class DeepSeekModel(ChatModel):
    """DeepSeek模型类"""
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = ModelConfig.get_model_config('deepseek')
        self.client = httpx.AsyncClient()
        
    async def stream_chat(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [msg.dict() for msg in messages],
            "stream": True
        }
        
        async with self.client.stream(
            "POST",
            self.config['api_url'],
            headers=headers,
            json=data,
            timeout=30.0
        ) as response:
            if response.status_code != 200:
                error_msg = await response.text()
                raise Exception(f"DeepSeek API error: {error_msg}")
                
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        chunk = json.loads(line[6:])
                        if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                            yield chunk["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue

class ModelFactory:
    """模型工厂类"""
    
    _model_map = {
        'openai': OpenAIModel,
        'ollama': OllamaModel,
        'deepseek': DeepSeekModel
    }
    
    @classmethod
    def create_model(cls, model_choice: Dict[str, str]) -> ChatModel:
        """
        创建模型实例
        
        Args:
            model_choice: 模型选择配置，包含 manufacturer 和 model 字段
            
        Returns:
            ChatModel: 模型实例
            
        Raises:
            ValueError: 如果模型厂商不支持
        """
        manufacturer = model_choice.get('manufacturer', '').lower()
        model_name = model_choice.get('model', '')
        
        model_class = cls._model_map.get(manufacturer)
        if not model_class:
            raise ValueError(f"Unsupported model manufacturer: {manufacturer}")
            
        return model_class(model_name)
