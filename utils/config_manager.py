#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
管理自定义功能的设置和加载
"""

import json
import os
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger("config_manager")

class ConfigManager:
    """配置管理器"""
    
    # 可用模型列表
    AVAILABLE_MODELS = [
        # 本地Ollama模型
        "qwen3-embedding", "novaforgeai/deepseek-coder", "kimi-k2.5", "minimax-m2.1",
        "glm-4.7", "deepseek-v3.2", "gemini-3-pro-preview", "gemini-3-flash-preview",
        "dandank/chatgpt", "dandank/deepseek", "kimi-k2-thinking", "qwen3-vl",
        "deepseek-v3.1", "qwen3-coder", "gpt-oss",
        
        # 通用模型名称
        "llama3", "llama3.1", "llama3.2", "mistral", "gemma", "gemma2", "phi3", "phi3.5",
        "mixtral", "yi", "llava", "moondream", "qwen2", "qwen2.5", "command-r", "command-r-plus",
        
        # OpenAI兼容API模型
        "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
        "claude-3-haiku", "claude-3-sonnet", "claude-3-opus", "claude-3-5-sonnet",
        "gemini-1.5-pro", "gemini-1.5-flash", "llama-3.1-8b", "llama-3.1-70b", "llama-3.2-1b", "llama-3.2-3b"
    ]
    
    # 默认自定义设置
    DEFAULT_CUSTOM_SETTINGS = {
        'prompt_template': "请对以下内容进行自定义处理：\n\n{text}",
        'function_name': "自定义功能",
        'model': "llama3.2",  # 使用通用模型名称
        'timestamp': 0
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器"""
        if config_path is None:
            # 默认配置文件路径
            config_dir = os.path.expanduser("~/.word_selection_assistant")
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "custom_settings.json")
        
        self.config_path = config_path
        self.custom_settings = self.DEFAULT_CUSTOM_SETTINGS.copy()
        
        # 加载已保存的配置
        self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """加载自定义设置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 合并默认设置和已加载的设置
                    self.custom_settings = {**self.DEFAULT_CUSTOM_SETTINGS, **loaded_settings}
                    
                    # 验证模型是否可用
                    if self.custom_settings.get('model') not in self.AVAILABLE_MODELS:
                        logger.warning(f"模型 {self.custom_settings.get('model')} 不在可用列表中，使用默认模型")
                        self.custom_settings['model'] = self.DEFAULT_CUSTOM_SETTINGS['model']
                    
                    logger.info(f"已加载自定义设置: {self.custom_settings}")
            else:
                logger.info("配置文件不存在，使用默认设置")
                
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            # 使用默认设置
            self.custom_settings = self.DEFAULT_CUSTOM_SETTINGS.copy()
        
        return self.custom_settings
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """保存自定义设置"""
        try:
            # 验证设置
            validated_settings = self._validate_settings(settings)
            
            # 更新内存中的设置
            self.custom_settings.update(validated_settings)
            
            # 保存到文件
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_settings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已保存自定义设置: {self.custom_settings}")
            return True
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            return False
    
    def _validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """验证设置"""
        validated = {}
        
        # 验证功能名称
        function_name = settings.get('function_name', '').strip()
        if function_name:
            validated['function_name'] = function_name
        else:
            validated['function_name'] = self.DEFAULT_CUSTOM_SETTINGS['function_name']
        
        # 验证提示词模板
        prompt_template = settings.get('prompt_template', '').strip()
        if prompt_template:
            validated['prompt_template'] = prompt_template
        else:
            validated['prompt_template'] = self.DEFAULT_CUSTOM_SETTINGS['prompt_template']
        
        # 验证模型
        model = settings.get('model', '').strip()
        if model in self.AVAILABLE_MODELS:
            validated['model'] = model
        else:
            validated['model'] = self.DEFAULT_CUSTOM_SETTINGS['model']
        
        # 添加时间戳
        import time
        validated['timestamp'] = int(time.time())
        
        return validated
    
    def get_settings(self) -> Dict[str, Any]:
        """获取当前设置"""
        return self.custom_settings.copy()
    
    def get_available_models(self) -> list:
        """获取可用模型列表"""
        return self.AVAILABLE_MODELS.copy()
    
    def reset_to_default(self):
        """重置为默认设置"""
        self.custom_settings = self.DEFAULT_CUSTOM_SETTINGS.copy()
        self.save_settings(self.custom_settings)
        logger.info("已重置为默认设置")

# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager