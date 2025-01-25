from typing import List, Optional
from pydantic import BaseModel

class ModelChoice(BaseModel):
    manufacturer: str
    model: str

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    model_choice: ModelChoice
    history: Optional[List[ChatMessage]] = []
    prompt_type: Optional[str] = "prompts"
    pdf_context: Optional[str] = None  # 添加PDF文件名字段
