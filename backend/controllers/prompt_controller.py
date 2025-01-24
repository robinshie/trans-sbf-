from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..models.CausalPromptFactory import CausalPromptFactory

router = APIRouter()
prompt_factory = CausalPromptFactory()

class PromptRequest(BaseModel):
    query: str
    texts: Optional[List[str]] = None
    history: Optional[List[str]] = None
    prompt_type: str = "query"  # query 或 followup

@router.post("/prompt/generate")
async def generate_prompt(request: PromptRequest):
    """生成prompt"""
    try:
        if request.prompt_type == "query":
            messages = await prompt_factory.build_query_prompt(
                query=request.query,
                texts=request.texts or [None]
            )
        else:
            messages = await prompt_factory.build_followup_prompt(
                query=request.query,
                texts=request.texts or [None],
                history=request.history or []
            )
        
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompt/templates")
async def get_prompt_templates():
    """获取预定义的prompt模板"""
    try:
        prompts = prompt_factory.config._prompts
        
        # 返回大类型和子类型的结构
        templates = []
        for category, content in prompts.items():
            if isinstance(content, dict):
                subtypes = []
                for subtype_key, subtype_content in content.items():
                    subtypes.append({
                        "name": subtype_key,
                        "content": subtype_content
                    })
                    
                templates.append({
                    "type": category,
                    "name": category.replace("_", " ").title(),
                    "subtypes": subtypes
                })
        
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompt/template/{category}")
async def get_prompt_template_by_category(category: str):
    """获取指定类别的prompt模板"""
    try:
        prompts = prompt_factory.config._prompts
        if category not in prompts:
            raise HTTPException(status_code=404, detail=f"Template category '{category}' not found")
            
        template = prompts[category]
        if not isinstance(template, dict):
            raise HTTPException(status_code=400, detail=f"Invalid template format for category '{category}'")
            
        return {
            "type": category,
            "name": category.replace("_", " ").title(),
            "content": template
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
