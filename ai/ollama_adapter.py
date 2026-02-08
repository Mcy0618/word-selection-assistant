#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama API适配器
集成Ollama本地AI服务
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncGenerator
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


class OllamaAdapter(BaseAdapter):
    """Ollama API适配器 - 兼容OpenAI格式"""

    def __init__(self, api_key: str = None, api_base: str = None):
        """
        初始化Ollama适配器

        Args:
            api_key: API密钥（Ollama通常不需要，保留兼容性）
            api_base: API基础URL（可选，默认从.env或默认值读取）
        """
        # 加载环境变量
        from dotenv import load_dotenv
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Ollama通常不需要API密钥，但保留用于兼容性
        self.api_key = api_key or os.getenv('OLLAMA_API_KEY', '') or os.getenv('OPENAI_API_KEY', '')
        
        # 默认Ollama API地址
        self.api_base = (api_base or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')).rstrip('/')
        
        # 获取模型列表并设置默认模型
        available_models = self.get_available_models()
        if available_models:
            self.model = available_models[0]  # 使用第一个可用模型作为默认值
        else:
            self.model = "llama3.2"  # 如果无法获取模型列表，则使用默认模型名
        
        # 创建复用的 OpenAI 客户端（自动连接池）
        from openai import OpenAI
        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key or "ollama",  # Ollama通常不需要真正的API密钥
            timeout=30,
            max_retries=3,
            http_client=None  # 使用默认 httpx 连接池
        )

        logger.info(f"Ollama API配置: base={self.api_base}, model={self.model}")

    def set_model(self, model: str):
        """设置使用的模型"""
        self.model = model
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
            # 调用Ollama API（非流式）
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2048),
                top_p=kwargs.get('top_p', 0.9)
            )

            # 转换为标准格式
            return self._format_response(response)

        except Exception as e:
            logger.error(f"Ollama API请求失败: {e}")
            raise

    async def stream_chat(self, messages: List[Dict], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式聊天

        Args:
            messages: OpenAI格式的消息列表
            **kwargs: 其他参数（temperature, max_tokens等）

        Yields:
            Dict: 包含 'content' 和 'delta' 字段的字典
        """
        try:
            # 调用Ollama API（流式）
            stream_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2048),
                top_p=kwargs.get('top_p', 0.9)
            )

            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield {"content": chunk.choices[0].delta.content, "delta": True}

        except Exception as e:
            logger.error(f"Ollama流式请求失败: {e}")
            yield {"error": str(e)}

    def _format_response(self, response) -> Dict[str, Any]:
        """格式化响应为OpenAI格式"""
        return {
            "id": response.id,
            "object": response.object,
            "created": response.created,
            "model": response.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content
                    },
                    "finish_reason": choice.finish_reason
                } for choice in response.choices
            ],
            "usage": {
                "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                "total_tokens": getattr(response.usage, 'total_tokens', 0)
            }
        }

    def get_available_models(self) -> List[str]:
        """
        获取可用的Ollama模型列表
        
        Returns:
            List[str]: 模型名称列表
        """
        try:
            import requests
            response = requests.get(f"{self.api_base.replace('/v1', '')}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model['name'].split(':')[0] for model in data.get('models', [])]
                return models
            else:
                logger.warning(f"无法获取Ollama模型列表: {response.status_code}")
                # 返回一些常见的Ollama模型
                return ["llama3.2", "llama3.1", "mistral", "gemma2", "phi3", "qwen2.5"]
        except Exception as e:
            logger.error(f"获取Ollama模型列表失败: {e}")
            # 返回一些常见的Ollama模型
            return ["llama3.2", "llama3.1", "mistral", "gemma2", "phi3", "qwen2.5"]