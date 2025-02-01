import os
import yaml
import re
from typing import List, Dict, Any
from backend.models.chat import ChatMessage, Role
import asyncio

class RoleConfig:
    """提示词配置管理"""
    
    # 加载提示词配置
    _prompt_path = os.path.join(os.path.dirname(__file__), "..", "config", "roles.yaml")
    with open(_prompt_path, 'r', encoding='utf-8') as f:
        _prompts = yaml.safe_load(f)

    @classmethod
    def get_prompt(cls, key: str, category: str = 'roles') -> str:
        """获取提示词"""
        prompt = cls._prompts.get(category, {}).get(key, "")
        return prompt

    @classmethod
    def get_prompt_nodes(cls, category: str = 'roles') -> List[str]:
        """获取提示词节点"""
        return list(cls._prompts.get(category, {}).keys())

    @classmethod
    def get_role_name(cls, node_name: str) -> str:
        """获取指定角色名称"""
        role_info = cls._prompts['roles']

        for key, value in role_info.items():
            if value["nodename"] == node_name:
                return value["name"]
        return None  # 如果没有匹配的 nodename，则返回 N

class AssistanceConfig:
    """提示词配置管理"""
    
    # 加载提示词配置
    _prompt_path = os.path.join(os.path.dirname(__file__), "..", "config", "assistantes.yaml")
    with open(_prompt_path, 'r', encoding='utf-8') as f:
        _prompts = yaml.safe_load(f)

    @classmethod
    def get_prompt(cls, key: str, category: str = 'roles') -> str:
        """获取提示词"""
        prompt = cls._prompts.get(category, {}).get(key, "")
        return prompt

    @classmethod
    def get_prompt_nodes(cls, category: str = 'roles') -> List[str]:
        """获取提示词节点"""
        return list(cls._prompts.get(category, {}).keys())


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

    @classmethod
    def get_prompt_nodes(cls, category: str = 'prompts') -> List[str]:
        """获取提示词节点"""
        return list(cls._prompts.get(category, {}).keys())


class CausalPromptFactory:
    """支持模型识别和消息顺序控制的提示词工厂"""
    
    def __init__(self, model_name: str = "deepseek-reasoner"):
        self.config = PromptConfig()
        self.role = RoleConfig()
        self.model_name = model_name.lower()  # 统一转为小写

    @staticmethod
    def extract_keys(template: str) -> List[str]:
        return re.findall(r'\{(.*?)\}', template)
    
    def _is_deepseek_model(self) -> bool:
        """判断是否为需要特殊处理的 Deepseek 模型"""
        return "deepseek" in self.model_name

    def _enforce_message_order(self, messages: List[ChatMessage]) -> List[ChatMessage]:
        """根据模型要求强制调整消息顺序"""
        if not messages:
            return messages

        # Deepseek 模型特殊处理
        if self._is_deepseek_model():
            last_msg = messages[-1]
            
            # 强制最后一条必须是 user 或启用 prefix 的 assistant
            if last_msg.role == "assistant":
                # 如果已经是最后一条，保留但标记需要 prefix
                self.need_prefix = True
            else:
                self.need_prefix = False
            
            # 检查连续角色问题
            for i in range(1, len(messages)):
                if messages[i].role == messages[i-1].role:
                    # 自动插入修正消息
                    fix_role = "user" if messages[i].role == "assistant" else "assistant"
                    messages.insert(i, ChatMessage(
                        role=fix_role, 
                        content=f"[自动修正] 检测到连续 {messages[i].role} 角色",
                        prefix= False
                    ))
        
        return messages

    async def build_prompt(self, params: Dict[str, Any]) -> List[ChatMessage]:
        messages = []
        prompt_type = params.get('prompt_type', 'prompts')
        self.need_prefix = False  # 重置标记

        for node in self.config.get_prompt_nodes(prompt_type):
            # 获取角色配置
            role = self.role.get_role_name(node) or "assistant"
            
            # 模型特定角色覆盖
            if self._is_deepseek_model() and node == "system":
                role = "user"  # Deepseek 通常用 user 角色承载系统提示

            # 获取并填充模板
            template = self.config.get_prompt(node, prompt_type)
            if not template:
                continue

            # 动态参数替换
            keys = self.extract_keys(template)
            content = template
            for key in keys:
                value = params.get(key, "")
                if isinstance(value, list):
                    value = "\n".join(map(str, value))
                content = content.replace(f"{{{key}}}", str(value))

            messages.append(ChatMessage(role=role, content=content, prefix=False))

        # 后处理：消息顺序强制调整
        messages = self._enforce_message_order(messages)
        return messages