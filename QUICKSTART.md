# 快速开始指南

10 分钟内运行 MCP Stack Composer！

## 前置要求

- Python 3.9+
- Git
- 互联网连接

## 步骤 1: 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/mcp-stack-composer.git
cd mcp-stack-composer
```

如果是本地开发：
```bash
cd /Users/lizhuolun/cursor/MCP-Navigator
```

## 步骤 2: 安装依赖

```bash
pip install -r requirements.txt
```

如果遇到权限问题：
```bash
pip install --user -r requirements.txt
```

## 步骤 3: 运行 Mock 模式（无需 API keys）

```bash
python3 run.py
```

输入测试需求：
```
I want an agent that reads GitHub issues, searches the web for similar solutions, and posts a daily summary.
```

你会看到完整的流程，使用模拟数据演示。

## 步骤 4: 配置真实 API（可选）

### 4.1 获取 Groq API Key

1. 访问 https://console.groq.com/
2. 注册并创建 API Key
3. 复制 key（格式：`gsk_...`）

### 4.2 配置环境变量

创建 `.env` 文件：
```bash
cat > .env << 'EOF'
GROQ_API_KEY=gsk_your_key_here
GITHUB_TOKEN=ghp_your_token_here
BRAVE_API_KEY=BSA_your_key_here
EOF
```

或者只配置必需的：
```bash
echo "GROQ_API_KEY=gsk_your_key_here" > .env
```

### 4.3 再次运行

```bash
python3 run.py
```

现在会使用真实的 Groq API 进行分析！

## 测试示例

### 示例 1: GitHub + Web 搜索

```
I want an agent that monitors GitHub issues for bugs and searches StackOverflow for solutions.
```

### 示例 2: 数据库 + 通知

```
I want an agent that queries MongoDB for daily reports and sends them via Slack.
```

### 示例 3: 浏览器自动化

```
I want an agent that uses browser automation to test web pages and logs results to Elasticsearch.
```

## 验证安装

```bash
# 测试导入
python3 -c "from app.config import Config; print('✓ Installation successful')"

# 测试依赖
python3 -c "import dotenv, requests, rich; print('✓ All dependencies available')"

# 查看 MCP 目录
python3 -c "from app.matcher import load_catalog; print(f'✓ {len(load_catalog())} MCPs available')"
```

## 故障排查

### 问题：ModuleNotFoundError: No module named 'app'

**解决**：使用 `run.py` 而不是直接运行 `app/main.py`

```bash
# ✓ 正确
python3 run.py

# ✗ 错误
python3 app/main.py
```

### 问题：依赖安装失败

**解决**：
```bash
# 单独安装
pip install python-dotenv
pip install requests
pip install rich
```

### 问题：MarkupError in rich output

**解决**：升级 rich
```bash
pip install --upgrade rich
```

## 下一步

- 📖 阅读 [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) 获取真实 API keys
- 🚀 查看 [E2B_DEPLOYMENT_GUIDE.md](E2B_DEPLOYMENT_GUIDE.md) 部署到云端
- 🎬 参考 [DEMO_VIDEO_GUIDE.md](DEMO_VIDEO_GUIDE.md) 录制演示视频
- 📚 浏览 [README.md](README.md) 了解详细信息

## 常用命令

```bash
# 运行程序
python3 run.py

# 查看 MCP 目录
cat data/mcp_catalog.json | python3 -m json.tool

# 测试特定模块
python3 -c "from app.planner import get_capabilities_from_description; print(get_capabilities_from_description('test'))"

# 查看配置
python3 -c "from app.config import Config; Config.validate()"
```

## 获取帮助

遇到问题？
- 查看 README.md
- 阅读 API_KEYS_GUIDE.md
- 检查 .env 文件配置
- 确认所有依赖已安装

Happy hacking! 🚀

