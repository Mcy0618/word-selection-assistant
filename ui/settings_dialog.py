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

# 导入主题管理器
from utils.theme_manager import get_theme_manager, ThemeType
from utils.config_loader import get_config
from utils.settings_manager import get_settings_manager

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

        # 主题选择
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["浅色", "深色"])
        layout.addRow("主题:", self.cmb_theme)

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
        # 从配置文件加载
        config = get_config()

        # 通用设置
        self.chk_auto_start.setChecked(config.get('app.auto_start', False))
        self.cmb_language.setCurrentText(config.get('app.language', 'zh-CN'))

        # 加载主题设置
        theme_manager = get_theme_manager()
        current_theme = theme_manager.load_theme_preference()
        if current_theme == ThemeType.DARK:
            self.cmb_theme.setCurrentText("深色")
        else:
            self.cmb_theme.setCurrentText("浅色")

        self.spin_hide_delay.setValue(config.get('window.hide_delay', 8000))
        self.spin_opacity.setValue(int(config.get('window.opacity', 95) * 100))

        # API设置
        self.cmb_provider.setCurrentText(config.get('ai.default_provider', '小马算力'))
        self.edit_api_base.setText(config.get('ai.xiaoma.api_base', 'https://api.tokenpony.com'))
        self.edit_api_key.setText(config.get('ai.xiaoma.api_key', ''))
        self.edit_model.setText(config.get('ai.xiaoma.model', 'deepseek'))

        # 热键设置
        self.edit_hotkey.setText(config.get('hotkey.combination', 'ctrl+q'))

    def _save_settings(self):
        """保存设置"""
        settings = {
            "auto_start": self.chk_auto_start.isChecked(),
            "language": self.cmb_language.currentText(),
            "theme": self.cmb_theme.currentText(),  # 添加主题设置
            "hide_delay": self.spin_hide_delay.value(),
            "opacity": self.spin_opacity.value(),
            "provider": self.cmb_provider.currentText(),
            "api_base": self.edit_api_base.text(),
            "api_key": self.edit_api_key.text(),
            "model": self.edit_model.text(),
            "hotkey": self.edit_hotkey.text()
        }

        # 应用主题更改
        theme_manager = get_theme_manager()
        if self.cmb_theme.currentText() == "深色":
            theme_manager.set_theme(ThemeType.DARK)
            theme_manager.save_theme_preference(ThemeType.DARK)
        else:
            theme_manager.set_theme(ThemeType.LIGHT)
            theme_manager.save_theme_preference(ThemeType.LIGHT)

        # 保存配置到文件
        self._save_config_to_file(settings)

        logger.info(f"保存设置: {settings}")
        self.accept()

    def _save_config_to_file(self, settings: dict):
        """将设置保存到配置文件"""
        try:
            config = get_config()

            # 更新配置
            config.set('app.auto_start', settings['auto_start'])
            config.set('app.language', settings['language'])
            config.set('window.hide_delay', settings['hide_delay'])
            config.set('window.opacity', settings['opacity'] / 100.0)

            # 根据提供者保存API设置
            provider = settings['provider']
            if provider == "小马算力":
                config.set('ai.default_provider', 'xiaoma')
                config.set('ai.xiaoma.api_base', settings['api_base'])
                config.set('ai.xiaoma.api_key', settings['api_key'])
                config.set('ai.xiaoma.model', settings['model'])
            elif provider == "OpenAI兼容":
                config.set('ai.default_provider', 'openai')
                config.set('ai.openai.api_base', settings['api_base'])
                config.set('ai.openai.api_key', settings['api_key'])
            elif provider == "iFlow SDK":
                config.set('ai.default_provider', 'iflow')

            # 保存热键设置
            config.set('hotkey.combination', settings['hotkey'])

            # 保存到文件
            config.save()

            logger.info("配置已保存到文件")

        except Exception as e:
            logger.error(f"保存配置失败: {e}", exc_info=True)
