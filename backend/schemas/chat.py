from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from backend.config.settings import get_settings

settings = get_settings()

class ModelChoice(BaseModel):
    """模型选择配置"""
    manufacturer: str = Field(
        default=settings.DEFAULT_MODEL_MANUFACTURER,
        description="模型厂商",
        example="ollama",
        enum=["openai", "ollama", "deepseek"]
    )
    model: str = Field(
        default=settings.DEFAULT_MODEL_NAME,
        description="模型名称",
        example="qwen2.5:latest"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "manufacturer": "ollama",
                    "model": "qwen2.5:latest"
                },
                {
                    "manufacturer": "openai",
                    "model": "gpt-3.5-turbo"
                },
                {
                    "manufacturer": "deepseek",
                    "model": "deepseek-chat"
                }
            ]
        }

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(
        ...,
        description="用户消息",
        example="请将这段文字翻译成英文",
        min_length=1
    )
    model_choice: ModelChoice = Field(
        default=ModelChoice(),
        description="模型选择，默认使用 Ollama qwen2.5"
    )
    context: Optional[str] = Field(
        None,
        description="上下文内容",
        example="人工智能正在改变我们的生活方式"
    )
    history: Optional[List[Dict[str, str]]] = Field(
        None,
        description="聊天历史",
        example=[
            {"role": "user", "content": "你好","prefix":False},
            {"role": "system", "content": "你好！有什么我可以帮你的吗？","prefix":False}
        ]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "请将这段文字翻译成英文",
                "model_choice": {
                    "manufacturer": "ollama",
                    "model": "qwen2.5:latest"
                },
                "context": "人工智能正在改变我们的生活方式",
                "history": None
            }
        }

class FileResponse(BaseModel):
    """文件上传响应"""
    text: str = Field(
        ...,
        description="提取的文本内容",
        example="这是从PDF文件中提取的文本内容..."
    )
    filename: str = Field(
        ...,
        description="文件名",
        example="document.pdf"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "这是从PDF文件中提取的文本内容...",
                "filename": "document.pdf"
            }
        }
