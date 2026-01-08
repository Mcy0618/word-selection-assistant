#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI提示词生成器
从配置文件加载和管理提示词模板
"""

import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptGenerator:
    """AI提示词生成器"""
    
    def __init__(self, template_file: str = None):
        """
        初始化提示词生成器
        
        Args:
            template_file: 模板文件路径
        """
        self.templates = {}
        self.template_file = template_file
        
        if template_file:
            self.load_templates(template_file)
    
    def load_templates(self, file_path: str):
        """加载模板文件"""
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'templates' in data:
                        self.templates = data['templates']
                    logger.info(f"已加载 {len(self.templates)} 个提示词模板")
            except Exception as e:
                logger.error(f"加载模板失败: {e}")
    
    def get_prompt(self, feature_type: str, text: str, 
                   context: Dict[str, Any] = None) -> str:
        """
        获取指定功能的提示词
        
        Args:
            feature_type: 功能类型（如 translator, explainer）
            text: 文本内容
            context: 上下文变量
        
        Returns:
            str: 完整的提示词
        """
        context = context or {}
        context['text'] = text
        
        # 查找模板
        if feature_type in self.templates:
            template = self.templates[feature_type]
            
            # 选择合适的子模板
            if isinstance(template, dict):
                # 根据上下文选择子模板
                sub_key = context.get('sub_type', 'default')
                if sub_key in template:
                    template = template[sub_key]
                else:
                    template = template.get('default', '')
            
            # 填充模板
            return self._fill_template(template, context)
        
        # 如果没有模板，返回默认
        return self._create_default_prompt(feature_type, text, context)
    
    def _fill_template(self, template: str, context: Dict[str, Any]) -> str:
        """填充模板变量"""
        result = template
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result.strip()
    
    def _create_default_prompt(self, feature_type: str, text: str, 
                               context: Dict[str, Any]) -> str:
        """创建默认提示词"""
        defaults = {
            "translator": f"请将以下文本翻译成{context.get('language', '中文')}:\n\n{text}",
            "explainer": f"请解释以下内容:\n\n{text}",
            "summarizer": f"请总结以下内容:\n\n{text}",
            "custom": f"请处理以下文本:\n\n{text}"
        }
        return defaults.get(feature_type, f"请处理:\n\n{text}")
    
    def generate_custom_prompt(self, description: str) -> Dict[str, Any]:
        """
        根据用户描述生成自定义功能的提示词
        
        Args:
            description: 用户的功能描述
        
        Returns:
            Dict: 包含name, prompt_template等的字典
        """
        # 基础模板
        base_prompt = f"""你是一个{description}助手。
当用户选中文本时，请按照以下要求处理：

用户选中: {{text}}

请提供专业的处理结果："""
        
        return {
            "name": description,
            "prompt_template": base_prompt,
            "description": f"自动生成的功能：{description}",
            "examples": []
        }
    
    def optimize_prompt(self, prompt: str) -> str:
        """
        优化提示词（简单版本）
        
        Args:
            prompt: 原始提示词
        
        Returns:
            str: 优化后的提示词
        """
        # 添加清晰的结构
        optimized = f"""任务要求：
{prompt}

请按照以下格式输出：
[处理结果]
"""
        return optimized
    
    def list_templates(self) -> Dict[str, Dict[str, str]]:
        """列出所有可用模板"""
        result = {}
        for key, value in self.templates.items():
            if isinstance(value, dict):
                result[key] = {
                    'name': key,
                    'description': value.get('description', ''),
                    'types': list(value.keys()) if key not in ('custom_generator',) else []
                }
            else:
                result[key] = {
                    'name': key,
                    'description': '',
                    'types': []
                }
        return result
