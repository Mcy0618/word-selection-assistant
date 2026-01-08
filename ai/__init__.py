# AI模块初始化
from .xiaoma_adapter import XiaomaAdapter
from .openai_compatible import OpenAICompatibleAdapter
from .iflow_integration import IFlowIntegration
from .prompt_generator import PromptGenerator

__all__ = ['XiaomaAdapter', 'OpenAICompatibleAdapter', 'IFlowIntegration', 'PromptGenerator']
