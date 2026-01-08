#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能路由器
根据用户选择路由到相应的功能处理
"""

import logging
from typing import Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class FunctionType(Enum):
    """功能类型枚举"""
    TRANSLATE = "translate"
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"
    CUSTOM = "custom"


@dataclass
class FunctionResult:
    """功能执行结果"""
    success: bool
    content: str
    error: str = None
    metadata: Dict[str, Any] = None


class FunctionRouter(QObject):
    """功能路由器"""
    
    # 信号
    result_ready = pyqtSignal(str, str)  # (功能类型, 结果)
    
    def __init__(self):
        super().__init__()
        self.handlers: Dict[FunctionType, Callable] = {}
        self.custom_functions: Dict[str, Dict[str, Any]] = {}
    
    def register_handler(self, func_type: FunctionType, handler: Callable):
        """注册功能处理器"""
        self.handlers[func_type] = handler
        logger.info(f"已注册功能处理器: {func_type.value}")
    
    def register_custom_function(self, name: str, config: Dict[str, Any]):
        """注册自定义功能"""
        self.custom_functions[name] = config
        logger.info(f"已注册自定义功能: {name}")
    
    async def route(self, func_type: str, text: str, 
                    options: Dict[str, Any] = None) -> str:
        """路由到相应的功能处理器"""
        options = options or {}
        
        try:
            if func_type == "translate":
                result = await self.handlers[FunctionType.TRANSLATE](text)
            elif func_type == "explain":
                result = await self.handlers[FunctionType.EXPLAIN](text)
            elif func_type == "summarize":
                result = await self.handlers[FunctionType.SUMMARIZE](text)
            elif func_type == "custom":
                func_name = options.get('function_name', '')
                result = await self._execute_custom(func_name, text)
            else:
                result = f"未知功能: {func_type}"
            
            self.result_ready.emit(func_type, result)
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"执行功能 {func_type} 失败: {error_msg}")
            self.result_ready.emit(func_type, f"错误: {error_msg}")
            return f"错误: {error_msg}"
    
    async def _execute_custom(self, func_name: str, text: str) -> str:
        """执行自定义功能"""
        if func_name in self.custom_functions:
            config = self.custom_functions[func_name]
            prompt = config.get('prompt_template', '{text}')
            return prompt.replace('{text}', text)
        return f"未找到自定义功能: {func_name}"
    
    def get_available_functions(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用的功能"""
        functions = {
            "translate": {'name': '翻译', 'description': '翻译文本', 'icon': '🔤'},
            "explain": {'name': '解释', 'description': '解释内容', 'icon': '💡'},
            "summarize": {'name': '总结', 'description': '总结要点', 'icon': '📝'}
        }
        
        for name, config in self.custom_functions.items():
            functions[f"custom_{name}"] = {
                'name': config.get('name', name),
                'description': config.get('description', ''),
                'icon': '⚙️',
                'is_custom': True
            }
        
        return functions