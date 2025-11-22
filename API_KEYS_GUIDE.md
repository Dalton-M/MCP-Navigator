# API Keys 申请指南

本文档指导你如何获取运行 MCP Stack Composer 所需的 API keys。

## 必需的 API Keys

### 1. Groq API Key（必需）

Groq 提供快速的 LLM 推理服务，用于分析需求和生成代码。

**申请步骤：**

1. 访问 [Groq Console](https://console.groq.com/)
2. 点击右上角 "Sign Up" 或使用 Google/GitHub 账号登录
3. 登录后，进入 [API Keys 页面](https://console.groq.com/keys)
4. 点击 "Create API Key"
5. 复制生成的 API Key（格式：`gsk_...`）

**免费配额：**
- 14,400 requests/day
- 适合开发和演示使用

**配置方式：**
```bash
# 在 .env 文件中添加
GROQ_API_KEY=gsk_your_key_here
```

---

## 演示用 API Keys（至少选 1 个）

### 2. GitHub Personal Access Token

用于演示 GitHub MCP 功能（读取 issues, repositories 等）。

**申请步骤：**

1. 登录 GitHub 账号
2. 访问 [Personal Access Tokens](https://github.com/settings/tokens)
3. 点击 "Generate new token" → "Generate new token (classic)"
4. 设置以下选项：
   - **Note**: "MCP Stack Composer Demo"
   - **Expiration**: 30 days（或根据需要）
   - **Scopes**: 勾选以下权限
     - `repo` (完整仓库访问)
     - `read:org` (读取组织信息)
5. 点击 "Generate token"
6. **立即复制 token**（只显示一次！）

**免费配额：**
- 完全免费
- Rate limit: 5,000 requests/hour (authenticated)

**配置方式：**
```bash
# 在 .env 文件中添加
GITHUB_TOKEN=ghp_your_token_here
```

**测试调用：**
```python
# 测试 GitHub MCP
python3 -c "from app.mcp_client import call_github_mcp; \
result = call_github_mcp('list_issues', {'owner': 'microsoft', 'repo': 'vscode', 'per_page': 3}); \
print(result)"
```

---

### 3. Brave Search API Key

用于演示 Web 搜索 MCP 功能。

**申请步骤：**

1. 访问 [Brave Search API](https://brave.com/search/api/)
2. 点击 "Get Started" 或 "Sign Up"
3. 使用邮箱注册账号并验证
4. 登录后进入 Dashboard
5. 创建新的 API Key
6. 复制 API Key

**免费配额：**
- 2,000 queries/month
- 适合演示使用

**配置方式：**
```bash
# 在 .env 文件中添加
BRAVE_API_KEY=BSA_your_key_here
```

---

## 完整的 .env 文件示例

创建 `/Users/lizhuolun/cursor/MCP-Navigator/.env` 文件：

```bash
# Groq API（必需 - 用于 LLM 分析）
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# GitHub Token（可选 - 用于演示 GitHub MCP）
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Brave Search API（可选 - 用于演示搜索 MCP）
BRAVE_API_KEY=BSA_xxxxxxxxxxxxxxxxxxxxxxxxx

# MCP Server Settings（可选）
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=3000
```

---

## 验证配置

运行以下命令验证配置是否正确：

```bash
cd /Users/lizhuolun/cursor/MCP-Navigator

# 测试配置加载
python3 -c "from app.config import Config; \
print(f'Groq API: {\"✓\" if Config.GROQ_API_KEY else \"✗\"}'); \
print(f'GitHub Token: {\"✓\" if Config.GITHUB_TOKEN else \"✗\"}'); \
print(f'Brave API: {\"✓\" if Config.BRAVE_API_KEY else \"✗\"}')"
```

**预期输出：**
```
Groq API: ✓
GitHub Token: ✓
Brave API: ✓
```

---

## 安全提示

⚠️ **重要安全建议：**

1. **不要提交 .env 文件到 Git**
   - `.env` 已经在 `.gitignore` 中
   - 检查：`git status` 不应显示 `.env`

2. **不要在代码中硬编码 API keys**
   - 始终使用环境变量

3. **定期轮换 API keys**
   - GitHub tokens 可以设置过期时间
   - 如果 key 泄露，立即撤销并重新生成

4. **最小权限原则**
   - GitHub token 只授予必要的 scopes
   - 不要使用 admin 权限的 token

---

## 故障排查

### 问题：Groq API 返回 401 Unauthorized

**解决方案：**
- 检查 API key 是否正确复制（没有多余空格）
- 确认 key 格式为 `gsk_...`
- 在 Groq Console 检查 key 是否被禁用

### 问题：GitHub API 返回 404 或 403

**解决方案：**
- 确认 token 有正确的 scopes (`repo`, `read:org`)
- 检查访问的 repository 是否存在且有权限
- GitHub rate limit: 等待一小时或使用新 token

### 问题：Brave Search 返回错误

**解决方案：**
- 确认已验证邮箱
- 检查是否超出免费配额 (2000 queries/month)
- API key 格式应为 `BSA...`

---

## 下一步

配置好 API keys 后：

1. 运行完整测试：
   ```bash
   python3 run.py
   ```

2. 输入测试需求：
   ```
   I want an agent that reads GitHub issues, searches the web for similar solutions, and posts a daily summary.
   ```

3. 观察完整流程：
   - Groq 分析需求 → 提取 capabilities
   - 匹配 MCP servers
   - Groq 生成配置和代码
   - 真实调用 MCP（GitHub 或 Brave）

4. 准备部署到 E2B 云端

---

## 相关链接

- [Groq Documentation](https://console.groq.com/docs)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Brave Search API Docs](https://brave.com/search/api/)
- [Docker MCP Hub](https://hub.docker.com/mcp)
- [E2B Platform](https://e2b.dev/)

