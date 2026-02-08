#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama API 连接测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from ai.ollama_adapter import OllamaAdapter

async def test_ollama_connection():
    """测试Ollama连接"""
    print("正在测试Ollama API连接...")
    
    try:
        # 创建Ollama适配器实例
        adapter = OllamaAdapter(
            api_base="http://localhost:11434/v1"
        )
        
        print(f"API基础URL: {adapter.api_base}")
        print(f"默认模型: {adapter.model}")
        
        # 获取可用模型列表
        print("\n正在获取可用模型列表...")
        available_models = adapter.get_available_models()
        print(f"可用模型: {available_models}")
        
        # 测试非流式聊天
        print("\n正在测试非流式聊天...")
        messages = [
            {"role": "user", "content": "你好，请简单介绍一下自己。"}
        ]
        
        response = await adapter.chat(messages, temperature=0.7)
        print(f"响应ID: {response.get('id', 'N/A')}")
        print(f"使用模型: {response.get('model', 'N/A')}")
        
        choices = response.get('choices', [])
        if choices:
            content = choices[0].get('message', {}).get('content', 'N/A')
            print(f"AI回复: {content[:100]}...")  # 只显示前100个字符
        else:
            print("未收到有效响应")
        
        # 测试流式聊天
        print("\n正在测试流式聊天...")
        print("流式响应: ", end="")
        async for chunk in adapter.stream_chat(messages, temperature=0.7):
            if 'content' in chunk:
                print(chunk['content'], end="", flush=True)
            elif 'error' in chunk:
                print(f"\n错误: {chunk['error']}")
                break
        print()  # 换行
        
        print("\n✅ Ollama API连接测试成功!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ollama API连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ollama_connection())
    if not success:
        print("\n⚠️  请注意: Ollama服务可能未运行。请确保Ollama已安装并正在运行。")
        print("   启动Ollama服务的方法:")
        print("   1. 安装Ollama: https://ollama.com/download")
        print("   2. 启动Ollama服务: ollama serve")
        print("   3. 拉取模型: ollama pull llama3.2")
    sys.exit(0 if success else 1)