#!/bin/bash
# E2B API Server 启动脚本
# 用途：在 E2B Sandbox 中后台启动 API Server

set -e

echo "========================================"
echo "🚀 Starting MCP Stack Composer API"
echo "========================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "api_server.py" ]; then
    echo "❌ Error: api_server.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# 检查依赖
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI not installed"
    echo "Running: pip install -r requirements.txt"
    pip install -r requirements.txt
fi
echo "✅ Dependencies OK"
echo ""

# 检查环境变量
echo "🔑 Checking environment variables..."
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  Warning: GROQ_API_KEY not set (will run in MOCK mode)"
else
    echo "✅ GROQ_API_KEY configured"
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  Warning: GITHUB_TOKEN not set"
else
    echo "✅ GITHUB_TOKEN configured"
fi
echo ""

# 停止已存在的进程
if [ -f "api_server.pid" ]; then
    OLD_PID=$(cat api_server.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "🛑 Stopping existing server (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
fi

# 启动服务
echo "🚀 Starting API server..."
nohup python3 api_server.py > api_server.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > api_server.pid

# 等待服务启动
echo "⏳ Waiting for server to start..."
sleep 3

# 检查进程是否还在运行
if ps -p $NEW_PID > /dev/null 2>&1; then
    echo ""
    echo "✅ API Server started successfully!"
    echo "   PID: $NEW_PID"
    echo "   Log: api_server.log"
    echo ""
    echo "📚 Endpoints:"
    echo "   • Health: http://0.0.0.0:8000/health"
    echo "   • Docs: http://0.0.0.0:8000/docs"
    echo "   • Compose: POST http://0.0.0.0:8000/api/v1/compose"
    echo ""
    echo "💡 Commands:"
    echo "   • View logs: tail -f api_server.log"
    echo "   • Stop server: kill $NEW_PID"
    echo ""
    echo "🌐 E2B Public URL:"
    echo "   https://YOUR_SANDBOX_ID-8000.e2b.dev"
    echo ""
else
    echo ""
    echo "❌ Failed to start server"
    echo "Check the log file: cat api_server.log"
    exit 1
fi

