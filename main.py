#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
划词助手 - 主程序入口
Word Selection Assistant - Main Entry Point

功能：
- 全局划词翻译/解释/总结
- AI辅助自定义功能
- 多模型支持（小马算力/OpenAI/iFlow）
"""

import sys
import os
import asyncio
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, Qt

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent

# 导入模块
from core.hotkey_manager import HotkeyManager
from core.text_capture import TextCapture
from core.function_router import FunctionRouter, FunctionType
from ui.tray_icon import TrayIcon
from ui.popup_window import PopupWindow
from ui.settings_dialog import SettingsDialog
from ai.xiaoma_adapter import XiaomaAdapter
from ai.iflow_integration import IFlowIntegration
from features.translator import Translator
from features.explainer import Explainer
from features.summarizer import Summarizer
from features.custom_builder import CustomBuilder
from utils.logger import setup_logger
from utils.config_loader import get_config

# 配置日志
logger = setup_logger(
    name="WordSelectionAssistant",
    level="INFO",
    log_file="logs/word_assistant.log"
)


class WordSelectionAssistant(QObject):
    """划词助手主类"""
    
    # 信号
    text_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Qt应用
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 配置 - 使用绝对路径
        config_path = str(PROJECT_ROOT / "config" / "settings.yaml")
        self.config = get_config(config_path)
        
        # 初始化组件
        self._init_components()
        self._connect_signals()
        
        logger.info("划词助手初始化完成")
    
    def _init_components(self):
        """初始化组件"""
        # API适配器
        self.xiaoma_adapter = XiaomaAdapter()
        self.iflow = IFlowIntegration()
        
        # 功能模块
        self.translator = Translator(self.xiaoma_adapter)
        self.explainer = Explainer(self.xiaoma_adapter)
        self.summarizer = Summarizer(self.xiaoma_adapter)
        self.custom_builder = CustomBuilder(self.xiaoma_adapter)
        
        # 核心组件
        self.hotkey_manager = HotkeyManager()
        self.text_capture = TextCapture()
        self.function_router = FunctionRouter()
        
        # 注册功能处理器
        self.function_router.register_handler(FunctionType.TRANSLATE, self.translator.translate)
        self.function_router.register_handler(FunctionType.EXPLAIN, self.explainer.explain)
        self.function_router.register_handler(FunctionType.SUMMARIZE, self.summarizer.summarize)
        
        # UI组件
        self.tray_icon = TrayIcon()
        self.popup_window = PopupWindow(self.translator, self.explainer, self.summarizer)
    
    def _connect_signals(self):
        """连接信号"""
        # 热键触发
        self.hotkey_manager.hotkey_triggered.connect(self._on_hotkey)
        
        # 托盘菜单
        self.tray_icon.show_popup_requested.connect(self._on_tray_popup)
        self.tray_icon.settings_requested.connect(self._show_settings)
        
        # 功能选择
        self.function_router.result_ready.connect(self._on_result)
    
    def _on_hotkey(self, data):
        """热键触发"""
        logger.info("热键被触发")
        # 获取选中文本
        text = self.text_capture.get_selected_text()
        if text:
            self.text_selected.emit(text)
            self.popup_window.show_with_text(text)
        else:
            logger.warning("未检测到选中文本")
    
    def _on_tray_popup(self):
        """托盘图标弹出菜单"""
        # 获取当前选中文本
        text = self.text_capture.get_selected_text()
        if text:
            self.text_selected.emit(text)
            self.popup_window.show_with_text(text)
        else:
            # 没有选中文本，显示设置窗口
            self._show_settings()
    
    def _on_result(self, feature_type: str, result: str):
        """处理结果"""
        logger.info(f"功能 {feature_type} 处理完成")
        self.popup_window.show_result(result)
    
    def _show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog()
        dialog.exec()
    
    def run(self):
        """运行程序"""
        # 注册热键 (Ctrl+Q)
        if self.hotkey_manager.register_default_hotkey():
            hotkey_text = "Ctrl+Q"
        else:
            hotkey_text = "未注册"
        
        # 显示托盘
        self.tray_icon.show()
        
        # 显示提示
        self.tray_icon.showMessage(
            "划词助手",
            f"程序已启动！选中文字后按 {hotkey_text} 使用",
            self.tray_icon.icon(),
            3000
        )
        
        logger.info(f"划词助手启动运行，热键: {hotkey_text}")
        
        # 主循环
        sys.exit(self.app.exec())


def main():
    """主入口"""
    assistant = WordSelectionAssistant()
    assistant.run()


if __name__ == "__main__":
    main()