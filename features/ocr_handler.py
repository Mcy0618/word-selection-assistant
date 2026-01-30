#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR处理模块
基于多模态AI模型的智能OCR和图像理解
"""

import logging
import asyncio
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from .vision_explainer import VisionExplainer

# 添加项目根目录到路径以便加载配置
PROJECT_ROOT = Path(__file__).parent.parent

logger = logging.getLogger(__name__)


class OCRHandler:
    """智能OCR处理类

    基于多模态AI模型的OCR识别，支持复杂的文档分析和理解
    """

    def __init__(self, api_adapter=None):
        """
        初始化OCR处理器

        Args:
            api_adapter: API适配器实例（用于调用多模态模型）
        """
        self.api_adapter = api_adapter
        self.vision_explainer = None
        self.config = self._load_config()
        self.provider = self.config.get("ocr", {}).get("default_provider", "ai_vision")
        self._init_ocr()

    def _load_config(self):
        """同步加载配置"""
        try:
            import yaml
            config_path = PROJECT_ROOT / "config" / "settings.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载OCR配置失败: {e}")
        return {}

    def _init_ocr(self):
        """初始化OCR引擎"""
        try:
            # 初始化视觉解释器（基于AI模型）
            self.vision_explainer = VisionExplainer(self.api_adapter)

            if self.vision_explainer.is_available():
                logger.info("AI视觉OCR引擎初始化成功")
            else:
                logger.warning("AI视觉OCR引擎初始化失败")

        except Exception as e:
            logger.error(f"OCR引擎初始化失败: {e}")

    def _check_ai_availability(self) -> bool:
        """检查AI视觉模型是否可用"""
        if not self.vision_explainer:
            return False

        if not self.api_adapter:
            logger.warning("API适配器未提供")
            return False

        return self.vision_explainer.is_available()

    async def recognize_from_image(self, image_path: str, language: str = "auto",
                                 use_ai: bool = True) -> Optional[str]:
        """
        从图片路径识别文字

        Args:
            image_path: 图片路径
            language: 识别语言（auto/中文/英文等）
            use_ai: 是否使用AI模型（默认True）

        Returns:
            识别出的文字，如果失败则返回None
        """
        if not os.path.exists(image_path):
            logger.error(f"图像文件不存在: {image_path}")
            return None

        try:
            if use_ai and self._check_ai_availability():
                # 使用AI视觉模型进行OCR识别
                logger.info(f"使用AI模型识别文字: {image_path}")
                result = await self.vision_explainer.recognize_text(image_path, language)
                return result
            else:
                # 回退到传统OCR或占位实现
                logger.warning("AI模型不可用，使用基础识别")
                return await self._basic_ocr_fallback(image_path)

        except Exception as e:
            logger.error(f"OCR识别失败: {e}", exc_info=True)
            return None

    async def _basic_ocr_fallback(self, image_path: str) -> str:
        """基础OCR回退实现"""
        try:
            # 简单的占位实现 - 可以扩展为其他OCR库
            return f"[占位] 基础OCR识别结果: {image_path}"
        except Exception as e:
            logger.error(f"基础OCR回退失败: {e}")
            return f"[OCR失败] 无法识别图像内容"

    async def analyze_document_advanced(self, image_path: str) -> Dict[str, Any]:
        """
        高级文档分析（结构化信息提取）

        Args:
            image_path: 图像文件路径

        Returns:
            详细的分析结果，包含结构化信息
        """
        if not self._check_ai_availability():
            logger.warning("AI模型不可用，无法进行高级文档分析")
            return {}

        try:
            logger.info(f"高级文档分析: {image_path}")
            return await self.vision_explainer.analyze_document(image_path)
        except Exception as e:
            logger.error(f"文档分析失败: {e}", exc_info=True)
            return {}

    async def answer_about_image(self, image_path: str, question: str) -> Optional[str]:
        """
        回答关于图像的问题

        Args:
            image_path: 图像文件路径
            question: 关于图像的问题

        Returns:
            问题答案，如果失败则返回None
        """
        if not self._check_ai_availability():
            return None

        try:
            logger.info(f"图像问答: {question}")
            return await self.vision_explainer.answer_image_question(image_path, question)
        except Exception as e:
            logger.error(f"图像问答失败: {e}", exc_info=True)
            return None

    async def translate_image_text(self, image_path: str, target_language: str = "中文") -> Optional[str]:
        """
        翻译图像中的文字

        Args:
            image_path: 图像文件路径
            target_language: 目标语言

        Returns:
            翻译后的文字，如果失败则返回None
        """
        if not self._check_ai_availability():
            return None

        try:
            logger.info(f"图像文字翻译到{target_language}: {image_path}")
            return await self.vision_explainer.translate_image_text(image_path, target_language)
        except Exception as e:
            logger.error(f"图像文字翻译失败: {e}", exc_info=True)
            return None

    def recognize_from_pil_image(self, pil_image, language: str = "auto", use_ai: bool = True) -> Optional[str]:
        """
        从PIL图像对象识别文字

        Args:
            pil_image: PIL图像对象
            language: 识别语言
            use_ai: 是否使用AI模型

        Returns:
            识别出的文字，如果失败则返回None
        """
        import io
        import tempfile

        try:
            # 保存PIL图像到临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                pil_image.save(tmp_file.name)
                tmp_path = tmp_file.name

            # 使用异步方法
            result = asyncio.run(self.recognize_from_image(tmp_path, language, use_ai))
            return result

        except Exception as e:
            logger.error(f"PIL图像OCR失败: {e}", exc_info=True)
            return None
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass

    def is_available(self) -> bool:
        """检查OCR是否可用"""
        return self._check_ai_availability()

    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return [
            "auto", "中文", "英文", "日文", "韩文", "法文", "德文",
            "西班牙文", "意大利文", "俄文", "阿拉伯文", "葡萄牙文"
        ]

    def get_capabilities(self) -> Dict[str, bool]:
        """获取功能能力列表"""
        return {
            "basic_ocr": self.is_available(),
            "advanced_analysis": self._check_ai_availability(),
            "image_qa": self._check_ai_availability(),
            "text_translation": self._check_ai_availability(),
            "document_structure": self._check_ai_availability(),
            "handwriting_recognition": self._check_ai_availability()
        }


# 全局OCR处理器实例（带适配器参数）
_ocr_handler = None


def get_ocr_handler(api_adapter=None):
    """获取OCR处理器实例

    Args:
        api_adapter: API适配器实例

    Returns:
        OCRHandler: OCR处理器实例
    """
    global _ocr_handler
    if _ocr_handler is None or (_ocr_handler.api_adapter != api_adapter):
        _ocr_handler = OCRHandler(api_adapter)
    return _ocr_handler