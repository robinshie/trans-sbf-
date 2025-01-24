from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import get_settings
from backend.controllers import chat_router, file_router, model_router, prompt_router
import os

# 加载配置
settings = get_settings()

# 创建上传目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 创建应用
app = FastAPI(
    title="Translation Assistant API",
    description="""
    # 翻译助手 API 文档
    
    这是一个基于多种大语言模型的翻译助手 API，支持以下功能：
    
    ## 功能特点
    * 📝 支持多种语言模型（OpenAI、Ollama、DeepSeek）
    * 📚 支持 PDF 文档上传和文本提取
    * 💬 支持流式聊天响应
    * 🔄 支持上下文对话
    
    ## 主要端点
    * `/api/v1/models`: 获取可用模型列表
    * `/api/v1/chat/stream`: 流式聊天接口
    * `/api/v1/upload`: 文件上传接口
    
    ## 环境变量
    在使用 API 之前，请确保设置以下环境变量：
    * `OPENAI_API_KEY`: OpenAI API 密钥
    * `DEEPSEEK_API_KEY`: DeepSeek API 密钥
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(model_router, prefix=settings.API_V1_STR, tags=["models"])
app.include_router(chat_router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(file_router, prefix=settings.API_V1_STR, tags=["files"])
app.include_router(prompt_router, prefix=settings.API_V1_STR, tags=["prompts"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
