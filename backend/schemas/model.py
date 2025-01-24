from typing import List, Optional
from pydantic import BaseModel, Field

class ModelInfo(BaseModel):
    """模型信息"""
    name: str = Field(..., description="模型名称")
    manufacturer: str = Field(..., description="模型厂商")
    description: Optional[str] = Field(None, description="模型描述")
    default: bool = Field(False, description="是否为默认模型")

class ModelsResponse(BaseModel):
    """模型列表响应"""
    models: List[ModelInfo] = Field(..., description="可用模型列表")
    total: int = Field(..., description="模型总数")
    default_model: ModelInfo = Field(..., description="默认模型")
