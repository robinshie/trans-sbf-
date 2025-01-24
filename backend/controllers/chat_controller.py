from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.chat import ChatRequest
from ..services.chat_service import ChatService
from .file_controller import pdf_contents
import json

router = APIRouter()
chat_service = ChatService()

@router.post("/chat/stream",
    summary="流式聊天",
    description="与 AI 助手进行流式对话，支持PDF上下文"
)
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    try:
        # 获取活跃的PDF上下文
        pdf_context = ""
        if hasattr(request, 'pdf_filename') and request.pdf_filename and request.pdf_filename in pdf_contents:
            pdf_context = pdf_contents[request.pdf_filename]['text']

        
        request.message = pdf_context

        # 创建一个异步生成器来处理流式响应
        async def generate_response():
            async for chunk in chat_service.generate_chat_response(
                request.message,
                request.model_choice,
                request.history,
                request.prompt_type
            ):
                # 确保每个块都是完整的字符串
                if isinstance(chunk, str):
                    yield chunk
                else:
                    yield json.dumps(chunk, ensure_ascii=False)

        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "X-Accel-Buffering": "no",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
