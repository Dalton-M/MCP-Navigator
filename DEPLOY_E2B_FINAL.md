# 🚀 E2B 部署最终方案

> 使用 E2B Custom Template 部署持久 API Server

---

## 📋 方案说明

根据搜索结果，E2B 支持通过**自定义模板（Custom Template）**部署服务：

- ✅ 使用 `e2b.toml` 配置模板
- ✅ 通过 `Dockerfile` 构建环境
- ✅ 暴露端口供外部访问
- ✅ 设置资源和网络配置

**关键文件：**
- `e2b.toml` - E2B 模板配置
- `Dockerfile.e2b` - Docker 构建文件
- `.env.e2b` - 环境变量

---

## 🛠️ 部署步骤

### 第 1 步：安装 E2B CLI

```bash
# 安装 E2B CLI
npm install -g @e2b/cli

# 验证安装
e2b --version
```

### 第 2 步：获取 E2B API Key

1. 访问 [E2B Dashboard](https://e2b.dev/)
2. 注册/登录账号（新用户获得 $100 免费额度）
3. 进入 Dashboard → API Keys
4. 复制你的 API Key

```bash
# 设置环境变量
export E2B_API_KEY=e2b_your_api_key_here
```

### 第 3 步：准备环境变量

```bash
# 复制环境变量模板
cp .env.e2b.example .env.e2b

# 编辑 .env.e2b，填入真实值
nano .env.e2b
```

`.env.e2b` 内容：
```bash
E2B_API_KEY=e2b_xxx
GROQ_API_KEY=gsk_xxx
GITHUB_TOKEN=ghp_xxx
```

### 第 4 步：构建 E2B 模板

```bash
cd /Users/lizhuolun/cursor/MCP-Navigator

# 构建自定义模板
e2b template build \
  --name mcp-stack-composer \
  --version 1.0.0

# 查看构建进度
# 这会构建 Docker 镜像并上传到 E2B
```

**输出示例：**
```
Building template mcp-stack-composer:1.0.0...
[+] Building Docker image...
[+] Pushing to E2B registry...
✅ Template built successfully!
Template ID: tmpl_abc123def456
```

### 第 5 步：创建 Sandbox 实例

```bash
# 创建并启动 Sandbox
e2b sandbox create \
  --template mcp-stack-composer:1.0.0 \
  --name mcp-api-production \
  --env-file .env.e2b \
  --metadata '{"env":"production","project":"mcp-navigator"}'
```

**输出示例：**
```
Creating sandbox from template mcp-stack-composer:1.0.0...
✅ Sandbox created successfully!
Sandbox ID: sbx_xyz789abc123
Status: running
Public URL: https://sbx_xyz789abc123-8000.e2b.dev
```

### 第 6 步：获取公网 URL

```bash
# 列出所有 Sandbox
e2b sandbox list

# 查看特定 Sandbox 详情
e2b sandbox info sbx_xyz789abc123

# 输出会包含：
# - Sandbox ID
# - Status: running
# - Public URL: https://sbx_xyz789abc123-8000.e2b.dev
# - Created at
# - Resources
```

### 第 7 步：测试 API

```bash
# 测试健康检查
curl https://sbx_xyz789abc123-8000.e2b.dev/health

# 应返回：
# {"status":"healthy","groq_configured":true,...}

# 测试 Swagger UI
# 浏览器访问：https://sbx_xyz789abc123-8000.e2b.dev/docs

# 测试 Compose API
curl -X POST https://sbx_xyz789abc123-8000.e2b.dev/api/v1/compose \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I want an agent that reads GitHub issues",
    "top_k": 3
  }'
```

---

## 🌐 前端调用

### JavaScript/TypeScript

```javascript
// 使用你的 E2B Sandbox URL
const E2B_API_URL = "https://sbx_xyz789abc123-8000.e2b.dev";

async function composeAgent(description) {
  const response = await fetch(`${E2B_API_URL}/api/v1/compose`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      description: description,
      top_k: 3
    })
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return await response.json();
}

// 使用
const result = await composeAgent(
  "I want an agent that reads GitHub issues and searches for solutions"
);

console.log("Recommended MCPs:", result.recommended_mcps);
console.log("Generated Code:", result.code_snippet.markdown);
```

### React 组件

```tsx
import React, { useState } from 'react';

const E2B_API_URL = "https://sbx_xyz789abc123-8000.e2b.dev";

export const MCPComposer: React.FC = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${E2B_API_URL}/api/v1/compose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, top_k: 3 }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe your agent..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Composing...' : 'Compose Agent'}
        </button>
      </form>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
};
```

### 更新 HTML Demo

打开 `frontend_example.html`，修改 API URL：

```javascript
// 找到这一行
const apiUrl = document.getElementById('apiUrl').value.trim();

// 将默认值改为你的 E2B URL
<input 
  type="text" 
  id="apiUrl" 
  value="https://sbx_xyz789abc123-8000.e2b.dev"
>
```

---

## 🔧 管理和维护

### 查看 Sandbox 状态

```bash
# 列出所有 Sandbox
e2b sandbox list

# 查看详细信息
e2b sandbox info sbx_xyz789abc123

# 查看日志
e2b sandbox logs sbx_xyz789abc123
```

### 更新部署

```bash
# 1. 修改代码后重新构建模板
e2b template build --name mcp-stack-composer --version 1.0.1

# 2. 停止旧 Sandbox
e2b sandbox stop sbx_xyz789abc123

# 3. 创建新 Sandbox（使用新版本）
e2b sandbox create \
  --template mcp-stack-composer:1.0.1 \
  --name mcp-api-production-v2 \
  --env-file .env.e2b
```

### 保持 Sandbox 运行

E2B Sandbox 默认有时间限制，可以通过以下方式保持运行：

```bash
# 方法 1: 设置更长的超时
e2b sandbox create \
  --template mcp-stack-composer:1.0.0 \
  --timeout 3600  # 1 小时

# 方法 2: 通过 SDK 保持连接
# 创建一个保活脚本
```

**保活脚本（`keep_alive.py`）：**

```python
import os
import time
import requests
from e2b import Sandbox

E2B_API_KEY = os.getenv("E2B_API_KEY")
SANDBOX_ID = "sbx_xyz789abc123"

def keep_sandbox_alive():
    """定期 ping Sandbox 保持连接"""
    sandbox = Sandbox.connect(SANDBOX_ID, api_key=E2B_API_KEY)
    
    while True:
        try:
            # 每 5 分钟 ping 一次
            sandbox.keep_alive()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sandbox is alive")
            time.sleep(300)  # 5 分钟
        except Exception as e:
            print(f"Error: {e}")
            # 尝试重新连接
            time.sleep(60)

if __name__ == "__main__":
    keep_sandbox_alive()
```

### 停止和删除

```bash
# 停止 Sandbox（保留数据）
e2b sandbox stop sbx_xyz789abc123

# 启动已停止的 Sandbox
e2b sandbox start sbx_xyz789abc123

# 删除 Sandbox（不可恢复）
e2b sandbox delete sbx_xyz789abc123

# 删除模板
e2b template delete mcp-stack-composer:1.0.0
```

---

## 💰 成本估算

E2B 定价（新用户获得 $100 免费额度）：

**资源配置（根据 e2b.toml）：**
- CPU: 2 核
- RAM: 4GB
- Disk: 10GB

**预估成本：**
- 按使用时间计费
- 免费额度可支持开发和测试
- 具体价格查看：https://e2b.dev/pricing

---

## 🐛 故障排查

### 问题 1: 构建失败

```bash
# 检查 Dockerfile 语法
docker build -f Dockerfile.e2b -t test-image .

# 查看详细构建日志
e2b template build --name mcp-stack-composer --verbose
```

### 问题 2: Sandbox 无法访问

```bash
# 检查 Sandbox 状态
e2b sandbox info sbx_xyz789abc123

# 查看日志
e2b sandbox logs sbx_xyz789abc123

# 常见原因：
# - 端口配置错误（检查 e2b.toml 的 allowed_ports）
# - 服务未启动（检查 init.command）
# - 环境变量缺失
```

### 问题 3: 环境变量未生效

```bash
# 验证环境变量
e2b sandbox exec sbx_xyz789abc123 "env | grep GROQ"

# 重新创建 Sandbox 并传入环境变量
e2b sandbox create \
  --template mcp-stack-composer:1.0.0 \
  --env-file .env.e2b
```

### 问题 4: API 响应慢

- 检查 Groq API 配置
- 增加资源配置（修改 e2b.toml 的 resources）
- 优化代码性能

---

## 📊 部署检查清单

- [ ] E2B CLI 已安装
- [ ] E2B API Key 已获取并配置
- [ ] `.env.e2b` 文件已创建并填写
- [ ] `e2b.toml` 配置正确
- [ ] `Dockerfile.e2b` 无语法错误
- [ ] 模板构建成功
- [ ] Sandbox 创建成功
- [ ] 获得公网 URL
- [ ] `/health` 端点返回正常
- [ ] `/docs` 可以访问
- [ ] POST `/api/v1/compose` 正常工作
- [ ] 前端可以成功调用

---

## 🎯 关键命令速查

```bash
# 完整部署流程
export E2B_API_KEY=e2b_xxx
e2b template build --name mcp-stack-composer --version 1.0.0
e2b sandbox create --template mcp-stack-composer:1.0.0 --env-file .env.e2b
e2b sandbox list
curl https://YOUR_SANDBOX_URL/health

# 日常管理
e2b sandbox list                    # 查看所有 Sandbox
e2b sandbox info SANDBOX_ID         # 查看详情
e2b sandbox logs SANDBOX_ID         # 查看日志
e2b sandbox stop SANDBOX_ID         # 停止
e2b sandbox start SANDBOX_ID        # 启动
e2b sandbox delete SANDBOX_ID       # 删除
```

---

## 📚 相关资源

- [E2B 官方文档](https://e2b.dev/docs)
- [E2B CLI 文档](https://e2b.dev/docs/cli)
- [E2B Custom Templates](https://e2b.dev/docs/templates)
- [E2B Python SDK](https://github.com/e2b-dev/python-sdk)

---

## 💡 提示

1. **首次部署**：模板构建可能需要几分钟
2. **Public URL**：每个 Sandbox 都有唯一的 URL
3. **日志查看**：使用 `e2b sandbox logs` 排查问题
4. **版本管理**：使用版本号管理模板（1.0.0, 1.0.1, ...）
5. **成本控制**：不用时停止 Sandbox 节省费用

---

**部署成功后，你的 API 就可以通过 E2B 公网 URL 被前端调用了！** 🎉

E2B URL 格式：`https://sbx_{sandbox_id}-8000.e2b.dev`

