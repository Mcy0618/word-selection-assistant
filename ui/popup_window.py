#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悬浮弹窗
显示功能选择和结果
"""

import logging
import asyncio
import threading
import os
import time
from typing import Callable
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QTextEdit, QFrame, QApplication,
                              QFileDialog, QMessageBox, QProgressBar, QDialog,
                              QComboBox, QLineEdit)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QCursor, QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, pyqtSlot, QRectF
from utils.event_loop_manager import EventLoopManager
from utils.thread_pool_manager import get_thread_pool_manager
from utils.settings_manager import get_settings_manager
from utils.config_manager import get_config_manager

# type: ignore[attr-defined, arg-type]

logger = logging.getLogger(__name__)


class PopupWindow(QWidget):
    """悬浮弹窗"""

    # 定义信号用于线程间通信
    stream_chunk = pyqtSignal(str)  # 流式数据块
    stream_complete = pyqtSignal()  # 流式完成
    stream_error = pyqtSignal(str)  # 流式错误

    def __init__(self, translator=None, explainer=None, summarizer=None,
                 custom_builder=None, chart_generator=None, prompt_optimizer=None,
                 question_asker=None):
        """
        初始化弹窗

        Args:
            translator: 翻译功能实例
            explainer: 解释功能实例
            summarizer: 总结功能实例
            custom_builder: 自定义功能构建器实例
            chart_generator: 图表生成功能实例
            prompt_optimizer: 提示词优化功能实例
            question_asker: 提问功能实例
        """
        super().__init__()

        # 功能模块引用
        self.translator = translator
        self.explainer = explainer
        self.summarizer = summarizer
        self.custom_builder = custom_builder
        self.chart_generator = chart_generator
        self.prompt_optimizer = prompt_optimizer
        self.question_asker = question_asker

        # 当前问题（用于提问功能）
        self.current_question = ""

        # 当前文本
        self.current_text = ""

        # 图表相关状态
        self.current_chart_path = None
        self.chart_scale_factor = 1.0  # 图片缩放比例
        self.max_chart_height = 300  # 图表最大高度

        # 配置管理器
        self.config_manager = get_config_manager()

        # 自定义设置
        self.custom_settings = self.config_manager.get_settings()

        # 流式输出状态
        self.is_streaming = False

        # 窗口固定状态
        self.is_pinned = False

        # 对话模式状态
        self.is_chat_mode = False  # 是否处于连续对话模式
        self.chat_history = []  # 对话历史

        # 初始化自动隐藏定时器
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self._on_auto_hide)

        # 连接信号
        self.stream_chunk.connect(self._on_stream_chunk)
        self.stream_complete.connect(self._on_stream_complete)
        self.stream_error.connect(self._on_stream_error)
        self.enable_stream = False  # 从配置加载

        # 监听设置变更
        self._connect_to_settings()

        # UI
        self._setup_ui()
        self._setup_styles()

    def _connect_to_settings(self):
        """连接到设置变更信号"""
        settings_manager = get_settings_manager()

        # 监听流式输出设置变更
        self._stream_setting_conn = settings_manager.connect_to_setting(
            'ai.api.enable_stream',
            self._on_stream_setting_changed
        )

        # 监听主题设置变更
        self._theme_setting_conn = settings_manager.connect_to_setting(
            'app.theme',
            self._on_theme_setting_changed
        )

        logger.debug("已连接到设置变更信号")

    def _on_stream_setting_changed(self, key: str, value: bool):
        """流式输出设置变更处理"""
        self.enable_stream = value
        logger.info(f"流式输出设置变更: {key} = {value}")

    def _on_theme_setting_changed(self, key: str, value: str):
        """主题设置变更处理"""
        logger.info(f"主题设置变更: {key} = {value}")
        # 主题变更由主应用统一处理

    def _setup_ui(self):
        """设置UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        # 主卡片
        self.card = QFrame(self)
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        # 标题
        self.title_label = QLabel("划词助手")
        self.title_label.setObjectName("title")
        card_layout.addWidget(self.title_label)

        # 选中文本预览
        self.preview_label = QLabel("请选中要处理的文本")
        self.preview_label.setObjectName("preview")
        self.preview_label.setWordWrap(True)
        self.preview_label.setMaximumHeight(60)
        card_layout.addWidget(self.preview_label)

        # 功能按钮区域
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(8)

        # 创建功能按钮
        self.btn_translate = self._create_button("🔤 翻译", "translate")
        self.btn_explain = self._create_button("💡 解释", "explain")
        self.btn_summarize = self._create_button("📝 总结", "summarize")
        self.btn_chart = self._create_button("📊 绘图", "chart")
        self.btn_optimize = self._create_button("✨ 优化", "optimize")
        self.btn_custom = self._create_button("⚙️ 自定义", "custom")
        self.btn_ask = self._create_button("❓ 提问", "ask")

        self.buttons_layout.addWidget(self.btn_translate)
        self.buttons_layout.addWidget(self.btn_explain)
        self.buttons_layout.addWidget(self.btn_summarize)
        self.buttons_layout.addWidget(self.btn_chart)
        self.buttons_layout.addWidget(self.btn_optimize)
        self.buttons_layout.addWidget(self.btn_custom)
        self.buttons_layout.addWidget(self.btn_ask)

        # 级别选择按钮（仅当检测到Python代码时显示）
        self.btn_level_beginner = QPushButton("初学者")
        self.btn_level_beginner.setObjectName("btn_level_beginner")
        self.btn_level_beginner.setVisible(False)
        self.btn_level_beginner.clicked.connect(lambda: self._on_level_changed("beginner"))
        self.buttons_layout.addWidget(self.btn_level_beginner)

        self.btn_level_default = QPushButton("默认")
        self.btn_level_default.setObjectName("btn_level_default")
        self.btn_level_default.setVisible(False)
        self.btn_level_default.clicked.connect(lambda: self._on_level_changed("default"))
        self.buttons_layout.addWidget(self.btn_level_default)

        self.btn_level_advanced = QPushButton("高级")
        self.btn_level_advanced.setObjectName("btn_level_advanced")
        self.btn_level_advanced.setVisible(False)
        self.btn_level_advanced.clicked.connect(lambda: self._on_level_changed("advanced"))
        self.buttons_layout.addWidget(self.btn_level_advanced)

        # 默认级别
        self.current_level = "default"

        card_layout.addLayout(self.buttons_layout)

        # 自定义功能设置按钮
        self.btn_settings = QPushButton("⚙️ 自定义设置")
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.clicked.connect(self._show_custom_settings)
        card_layout.addWidget(self.btn_settings, alignment=Qt.AlignmentFlag.AlignRight)

        # 进度指示区域（初始隐藏）
        self.progress_container = QWidget()
        self.progress_container.setObjectName("progress_container")
        self.progress_container.setVisible(False)
        progress_layout = QHBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 5, 0, 5)
        progress_layout.setSpacing(10)

        # 加载动画标签（使用旋转图标）
        self.loading_icon = QLabel()
        self.loading_icon.setObjectName("loading_icon")
        self.loading_icon.setFixedSize(16, 16)
        self.loading_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.loading_icon)

        # 进度条（不确定进度模式）
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setMinimumHeight(6)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        card_layout.addWidget(self.progress_container)

        # 结果区域（初始隐藏）
        self.result_frame = QFrame()
        self.result_frame.setObjectName("result_frame")
        self.result_frame.setVisible(False)
        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(5)

        # 结果文本框（支持代码块）
        self.result_text = QTextEdit()
        self.result_text.setObjectName("result")
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        result_layout.addWidget(self.result_text)

        # 图表显示区域（初始隐藏）
        self.chart_container = QWidget()
        self.chart_container.setObjectName("chart_container")
        self.chart_container.setVisible(False)
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(5)

        # 图表图片标签
        self.chart_image_label = QLabel()
        self.chart_image_label.setObjectName("chart_image")
        self.chart_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_image_label.setMinimumHeight(100)
        self.chart_image_label.setMaximumHeight(self.max_chart_height)
        chart_layout.addWidget(self.chart_image_label)

        # 图表控制栏
        self.chart_controls = QHBoxLayout()
        self.chart_controls.setSpacing(10)

        # 缩放按钮
        self.btn_chart_zoom_in = QPushButton("🔍+")
        self.btn_chart_zoom_in.setObjectName("btn_chart_zoom_in")
        self.btn_chart_zoom_in.setFixedSize(32, 28)
        self.btn_chart_zoom_in.clicked.connect(self._on_chart_zoom_in)
        self.chart_controls.addWidget(self.btn_chart_zoom_in)

        self.btn_chart_zoom_out = QPushButton("🔍-")
        self.btn_chart_zoom_out.setObjectName("btn_chart_zoom_out")
        self.btn_chart_zoom_out.setFixedSize(32, 28)
        self.btn_chart_zoom_out.clicked.connect(self._on_chart_zoom_out)
        self.chart_controls.addWidget(self.btn_chart_zoom_out)

        self.btn_chart_reset = QPushButton("🔍100%")
        self.btn_chart_reset.setObjectName("btn_chart_reset")
        self.btn_chart_reset.setFixedSize(50, 28)
        self.btn_chart_reset.clicked.connect(self._on_chart_reset)
        self.chart_controls.addWidget(self.btn_chart_reset)

        # 缩放比例标签
        self.chart_scale_label = QLabel("100%")
        self.chart_scale_label.setObjectName("chart_scale_label")
        self.chart_scale_label.setMinimumWidth(40)
        self.chart_controls.addWidget(self.chart_scale_label)

        self.chart_controls.addStretch()

        # 保存图表按钮
        self.btn_chart_save = QPushButton("💾 保存")
        self.btn_chart_save.setObjectName("btn_chart_save")
        self.btn_chart_save.clicked.connect(self._on_chart_save)
        self.chart_controls.addWidget(self.btn_chart_save)

        chart_layout.addLayout(self.chart_controls)

        result_layout.addWidget(self.chart_container)

        # 复制按钮和固定按钮容器
        result_buttons_layout = QHBoxLayout()

        # 固定按钮
        self.btn_pin = QPushButton("📌 固定")
        self.btn_pin.setObjectName("btn_pin")
        self.btn_pin.setVisible(False)
        self.btn_pin.setCheckable(True)
        self.btn_pin.clicked.connect(self._on_pin_clicked)
        result_buttons_layout.addWidget(self.btn_pin)

        result_buttons_layout.addStretch()

        # 复制按钮
        self.btn_copy = QPushButton("📋 复制")
        self.btn_copy.setObjectName("btn_copy")
        self.btn_copy.setVisible(False)
        self.btn_copy.clicked.connect(self._copy_result)
        result_buttons_layout.addWidget(self.btn_copy)

        result_layout.addLayout(result_buttons_layout)

        card_layout.addWidget(self.result_frame)

        # 关闭按钮
        close_layout = QHBoxLayout()
        close_layout.addStretch()

        self.btn_close = QPushButton("关闭")
        self.btn_close.setObjectName("close")
        self.btn_close.clicked.connect(self.hide)
        close_layout.addWidget(self.btn_close)

        card_layout.addLayout(close_layout)

        self.layout.addWidget(self.card)

    def _create_button(self, text: str, feature_type: str) -> QPushButton:
        """创建功能按钮"""
        btn = QPushButton(text)
        btn.setObjectName(f"btn_{feature_type}")

        # 连接功能按钮点击事件
        btn.clicked.connect(lambda: self._on_feature_clicked(feature_type))

        return btn

    def _setup_styles(self):
        """设置样式"""
        self.setStyleSheet("""
            PopupWindow {
                background: transparent;
            }
            #card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid rgba(200, 200, 200, 0.5);
            }
            #title {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            #preview {
                font-size: 13px;
                color: #666;
                background: #f5f5f5;
                padding: 8px;
                border-radius: 6px;
            }
            #btn_translate, #btn_explain, #btn_summarize, #btn_chart, #btn_custom {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                background: #f8f8f8;
                font-size: 12px;
            }
            #btn_translate:hover, #btn_explain:hover, #btn_summarize:hover, #btn_chart:hover, #btn_custom:hover {
                background: #e8e8e8;
            }
            #result_frame {
                background: #f0f7ff;
                border-radius: 8px;
                padding: 10px;
            }
            #result {
                font-size: 13px;
                color: #333;
            }
            #close {
                background: transparent;
                border: none;
                color: #999;
                font-size: 12px;
            }
            #close:hover {
                color: #666;
            }
            #progress_container {
                background: transparent;
            }
            #loading_icon {
                qproperty-alignment: AlignCenter;
            }
            #progress_bar {
                border: none;
                background-color: #e0e0e0;
                border-radius: 3px;
                min-height: 6px;
                max-height: 6px;
            }
            #progress_bar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #007bff, stop:1 #00d4ff);
                border-radius: 3px;
                width: 20px;
            }
            #chart_container {
                background: #ffffff;
                border-radius: 8px;
                padding: 5px;
            }
            #chart_image {
                background: transparent;
            }
            #btn_chart_zoom_in, #btn_chart_zoom_out, #btn_chart_reset, #btn_chart_save {
                padding: 4px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f0f0f0;
                font-size: 11px;
            }
            #btn_chart_zoom_in:hover, #btn_chart_zoom_out:hover, #btn_chart_reset:hover, #btn_chart_save:hover {
                background: #e0e0e0;
            }
            #chart_scale_label {
                font-size: 11px;
                color: #666;
            }
        """)

    def show_with_text(self, text: str):
        """显示弹窗并设置文本"""
        if not text or not text.strip():
            return

        self.current_text = text.strip()
        self.preview_label.setText(self.current_text[:100] + "..." if len(self.current_text) > 100 else self.current_text)

        # 重置结果区域
        self.result_frame.setVisible(False)
        self.result_text.setPlainText("")
        self.btn_copy.setVisible(False)

        # 重置固定按钮和状态
        self.btn_pin.setVisible(False)
        self.btn_pin.setChecked(False)
        self.btn_pin.setText("📌 固定")
        self.is_pinned = False

        # 重置对话模式
        self.is_chat_mode = False
        self.chat_history = []
        self.current_question = ""
        # 清空提问器的对话历史
        if self.question_asker:
            self.question_asker.clear_history()

        # 显示窗口
        self._position_at_cursor()
        self.show()

        # 停止自动隐藏计时器（不再自动隐藏）
        self.hide_timer.stop()

    def show_with_screenshot(self, image_path: str):
        """显示弹窗（截图功能已移除）"""
        # 显示功能已移除的消息
        preview_text = "❌ 截图功能已移除\n\n请选中文字后使用 Ctrl+Q 或托盘菜单"
        self.preview_label.setText(preview_text)

        # 重置结果区域
        self.result_frame.setVisible(False)
        self.result_text.setPlainText("")
        self.btn_copy.setVisible(False)

        # 重置固定按钮和状态
        self.btn_pin.setVisible(False)
        self.btn_pin.setChecked(False)
        self.btn_pin.setText("📌 固定")
        self.is_pinned = False

        # 显示窗口
        self._position_at_cursor()
        self.show()

        # 停止自动隐藏计时器（不再自动隐藏）
        self.hide_timer.stop()

        logger.info("截图功能已移除，显示提示信息")

    def _position_at_cursor(self):
        """定位到鼠标位置"""
        cursor_pos = QCursor.pos()
        x = cursor_pos.x() + 20
        y = cursor_pos.y() + 20

        # 确保不超出屏幕
        screen = QApplication.primaryScreen().geometry() # pyright: ignore[reportOptionalMemberAccess]
        if x + self.width() > screen.width():
            x = screen.width() - self.width() - 20
        if y + self.height() > screen.height():
            y = screen.height() - self.height() - 20

        self.move(x, y)

    def _on_feature_clicked(self, feature_type: str):
        """功能按钮点击"""
        logger.info(f"用户选择功能: {feature_type}")

        # 停止自动隐藏定时器（特别是图表生成需要较长时间）
        self.hide_timer.stop()

        # 显示进度指示器
        self.progress_container.setVisible(True)
        self._start_loading_animation()

        # 显示加载状态
        self.result_frame.setVisible(True)
        self.result_text.setPlainText("处理中...")
        self._apply_plain_style()

        # 隐藏图表容器，显示文本区域
        self.chart_container.setVisible(False)
        self.result_text.setVisible(True)

        # 检测是否为Python代码（仅对解释功能）
        if self._is_python_code(self.current_text) and feature_type == "explain":
            # 显示级别选择按钮
            self.btn_level_beginner.setVisible(True)
            self.btn_level_default.setVisible(True)
            self.btn_level_advanced.setVisible(True)
            # 设置默认级别样式
            self.btn_level_default.setStyleSheet("background-color: #007bff; color: white;")
        else:
            # 隐藏级别选择按钮
            self.btn_level_beginner.setVisible(False)
            self.btn_level_default.setVisible(False)
            self.btn_level_advanced.setVisible(False)

        # 特殊处理提问功能
        if feature_type == "ask":
            self._on_ask_clicked()
            return

        # 根据配置选择流式或非流式
        streamable_types = ["translate", "explain", "summarize", "custom"]
        if self.enable_stream and feature_type in streamable_types:
            QTimer.singleShot(0, lambda: self._process_text_stream(feature_type))
        else:
            QTimer.singleShot(0, lambda: self._process_text_sync(feature_type))

    def _process_text_sync(self, feature_type: str):
        """同步处理文本 - 使用线程池避免UI卡顿"""
        def run_task():
            try:
                thread_manager = get_thread_pool_manager()

                def execute_feature():
                    """在线程中执行功能"""
                    import asyncio

                    async def async_task():
                        if feature_type == "translate":
                            if self.translator:
                                return await self.translator.translate(self.current_text)
                            return f"[模拟翻译] {self.current_text}"
                        elif feature_type == "explain":
                            if self.explainer:
                                return await self.explainer.explain(self.current_text)
                            return f"[模拟解释] {self.current_text}"
                        elif feature_type == "summarize":
                            if self.summarizer:
                                return await self.summarizer.summarize(self.current_text)
                            return f"[模拟总结] {self.current_text}"
                        elif feature_type == "chart":
                            if self.chart_generator:
                                return await self.chart_generator.generate_chart(self.current_text)
                            return {"error": "图表功能未初始化"}
                        elif feature_type == "custom":
                            custom_prompt = self.custom_settings.get('prompt_template', "请对以下内容进行自定义处理：\n\n{text}")
                            processed_prompt = custom_prompt.replace("{text}", self.current_text)
                            custom_model = self.custom_settings.get('model', 'qwen3-32b')
                            if self.custom_builder:
                                return await self.custom_builder.execute(processed_prompt, model=custom_model)
                            return f"[模拟自定义] {processed_prompt}"
                        elif feature_type == "optimize":
                            if self.prompt_optimizer:
                                return await self.prompt_optimizer.optimize(self.current_text)
                            return f"[模拟优化] {self.current_text}"
                        else:
                            return f"未知功能: {feature_type}"

                    # 使用 asyncio.run() 执行
                    return asyncio.run(async_task())

                # 提交到线程池（不阻塞主线程）
                future = thread_manager.submit(execute_feature)

                def check_result():
                    """检查任务是否完成，使用 QTimer 轮询，避免阻塞"""
                    try:
                        # 使用 nowait 避免阻塞
                        result = future.result(timeout=0.1)
                        # 任务完成，在主线程中更新UI
                        QTimer.singleShot(0, lambda: self._update_result(result))
                    except Exception as e:
                        # 任务仍在进行中，继续等待
                        error = e
                        if "Timeout" in str(type(e).__name__) or "TimeoutError" in str(type(e).__name__):
                            # 任务仍在进行，设置下一个检查
                            QTimer.singleShot(100, check_result)
                        else:
                            # 真正出错
                            error_msg = f"处理失败: {e}"
                            logger.error(f"处理失败: {e}", exc_info=True)
                            QTimer.singleShot(0, lambda: self._update_result(error_msg))

                # 开始异步检查任务状态
                QTimer.singleShot(0, check_result)

            except Exception as e:
                error_msg = f"处理失败: {e}"
                logger.error(f"处理失败: {e}", exc_info=True)
                self._update_result(error_msg)

        # 使用 QTimer.singleShot 在主线程中执行
        QTimer.singleShot(0, run_task)

    @pyqtSlot(str)
    def _update_result(self, result):
        """更新结果到UI（在主线程中调用）"""
        # 隐藏进度指示器
        self.progress_container.setVisible(False)
        self._stop_loading_animation()

        # 处理图表结果（Dict 类型）
        if isinstance(result, dict):
            if "error" in result:
                self.result_text.setVisible(True)
                self.chart_container.setVisible(False)
                self.result_text.setPlainText(f"错误: {result['error']}")
                self._apply_plain_style()
                return

            if "image_path" in result:
                # 显示图表
                self._display_chart(result["image_path"], result.get("description", ""))
                return

        # 处理普通文本结果
        if isinstance(result, str):
            self.result_text.setVisible(True)
            self.chart_container.setVisible(False)
            self.result_text.setPlainText(result)

            # 根据内容类型应用样式
            if self._is_code(result):
                self._apply_code_style()
            else:
                self._apply_plain_style()
        else:
            logger.warning(f"未知的结果类型: {type(result)}")
            self.result_text.setVisible(True)
            self.chart_container.setVisible(False)
            self.result_text.setPlainText(f"无法处理的结果类型: {type(result)}")

        # 显示固定按钮
        self.btn_pin.setVisible(True)
        # 禁用自动隐藏
        self.hide_timer.stop()

    @pyqtSlot(str)
    def _on_stream_chunk(self, content: str):
        """处理流式数据块（在主线程中调用）"""
        if not self.is_streaming:
            return

        cursor = self.result_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(content)
        self.result_text.setTextCursor(cursor)

        # 自动滚动到底部
        scrollbar = self.result_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # 显示复制按钮
        self.btn_copy.setVisible(True)

    @pyqtSlot()
    def _on_stream_complete(self):
        """流式完成（在主线程中调用）"""
        self.is_streaming = False
        logger.info("流式处理完成")

        # 隐藏进度指示器
        self.progress_container.setVisible(False)
        self._stop_loading_animation()

        # 检测是否为代码并应用样式
        result_text = self.result_text.toPlainText()
        if self._is_code(result_text):
            self._apply_code_style()
        else:
            self._apply_plain_style()

        # 显示固定按钮
        self.btn_pin.setVisible(True)

        # 在对话模式下，添加继续对话的提示
        if self.is_chat_mode:
            # 显示对话轮数
            round_num = len(self.chat_history)
            self.result_text.append(f"\n\n--- 第{round_num}轮对话结束 ---")
            self.result_text.append("点击 ❓ 提问 按钮继续对话，或选择其他功能")

        # 禁用自动隐藏
        self.hide_timer.stop()

    @pyqtSlot(str)
    def _on_stream_error(self, error: str):
        """流式错误（在主线程中调用）"""
        self.is_streaming = False
        self.result_text.append(f"\n[错误] {error}")

        # 隐藏进度指示器
        self.progress_container.setVisible(False)
        self._stop_loading_animation()

        # 显示固定按钮
        self.btn_pin.setVisible(True)

        # 禁用自动隐藏
        self.hide_timer.stop()
    def _call_feature_api(self, feature_type: str) -> str:
        """调用特定功能的API"""
        try:
            if feature_type == "translate":
                # 使用同步版本的翻译
                return self._handle_translate_sync()
            elif feature_type == "explain":
                # 使用同步版本的解释
                return self._handle_explain_sync()
            elif feature_type == "summarize":
                # 使用同步版本的总结
                return self._handle_summarize_sync()
            else:
                return f"未知功能: {feature_type}"
        except Exception as e:
            logger.error(f"API调用失败: {e}", exc_info=True)
            return f"处理失败: {e}"

    def _handle_translate_sync(self) -> str:
        """处理翻译请求（同步）- 使用线程池避免UI卡顿"""
        if self.translator:
            try:
                # 使用线程池在后台执行阻塞操作
                thread_manager = get_thread_pool_manager()

                def run_translation():
                    """在线程中运行的翻译任务"""
                    try:
                        return EventLoopManager.run_in_loop(
                            self.translator.translate(self.current_text)
                        )
                    except Exception as e:
                        logger.error(f"翻译失败: {e}", exc_info=True)
                        raise e

                future = thread_manager.submit(run_translation)
                return future.result(timeout=30)
            except Exception as e:
                logger.error(f"翻译失败: {e}", exc_info=True)
                return f"翻译失败: {e}"
        else:
            return f"[模拟翻译] {self.current_text}"

    def _handle_explain_sync(self) -> str:
        """处理解释请求（同步）- 使用线程池避免UI卡顿"""
        if self.explainer:
            try:
                # 使用线程池在后台执行阻塞操作
                thread_manager = get_thread_pool_manager()

                def run_explanation():
                    """在线程中运行的解释任务"""
                    try:
                        return EventLoopManager.run_in_loop(
                            self.explainer.explain(self.current_text)
                        )
                    except Exception as e:
                        logger.error(f"解释失败: {e}", exc_info=True)
                        raise e

                future = thread_manager.submit(run_explanation)
                return future.result(timeout=30)
            except Exception as e:
                logger.error(f"解释失败: {e}", exc_info=True)
                return f"解释失败: {e}"
        else:
            return f"[模拟解释] {self.current_text}"

    def _handle_summarize_sync(self) -> str:
        """处理总结请求（同步）- 使用线程池避免UI卡顿"""
        if self.summarizer:
            try:
                # 使用线程池在后台执行阻塞操作
                thread_manager = get_thread_pool_manager()

                def run_summarization():
                    """在线程中运行的总结任务"""
                    try:
                        return EventLoopManager.run_in_loop(
                            self.summarizer.summarize(self.current_text)
                        )
                    except Exception as e:
                        logger.error(f"总结失败: {e}", exc_info=True)
                        raise e

                future = thread_manager.submit(run_summarization)
                return future.result(timeout=30)
            except Exception as e:
                logger.error(f"总结失败: {e}", exc_info=True)
                return f"总结失败: {e}"
        else:
            return f"[模拟总结] {self.current_text}"

    async def _handle_translate_async(self) -> str:
        """处理翻译请求（异步）"""
        if self.translator:
            return await self.translator.translate(self.current_text)
        else:
            return f"[模拟翻译] {self.current_text}"

    async def _handle_explain_async(self) -> str:
        """处理解释请求（异步）"""
        if self.explainer:
            return await self.explainer.explain(self.current_text)
        else:
            return f"[模拟解释] {self.current_text}"

    async def _handle_summarize_async(self) -> str:
        """处理总结请求（异步）"""
        if self.summarizer:
            return await self.summarizer.summarize(self.current_text)
        else:
            return f"[模拟总结] {self.current_text}"

    def _is_code(self, text: str) -> bool:
        """检测文本是否为代码"""
        import re
        code_patterns = [
            r'\bdef\s+\w+\s*\(',
            r'\bfunction\s+\w+\s*\(',
            r'\bclass\s+\w+\s*[:{]',
            r'\{[\s\S]*\}',
            r'=>\s*[{]',
            r'\bif\s+\w+\s*:',
            r'\bfor\s+\w+\s*:',
            r'\bwhile\s+\w+\s*:',
            r'\bimport\s+\w+',
            r'\bfrom\s+\w+\s+import',
            r'\breturn\s+',
            r'console\.log\(',
            r'print\(',
            r'System\.out\.println',
        ]

        for pattern in code_patterns:
            if re.search(pattern, text):
                return True

        # 检查缩进和特殊字符密度
        lines = text.split('\n')
        if len(lines) > 1:
            indented_lines = sum(1 for line in lines if line.startswith(('    ', '\t', '  ')))
            if indented_lines > len(lines) * 0.3:
                return True

        return False

    def _is_python_code(self, text: str) -> bool:
        """检测文本是否为Python代码"""
        import re

        python_patterns = [
            r'\bdef\s+\w+\s*\(',  # 函数定义
            r'\bclass\s+\w+\s*:',  # 类定义
            r'\bimport\s+\w+',  # import语句
            r'\bfrom\s+\w+\s+import',  # from import
            r'\bprint\s*\(',  # print函数
            r'\bif\s+.*:',  # if语句
            r'\bfor\s+.*:',  # for循环
            r'\bwhile\s+.*:',  # while循环
            r'\breturn\s+',  # return语句
            r'\btry\s*:',  # try语句
            r'\bexcept\s+',  # except语句
            r'\bwith\s+.*:',  # with语句
            r'\basync\s+def\s+',  # 异步函数
            r'\bawait\s+',  # await表达式
            r'->\s*\w+',  # 类型注解
        ]

        for pattern in python_patterns:
            if re.search(pattern, text):
                return True

        # 检查Python特有的缩进结构
        lines = text.split('\n')
        if len(lines) > 1:
            # 检查是否有4空格缩进（Python标准）
            indented_lines = sum(1 for line in lines if line.startswith('    '))
            if indented_lines >= len(lines) * 0.3:
                return True

        return False

    def _on_ask_clicked(self):
        """提问按钮点击处理 - 支持连续对话"""
        # 首次进入对话模式时设置上下文
        if not self.is_chat_mode:
            self.is_chat_mode = True
            # 清空之前的对话历史
            self.chat_history = []
            # 设置上下文到提问器
            if self.question_asker:
                self.question_asker.set_context(self.current_text)

        # 显示对话输入对话框
        self._show_chat_dialog()

    def _show_chat_dialog(self):
        """显示连续对话输入对话框"""
        from PyQt6.QtWidgets import QInputDialog, QLineEdit

        # 构建对话框标题，显示当前是第几轮对话
        round_num = len(self.chat_history) + 1
        title = f"连续对话 - 第{round_num}轮"

        # 弹出输入对话框
        question, ok = QInputDialog.getText(
            self,
            title,
            f"请输入您的问题（基于选中的{len(self.current_text)}字符文本）：",
            QLineEdit.EchoMode.Normal,
            self.current_question
        )

        if ok and question.strip():
            self.current_question = question.strip()
            logger.info(f"用户第{round_num}轮提问: {self.current_question}")

            # 显示进度指示器
            self.progress_container.setVisible(True)
            self._start_loading_animation()

            # 显示加载状态
            self.result_frame.setVisible(True)
            self.result_text.setPlainText("思考中...")
            self._apply_plain_style()

            # 隐藏图表容器，显示文本区域
            self.chart_container.setVisible(False)
            self.result_text.setVisible(True)

            # 使用流式处理
            QTimer.singleShot(0, lambda: self._process_ask_stream())
        else:
            # 用户取消，如果已经有对话历史则保持在对话模式
            if not self.chat_history:
                self.is_chat_mode = False
                self.progress_container.setVisible(False)
                self._stop_loading_animation()

    def _apply_code_style(self):
        """应用代码块样式（浅色主题）"""
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                color: #333333;
                font-family: Consolas, "Cascadia Code", "Fira Code", "Microsoft YaHei Mono", monospace;
                font-size: 13px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 8px;
                line-height: 1.5;
            }
        """)
        self.result_frame.setStyleSheet("""
            #result_frame {
                background: #f8f8f8;
                border: 1px dashed #ccc;
                border-radius: 8px;
                padding: 8px;
            }
        """)

    def _apply_plain_style(self):
        """应用普通文本样式"""
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f7ff;
                color: #333333;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                font-size: 13px;
                border-radius: 6px;
                padding: 8px;
                line-height: 1.5;
            }
        """)
        self.result_frame.setStyleSheet("""
            #result_frame {
                background: #f0f7ff;
                border-radius: 8px;
                padding: 10px;
            }
        """)

    def _start_loading_animation(self):
        """开始加载动画"""
        # 使用 QTimer 创建旋转动画效果
        self.loading_angle = 0
        if hasattr(self, 'loading_timer') and self.loading_timer is not None:
            self.loading_timer.stop()
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self._update_loading_animation)
        self.loading_timer.start(50)  # 每50ms更新一次
        logger.debug("加载动画已启动")

    def _start_streaming_indicator(self):
        """开始流式输出指示器"""
        # 在结果文本框顶部显示流式输出状态
        self.result_text.setPlainText("🔄 正在接收流式输出...")
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #fff8e6;
                color: #333333;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                font-size: 13px;
                border-radius: 6px;
                padding: 8px;
                line-height: 1.5;
            }
        """)
        logger.debug("流式输出指示器已启动")

    def _update_loading_animation(self):
        """更新加载动画"""
        self.loading_angle = (self.loading_angle + 15) % 360
        # 绘制旋转的加载图标
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#007bff"))
        pen.setWidth(2)
        painter.setPen(pen)

        # 绘制圆弧
        rect = QRectF(2, 2, 12, 12)
        start_angle = self.loading_angle * 16
        painter.drawArc(rect, start_angle, 90 * 16)
        painter.end()

        self.loading_icon.setPixmap(pixmap)

    def _stop_loading_animation(self):
        """停止加载动画"""
        if hasattr(self, 'loading_timer') and self.loading_timer.isActive():
            self.loading_timer.stop()
        self.loading_icon.clear()

    def _copy_result(self):
        """复制结果到剪贴板"""
        text = self.result_text.toPlainText()
        QApplication.clipboard().setText(text) # pyright: ignore[reportOptionalMemberAccess]

        # 显示复制成功提示
        self.btn_copy.setText("✅ 已复制")
        # 2秒后恢复
        QTimer.singleShot(2000, lambda: self.btn_copy.setText("📋 复制"))

    def _on_pin_clicked(self):
        """固定按钮点击 - 现在仅作为视觉提示，窗口始终固定"""
        self.is_pinned = self.btn_pin.isChecked()
        if self.is_pinned:
            self.btn_pin.setText("🔓 取消固定")
            logger.info("窗口已固定")
        else:
            self.btn_pin.setText("📌 固定")
            logger.info("窗口已取消固定")

        # 显示复制成功反馈
        self.btn_copy.setText("✅ 已复制")

        # 2秒后恢复
        QTimer.singleShot(2000, lambda: self.btn_copy.setText("📋 复制"))

    def _on_auto_hide(self):
        """自动隐藏"""
        self.hide()

    def mousePressEvent(self, event): # pyright: ignore[reportIncompatibleMethodOverride]
        """鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.pos()
            self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseMoveEvent(self, event): # pyright: ignore[reportIncompatibleMethodOverride]
        """鼠标移动"""
        if self.dragging:
            self.move(self.pos() + event.pos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event): # pyright: ignore[reportIncompatibleMethodOverride]
        """鼠标释放"""
        self.dragging = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def enterEvent(self, event):
        """鼠标进入"""
        self.hide_timer.stop()

    def leaveEvent(self, event): # pyright: ignore[reportIncompatibleMethodOverride]
        """鼠标离开 - 不再自动隐藏"""
        # 完全禁用自动隐藏，保持窗口显示
        pass

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查拖拽的文件是否为图片
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """拖拽释放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                    # 执行OCR识别
                    self._perform_ocr_from_file(file_path)
                    event.acceptProposedAction()
                    return
        event.ignore()

    def _perform_ocr_from_file(self, file_path: str):
        """从文件执行OCR识别（已移除）"""
        # 此功能已移除
        pass

    @pyqtSlot(str)
    def _update_ocr_result(self, result: str):
        """更新OCR结果到UI（已移除）"""
        # 此功能已移除
        pass

    def _show_custom_settings(self):
        """显示自定义功能设置"""
        # 创建设置对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("自定义功能设置")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # 标题
        title_label = QLabel("自定义功能配置")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 提示词模板配置
        template_label = QLabel("提示词模板:")
        layout.addWidget(template_label)

        self.custom_prompt = QTextEdit()
        self.custom_prompt.setPlainText("请对以下内容进行自定义处理：\n\n{text}")
        self.custom_prompt.setPlaceholderText("在这里输入自定义提示词，使用{text}作为文本占位符")
        self.custom_prompt.setMaximumHeight(80)
        layout.addWidget(self.custom_prompt)

        # 功能名称配置
        name_label = QLabel("功能名称:")
        layout.addWidget(name_label)

        self.custom_name = QLineEdit("自定义功能")
        layout.addWidget(self.custom_name)

        # 高级设置
        advanced_label = QLabel("高级设置:")
        advanced_label.setStyleSheet("margin-top: 10px;")
        layout.addWidget(advanced_label)

        # API模型选择
        model_label = QLabel("API模型:")
        layout.addWidget(model_label)

        self.model_combo = QComboBox()
        # 使用配置管理器获取可用模型
        available_models = self.config_manager.get_available_models()
        self.model_combo.addItems(available_models)

        # 设置当前选中的模型
        current_model = self.custom_settings.get('model', 'qwen3-32b')
        if current_model in available_models:
            index = available_models.index(current_model)
            self.model_combo.setCurrentIndex(index)

        # 设置当前的提示词模板和功能名称
        self.custom_prompt.setPlainText(self.custom_settings.get('prompt_template', "请对以下内容进行自定义处理：\n\n{text}"))
        self.custom_name.setText(self.custom_settings.get('function_name', '自定义功能'))
        layout.addWidget(self.model_combo)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self._save_custom_settings)
        button_layout.addWidget(self.save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # 保存设置到实例变量
        self.settings_dialog = dialog

        # 显示对话框
        dialog.exec()

    def _save_custom_settings(self):
        """保存自定义设置"""
        try:
            # 获取用户输入的设置
            prompt_template = self.custom_prompt.toPlainText()
            function_name = self.custom_name.text()
            selected_model = self.model_combo.currentText()

            # 验证输入
            if not function_name.strip():
                QMessageBox.warning(self, "警告", "请输入功能名称")
                return

            if not prompt_template.strip():
                QMessageBox.warning(self, "警告", "请输入提示词模板")
                return

            # 使用配置管理器保存设置
            new_settings = {
                'prompt_template': prompt_template,
                'function_name': function_name,
                'model': selected_model
            }

            # 保存设置
            if self.config_manager.save_settings(new_settings):
                # 更新本地的自定义设置
                self.custom_settings = self.config_manager.get_settings()

                # 更新自定义功能按钮的显示
                self.btn_custom.setText(f"⚙️ {function_name}")

                # 关闭对话框
                if hasattr(self, 'settings_dialog'):
                    self.settings_dialog.close()

                # 显示成功消息
                QMessageBox.information(self, "成功", f"自定义功能 '{function_name}' 已保存")

                logger.info(f"自定义设置已保存: {self.custom_settings}")
            else:
                QMessageBox.critical(self, "错误", "保存设置失败")

        except Exception as e:
            logger.error(f"保存自定义设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")

    def _on_ocr_clicked(self):
        """OCR按钮点击事件（已移除）"""
        # 此功能已移除
        self.result_text.setPlainText("❌ OCR功能已移除")
        self.result_frame.setVisible(True)
        self._apply_plain_style()
        self.progress_container.setVisible(False)

    def _perform_ocr_from_current_screenshot(self):
        """对当前截图进行OCR处理（已移除）"""
        # 此功能已移除
        pass

    def _perform_ocr_from_file(self, file_path: str):
        """从文件路径执行OCR（已移除）"""
        # 此功能已移除
        pass

    def _process_ask_stream(self):
        """流式处理提问 - 使用信号机制进行线程间通信（支持连续对话）"""
        import asyncio
        from datetime import datetime

        # 防止重复启动流式任务
        if self.is_streaming:
            logger.warning("已有流式任务在运行，忽略重复请求")
            return

        self.result_text.setPlainText("")
        self.is_streaming = True

        # 显示流式输出状态
        self._start_streaming_indicator()

        def stream_task():
            """流式任务"""
            async def run_stream():
                start_time = datetime.now()
                current_answer = []  # 收集当前回答
                try:
                    if self.question_asker and self.current_question:
                        # 不传 current_text，使用 QuestionAsker 中维护的上下文
                        stream = self.question_asker.ask_stream(
                            question=self.current_question
                        )
                    else:
                        self.stream_error.emit("提问功能未初始化或问题为空")
                        return

                    chunk_count = 0
                    async for chunk in stream:
                        if not self.is_streaming:
                            logger.info("流式输出已停止")
                            break

                        if "error" in chunk:
                            self.stream_error.emit(chunk["error"])
                            break

                        content = chunk.get("content", "")
                        if content:
                            chunk_count += 1
                            current_answer.append(content)
                            self.stream_chunk.emit(content)

                            # 每5个chunk更新一次状态
                            if chunk_count % 5 == 0:
                                elapsed = (datetime.now() - start_time).total_seconds()
                                logger.debug(f"流式输出进度: {chunk_count} chunks, {elapsed:.1f}s")

                    # 保存对话到历史
                    self.chat_history.append({
                        "question": self.current_question,
                        "answer": "".join(current_answer)
                    })

                    self.stream_complete.emit()

                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.info(f"流式输出完成: {chunk_count} chunks, 耗时 {elapsed:.2f}s")

                except Exception as e:
                    logger.error(f"流式输出失败: {e}", exc_info=True)
                    self.stream_error.emit(str(e))

            # 在后台线程中创建独立的事件循环
            asyncio.run(run_stream())

        # 在后台线程运行流式任务
        thread = threading.Thread(target=stream_task, daemon=True)
        thread.start()

    def _process_text_stream(self, feature_type: str):
        """流式处理文本 - 使用信号机制进行线程间通信"""
        import asyncio
        from datetime import datetime

        # 防止重复启动流式任务
        if self.is_streaming:
            logger.warning("已有流式任务在运行，忽略重复请求")
            return

        self.result_text.setPlainText("")
        self.is_streaming = True

        # 显示流式输出状态
        self._start_streaming_indicator()

        def stream_task():
            """流式任务"""
            async def run_stream():
                start_time = datetime.now()
                try:
                    if feature_type == "translate":
                        stream = self.translator.translate_stream(self.current_text)
                    elif feature_type == "explain":
                        stream = self.explainer.explain_stream(self.current_text)
                    elif feature_type == "summarize":
                        stream = self.summarizer.summarize_stream(self.current_text)
                    elif feature_type == "custom":
                        # 使用自定义设置处理
                        custom_prompt = self.custom_settings.get('prompt_template', "请对以下内容进行自定义处理：\n\n{text}")
                        # 替换占位符
                        processed_prompt = custom_prompt.replace("{text}", self.current_text)

                        # 使用自定义功能名称
                        custom_name = self.custom_settings.get('function_name', '自定义功能')
                        custom_model = self.custom_settings.get('model', 'qwen3-32b')

                        # 创建一个简单的流式处理
                        async def custom_stream():
                            try:
                                # 使用指定的模型处理
                                result = await self.custom_builder.execute_simple(processed_prompt, model=custom_model)
                                yield {"content": result}
                            except Exception as e:
                                yield {"error": str(e)}

                        stream = custom_stream()
                    else:
                        self.stream_error.emit(f"不支持流式的功能: {feature_type}")
                        return

                    chunk_count = 0
                    async for chunk in stream:
                        if not self.is_streaming:
                            logger.info("流式输出已停止")
                            break

                        if "error" in chunk:
                            self.stream_error.emit(chunk["error"])
                            break

                        content = chunk.get("content", "")
                        if content:
                            chunk_count += 1
                            self.stream_chunk.emit(content)

                            # 每5个chunk更新一次状态
                            if chunk_count % 5 == 0:
                                elapsed = (datetime.now() - start_time).total_seconds()
                                logger.debug(f"流式输出进度: {chunk_count} chunks, {elapsed:.1f}s")

                    self.stream_complete.emit()

                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.info(f"流式输出完成: {chunk_count} chunks, 耗时 {elapsed:.2f}s")

                except Exception as e:
                    logger.error(f"流式输出失败: {e}", exc_info=True)
                    self.stream_error.emit(str(e))

            # 在后台线程中创建独立的事件循环
            asyncio.run(run_stream())

        # 在后台线程运行流式任务
        thread = threading.Thread(target=stream_task, daemon=True)
        thread.start()

    def _on_level_changed(self, level: str):
        """级别切换处理"""
        self.current_level = level

        # 更新按钮样式
        self.btn_level_beginner.setStyleSheet("")
        self.btn_level_default.setStyleSheet("")
        self.btn_level_advanced.setStyleSheet("")

        if level == "beginner":
            self.btn_level_beginner.setStyleSheet("background-color: #007bff; color: white;")
        elif level == "default":
            self.btn_level_default.setStyleSheet("background-color: #007bff; color: white;")
        elif level == "advanced":
            self.btn_level_advanced.setStyleSheet("background-color: #007bff; color: white;")

        # 如果当前显示的是Python代码讲解结果，重新执行
        if self.result_frame.isVisible() and self._is_python_code(self.current_text):
            self.result_text.setPlainText("处理中...")
            self._apply_plain_style()
            QTimer.singleShot(0, lambda: self._process_text_stream("explain"))

    # ==================== 图表相关方法 ====================

    def _on_chart_zoom_in(self):
        """放大图表"""
        self.chart_scale_factor = min(2.0, self.chart_scale_factor + 0.25)
        self._update_chart_display()

    def _on_chart_zoom_out(self):
        """缩小图表"""
        self.chart_scale_factor = max(0.25, self.chart_scale_factor - 0.25)
        self._update_chart_display()

    def _on_chart_reset(self):
        """重置图表缩放"""
        self.chart_scale_factor = 1.0
        self._update_chart_display()

    def _update_chart_display(self):
        """更新图表显示"""
        if not self.current_chart_path:
            return

        # 更新缩放比例标签
        scale_percent = int(self.chart_scale_factor * 100)
        self.chart_scale_label.setText(f"{scale_percent}%")

        # 加载并缩放图片
        pixmap = QPixmap(self.current_chart_path)
        if pixmap.isNull():
            logger.error(f"无法加载图表: {self.current_chart_path}")
            return

        # 计算缩放后的尺寸
        scaled_pixmap = pixmap.scaled(
            int(pixmap.width() * self.chart_scale_factor),
            int(pixmap.height() * self.chart_scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.chart_image_label.setPixmap(scaled_pixmap)

    def _on_chart_save(self):
        """保存图表"""
        if not self.current_chart_path:
            QMessageBox.warning(self, "警告", "没有可保存的图表")
            return

        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图表",
            f"chart_{int(time.time())}.png",
            "PNG 图片 (*.png);;JPEG 图片 (*.jpg);;所有文件 (*.*)"
        )

        if file_path:
            try:
                # 复制文件到目标路径
                import shutil
                shutil.copy2(self.current_chart_path, file_path)
                QMessageBox.information(self, "成功", f"图表已保存到:\n{file_path}")
                logger.info(f"图表已保存: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")
                logger.error(f"保存图表失败: {e}")

    def _display_chart(self, chart_path: str, description: str = ""):
        """
        显示图表

        Args:
            chart_path: 图表图片路径
            description: 图表描述（可选）
        """
        self.current_chart_path = chart_path
        self.chart_scale_factor = 1.0

        # 隐藏结果文本，显示图表容器
        self.result_text.setVisible(False)
        self.chart_container.setVisible(True)

        # 加载并显示图片
        pixmap = QPixmap(chart_path)
        if pixmap.isNull():
            logger.error(f"无法加载图表: {chart_path}")
            self.result_text.setVisible(True)
            self.chart_container.setVisible(False)
            self.result_text.setPlainText(f"错误: 无法加载图表 {chart_path}")
            return

        # 缩放到合适大小
        scaled_pixmap = pixmap.scaled(
            pixmap.width(),
            self.max_chart_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.chart_image_label.setPixmap(scaled_pixmap)
        self.chart_scale_label.setText("100%")

        # 显示描述（如果有）
        if description:
            self.result_text.setVisible(True)
            self.result_text.setPlainText(description)
            self._apply_plain_style()

        # 显示复制按钮（用于描述文本）
        self.btn_copy.setVisible(bool(description))

    def _hide_chart(self):
        """隐藏图表，显示文本结果"""
        self.chart_container.setVisible(False)
        self.result_text.setVisible(True)
        self.current_chart_path = None
