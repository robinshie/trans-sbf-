from .chat_models import OpenAIModel, OllamaModel, DeepSeekModel

class ModelFactory:
    """工厂模式创建不同的 ChatModel"""

    _model_map = {
        'openai': OpenAIModel,
        'ollama': OllamaModel,
        'deepseek': DeepSeekModel
    }

    @classmethod
    def create_model(cls, manufacturer: str, model_name: str):
        """
        根据厂商创建对应的模型实例
        """
        manufacturer = manufacturer.lower()
        model_class = cls._model_map.get(manufacturer)
        if not model_class:
            raise ValueError(f"Unsupported model manufacturer: {manufacturer}")
        return model_class(model_name)
