# 配置说明

## API提供商配置

项目支持多种AI服务提供商，您可以通过修改 `config/settings.yaml` 中的 `default_provider` 字段来选择默认的AI服务。

### 可用提供商

1. **Ollama (本地)** - `default_provider: ollama`
   - 优点：本地运行，保护隐私，无需网络
   - 缺点：需要本地安装Ollama和模型
   - 配置：在 `.env` 中设置 `OLLAMA_BASE_URL`

2. **OpenAI兼容API (云端)** - `default_provider: openai`
   - 优点：功能强大，模型丰富
   - 缺点：需要网络连接，可能产生费用
   - 配置：在 `.env` 中设置 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL`

### 配置步骤

1. 编辑 `.env` 文件，配置相应的API密钥和URL
2. 编辑 `config/settings.yaml`，设置 `default_provider`
3. 重启应用程序使配置生效

### 模型选择

项目支持多种模型，您可以在自定义功能中选择适合的模型。对于Ollama，模型名称应与 `ollama list` 命令显示的名称匹配。