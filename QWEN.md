# Word Selection Assistant (智能划词助手) - 项目上下文

## 项目概述

Word Selection Assistant 是一个基于 PyQt6 的智能文本处理助手，集成了多模态 AI 能力，支持文本翻译、解释、总结和自定义功能处理。该项目提供了一个完整的桌面应用程序，允许用户通过全局热键（默认 Ctrl+Q）快速选择文本并将其发送给 AI 进行处理。

### 核心功能
- **文本翻译**: 支持多语言智能翻译
- **内容解释**: 智能解释文本含义和背景
- **内容总结**: 自动提取文本要点和总结
- **自定义功能**: 个性化AI功能配置和模型选择
- **图表生成**: 根据文本内容生成可视化图表
- **提示词优化**: 优化用户输入的提示词

### 技术栈
- **GUI框架**: PyQt6
- **AI集成**: OpenAI兼容API，支持Ollama本地服务和小马算力TokenPony服务
- **系统集成**: keyboard（全局热键）、pywin32（Windows API）
- **配置管理**: PyYAML、python-dotenv
- **异步处理**: asyncio、aiohttp

## 项目架构

### 分层架构
```
┌─────────────────────────────────────────────────────────────────┐
│                      main.py (入口层)                           │
│              WordSelectionAssistant (主控制器)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   UI Layer    │   │  Core Layer   │   │   AI Layer    │
│    (ui/)      │   │   (core/)     │   │    (ai/)      │
│               │   │               │   │               │
│ TrayIcon      │   │ HotkeyManager │   │ XiaomaAdapter │
│ PopupWindow   │   │ TextCapture   │   │ OpenAICompatible│
│ SettingsDialog│   │ FunctionRouter│   │ PromptGenerator│
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              Features Layer (features/)                  │
│   Translator  │  Explainer  │  Summarizer  │ Custom    │
│   ChartGen    │  PromptOpt  │  OCRHandler  │ VisionExp  │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│            Utils Layer (utils/)                         │
│ ConfigManager │ ThreadPoolManager │ EventLoopManager   │
│ ThemeManager  │ LocalCache │ Logger │ StreamHandler    │
└─────────────────────────────────────────────────────────┘
```

### 主要模块

#### 入口模块 (main.py)
- `WordSelectionAssistant` 类负责应用程序初始化
- 加载配置、创建组件、注册热键、管理系统托盘
- 连接所有功能模块

#### 核心功能 (core/)
- `hotkey_manager.py`: 全局热键管理，使用 keyboard 库实现
- `text_capture.py`: 文本捕获，通过剪贴板获取选中文本
- `function_router.py`: 功能路由器，分发请求到对应处理器

#### AI适配器 (ai/)
- `xiaoma_adapter.py`: OpenAI兼容API适配器
- `ollama_adapter.py`: Ollama本地API适配器，兼容OpenAI格式
- 支持多种AI模型，包括本地模型和云端模型
- 提供同步和流式API调用

#### 功能实现 (features/)
- `translator.py`: 翻译功能
- `explainer.py`: 解释功能
- `summarizer.py`: 总结功能
- `custom_builder.py`: 自定义功能构建器
- `chart_generator.py`: 图表生成功能
- `prompt_optimizer.py`: 提示词优化功能

#### 用户界面 (ui/)
- `popup_window.py`: 悬浮弹窗主窗口，支持流式输出
- `tray_icon.py`: 系统托盘图标管理
- `settings_dialog.py`: 设置对话框

#### 工具函数 (utils/)
- `config_manager.py`: 配置管理器
- `thread_pool_manager.py`: 线程池管理器
- `event_loop_manager.py`: 异步事件循环管理器
- `local_cache.py`: 本地缓存
- `theme_manager.py`: 主题管理器

## 配置系统

### 应用配置 (config/settings.yaml)
- AI API配置（模型选择、超时、流式输出等）
- 支持多个AI提供商（Ollama本地、小马算力云端）
- 热键配置（默认Ctrl+Q）
- 窗口配置（尺寸、位置、透明度等）
- 功能开关（翻译、解释、总结、自定义等）
- 缓存配置（启用、大小、过期时间等）

### 提示词模板 (config/prompt_templates.yaml)
- 翻译、解释、总结等功能的提示词模板
- 支持多种语言和详细程度的模板
- 自定义功能和图表生成的模板

### 环境变量 (.env)
- OLLAMA_BASE_URL: Ollama API基础URL
- OLLAMA_API_KEY: Ollama API密钥（通常不需要）
- OPENAI_API_KEY: OpenAI兼容API密钥
- OPENAI_BASE_URL: OpenAI兼容API基础URL

## 开发指南

### 环境设置
1. 创建Python虚拟环境（推荐Python 3.8+）
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量：复制 `.env.example` 为 `.env` 并填入API密钥
4. 运行应用：`python main.py`

### 代码规范
- 使用 snake_case 命名函数和变量
- 使用 PascalCase 命名类
- 所有函数和方法应包含类型注解
- 使用Google风格的文档字符串
- 遵循PEP 8代码风格

### 性能优化
- EventLoop复用：避免每次API调用创建新事件循环
- HTTP连接池：复用连接减少握手开销
- 配置缓存：缓存配置信息减少I/O操作
- 线程池管理：处理阻塞操作避免UI冻结
- 本地缓存：缓存API响应避免重复请求

### 测试策略
- 使用pytest进行单元测试
- 为新功能编写相应的测试用例
- 运行测试：`pytest tests/`
- 检查覆盖率：`pytest tests/ --cov=.`

## 已知问题与限制

### 平台限制
- 需要管理员权限才能正常工作（全局热键功能）
- 主要支持Windows平台（依赖pywin32和keyboard库）
- 托盘图标实现依赖Windows API

### 功能限制
- 需要网络连接才能使用AI功能
- 依赖外部AI API服务
- 当前只支持中文界面
- 需要安装matplotlib和numpy才能使用图表功能

### 开发注意事项
- 热键可能与其他程序冲突
- API密钥不应提交到版本控制系统
- 建议使用虚拟环境隔离依赖
- 新功能必须包含相应测试

## 扩展开发

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
2. 更新样式表CSS样式
3. 实现事件处理方法

## 项目维护

### 依赖管理
- 使用Poetry管理依赖（pyproject.toml）
- 定期更新依赖包以获得安全补丁
- 测试新版本的兼容性

### 日志管理
- 使用colorlog实现彩色日志输出
- 按照DEBUG/INFO/WARNING/ERROR/CRITICAL级别记录
- 日志文件存储在logs/目录

### 版本控制
- 遵循语义化版本控制
- 为每个版本维护更新日志
- 使用Git进行版本控制