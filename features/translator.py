#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译功能模块
"""

import logging
from typing import Dict, Any, Optional, AsyncGenerator
from ai.xiaoma_adapter import XiaomaAdapter
from utils.local_cache import get_cache_manager

logger = logging.getLogger(__name__)


class Translator:
    """翻译功能"""
    
    def __init__(self, adapter: Optional[XiaomaAdapter] = None, enable_cache: bool = True):
        """
        初始化翻译功能
        
        Args:
            adapter: API适配器实例
            enable_cache: 是否启用缓存
        """
        self.adapter = adapter
        self.target_language = "中文"
        self.enable_cache = enable_cache
        self.cache_manager = get_cache_manager() if enable_cache else None
    
    async def translate(self, text: str, target_lang: Optional[str] = None, 
                        preserve_format: bool = True) -> str:
        """
        翻译文本
        
        Args:
            text: 源文本
            target_lang: 目标语言
            preserve_format: 是否保持格式
        
        Returns:
            str: 翻译结果
        """
        target_lang = target_lang or self.target_language
        
        if not self.adapter:
            return f"[模拟翻译] {text} → {target_lang}"
        
        # 检查缓存
        if self.enable_cache and self.cache_manager:
            cached_result = self.cache_manager.get(
                "translate", text, 
                target_lang=target_lang, 
                preserve_format=preserve_format
            )
            if cached_result is not None:
                logger.debug(f"翻译缓存命中: {text[:50]}...")
                return cached_result
        
        try:
            # 创建提示词
            prompt = self._create_prompt(text, target_lang, preserve_format)
            
            # 调用API
            messages = [
                {"role": "system", "content": f"你是一个专业翻译，将文本翻译成{target_lang}，保持原文格式。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.adapter.chat(messages)
            result = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 缓存结果
            if self.enable_cache and self.cache_manager:
                self.cache_manager.set(
                    "translate", text, result.strip(),
                    target_lang=target_lang,
                    preserve_format=preserve_format
                )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return f"翻译失败: {e}"
    
    async def translate_stream(self, text: str, target_lang: Optional[str] = None, 
                              preserve_format: bool = True) -> AsyncGenerator[Dict[str, str], None]:
        """
        流式翻译文本
        
        Args:
            text: 源文本
            target_lang: 目标语言
            preserve_format: 是否保持格式
        
        Yields:
            Dict: 包含 'content' 字段的字典
        """
        target_lang = target_lang or self.target_language
        
        if not self.adapter:
            yield {"content": f"[模拟翻译] {text} → {target_lang}"}
            return
        
        # 检查缓存
        if self.enable_cache and self.cache_manager:
            cached_result = self.cache_manager.get(
                "translate", text, 
                target_lang=target_lang, 
                preserve_format=preserve_format
            )
            if cached_result is not None:
                logger.debug(f"翻译缓存命中（流式）: {text[:50]}...")
                # 模拟流式输出
                yield {"content": cached_result, "delta": False, "from_cache": True}
                return
        
        try:
            # 创建提示词
            prompt = self._create_prompt(text, target_lang, preserve_format)
            
            # 调用流式API
            messages = [
                {"role": "system", "content": f"你是一个专业翻译，将文本翻译成{target_lang}，保持原文格式。"},
                {"role": "user", "content": prompt}
            ]
            
            full_result = ""
            async for chunk in self.adapter.stream_chat(messages):
                if "error" in chunk:
                    yield chunk
                    break
                
                content = chunk.get("content", "")
                if content:
                    full_result += content
                    yield {"content": content, "delta": True}
            
            # 缓存完整结果
            if self.enable_cache and self.cache_manager and full_result:
                self.cache_manager.set(
                    "translate", text, full_result,
                    target_lang=target_lang,
                    preserve_format=preserve_format
                )
                    
        except Exception as e:
            logger.error(f"流式翻译失败: {e}")
            yield {"error": str(e)}
    
    def _create_prompt(self, text: str, target_lang: str, 
                       preserve_format: bool) -> str:
        """创建翻译提示词"""
        if preserve_format:
            return f"""请将以下内容翻译成{target_lang}，保持原文的格式和结构：

{text}

翻译："""
        else:
            return f"翻译成{target_lang}: {text}"
    
    def detect_language(self, text: str) -> str:
        """
        简单检测语言
        
        Args:
            text: 文本
        
        Returns:
            str: 检测到的语言
        """
        # 简单实现：检查是否包含中文字符
        import re
        if re.search(r'[\u4e00-\u9fff]', text):
            return "zh"
        return "en"
