#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局热键管理 - 使用 keyboard 库
"""

import logging
import keyboard
from PyQt6.QtCore import QObject, pyqtSignal, QEvent, QCoreApplication

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    """全局热键管理器"""
    
    hotkey_triggered = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.registered = False
        self.hotkey_combo = "ctrl+q"  # 默认热键
        
        logger.info(f"热键管理器初始化，使用 {self.hotkey_combo}")
    
    def register_hotkey(self, combo: str = None) -> bool:
        """
        注册热键
        
        Args:
            combo: 热键组合字符串，如 "ctrl+q"
        
        Returns:
            bool: 是否注册成功
        """
        if combo:
            self.hotkey_combo = combo
        
        return self._do_register()
    
    def register_default_hotkey(self) -> bool:
        """注册默认热键 Ctrl+Q"""
        self.hotkey_combo = "ctrl+q"
        return self._do_register()
    
    def _do_register(self) -> bool:
        """执行注册"""
        try:
            self.unregister_hotkey()
            
            keyboard.add_hotkey(self.hotkey_combo, self._on_hotkey)
            
            self.registered = True
            logger.info(f"热键注册成功: {self.hotkey_combo}")
            return True
            
        except Exception as e:
            logger.exception(f"注册热键时发生异常: {e}")
            return False
    
    def unregister_hotkey(self):
        """注销热键"""
        try:
            if self.registered:
                keyboard.remove_hotkey(self.hotkey_combo)
                logger.info("热键已注销")
            
            self.registered = False
            
        except Exception as e:
            logger.exception(f"注销热键时发生异常: {e}")
    
    def _on_hotkey(self):
        """热键被触发 - 直接发送信号"""
        logger.info(f"热键 {self.hotkey_combo} 被触发")
        # 直接发送信号（keyboard 回调在主线程中执行）
        self.hotkey_triggered.emit(self.hotkey_combo)
    
    def customEvent(self, event):
        """处理自定义事件"""
        if isinstance(event, _HotkeyEvent):
            self.hotkey_triggered.emit(event.hotkey)
    
    def __del__(self):
        self.unregister_hotkey()


class _HotkeyEvent(QEvent):
    """热键事件"""
    _type = QEvent.Type.User + 1
    
    def __init__(self, hotkey: str):
        super().__init__(self._type)
        self.hotkey = hotkey