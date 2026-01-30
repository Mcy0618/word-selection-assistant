#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流式处理工具类
用于处理流式数据的通用工具
"""

import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, Callable

logger = logging.getLogger(__name__)


class StreamHandler:
    """流式处理工具类
    
    提供流式数据的统一处理接口，支持回调机制。
    """
    
    @staticmethod
    async def process_stream(
        stream: AsyncGenerator[Dict[str, Any], None],
        on_chunk: Callable[[str], None],
        on_complete: Callable[[], None],
        on_error: Callable[[str], None]
    ):
        """
        处理流式数据
        
        Args:
            stream: 流式数据生成器
            on_chunk: 接收到数据块时的回调函数，参数为内容字符串
            on_complete: 完成时的回调函数
            on_error: 错误时的回调函数，参数为错误信息
        """
        try:
            async for chunk in stream:
                if "error" in chunk:
                    on_error(chunk["error"])
                    return
                
                content = chunk.get("content", "")
                if content:
                    on_chunk(content)
            
            on_complete()
            
        except Exception as e:
            logger.error(f"流式处理失败: {e}")
            on_error(str(e))
    
    @staticmethod
    async def process_stream_with_buffer(
        stream: AsyncGenerator[Dict[str, Any], None],
        on_chunk: Callable[[str], None],
        on_complete: Callable[[], None],
        on_error: Callable[[str], None],
        buffer_size: int = 1
    ):
        """
        处理流式数据（带缓冲）
        
        Args:
            stream: 流式数据生成器
            on_chunk: 接收到数据块时的回调函数
            on_complete: 完成时的回调函数
            on_error: 错误时的回调函数
            buffer_size: 缓冲区大小，积累指定数量的token后触发回调
        """
        try:
            buffer = ""
            
            async for chunk in stream:
                if "error" in chunk:
                    on_error(chunk["error"])
                    return
                
                content = chunk.get("content", "")
                if content:
                    buffer += content
                    
                    # 达到缓冲区大小时触发回调
                    if len(buffer) >= buffer_size:
                        on_chunk(buffer)
                        buffer = ""
            
            # 输出剩余内容
            if buffer:
                on_chunk(buffer)
            
            on_complete()
            
        except Exception as e:
            logger.error(f"流式处理失败: {e}")
            on_error(str(e))
    
    @staticmethod
    def create_mock_stream(text: str, chunk_size: int = 10) -> AsyncGenerator[Dict[str, Any], None]:
        """
        创建模拟流式数据生成器（用于测试）
        
        Args:
            text: 要分流的文本
            chunk_size: 每个块的大小
        
        Yields:
            Dict: 包含 'content' 字段的字典
        """
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            yield {"content": chunk, "delta": True}
            await asyncio.sleep(0.01)  # 模拟网络延迟