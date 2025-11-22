#!/usr/bin/env python3
"""
测试 GitHub REST API 直接调用（真实场景）
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp_client import call_github_mcp
import json

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ 请设置 GITHUB_TOKEN 环境变量")
    exit(1)

print("=" * 70)
print("测试真实 GitHub API 调用")
print("=" * 70)
print()

print(f"✓ GitHub Token: {GITHUB_TOKEN[:20]}...")
print()

# 测试 1: 列出 microsoft/vscode 的 issues
print("测试 1: 获取 microsoft/vscode 的前 5 个 open issues")
print("-" * 70)

try:
    result = call_github_mcp(
        tool='list_issues',
        args={
            'owner': 'microsoft',
            'repo': 'vscode',
            'state': 'open',
            'per_page': 5
        }
    )
    
    print("✓ 调用成功!")
    print(f"\n找到 {len(result['result'])} 个 issues:\n")
    
    for issue in result['result']:
        print(f"  #{issue['number']}: {issue['title']}")
        print(f"  状态: {issue['state']} | 评论: {issue['comments']}")
        if issue.get('labels'):
            print(f"  标签: {', '.join(issue['labels'][:3])}")
        print(f"  URL: {issue['url']}\n")
    
    print("\n" + "=" * 70)
    print("✅ GitHub API 调用成功 - 这就是真实的 MCP 调用!")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ 调用失败: {e}")
    import traceback
    traceback.print_exc()

