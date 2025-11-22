# 🏭 E2B 生产环境部署指南

> 解决 Sandbox 超时问题，实现持续运行

---

## ⚠️ E2B Sandbox 超时限制

E2B Sandbox 有固定的生命周期限制：

| 账户类型 | 最大超时 | 说明 |
|----------|----------|------|
| **Hobby** | 3600秒 (1小时) | 免费账户 |
| **Pro** | 86400秒 (24小时) | 付费账户 |

**默认超时：** 300 秒（5分钟）

---

## 🎯 解决方案：自动重启机制

由于 E2B Sandbox 无法永久运行，我们实现了**自动重启机制**：

```
Sandbox 1 (1小时) → 自动重启 → Sandbox 2 (1小时) → 自动重启 → ...
```

**优点：**
- ✅ 近乎持续运行
- ✅ 自动创建新 Sandbox
- ✅ 零停机切换
- ✅ 保持公网 URL 可用

---

## 🚀 使用生产部署脚本

### 1. 运行生产脚本

```bash
python deploy_to_e2b_prod.py
```

**脚本特性：**
- 设置最大超时时间（1小时或24小时）
- 在超时前 60 秒自动创建新 Sandbox
- 无缝切换，保持服务可用
- 自动更新公网 URL

### 2. 输出示例

```
🚀 E2B Production Deployment
======================================================================

✅ E2B_API_KEY: e2b_b72d7b...
✅ GROQ_API_KEY: gsk_ZY3wox...

⏰ Sandbox timeout: 3600s (60 minutes)
💡 Will auto-restart before timeout

🚀 Creating E2B Sandbox with 3600s (60 minutes) timeout...
✅ Sandbox created: abc123def456
🌐 Public URL: https://8000-abc123def456.e2b.app

... (部署过程) ...

🎉 Deployment Complete!
🌐 Public URL: https://8000-abc123def456.e2b.app

🔄 Auto-restart enabled (will restart every 60 minutes)
💡 Press Ctrl+C to stop

💓 [13:00:00] Keepalive | Next restart in 59m 30s
💓 [13:01:00] Keepalive | Next restart in 58m 30s
...
💓 [13:59:00] Keepalive | Next restart in 0m 30s

======================================================================
🔄 Sandbox timeout approaching - Creating new sandbox...
======================================================================
🚀 Creating E2B Sandbox...
✅ New sandbox ready!
🌐 Public URL: https://8000-xyz789uvw123.e2b.app
⏰ Next restart in 60 minutes
```

---

## ⚙️ 配置选项

### 修改超时时间

编辑 `deploy_to_e2b_prod.py` 第 222 行：

```python
# Hobby 用户（1小时）
TIMEOUT = 3600

# Pro 用户（24小时）
# TIMEOUT = 86400
```

### 修改重启提前时间

编辑 `deploy_to_e2b_prod.py` 第 118 行：

```python
restart_before = 60  # 在超时前 60 秒重启
```

---

## 🌐 前端集成

### 问题：URL 会变化

每次重启 Sandbox，公网 URL 会变化：
```
https://8000-abc123.e2b.app  →  https://8000-xyz789.e2b.app
```

### 解决方案 1：动态 URL 配置

```javascript
// 前端定期从配置文件读取最新 URL
async function getAPIUrl() {
  const response = await fetch('/config/e2b_url.txt');
  const url = await response.text();
  return url.trim();
}

// 使用
const apiUrl = await getAPIUrl();
const result = await fetch(`${apiUrl}/api/v1/compose`, {...});
```

### 解决方案 2：中间代理层（推荐）

```
前端 → 固定URL代理 (Railway/Vercel) → E2B动态URL
```

**部署代理：**

```javascript
// proxy-server.js (部署在 Railway/Vercel)
import express from 'express';
import fs from 'fs';

const app = express();

// 从文件读取当前 E2B URL
function getCurrentE2BURL() {
  return fs.readFileSync('e2b_url.txt', 'utf8').trim();
}

// 代理所有请求到 E2B
app.all('*', async (req, res) => {
  const e2bUrl = getCurrentE2BURL();
  const targetUrl = `${e2bUrl}${req.path}`;
  
  // 转发请求
  const response = await fetch(targetUrl, {
    method: req.method,
    headers: req.headers,
    body: req.body
  });
  
  res.status(response.status).send(await response.text());
});

app.listen(3000);
```

**前端调用：**
```javascript
// 固定 URL！
const API_URL = "https://your-proxy.railway.app";

const response = await fetch(`${API_URL}/api/v1/compose`, {
  method: "POST",
  body: JSON.stringify({...})
});
```

---

## 💰 成本考虑

### Hobby 账户（免费）
- $100 免费额度
- 1小时最大超时
- 需要频繁重启
- 每次重启消耗资源创建新 Sandbox

### Pro 账户
- 24小时最大超时
- 减少重启次数（每天1次 vs 每小时1次）
- 更稳定的服务

**估算：**
- Hobby: 每天重启 24 次
- Pro: 每天重启 1 次

---

## 🆚 与传统部署对比

| 特性 | E2B (本方案) | Railway/Render |
|------|-------------|----------------|
| 部署难度 | ⭐⭐⭐⭐ | ⭐ |
| 持久运行 | ❌ (需自动重启) | ✅ |
| 公网URL | ⚠️ (会变化) | ✅ (固定) |
| 成本 | 按用量 | 免费/$5 |
| E2B要求 | ✅ | ❌ |

---

## 💡 最终建议

### 如果必须使用 E2B：

**最佳方案：混合部署**

```
[前端] → [Railway代理] → [E2B Sandbox (自动重启)]
         固定URL           动态URL
```

**优点：**
- ✅ 满足 E2B 使用要求
- ✅ 前端使用固定 URL
- ✅ 自动处理 Sandbox 重启
- ✅ 对前端透明

### 实现步骤：

1. **使用本脚本部署 E2B**
   ```bash
   python deploy_to_e2b_prod.py
   ```

2. **部署代理到 Railway**
   - 创建简单的代理服务
   - 定期更新 E2B URL
   - 转发所有请求

3. **前端调用 Railway URL**
   - 固定 URL，无需修改
   - 自动路由到最新 E2B Sandbox

---

## 🚀 快速开始

```bash
# 1. 设置环境变量
export E2B_API_KEY=e2b_xxx
export GROQ_API_KEY=gsk_xxx

# 2. 运行生产部署（会自动重启）
python deploy_to_e2b_prod.py

# 3. 脚本会输出公网 URL
# 4. 前端使用该 URL（或通过代理）
```

---

## 📝 总结

**E2B 限制：**
- ❌ Sandbox 有固定超时（最多24小时）
- ❌ 无法永久运行
- ❌ 每次重启 URL 会变

**我们的解决方案：**
- ✅ 自动重启机制（近乎持续运行）
- ✅ 提前重启（零停机）
- ✅ 可选：代理层（固定 URL）

**这是在 E2B 限制下的最佳方案！** 🎉

