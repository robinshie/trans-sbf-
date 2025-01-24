import yaml
import os
from typing import List
from backend.schemas.model import ModelInfo
from backend.config.settings import get_settings

settings = get_settings()

class ModelService:
    """模型服务"""
    
    def __init__(self):
        """初始化模型服务"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def get_models(self) -> List[ModelInfo]:
        """获取所有可用模型"""
        models = []
        
        # 遍历所有厂商和其模型
        for manufacturer, config in self.config['models'].items():
            for model_name in config.get('models', []):
                is_default = (
                    manufacturer == settings.DEFAULT_MODEL_MANUFACTURER and
                    model_name == settings.DEFAULT_MODEL_NAME
                )
                
                description = self._get_model_description(manufacturer, model_name)
                
                models.append(ModelInfo(
                    name=model_name,
                    manufacturer=manufacturer,
                    description=description,
                    default=is_default
                ))
        
        return models
    
    def get_default_model(self) -> ModelInfo:
        """获取默认模型信息"""
        description = self._get_model_description(
            settings.DEFAULT_MODEL_MANUFACTURER,
            settings.DEFAULT_MODEL_NAME
        )
        
        return ModelInfo(
            name=settings.DEFAULT_MODEL_NAME,
            manufacturer=settings.DEFAULT_MODEL_MANUFACTURER,
            description=description,
            default=True
        )
    
    def _get_model_description(self, manufacturer: str, model_name: str) -> str:
        """获取模型描述"""
        descriptions = {
            'openai': {
                'gpt-3.5-turbo': 'OpenAI的GPT-3.5模型，适合一般对话和翻译任务',
                'gpt-4': 'OpenAI的GPT-4模型，具有更强的理解和翻译能力'
            },
            'ollama': {
                'qwen2.5:latest': '通义千问2.5模型，适合中英文翻译',
                'llama2': 'Meta的Llama2模型，支持多语言翻译',
                'mistral': 'Mistral AI的开源模型，支持多语言任务'
            },
            'deepseek': {
                'deepseek-chat': 'DeepSeek的对话模型，支持中英文交互',
                'deepseek-coder': 'DeepSeek的代码模型，适合技术文档翻译'
            }
        }
        
        return descriptions.get(manufacturer, {}).get(
            model_name,
            f"{manufacturer} {model_name} 模型"
        )
