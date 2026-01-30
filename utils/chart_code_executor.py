#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表代码执行器
安全地执行 LLM 生成的绑图代码
"""

import logging
import sys
import io
import traceback
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)

# 允许导入的模块
ALLOWED_IMPORTS = [
    "matplotlib",
    "matplotlib.pyplot",
    "matplotlib.figure",
    "mpl_toolkits.mplot3d",
    "numpy",
    "numpy.random",
    "numpy.linalg",
    "pandas",
    "scipy",
    "sklearn",
    "sklearn.decomposition",
    "sklearn.manifold",
    "sklearn.feature_selection",
    "seaborn",
    "pylab",
    "typing",
    "math",
    "random",
    "itertools",
    "collections",
    "datetime",
]

# 禁止的操作
FORBIDDEN_PATTERNS = [
    "import os",
    "import sys",
    "import subprocess",
    "import socket",
    "import requests",
    "import urllib",
    "open(",
    "exec(",
    "eval(",
    "__import__",
    "getattr",
    "setattr",
    "delattr",
    "compile(",
    "globals()",
    "locals()",
    "vars(",
]


class ChartCodeExecutor:
    """图表代码执行器
    
    安全地执行 LLM 生成的绑图代码，
    捕获输出并返回生成的图片路径。
    """
    
    def __init__(self, output_dir: Optional[Path] = None, timeout: int = 30):
        """
        初始化代码执行器
        
        Args:
            output_dir: 图片输出目录
            timeout: 执行超时时间（秒）
        """
        self.output_dir = output_dir or Path(__file__).parent.parent / "charts"
        self.output_dir.mkdir(exist_ok=True)
        self.timeout = timeout
        
        # matplotlib 无显示器后端
        self._setup_matplotlib_backend()
    
    def _setup_matplotlib_backend(self):
        """配置 matplotlib 后端"""
        import os
        # 强制使用 Agg 后端（无显示器环境）
        os.environ.setdefault('MPLBACKEND', 'Agg')
        
        try:
            import matplotlib
            if matplotlib.get_backend().lower() != 'agg':
                matplotlib.use('Agg')
        except Exception as e:
            logger.warning(f"配置 matplotlib 后端失败: {e}")
    
    def validate_code(self, code: str) -> Dict:
        """
        验证代码安全性
        
        Args:
            code: Python 代码
        
        Returns:
            Dict: 包含 safe 和 reason 字段的字典
        """
        code_lower = code.lower()
        
        # 检查禁止的导入
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in code_lower:
                return {
                    "safe": False,
                    "reason": f"代码包含禁止的操作: {pattern}"
                }
        
        # 检查是否包含必要的 matplotlib 导入
        if "matplotlib" not in code_lower and "plt." not in code_lower:
            return {
                "safe": False,
                "reason": "代码未包含 matplotlib 导入"
            }
        
        # 检查是否包含保存图片的代码
        if "savefig" not in code_lower and "save" not in code_lower:
            return {
                "safe": False,
                "reason": "代码未包含图片保存操作 (plt.savefig)"
            }
        
        return {"safe": True, "reason": ""}
    
    def execute(self, code: str) -> Dict:
        """
        执行代码并生成图片
        
        Args:
            code: Python 代码
        
        Returns:
            Dict: 包含 image_path 或 error 字段的字典
        """
        # 验证代码
        validation = self.validate_code(code)
        if not validation["safe"]:
            return {"error": validation["reason"]}
        
        # 准备执行环境
        local_vars = {}
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # 生成输出文件路径
        import uuid
        output_filename = f"chart_{uuid.uuid4().hex[:8]}.png"
        output_path = self.output_dir / output_filename
        
        try:
            # 添加必要的导入到代码
            setup_code = f"""
import sys
import os

# 设置输出路径
OUTPUT_PATH = r\"{output_path.as_posix()}\"

# 确保输出目录存在
os.makedirs(os.path.dirname(OUTPUT_PATH) if os.path.dirname(OUTPUT_PATH) else '.', exist_ok=True)

# 创建 output_path 别名以便与 LLM 生成的代码兼容
output_path = OUTPUT_PATH
"""
            
            full_code = setup_code + code
            
            # 设置 matplotlib 后端
            import matplotlib
            matplotlib.use('Agg')
            
            # 执行代码 - 不做路径替换，直接执行
            # setup_code 中定义的 output_path 是全局变量
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(full_code, {}, local_vars)
            
            # 检查输出
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            if stderr_output:
                logger.warning(f"代码执行警告: {stderr_output}")
            
            # 检查图片是否生成
            if output_path.exists():
                return {
                    "success": True,
                    "image_path": str(output_path),
                    "stdout": stdout_output,
                }
            
            # 尝试从标准输出中提取路径
            if "IMAGE_SAVED:" in stdout_output:
                import re
                match = re.search(r'IMAGE_SAVED:([^\n]+)', stdout_output)
                if match:
                    saved_path = Path(match.group(1).strip())
                    if saved_path.exists():
                        return {
                            "success": True,
                            "image_path": str(saved_path),
                            "stdout": stdout_output,
                        }
            
            return {
                "error": "代码执行完成但未生成图片",
                "stdout": stdout_output,
                "stderr": stderr_output
            }
            
        except SyntaxError as e:
            error_msg = f"语法错误: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"执行错误: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def execute_with_timeout(self, code: str) -> Dict:
        """
        带超时的代码执行
        
        Args:
            code: Python 代码
        
        Returns:
            Dict: 执行结果
        """
        import threading
        execution_result: Dict = {}
        execution_done = threading.Event()
        
        def run_execution():
            try:
                exec_result = self.execute(code)
                execution_result.update(exec_result)
            except Exception as e:
                execution_result.update({"error": str(e)})
            finally:
                execution_done.set()
        
        thread = threading.Thread(target=run_execution)
        thread.daemon = True
        thread.start()
        
        # 等待线程完成或超时
        finished = execution_done.wait(timeout=self.timeout)
        
        if finished:
            # 线程正常完成，返回结果（可能包含 error 字段）
            return execution_result
        else:
            # 超时
            return {"error": f"执行超时（{self.timeout}秒）"}
    
    def cleanup_old_files(self, max_age: int = 3600, max_files: int = 100):
        """
        清理旧的临时图片文件
        
        Args:
            max_age: 最大文件存活时间（秒）
            max_files: 最大保留文件数
        """
        import time
        import os
        
        now = time.time()
        files = []
        
        for f in self.output_dir.glob("chart_*.png"):
            age = now - f.stat().st_mtime
            files.append((f, age))
        
        # 按时间排序
        files.sort(key=lambda x: x[1], reverse=True)
        
        # 删除过期的文件
        deleted = 0
        for f, age in files:
            if age > max_age or len(files) - deleted > max_files:
                try:
                    f.unlink()
                    deleted += 1
                except Exception as e:
                    logger.warning(f"删除文件失败: {f}, {e}")
        
        if deleted > 0:
            logger.info(f"清理了 {deleted} 个旧图表文件")
    
    def get_output_dir(self) -> Path:
        """获取输出目录"""
        return self.output_dir
    
    def list_charts(self) -> List[Dict]:
        """
        列出所有生成的图表
        
        Returns:
            List[Dict]: 图表文件信息列表
        """
        import time
        
        charts = []
        for f in self.output_dir.glob("chart_*.png"):
            try:
                stat = f.stat()
                charts.append({
                    "path": str(f),
                    "name": f.name,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "modified_human": time.strftime(
                        "%Y-%m-%d %H:%M:%S", 
                        time.localtime(stat.st_mtime)
                    ),
                })
            except Exception as e:
                logger.warning(f"获取文件信息失败: {f}, {e}")
        
        # 按修改时间排序
        charts.sort(key=lambda x: x["modified"], reverse=True)
        return charts


# 便捷函数
def execute_chart_code(code: str, output_dir: Optional[str] = None) -> Dict:
    """
    执行图表代码的便捷函数
    
    Args:
        code: Python 代码
        output_dir: 输出目录
    
    Returns:
        Dict: 执行结果
    """
    executor = ChartCodeExecutor(Path(output_dir) if output_dir else None)
    return executor.execute(code)
