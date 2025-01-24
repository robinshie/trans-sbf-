import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    """应用配置"""
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Translation Assistant API"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",  # 前端开发服务器
        "http://localhost:5500",  # VS Code Live Server
        "http://127.0.0.1:5500"   # VS Code Live Server (IP)
    ]
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 模型配置
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_MANUFACTURER: str = "openai"
    
    # 默认模型配置
    DEFAULT_MODEL_MANUFACTURER: str = "ollama"
    DEFAULT_MODEL_NAME: str = "qwen2.5:latest"
    
    # API密钥
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()
