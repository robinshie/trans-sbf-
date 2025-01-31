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
        role_info = cls._prompts['roles'].get(node_name, {})
        return role_info.get('name', None)

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
    """提示词工厂类，用于构建不同场景的提示词"""
    
    def __init__(self):
        """初始化提示词工厂"""
        self.config = PromptConfig()
        self.role = RoleConfig()
    
    @staticmethod
    def extract_keys(template: str) -> List[str]:
        """从模板中提取占位符键"""
        return re.findall(r'\{(.*?)\}', template)
        
    async def build_prompt(self, params: Dict[str, Any]):
        """
        构建查询提示词

        Args:
            params (Dict[str, Any]): 包含 'query', 'texts', 'prompt_type', 和 'history' 的字典。

        Returns:
            List[ChatMessage]: 完整的提示词消息列表
        """
        messages = []
        prompt_type = params.get('prompt_type', 'prompts')
        role = ''
        # 遍历 prompt 的节点类型
        for node in self.config.get_prompt_nodes(prompt_type):
            rolename = self.role.get_role_name(node)
            if rolename is not None:
                role = rolename
            else: 
                role = 'assistant' 
            # 获取当前节点的模板
            node_template = self.config.get_prompt(node, prompt_type)
            if not node_template:
                continue
            
            # 提取模板中的占位符并按长度降序排序（确保最大匹配优先）
            keys = sorted(self.extract_keys(node_template), key=len, reverse=True)
            
            # 替换占位符为实际值
            filled_content = node_template
            for key in keys:
                value = params.get(key, f"{{{key}}}")  # 如果未提供参数，保留占位符
                
                # 处理列表和字符串类型的值
                if isinstance(value, list):
                    value = "\n\n".join(str(v) for v in value)
                elif isinstance(value, str):
                    pass  # 字符串直接使用
                else:
                    value = str(value)  # 其他类型转为字符串
                
                # 替换占位符
                filled_content = filled_content.replace(f"{{{key}}}", value)
            
            # 添加消息
            messages.append(ChatMessage(role=role, content=filled_content))
        
        return messages
    
    async def build_role(self, role: Role):
        # Implementation logic for handling the role
        print(f'Building role: {role}')
