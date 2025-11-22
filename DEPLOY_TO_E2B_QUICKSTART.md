# 🚀 E2B 快速部署指南（API Server）

> 5分钟内将 API Server 部署到 E2B，让前端可以调用

---

## 第1步：准备工作

### 1.1 注册 E2B
```bash
# 访问并注册
https://e2b.dev/

# 获取一个 Sandbox
```

### 1.2 准备 API Keys
```bash
# 必需
GROQ_API_KEY=gsk_xxx  # https://console.groq.com/

# 可选（用于 demo）
GITHUB_TOKEN=ghp_xxx  # https://github.com/settings/tokens
```

---

## 第2步：在 E2B 部署

### 选项A：使用 E2B Web UI（推荐新手）

1. **登录 E2B Dashboard**
   ```
   https://e2b.dev/dashboard
   ```

2. **创建新 Sandbox**
   - 点击 "New Sandbox"
   - 选择 **Python 3.11+**
   - 勾选 **"Expose Port 8000"**

3. **配置环境变量**
   - Settings → Environment Variables
   - 添加：
     ```
     GROQ_API_KEY=your_key_here
     GITHUB_TOKEN=your_token_here  (可选)
     ```

4. **在 Sandbox Terminal 执行**
   ```bash
   # 克隆代码
   git clone https://github.com/YOUR_USERNAME/MCP-Navigator.git
   cd MCP-Navigator
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 启动服务（一键）
   chmod +x start_api_e2b.sh
   ./start_api_e2b.sh
   ```

5. **获取 Public URL**
   - 在 Dashboard 查看 "Exposed Ports"
   - 复制类似：`https://abc123-8000.e2b.dev`

### 选项B：使用 E2B CLI（推荐熟手）

```bash
# 1. 安装 CLI
npm install -g @e2b/cli

# 2. 登录
e2b login

# 3. 创建 Sandbox
e2b sandbox create --name mcp-api --template python --port 8000

# 4. 上传代码
cd /Users/lizhuolun/cursor/MCP-Navigator
e2b sandbox upload --sandbox-id YOUR_SANDBOX_ID

# 5. 在 Sandbox 中执行
e2b sandbox exec YOUR_SANDBOX_ID "cd MCP-Navigator && pip install -r requirements.txt && ./start_api_e2b.sh"

# 6. 获取 URL
e2b sandbox info YOUR_SANDBOX_ID
```

---

## 第3步：验证部署

### 测试 1：健康检查
```bash
curl https://YOUR_SANDBOX_ID-8000.e2b.dev/health

# 预期输出：
# {"status":"healthy","groq_configured":true,...}
```

### 测试 2：查看 API 文档
```bash
# 浏览器访问
https://YOUR_SANDBOX_ID-8000.e2b.dev/docs
```

### 测试 3：完整 API 测试
```bash
# 在本地运行测试脚本
./test_api.sh https://YOUR_SANDBOX_ID-8000.e2b.dev
```

---

## 第4步：前端调用

### 方法1：使用提供的 HTML Demo

```bash
# 1. 打开 frontend_example.html
open frontend_example.html

# 2. 修改 API URL
# 将 http://localhost:8000 改为你的 E2B URL

# 3. 测试调用
```

### 方法2：JavaScript/TypeScript

```javascript
const API_URL = "https://YOUR_SANDBOX_ID-8000.e2b.dev";

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

### 方法3：React 组件

```tsx
// 复制使用 E2B_API_DEPLOYMENT.md 中的 React 示例
```

---

## 🔧 常用命令

### 在 E2B Sandbox 中：

```bash
# 查看日志
tail -f api_server.log

# 重启服务
./stop_api_e2b.sh
./start_api_e2b.sh

# 查看进程
ps aux | grep api_server

# 测试本地 API
curl localhost:8000/health
```

---

## 🐛 常见问题

### Q1: API 无法访问？
```bash
# 检查服务是否运行
ps aux | grep api_server

# 如果没运行，重新启动
./start_api_e2b.sh

# 查看错误日志
cat api_server.log
```

### Q2: CORS 错误？
```python
# api_server.py 已配置 CORS (line 32-38)
# 允许所有域名：allow_origins=["*"]

# 如果需要限制特定域名：
allow_origins=[
    "https://your-frontend.com",
    "http://localhost:3000"
]
```

### Q3: 环境变量未加载？
```bash
# 在 E2B Terminal 验证
echo $GROQ_API_KEY

# 如果为空，在 E2B Dashboard 重新设置：
# Settings → Environment Variables
```

### Q4: 依赖安装失败？
```bash
# 升级 pip
pip install --upgrade pip

# 逐个安装
pip install python-dotenv requests rich fastapi uvicorn pydantic
```

---

## 📊 部署检查清单

部署前检查：
- [ ] E2B 账号已创建
- [ ] Sandbox 已创建（Python 3.11+）
- [ ] 端口 8000 已暴露
- [ ] 环境变量已配置（GROQ_API_KEY）
- [ ] 代码已上传到 Sandbox

部署后验证：
- [ ] `/health` 返回正常
- [ ] `/docs` 可以访问 Swagger UI
- [ ] POST `/api/v1/compose` 返回正确响应
- [ ] 前端可以成功调用
- [ ] 日志记录正常

---

## 🌐 关键 URL 格式

```
E2B Public URL:
https://{sandbox-id}-{port}.e2b.dev

示例:
https://abc123def456-8000.e2b.dev

完整 API 端点:
https://abc123def456-8000.e2b.dev/api/v1/compose
https://abc123def456-8000.e2b.dev/docs
https://abc123def456-8000.e2b.dev/health
```

---

## 📚 相关文档

- **详细部署指南：** [E2B_API_DEPLOYMENT.md](./E2B_API_DEPLOYMENT.md)
- **API 使用文档：** [README_API.md](./README_API.md)
- **项目总体说明：** [README.md](./README.md)

---

## 💡 Pro Tips

1. **开发调试：** 先在本地测试 `python api_server.py`，确认无误后再部署
2. **日志监控：** 定期检查 `api_server.log` 发现问题
3. **Swagger UI：** 访问 `/docs` 可以直接在浏览器测试所有 API
4. **Mock 模式：** 如果没有 Groq API key，系统会自动使用 Mock 数据
5. **后台运行：** 使用 `start_api_e2b.sh` 确保服务持续运行

---

## 🆘 需要帮助？

遇到问题？

1. **查看日志：** `cat api_server.log`
2. **运行测试：** `./test_api.sh`
3. **检查文档：** 查看 E2B_API_DEPLOYMENT.md
4. **联系支持：** E2B Discord 或 GitHub Issues

---

**部署成功！** 🎉 你的 API 现在可以被前端调用了！

