#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词优化功能模块
"""

import logging
from typing import Dict, Any, Optional, AsyncGenerator
from ai.xiaoma_adapter import XiaomaAdapter
from utils.local_cache import get_cache_manager

logger = logging.getLogger(__name__)


class PromptOptimizer:
    """提示词优化功能"""

    def __init__(self, adapter: Optional[XiaomaAdapter] = None, enable_cache: bool = True):
        """
        初始化提示词优化功能

        Args:
            adapter: API适配器实例
            enable_cache: 是否启用缓存
        """
        self.adapter = adapter
        self.enable_cache = enable_cache
        self.cache_manager = get_cache_manager() if enable_cache else None

    async def optimize(self, text: str, recursive: bool = False) -> str:
        """
        优化提示词

        Args:
            text: 原始提示词文本
            recursive: 是否递归优化（优化提示词优化助手本身）

        Returns:
            str: 优化后的提示词
        """
        if not self.adapter:
            return self._mock_optimize(text, recursive)

        # 检查缓存
        if self.enable_cache and self.cache_manager:
            cached_result = self.cache_manager.get(
                "optimize", text,
                recursive=recursive
            )
            if cached_result is not None:
                logger.debug(f"提示词优化缓存命中: {text[:50]}...")
                return cached_result

        try:
            # 创建优化提示词
            prompt = self._create_optimization_prompt(text, recursive)

            # 系统提示词
            system_prompt = self._get_system_prompt(recursive)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            response = await self.adapter.chat(messages)
            result = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            # 缓存结果
            if self.enable_cache and self.cache_manager:
                self.cache_manager.set(
                    "optimize", text, result.strip(),
                    recursive=recursive
                )

            return result.strip()

        except Exception as e:
            logger.error(f"提示词优化失败: {e}")
            return f"提示词优化失败: {e}"

    async def optimize_stream(self, text: str, recursive: bool = False) -> AsyncGenerator[Dict[str, str], None]:
        """
        流式优化提示词

        Args:
            text: 原始提示词文本
            recursive: 是否递归优化

        Yields:
            Dict: 包含 'content' 字段的字典
        """
        if not self.adapter:
            yield {"content": self._mock_optimize(text, recursive)}
            return

        # 检查缓存
        if self.enable_cache and self.cache_manager:
            cached_result = self.cache_manager.get(
                "optimize", text,
                recursive=recursive
            )
            if cached_result is not None:
                logger.debug(f"提示词优化缓存命中（流式）: {text[:50]}...")
                # 模拟流式输出
                yield {"content": cached_result, "delta": False, "from_cache": True}
                return

        try:
            # 创建优化提示词
            prompt = self._create_optimization_prompt(text, recursive)

            # 系统提示词
            system_prompt = self._get_system_prompt(recursive)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            # 调用流式API
            full_result = ""
            async for chunk in self.adapter.stream_chat(messages):
                if "error" in chunk:
                    yield chunk
                    break

                content = chunk.get("content", "")
                if content:
                    full_result += content
                    yield {"content": content, "delta": True}

            # 缓存完整结果
            if self.enable_cache and self.cache_manager and full_result:
                self.cache_manager.set(
                    "optimize", text, full_result,
                    recursive=recursive
                )

        except Exception as e:
            logger.error(f"流式提示词优化失败: {e}")
            yield {"error": str(e)}

    def _get_system_prompt(self, recursive: bool) -> str:
        """获取系统提示词"""
        if recursive:
            return """你是一个提示词优化专家，专注构建与迭代用于"划词助手"的提示词生成系统，支持递归优化（即优化"提示词创建提示词优化助手"本身）。

请对输入文本进行语言与结构优化，使其成为高质量的提示词优化助手指令。"""

        return """你是一个提示词优化专家，专注构建与迭代用于"划词助手"的提示词生成系统。

请对输入文本进行语言与结构优化，使其成为高质量的提示词。"""

    def _create_optimization_prompt(self, text: str, recursive: bool) -> str:
        """创建优化提示词"""
        if recursive:
            return f"""请优化以下内容，使其成为高质量的提示词优化助手指令：

**优化准则**
1. **句式规范**  
   - 统一采用"动词 + 宾语"结构（如"提取关键词""重写句子"）  
   - 禁止出现主语（如"你""用户""系统"等代词）

2. **框架强化**  
   - 明确定义：
     - **输入**：原始提示词文本（由 `{{text}}` 提供）
     - **输出**：符合结构化标准的优化版提示词（Markdown 格式）
     - **边界**：仅重构表达，不增删功能或意图
     - **约束**：保留原始关键术语与核心目标

3. **清晰度提升**
   - 替换模糊表达（如"更好""优化一下"）为具体动作动词：
     - ✅ 使用："重构""拆分""替换""明确""限定""标准化"
     - ❌ 禁用："改进""弄好""调整一下"

4. **模型友好性**
   - 输出为结构化 Markdown，无冗余解释
   - 逻辑分层清晰，使用标题、列表、代码块等增强可解析性
   - 避免修辞性描述、情感化表达或抽象建议

**输出格式**
```markdown
# 优化后的提示词优化助手
[在此插入优化后的完整提示词优化助手内容]

---
**优化逻辑**：[一句话说明核心重构策略，聚焦表达形式的工程化升级]
**约束**：保留原始意图与关键术语，仅重构表达形式
```

**待优化的提示词优化助手**
{text}

优化后的提示词优化助手："""

        return f"""请对以下内容进行语言与结构优化，使其成为高质量的提示词：

**优化准则**
1. **句式规范**  
   - 统一采用"动词 + 宾语"结构（如"提取关键词""重写句子"）  
   - 禁止出现主语（如"你""用户""系统"等代词）

2. **框架强化**  
   - 明确定义：
     - **输入**：原始提示词文本（由 `{{text}}` 提供）
     - **输出**：符合结构化标准的优化版提示词（Markdown 格式）
     - **边界**：仅重构表达，不增删功能或意图
     - **约束**：保留原始关键术语与核心目标

3. **清晰度提升**
   - 替换模糊表达（如"更好""优化一下"）为具体动作动词：
     - ✅ 使用："重构""拆分""替换""明确""限定""标准化"
     - ❌ 禁用："改进""弄好""调整一下"

4. **模型友好性**
   - 输出为结构化 Markdown，无冗余解释
   - 逻辑分层清晰，使用标题、列表、代码块等增强可解析性
   - 避免修辞性描述、情感化表达或抽象建议

**输出格式**
```markdown
# 优化后的提示词
[在此插入优化后的完整提示词内容]

---
**优化逻辑**：[一句话说明核心重构策略，聚焦表达形式的工程化升级]
**约束**：保留原始意图与关键术语，仅重构表达形式
```

**待优化的提示词**
{text}

优化后的提示词："""

    def _mock_optimize(self, text: str, recursive: bool) -> str:
        """模拟优化结果"""
        if recursive:
            return f"""# 优化后的提示词优化助手

## 角色定位
作为提示词优化专家，专注构建与迭代用于"划词助手"的提示词生成系统，支持递归优化。

## 任务说明
对输入文本进行语言与结构优化。

## 优化准则
1. **句式规范**：统一采用"动词 + 宾语"结构，禁止出现主语
2. **框架强化**：明确定义输入、输出、边界和约束
3. **清晰度提升**：替换模糊表达为具体动作动词
4. **模型友好性**：输出结构化 Markdown，逻辑分层清晰

## 输出格式
```markdown
# 优化后的提示词
[优化后的提示词内容]

---
**优化逻辑**：[核心重构策略说明]
**约束**：保留原始意图与关键术语
```

---
**优化逻辑**：将描述性语言重构为结构化指令，明确输入输出格式，使用动作动词替代模糊表达
**约束**：保留原始意图与关键术语，仅重构表达形式"""
        
        return f"""# 优化后的提示词

[优化后的提示词内容]

---
**优化逻辑**：将描述性语言重构为结构化指令，明确输入输出格式，使用动作动词替代模糊表达
**约束**：保留原始意图与关键术语，仅重构表达形式"""