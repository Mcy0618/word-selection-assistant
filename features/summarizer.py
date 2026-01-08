#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
总结功能模块
"""

import logging
from typing import Dict, Any, Optional
from ai.xiaoma_adapter import XiaomaAdapter

logger = logging.getLogger(__name__)


class Summarizer:
    """总结功能"""
    
    def __init__(self, adapter: Optional[XiaomaAdapter] = None):
        """
        初始化总结功能
        
        Args:
            adapter: API适配器实例
        """
        self.adapter = adapter
        self.max_length = 200
        self.style = "concise"
    
    async def summarize(self, text: str, max_length: Optional[int] = None, 
                        style: Optional[str] = None) -> str:
        """
        总结文本
        
        Args:
            text: 源文本
            max_length: 最大长度
            style: 风格 (concise/detailed/bullet)
        
        Returns:
            str: 总结结果
        """
        max_length = max_length or self.max_length
        style = style or self.style
        
        if not self.adapter:
            return self._mock_summarize(text, max_length, style)
        
        try:
            prompt = self._create_prompt(text, max_length, style)
            
            messages = [
                {"role": "system", "content": f"你是一个总结助手，用不超过{max_length}字总结文本，风格为{style}。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.adapter.chat(messages)
            result = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"总结失败: {e}")
            return f"总结失败: {e}"
    
    def _create_prompt(self, text: str, max_length: int, 
                       style: str) -> str:
        """创建总结提示词"""
        style_instructions = {
            "concise": "用简洁的语言概括核心要点。",
            "detailed": "详细总结，包括主要观点和支持细节。",
            "bullet": "用要点列表形式总结，每个要点简洁明了。"
        }
        
        instruction = style_instructions.get(style, style_instructions["concise"])
        
        return f"""请总结以下内容，{instruction}

要求：
- 不超过{max_length}字
- 保留关键信息
- 结构清晰

原文：
{text}

总结："""
    
    def _mock_summarize(self, text: str, max_length: int, 
                       style: str) -> str:
        """模拟总结结果"""
        if style == "bullet":
            lines = text.split('\n')[:3]
            bullets = '\n'.join(f"• {line[:50]}..." for line in lines if line.strip())
            return f"要点总结：\n{bullets}"
        else:
            return f"总结要点：\n\n{text[:max_length]}..."
