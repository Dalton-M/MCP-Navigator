#!/bin/bash
# 启动 MCP Stack Composer API 服务

# 设置环境变量
export GROQ_API_KEY="your_groq_key_here"
export GITHUB_TOKEN="your_github_token_here"
export BRAVE_API_KEY="your_brave_key_here"

cd "$(dirname "$0")"

echo "🚀 启动 MCP Stack Composer API 服务..."
echo ""
echo "访问地址："
echo "  • Swagger UI: http://localhost:8000/docs"
echo "  • ReDoc: http://localhost:8000/redoc"
echo "  • Health Check: http://localhost:8000/health"
echo ""

python3 api_server.py

