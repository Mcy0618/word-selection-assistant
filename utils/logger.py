#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(name: str = None, 
                 level: str = "INFO",
                 log_file: Optional[str] = None,
                 max_size: int = 10 * 1024 * 1024,
                 backup_count: int = 3) -> logging.Logger:
    """
    设置日志
    
    Args:
        name: 日志器名称
        level: 日志级别
        log_file: 日志文件路径
        max_size: 最大文件大小（字节）
        backup_count: 保留的备份数量
    
    Returns:
        logging.Logger: 日志器实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)
