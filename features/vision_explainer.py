#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉解释器模块
基于多模态AI模型的图像理解和OCR功能
"""

import logging
import base64
import os
from typing import Optional, Dict, Any
from pathlib import Path
import aiohttp
import asyncio
from PIL import Image

logger = logging.getLogger(__name__)


class VisionExplainer:
    """视觉解释器类

    使用多模态AI模型（如Qwen-VL、GPT-4V等）进行图像理解和文字识别
    """

    def __init__(self, api_adapter=None):
        """
        初始化视觉解释器

        Args:
            api_adapter: API适配器实例（可选）
        """
        self.api_adapter = api_adapter
        self._available = self._check_availability()
        self.supported_models = [
            "qwen-vl-plus",           # 通义千问视觉版
            "qwen-vl-max",            # 通义千问视觉增强版
            "gpt-4-vision-preview",   # GPT-4 Vision
            "gpt-4o",                 # GPT-4o
            "gemini-pro-vision",      # Gemini Pro Vision
            "claude-3-vision",        # Claude 3 Vision
            "qwen3-vl-235b-a22b-instruct"  # Qwen3-VL模型
        ]

    def _check_availability(self) -> bool:
        """检查依赖是否可用"""
        try:
            # 检查PIL是否可用
            Image.open
            # 检查API适配器
            if self.api_adapter is None:
                logger.warning("API适配器未提供")
                return False

            logger.info("视觉解释器已初始化")
            return True
        except Exception as e:
            self._available = False
            logger.warning(f"视觉解释器不可用: {e}")
            return False

    def is_available(self) -> bool:
        """检查视觉解释器是否可用

        Returns:
            bool: 是否可用
        """
        return self._available

    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图像编码为base64字符串

        Args:
            image_path: 图像文件路径

        Returns:
            str: base64编码的图像数据
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"图像编码失败: {e}")
            raise

    def _build_vision_messages(self, image_path: str, prompt: str = None) -> list:
        """构建多模态消息

        Args:
            image_path: 图像文件路径
            prompt: 提示词（可选）

        Returns:
            list: 格式化的消息列表
        """
        base64_image = self._encode_image_to_base64(image_path)

        # 默认提示词
        if not prompt:
            prompt = "请详细描述这张图片中的内容，包括文字信息、图表信息、布局结构等所有可见的细节。"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        return messages

    async def explain_image(self, image_path: str, prompt: str = None) -> Optional[str]:
        """解释图像内容

        使用多模态AI模型分析图像内容

        Args:
            image_path: 图像文件路径
            prompt: 特定的提示词（可选）

        Returns:
            Optional[str]: 图像分析结果，如果失败则返回 None
        """
        if not self._available:
            logger.warning("视觉解释器不可用")
            return None

        if not os.path.exists(image_path):
            logger.error(f"图像文件不存在: {image_path}")
            return None

        try:
            logger.info(f"分析图像: {image_path}")

            # 构建消息
            messages = self._build_vision_messages(image_path, prompt)

            # 调用API
            response = await self.api_adapter.chat(messages, stream=False)

            if response and 'choices' in response:
                content = response['choices'][0]['message']['content']
                logger.info(f"图像分析完成: {len(content)}字符")
                return content
            else:
                logger.error(f"API响应格式错误: {response}")
                return None

        except Exception as e:
            logger.error(f"图像分析失败: {e}", exc_info=True)
            return None

    async def recognize_text(self, image_path: str, language: str = "auto") -> Optional[str]:
        """从图像中识别文字

        使用视觉模型进行OCR识别

        Args:
            image_path: 图像文件路径
            language: 识别语言（auto/中文/英文等）

        Returns:
            Optional[str]: 识别出的文字，如果失败则返回 None
        """
        if not self._available:
            logger.warning("视觉解释器不可用")
            return None

        # 构建针对文字识别的提示词
        if language == "auto":
            prompt = "请仔细识别并提取图片中的所有文字内容，保持原文格式，忽略图片中的非文字元素。"
        else:
            prompt = f"请仔细识别并提取图片中的所有{language}文字内容，保持原文格式。"

        return await self.explain_image(image_path, prompt)

    async def analyze_document(self, image_path: str) -> Dict[str, Any]:
        """分析文档类图像

        对表格、发票、文档等进行结构化分析

        Args:
            image_path: 图像文件路径

        Returns:
            Dict[str, Any]: 结构化的分析结果
        """
        if not self._available:
            logger.warning("视觉解释器不可用")
            return {}

        prompt = """
        请详细分析这张文档图片，提供以下信息：
        1. 文档类型（表格、发票、合同、报告等）
        2. 主要内容摘要
        3. 关键数据提取
        4. 结构化信息（如表格行列、字段等）
        5. 重要细节和注意事项

        请用结构化的方式输出结果。
        """

        result = await self.explain_image(image_path, prompt)

        return {
            "analysis": result,
            "file_path": image_path,
            "type": "document_analysis"
        }

    async def answer_image_question(self, image_path: str, question: str) -> Optional[str]:
        """回答关于图像的问题

        Args:
            image_path: 图像文件路径
            question: 关于图像的问题

        Returns:
            Optional[str]: 问题的答案，如果失败则返回 None
        """
        if not self._available:
            logger.warning("视觉解释器不可用")
            return None

        prompt = f"基于这张图片，请回答以下问题：{question}"

        return await self.explain_image(image_path, prompt)

    async def translate_image_text(self, image_path: str, target_language: str = "中文") -> Optional[str]:
        """翻译图像中的文字

        Args:
            image_path: 图像文件路径
            target_language: 目标语言

        Returns:
            Optional[str]: 翻译后的文字，如果失败则返回 None
        """
        prompt = f"请识别图片中的所有文字，然后翻译成{target_language}，保持原文格式。"

        return await self.explain_image(image_path, prompt)


# 全局视觉解释器实例
_vision_explainer = None


def get_vision_explainer(api_adapter=None) -> VisionExplainer:
    """获取全局视觉解释器实例

    Args:
        api_adapter: API适配器实例

    Returns:
        VisionExplainer: 视觉解释器实例
    """
    global _vision_explainer
    if _vision_explainer is None or (_vision_explainer.api_adapter != api_adapter):
        _vision_explainer = VisionExplainer(api_adapter)
    return _vision_explainer