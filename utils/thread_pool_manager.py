#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
线程池管理器
用于在后台线程中执行阻塞操作，避免UI卡顿
"""

import logging
import concurrent.futures
from typing import Callable, Any, Optional
from functools import partial

logger = logging.getLogger(__name__)


class ThreadPoolManager:
    """线程池管理器

    用于管理后台线程池，执行阻塞操作，避免UI线程卡顿。
    """

    _instance = None
    _executor = None
    _max_workers = 4

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化线程池"""
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_workers,
            thread_name_prefix="WordAssistantWorker"
        )
        logger.info(f"线程池初始化完成，工作线程数: {self._max_workers}")

    def submit(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """
        提交任务到线程池

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            Future: 可用于获取任务结果
        """
        if not self._executor or self._executor._shutdown:
            self._initialize()

        future = self._executor.submit(func, *args, **kwargs)
        logger.debug(f"任务已提交到线程池: {func.__name__}")
        return future

    def submit_with_callback(self, func: Callable, callback: Callable, *args, **kwargs):
        """
        提交任务并设置回调

        Args:
            func: 要执行的函数
            callback: 任务完成后的回调函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        future = self.submit(func, *args, **kwargs)
        future.add_done_callback(
            lambda f: callback(f.result()) if f.exception() is None else callback(f.exception())
        )
        return future

    def shutdown(self):
        """关闭线程池"""
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("线程池已关闭")

    @property
    def executor(self) -> Optional[concurrent.futures.ThreadPoolExecutor]:
        """获取线程池执行器"""
        return self._executor


# 全局实例
_thread_pool_manager = None


def get_thread_pool_manager() -> ThreadPoolManager:
    """获取线程池管理器实例"""
    global _thread_pool_manager
    if _thread_pool_manager is None:
        _thread_pool_manager = ThreadPoolManager()
    return _thread_pool_manager


def run_in_thread(func: Callable) -> Callable:
    """
    装饰器：在后台线程中执行函数

    Args:
        func: 要装饰的函数

    Returns:
        Callable: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        manager = get_thread_pool_manager()
        future = manager.submit(func, *args, **kwargs)
        return future
    return wrapper


def run_in_thread_with_callback(func: Callable, callback: Callable) -> Callable:
    """
    装饰器工厂：在后台线程中执行函数并调用回调

    Args:
        func: 要执行的函数
        callback: 回调函数

    Returns:
        Callable: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        manager = get_thread_pool_manager()
        manager.submit_with_callback(func, callback, *args, **kwargs)
    return wrapper