#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置管理器
提供设置变更通知机制
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any
from utils.config_loader import get_config

logger = logging.getLogger(__name__)


class SettingsManager(QObject):
    """设置管理器
    
    提供设置变更通知机制，当设置发生变化时通知所有监听器。
    """
    
    # 设置变更信号
    settings_changed = pyqtSignal(str, object)  # (设置键, 新值)
    settings_saved = pyqtSignal()  # 设置已保存信号
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值
        
        Args:
            key: 设置键（支持点分隔，如 "app.name"）
            default: 默认值
            
        Returns:
            Any: 设置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, notify: bool = True):
        """设置值并通知变更
        
        Args:
            key: 设置键
            value: 值
            notify: 是否通知变更
        """
        old_value = self.config.get(key)
        self.config.set(key, value)
        
        if notify and old_value != value:
            self.settings_changed.emit(key, value)
            logger.info(f"设置变更: {key} = {value}")
    
    def save(self):
        """保存设置到文件并通知"""
        self.config.save()
        self.settings_saved.emit()
        logger.info("设置已保存到文件")
    
    def connect_to_setting(self, key: str, callback: callable):
        """连接到特定设置的变更事件
        
        Args:
            key: 设置键
            callback: 回调函数，接收 (key, value) 参数
            
        Returns:
            int: 连接ID，可用于断开连接
        """
        return self.settings_changed.connect(lambda k, v: k == key and callback(k, v))
    
    def disconnect_from_setting(self, connection_id: int):
        """断开设置变更连接
        
        Args:
            connection_id: 连接ID
        """
        self.settings_changed.disconnect(connection_id)


# 全局设置管理器实例
_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """获取全局设置管理器实例
    
    Returns:
        SettingsManager: 设置管理器实例
    """
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_setting(key: str, default: Any = None) -> Any:
    """便捷函数：获取设置值
    
    Args:
        key: 设置键
        default: 默认值
        
    Returns:
        Any: 设置值
    """
    return get_settings_manager().get(key, default)


def set_setting(key: str, value: Any, notify: bool = True):
    """便捷函数：设置值
    
    Args:
        key: 设置键
        value: 值
        notify: 是否通知变更
    """
    get_settings_manager().set(key, value, notify)


def connect_to_setting(key: str, callback: callable) -> int:
    """便捷函数：连接到设置变更
    
    Args:
        key: 设置键
        callback: 回调函数
        
    Returns:
        int: 连接ID
    """
    return get_settings_manager().connect_to_setting(key, callback)


def disconnect_from_setting(connection_id: int):
    """便捷函数：断开设置变更连接
    
    Args:
        connection_id: 连接ID
    """
    get_settings_manager().disconnect_from_setting(connection_id)