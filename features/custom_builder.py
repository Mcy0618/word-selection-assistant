#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI辅助自定义功能模块
"""

import logging
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from ai.xiaoma_adapter import XiaomaAdapter
from ai.prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


@dataclass
class CustomFunction:
    """自定义功能配置"""
    name: str
    description: str
    prompt_template: str
    parameters: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CustomBuilder:
    """自定义功能构建器"""
    
    def __init__(self, adapter: Optional[XiaomaAdapter] = None, 
                 prompt_generator: Optional[PromptGenerator] = None):
        """
        初始化自定义功能构建器
        
        Args:
            adapter: API适配器
            prompt_generator: 提示词生成器
        """
        self.adapter = adapter
        self.prompt_generator = prompt_generator or PromptGenerator()
        self.custom_functions: Dict[str, CustomFunction] = {}
    
    def create_function(self, description: str, name: Optional[str] = None) -> CustomFunction:
        """
        根据描述创建自定义功能
        
        Args:
            description: 功能描述
            name: 功能名称（可选）
        
        Returns:
            CustomFunction: 创建的功能配置
        """
        func_name = name or description.split()[0] if description else "自定义功能"
        
        func = CustomFunction(
            name=func_name,
            description=description,
            prompt_template=self._generate_template(description)
        )
        
        self.custom_functions[func_name] = func
        return func
    
    def _generate_template(self, description: str) -> str:
        """生成提示词模板"""
        return f"""你是一个{description}助手。
当用户选中文本时，请按照以下要求处理：

用户选中：{{text}}

请提供专业的处理结果："""
    
    async def ai_optimize(self, description: str) -> Dict[str, Any]:
        """
        使用AI优化提示词
        
        Args:
            description: 功能描述
        
        Returns:
            Dict: 优化后的配置
        """
        if not self.adapter:
            return self._mock_optimize(description)
        
        try:
            optimization_prompt = f"""
请将以下功能描述转换为一个AI提示词模板：

功能描述：{description}

请返回JSON格式：
{{
    "name": "功能名称",
    "system_prompt": "系统提示词",
    "user_prompt": "用户提示词模板，使用{{{{text}}}}表示选中文本",
    "parameters": {{"参数": "说明"}}
}}
"""
            
            messages = [
                {"role": "system", "content": "你是一个AI助手功能设计专家。请将用户需求转换为AI提示词模板。"},
                {"role": "user", "content": optimization_prompt}
            ]
            
            response = await self.adapter.chat(messages)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 尝试解析JSON
            try:
                # 提取JSON部分
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
            except:
                pass
            
            return {"error": "无法解析AI返回的结果"}
            
        except Exception as e:
            logger.error(f"AI优化失败: {e}")
            return {"error": str(e)}
    
    def _mock_optimize(self, description: str) -> Dict[str, Any]:
        """模拟AI优化"""
        return {
            "name": "自定义功能",
            "system_prompt": f"你是一个{description}助手。",
            "user_prompt": f"请处理以下文本：\n\n{{text}}",
            "parameters": {}
        }
    
    def save_functions(self, file_path: str):
        """保存自定义功能到文件"""
        import json
        data = {
            name: func.to_dict() 
            for name, func in self.custom_functions.items()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存 {len(data)} 个自定义功能")
    
    def load_functions(self, file_path: str):
        """从文件加载自定义功能"""
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for name, config in data.items():
                    self.custom_functions[name] = CustomFunction(**config)
                logger.info(f"已加载 {len(self.custom_functions)} 个自定义功能")
        except FileNotFoundError:
            logger.warning(f"文件不存在: {file_path}")
        except Exception as e:
            logger.error(f"加载失败: {e}")
    
    def get_functions(self) -> Dict[str, Dict[str, str]]:
        """获取所有自定义功能"""
        return {
            name: {
                'name': func.name,
                'description': func.description
            }
            for name, func in self.custom_functions.items()
        }
    
    def delete_function(self, name: str) -> bool:
        """删除自定义功能"""
        if name in self.custom_functions:
            del self.custom_functions[name]
            return True
        return False
