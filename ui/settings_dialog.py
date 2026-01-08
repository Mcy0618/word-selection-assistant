#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框
"""

import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QComboBox, QCheckBox,
                              QTabWidget, QFormLayout, QSpinBox, QWidget)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("划词助手 - 设置")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tabs = QTabWidget()
        
        # 通用设置
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "通用")
        
        # API设置
        api_tab = self._create_api_tab()
        tabs.addTab(api_tab, "API")
        
        # 热键设置
        hotkey_tab = self._create_hotkey_tab()
        tabs.addTab(hotkey_tab, "热键")
        
        layout.addWidget(tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("保存")
        btn_save.clicked.connect(self._save_settings)
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """创建通用设置页"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # 自动启动
        self.chk_auto_start = QCheckBox("开机自动启动")
        layout.addRow("", self.chk_auto_start)
        
        # 语言
        self.cmb_language = QComboBox()
        self.cmb_language.addItems(["中文", "English"])
        layout.addRow("语言:", self.cmb_language)
        
        # 自动隐藏延迟
        self.spin_hide_delay = QSpinBox()
        self.spin_hide_delay.setRange(1000, 30000)
        self.spin_hide_delay.setSuffix(" 毫秒")
        layout.addRow("自动隐藏延迟:", self.spin_hide_delay)
        
        # 窗口透明度
        self.spin_opacity = QSpinBox()
        self.spin_opacity.setRange(50, 100)
        self.spin_opacity.setSuffix(" %")
        layout.addRow("窗口透明度:", self.spin_opacity)
        
        return tab
    
    def _create_api_tab(self) -> QWidget:
        """创建API设置页"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # 默认AI提供者
        self.cmb_provider = QComboBox()
        self.cmb_provider.addItems(["小马算力", "OpenAI兼容", "iFlow SDK"])
        layout.addRow("AI提供者:", self.cmb_provider)
        
        # API地址
        self.edit_api_base = QLineEdit()
        layout.addRow("API地址:", self.edit_api_base)
        
        # API密钥
        self.edit_api_key = QLineEdit()
        self.edit_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API密钥:", self.edit_api_key)
        
        # 模型
        self.edit_model = QLineEdit()
        layout.addRow("模型:", self.edit_model)
        
        return tab
    
    def _create_hotkey_tab(self) -> QWidget:
        """创建热键设置页"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # 热键组合
        self.edit_hotkey = QLineEdit("ctrl+alt+d")
        layout.addRow("触发热键:", self.edit_hotkey)
        
        # 提示
        hint = QLabel("提示：使用+连接按键，如 ctrl+alt+s")
        hint.setStyleSheet("color: #666;")
        layout.addRow("", hint)
        
        return tab
    
    def _load_settings(self):
        """加载设置"""
        # TODO: 从配置文件加载
        self.chk_auto_start.setChecked(False)
        self.cmb_language.setCurrentText("中文")
        self.spin_hide_delay.setValue(8000)
        self.spin_opacity.setValue(95)
        self.edit_api_base.setText("https://api.tokenpony.com")
        self.edit_model.setText("deepseek")
    
    def _save_settings(self):
        """保存设置"""
        settings = {
            "auto_start": self.chk_auto_start.isChecked(),
            "language": self.cmb_language.currentText(),
            "hide_delay": self.spin_hide_delay.value(),
            "opacity": self.spin_opacity.value(),
            "provider": self.cmb_provider.currentText(),
            "api_base": self.edit_api_base.text(),
            "api_key": self.edit_api_key.text(),
            "model": self.edit_model.text(),
            "hotkey": self.edit_hotkey.text()
        }
        
        logger.info(f"保存设置: {settings}")
        self.accept()
