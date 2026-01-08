# Core模块初始化
from .hotkey_manager import HotkeyManager
from .text_capture import TextCapture
from .function_router import FunctionRouter, FunctionType, FunctionResult

__all__ = ['HotkeyManager', 'TextCapture', 'FunctionRouter', 'FunctionType', 'FunctionResult']
