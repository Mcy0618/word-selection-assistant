#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iFlow SDK 适配器
集成 iFlow CLI 的 AI 能力，支持智能任务规划和工具执行
使用 iflow_sdk 的 IFlowClient 直接调用本地 iFlow CLI
"""

import logging
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from abc import ABC, abstractmethod

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


class iFlowAdapter(BaseAdapter):
    """
    iFlow SDK 适配器
    利用 iFlow CLI 的智能体能力增强划词助手功能
    SDK 自动管理 iFlow 进程、端口和资源
    """

    def __init__(self, model: str = 'default', **kwargs):
        """
        初始化 iFlow 适配器

        Args:
            model: 模型名称，默认 'default'
            **kwargs: 其他配置参数（保留兼容）
        """
        self.model = model
        # 减少重试次数和延迟，提高响应速度
        self.max_retries = kwargs.get('max_retries', 2)
        self.retry_delay = kwargs.get('retry_delay', 1)
        logger.info(f"iFlow 适配器初始化完成，模型: {self.model}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口 - SDK 自动清理资源"""
        return False

    def set_model(self, model: str):
        """设置使用的模型"""
        self.model = model
        logger.info(f"切换模型: {self.model}")

    async def _wait_for_connection(self, client, timeout: int = 5) -> bool:
        """
        快速检查 iFlow 连接状态（优化版，减少等待时间）

        Args:
            client: IFlowClient 实例
            timeout: 超时时间（秒），默认5秒

        Returns:
            bool: 是否成功连接
        """
        start_time = asyncio.get_event_loop().time()
        # 最多等待 timeout 秒，每次检查间隔 0.1 秒
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                # 检查客户端是否已连接
                if hasattr(client, '_connected') and client._connected:
                    return True
                if hasattr(client, 'is_connected'):
                    is_conn = await client.is_connected()
                    if is_conn:
                        return True
                # 短暂等待后重试
                await asyncio.sleep(0.1)
            except Exception:
                await asyncio.sleep(0.1)
        return False

    async def chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        发送聊天请求（使用 iFlow SDK）

        Args:
            messages: OpenAI 格式的消息列表
            kwargs: 其他参数（保留兼容）

        Returns:
            OpenAI 格式的响应
        """
        try:
            from iflow_sdk import IFlowClient, AssistantMessage, TaskFinishMessage

            # 转换消息为文本
            prompt = self._convert_messages(messages)

            # 使用 SDK 的上下文管理器 - 自动管理 iFlow 进程和端口
            async with IFlowClient() as client:
                # 快速检查连接（最多5秒）
                connected = await self._wait_for_connection(client, timeout=5)
                if not connected:
                    logger.warning("iFlow 连接检查超时，尝试直接发送消息")

                # 发送消息
                await client.send_message(prompt)

                # 收集完整响应（添加超时机制）
                full_response = []
                try:
                    async with asyncio.timeout(60):  # 60秒总超时
                        async for message in client.receive_messages():
                            if isinstance(message, AssistantMessage):
                                full_response.append(message.chunk.text)
                            elif isinstance(message, TaskFinishMessage):
                                break
                except asyncio.TimeoutError:
                    logger.warning("响应接收超时，返回已接收内容")

                content = "".join(full_response)
                if not content:
                    return self._format_error("iFlow 返回空响应或超时")
                return self._format_response(content)

        except ImportError as e:
            logger.error(f"iflow_sdk 导入失败: {e}")
            return self._format_error("iFlow SDK 未安装")
        except Exception as e:
            logger.error(f"iFlow 调用失败: {e}")
            return self._format_error(str(e))

    async def stream_chat(self, messages: List[Dict], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式聊天（使用 iFlow SDK）- 优化版，减少等待时间

        Args:
            messages: OpenAI 格式的消息列表
            kwargs: 其他参数

        Yields:
            Dict: 包含 'content' 和 'delta' 字段的字典
        """
        retry_count = 0
        last_error = None

        while retry_count < self.max_retries:
            try:
                from iflow_sdk import IFlowClient, AssistantMessage, TaskFinishMessage

                prompt = self._convert_messages(messages)

                async with IFlowClient() as client:
                    # 快速检查连接（最多5秒）
                    connected = await self._wait_for_connection(client, timeout=5)
                    if not connected:
                        logger.debug("iFlow 连接未就绪，尝试直接发送")

                    await client.send_message(prompt)

                    chunk_count = 0
                    try:
                        # 使用超时机制，防止无限等待
                        async with asyncio.timeout(120):  # 2分钟总超时
                            async for message in client.receive_messages():
                                if isinstance(message, AssistantMessage):
                                    yield {"content": message.chunk.text, "delta": True}
                                    chunk_count += 1
                                elif isinstance(message, TaskFinishMessage):
                                    break
                    except asyncio.TimeoutError:
                        logger.warning("流式响应接收超时")
                        yield {"error": "响应超时，请重试"}
                        return

                    if chunk_count > 0:
                        return  # 成功完成
                    else:
                        raise Exception("未收到任何响应数据")

            except ImportError as e:
                logger.error(f"iflow_sdk 导入失败: {e}")
                yield {"error": "iFlow SDK 未安装"}
                return
            except Exception as e:
                last_error = e
                retry_count += 1
                logger.warning(f"流式请求失败（尝试 {retry_count}/{self.max_retries}）: {e}")
                if retry_count < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"流式请求最终失败: {e}")
                    yield {"error": f"连接失败: {str(e)}"}

    async def execute_workflow(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 iFlow Workflow（如果 SDK 支持）

        Args:
            workflow_name: 工作流名称
            params: 工作流参数

        Returns:
            Dict: 工作流执行结果
        """
        try:
            from iflow_sdk import IFlowClient, AssistantMessage, TaskFinishMessage

            async with IFlowClient() as client:
                # 快速检查连接
                await self._wait_for_connection(client, timeout=5)

                # 检查 SDK 是否支持工作流执行
                if hasattr(client, 'execute_workflow'):
                    result = await client.execute_workflow(
                        name=workflow_name,
                        params=params
                    )
                    return result
                else:
                    # 降级：使用普通聊天执行
                    prompt = f"执行工作流 '{workflow_name}':\n{params}"
                    await client.send_message(prompt)

                    full_response = []
                    try:
                        async with asyncio.timeout(60):
                            async for message in client.receive_messages():
                                if isinstance(message, AssistantMessage):
                                    full_response.append(message.chunk.text)
                                elif isinstance(message, TaskFinishMessage):
                                    break
                    except asyncio.TimeoutError:
                        pass

                    return {
                        "workflow": workflow_name,
                        "result": "".join(full_response)
                    }

        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            return {"error": str(e)}

    def _convert_messages(self, messages: List[Dict]) -> str:
        """将 OpenAI 消息格式转换为纯文本"""
        text_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            text_parts.append(f"[{role}]: {content}")
        return '\n'.join(text_parts)

    def _format_response(self, content: str) -> Dict[str, Any]:
        """格式化响应为 OpenAI 格式"""
        import time
        return {
            "id": f"iflow-{int(time.time())}",
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

    def _format_error(self, error_msg: str) -> Dict[str, Any]:
        """格式化错误响应为 OpenAI 格式"""
        return {
            "error": error_msg,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": f"抱歉，iFlow 服务暂时不可用。错误: {error_msg}"
                }
            }]
        }

    def get_available_models(self) -> List[str]:
        """获取可用的模型列表 - iFlow 支持的模型"""
        return [
            'GLM-4.7',
            'iFlow-ROME-30BA3B',
            'DeepSeek-V3.2',
            'Qwen3-Coder-Plus',
            'Kimi-K2-Thinking',
            'MiniMax-M2.1',
            'Kimi-K2.5',
            'Kimi-V3-0905',
            'default'
        ]


# 导出适配器类
__all__ = ['iFlowAdapter', 'BaseAdapter']