# Word Selection Assistant (划词助手)

一个基于 PyQt6 的桌面划词助手，集成了 AI 能力，支持翻译、解释、总结等功能。

## 功能特性

- **划词翻译**: 选中文字后快速翻译
- **单词解释**: 提供单词的详细释义和用法
- **内容总结**: 对长文本进行智能总结
- **自定义功能**: 支持扩展自定义 AI 功能
- **系统托盘**: 程序常驻系统托盘，不占用任务栏
- **全局热键**: 使用 `Ctrl+Q` 快速触发划词功能
- **多 API 支持**: 兼容 OpenAI 格式的 API (小马算力 TokenPony)

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

1. 启动程序后，图标会出现在系统托盘
2. 选中任意文字
3. 按 `Ctrl+Q` 快捷键
4. 悬浮窗会显示 AI 处理结果

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
    └── logger.py              # 日志系统
```

## 配置说明

### 应用配置 (config/settings.yaml)

```yaml
app:
  name: "划词助手"
  version: "1.0.0"
  log_level: "INFO"

hotkey:
  combination: "ctrl+q"  # 快捷键

ai:
  provider: "xiaoma"     # API提供商
  model: "minimax-m2"    # 默认模型
  timeout: 30            # 超时时间(秒)

features:
  translator:
    enabled: true
    auto_translate: false

  explainer:
    enabled: true

  summarizer:
    enabled: true
    max_length: 500
```

### 提示词模板 (config/prompt_templates.yaml)

```yaml
translator: "请将以下文字翻译成{target_lang}：\n\n{text}"

explainer: "请解释以下单词的含义、用法并给出例句：\n\n{text}"

summarizer: "请对以下内容进行简洁总结（不超过100字）：\n\n{text}"
```

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
    │ - SettingsDialog│ │ - FunctionRouter│ │ - PromptGenerator│
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
    ┌─────────────────────────────────────────────────────────┐
    │              Features Layer (features/)                  │
    │   Translator  │  Explainer  │  Summarizer  │ Custom     │
    └─────────────────────────────────────────────────────────┘
```

## 依赖说明

| 依赖 | 版本 | 用途 |
|------|------|------|
| PyQt6 | >=6.6.0 | GUI框架 |
| openai | >=1.0.0 | API调用 |
| aiohttp | >=3.9.0 | 异步HTTP |
| keyboard | >=0.13.5 | 全局热键 |
| pywin32 | >=306 | Windows API |
| pyyaml | >=6.0.1 | 配置解析 |
| python-dotenv | >=1.0.0 | 环境变量 |

## 常见问题

### Q: 程序启动后没有反应
A: 检查系统托盘，程序运行后图标会出现在托盘区域。

### Q: Ctrl+Q 快捷键不生效
A: 确保当前窗口有文本选中，且没有其他程序占用该快捷键。

### Q: API 调用失败
A: 检查 `.env` 文件中的 `TOKENPONY_API_KEY` 是否正确，以及网络连接是否正常。

### Q: 悬浮窗显示异常
A: 尝试重启程序，或检查 `config/settings.yaml` 中的窗口配置。

## 开发日志

### v1.0.0 (2026-01-07)
- 初始版本发布
- 支持翻译、解释、总结功能
- 实现系统托盘和全局热键
- 集成小马算力 TokenPony API

## 许可证

MIT License
