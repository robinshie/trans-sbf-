from .chat_controller import router as chat_router
from .file_controller import router as file_router
from .model_controller import router as model_router
from .prompt_controller import router as prompt_router

__all__ = ['chat_router', 'file_router', 'model_router', 'prompt_router']
