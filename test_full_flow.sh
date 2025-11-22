#!/bin/bash
# 完整流程测试脚本

export GROQ_API_KEY="your_groq_key_here"
export GITHUB_TOKEN="your_github_token_here"
export BRAVE_API_KEY="your_brave_key_here"

echo "🧪 测试完整流程..."
echo ""

cd "$(dirname "$0")"

# 自动输入测试需求
echo "I want an agent that reads GitHub issues, searches the web for similar solutions, and posts a daily summary." | python3 run.py

