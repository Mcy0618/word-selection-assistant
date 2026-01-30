#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件入口
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == '__main__':
    # 自动发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = PROJECT_ROOT / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)