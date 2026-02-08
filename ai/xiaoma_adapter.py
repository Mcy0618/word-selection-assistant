#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI兼容API适配器
支持各种OpenAI兼容的服务提供商
"""

import os
import sys
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent  # word-selection-assistant 目录

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """API适配器基类"""

    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """发送聊天请求"""
        pass

    @abstractmethod
    def set_model(self, model: str):
        """设置模型"""
        pass


class OpenAIAdapter(BaseAdapter):
    """OpenAI兼容API适配器"""

    def __init__(self, api_key: str = None, api_base: str = None):
        """
        初始化OpenAI兼容适配器

        Args:
            api_key: API密钥（可选，默认从.env读取）
            api_base: API基础URL（可选，默认从.env读取）
        """
        # 加载环境变量
        from dotenv import load_dotenv
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.api_base = (api_base or os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')).rstrip('/')
        self.model = "gpt-3.5-turbo"  # 使用通用模型名称
        self.session = None

        # 创建复用的 OpenAI 客户端（自动连接池）
        from openai import OpenAI
        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key,
            timeout=30,
            max_retries=3,
            http_client=None  # 使用默认 httpx 连接池
        )

        logger.info(f"OpenAI兼容API配置: base={self.api_base}, key=***")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    def set_model(self, model: str):
        """设置使用的模型"""
        self.model = self.model_mapping.get(model, model)
        logger.info(f"切换模型: {self.model}")
    
    async def chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        发送聊天请求（OpenAI兼容格式）
        
        Args:
            messages: OpenAI格式的消息列表
            kwargs: 其他参数（temperature, max_tokens等）
        
        Returns:
            OpenAI格式的响应
        """
        try:
            # 转换消息格式
            prompt = self._convert_messages(messages)
            
            # 调用实际API（非流式）
            response = await self._call_api_sync(prompt, **kwargs)
            
            # 转换为OpenAI格式
            return self._format_response(response)
            
        except Exception as e:
            logger.error(f"API请求失败: {e}")
            raise
    
    def _convert_messages(self, messages: List[Dict]) -> str:
        """将OpenAI消息格式转换为纯文本"""
        text_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            text_parts.append(f"[{role}]: {content}")
        return '\n'.join(text_parts)
    
    async def _call_api_sync(self, prompt: str, **kwargs):
        """
        调用小马算力API（非流式）
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数（temperature, max_tokens等）
        
        Returns:
            str: 完整响应
        """
        try:
            # 非流式调用 - 使用复用的客户端
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            raise
    
    async def _call_api_stream(self, prompt: str, **kwargs):
        """
        调用小马算力API（流式）
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数（temperature, max_tokens等）
        
        Yields:
            str: 流式输出的内容块
        """
        try:
            # 流式调用 - 使用复用的客户端
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=kwargs.get('temperature', 0.7)
            )
            
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            yield f"错误: {str(e)}"
    
    def _format_response(self, content: str) -> Dict[str, Any]:
        """格式化响应为OpenAI格式"""
        import time
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(content) // 4,
                "completion_tokens": len(content) // 4,
                "total_tokens": len(content) // 2
            }
        }
    
    async def stream_chat(self, messages: List[Dict], **kwargs):
        """
        流式聊天（真实实现）

        Args:
            messages: OpenAI格式的消息列表
            **kwargs: 其他参数（temperature, max_tokens等）

        Yields:
            Dict: 包含 'content' 和 'delta' 字段的字典
        """
        try:
            # 调用真实流式API
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=kwargs.get('temperature', 0.7)
            )

            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    yield {"content": chunk.choices[0].delta.content, "delta": True}

        except Exception as e:
            logger.error(f"流式请求失败: {e}")
            yield {"error": str(e)}


# 为了向后兼容，保留XiaomaAdapter名称
XiaomaAdapter = OpenAIAdapter
