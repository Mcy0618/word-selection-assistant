#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI兼容接口适配器
支持任意兼容OpenAI API格式的模型
"""

import logging
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenAICompatibleAdapter:
    """OpenAI兼容接口适配器"""
    
    def __init__(self, api_base: str, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        初始化适配器
        
        Args:
            api_base: API基础URL
            api_key: API密钥
            model: 模型名称
        """
        self.api_base = api_base.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.session = None
        self.timeout = 60  # 秒
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    def set_model(self, model: str):
        """设置模型"""
        self.model = model
        logger.info(f"切换模型: {model}")
    
    async def chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            kwargs: temperature, max_tokens, top_p等
        
        Returns:
            API响应
        """
        session = await self._get_session()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        # 设置默认值
        payload.setdefault("temperature", 0.7)
        payload.setdefault("max_tokens", 2000)
        payload.setdefault("stream", False)
        
        try:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API错误 ({response.status}): {error_text}")
                    raise Exception(f"API错误: {response.status}")
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"网络错误: {e}")
            raise
    
    async def stream_chat(self, messages: List[Dict], 
                          **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式聊天请求
        
        Yields:
            每个数据块的字典
        """
        session = await self._get_session()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        payload.setdefault("temperature", 0.7)
        payload.setdefault("max_tokens", 2000)
        
        try:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    yield {"error": f"API错误: {response.status}"}
                    return
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line or line == "data: [DONE]":
                        continue
                    
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            import json
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            pass
                            
        except aiohttp.ClientError as e:
            yield {"error": str(e)}
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """列出可用模型"""
        session = await self._get_session()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with session.get(
                f"{self.api_base}/models",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.warning(f"无法获取模型列表: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"获取模型列表失败: {e}")
            return []
    
    def format_message(self, role: str, content: str) -> Dict[str, str]:
        """格式化单条消息"""
        return {"role": role, "content": content}
    
    def create_translation_prompt(self, text: str, target_lang: str = "中文") -> List[Dict]:
        """创建翻译提示词"""
        return [
            {"role": "system", "content": f"你是一个专业翻译，将文本翻译成{target_lang}，保持原文格式。"},
            {"role": "user", "content": f"翻译以下内容:\n\n{text}"}
        ]
    
    def create_explanation_prompt(self, text: str, detail_level: str = "medium") -> List[Dict]:
        """创建解释提示词"""
        levels = {
            "simple": "简单解释",
            "medium": "详细解释，包括背景和含义",
            "detailed": "全面解释，包括背景、含义、使用场景和示例"
        }
        
        return [
            {"role": "system", "content": f"你是一个知识助手。请{levels.get(detail_level, '详细解释')}文本内容。"},
            {"role": "user", "content": f"解释以下内容:\n\n{text}"}
        ]
    
    def create_summary_prompt(self, text: str, max_length: int = 200) -> List[Dict]:
        """创建总结提示词"""
        return [
            {"role": "system", "content": f"你是一个总结助手。请用不超过{max_length}字总结文本要点。"},
            {"role": "user", "content": f"总结以下内容:\n\n{text}"}
        ]
