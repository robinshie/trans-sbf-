from typing import List, Dict, AsyncGenerator
import asyncio
from ..models.chat import ModelChoice, ChatMessage
from ..models.CausalPromptFactory import CausalPromptFactory
from ..models.ModelFactory import ModelFactory

class ChatService:
    """聊天服务"""
    def __init__(self):
        self.prompt_factory = CausalPromptFactory()
        
    async def generate_chat_response(
        self,
        message: str,
        model_choice: ModelChoice,
        history: List[ChatMessage],
        prompt_type: str = "query"
    ) -> AsyncGenerator[str, None]:
        """生成聊天响应"""
        try:
            # 构建提示词
            if history:
                # 如果有历史记录，使用followup prompt
                messages = [
                    ChatMessage(role="system", content=self.prompt_factory.config.get_prompt('system', prompt_type)),
                    *history,
                    ChatMessage(role="user", content=self.prompt_factory.config.get_prompt('followup', prompt_type).format(
                        text="",
                        query=message
                    ))
                ]
            else:
                # 否则使用query prompt
                messages = [
                    ChatMessage(role="system", content=self.prompt_factory.config.get_prompt('system', prompt_type)),
                    ChatMessage(role="user", content=self.prompt_factory.config.get_prompt('query', prompt_type).format(
                        text="",
                        query=message
                    ))
                ]
            
            # 获取模型实例
            model = ModelFactory.create_model({
                'manufacturer': model_choice.manufacturer,
                'model': model_choice.model
            })
            
            # 生成流式响应
            async for chunk in model.stream_chat(messages):
                yield chunk
                
        except Exception as e:
            print(f"Error in generate_chat_response: {str(e)}")
            yield f"对话生成出错: {str(e)}"
