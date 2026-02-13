# AI模块初始化
from .xiaoma_adapter import XiaomaAdapter
from .openai_compatible import OpenAICompatibleAdapter
from .iflow_adapter import iFlowAdapter
from .prompt_generator import PromptGenerator
from .iflow_workflow import WorkflowManager, Workflow, WorkflowStep, WORKFLOW_PRESETS

__all__ = [
    'XiaomaAdapter',
    'OpenAICompatibleAdapter',
    'iFlowAdapter',
    'PromptGenerator',
    'WorkflowManager',
    'Workflow',
    'WorkflowStep',
    'WORKFLOW_PRESETS'
]
