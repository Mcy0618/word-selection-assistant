#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表生成功能模块
使用 LLM 分析文本并生成相应的图表
"""

import logging
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, AsyncGenerator, Tuple
from ai.xiaoma_adapter import XiaomaAdapter
from utils.local_cache import get_cache_manager
from utils.chart_dependency_manager import get_dependency_manager
from utils.chart_code_executor import ChartCodeExecutor

logger = logging.getLogger(__name__)


class ChartGenerator:
    """图表生成功能
    
    根据用户选中的文本，使用 LLM 分析并生成相应的图表。
    支持函数图、统计图、散点图等多种图表类型。
    """
    
    def __init__(self, adapter: Optional[XiaomaAdapter] = None, 
                 enable_cache: bool = True,
                 output_dir: Optional[str] = None):
        """
        初始化图表生成功能
        
        Args:
            adapter: API 适配器实例
            enable_cache: 是否启用缓存
            output_dir: 图表输出目录
        """
        self.adapter = adapter
        self.enable_cache = enable_cache
        self.cache_manager = get_cache_manager() if enable_cache else None
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "charts"
        self.output_dir.mkdir(exist_ok=True)
        
        self.code_executor = ChartCodeExecutor(self.output_dir)
        self.dep_manager = get_dependency_manager()
        
        # 默认配置
        self.default_figsize = (10, 8)
        self.default_dpi = 400  # 从 300 提升至 400
    
    async def can_draw_chart(self, text: str) -> Tuple[bool, str]:
        """
        判断文本是否包含可绘图内容
        
        Args:
            text: 用户选中的文本
        
        Returns:
            Tuple[是否可以绘图, 原因说明]
        """
        if not self.adapter:
            # 无 adapter 时，使用简单规则判断
            return self._simple_check(text)
        
        try:
            prompt = self._create_analysis_prompt(text)
            messages = [
                {"role": "system", "content": "你是一个数据分析助手，负责判断文本内容是否可以可视化为图表。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.adapter.chat(messages)
            result = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析 LLM 返回
            result_lower = result.lower().strip()
            
            if "yes" in result_lower or "可以" in result or "true" in result_lower:
                return True, "LLM 判断可以生成图表"
            else:
                reason = result.split("\n")[-1] if "\n" in result else result
                return False, f"LLM 判断: {reason}"
                
        except Exception as e:
            logger.error(f"判断图表生成能力失败: {e}")
            return self._simple_check(text)
    
    def _simple_check(self, text: str) -> Tuple[bool, str]:
        """简单的规则检查"""
        # 可绘图的关键词
        keywords = [
            # 数学函数
            r"sin|cos|tan|log|ln|exp|sqrt|pow",
            # 统计相关
            r"正态分布|均匀分布|指数分布|直方图|箱线图|散点图|折线图|柱状图",
            r"平均数|中位数|方差|标准差|概率",
            # 数据描述
            r"数据点|坐标|函数|方程|曲线|图形",
            # 数学表达式 - 支持 X + Y, Z = X + Y 等格式
            r"\d+\s*[\+\-\*\/]\s*\d+",  # 简单运算如 1+2, 3*4
            r"[xyzXYZ]=\s*[\w\+\-\*\/]+",  # 变量赋值如 Z = X + Y, y = sin(x)
            r"[a-zA-Z]\s*=\s*[a-zA-Z0-9\+\-\*\/\s]+",  # 通用变量赋值
        ]
        
        import re
        for pattern in keywords:
            if re.search(pattern, text, re.IGNORECASE):
                return True, f"匹配关键词模式: {pattern}"
        
        # 检查是否包含数据
        has_numbers = bool(re.search(r'\d+', text))
        has_text = len(text) > 10
        
        if has_numbers and has_text:
            return True, "检测到数字数据"
        
        return False, "未检测到可绘图内容"
    
    async def generate_chart(self, text: str, 
                            chart_type: Optional[str] = None) -> Dict:
        """
        生成图表
        
        Args:
            text: 用户选中的文本
            chart_type: 指定的图表类型，None 表示自动判断
        
        Returns:
            Dict: 包含 image_path 或 error 字段的字典
        """
        logger.info(f"开始生成图表，文本长度: {len(text)}")
        
        # 1. 确保依赖已安装
        deps_ok, deps_msg = self.dep_manager.ensure_imports()
        if not deps_ok:
            logger.error(f"依赖检查失败: {deps_msg}")
            return {"error": f"依赖安装失败: {deps_msg}"}
        
        # 2. 检查缓存
        if self.enable_cache and self.cache_manager:
            cache_key = self._generate_cache_key(text, chart_type)
            cached = self.cache_manager.get("chart", text, chart_type=chart_type)
            if cached:
                logger.debug("图表生成缓存命中")
                return json.loads(cached)
        
        # 3. 如果没有 adapter，直接使用 mock 代码（避免 LLM API 调用）
        if not self.adapter:
            logger.info("无 API 适配器，使用模拟代码生成")
            code_result = self._generate_mock_code(text, chart_type)
        else:
            # 有 adapter，生成图表代码
            logger.info("调用 LLM 生成图表代码")
            code_result = await self._generate_code(text, chart_type)
        
        if "error" in code_result:
            return code_result
        
        code = code_result["code"]
        chart_info = code_result.get("info", {})
        logger.info(f"代码生成成功，长度: {len(code)}")
        
        # 4. 执行代码生成图片
        logger.info("开始执行代码生成图片")
        exec_result = self.code_executor.execute_with_timeout(code)
        if "error" in exec_result:
            logger.error(f"代码执行失败: {exec_result['error']}")
            return exec_result
        
        logger.info(f"图表生成成功: {exec_result.get('image_path')}")
        
        result = {
            "success": True,
            "image_path": exec_result["image_path"],
            "description": chart_info.get("description", "图表生成成功"),
            "chart_type": chart_info.get("type", "自定义图表"),
            "code": code,
        }
        
        # 5. 缓存结果
        if self.enable_cache and self.cache_manager:
            self.cache_manager.set(
                "chart", text, json.dumps(result),
                chart_type=chart_type
            )
        
        return result
    
    async def generate_chart_stream(self, text: str, 
                                   chart_type: Optional[str] = None) -> AsyncGenerator[Dict, None]:
        """
        流式生成图表（带进度反馈）
        
        Args:
            text: 用户选中的文本
            chart_type: 指定的图表类型
        
        Yields:
            Dict: 包含进度信息的字典
        """
        # 阶段 1: 分析文本
        yield {"stage": "analyzing", "message": "正在分析文本内容...", "progress": 10}
        
        can_draw, reason = await self.can_draw_chart(text)
        if not can_draw:
            yield {"stage": "error", "message": f"无法生成图表: {reason}", "error": True}
            return
        
        # 阶段 2: 依赖检查
        yield {"stage": "checking_deps", "message": "检查依赖...", "progress": 20}
        deps_ok, deps_msg = self.dep_manager.ensure_imports()
        if not deps_ok:
            yield {"stage": "error", "message": f"依赖检查失败: {deps_msg}", "error": True}
            return
        
        # 阶段 3: 生成代码
        yield {"stage": "generating_code", "message": "正在生成图表代码...", "progress": 40}
        code_result = await self._generate_code(text, chart_type)
        
        if "error" in code_result:
            yield {"stage": "error", "message": code_result["error"], "error": True}
            return
        
        yield {"stage": "code_ready", "message": "代码生成完成", "progress": 50, "code_preview": code_result["code"][:200]}
        
        # 阶段 4: 执行代码
        yield {"stage": "executing", "message": "正在绘制图表...", "progress": 70}
        exec_result = self.code_executor.execute_with_timeout(code_result["code"])
        
        if "error" in exec_result:
            yield {"stage": "error", "message": f"绘图失败: {exec_result['error']}", "error": True}
            return
        
        # 阶段 5: 完成
        yield {
            "stage": "complete", 
            "message": "图表生成完成", 
            "progress": 100,
            "result": {
                "image_path": exec_result["image_path"],
                "description": code_result.get("info", {}).get("description", ""),
                "chart_type": code_result.get("info", {}).get("type", "自定义图表"),
            }
        }
    
    async def _generate_code(self, text: str, 
                            chart_type: Optional[str] = None) -> Dict:
        """
        生成 Python 绘图代码
        
        Args:
            text: 用户文本
            chart_type: 图表类型
        
        Returns:
            Dict: 包含 code 和 info 的字典
        """
        if not self.adapter:
            return self._generate_mock_code(text, chart_type)
        
        try:
            prompt = self._create_code_prompt(text, chart_type)
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.adapter.chat(messages)
            code = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 提取代码块
            code = self._extract_code(code)
            if not code:
                return {"error": "无法从响应中提取代码"}
            
            # 验证代码安全性
            safety_result = self.code_executor.validate_code(code)
            if not safety_result["safe"]:
                return {"error": f"代码安全检查失败: {safety_result['reason']}"}
            
            # 解析图表信息
            info = self._parse_chart_info(text, code)
            
            return {"code": code, "info": info}
            
        except Exception as e:
            logger.error(f"生成代码失败: {e}")
            return {"error": str(e)}
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个数据可视化专家，根据用户需求生成 Python 绑图代码。

要求：
1. 只返回可执行的 Python 代码，不要有其他说明
2. 使用 matplotlib、numpy 和 sklearn 进行绑图
3. 代码必须完整且可直接运行
4. 设置合适的中文字体和图表样式
5. 将图片保存到临时文件，使用全局变量 output_path

图表类型选择规则：
- 2维数据 → 2D图表（折线图、散点图、柱状图、直方图、饼图、箱线图、热力图）
- 3维数据 → 3D图表（3D散点图、3D曲面图、3D线图）
- 4+维数据 → 必须先降维再可视化（PCA/t-SNE/特征选择）

降维策略（4+维数据必须）：
- PCA降维：将数据降至3维用于3D可视化
- t-SNE降维：非线性降维，适合复杂数据结构
- 特征选择：选取最重要的3个特征

3D图表代码模板：
```python
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z, c='blue', s=50)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D散点图')
plt.savefig(output_path, dpi=400, bbox_inches='tight', facecolor='white')
print(f"IMAGE_SAVED:{output_path}")
```

2D图表代码模板：
```python
import matplotlib.pyplot as plt
import numpy as np
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(x, y, marker='o')
ax.set_title('折线图')
plt.savefig(output_path, dpi=400, bbox_inches='tight', facecolor='white')
print(f"IMAGE_SAVED:{output_path}")
```"""
    
    def _create_code_prompt(self, text: str, chart_type: Optional[str] = None) -> str:
        """创建代码生成提示词"""
        base_prompt = f"""请为以下内容生成 Python 绑图代码：

用户输入：
{text}
"""
        
        if chart_type:
            base_prompt += f"\n绑图类型: {chart_type}\n"
        else:
            base_prompt += "\n请根据内容自动判断合适的图表类型。\n"
        
        base_prompt += """
请生成完整的可执行代码，只返回代码，不需要解释。"""
        
        return base_prompt
    
    def _create_analysis_prompt(self, text: str) -> str:
        """创建分析提示词"""
        return f"""请判断以下文本内容是否可以通过图表可视化：

{text[:500]}

请回答：
1. 是否可以生成图表？(yes/no)
2. 建议的图表类型
3. 简要说明原因

格式：
YES/NO
图表类型: xxx
原因: xxx
"""
    
    def _extract_code(self, response: str) -> str:
        """从响应中提取代码块"""
        import re
        
        # 尝试提取 markdown 代码块
        patterns = [
            r'```python\s*\n([\s\S]*?)\n```',
            r'```\s*\n([\s\S]*?)\n```',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                code = match.group(1).strip()
                # 确保代码包含必要的导入
                if "plt.subplots" in code and "plt.savefig" in code:
                    return code
        
        # 如果没有代码块，尝试直接使用响应
        if "plt.subplots" in response and "plt.savefig" in response:
            lines = response.split("\n")
            code_lines = []
            in_code = False
            for line in lines:
                if "import" in line or "plt" in line or "np." in line or "print(" in line:
                    in_code = True
                if in_code:
                    code_lines.append(line)
            return "\n".join(code_lines)
        
        return ""
    
    def _generate_mock_code(self, text: str, 
                           chart_type: Optional[str] = None) -> Dict:
        """生成模拟代码（无 adapter 时）"""
        import numpy as np
        
        # 简单分析文本中的数据
        import re
        numbers = re.findall(r'[-+]?\d*\.?\d+', text)
        
        if len(numbers) >= 2:
            data_list = [float(n) for n in numbers[:10]]
        else:
            data_list = [1, 2, 3, 4, 5, 4, 3, 2, 1]
        
        # 生成代码 - 使用全局 output_path 变量和类 DPI 设置
        dpi = self.default_dpi
        code = f"""import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据
data = {data_list}

# 绑图
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(data, marker='o', linewidth=2, markersize=8)
ax.set_title('数据可视化', fontsize=16, fontweight='bold')
ax.set_xlabel('索引', fontsize=12)
ax.set_ylabel('值', fontsize=12)
ax.tick_params(axis='both', labelsize=10)
ax.grid(True, linestyle='--', alpha=0.7)

# 保存 - 高 DPI ({dpi})
# 使用全局变量 output_path（由执行器传入）
plt.savefig(output_path, dpi={dpi}, bbox_inches='tight', facecolor='white')
print(f"IMAGE_SAVED:{{output_path}}")
"""
        
        return {
            "code": code,
            "info": {
                "type": "折线图",
                "description": f"基于 {len(numbers)} 个数据点生成的可视化"
            }
        }
    
    def _parse_chart_info(self, text: str, code: str) -> Dict:
        """解析图表信息"""
        info = {"type": "自定义图表", "description": ""}
        
        # 从代码中推断图表类型
        if "scatter" in code:
            info["type"] = "散点图"
        elif "bar" in code:
            info["type"] = "柱状图"
        elif "hist" in code:
            info["type"] = "直方图"
        elif "plot" in code:
            info["type"] = "折线图"
        elif "pie" in code:
            info["type"] = "饼图"
        elif "boxplot" in code:
            info["type"] = "箱线图"
        elif "imshow" in code:
            info["type"] = "热力图"
        
        # 简单描述
        import re
        numbers = re.findall(r'\d+', text[:100])
        info["description"] = f"基于 {len(numbers)} 个数据点的 {info['type']}"
        
        return info
    
    def _generate_cache_key(self, text: str, chart_type: Optional[str]) -> str:
        """生成缓存键"""
        content = f"{text}:{chart_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_supported_types(self) -> list:
        """获取支持的图表类型"""
        return [
            "折线图", "散点图", "柱状图", "直方图", 
            "饼图", "箱线图", "热力图", "3D图", "自定义"
        ]
