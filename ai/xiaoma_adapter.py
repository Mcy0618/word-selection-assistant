#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小马算力API适配器
集成tokenpony的小马算力API
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


class XiaomaAdapter(BaseAdapter):
    """小马算力API适配器 - 兼容OpenAI格式"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        """
        初始化小马算力适配器
        
        Args:
            api_key: API密钥（可选，默认从.env读取）
            api_base: API基础URL（可选，默认从.env读取）
        """
        # 加载环境变量
        from dotenv import load_dotenv
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        self.api_key = api_key or os.getenv('TOKENPONY_API_KEY')
        self.api_base = (api_base or os.getenv('TOKENPONY_BASE_URL', 'https://api.tokenpony.cn/v1')).rstrip('/')
        self.model = "minimax-m2"  # 使用有效的模型名称
        self.session = None
        
        # 模型映射
        self.model_mapping = {
            "gpt-4": "deepseek",
            "gpt-3.5-turbo": "qwen",
            "claude-3": "glm",
        }
        
        logger.info(f"API配置: base={self.api_base}, key=***")
    
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
            
            # 调用实际API
            response = await self._call_api(prompt, **kwargs)
            
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
    
    async def _call_api(self, prompt: str, **kwargs) -> str:
        """
        调用小马算力API（OpenAI兼容格式）
        """
        # 在线程池中执行同步API调用
        loop = asyncio.get_event_loop()
        
        def sync_call():
            from openai import OpenAI
            
            client = OpenAI(
                base_url=self.api_base,
                api_key=self.api_key
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return response.choices[0].message.content
        
        try:
            result = await loop.run_in_executor(None, sync_call)
            logger.info(f"API调用成功，返回长度: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            # 返回错误信息而不是模拟数据
            raise
    
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
        流式聊天
        产生字典流，每项包含 'content' 字段
        """
        try:
            prompt = self._convert_messages(messages)
            # 模拟流式输出
            words = prompt.split()[:10]
            for word in words:
                yield {"content": word + " ", "delta": True}
                await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"流式请求失败: {e}")
            yield {"error": str(e)}
