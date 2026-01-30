# Word Selection Assistant - AI 交互指南

本文档为 AI 助手提供项目的完整上下文，帮助快速理解代码库结构、高效进行代码修改和功能扩展。

## 项目概述

### 基本信息

| 属性 | 值 |
|------|-----|
| 项目名称 | Word Selection Assistant (智能划词助手) |
| 当前版本 | 2.0.0 |
| 项目类型 | Windows 桌面应用程序 |
| 主要语言 | Python 3.8+ |
| GUI 框架 | PyQt6 |
| 许可证 | 开源 (具体许可证见仓库) |

### 核心功能

智能划词助手是一个基于 AI 的全局划词文本处理工具，提供以下核心功能：

- **智能翻译**: 支持多语言智能翻译，集成 20+ 专业 AI 模型
- **内容解释**: 智能解释文本含义、背景知识和专业术语
- **内容总结**: 自动提取文本要点，生成简洁摘要
- **自定义功能**: 用户可配置 AI 提示词和模型选择
- **图像 OCR**: 支持图片划词识别和解释
- **流式输出**: 实时显示 AI 响应内容
- **主题切换**: 支持浅色/深色主题切换

### 目标用户

- 需要频繁处理多语言文本的用户
- 学习外语或专业知识的用户
- 需要快速理解长文本要点的用户
- 程序员和技术文档阅读者

---

## 技术栈详解

### 运行时环境

```
Python 3.8+ (推荐 Python 3.11 以获得最佳性能)
```

### 核心依赖

| 包名 | 版本要求 | 用途说明 |
|------|----------|----------|
| PyQt6 | >=6.6.0 | 桌面 GUI 框架，提供所有界面组件 |
| PyQt6-webengine | >=6.6.0 | Web 引擎支持，用于可能的 HTML 内容渲染 |
| openai | >=1.0.0 | OpenAI 兼容 API 客户端，用于调用 AI 模型 |
| aiohttp | >=3.9.0 | 异步 HTTP 客户端，支持并发 API 请求 |
| requests | >=2.31.0 | 同步 HTTP 请求，备用方案 |
| python-dotenv | >=1.0.0 | 环境变量管理，从 .env 文件加载配置 |
| pyyaml | >=6.0.1 | YAML 配置文件解析 |
| pillow | >=9.0.0 | 图像处理，支持 OCR 功能 |

### 系统集成依赖

| 包名 | 版本要求 | 用途说明 |
|------|----------|----------|
| pywin32 | >=306 | Windows API 集成，系统托盘、窗口控制 |
| keyboard | >=0.13.5 | 全局热键监听，捕获 Ctrl+Q 等快捷键 |
| pyperclip | >=1.8.2 | 剪贴板操作，复制粘贴文本 |
| colorlog | >=6.10.1 | 彩色日志输出，便于调试 |

### 开发工具依赖

| 包名 | 用途说明 |
|------|----------|
| pytest | 单元测试框架 |
| pytest-asyncio | 异步测试支持 |
| black | 代码格式化 |
| mypy | 类型检查 |
| pylint | 代码质量检查 |

---

## 目录结构

```
word-selection-assistant/
├── main.py                           # 应用程序入口点
├── requirements.txt                  # pip 依赖清单
├── pyproject.toml                    # Poetry 项目配置
├── .env.example                      # 环境变量配置模板
├── .env                              # 本地环境变量 (git 忽略)
├── README.md                         # 项目主文档
├── AGENTS.md                         # AI 交互指南 (本文档)
│
├── config/                           # 配置文件目录
│   ├── settings.yaml                 # 应用运行时配置
│   └── prompt_templates.yaml         # AI 提示词模板
│
├── ai/                               # AI 集成层
│   ├── __init__.py
│   ├── xiaoma_adapter.py             # 小马算力 TokenPony API 适配器
│   ├── openai_compatible.py          # OpenAI 兼容接口封装
│   ├── prompt_generator.py           # 动态提示词生成器
│   └── iflow_integration.py          # iFlow SDK 集成 (可选)
│
├── core/                             # 核心功能层
│   ├── __init__.py
│   ├── function_router.py            # 功能路由器，分发请求到对应处理器
│   ├── hotkey_manager.py             # 全局热键管理
│   └── text_capture.py               # 文本捕获和预处理
│
├── features/                         # 功能实现层
│   ├── __init__.py
│   ├── translator.py                 # 翻译功能实现
│   ├── explainer.py                  # 解释功能实现
│   ├── summarizer.py                 # 总结功能实现
│   ├── custom_builder.py             # 自定义功能构建器
│   ├── ocr_handler.py                # OCR 图像识别处理
│   └── vision_explainer.py           # 视觉多模态解释
│
├── ui/                               # 用户界面层
│   ├── __init__.py
│   ├── popup_window.py               # 悬浮弹窗主窗口 (1113 行)
│   ├── tray_icon.py                  # 系统托盘图标管理
│   └── settings_dialog.py            # 设置对话框
│
├── utils/                            # 工具函数层
│   ├── __init__.py
│   ├── config_loader.py              # 配置文件加载器
│   ├── config_manager.py             # 配置管理器
│   ├── settings_manager.py           # 设置管理器
│   ├── theme_manager.py              # 主题管理器
│   ├── logger.py                     # 日志系统
│   ├── thread_pool_manager.py        # 线程池管理器
│   ├── event_loop_manager.py         # 异步事件循环管理器
│   ├── local_cache.py                # 本地缓存
│   ├── stream_handler.py             # 流式输出处理器
│   └── stream_handler.py             # (重复) 流式输出处理器
│
├── logs/                             # 日志输出目录
├── tests/                            # 测试文件目录
│   ├── __init__.py
│   └── test_*.py                     # 各模块测试用例
│
├── .vscode/                          # VS Code 配置
│   ├── settings.json
│   └── extensions.json
│
├── .venv/ 或 venv/                   # Python 虚拟环境
└── .gitignore                        # Git 忽略规则
```

---

## 架构设计

### 分层架构

项目采用经典的分层架构设计，从上到下依次为：

```
┌─────────────────────────────────────────────────────────────────┐
│                      main.py (入口层)                           │
│              WordSelectionAssistant (主控制器)                   │
│     初始化配置 → 创建组件 → 注册热键 → 显示托盘 → 生命周期管理   │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   UI Layer    │   │  Core Layer   │   │   AI Layer    │  ← 表现层
│    (ui/)      │   │   (core/)     │   │    (ai/)      │
│               │   │               │   │               │
│ TrayIcon      │   │ HotkeyManager │   │ XiaomaAdapter │
│ PopupWindow   │   │ TextCapture   │   │ OpenAICompatible│
│ SettingsDialog│   │ FunctionRouter│   │ IFlowIntegration│
│               │   │               │   │ PromptGenerator│
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              Features Layer (features/)                  │  ← 业务逻辑层
│   Translator  │  Explainer  │  Summarizer  │ Custom     │
│   OCRHandler  │  VisionExplainer                               │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│            Utils Layer (utils/)                         │  ← 基础设施层
│ ConfigManager │ ThreadPoolManager │ EventLoopManager   │
│ ThemeManager  │ LocalCache │ Logger │ StreamHandler    │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    External Services                     │
│           TokenPony AI API (小马算力)                    │
└─────────────────────────────────────────────────────────┘
```

### 模块职责划分

| 层级 | 模块 | 主要职责 |
|------|------|----------|
| **入口层** | main.py | 应用初始化、组件连接、生命周期管理 |
| **表现层** | ui/ | 用户界面、交互响应、界面状态管理 |
| **表现层** | core/ | 核心功能协调、热键管理、文本捕获 |
| **表现层** | ai/ | AI API 集成、提示词生成、响应处理 |
| **业务逻辑层** | features/ | 具体功能实现（翻译、解释、总结等） |
| **基础设施层** | utils/ | 配置管理、日志、缓存、线程管理 |

### 数据流向

```
用户操作 (热键/托盘)
        │
        ▼
┌─────────────────┐
│ hotkey_manager  │ ← 捕获全局热键
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ text_capture    │ ← 获取选中文本
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ function_router │ ← 路由到对应功能
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
┌───────┐ ┌───────┐ ┌────────┐ ┌────────┐
│Trans- │ │Explain│ │Summarize│ │Custom  │ ← features/
│lator  │ │       │ │        │ │Builder │
└───┬───┘ └───┬───┘ └────┬───┘ └────┬───┘
    │         │          │          │
    └────┬────┴──────────┴──────────┘
         │
         ▼
┌─────────────────────────────────┐
│        ai/xiaoma_adapter        │ ← 调用 AI API
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│       popup_window              │ ← 显示结果
└─────────────────────────────────┘
```

---

## 核心模块详解

### 入口模块 (main.py)

**文件路径**: `core/main.py`

**主要类**: `WordSelectionAssistant`

**核心功能**:
- 应用程序初始化和配置加载
- 创建并连接所有组件
- 注册全局热键 (默认 Ctrl+Q)
- 创建和管理系统托盘图标
- 应用程序生命周期管理
- 优雅退出处理

**关键方法**:
```python
class WordSelectionAssistant:
    def __init__(self)          # 初始化所有组件
    def setup_components(self)  # 设置组件连接
    def setup_hotkeys(self)     # 注册全局热键
    def setup_tray_icon(self)   # 创建托盘图标
    def run(self)              # 启动应用主循环
    def shutdown(self)         # 清理和退出
```

**依赖注入**:
- `ConfigManager` - 配置管理
- `HotkeyManager` - 热键管理
- `ThreadPoolManager` - 线程池
- `EventLoopManager` - 异步事件循环
- `FunctionRouter` - 功能路由

### 功能路由器 (core/function_router.py)

**文件路径**: `core/function_router.py`

**功能类型枚举**:
```python
class FunctionType(Enum):
    TRANSLATE = "translate"     # 翻译功能
    EXPLAIN = "explain"         # 解释功能
    SUMMARIZE = "summarize"     # 总结功能
    CUSTOM = "custom"           # 自定义功能
```

**核心方法**:
```python
class FunctionRouter:
    def register_handler(ft: FunctionType, handler: Callable)  # 注册处理器
    async def route(text: str, ft: FunctionType) -> str       # 路由执行
    def get_available_functions() -> List[FunctionType]        # 获取可用功能
```

**设计模式**: 策略模式 + 简单工厂模式

### AI 适配器 (ai/xiaoma_adapter.py)

**文件路径**: `ai/xiaoma_adapter.py`

**支持的 AI 模型** (20+ 专业模型):

| 模型类别 | 模型名称 | 用途 |
|----------|----------|------|
| **通用大模型** | qwen3-32b | 通用对话和推理 |
| | qwen3-8b | 轻量级通用对话 |
| | glm-4-plus | 智谱 AI 通用模型 |
| **推理模型** | deepseek-r1-0528 | 深度推理任务 |
| | qwen3-32b-think | 思考增强模型 |
| **多模态模型** | qwen3-vl-235b-a22b-instruct | 视觉理解 |
| | qwen3-vl-32b-a3b-instruct | 轻量级视觉 |
| **代码模型** | qwen3-coder-480b | 代码生成和理解 |
| | qwen3-coder-32b | 轻量级代码 |
| | deepseek-coder-v2 | 代码专项模型 |
| **OCR 模型** | deepseek-ocr | 图像文字识别 |
| | qwen3-ocr-32b | 阿里 OCR |
| **嵌入模型** | qwen3-embedding-8b | 文本向量化 |
| | bge-m3 | 检索增强嵌入 |
| **数学模型** | qwen3-math-72b | 数学计算 |
| | qwen3-math-32b | 轻量级数学 |
| **医疗模型** | qwen3-medical-72b | 医疗领域 |
| **法律模型** | qwen3-legal-72b | 法律领域 |
| **金融模型** | qwen3-finance-72b | 金融领域 |

**核心方法**:
```python
class XiaomaAdapter:
    def __init__(api_key: str, base_url: str)
    async def chat(messages: List[Dict], model: str) -> str           # 同步聊天
    async def stream_chat(messages: List[Dict], model: str) -> AsyncIterator[str]  # 流式聊天
    def get_available_models() -> List[str]                           # 获取模型列表
```

**特性**:
- OpenAI 兼容格式 API
- 支持流式输出 (Server-Sent Events)
- HTTP 连接池复用
- 自动重试和错误处理

### 图表生成器 (features/chart_generator.py)

**文件路径**: `features/chart_generator.py`

**功能**: 根据用户选中的文本，使用 LLM 分析并生成对应的图表

**核心方法**:
```python
class ChartGenerator:
    def __init__(adapter: XiaomaAdapter, executor: ChartCodeExecutor)
    async def generate_chart(text: str) -> Dict[str, str]  # 生成图表
```

**处理流程**:
1. **文本分析**: 调用 LLM 判断文本是否包含可绘图信息
2. **代码生成**: 根据分析结果生成 Python 绑图代码
3. **代码执行**: 安全执行生成的代码，生成图片
4. **返回结果**: 返回图片路径和描述

**返回格式**:
```python
{
    "image_path": "/path/to/chart_abc123.png",
    "description": "正弦函数 y=sin(x) 在 [0, 2π] 范围内的图像"
}
```

**错误返回**:
```python
{"error": "错误描述信息"}
```

### 图表代码执行器 (utils/chart_code_executor.py)

**文件路径**: `utils/chart_code_executor.py`

**功能**: 安全地执行 LLM 生成的绑图代码

**核心方法**:
```python
class ChartCodeExecutor:
    def __init__(output_dir: Path, timeout: int)
    def validate_code(code: str) -> Dict  # 验证代码安全性
    def execute(code: str) -> Dict        # 执行代码
    def execute_with_timeout(code: str) -> Dict  # 带超时执行
    def cleanup_old_files(max_age: int, max_files: int)  # 清理旧文件
```

**安全特性**:
- 检查禁止的操作 (import os, exec, open 等)
- 验证必要的 matplotlib 导入
- 强制使用 Agg 后端（无显示器环境）
- 超时保护 (默认 30 秒)

**支持的绑图库**:
- `matplotlib` - 基础绑图（函数图、散点图、柱状图等）
- `numpy` - 数值计算支持

### 依赖管理器 (utils/chart_dependency_manager.py)

**文件路径**: `utils/chart_dependency_manager.py`

**功能**: 检测和安装图表功能所需的依赖

**核心方法**:
```python
class ChartDependencyManager:
    @staticmethod
    def check_dependencies() -> Dict  # 检测依赖是否安装
    @staticmethod
    def install_dependencies() -> bool  # 安装依赖
    @staticmethod
    def ensure_dependencies() -> bool   # 确保依赖已安装
```

**检测的依赖**:
| 包名 | 用途 | 必需性 |
|------|------|--------|
| `matplotlib` | 主要绑图库 | 必需 |
| `numpy` | 数值计算 | 必需 |
| `pillow` | 图像处理 | 可选 |

**检测结果示例**:
```python
{
    "matplotlib": {"installed": True, "version": "3.8.0"},
    "numpy": {"installed": True, "version": "1.24.0"},
    "all_installed": True
}
```

### 悬浮窗 UI (ui/popup_window.py)

**文件路径**: `ui/popup_window.py`

**行数**: 1113 行

**核心功能**:
- 显示功能按钮 (翻译、解释、总结、自定义)
- 显示 AI 处理结果
- 流式输出实时显示
- 加载动画和进度指示
- 拖拽支持 (图片 OCR)
- 自动隐藏和位置调整
- 主题切换 (浅色/深色)

**核心组件**:
```python
class PopupWindow(QWidget):
    def show_at(x: int, y: int, text: str)  # 在指定位置显示
    async def process_request(text: str, func_type: FunctionType)  # 处理请求
    def update_content(content: str)         # 更新显示内容
    def show_loading()                       # 显示加载状态
    def hide()                               # 隐藏窗口
```

**UI 元素**:
- 功能按钮栏 (翻译、解释、总结、自定义)
- 结果显示区域 (QTextEdit)
- 复制按钮
- 加载动画 (QLabel + 动画)
- 拖拽区域 (支持图片文件)

### 热键管理 (core/hotkey_manager.py)

**文件路径**: `core/hotkey_manager.py`

**默认热键**: `Ctrl+Q`

**实现方式**: 使用 `keyboard` 库实现全局热键监听

**核心方法**:
```python
class HotkeyManager:
    def __init__(callback: Callable)
    def register(combo: str)  # 注册热键
    def unregister(combo: str)  # 注销热键
    def start_listening()     # 开始监听
    def stop_listening()      # 停止监听
```

**注意事项**:
- 需要管理员权限才能正常工作
- 只在 Windows 平台上支持
- 避免与系统热键冲突

---

## 配置系统

### 应用配置 (config/settings.yaml)

**文件路径**: `config/settings.yaml`

```yaml
# 应用程序配置
app:
  name: "智能划词助手"
  version: "2.0.0"
  theme: "light"  # light 或 dark

# 热键配置
hotkey:
  enabled: true
  combination: "ctrl+q"

# AI 配置
ai:
  default_provider: "xiaoma"  # 默认 AI 提供商
  xiaoma:
    model: "qwen3-32b"  # 默认使用千问 32B 模型
  api:
    enable_stream: true  # 启用流式输出
    timeout: 30  # API 超时时间（秒）

# 窗口配置
window:
  width: 400
  height: 300
  position: "auto"  # 自动定位或指定坐标

# 缓存配置
cache:
  enabled: true
  max_size: 1000  # 最大缓存条目数
  ttl: 3600  # 缓存过期时间（秒）
```

### 提示词模板 (config/prompt_templates.yaml)

**文件路径**: `config/prompt_templates.yaml`

**模板结构**:
```yaml
translation:
  default: "请将以下文本翻译成中文，保持原文的格式和风格：\n\n{{text}}"
  formal: "请将以下正式文本翻译成中文：\n\n{{text}}"
  casual: "请将以下口语化文本翻译成中文：\n\n{{text}}"

explanation:
  beginner: |
    请用简单易懂的语言解释以下文本：
    {{text}}
    
    请：
    1. 用简单的词汇解释
    2. 提供日常生活的例子
    3. 保持解释简短（100字以内）
  
  default: |
    请解释以下文本的含义和背景：
    {{text}}
  
  advanced: |
    请详细解释以下文本，包括：
    {{text}}
    
    请涵盖：
    1. 字面含义
    2. 深层含义
    3. 历史背景
    4. 相关概念

summarization:
  brief: "请用一句话总结以下文本：\n\n{{text}}"
  default: "请总结以下文本的要点：\n\n{{text}}"
  detailed: |
    请详细总结以下文本：
    {{text}}
    
    格式：
    - 主要观点
    - 关键细节
    - 结论

python_explainer: |
  请解释以下 Python 代码：
  ```python
  {{text}}
  ```
  
  请涵盖：
  1. 代码功能概述
  2. 关键语法点
  3. 可能的改进建议

chart_generator:
  analyze: |
    你是一个图表生成专家。请分析以下文本，判断是否包含可绘制成图表的信息。
    
    用户选中的文本：{{text}}
    
    请分析并返回JSON格式...
  
  code_generation: |
    你是一个Python绑图专家。根据分析结果，生成绑制图表的Python代码。
    
    用户选中的文本：{{text}}
    
    要求：
    1. 使用matplotlib绑制图表
    2. 必须包含 plt.savefig(output_path) 保存图片
    3. 使用 Agg 后端（无显示器环境）
    4. 代码要简洁、正确
```

**模板变量**:
- `{{text}}` - 被处理的文本内容
- `{{chart_type}}` - 图表类型（图表生成）
- `{{description}}` - 图表描述（图表生成）
- `{{parameters}}` - 绑图参数（图表生成）

### 环境变量 (.env)

**文件模板**: `.env.example`

```env
# TokenPony API 配置 (小马算力)
TOKENPONY_API_KEY=your_tokenpony_api_key_here
TOKENPONY_BASE_URL=https://api.tokenpony.cn/v1

# 可选：自定义 API 配置
# CUSTOM_API_KEY=
# CUSTOM_BASE_URL=
```

**环境变量加载顺序**:
1. 系统环境变量
2. `.env` 文件变量
3. 默认值

### 自定义设置

**存储位置**: `~/.word_selection_assistant/custom_settings.json`

**示例结构**:
```json
{
  "prompt_template": "请用一句话解释：{{text}}",
  "function_name": "一句话解释",
  "model": "qwen3-8b",
  "temperature": 0.7,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 开发指南

### 环境设置

#### 1. 克隆仓库

```bash
git clone https://github.com/MCY0618/word-selection-assistant.git
cd word-selection-assistant
```

#### 2. 创建虚拟环境

**使用 venv**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

**使用 Poetry**:
```bash
poetry install
poetry shell
```

#### 3. 安装依赖

**pip 方式**:
```bash
pip install -r requirements.txt
```

**Poetry 方式**:
```bash
poetry install
```

#### 4. 配置环境变量

```bash
copy .env.example .env
# 编辑 .env 文件，填入 API Key
```

#### 5. 运行应用

```bash
python main.py
```

**注意**: 需要以管理员权限运行以支持全局热键功能。

### 开发命令

| 命令 | 说明 |
|------|------|
| `python main.py` | 启动应用程序 |
| `pytest tests/` | 运行所有测试 |
| `pytest tests/ -v` | 运行测试并显示详情 |
| `pytest tests/ --cov` | 运行测试并检查覆盖率 |
| `black .` | 代码格式化 |
| `mypy .` | 类型检查 |
| `pylint .` | 代码质量检查 |

### 代码风格规范

#### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 类名 | PascalCase | `PopupWindow`, `FunctionRouter` |
| 函数/变量 | snake_case | `get_available_models`, `api_key` |
| 常量 | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT`, `MAX_CACHE_SIZE` |
| 私有方法 | `_snake_case` | `_load_config`, `_init_components` |
| 模块名 | snake_case | `text_capture`, `hotkey_manager` |

#### 类型注解

所有公开函数和方法应包含类型注解：

```python
from typing import List, Dict, Optional, AsyncIterator

async def process_text(
    self,
    text: str,
    func_type: FunctionType,
    model: Optional[str] = None
) -> str:
    """处理文本并返回 AI 响应。"""
    ...
```

#### 文档字符串

使用 Google 风格的文档字符串：

```python
def translate(text: str, target_lang: str = "zh") -> str:
    """将文本翻译成目标语言。
    
    Args:
        text: 要翻译的源文本
        target_lang: 目标语言代码，默认中文
    
    Returns:
        翻译后的文本
    
    Raises:
        TranslationError: 翻译失败时抛出
    """
    ...
```

#### 导入顺序

```python
# 标准库导入
import asyncio
from typing import List, Dict
from enum import Enum

# 第三方库导入
from PyQt6.QtWidgets import QWidget, QLabel
from openai import AsyncOpenAI

# 本地模块导入
from core.function_router import FunctionType
from ai.xiaoma_adapter import XiaomaAdapter
```

### 日志规范

项目使用 `colorlog` 实现彩色日志输出：

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

**日志级别**:
- `DEBUG`: 详细调试信息
- `INFO`: 一般运行信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 异常处理

```python
from utils.exceptions import APIError, ConfigurationError

try:
    result = await adapter.chat(messages, model)
except APIError as e:
    logger.error(f"API 调用失败: {e}")
    return f"请求失败: {str(e)}"
except ConfigurationError as e:
    logger.error(f"配置错误: {e}")
    raise
```

---

## 性能优化

### 1. EventLoop 复用

**问题**: 每次 API 调用创建新的 asyncio 事件循环会有 10-50ms 开销

**解决方案**: 使用 `EventLoopManager` 复用事件循环

```python
from utils.event_loop_manager import EventLoopManager

loop_manager = EventLoopManager()
async with loop_manager.run() as loop:
    result = await adapter.chat(messages, model)
```

### 2. HTTP 连接池

**问题**: 频繁创建 HTTP 连接有 50-100ms TCP 握手开销

**解决方案**: 使用 `aiohttp` 的连接池功能

```python
from ai.xiaoma_adapter import XiaomaAdapter

adapter = XiaomaAdapter(
    api_key=api_key,
    base_url=base_url,
    use_pool=True,  # 启用连接池
    pool_size=10    # 连接池大小
)
```

### 3. 配置缓存

**问题**: 每次请求都从文件读取配置

**解决方案**: 使用 `ConfigManager` 缓存配置

```python
from utils.config_manager import ConfigManager

config = ConfigManager()
api_key = config.get("TOKENPONY_API_KEY")  # 自动缓存
```

### 4. 线程池管理

**问题**: 同步阻塞操作会阻塞主线程

**解决方案**: 使用 `ThreadPoolManager` 处理阻塞操作

```python
from utils.thread_pool_manager import ThreadPoolManager

pool = ThreadPoolManager()

# 在后台线程执行
result = await pool.run_sync(heavy_computation, text)
```

### 5. 本地缓存

**问题**: 重复调用相同文本的 API

**解决方案**: 使用 `LocalCache` 缓存响应

```python
from utils.local_cache import LocalCache

cache = LocalCache()

@cache.cached(ttl=3600)
async def translate_cached(text: str, target_lang: str) -> str:
    return await translate(text, target_lang)
```

---

## 已知问题与注意事项

### 平台限制

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| **管理员权限** | 全局热键需要管理员权限 | 右键以管理员身份运行 |
| **Windows 专用** | `pywin32` 和 `keyboard` 只支持 Windows | 考虑跨平台重设计 |
| **托盘图标** | 系统托盘实现依赖 Windows API | 使用 `pystray` 跨平台替代 |

### API 依赖

| 问题 | 说明 |
|------|------|
| **网络依赖** | 需要网络连接才能使用 AI 功能 |
| **TokenPony 依赖** | 主要使用小马算力 API |
| **速率限制** | 可能受 API 速率限制影响 |

### 功能限制

| 问题 | 说明 |
|------|------|
| **单语言界面** | 当前只支持中文界面 |
| **固定热键** | 热键组合不可自定义（当前） |
| **无离线模式** | 需要 AI API，无法完全离线使用 |
| **图表功能依赖** | 需要安装 matplotlib 和 numpy 才能使用图表功能 |

### 开发注意事项

1. **热键冲突**: 使用 `keyboard` 库可能与其他程序的热键冲突
2. **API Key 安全**: 永远不要将 API Key 提交到版本控制
3. **虚拟环境**: 开发时必须使用虚拟环境隔离依赖
4. **测试覆盖**: 新功能必须有对应的单元测试

---

## 测试指南

### 测试结构

```
tests/
├── __init__.py
├── conftest.py           # pytest 配置和 fixture
├── test_core/
│   ├── __init__.py
│   ├── test_function_router.py
│   └── test_hotkey_manager.py
├── test_ai/
│   ├── __init__.py
│   └── test_xiaoma_adapter.py
├── test_features/
│   ├── __init__.py
│   ├── test_translator.py
│   └── test_explainer.py
└── test_ui/
    ├── __init__.py
    └── test_popup_window.py
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定模块
pytest tests/test_core/

# 运行特定测试
pytest tests/test_core/test_function_router.py::test_route

# 生成覆盖率报告
pytest tests/ --cov=.
```

### 编写测试

```python
import pytest
from core.function_router import FunctionRouter, FunctionType

class TestFunctionRouter:
    def setup_method(self):
        self.router = FunctionRouter()
    
    def test_register_handler(self):
        async def dummy_handler(text: str) -> str:
            return text
        
        self.router.register_handler(FunctionType.TRANSLATE, dummy_handler)
        assert FunctionType.TRANSLATE in self.router._handlers
    
    @pytest.mark.asyncio
    async def test_route_success(self):
        async def echo_handler(text: str) -> str:
            return f"processed: {text}"
        
        self.router.register_handler(FunctionType.EXPLAIN, echo_handler)
        result = await self.router.route("test", FunctionType.EXPLAIN)
        assert result == "processed: test"
```

---

## 贡献指南

### 提交约定

#### 提交消息格式

```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

**类型标识**:

| 类型 | 描述 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构 |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建或辅助工具修改 |

**示例**:

```
feat(ai): 添加新模型 qwen3-32b 支持

- 实现模型选择逻辑
- 添加模型配置验证
- 更新文档

Closes #123
```

### 分支策略

```
main          # 主分支，始终保持稳定
  │
  ├── develop # 开发分支
  │     │
  │     ├── feature/new-translation-feature  # 功能分支
  │     ├── feature/ui-improvements          # UI 改进
  │     └── bugfix/fix-hotkey-issue          # Bug 修复
  │
  └── release/v2.1.0  # 发布分支
```

### 代码审查流程

1. **创建功能分支**: `feature/xxx` 或 `bugfix/xxx`
2. **开发并测试**: 确保所有测试通过
3. **提交更改**: 遵循提交消息约定
4. **创建 Pull Request**: 描述变更内容和原因
5. **代码审查**: 至少一位维护者审查
6. **合并到 develop**: 通过审查后合并
7. **定期发布**: 从 develop 合并到 main 并发布

### 行为准则

- 尊重所有贡献者
- 使用包容性语言
- 接受建设性批评
- 专注于项目最佳利益

---

## 常见任务指南

### 添加新功能

1. **在 features/ 中创建新模块**
2. **实现功能处理器**
3. **注册到 FunctionRouter**
4. **添加 UI 按钮** (如需要)
5. **编写单元测试**
6. **更新文档**

#### 示例：添加图表生成功能

```python
# 1. 创建 features/chart_generator.py
from features.base import BaseFeature

class ChartGenerator(BaseFeature):
    async def process(self, text: str) -> dict:
        # 实现图表生成逻辑
        return {"image_path": "path/to/chart.png"}
```

```python
# 2. 注册到 core/function_router.py
from core.function_router import FunctionRouter, FunctionType

class FunctionRouter:
    def __init__(self):
        self._handlers = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        # 添加图表生成处理器
        from features.chart_generator import ChartGenerator
        self._handlers[FunctionType.CHART] = ChartGenerator().process
```

```python
# 3. 在 UI 中添加按钮 (ui/popup_window.py)
self.chart_button = QPushButton("📊 绘图")
self.chart_button.clicked.connect(self._on_chart_clicked)
```

```python
# 4. 编写测试 (tests/test_features/test_chart_generator.py)
import pytest
from features.chart_generator import ChartGenerator

class TestChartGenerator:
    def setup_method(self):
        self.generator = ChartGenerator()
    
    @pytest.mark.asyncio
    async def test_generate_simple_chart(self):
        # 测试简单图表生成
        result = await self.generator.process("绘制 y=x² 的图像")
        assert "image_path" in result
```

### 添加新 AI 模型

1. **在 ai/xiaoma_adapter.py 中添加模型配置**
2. **更新 config/settings.yaml**
3. **更新 config/prompt_templates.yaml** (如需要)
4. **编写集成测试**
5. **更新 AGENTS.md**

### 修改 UI

1. **在 ui/ 中找到对应文件**
2. **修改 UI 布局或样式**
3. **测试在不同 DPI 下的显示**
4. **测试主题切换**
5. **更新文档截图** (如需要)

### 修复 Bug

1. **编写失败的测试用例**
2. **修复代码使测试通过**
3. **确保所有测试通过**
4. **更新文档** (如需要)

---

## 快速参考

### 关键文件速查

| 文件 | 行数 | 作用 |
|------|------|------|
| main.py | ~200 | 应用入口 |
| ui/popup_window.py | ~1330 | 悬浮窗 UI |
| ai/xiaoma_adapter.py | ~400 | AI API 适配 |
| core/function_router.py | ~180 | 功能路由 |
| config/settings.yaml | ~60 | 应用配置 |
| features/chart_generator.py | ~180 | 图表生成功能 |
| utils/chart_code_executor.py | ~230 | 图表代码执行器 |
| utils/chart_dependency_manager.py | ~160 | 图表依赖管理 |

### 常用路径

| 路径 | 说明 |
|------|------|
| `%APPDATA%/word_selection_assistant/` | 用户数据目录 |
| `./logs/` | 日志文件目录 |
| `./config/` | 配置文件目录 |

### 调试技巧

1. **启用详细日志**: 设置 `LOG_LEVEL=DEBUG`
2. **查看 API 请求**: 启用 `aiohttp` 调试日志
3. **检查热键注册**: 使用 `keyboard._os_keyboard` 检查
4. **监控网络请求**: 使用 Wireshark 抓包

---

## 外部资源

### 文档链接

- [PyQt6 文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Python asyncio 文档](https://docs.python.org/3/library/asyncio.html)
- [PyYAML 文档](https://pyyaml.org/wiki/PyYAMLDocumentation)

### 相关项目

- [小马算力 TokenPony](https://tokenpony.cn/) - AI API 提供商
- [PyQt6 示例](https://github.com/pyqtgraph/pyqt5/tree/master/examples) - UI 参考

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| 2.1.0 | 2026-01 | 添加图表生成功能（chart_generator）、代码执行器（chart_code_executor）、依赖管理器（chart_dependency_manager） |
| 2.0.0 | 2024 | 重构架构，添加流式输出 |
| 1.5.0 | 2023 | 添加多模态支持 |
| 1.0.0 | 2022 | 初始版本 |

---

## 联系方式

- **项目仓库**: https://github.com/MCY0618/word-selection-assistant
- **问题反馈**: GitHub Issues
- **维护者**: MCY0618

---

