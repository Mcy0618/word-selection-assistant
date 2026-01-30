#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地缓存管理器
用于缓存翻译、解释和总结的结果
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class LocalCacheManager:
    """本地缓存管理器"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """初始化缓存管理器"""
        if cache_dir is None:
            home_dir = Path.home()
            cache_dir = home_dir / ".word_selection_assistant" / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "cache.json"
        
        # 加载缓存
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def _generate_key(self, feature_type: str, text: str, **kwargs) -> str:
        """生成缓存键"""
        params = {'feature_type': feature_type, 'text': text, **kwargs}
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode('utf-8')).hexdigest()
    
    def get(self, feature_type: str, text: str, **kwargs) -> Optional[str]:
        """获取缓存"""
        key = self._generate_key(feature_type, text, **kwargs)
        return self.cache.get(key)
    
    def set(self, feature_type: str, text: str, result: str, **kwargs):
        """设置缓存"""
        key = self._generate_key(feature_type, text, **kwargs)
        self.cache[key] = result
        self._save_cache()
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self._save_cache()


# 全局实例
_cache_manager: Optional[LocalCacheManager] = None


def get_cache_manager() -> LocalCacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = LocalCacheManager()
    return _cache_manager