#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置加载器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        
        # 加载 .env 文件
        self._load_env_file()
        
        if config_file:
            self.load(config_file)
    
    def _load_env_file(self):
        """加载 .env 文件"""
        try:
            # 尝试从项目根目录加载 .env
            project_root = Path(__file__).parent.parent
            env_file = project_root / ".env"
            
            if env_file.exists():
                load_dotenv(env_file)
                logger.info(f"已加载环境变量文件: {env_file}")
        except Exception as e:
            logger.warning(f"加载 .env 文件失败: {e}")
    
    def _replace_env_vars(self, data: Any) -> Any:
        """
        递归替换配置中的环境变量占位符
        
        Args:
            data: 配置数据（可能是字典、列表或字符串）
        
        Returns:
            Any: 替换后的数据
        """
        if isinstance(data, dict):
            return {k: self._replace_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_env_vars(item) for item in data]
        elif isinstance(data, str):
            # 匹配 ${VAR_NAME} 格式
            pattern = r'\$\{([^}]+)\}'
            
            def replace_match(match):
                var_name = match.group(1)
                # 优先从环境变量读取
                value = os.getenv(var_name)
                if value is not None:
                    return value
                # 如果环境变量不存在，返回原始字符串
                return match.group(0)
            
            return re.sub(pattern, replace_match, data)
        else:
            return data
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            file_path: 配置文件路径
        
        Returns:
            Dict: 配置内容
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"配置文件不存在: {file_path}")
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
                # 自动替换环境变量
                self.config = self._replace_env_vars(self.config)
                logger.info(f"已加载配置: {file_path}")
                return self.config
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点分隔，如 "app.name"）
            default: 默认值
        
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 值
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, file_path: str = None):
        """
        保存配置到文件
        
        Args:
            file_path: 保存路径（可选）
        """
        path = file_path or self.config_file
        if not path:
            logger.error("未指定保存路径")
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
                logger.info(f"配置已保存: {path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def reload(self):
        """重新加载配置"""
        if self.config_file:
            self.load(self.config_file)


# 全局配置实例
_config_instance: Optional[ConfigLoader] = None


def get_config(config_file: str = None) -> ConfigLoader:
    """
    获取全局配置实例
    
    Args:
        config_file: 配置文件路径
    
    Returns:
        ConfigLoader: 配置加载器实例
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigLoader(config_file)
    
    return _config_instance
