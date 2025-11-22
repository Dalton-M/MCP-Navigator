#!/usr/bin/env python3
"""
测试真实的 Docker MCP 调用
"""
import json
import subprocess
import os

# 设置环境变量
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "your_token_here")

print("=" * 70)
print("测试 GitHub MCP Docker 调用")
print("=" * 70)
print()

# 方法 1: 使用 MCP 标准协议（initialize + tool call）
print("测试 1: MCP 初始化握手")
print("-" * 70)

# MCP 协议需要先 initialize
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "mcp-stack-composer",
            "version": "0.1.0"
        }
    }
}

docker_cmd = [
    'docker', 'run', '-i', '--rm',
    '-e', f'GITHUB_TOKEN={GITHUB_TOKEN}',
    'mcp/github'
]

print(f"命令: {' '.join(docker_cmd)}")
print(f"输入: {json.dumps(init_request)}")
print()

try:
    # 发送初始化请求
    result = subprocess.run(
        docker_cmd,
        input=json.dumps(init_request).encode(),
        capture_output=True,
        timeout=10
    )
    
    print(f"返回码: {result.returncode}")
    print(f"stdout: {result.stdout.decode()[:500]}")
    print(f"stderr: {result.stderr.decode()[:500]}")
    print()
    
    if result.returncode == 0 and result.stdout:
        response = json.loads(result.stdout.decode())
        print("✓ 初始化成功!")
        print(f"响应: {json.dumps(response, indent=2)}")
    
except subprocess.TimeoutExpired:
    print("❌ 超时")
except json.JSONDecodeError as e:
    print(f"❌ JSON 解析失败: {e}")
    print(f"原始输出: {result.stdout.decode()}")
except Exception as e:
    print(f"❌ 错误: {e}")

print()
print("=" * 70)
print("测试 2: 调用 tools/list 列出可用工具")
print("=" * 70)
print()

list_tools_request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
}

print(f"输入: {json.dumps(list_tools_request)}")
print()

try:
    result = subprocess.run(
        docker_cmd,
        input=json.dumps(list_tools_request).encode(),
        capture_output=True,
        timeout=10
    )
    
    print(f"返回码: {result.returncode}")
    
    if result.returncode == 0 and result.stdout:
        stdout = result.stdout.decode().strip()
        print(f"输出: {stdout[:1000]}")
        
        try:
            response = json.loads(stdout)
            print("\n✓ 成功!")
            print(f"可用工具: {json.dumps(response, indent=2)[:500]}...")
        except:
            print("⚠️  输出不是有效的 JSON")
    else:
        print(f"stderr: {result.stderr.decode()}")
    
except Exception as e:
    print(f"❌ 错误: {e}")

print()
print("=" * 70)
print("测试 3: 使用交互式会话")
print("=" * 70)
print()

# 使用 Popen 进行交互式通信
print("启动交互式 MCP 会话...")

try:
    proc = subprocess.Popen(
        docker_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # 发送初始化
    print("→ 发送初始化请求")
    proc.stdin.write(json.dumps(init_request) + '\n')
    proc.stdin.flush()
    
    # 读取响应（设置超时）
    import select
    import sys
    
    # 等待输出（最多 5 秒）
    print("← 等待响应...")
    
    # 简单的超时读取
    proc.stdin.close()
    output, errors = proc.communicate(timeout=5)
    
    print(f"输出: {output[:1000]}")
    if errors:
        print(f"错误: {errors[:500]}")
    
    proc.terminate()
    
except subprocess.TimeoutExpired:
    print("⚠️  超时，可能需要不同的通信方式")
    proc.kill()
except Exception as e:
    print(f"❌ 错误: {e}")

print()
print("=" * 70)
print("结论与建议")
print("=" * 70)
print("""
MCP 服务器使用 stdio + JSON-RPC 协议。

标准流程：
1. 发送 initialize 请求
2. 等待 initialized 通知
3. 调用 tools/list 获取可用工具
4. 调用 tools/call 执行具体工具

如果直接调用失败，可能需要：
- 使用持久化的进程通信
- 或使用 GitHub REST API 作为 fallback（更可靠）
""")

