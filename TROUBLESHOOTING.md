# 故障排查指南

## 问题：.env 文件无法被读取（Operation not permitted）

### 症状
- 程序显示 "✓ Groq API connected" 但实际调用时报错 400
- 或者显示 "Running in MOCK MODE"
- 错误信息：`PermissionError: [Errno 1] Operation not permitted: '.env'`

### 原因
macOS 的安全机制（SIP - System Integrity Protection）可能阻止某些应用读取 .env 文件。

### 解决方案

#### 方案 1：使用环境变量（最简单）

在运行程序前，先在终端中导出环境变量：

```bash
cd /Users/lizhuolun/cursor/MCP-Navigator

# 设置环境变量（替换为你的实际 keys）
export GROQ_API_KEY="gsk_your_actual_key_here"
export GITHUB_TOKEN="ghp_your_actual_token_here"
export BRAVE_API_KEY="BSA_your_actual_key_here"

# 验证设置成功
echo "GROQ_API_KEY: ${GROQ_API_KEY:0:30}..."

# 运行程序
python3 run.py
```

#### 方案 2：使用 run_with_env.sh 脚本

1. 编辑 `run_with_env.sh` 文件：
   ```bash
   nano run_with_env.sh
   # 或
   open -e run_with_env.sh
   ```

2. 填入你的 API keys：
   ```bash
   export GROQ_API_KEY="gsk_实际的key"
   export GITHUB_TOKEN="ghp_实际的token"
   ```

3. 保存并运行：
   ```bash
   chmod +x run_with_env.sh
   ./run_with_env.sh
   ```

#### 方案 3：检查和修复 .env 文件

1. 检查 .env 文件是否存在：
   ```bash
   ls -la .env
   ```

2. 如果不存在，创建它：
   ```bash
   cat > .env << 'EOF'
   GROQ_API_KEY=gsk_your_key_here
   GITHUB_TOKEN=ghp_your_token_here
   BRAVE_API_KEY=BSA_your_key_here
   EOF
   ```

3. 设置正确的权限：
   ```bash
   chmod 600 .env
   chown $(whoami) .env
   ```

4. 验证内容：
   ```bash
   cat .env
   ```

#### 方案 4：在 Python 中直接设置（临时测试用）

创建 `test_with_keys.py`：

```python
import os
import sys

# 直接设置环境变量（用于测试）
os.environ['GROQ_API_KEY'] = 'gsk_your_actual_key'
os.environ['GITHUB_TOKEN'] = 'ghp_your_actual_token'

# 然后导入并运行
sys.path.insert(0, os.path.dirname(__file__))
from app.main import main
main()
```

---

## 问题：Groq API 400 错误

### 症状
```
⚠️  Groq API error: 400 Client Error: Bad Request
```

### 可能原因和解决方案

#### 1. API Key 无效或过期

**检查**：
```bash
# 验证 key 格式（应该以 gsk_ 开头）
echo $GROQ_API_KEY
```

**解决**：
- 访问 https://console.groq.com/keys
- 检查 key 是否有效
- 如果过期，重新生成新的 key

#### 2. API Key 未正确加载

**检查**：
```bash
python3 -c "import os; print('Key loaded:', bool(os.getenv('GROQ_API_KEY')))"
```

**解决**：使用上面的环境变量方案

#### 3. 请求格式问题

已在代码中修复，确保使用最新版本：
```bash
git pull  # 如果从 Git 克隆
# 或查看文件修改日期
ls -l app/planner.py
```

---

## 问题：MCP 调用失败

### 症状
```
⚠️  Real MCP call failed: Failed to parse MCP response
```

### 解决方案

#### 1. 使用直接 API 调用（Fallback）

MCP Docker 调用比较复杂，程序会自动降级到直接 API 调用。这是正常的。

#### 2. 检查 Docker 是否运行

```bash
docker ps
docker version
```

#### 3. 测试 GitHub API

```bash
export GITHUB_TOKEN="your_token"
python3 -c "
import requests
headers = {'Authorization': f'token $GITHUB_TOKEN'}
r = requests.get('https://api.github.com/repos/microsoft/vscode/issues?per_page=3', headers=headers)
print(f'Status: {r.status_code}')
print(r.json()[0]['title'])
"
```

---

## 验证步骤

### 完整的验证流程

```bash
# 1. 进入项目目录
cd /Users/lizhuolun/cursor/MCP-Navigator

# 2. 设置环境变量（替换为你的实际值）
export GROQ_API_KEY="gsk_..."
export GITHUB_TOKEN="ghp_..."

# 3. 验证环境变量
python3 -c "
import os
print('✓ GROQ_API_KEY:', 'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET')
print('✓ GITHUB_TOKEN:', 'SET' if os.getenv('GITHUB_TOKEN') else 'NOT SET')
"

# 4. 测试 Groq API
python3 -c "
import os
import requests
headers = {'Authorization': f'Bearer {os.getenv(\"GROQ_API_KEY\")}', 'Content-Type': 'application/json'}
payload = {'model': 'llama-3.1-70b-versatile', 'messages': [{'role': 'user', 'content': 'Say hello'}], 'temperature': 0.1}
r = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=payload)
print(f'Groq API Status: {r.status_code}')
if r.status_code == 200:
    print('✓ Groq API working!')
else:
    print(f'✗ Error: {r.text[:200]}')
"

# 5. 运行程序
python3 run.py
```

---

## 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| 400 Bad Request | 请求格式错误或 API key 无效 | 检查 API key 是否正确 |
| 401 Unauthorized | API key 未提供或无效 | 重新生成 API key |
| 403 Forbidden | 权限不足 | 检查 API key 权限 |
| 429 Too Many Requests | 超出速率限制 | 等待一段时间后重试 |
| 500 Server Error | Groq 服务器错误 | 等待片刻后重试 |

---

## 获取帮助

如果以上方案都无法解决问题：

1. 查看完整的错误信息
2. 检查 Groq Console 的使用情况：https://console.groq.com/
3. 确认 API key 有效且有足够配额
4. 尝试在浏览器中访问 Groq API 文档

---

## 快速解决方案（推荐）

**最快的方法**：

```bash
# 1. 在终端运行以下命令（一次性）
cd /Users/lizhuolun/cursor/MCP-Navigator

# 2. 复制粘贴你的 API keys（替换下面的值）
export GROQ_API_KEY="gsk_在这里粘贴你的实际key"
export GITHUB_TOKEN="ghp_在这里粘贴你的实际token"

# 3. 直接运行
python3 run.py
```

这个方法绕过了 .env 文件的权限问题，应该能立即工作！

