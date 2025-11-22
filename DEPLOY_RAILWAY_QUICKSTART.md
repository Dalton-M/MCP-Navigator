# 🚂 Railway 快速部署指南（推荐）

> 5 分钟部署 API Server，让前端可以调用

---

## 为什么选择 Railway？

根据 [E2B 官方文档](https://e2b.dev/docs/quickstart)，E2B 是**临时沙盒服务**，不适合部署持久 API Server。

**Railway 优势：**
- ✅ 免费 $5/月额度（够用）
- ✅ 自动 HTTPS 和域名
- ✅ GitHub 自动部署
- ✅ 有 Web UI（无需 CLI）
- ✅ 支持环境变量管理
- ✅ 自动重启和监控

---

## 🚀 部署步骤（5 分钟）

### 第 1 步：准备 GitHub 仓库

```bash
cd /Users/lizhuolun/cursor/MCP-Navigator

# 确保所有文件已提交
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 第 2 步：注册 Railway

1. 访问 https://railway.app/
2. 点击 **"Start a New Project"**
3. 使用 **GitHub 账号登录**（推荐）

### 第 3 步：创建项目

1. 点击 **"Deploy from GitHub repo"**
2. 授权 Railway 访问你的 GitHub
3. 选择 **`MCP-Navigator`** 仓库
4. 点击 **"Deploy Now"**

### 第 4 步：配置环境变量

1. 在 Railway Dashboard，点击你的项目
2. 进入 **"Variables"** 标签
3. 添加环境变量：

```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
GITHUB_TOKEN=ghp_your_github_token_here
BRAVE_API_KEY=BSA_your_api_key_here  # 可选
```

4. 点击 **"Add"** 保存

### 第 5 步：配置启动命令

1. 进入 **"Settings"** 标签
2. 找到 **"Deploy"** 部分
3. 设置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`
4. 保存

### 第 6 步：获取公网 URL

1. 在 **"Settings"** → **"Networking"**
2. 点击 **"Generate Domain"**
3. 获得类似：`https://mcp-navigator-production.up.railway.app`

### 第 7 步：测试 API

```bash
# 测试健康检查
curl https://your-app.up.railway.app/health

# 测试 Compose API
curl -X POST https://your-app.up.railway.app/api/v1/compose \
  -H "Content-Type: application/json" \
  -d '{"description":"test","top_k":3}'
```

---

## 🌐 前端调用

### JavaScript

```javascript
const API_URL = "https://your-app.up.railway.app";

async function composeAgent(description) {
  const response = await fetch(`${API_URL}/api/v1/compose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      description: description,
      top_k: 3 
    })
  });
  
  return await response.json();
}

// 使用
const result = await composeAgent(
  "I want an agent that reads GitHub issues"
);
console.log(result.recommended_mcps);
```

### HTML Demo

打开 `frontend_example.html`，修改 API URL：

```javascript
// 将这行
const apiUrl = "http://localhost:8000";

// 改为
const apiUrl = "https://your-app.up.railway.app";
```

---

## 📊 Railway Dashboard 功能

### 查看日志
1. 进入项目
2. 点击 **"Deployments"**
3. 点击最新的部署
4. 查看实时日志

### 重新部署
1. 进入项目
2. 点击 **"Deploy"** 按钮
3. 或推送代码到 GitHub（自动部署）

### 监控
1. **"Metrics"** 标签查看：
   - CPU 使用率
   - 内存使用
   - 网络流量
   - 响应时间

---

## 🔧 项目配置文件（可选）

Railway 会自动检测 Python 项目，但你也可以创建配置文件：

### `railway.toml`（可选）

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python api_server.py"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### `Procfile`（可选）

```
web: python api_server.py
```

---

## 🐛 常见问题

### Q1: 部署失败？

**检查日志：**
1. Railway Dashboard → Deployments
2. 查看 Build Logs 和 Deploy Logs
3. 常见原因：
   - `requirements.txt` 依赖问题
   - 端口配置错误
   - 环境变量缺失

**解决方案：**
```bash
# 确保 api_server.py 使用环境变量端口
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### Q2: API 调用失败？

**CORS 检查：**
- 已在 `api_server.py` 配置 `allow_origins=["*"]`
- 检查浏览器控制台错误

**URL 检查：**
- 确保使用 Railway 生成的完整 URL
- 包含 `https://`

### Q3: 环境变量未生效？

**验证步骤：**
1. Railway Dashboard → Variables
2. 确认所有变量已添加
3. 重新部署（Variables 更改需要重新部署）

---

## 💰 成本说明

**免费层：**
- $5 月度额度（按使用量）
- 约可支持：
  - 500 小时运行时间
  - 或大量 API 请求

**超出免费层：**
- 自动升级到付费计划
- 按实际使用量计费
- 通常每月 $5-20（取决于流量）

**省钱技巧：**
- 设置 **Sleep on idle**（空闲时休眠）
- 使用 Railway 的监控功能控制成本

---

## 🎯 部署检查清单

- [ ] GitHub 仓库已创建并推送
- [ ] Railway 账号已注册
- [ ] 项目已从 GitHub 部署
- [ ] 环境变量已添加（GROQ_API_KEY 等）
- [ ] 生成了公网域名
- [ ] `/health` 端点返回正常
- [ ] `/docs` 可以访问 Swagger UI
- [ ] 测试 POST `/api/v1/compose` 成功
- [ ] 前端可以调用 API
- [ ] 日志显示正常

---

## 🔄 自动部署流程

Railway 自动监听 GitHub：

```
1. 你在本地修改代码
   ↓
2. git push 到 GitHub
   ↓
3. Railway 自动检测更新
   ↓
4. 自动构建和部署
   ↓
5. 新版本上线（零停机）
```

---

## 📚 其他部署选项

如果 Railway 不满足需求，还可以考虑：

### 1. Render.com
- 免费层
- 类似 Railway
- 文档：https://render.com/docs

### 2. Fly.io
- 免费额度
- 更多控制权
- 需要 CLI：`fly launch`

### 3. Vercel
- 适合 Serverless
- 需要修改代码适配

---

## 🎉 完成！

现在你有一个：
- ✅ 持久运行的 API Server
- ✅ 自动 HTTPS 和域名
- ✅ 自动部署（推送代码即更新）
- ✅ 监控和日志
- ✅ 前端可以随时调用

**你的 API 地址：**
```
https://your-app.up.railway.app/api/v1/compose
```

**Swagger UI：**
```
https://your-app.up.railway.app/docs
```

---

## 🆚 Railway vs E2B

| 特性 | Railway | E2B |
|------|---------|-----|
| 持久运行 | ✅ | ❌ (5分钟) |
| Web UI | ✅ | ❌ |
| 自动部署 | ✅ | ❌ |
| 成本 | 免费/$5 | 按用量 |
| 适用场景 | API Server | 临时执行 |
| 部署难度 | ⭐ | ⭐⭐⭐ |

**结论：** Railway 是部署 API Server 的最佳选择！

---

有问题？查看 Railway 文档：https://docs.railway.app/

