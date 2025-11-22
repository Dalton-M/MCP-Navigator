#!/bin/bash
# E2B API Server 停止脚本

echo "🛑 Stopping MCP Stack Composer API..."

if [ ! -f "api_server.pid" ]; then
    echo "❌ No PID file found"
    echo "Server might not be running or was started manually"
    exit 1
fi

PID=$(cat api_server.pid)

if ps -p $PID > /dev/null 2>&1; then
    kill $PID
    echo "✅ Server stopped (PID: $PID)"
    rm api_server.pid
else
    echo "⚠️  Process $PID not found (already stopped?)"
    rm api_server.pid
fi

