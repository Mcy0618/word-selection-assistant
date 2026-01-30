#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘图标
"""

import logging
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QObject, pyqtSignal

logger = logging.getLogger(__name__)


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标"""
    
    show_popup_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 保持对图标和菜单的强引用，防止被垃圾回收
        self._icon = None
        self.menu = QMenu()
        
        # 创建图标
        self._icon = self._create_icon()
        self.setIcon(self._icon)
        
        # 添加菜单项
        self._setup_menu()
        
        # 设置上下文菜单 - 这是关键！
        self.setContextMenu(self.menu)
        
        # 激活时的处理
        self.activated.connect(self._on_activated)
        
        # 确保托盘图标可见
        self.setVisible(True)
        
        logger.info("托盘图标已创建")
    
    def _create_icon(self) -> QIcon:
        """创建托盘图标"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 绘制圆形背景
        painter.setBrush(QColor(66, 133, 244))
        painter.drawEllipse(4, 4, 24, 24)
        
        # 绘制文字 "词"
        painter.setPen(Qt.GlobalColor.white)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "词")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _setup_menu(self):
        """设置菜单"""
        # 显示主窗口
        show_action = QAction("📖 显示窗口", self)
        show_action.triggered.connect(self.show_popup_requested.emit)
        self.menu.addAction(show_action)

        # 分隔线
        self.menu.addSeparator()

        # 功能菜单
        translate_action = QAction("🔤 翻译", self)
        translate_action.triggered.connect(lambda: self._on_quick_action("translate"))
        self.menu.addAction(translate_action)

        explain_action = QAction("💡 解释", self)
        explain_action.triggered.connect(lambda: self._on_quick_action("explain"))
        self.menu.addAction(explain_action)

        summarize_action = QAction("📝 总结", self)
        summarize_action.triggered.connect(lambda: self._on_quick_action("summarize"))
        self.menu.addAction(summarize_action)

        # 分隔线
        self.menu.addSeparator()

        # 设置
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        self.menu.addAction(settings_action)

        # 分隔线
        self.menu.addSeparator()

        # 退出
        exit_action = QAction("❌ 退出", self)
        exit_action.triggered.connect(self._on_exit)
        self.menu.addAction(exit_action)
    
    def _on_quick_action(self, action: str):
        """快速操作"""
        logger.info(f"用户选择快速操作: {action}")
        self.show_popup_requested.emit()
    
    def _on_activated(self, reason):
        """托盘图标被激活"""
        logger.debug(f"托盘图标被激活: {reason}")
        
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_popup_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            logger.debug("右键点击")
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            logger.debug("中键点击")
    
    def _on_exit(self):
        """退出程序"""
        logger.info("用户请求退出")
        QApplication.quit()