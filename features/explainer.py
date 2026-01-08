#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解释功能模块
"""

import logging
from typing import Dict, Any, Optional
from ai.xiaoma_adapter import XiaomaAdapter

logger = logging.getLogger(__name__)


class Explainer:
    """解释功能"""
    
    def __init__(self, adapter: Optional[XiaomaAdapter] = None):
        """
        初始化解释功能
        
        Args:
            adapter: API适配器实例
        """
        self.adapter = adapter
        self.detail_level = "medium"
        self.audience = "general"
    
    async def explain(self, text: str, detail_level: Optional[str] = None, 
                      audience: Optional[str] = None) -> str:
        """
        解释文本内容
        
        Args:
            text: 源文本
            detail_level: 详细程度 (simple/medium/detailed)
            audience: 受众 (beginner/general/expert)
        
        Returns:
            str: 解释结果
        """
        detail_level = detail_level or self.detail_level
        audience = audience or self.audience
        
        if not self.adapter:
            return self._mock_explain(text, detail_level, audience)
        
        try:
            prompt = self._create_prompt(text, detail_level, audience)
            
            messages = [
                {"role": "system", "content": self._get_system_prompt(detail_level, audience)},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.adapter.chat(messages)
            result = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"解释失败: {e}")
            return f"解释失败: {e}"
    
    def _get_system_prompt(self, detail_level: str, audience: str) -> str:
        """获取系统提示词"""
        level_prompts = {
            "simple": "请简单解释文本的核心含义，用通俗易懂的语言。",
            "medium": "请详细解释文本的背景、含义和要点。",
            "detailed": "请全面解释文本，包括背景、含义、使用场景、示例和相关知识。"
        }
        
        audience_hints = {
            "beginner": "假设读者是初学者，需要从基础讲起。",
            "general": "假设读者有一定了解，保持适中的深度。",
            "expert": "假设读者是专家，可以深入讨论技术细节。"
        }
        
        return f"{level_prompts.get(detail_level, level_prompts['medium'])} {audience_hints.get(audience, '')}"
    
    def _create_prompt(self, text: str, detail_level: str, 
                       audience: str) -> str:
        """创建解释提示词"""
        return f"""请解释以下内容：

{text}

请按照{detail_level}级别和面向{audience}受众的方式进行解释："""
    
    def _mock_explain(self, text: str, detail_level: str, 
                      audience: str) -> str:
        """模拟解释结果"""
        level_words = {
            "simple": "简单来说",
            "medium": "详细来说",
            "detailed": "深入分析"
        }
        return f"[{level_words.get(detail_level, '解释')}]\n\n「{text[:30]}...」的含义是：这是一个需要解释的概念。"
