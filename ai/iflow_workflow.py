#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iFlow 工作流支持
提供智能任务规划、多步骤处理和链式调用能力
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WorkflowStepType(Enum):
    """工作流步骤类型"""
    TRANSLATE = "translate"
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"
    OPTIMIZE = "optimize"
    CUSTOM = "custom"


class WorkflowCondition(Enum):
    """工作流条件"""
    ALWAYS = "always"
    IF_LONG_TEXT = "if_long_text"
    IF_SHORT_TEXT = "if_short_text"
    IF_CONTAINS_CODE = "if_contains_code"
    IF_MULTILINGUAL = "if_multilingual"


class WorkflowStep:
    """工作流步骤"""

    def __init__(
        self,
        step_type: WorkflowStepType,
        name: str,
        condition: WorkflowCondition = WorkflowCondition.ALWAYS,
        options: Optional[Dict[str, Any]] = None
    ):
        self.step_type = step_type
        self.name = name
        self.condition = condition
        self.options = options or {}

    def should_execute(self, text: str, context: Dict[str, Any]) -> bool:
        """判断是否应该执行此步骤"""
        if self.condition == WorkflowCondition.ALWAYS:
            return True
        elif self.condition == WorkflowCondition.IF_LONG_TEXT:
            return len(text) > 500
        elif self.condition == WorkflowCondition.IF_SHORT_TEXT:
            return len(text) <= 500
        elif self.condition == WorkflowCondition.IF_CONTAINS_CODE:
            return "```" in text or "def " in text or "function " in text
        elif self.condition == WorkflowCondition.IF_MULTILINGUAL:
            # 简单检测多语言
            import re
            pattern = re.compile(r'[\u4e00-\u9fff]+')
            has_chinese = pattern.search(text) is not None
            has_english = any(c.isalpha() and c.isascii() for c in text)
            return has_chinese and has_english
        return True


class Workflow:
    """工作流"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.context: Dict[str, Any] = {}

    def add_step(self, step: WorkflowStep):
        """添加工作流步骤"""
        self.steps.append(step)
        return self

    def get_executable_steps(self, text: str) -> List[WorkflowStep]:
        """获取可执行的步骤列表"""
        return [step for step in self.steps if step.should_execute(text, self.context)]


class WorkflowManager:
    """工作流管理器"""

    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self._init_default_workflows()

    def _init_default_workflows(self):
        """初始化默认工作流"""
        # 1. 完整处理工作流：翻译 -> 解释 -> 总结
        full_processing = Workflow(
            name="full_processing",
            description="完整处理：翻译、解释、总结"
        )
        full_processing.add_step(
            WorkflowStep(WorkflowStepType.TRANSLATE, "翻译", options={"target_language": "中文"})
        )
        full_processing.add_step(
            WorkflowStep(WorkflowStepType.EXPLAIN, "解释", options={"detail_level": "medium"})
        )
        full_processing.add_step(
            WorkflowStep(WorkflowStepType.SUMMARIZE, "总结", options={"style": "concise"})
        )
        self.workflows["full_processing"] = full_processing

        # 2. 智能分析工作流：根据文本内容自动选择
        smart_analysis = Workflow(
            name="smart_analysis",
            description="智能分析：根据文本类型自动选择处理方式"
        )
        smart_analysis.add_step(
            WorkflowStep(WorkflowStepType.TRANSLATE, "翻译", condition=WorkflowCondition.IF_MULTILINGUAL)
        )
        smart_analysis.add_step(
            WorkflowStep(WorkflowStepType.EXPLAIN, "解释", condition=WorkflowCondition.IF_LONG_TEXT)
        )
        smart_analysis.add_step(
            WorkflowStep(WorkflowStepType.SUMMARIZE, "总结", condition=WorkflowCondition.IF_LONG_TEXT)
        )
        self.workflows["smart_analysis"] = smart_analysis

        # 3. 代码理解工作流
        code_understanding = Workflow(
            name="code_understanding",
            description="代码理解：针对代码片段的专用处理"
        )
        code_understanding.add_step(
            WorkflowStep(WorkflowStepType.EXPLAIN, "代码解释", condition=WorkflowCondition.IF_CONTAINS_CODE)
        )
        code_understanding.add_step(
            WorkflowStep(WorkflowStepType.OPTIMIZE, "代码优化", condition=WorkflowCondition.IF_CONTAINS_CODE)
        )
        self.workflows["code_understanding"] = code_understanding

        # 4. 快速翻译工作流
        quick_translate = Workflow(
            name="quick_translate",
            description="快速翻译：仅翻译，适用于短文本"
        )
        quick_translate.add_step(
            WorkflowStep(WorkflowStepType.TRANSLATE, "翻译", options={"target_language": "中文"})
        )
        self.workflows["quick_translate"] = quick_translate

        logger.info(f"初始化了 {len(self.workflows)} 个默认工作流")

    def register_workflow(self, workflow: Workflow):
        """注册自定义工作流"""
        self.workflows[workflow.name] = workflow
        logger.info(f"注册工作流: {workflow.name}")

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """获取工作流"""
        return self.workflows.get(name)

    def list_workflows(self) -> List[Dict[str, str]]:
        """列出所有工作流"""
        return [
            {
                "name": name,
                "description": workflow.description,
                "steps_count": len(workflow.steps)
            }
            for name, workflow in self.workflows.items()
        ]

    async def execute_workflow(
        self,
        workflow_name: str,
        text: str,
        handlers: Dict[WorkflowStepType, Callable]
    ) -> Dict[str, Any]:
        """
        执行工作流

        Args:
            workflow_name: 工作流名称
            text: 输入文本
            handlers: 各步骤的处理函数

        Returns:
            Dict: 执行结果
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_name}")

        executable_steps = workflow.get_executable_steps(text)
        if not executable_steps:
            logger.warning(f"工作流 {workflow_name} 没有可执行的步骤")
            return {
                "workflow": workflow_name,
                "steps_executed": 0,
                "results": [],
                "warning": "没有可执行的步骤"
            }

        results = []
        current_text = text

        for step in executable_steps:
            logger.info(f"执行步骤: {step.name} ({step.step_type.value})")

            try:
                # 获取对应的处理器
                handler = handlers.get(step.step_type)
                if not handler:
                    logger.warning(f"未找到处理器: {step.step_type}")
                    continue

                # 执行步骤
                result = await handler(current_text, **step.options)
                results.append({
                    "step": step.name,
                    "type": step.step_type.value,
                    "result": result
                })

                # 更新当前文本（用于链式处理）
                current_text = result

            except Exception as e:
                logger.error(f"步骤执行失败: {step.name}, 错误: {e}")
                results.append({
                    "step": step.name,
                    "type": step.step_type.value,
                    "error": str(e)
                })

        return {
            "workflow": workflow_name,
            "steps_executed": len(results),
            "results": results
        }


# 预定义的工作流配置
WORKFLOW_PRESETS = {
    "translate_explain": {
        "name": "翻译并解释",
        "description": "先翻译文本，然后解释含义",
        "steps": [
            {"type": "translate", "options": {"target_language": "中文"}},
            {"type": "explain", "options": {"detail_level": "medium"}}
        ]
    },
    "translate_summarize": {
        "name": "翻译并总结",
        "description": "先翻译文本，然后生成摘要",
        "steps": [
            {"type": "translate", "options": {"target_language": "中文"}},
            {"type": "summarize", "options": {"style": "concise"}}
        ]
    },
    "explain_summarize": {
        "name": "解释并总结",
        "description": "先解释文本，然后生成摘要",
        "steps": [
            {"type": "explain", "options": {"detail_level": "detailed"}},
            {"type": "summarize", "options": {"style": "bullet"}}
        ]
    }
}


# 导出
__all__ = [
    'WorkflowManager',
    'Workflow',
    'WorkflowStep',
    'WorkflowStepType',
    'WorkflowCondition',
    'WORKFLOW_PRESETS'
]