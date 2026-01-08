#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本捕获引擎
从各种应用中捕获选中的文本
"""

import logging
import threading
import time
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class TextCapture(QObject):
    """文本捕获引擎"""
    
    text_captured = pyqtSignal(str)
    capture_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.retry_count = 3
        self.retry_delay = 0.1
        self.max_text_length = 10000
    
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
        try:
            import win32clipboard
            import win32con
            import ctypes
            
            vk_control = 0x11
            vk_c = 0x43
            
            ctypes.windll.user32.keybd_event(vk_control, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk_c, 0, 0, 0)
            ctypes.windll.user32.keybd_event(vk_c, 0, 2, 0)
            ctypes.windll.user32.keybd_event(vk_control, 0, 2, 0)
            
            time.sleep(0.05)
            
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            finally:
                win32clipboard.CloseClipboard()
                
        except ImportError:
            logger.debug("pywin32未安装")
        except Exception as e:
            logger.debug(f"剪贴板方法失败: {e}")
        
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
    
    def get_selected_text(self) -> Optional[str]:
        """获取选中的文本 - capture 方法的别名"""
        return self.capture()
