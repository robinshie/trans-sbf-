from fastapi import APIRouter, Depends
from backend.services.model_service import ModelService
from backend.schemas.model import ModelsResponse

router = APIRouter()

@router.get("/models",
    response_model=ModelsResponse,
    summary="获取可用模型列表",
    description="""
    获取所有可用的翻译模型列表。
    
    **返回信息：**
    * 所有可用模型的列表
    * 每个模型的详细信息（名称、厂商、描述）
    * 默认模型信息
    * 模型总数
    
    **示例响应：**
    ```json
    {
        "models": [
            {
                "name": "qwen2.5:latest",
                "manufacturer": "ollama",
                "description": "通义千问2.5模型，适合中英文翻译",
                "default": true
            },
            {
                "name": "gpt-3.5-turbo",
                "manufacturer": "openai",
                "description": "OpenAI的GPT-3.5模型，适合一般对话和翻译任务",
                "default": false
            }
        ],
        "total": 2,
        "default_model": {
            "name": "qwen2.5:latest",
            "manufacturer": "ollama",
            "description": "通义千问2.5模型，适合中英文翻译",
            "default": true
        }
    }
    ```
    """
)
async def get_models(
    model_service: ModelService = Depends(lambda: ModelService())
) -> ModelsResponse:
    """获取可用模型列表"""
    models = model_service.get_models()
    default_model = model_service.get_default_model()
    
    return ModelsResponse(
        models=models,
        total=len(models),
        default_model=default_model
    )
