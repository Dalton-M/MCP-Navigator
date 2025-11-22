#!/bin/bash
# 测试 API Server 是否正常工作

# 检查参数
if [ -z "$1" ]; then
    API_URL="http://localhost:8000"
else
    API_URL="$1"
fi

echo "========================================"
echo "🧪 Testing API Server"
echo "========================================"
echo "API URL: $API_URL"
echo ""

# 测试 1: 健康检查
echo "Test 1: Health Check"
echo "GET $API_URL/health"
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
echo "Response: $HEALTH_RESPONSE"
echo ""

# 测试 2: 列出 MCPs
echo "Test 2: List MCPs"
echo "GET $API_URL/api/v1/mcps"
MCPS_RESPONSE=$(curl -s "$API_URL/api/v1/mcps")
echo "Response: ${MCPS_RESPONSE:0:200}..."
echo ""

# 测试 3: Compose Agent
echo "Test 3: Compose Agent"
echo "POST $API_URL/api/v1/compose"

COMPOSE_REQUEST='{
  "description": "I want an agent that reads GitHub issues and searches the web for solutions",
  "top_k": 3
}'

echo "Request: $COMPOSE_REQUEST"
echo ""

COMPOSE_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/compose" \
  -H "Content-Type: application/json" \
  -d "$COMPOSE_REQUEST")

# 检查响应
if echo "$COMPOSE_RESPONSE" | grep -q "recommended_mcps"; then
    echo "✅ Compose API works!"
    echo "Response preview:"
    echo "$COMPOSE_RESPONSE" | python3 -m json.tool 2>/dev/null | head -30
else
    echo "❌ Compose API failed"
    echo "Response: $COMPOSE_RESPONSE"
fi

echo ""
echo "========================================"
echo "✅ API Testing Complete"
echo "========================================"
echo ""
echo "💡 View full API docs at: $API_URL/docs"

