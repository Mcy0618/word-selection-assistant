#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悬浮弹窗
显示功能选择和结果
"""

import logging
import asyncio
from typing import Callable
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QCursor
from PyQt6.QtCore import Qt, QTimer, QPoint

logger = logging.getLogger(__name__)


class PopupWindow(QWidget):
    """悬浮弹窗"""
    
    def __init__(self, translator=None, explainer=None, summarizer=None):
        """
        初始化弹窗
        
        Args:
            translator: 翻译功能实例
            explainer: 解释功能实例
            summarizer: 总结功能实例
        """
        super().__init__()
        
        # 功能模块引用
        self.translator = translator
        self.explainer = explainer
        self.summarizer = summarizer
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 自动隐藏计时器
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self._on_auto_hide)
        self.hide_timer.setSingleShot(True)
        
        # 状态
        self.current_text = ""
        self.callbacks = {}
        
        # UI
        self._setup_ui()
        self._setup_styles()
        
        # 移动
        self.dragging = False
        self.drag_position = QPoint()
    
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
        self.btn_custom = self._create_button("⚙️ 自定义", "custom")
        
        self.buttons_layout.addWidget(self.btn_translate)
        self.buttons_layout.addWidget(self.btn_explain)
        self.buttons_layout.addWidget(self.btn_summarize)
        self.buttons_layout.addWidget(self.btn_custom)
        
        card_layout.addLayout(self.buttons_layout)
        
        # 结果区域（初始隐藏）
        self.result_frame = QFrame()
        self.result_frame.setObjectName("result_frame")
        self.result_frame.setVisible(False)
        result_layout = QVBoxLayout(self.result_frame)
        
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setObjectName("result")
        result_layout.addWidget(self.result_label)
        
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
            #btn_translate, #btn_explain, #btn_summarize, #btn_custom {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                background: #f8f8f8;
                font-size: 12px;
            }
            #btn_translate:hover, #btn_explain:hover, #btn_summarize:hover, #btn_custom:hover {
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
        """)
    
    def show_with_text(self, text: str):
        """显示弹窗并设置文本"""
        if not text or not text.strip():
            return
        
        self.current_text = text.strip()
        self.preview_label.setText(self.current_text[:100] + "..." if len(self.current_text) > 100 else self.current_text)
        
        # 重置结果区域
        self.result_frame.setVisible(False)
        self.result_label.setText("")
        
        # 显示窗口
        self._position_at_cursor()
        self.show()
        
        # 重置自动隐藏计时器
        self.hide_timer.stop()
        self.hide_timer.start(8000)  # 8秒后自动隐藏
    
    def _position_at_cursor(self):
        """定位到鼠标位置"""
        cursor_pos = QCursor.pos()
        x = cursor_pos.x() + 20
        y = cursor_pos.y() + 20
        
        # 确保不超出屏幕
        screen = QApplication.primaryScreen().geometry()
        if x + self.width() > screen.width():
            x = screen.width() - self.width() - 20
        if y + self.height() > screen.height():
            y = screen.height() - self.height() - 20
        
        self.move(x, y)
    
    def _on_feature_clicked(self, feature_type: str):
        """功能按钮点击"""
        logger.info(f"用户选择功能: {feature_type}")
        
        # 显示加载状态
        self.result_frame.setVisible(True)
        self.result_label.setText("处理中...")
        
        # 使用 QTimer 模拟异步处理
        QTimer.singleShot(500, lambda: self._process_text_sync(feature_type))
    
    def _process_text_sync(self, feature_type: str):
        """同步处理文本"""
        # 实际调用API
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if feature_type == "translate":
                if self.translator:
                    result = loop.run_until_complete(self.translator.translate(self.current_text))
                else:
                    result = f"[模拟翻译] {self.current_text}"
            
            elif feature_type == "explain":
                if self.explainer:
                    result = loop.run_until_complete(self.explainer.explain(self.current_text))
                else:
                    result = f"[模拟解释] {self.current_text}"
            
            elif feature_type == "summarize":
                if self.summarizer:
                    result = loop.run_until_complete(self.summarizer.summarize(self.current_text))
                else:
                    result = f"[模拟总结] {self.current_text}"
            
            elif feature_type == "custom":
                result = "自定义功能待实现"
            
            else:
                result = f"未知功能: {feature_type}"
        
        except Exception as e:
            result = f"处理失败: {e}"
        finally:
            loop.close()
        
        self.result_label.setText(result)
    
    def _on_auto_hide(self):
        """自动隐藏"""
        self.hide()
    
    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.pos()
    
    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.dragging:
            self.move(self.pos() + event.pos() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        self.dragging = False
    
    def enterEvent(self, event):
        """鼠标进入"""
        self.hide_timer.stop()
    
    def leaveEvent(self, event):
        """鼠标离开"""
        self.hide_timer.start(3000)
