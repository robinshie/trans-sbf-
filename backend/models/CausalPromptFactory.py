import os
import yaml
from typing import List, Dict, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str

class PromptConfig:
    """提示词配置管理"""
    
    # 加载提示词配置
    _prompt_path = os.path.join(os.path.dirname(__file__), "..", "config", "prompts.yaml")
    with open(_prompt_path, 'r', encoding='utf-8') as f:
        _prompts = yaml.safe_load(f)

    @classmethod
    def get_prompt(cls, key: str, category: str = 'prompts') -> str:
        """获取提示词"""

        prompt = cls._prompts.get(category, {}).get(key, "")
        return prompt

class CausalPromptFactory:
    """提示词工厂类，用于构建不同场景的提示词"""
    
    def __init__(self):
        """初始化提示词工厂"""
        self.config = PromptConfig()
    
    async def build_query_prompt(self, query: str, texts: List[str]) -> List[ChatMessage]:
        """
        构建查询提示词
        
        Args:
            query: 用户查询
            texts: 相关文本列表
            
        Returns:
            List[ChatMessage]: 完整的提示词消息列表
        """
        messages = [
            ChatMessage(role="system", content=self.config.get_prompt('system', 'prompts'))
        ]
        
        # 合并所有文本
        text_content = "\n\n".join([t for t in texts if t]) if texts else "没有提供文本内容。"
        
        # 查询提示词
        query_prompt = self.config.get_prompt('query', 'prompts').format(
            text=text_content,
            query=query
        )
        messages.append(ChatMessage(role="user", content=query_prompt))
        
        return messages
    
    async def build_followup_prompt(self, query: str, texts: List[str], 
                                  history: List[Dict[str, str]]) -> List[ChatMessage]:
        """
        构建后续对话提示词
        
        Args:
            query: 用户查询
            texts: 相关文本列表
            history: 对话历史
            
        Returns:
            List[ChatMessage]: 完整的提示词消息列表
        """
        messages = [
            ChatMessage(role="system", content=self.config.get_prompt('system', 'prompts'))
        ]
        
        # 添加历史对话
        for msg in history:
            messages.append(ChatMessage(
                role="user" if msg['role'] == 'user' else "assistant",
                content=msg['content']
            ))
        
        # 合并所有文本
        text_content = "\n\n".join([t for t in texts if t]) if texts else "没有提供文本内容。"
        
        # 构建后续对话提示词
        followup_prompt = self.config.get_prompt('followup', 'prompts').format(
            text=text_content,
            query=query
        )
        messages.append(ChatMessage(role="user", content=followup_prompt))
        
        return messages

class AcademicReadingAssistant:
    """学术文献分析系统"""
    
    _prompt_path = os.path.join(os.path.dirname(__file__), "..", "config", "prompts.yaml")
    
    @classmethod
    async def build_context_prompt(cls, pdf_content: str, language: str = "中文") -> List[ChatMessage]:
        """构建上下文分析提示"""
        with open(cls._prompt_path, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)['academic']
        
        messages = [
            ChatMessage(role="system", content=prompts['system']),
            ChatMessage(role="user", content=prompts['context'].format(
                content=pdf_content,
                language=language
            ))
        ]
        return messages
    
    @classmethod
    async def build_query_prompt(cls, question: str, context_tags: list, 
                               language: str = "中文") -> List[ChatMessage]:
        """构建问题分析提示"""
        with open(cls._prompt_path, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)['academic']
        
        context = "\n".join(context_tags)
        messages = [
            ChatMessage(role="system", content=prompts['system']),
            ChatMessage(role="user", content=prompts['query'].format(
                context=context,
                question=question,
                language=language
            ))
        ]
        return messages