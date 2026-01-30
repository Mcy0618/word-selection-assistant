#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图捕获引擎
支持截图和文本捕获功能
"""

import logging
import threading
import time
import os
import tempfile
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from PIL import Image, ImageGrab

logger = logging.getLogger(__name__)


class TextCapture(QObject):
    """截图捕获引擎

    支持截图和文本捕获功能，主要用于OCR和图像分析
    """

    text_captured = pyqtSignal(str)
    image_captured = pyqtSignal(str)  # 截图文件路径
    capture_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.retry_count = 3
        self.retry_delay = 0.1
        self.max_text_length = 10000
        self.temp_dir = tempfile.mkdtemp(prefix="word_assistant_")

    def capture(self, retry: int = None) -> Optional[str]:
        """捕获当前选中的文本"""
        if retry is None:
            retry = self.retry_count

        for attempt in range(retry):
            try:
                text = self._capture_via_clipboard()
                if text:
                    return self._validate_and_clean(text)
                time.sleep(self.retry_delay)
            except Exception as e:
                logger.debug(f"捕获尝试 {attempt + 1} 失败: {e}")

        self.capture_failed.emit("无法捕获选中文本")
        return None

    def capture_screenshot(self) -> Optional[str]:
        """截图并保存，返回图片路径"""
        try:
            logger.info("开始截图...")

            # 获取屏幕截图
            screenshot = ImageGrab.grab()

            # 保存到临时文件
            temp_file = os.path.join(self.temp_dir, f"screenshot_{int(time.time())}.png")
            screenshot.save(temp_file, "PNG")

            logger.info(f"截图保存成功: {temp_file}")
            self.image_captured.emit(temp_file)
            return temp_file

        except Exception as e:
            logger.error(f"截图失败: {e}")
            self.capture_failed.emit(f"截图失败: {e}")
            return None

    def capture_screenshot_async(self, callback: Callable[[str], None]):
        """异步截图"""
        def capture_task():
            image_path = self.capture_screenshot()
            if image_path and callback:
                callback(image_path)

        thread = threading.Thread(target=capture_task, daemon=True)
        thread.start()

    def get_selected_text(self) -> Optional[str]:
        """获取选中的文本"""
        return self.capture()

    def get_screenshot(self) -> Optional[str]:
        """获取屏幕截图"""
        return self.capture_screenshot()

    def capture_async(self, callback: Callable[[str], None]):
        """异步捕获文本"""
        def capture_task():
            text = self.capture()
            if text:
                self.text_captured.emit(text)
                if callback:
                    callback(text)

        thread = threading.Thread(target=capture_task, daemon=True)
        thread.start()

    def _capture_via_clipboard(self) -> Optional[str]:
        """通过剪贴板捕获文本"""
        # 首先尝试使用 Windows API 直接获取选中文本，避免模拟按键
        try:
            import win32gui
            import win32process
            import win32api
            import win32clipboard
            import win32con
            import ctypes
            from ctypes import wintypes, windll

            # 获取前台窗口句柄
            hwnd = windll.user32.GetForegroundWindow()
            if not hwnd:
                raise Exception("无法获取前台窗口句柄")

            # 保存当前剪贴板内容
            win32clipboard.OpenClipboard()
            try:
                # 检查是否有文本在剪贴板中
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    saved_clipboard_content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                else:
                    saved_clipboard_content = ""
            finally:
                win32clipboard.CloseClipboard()

            # 使用 keyboard 库模拟 Ctrl+C
            import keyboard
            keyboard.press_and_release('ctrl+c')
            time.sleep(0.05)  # 等待剪贴板更新

            # 读取剪贴板中的新内容
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    new_content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)

                    # 如果新内容与保存的内容不同，说明复制了选中文本
                    if new_content != saved_clipboard_content:
                        return new_content
            finally:
                # 恢复原始剪贴板内容
                win32clipboard.CloseClipboard()
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, saved_clipboard_content)
                finally:
                    win32clipboard.CloseClipboard()

        except ImportError as e:
            logger.debug(f"pywin32未安装: {e}")
        except Exception as e:
            logger.debug(f"Windows API方法失败: {e}")

        # 如果 Windows API 方法失败，尝试使用 pyperclip 作为备选方案
        try:
            import pyperclip
            saved_content = pyperclip.paste()  # 保存当前剪贴板内容

            # 模拟 Ctrl+C 操作
            import keyboard
            keyboard.press_and_release('ctrl+c')
            time.sleep(0.05)  # 等待剪贴板更新

            selected_text = pyperclip.paste()  # 获取新内容

            # 如果新内容与原内容不同，则认为是选中的文本
            if selected_text != saved_content:
                return selected_text
            else:
                # 没有选中文本，恢复原内容
                pyperclip.copy(saved_content)

        except ImportError:
            logger.debug("pyperclip未安装")
        except Exception as e:
            logger.debug(f"pyperclip方法失败: {e}")

        return None

    def _validate_and_clean(self, text: str) -> str:
        """验证和清理文本"""
        if not text:
            return ""

        text = text.strip()

        import re
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        if len(text) > self.max_text_length:
            text = text[:self.max_text_length]

        return text

    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            logger.info("临时文件清理完成")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")

    def __del__(self):
        """析构函数"""
        self.cleanup()
