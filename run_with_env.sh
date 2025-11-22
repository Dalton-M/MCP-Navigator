#!/bin/bash
# 临时运行脚本 - 手动设置环境变量

# 使用方法：
# 1. 编辑此文件，填入你的 API keys
# 2. chmod +x run_with_env.sh
# 3. ./run_with_env.sh

# ===== 在这里填入你的 API Keys =====
export GROQ_API_KEY="your_groq_key_here"
export GITHUB_TOKEN="your_github_token_here" 
export BRAVE_API_KEY="your_brave_key_here"
# ====================================

# 检查 GROQ_API_KEY 是否设置
if [ "$GROQ_API_KEY" = "your_groq_key_here" ]; then
    echo "❌ 请先编辑 run_with_env.sh 并填入你的 GROQ_API_KEY"
    exit 1
fi

echo "✓ 环境变量已设置"
echo "✓ GROQ_API_KEY: ${GROQ_API_KEY:0:30}..."
echo "✓ GITHUB_TOKEN: ${GITHUB_TOKEN:0:20}..."

cd "$(dirname "$0")"
python3 run.py

