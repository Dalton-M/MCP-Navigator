#!/bin/bash
# E2B 快速部署脚本

set -e

echo "========================================"
echo "🚀 E2B Deployment Script"
echo "========================================"
echo ""

# 检查 E2B CLI
if ! command -v e2b &> /dev/null; then
    echo "❌ E2B CLI not found"
    echo "Installing E2B CLI..."
    npm install -g @e2b/cli
fi

echo "✅ E2B CLI installed"
echo ""

# 检查 E2B API Key
if [ -z "$E2B_API_KEY" ]; then
    echo "⚠️  E2B_API_KEY not set"
    echo "Please set your E2B API Key:"
    echo "  export E2B_API_KEY=e2b_xxx"
    echo ""
    echo "Get your key from: https://e2b.dev/dashboard"
    exit 1
fi

echo "✅ E2B_API_KEY configured"
echo ""

# 检查环境变量文件
if [ ! -f ".env.e2b" ]; then
    echo "⚠️  .env.e2b not found"
    echo "Creating from template..."
    cp env.e2b.example .env.e2b
    echo ""
    echo "📝 Please edit .env.e2b and add your API keys:"
    echo "  nano .env.e2b"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ .env.e2b found"
echo ""

# 询问是否构建模板
read -p "Build E2B template? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Building E2B template..."
    e2b template build --name mcp-stack-composer --version 1.0.0
    echo ""
    echo "✅ Template built successfully!"
    echo ""
fi

# 询问是否创建 Sandbox
read -p "Create E2B sandbox? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Creating E2B sandbox..."
    
    # 创建 Sandbox
    SANDBOX_OUTPUT=$(e2b sandbox create \
      --template mcp-stack-composer:1.0.0 \
      --name mcp-api-production \
      --env-file .env.e2b \
      --metadata '{"env":"production","project":"mcp-navigator"}')
    
    echo "$SANDBOX_OUTPUT"
    echo ""
    
    # 提取 Sandbox ID（简化版）
    echo "📋 To get your Sandbox URL, run:"
    echo "  e2b sandbox list"
    echo ""
fi

echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Get your Sandbox URL: e2b sandbox list"
echo "2. Test the API: curl https://YOUR_SANDBOX_URL/health"
echo "3. Update frontend with your URL"
echo ""
echo "📚 Full documentation: DEPLOY_E2B_FINAL.md"

