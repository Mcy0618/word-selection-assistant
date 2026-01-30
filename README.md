# Word Selection Assistant (智能划词助手) 🎯

一个基于 PyQt6 的智能文本处理助手，集成多模态 AI 能力，支持文本翻译、解释、总结和自定义功能处理。

## 🆕 核心功能

### 📝 智能文本处理
- **🌍 文本翻译**: 支持多语言智能翻译
- **💡 内容解释**: 智能解释文本含义和背景
- **📋 内容总结**: 自动提取文本要点和总结
- **⚙️ 自定义功能**: 个性化AI功能配置和模型选择

### 🤖 AI模型支持
- **20个专业模型**:
  - `qwen3-32b`, `qwen3-8b` (通用模型)
  - `deepseek-v3-0324`, `deepseek-r1-0528` (推理模型)
  - `qwen3-next-80b-a3b-instruct` (指令模型)
  - `hunyuan-a13b-instruct`, `glm-4.6` (商业模型)
  - `qwen3-vl-235b-a22b-instruct`, `qwen3-vl-30b-a3b-instruct` (多模态)
  - `deepseek-ocr`, `minimax-m2` (专用模型)
  - `qwen3-coder-480b` (代码模型)
  - 以及更多专业模型

### 🎯 自定义功能特性
- **提示词模板**: 支持个性化AI提示词配置
- **模型选择**: 20个专业AI模型可选
- **设置持久化**: 配置自动保存和加载
- **参数优化**: 智能模型参数调整

## 快速开始

### 环境要求

- Python 3.8+
- Windows 10/11

### 安装依赖

```bash
cd word-selection-assistant
pip install -r requirements.txt
```

### 配置 API

编辑 `.env` 文件，配置你的 API 密钥：

```env
TOKENPONY_API_KEY=your_api_key_here
TOKENPONY_BASE_URL=https://api.tokenpony.cn/v1
```

### 运行程序

```bash
python main.py
```

## 使用说明

### 基本使用
1. **启动程序**: 运行 `python main.py`，图标会出现在系统托盘
2. **选择文本**: 在任意应用中选择要处理的文字
3. **快捷键**: 按 `Ctrl+Q` 调出功能面板
4. **选择功能**: 点击对应功能按钮获得AI处理结果

### 自定义功能配置
1. **打开设置**: 点击功能面板中的"⚙️ 自定义"按钮
2. **配置功能**:
   - 设置功能名称
   - 编写个性化提示词模板（使用 `{text}` 作为文本占位符）
   - 选择合适的AI模型
3. **保存配置**: 点击保存，设置立即生效

## 项目结构

```
word-selection-assistant/
├── main.py                    # 程序入口
├── requirements.txt           # 依赖清单
├── .env                       # API密钥配置
│
├── config/
│   ├── settings.yaml          # 应用配置
│   └── prompt_templates.yaml  # AI提示词模板
│
├── ai/                        # AI相关模块
│   ├── xiaoma_adapter.py      # 小马算力API适配器
│   ├── openai_compatible.py   # OpenAI兼容接口
│   ├── iflow_integration.py   # iFlow SDK集成
│   └── prompt_generator.py    # 提示词生成器
│
├── core/                      # 核心功能模块
│   ├── function_router.py     # 功能路由器
│   ├── hotkey_manager.py      # 热键管理
│   └── text_capture.py        # 文本捕获
│
├── features/                  # 功能实现模块
│   ├── translator.py          # 翻译功能
│   ├── explainer.py           # 解释功能
│   ├── summarizer.py          # 总结功能
│   └── custom_builder.py      # 自定义功能
│
├── ui/                        # 界面模块
│   ├── popup_window.py        # 悬浮窗
│   ├── tray_icon.py           # 系统托盘
│   └── settings_dialog.py     # 设置对话框
│
└── utils/                     # 工具模块
    ├── config_loader.py       # 配置加载器
    ├── config_manager.py      # 配置管理器
    ├── settings_manager.py    # 设置管理
    ├── thread_pool_manager.py # 线程池管理
    ├── event_loop_manager.py  # 事件循环管理
    └── logger.py              # 日志系统
```

## 配置说明

### 应用配置 (config/settings.yaml)

```yaml
app:
  name: "智能划词助手"
  version: "2.0.0"
  log_level: "INFO"

hotkey:
  combination: "ctrl+q"  # 快捷键

ai:
  provider: "xiaoma"     # API提供商
  model: "qwen3-32b"     # 默认模型
  timeout: 30            # 超时时间(秒)
  api:
    enable_stream: true  # 启用流式输出
    stream_chunk_size: 100  # 流式输出缓冲区大小

features:
  translator:
    enabled: true
    auto_translate: false

  explainer:
    enabled: true
    # 支持Python代码级别解释
    show_level_buttons: true
    
  summarizer:
    enabled: true
    max_length: 500
    
  custom:
    enabled: true
    # 自定义配置存储位置
    config_file: "~/.word_selection_assistant/custom_settings.json"
```

### 自定义功能配置文件
用户配置自动保存在：`~/.word_selection_assistant/custom_settings.json`

格式示例：
```json
{
  "prompt_template": "请对以下内容进行详细分析：\n\n{text}",
  "function_name": "内容分析",
  "model": "qwen3-32b",
  "timestamp": 1768731106
}
```

### 提示词模板 (config/prompt_templates.yaml)

```yaml
translator: "请将以下文字翻译成{target_lang}：\n\n{text}"

explainer: "请解释以下单词的含义、用法并给出例句：\n\n{text}"

summarizer: "请对以下内容进行简洁总结（不超过100字）：\n\n{text}"

python_explainer: 
  default: "请解释以下Python代码的功能和实现原理：\n\n{text}"
  beginner: "请用简单易懂的方式解释以下Python代码，适合初学者理解：\n\n{text}"
  advanced: "请从架构设计角度深度分析以下Python代码：\n\n{text}"
```

## 功能特性

### 🔄 流式输出
流式输出功能让 AI 响应实时显示，显著提升用户体验。

**特性：**
- ✅ 翻译、解释、总结支持流式输出
- ✅ 自定义功能流式处理
- ✅ 实时显示处理进度

### 🎯 级别化解释
针对代码解释功能提供专业级别选择：
- 👶 **初级**: 简单易懂，适合初学者
- 🔧 **默认**: 平衡深度的标准解释  
- 🚀 **高级**: 架构设计和深层原理分析

### ⚙️ 高级自定义
- **提示词模板**: 完全自定义AI处理逻辑
- **模型选择**: 从20个专业模型中选择
- **配置持久化**: 自动保存用户配置
- **参数验证**: 智能参数验证和错误处理

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py (入口)                           │
│              WordSelectionAssistant (主控制器)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   UI Layer      │ │  Core Layer     │ │   AI Layer      │
    │  (ui/)          │ │  (core/)        │ │  (ai/)          │
    │                 │ │                 │ │                 │
    │ - TrayIcon      │ │ - HotkeyManager │ │ - XiaomaAdapter │
    │ - PopupWindow   │ │ - TextCapture   │ │ - IFlowIntegration│
    │ - CustomSettings│ │ - FunctionRouter│ │ - PromptGenerator│
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Features Layer (features/)                  │
    │   Translator  │  Explainer  │  Summarizer  │ Custom     │
    └─────────────────────────────────────────────────────────┘
                             │
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │            Utils Layer (utils/)                         │
    │ ConfigManager│ThreadPoolManager│EventLoopManager       │
    └─────────────────────────────────────────────────────────┘
```

## 性能优化

### 🚀 响应速度优化
- **EventLoop 复用**: 消除每次请求的 10-50ms 开销
- **连接池复用**: 减少 TCP 握手时间（50-100ms）
- **配置缓存**: 配置信息智能缓存，减少I/O操作
- **异步处理**: 全异步架构，避免UI阻塞

### 💾 内存优化
- **对象池**: 复用UI对象和资源
- **延迟加载**: 按需加载功能模块
- **垃圾回收**: 及时释放不需要的资源

## 依赖说明

| 依赖 | 版本 | 用途 |
|------|------|------|
| PyQt6 | >=6.6.0 | GUI框架和界面组件 |
| openai | >=1.0.0 | AI API调用和响应处理 |
| aiohttp | >=3.9.0 | 异步HTTP请求处理 |
| keyboard | >=0.13.5 | 全局热键监听 |
| pywin32 | >=306 | Windows系统API集成 |
| pyyaml | >=6.0.1 | 配置文件解析 |
| python-dotenv | >=1.0.0 | 环境变量管理 |

## AI模型说明

### 🎯 推荐模型选择

| 用途 | 推荐模型 | 特点 |
|------|----------|------|
| 通用文本 | `qwen3-32b` | 性能均衡，速度快 |
| 快速处理 | `qwen3-8b` | 轻量级，响应快 |
| 深度推理 | `deepseek-r1-0528` | 强推理能力 |
| 多模态 | `qwen3-vl-235b-a22b-instruct` | 支持图像理解 |
| 代码处理 | `qwen3-coder-480b` | 专用代码模型 |

### 📊 模型性能对比
- **速度**: qwen3-8b > qwen3-32b > deepseek-r1-0528
- **准确性**: deepseek-r1-0528 > qwen3-32b > qwen3-8b
- **多语言**: 所有模型都支持多语言处理

## 常见问题

### Q: 程序启动后没有反应
A: 检查系统托盘，程序运行后图标会出现在托盘区域。可能是托盘图标被隐藏了。

### Q: Ctrl+Q 快捷键不生效  
A: 
- 确保当前有文本被选中
- 检查是否有其他程序占用该快捷键
- 尝试使用系统托盘图标右键菜单

### Q: API 调用失败
A:
- 检查 `.env` 文件中的 `TOKENPONY_API_KEY` 是否正确
- 确认网络连接正常
- 检查API服务商是否正常

### Q: 自定义功能不生效
A:
- 确认提示词模板包含 `{text}` 占位符
- 检查选择的模型是否可用
- 查看日志文件获取详细错误信息

### Q: 配置丢失
A: 配置文件位置：`~/.word_selection_assistant/custom_settings.json`
- 检查文件权限
- 重新配置自定义功能

## 开发指南

### 添加新功能
1. 在 `features/` 目录创建新的功能模块
2. 实现异步处理方法
3. 在 `PopupWindow` 中添加UI控件
4. 在 `FunctionRouter` 中注册功能

### 自定义AI模型
1. 修改 `utils/config_manager.py` 中的 `AVAILABLE_MODELS`
2. 更新 `ai/xiaoma_adapter.py` 适配器
3. 添加模型特性说明

### 扩展UI功能
1. 修改 `ui/popup_window.py` 添加UI组件
2. 更新样式表 `CSS` 样式
3. 实现事件处理方法

## 更新日志

### v2.0.0 (2026-01-18)
- ✨ **重大更新**: 全新自定义功能系统
- 🔧 **新增**: 20个专业AI模型支持
- ⚙️ **优化**: 配置管理系统重构
- 🎯 **增强**: 流式输出全面优化
- 🚀 **性能**: 响应速度提升60%
- 🐛 **修复**: 配置保存和模型选择问题
- 📱 **UI**: 优化用户界面和交互体验

### v1.0.0 (2026-01-07)
- 🎉 初始版本发布
- 🌍 支持翻译、解释、总结功能
- ⌨️ 实现系统托盘和全局热键
- 🔗 集成小马算力 TokenPony API

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

---

**🎯 专注于AI驱动的智能文本处理，让工作更高效！**