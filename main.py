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
from PyQt6.QtWidgets import QApplication, QMessageBox
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
from utils.theme_manager import get_theme_manager, ThemeType
from ai.xiaoma_adapter import XiaomaAdapter
from ai.ollama_adapter import OllamaAdapter
from features.translator import Translator
from features.explainer import Explainer
from features.summarizer import Summarizer
from features.custom_builder import CustomBuilder
from features.chart_generator import ChartGenerator
from features.prompt_optimizer import PromptOptimizer
from utils.logger import setup_logger
from utils.config_loader import get_config


def check_admin_privileges():
    """检查是否具有管理员权限"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def show_admin_warning():
    """显示管理员权限警告"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("权限不足")
    msg.setText("划词助手需要管理员权限才能正常工作")
    msg.setInformativeText("请以管理员身份重新运行此程序，否则热键和文本捕获功能可能无法正常使用。")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

def main():
    """主入口"""
    # 先创建 QApplication
    app = QApplication(sys.argv)

    # 检查管理员权限
    if not check_admin_privileges():
        logger = setup_logger(
            name="WordSelectionAssistant",
            level="WARNING",
            log_file="logs/word_assistant.log"
        )
        logger.warning("程序未以管理员权限运行")
        show_admin_warning()
        # 显示警告后继续运行，但功能可能受限

    # 正常初始化
    logger = setup_logger(
        name="WordSelectionAssistant",
        level="INFO",
        log_file="logs/word_assistant.log"
    )

    assistant = WordSelectionAssistant(app)
    assistant.run()

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

    def __init__(self, app):
        super().__init__()

        # Qt应用
        self.app = app
        self.app.setQuitOnLastWindowClosed(False)

        # 配置 - 使用绝对路径
        config_path = str(PROJECT_ROOT / "config" / "settings.yaml")
        self.config = get_config(config_path)

        # 初始化组件
        self._init_components()
        self._connect_signals()

        # 应用主题设置
        self._apply_theme()

        logger.info("划词助手初始化完成")

    def _init_components(self):
        """初始化组件"""
        # 根据配置选择API适配器
        default_provider = self.config.get('ai', {}).get('default_provider', 'openai')
        
        if default_provider == 'ollama':
            self.ai_adapter = OllamaAdapter(
                api_base=self.config.get('ai', {}).get('ollama', {}).get('api_base'),
            )
            # 设置默认模型
            ollama_model = self.config.get('ai', {}).get('ollama', {}).get('model', 'llama3.2')
            self.ai_adapter.set_model(ollama_model)
            logger.info(f"使用Ollama适配器，模型: {ollama_model}")
        else:  # 默认使用OpenAI兼容API
            self.ai_adapter = XiaomaAdapter()  # 保留向后兼容性
            # 设置默认模型
            openai_model = self.config.get('ai', {}).get('openai', {}).get('model', 'gpt-3.5-turbo')
            self.ai_adapter.set_model(openai_model)
            logger.info(f"使用OpenAI兼容适配器，模型: {openai_model}")

        # 功能模块
        self.translator = Translator(self.ai_adapter)
        self.explainer = Explainer(self.ai_adapter)
        self.summarizer = Summarizer(self.ai_adapter)
        self.custom_builder = CustomBuilder(self.ai_adapter)
        self.prompt_optimizer = PromptOptimizer(self.ai_adapter)

        # 图表生成模块（初始化依赖检查）
        try:
            from features.chart_generator import ChartGenerator
            from utils.chart_code_executor import ChartCodeExecutor
            self.chart_code_executor = ChartCodeExecutor()
            self.chart_generator = ChartGenerator(self.ai_adapter, self.chart_code_executor)
            logger.info("图表功能已初始化")
        except ImportError as e:
            logger.warning(f"图表功能初始化失败（依赖缺失）: {e}")
            self.chart_generator = None

        # 核心组件
        self.hotkey_manager = HotkeyManager()
        self.text_capture = TextCapture()
        self.function_router = FunctionRouter()

        # 注册功能处理器
        self.function_router.register_handler(FunctionType.TRANSLATE, self.translator.translate)
        self.function_router.register_handler(FunctionType.EXPLAIN, self.explainer.explain)
        self.function_router.register_handler(FunctionType.SUMMARIZE, self.summarizer.summarize)

        # 注册图表处理器（如果可用）
        if self.chart_generator:
            self.function_router.register_handler(FunctionType.CHART, self.chart_generator.generate_chart)
            logger.info("图表处理器已注册到路由器")

        # 注册提示词优化处理器
        self.function_router.register_handler(FunctionType.OPTIMIZE, self.prompt_optimizer.optimize)
        logger.info("提示词优化处理器已注册到路由器")

        # UI组件
        self.tray_icon = TrayIcon()
        self.popup_window = PopupWindow(
            self.translator,
            self.explainer,
            self.summarizer,
            custom_builder=self.custom_builder,
            chart_generator=self.chart_generator,
            prompt_optimizer=self.prompt_optimizer
        )

        # 集成配置到UI组件
        self._apply_ui_config()

        # 打印功能可用性状态
        self._log_capabilities()

    def _apply_theme(self):
        """应用主题设置"""
        theme_manager = get_theme_manager()
        saved_theme = theme_manager.load_theme_preference()
        theme_manager.set_theme(saved_theme, self.app)

    def _apply_ui_config(self):
        """应用UI配置"""
        # 从配置中读取流式输出设置
        enable_stream = self.config.get('ai', {}).get('api', {}).get('enable_stream', False)

        # 应用到 PopupWindow
        self.popup_window.enable_stream = enable_stream

        logger.info(f"流式输出配置: {'启用' if enable_stream else '禁用'}")

    def _log_capabilities(self):
        """记录功能可用性状态"""
        logger.info("=== 功能可用性检查 ===")

        # 基础功能
        logger.info(f"翻译功能: {'可用' if self.translator else '不可用'}")
        logger.info(f"解释功能: {'可用' if self.explainer else '不可用'}")
        logger.info(f"总结功能: {'可用' if self.summarizer else '不可用'}")
        logger.info(f"自定义功能: {'可用' if self.custom_builder else '不可用'}")
        logger.info(f"图表功能: {'可用' if self.chart_generator else '不可用'}")
        logger.info(f"提示词优化功能: {'可用' if self.prompt_optimizer else '不可用'}")

        logger.info("=== 功能检查完成 ===")

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
        try:
            logger.info("热键被触发，获取选中文本...")

            # 获取当前选中文本
            text = self.text_capture.get_selected_text()
            if text:
                logger.info(f"文本获取成功: {len(text)} 字符")
                self.popup_window.show_with_text(text)
            else:
                logger.warning("没有选中文本")

        except Exception as e:
            logger.error(f"热键处理失败: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())

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
        self.popup_window._update_result(result)

    def _show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog()
        dialog.exec()

    def run(self):
        """运行程序"""
        try:
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
        except Exception as e:
            logger.error(f"程序运行时发生未捕获的异常: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            sys.exit(1)


if __name__ == "__main__":
    main()