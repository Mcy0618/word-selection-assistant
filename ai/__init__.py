# AI模块初始化
from .xiaoma_adapter import XiaomaAdapter
from .openai_compatible import OpenAICompatibleAdapter
from .prompt_generator import PromptGenerator

__all__ = ['XiaomaAdapter', 'OpenAICompatibleAdapter', 'PromptGenerator']
