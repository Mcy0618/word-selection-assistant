#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EventLoop管理器
全局复用EventLoop，避免重复创建开销
"""

import asyncio
import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)


class EventLoopManager:
    """全局 EventLoop 管理器
    
    用于复用 EventLoop，避免每次API调用都创建新的事件循环，
    从而消除10-50ms的创建开销。
    """
    
    _loop = None
    _lock = None
    _initialized = False
    
    @classmethod
    def _initialize(cls):
        """初始化管理器"""
        if not cls._initialized:
            cls._lock = threading.Lock()
            cls._initialized = True
    
    @classmethod
    def get_loop(cls) -> asyncio.AbstractEventLoop:
        """
        获取或创建 EventLoop
        
        Returns:
            asyncio.AbstractEventLoop: 共享的EventLoop实例
        """
        cls._initialize()
        
        with cls._lock:
            if cls._loop is None or cls._loop.is_closed():
                cls._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(cls._loop)
                logger.debug("创建新的EventLoop")
            else:
                logger.debug("复用现有EventLoop")
        
        return cls._loop
    
    @classmethod
    def run_in_loop(cls, coro: Any) -> Any:
        """
        在共享 EventLoop 中运行协程
        
        Args:
            coro: 要运行的协程对象
        
        Returns:
            Any: 协程的返回值
        """
        loop = cls.get_loop()
        
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            with cls._lock:
                cls._loop = loop
        
        return loop.run_until_complete(coro)
    
    @classmethod
    def close(cls):
        """关闭 EventLoop"""
        with cls._lock:
            if cls._loop and not cls._loop.is_closed():
                cls._loop.close()
                logger.debug("EventLoop已关闭")
                cls._loop = None
    
    @classmethod
    def is_running(cls) -> bool:
        """
        检查EventLoop是否正在运行
        
        Returns:
            bool: EventLoop是否正在运行
        """
        if cls._loop is None:
            return False
        return cls._loop.is_running()