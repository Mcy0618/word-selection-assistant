#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表依赖管理器
自动检测和安装 matplotlib、numpy、pillow 等绘图依赖
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# 必需的依赖列表
REQUIRED_DEPENDENCIES = {
    "matplotlib": "matplotlib>=3.8.0",
    "numpy": "numpy>=1.24.0",
}

# 可选的增强依赖
OPTIONAL_DEPENDENCIES = {
    "scipy": "scipy>=1.11.0",
    "seaborn": "seaborn>=0.12.0",
    "plotly": "plotly>=5.18.0",
}


class ChartDependencyManager:
    """图表依赖管理器
    
    自动检测 matplotlib、numpy、pillow 等依赖的安装状态，
    提供安装功能，确保图表生成功能正常工作。
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化依赖管理器
        
        Args:
            project_root: 项目根目录，用于确定 poetry 虚拟环境位置
        """
        self.project_root = project_root or Path(__file__).parent.parent
        self._cache_status: Dict[str, Tuple[bool, Optional[str]]] = {}
    
    def check_dependency(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        检查单个依赖是否已安装
        
        Args:
            name: 依赖名称 (matplotlib, numpy, pillow)
        
        Returns:
            Tuple[是否安装, 版本号或None]
        """
        if name in self._cache_status:
            return self._cache_status[name]
        
        try:
            module = __import__(name)
            version = getattr(module, '__version__', None)
            self._cache_status[name] = (True, version)
            logger.debug(f"依赖 {name} 已安装，版本: {version}")
            return True, version
        except ImportError:
            self._cache_status[name] = (False, None)
            logger.debug(f"依赖 {name} 未安装")
            return False, None
    
    def check_all_dependencies(self) -> Dict[str, Dict]:
        """
        检查所有必需依赖的安装状态
        
        Returns:
            Dict: 每个依赖的状态信息
        """
        result = {}
        for dep_name in REQUIRED_DEPENDENCIES:
            installed, version = self.check_dependency(dep_name)
            result[dep_name] = {
                "installed": installed,
                "version": version,
                "required_version": REQUIRED_DEPENDENCIES[dep_name],
                "optional": False,
            }
        
        for dep_name in OPTIONAL_DEPENDENCIES:
            installed, version = self.check_dependency(dep_name)
            result[dep_name] = {
                "installed": installed,
                "version": version,
                "required_version": OPTIONAL_DEPENDENCIES[dep_name],
                "optional": True,
            }
        
        return result
    
    def get_missing_dependencies(self) -> list:
        """
        获取未安装的必需依赖列表
        
        Returns:
            list: 未安装的依赖名称列表
        """
        missing = []
        for dep_name in REQUIRED_DEPENDENCIES:
            installed, _ = self.check_dependency(dep_name)
            if not installed:
                missing.append(dep_name)
        return missing
    
    def is_ready(self) -> bool:
        """
        检查所有必需依赖是否已安装
        
        Returns:
            bool: True 表示所有必需依赖已安装
        """
        return len(self.get_missing_dependencies()) == 0
    
    def install_dependencies(self, 
                            missing_only: bool = True,
                            optional: bool = False) -> Tuple[bool, str]:
        """
        安装缺失的依赖
        
        Args:
            missing_only: 是否只安装缺失的依赖
            optional: 是否也安装可选依赖
        
        Returns:
            Tuple[是否成功, 消息]
        """
        deps_to_install = []
        
        if not missing_only:
            deps_to_install = list(REQUIRED_DEPENDENCIES.values())
            if optional:
                deps_to_install.extend(list(OPTIONAL_DEPENDENCIES.values()))
        else:
            for dep_name in REQUIRED_DEPENDENCIES:
                installed, _ = self.check_dependency(dep_name)
                if not installed:
                    deps_to_install.append(REQUIRED_DEPENDENCIES[dep_name])
            
            if optional:
                for dep_name in OPTIONAL_DEPENDENCIES:
                    installed, _ = self.check_dependency(dep_name)
                    if not installed:
                        deps_to_install.append(OPTIONAL_DEPENDENCIES[dep_name])
        
        if not deps_to_install:
            return True, "所有依赖已安装，无需安装"
        
        logger.info(f"开始安装依赖: {deps_to_install}")
        
        try:
            # 使用 poetry add 安装依赖
            cmd = [sys.executable, "-m", "poetry", "add"]
            cmd.extend(deps_to_install)
            
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            if result.returncode == 0:
                # 更新缓存
                self._cache_status.clear()
                return True, f"依赖安装成功: {', '.join(deps_to_install)}"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"依赖安装失败: {error_msg}")
                return False, f"安装失败: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "安装超时，请手动安装"
        except Exception as e:
            error_msg = str(e)
            logger.error(f"安装依赖时出错: {error_msg}")
            return False, f"安装出错: {error_msg}"
    
    def get_installation_status(self) -> Dict:
        """
        获取完整的安装状态报告
        
        Returns:
            Dict: 包含 ready 状态和详细信息的状态报告
        """
        status = self.check_all_dependencies()
        
        missing = [name for name, info in status.items() 
                   if not info["installed"] and not info["optional"]]
        
        return {
            "ready": len(missing) == 0,
            "dependencies": status,
            "missing_required": missing,
            "optional_available": [name for name, info in status.items() 
                                   if info["installed"] and info["optional"]],
            "optional_missing": [name for name, info in status.items() 
                                 if not info["installed"] and info["optional"]],
        }
    
    def verify_matplotlib_backend(self) -> Tuple[bool, str]:
        """
        验证 matplotlib 后端配置是否正确
        
        matplotlib 在无显示器环境下需要使用 Agg 后端
        
        Returns:
            Tuple[是否配置正确, 消息]
        """
        try:
            import matplotlib
            current_backend = matplotlib.get_backend()
            
            # 检查是否需要切换到 Agg 后端
            import os
            if os.environ.get("DISPLAY") is None and sys.platform != "win32":
                # Linux/macOS 无显示器环境
                if current_backend.lower() != "agg":
                    matplotlib.use("Agg")
                    return True, f"已切换到 Agg 后端 (当前: {current_backend})"
            
            return True, f"后端配置正常: {current_backend}"
            
        except Exception as e:
            return False, f"matplotlib 后端配置错误: {str(e)}"
    
    def ensure_imports(self) -> Tuple[bool, str]:
        """
        确保所有必需依赖可用
        
        注意：不自动安装依赖，只检查状态
        如果依赖缺失，返回错误信息
        
        Returns:
            Tuple[是否成功, 消息]
        """
        if self.is_ready():
            # 验证 matplotlib 后端
            backend_ok, backend_msg = self.verify_matplotlib_backend()
            if not backend_ok:
                return False, backend_msg
            
            return True, "所有依赖已就绪"
        
        # 有缺失的依赖
        missing = self.get_missing_dependencies()
        missing_versions = [REQUIRED_DEPENDENCIES[d] for d in missing]
        
        error_msg = (
            f"缺少必要的依赖: {', '.join(missing)}\n"
            f"请手动安装: pip install {' '.join(missing_versions)}"
        )
        logger.error(error_msg)
        return False, error_msg


# 全局单例
_dependency_manager: Optional[ChartDependencyManager] = None


def get_dependency_manager() -> ChartDependencyManager:
    """
    获取全局依赖管理器单例
    
    Returns:
        ChartDependencyManager: 依赖管理器实例
    """
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = ChartDependencyManager()
    return _dependency_manager


def check_chart_dependencies() -> Dict:
    """
    快速检查图表依赖状态
    
    Returns:
        Dict: 依赖状态信息
    """
    manager = get_dependency_manager()
    return manager.get_installation_status()


def ensure_chart_dependencies() -> Tuple[bool, str]:
    """
    确保图表依赖可用
    
    Returns:
        Tuple[是否成功, 消息]
    """
    manager = get_dependency_manager()
    return manager.ensure_imports()
