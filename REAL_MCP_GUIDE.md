# 真实 MCP 调用指南

## 概述

本项目支持两种 MCP 调用方式：
1. **Mock 模式** - 使用模拟数据，无需任何配置
2. **真实模式** - 调用实际的 API，需要配置 API keys

## 🎯 快速开始 - 真实调用

### 方法 1：使用 GitHub REST API（推荐）

这是最可靠的真实调用方式。

```bash
# 1. 设置环境变量
export GROQ_API_KEY="你的_groq_key"
export GITHUB_TOKEN="你的_github_token"

# 2. 运行程序
cd /Users/lizhuolun/cursor/MCP-Navigator
python3 run.py
```

**工作原理**：
- 程序自动检测到 `GITHUB_TOKEN` 已设置
- 使用 GitHub REST API 代替 Docker MCP
- 获取真实的 GitHub issues 数据

**测试**：
```bash
# 单独测试 GitHub API
GITHUB_TOKEN="你的_token" python3 test_github_api.py
```

---

### 方法 2：使用 Docker MCP（高级）

如果你想使用真正的 Docker MCP 服务器：

#### 前提条件
- Docker Desktop 已安装并运行
- 相关的 API keys 已配置

#### GitHub MCP

```bash
# 1. 拉取镜像
docker pull mcp/github

# 2. 测试运行
docker run -i --rm -e GITHUB_TOKEN=$GITHUB_TOKEN mcp/github

# 3. MCP 使用 stdio 协议（JSON-RPC over stdin/stdout）
# 这需要持久化的进程通信，比较复杂
```

**挑战**：
- MCP stdio 协议需要交互式会话
- 需要正确的 JSON-RPC 握手流程
- 对于快速 demo，REST API 更简单可靠

---

## 🔧 当前实现状态

### 已实现 ✅

1. **Groq API 真实调用**
   ```python
   # app/planner.py
   # 使用 Groq 的 meta-llama/llama-4-scout-17b-16e-instruct 模型
   # 真实的需求分析和代码生成
   ```

2. **GitHub REST API 调用**
   ```python
   # app/mcp_client.py
   def call_github_mcp(tool, args):
       # 直接调用 GitHub REST API
       # 获取真实的 issues, repos 等
   ```

3. **自动 Fallback**
   ```python
   # 如果没有 API key -> Mock 模式
   # 如果有 API key -> 真实调用
   # 如果真实调用失败 -> Fallback 到 Mock
   ```

### 工作中 🚧

1. **Docker MCP stdio 通信**
   - 需要实现完整的 JSON-RPC 会话管理
   - 对于 MVP，REST API fallback 足够

2. **其他 MCP（Brave, Slack, 等）**
   - 可以按照 GitHub 的模式添加直接 API 调用

---

## 📊 调用流程

### Mock 模式（默认）
```
用户输入
  ↓
Groq 分析（Mock）
  ↓
MCP 匹配
  ↓
代码生成（Mock）
  ↓
Mock MCP 调用
  ↓
模拟数据返回
```

### 真实模式（有 API keys）
```
用户输入
  ↓
Groq 真实 API 调用 ✅
  ↓
MCP 匹配
  ↓
Groq 代码生成 ✅
  ↓
GitHub REST API 调用 ✅
  ↓
真实数据返回
```

---

## 🧪 测试真实调用

### 测试 1：Groq API

```bash
export GROQ_API_KEY="你的_key"

python3 -c "
from app.planner import get_capabilities_from_description
result = get_capabilities_from_description('I want to read GitHub issues')
print(f'✓ Groq 工作正常')
print(f'Capabilities: {result[\"capabilities\"]}')
"
```

**预期输出**：
```
✓ Groq 工作正常
Capabilities: ['code_hosting.read_issues']
```

### 测试 2：GitHub API

```bash
export GITHUB_TOKEN="你的_token"

python3 test_github_api.py
```

**预期输出**：
```
✓ 调用成功!
找到 5 个 issues:
  #278970: VS Code crashes...
  ...
```

### 测试 3：完整流程

```bash
export GROQ_API_KEY="你的_groq_key"
export GITHUB_TOKEN="你的_github_token"

python3 run.py
```

**预期行为**：
1. ✅ 显示 "✓ Groq API connected"（不是 Mock 模式）
2. ✅ Groq 真实分析需求
3. ✅ 匹配 MCP
4. ✅ Groq 生成代码
5. ✅ 调用 GitHub REST API，获取真实 issues

---

## 🔍 调试技巧

### 检查是否使用真实调用

```python
from app.config import Config

# 检查 API keys
print(f"Groq: {'✓' if Config.GROQ_API_KEY else '✗'}")
print(f"GitHub: {'✓' if Config.GITHUB_TOKEN else '✗'}")
print(f"Mock Mode: {Config.USE_MOCK_MODE}")
```

### 查看调用详情

在 `app/main.py` 中，程序会显示：
- "✓ Groq API connected" - 真实模式
- "⚠️ Running in MOCK MODE" - Mock 模式

在每个步骤中：
- 如果看到 "⚠️ ... error ... Falling back to mock" - 真实调用失败
- 如果没有警告 - 真实调用成功

---

## 📈 扩展其他 MCP

### 添加 Brave Search

```python
# 在 app/mcp_client.py 中添加

def call_brave_search(query: str) -> Dict:
    """直接调用 Brave Search API"""
    if not Config.BRAVE_API_KEY:
        raise ValueError("BRAVE_API_KEY not configured")
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": Config.BRAVE_API_KEY
    }
    
    params = {"q": query, "count": 10}
    
    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers=headers,
        params=params,
        timeout=10
    )
    response.raise_for_status()
    
    return {
        "mcp_id": "brave-search",
        "tool": "search",
        "success": True,
        "result": response.json()
    }
```

### 更新 call_mcp()

```python
def call_mcp(mcp_id: str, tool: str, args: Dict = None):
    # ...
    
    if mcp_id == 'github':
        return call_github_mcp(tool, args)
    elif mcp_id in ['brave-search', 'brave']:
        return call_brave_search(args.get('query', ''))
    # ...
```

---

## 🚀 生产环境建议

### 推荐方案：REST API

**优点**：
- ✅ 可靠性高
- ✅ 调试简单
- ✅ 不依赖 Docker
- ✅ 错误处理容易
- ✅ 适合 serverless 部署

**缺点**：
- ❌ 需要为每个服务实现单独的客户端
- ❌ 不是"纯粹"的 MCP 协议

### Docker MCP 方案

**优点**：
- ✅ 符合 MCP 标准
- ✅ 统一的协议
- ✅ 易于添加新的 MCP

**缺点**：
- ❌ stdio 通信复杂
- ❌ 需要持久化进程
- ❌ Docker 依赖
- ❌ 调试困难

**建议**：
- **Demo/Hackathon**：使用 REST API（当前实现）
- **生产环境**：两者混合
  - 关键服务（GitHub, Stripe）：REST API
  - 标准 MCP：Docker MCP
  - 所有服务：Mock fallback

---

## 🎯 当前状态总结

| 组件 | Mock 模式 | 真实模式 | 状态 |
|------|----------|---------|------|
| Groq 分析 | ✅ | ✅ | 完成 |
| Groq 代码生成 | ✅ | ✅ | 完成 |
| GitHub MCP | ✅ | ✅ (REST API) | 完成 |
| Brave Search | ✅ | ⏳ | 可扩展 |
| Slack | ✅ | ⏳ | 可扩展 |
| Docker MCP stdio | ❌ | 🚧 | 复杂，非必需 |

---

## 📞 支持

如果真实调用遇到问题：

1. **检查 API keys**
   ```bash
   echo $GROQ_API_KEY
   echo $GITHUB_TOKEN
   ```

2. **查看错误信息**
   - 程序会显示详细的错误和 fallback 提示

3. **测试独立模块**
   ```bash
   python3 test_github_api.py
   python3 test_groq_direct.py
   ```

4. **查看日志**
   - 所有 API 调用都有详细的输出

---

**当前实现已经足够用于 Hackathon demo！** ✨

真实的 Groq + GitHub API 调用展示了完整的功能，Docker MCP stdio 是一个可选的高级特性。

