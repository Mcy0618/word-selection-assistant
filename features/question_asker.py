#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于文本提问功能
允许用户针对选中的文本内容进行提问
"""

import logging
from typing import Optional
from ai.xiaoma_adapter import BaseAdapter
from ai.prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


class QuestionAsker:
    """基于文本的提问器，支持连续对话"""

    def __init__(self, adapter: BaseAdapter, enable_cache: bool = True):
        """
        初始化提问器

        Args:
            adapter: AI 适配器
            enable_cache: 是否启用缓存（当前未实现）
        """
        self.adapter = adapter
        self.prompt_generator = PromptGenerator()
        # 对话历史：包含上下文文本和多轮问答
        self.conversation_history: list = []
        self.current_context: str = ""
        logger.info("提问器初始化完成（支持连续对话）")

    def set_context(self, text: str):
        """设置当前上下文文本"""
        self.current_context = text
        # 清空之前的对话历史，因为上下文改变了
        self.conversation_history = []
        logger.info(f"设置上下文: {text[:50]}...")

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        logger.info("对话历史已清空")

    async def ask(self, text: str = None, question: str = "", model: Optional[str] = None) -> str:
        """
        基于文本回答问题，支持连续对话

        Args:
            text: 选中的文本内容（首次调用时传入，后续可为None）
            question: 用户的问题
            model: 模型名称（可选）

        Returns:
            str: AI 的回答
        """
        try:
            # 如果传入了新文本，更新上下文
            if text and text != self.current_context:
                self.set_context(text)

            # 构建包含对话历史的消息
            messages = self._build_conversation_messages(question)

            # 调用 AI
            response = await self.adapter.chat(messages)

            # 提取回答内容
            if isinstance(response, dict):
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                content = str(response)

            # 保存到对话历史
            self.conversation_history.append({
                "question": question,
                "answer": content
            })

            return content

        except Exception as e:
            logger.error(f"提问失败: {e}")
            return f"抱歉，处理您的问题时出现错误: {str(e)}"

    async def ask_stream(self, text: str = None, question: str = "", model: Optional[str] = None):
        """
        基于文本回答问题（流式版本），支持连续对话

        Args:
            text: 选中的文本内容（首次调用时传入，后续可为None）
            question: 用户的问题
            model: 模型名称（可选）

        Yields:
            dict: 包含 'content' 和 'delta' 的字典
        """
        try:
            # 如果传入了新文本，更新上下文
            if text and text != self.current_context:
                self.set_context(text)

            # 构建包含对话历史的消息
            messages = self._build_conversation_messages(question)

            # 调用流式 API
            full_answer = []
            async for chunk in self.adapter.stream_chat(messages):
                if "content" in chunk:
                    full_answer.append(chunk["content"])
                yield chunk

            # 保存到对话历史
            self.conversation_history.append({
                "question": question,
                "answer": "".join(full_answer)
            })

        except Exception as e:
            logger.error(f"流式提问失败: {e}")
            yield {"error": str(e)}

    def _build_conversation_messages(self, question: str) -> list:
        """
        构建包含对话历史的消息列表

        Args:
            question: 当前用户的问题

        Returns:
            list: OpenAI 格式的消息列表
        """
        # 系统提示词
        system_prompt = """你是一个智能助手，正在与用户进行关于某段文本的对话。
请参考用户提供的文本内容回答用户的问题。
如果问题与文本无关，请礼貌地指出。
回答应该准确、简洁、有帮助。"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 添加上下文文本（只在第一次或上下文改变时）
        if self.current_context:
            context_msg = f"参考文本：\n{self.current_context}\n\n请基于以上文本回答用户的问题。"
            messages.append({"role": "system", "content": context_msg})

        # 添加对话历史
        for item in self.conversation_history:
            messages.append({"role": "user", "content": item["question"]})
            messages.append({"role": "assistant", "content": item["answer"]})

        # 添加当前问题
        messages.append({"role": "user", "content": question})

        return messages

    def get_conversation_history(self) -> list:
        """获取对话历史"""
        return self.conversation_history.copy()

    def format_conversation_for_display(self) -> str:
        """格式化对话历史用于显示"""
        if not self.conversation_history:
            return ""

        lines = []
        for i, item in enumerate(self.conversation_history, 1):
            lines.append(f"Q{i}: {item['question']}")
            lines.append(f"A{i}: {item['answer']}")
            lines.append("")

        return "\n".join(lines)

    def set_model(self, model: str):
        """设置使用的模型"""
        self.adapter.set_model(model)
        logger.info(f"提问器切换模型: {model}")


# 导出
__all__ = ['QuestionAsker']
