from typing import List, Optional
from pydantic import BaseModel
import json

class BaseModelWithJSON(BaseModel):
    """所有 Pydantic 模型的基类，提供 `to_json` 方法"""

    def to_json(self, **json_kwargs) -> str:
        """
        将 Pydantic 模型序列化为 JSON 字符串
        """
    """通用 BaseModel，添加 JSON 序列化方法"""

    def to_json(self, **json_kwargs) -> str:
        """使用 Pydantic 内置的 `model_dump_json()`（适用于 Pydantic v2）"""
        return self.model_dump_json(**json_kwargs)

    def to_dict(self) -> dict:
        """返回字典格式"""
        return self.model_dump()


class ContentItem(BaseModelWithJSON):
    """
    用于表示一个通用的 content 项，通过 'type' 字段区分不同类型。
    """
    type_: str
    text: Optional[str] = None
    image_base64: Optional[str] = None

    def to_dict(self):
        """
        根据 type_ 输出对应的字典结构。
        """
        if self.type_ == "text":
            return {
                "type": "text",
                "text": self.text or ""
            }
        elif self.type_ == "image_url":
            return {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{self.image_base64 or ''}"
            }
        else:
            return {
                "type": self.type_,
                "text": self.text,
                "image_base64": self.image_base64
            }


class ContentMessage(BaseModelWithJSON):
    """
    将多个 ContentItem 收集并生成 {"content": [...]} 的结构。
    """
    content_list: List[ContentItem] = []

    def add_item(self, type_: str, **kwargs):
        """
        添加 ContentItem
        """
        item = ContentItem(type_=type_, **kwargs)
        self.content_list.append(item)

    def to_dict(self) -> dict:
        """
        返回字典形式的内容
        """
        return {
            "content": [i.to_dict() for i in self.content_list]
        }


class Chat2Message(BaseModelWithJSON):
    """聊天消息模型"""
    role: str
    content: List[ContentMessage]


class ModelChoice(BaseModelWithJSON):
    manufacturer: str
    model: str


class ChatMessage(BaseModelWithJSON):
    """聊天消息模型"""
    role: str
    content: str


class ChatRequest(BaseModelWithJSON):
    message: str
    model_choice: ModelChoice
    history: Optional[List[ChatMessage]] = []
    prompt_type: Optional[str] = "prompts"
    pdf_context: Optional[str] = None  # 添加PDF文件名字段


class Assistant(BaseModelWithJSON):
    name: str


class Tools(BaseModelWithJSON):
    name: str


class Role(BaseModelWithJSON):
    name: str
    nodename: str
