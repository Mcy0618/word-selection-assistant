#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题管理器
管理应用的主题切换功能
"""

import json
from enum import Enum
from typing import Dict, Any
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject


class ThemeType(Enum):
    """主题类型枚举"""
    LIGHT = "light"
    DARK = "dark"


class ThemeManager(QObject):
    """主题管理器"""
    
    def __init__(self):
        super().__init__()
        self.current_theme = ThemeType.LIGHT
        self.themes = {
            ThemeType.LIGHT: self._get_light_theme(),
            ThemeType.DARK: self._get_dark_theme()
        }
    
    def set_theme(self, theme_type: ThemeType, app: QApplication = None):
        """设置主题"""
        self.current_theme = theme_type
        theme_stylesheet = self.themes[theme_type]
        
        if app:
            app.setStyleSheet(theme_stylesheet)
        else:
            # 如果没有传入app，尝试获取当前应用实例
            current_app = QApplication.instance()
            if current_app:
                current_app.setStyleSheet(theme_stylesheet)
    
    def get_current_theme(self) -> ThemeType:
        """获取当前主题"""
        return self.current_theme
    
    def _get_light_theme(self) -> str:
        """获取浅色主题样式"""
        return """
        /* 浅色主题 */
        QWidget {
            background-color: #ffffff;
            color: #333333;
        }
        
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 8px 16px;
            color: #333333;
        }
        
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        
        QTextEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 4px;
            color: #333333;
        }
        
        QFrame#card {
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid #e0e0e0;
            border-radius: 10px;
        }
        
        QLabel#title {
            color: #2c3e50;
            font-size: 16px;
            font-weight: bold;
        }
        
        QLabel#preview {
            color: #555555;
            background-color: #f9f9f9;
            border: 1px solid #eee;
            border-radius: 4px;
            padding: 8px;
        }
        
        QPushButton#btn_translate, QPushButton#btn_explain, 
        QPushButton#btn_summarize, QPushButton#btn_custom, QPushButton#btn_ocr {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 12px;
            font-weight: bold;
        }
        
        QPushButton#btn_translate:hover, QPushButton#btn_explain:hover, 
        QPushButton#btn_summarize:hover, QPushButton#btn_custom:hover, QPushButton#btn_ocr:hover {
            background-color: #2980b9;
        }
        
        QTextEdit#result {
            background-color: #fafafa;
            border: 1px solid #eee;
        }
        
        QPushButton#btn_copy {
            background-color: #2ecc71;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton#btn_copy:hover {
            background-color: #27ae60;
        }
        
        QPushButton#close {
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton#close:hover {
            background-color: #c0392b;
        }
        
        /* 设置对话框样式 */
        QDialog {
            background-color: #ffffff;
        }
        
        QTabWidget::pane {
            border: 1px solid #ccc;
            background-color: #fff;
        }
        
        QTabBar::tab {
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            padding: 8px 16px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #fff;
            border-bottom-color: #fff;
        }
        
        QLineEdit, QComboBox, QSpinBox {
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #3498db;
        }
        """
    
    def _get_dark_theme(self) -> str:
        """获取深色主题样式"""
        return """
        /* 深色主题 */
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #3c3f41;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 8px 16px;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: #4b4f52;
        }
        
        QPushButton:pressed {
            background-color: #35383a;
        }
        
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #ffffff;
        }
        
        QFrame#card {
            background-color: rgba(43, 43, 43, 0.9);
            border: 1px solid #444444;
            border-radius: 10px;
        }
        
        QLabel#title {
            color: #ecf0f1;
            font-size: 16px;
            font-weight: bold;
        }
        
        QLabel#preview {
            color: #ecf0f1;
            background-color: #36393c;
            border: 1px solid #4a4a4a;
            border-radius: 4px;
            padding: 8px;
        }
        
        QPushButton#btn_translate, QPushButton#btn_explain, 
        QPushButton#btn_summarize, QPushButton#btn_custom, QPushButton#btn_ocr {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 12px;
            font-weight: bold;
        }
        
        QPushButton#btn_translate:hover, QPushButton#btn_explain:hover, 
        QPushButton#btn_summarize:hover, QPushButton#btn_custom:hover, QPushButton#btn_ocr:hover {
            background-color: #2980b9;
        }
        
        QTextEdit#result {
            background-color: #252526;
            border: 1px solid #404040;
            color: #d4d4d4;
        }
        
        QPushButton#btn_copy {
            background-color: #2ecc71;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton#btn_copy:hover {
            background-color: #27ae60;
        }
        
        QPushButton#close {
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QPushButton#close:hover {
            background-color: #c0392b;
        }
        
        /* 设置对话框样式 */
        QDialog {
            background-color: #2b2b2b;
        }
        
        QTabWidget::pane {
            border: 1px solid #555;
            background-color: #2b2b2b;
        }
        
        QTabBar::tab {
            background-color: #3c3f41;
            border: 1px solid #555;
            padding: 8px 16px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: #ffffff;
        }
        
        QTabBar::tab:selected {
            background-color: #2b2b2b;
            border-bottom-color: #2b2b2b;
        }
        
        QLineEdit, QComboBox, QSpinBox {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
            color: #ffffff;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #3498db;
        }
        """
    
    def save_theme_preference(self, theme_type: ThemeType):
        """保存主题偏好到配置"""
        from utils.config_loader import get_config
        config = get_config()
        config.set("app.theme", theme_type.value)
        config.save()
    
    def load_theme_preference(self) -> ThemeType:
        """从配置加载主题偏好"""
        from utils.config_loader import get_config
        config = get_config()
        theme_value = config.get("app.theme", "light")
        try:
            return ThemeType(theme_value)
        except ValueError:
            return ThemeType.LIGHT


# 全局主题管理器实例
theme_manager = ThemeManager()


def get_theme_manager():
    """获取主题管理器实例"""
    return theme_manager