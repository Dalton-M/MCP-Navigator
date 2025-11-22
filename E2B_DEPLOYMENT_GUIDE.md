# E2B 部署指南

本指南详细说明如何将 MCP Stack Composer 部署到 E2B (End-to-End Browser) 云端沙盒环境。

## 什么是 E2B？

E2B 是一个云端代码执行沙盒平台，提供：
- 安全的隔离执行环境
- 预配置的开发环境（Python, Node.js, etc.）
- 环境变量管理
- 持久化存储（可选）
- 适合运行 AI agents 和自动化任务

官网：https://e2b.dev/

---

## 部署步骤

### 第 1 步：创建 E2B 账号

1. 访问 [E2B Platform](https://e2b.dev/)
2. 点击 "Sign Up" 或 "Get Started"
3. 使用 GitHub、Google 或邮箱注册
4. 验证邮箱（如果需要）

### 第 2 步：创建新的 Sandbox

1. 登录 E2B Dashboard
2. 点击 "Create Sandbox" 或 "New Environment"
3. 选择环境类型：
   - **Runtime**: Python 3.11+
   - **Template**: Standard Python（或 Data Science 如果需要额外工具）
4. 配置选项：
   - **Name**: "mcp-stack-composer"
   - **Region**: 选择最近的地区（降低延迟）
5. 点击 "Create"

### 第 3 步：配置环境变量

在 E2B Sandbox 设置中配置环境变量：

1. 进入 Sandbox Settings → Environment Variables
2. 添加以下变量：

```bash
# 必需
GROQ_API_KEY=gsk_your_groq_api_key_here

# 可选（根据你要演示的 MCP）
GITHUB_TOKEN=ghp_your_github_token_here
BRAVE_API_KEY=BSA_your_brave_api_key_here
```

**注意：** E2B 会安全地存储这些环境变量，不会暴露给外部。

### 第 4 步：部署代码

#### 方案 A：从 Git 仓库部署（推荐）

1. 将代码推送到 GitHub（确保 `.env` 在 `.gitignore` 中）：
   ```bash
   cd /Users/lizhuolun/cursor/MCP-Navigator
   git init
   git add .
   git commit -m "Initial commit: MCP Stack Composer"
   git remote add origin https://github.com/YOUR_USERNAME/mcp-stack-composer.git
   git push -u origin main
   ```

2. 在 E2B Sandbox 的终端中：
   ```bash
   git clone https://github.com/YOUR_USERNAME/mcp-stack-composer.git
   cd mcp-stack-composer
   ```

#### 方案 B：直接上传文件

1. 在 E2B 界面使用文件上传功能
2. 上传整个项目目录（除了 `.env`）
3. 或使用 E2B CLI 工具同步文件

### 第 5 步：安装依赖

在 E2B Sandbox 终端执行：

```bash
cd mcp-stack-composer
pip install -r requirements.txt
```

### 第 6 步：运行测试

```bash
# 测试程序
python3 run.py
```

输入测试需求并观察结果。

---

## E2B 特定配置

### 持久化配置

如果需要保存配置或数据：

```python
# 在代码中使用 E2B 的持久化存储
import os
E2B_STORAGE = os.getenv('E2B_STORAGE_PATH', '/persistent')

# 保存结果
with open(f'{E2B_STORAGE}/results.json', 'w') as f:
    json.dump(results, f)
```

### 定时任务

在 E2B 中设置 cron job 运行定期任务：

```bash
# 在 E2B 终端
crontab -e

# 添加定时任务（每天 9:00 AM 运行）
0 9 * * * cd /home/user/mcp-stack-composer && python3 run.py < input.txt >> daily_log.txt
```

### 网络访问

E2B sandbox 允许出站网络访问，可以：
- 调用 Groq API
- 调用 GitHub API
- 访问 Docker MCP Hub
- 调用其他外部 API

---

## Docker MCP 集成（高级）

如果 E2B 支持 Docker-in-Docker，可以运行真实的 MCP 服务器：

```bash
# 在 E2B 终端
docker run -i --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  mcp/github
```

**注意：** 需要检查 E2B 是否支持 Docker。如果不支持，使用我们的 fallback 机制（直接调用 REST API）。

---

## 监控和调试

### 查看日志

```bash
# 实时查看应用日志
tail -f /path/to/logfile.txt

# 或使用 E2B 的日志查看功能
```

### 性能监控

```python
# 在代码中添加性能监控
import time

start = time.time()
result = call_mcp(...)
print(f"MCP call took {time.time() - start:.2f}s")
```

### 错误追踪

E2B 提供错误追踪功能，可以在 Dashboard 查看：
- 运行时错误
- API 调用失败
- 超时问题

---

## 成本估算

E2B 定价（参考官网最新信息）：

- **免费层**: 
  - 有限的执行时间/月
  - 适合开发和小规模演示

- **付费计划**:
  - 按使用量计费
  - 无限制的执行时间
  - 更多并发任务

对于 hackathon demo，免费层足够使用。

---

## 安全最佳实践

1. **环境变量管理**
   - 在 E2B UI 配置，不在代码中
   - 定期轮换 API keys
   - 使用只读权限的 tokens（如果可能）

2. **代码审查**
   - 确保没有硬编码的密钥
   - 检查 `.gitignore` 包含敏感文件

3. **访问控制**
   - E2B sandbox 设置适当的访问权限
   - 不要公开分享 sandbox URL

---

## 故障排查

### 问题：依赖安装失败

**解决方案：**
```bash
# 升级 pip
pip install --upgrade pip

# 逐个安装依赖
pip install python-dotenv
pip install requests
pip install rich
```

### 问题：环境变量未加载

**解决方案：**
```bash
# 手动验证
echo $GROQ_API_KEY

# 如果为空，重新在 E2B UI 设置
```

### 问题：网络超时

**解决方案：**
- 检查 E2B 的网络连接状态
- 增加 timeout 值
- 使用 E2B 提供的代理（如果有）

---

## 演示建议

对于 hackathon 演示：

1. **准备一个测试脚本**：
   ```bash
   # test_demo.sh
   echo "I want an agent that monitors GitHub issues and sends alerts" | python3 run.py
   ```

2. **录制屏幕**：
   - 显示 E2B Dashboard
   - 运行程序
   - 展示完整输出

3. **准备备用方案**：
   - 本地也能运行的版本
   - 预录的演示视频

---

## 下一步

部署成功后：

1. **测试完整流程**
   - 尝试不同的需求描述
   - 验证 Groq 集成
   - 测试 MCP 调用

2. **优化性能**
   - 缓存常用的 MCP 目录
   - 减少不必要的 API 调用

3. **准备演示**
   - 录制 demo 视频
   - 准备演讲内容
   - 测试各种边界情况

4. **文档完善**
   - 更新 README
   - 添加使用示例
   - 准备 FAQ

---

## 相关资源

- [E2B Documentation](https://e2b.dev/docs)
- [E2B Python SDK](https://github.com/e2b-dev/e2b)
- [E2B Examples](https://e2b.dev/examples)
- [MCP Stack Composer GitHub](https://github.com/YOUR_USERNAME/mcp-stack-composer)

---

## 联系支持

如果遇到 E2B 相关问题：
- E2B Discord: https://discord.gg/e2b
- E2B GitHub Issues: https://github.com/e2b-dev/e2b/issues
- E2B 官方文档: https://e2b.dev/docs

