from typing import List, Dict, AsyncGenerator
import asyncio
from ..models.chat import ModelChoice, ChatMessage
from ..models.CausalPromptFactory import CausalPromptFactory
from ..models.ModelFactory import ModelFactory
#from ..services.file_service import file_contents
from  backend.controllers.file_controller import pdf_contents
class ChatService:
    """聊天服务"""
    def __init__(self):
        self.prompt_factory = CausalPromptFactory()
        
    async def generate_chat_response(
        self,
        message: str,
        model_choice: ModelChoice,
        history: List[ChatMessage],
        prompt_type: str = "query",
        pdf_context: str = None
    ) -> AsyncGenerator[str, None]:
        """生成聊天响应"""
        try:
            pdf_content = ""
            if pdf_context and pdf_context in pdf_contents:
                  pdf_content = pdf_contents[pdf_context]['text']

            messages = await self.prompt_factory.build_prompt({
                'query': message,
                'text': pdf_content,
                'prompt_type': prompt_type,
                'history': history
            })
            # # 构建提示词
            # if history:
            #     # 如果有历史记录，使用followup prompt
            #     messages = [
            #         ChatMessage(role="system", content=self.prompt_factory.config.get_prompt('system', prompt_type)),
            #         *history,
            #         ChatMessage(role="user", content=self.prompt_factory.config.get_prompt('followup', prompt_type).format(
            #             text="",
            #             query=message,
            #             history=history
            #         ))
            #     ]
            # else:
            #     # 否则使用query prompt
            #     messages = [
            #         ChatMessage(role="system", content=self.prompt_factory.config.get_prompt('system', prompt_type)),
            #         ChatMessage(role="user", content=self.prompt_factory.config.get_prompt('query', prompt_type).format(
            #             text="",
            #             query=message
            #         ))
            #     ]
            
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
