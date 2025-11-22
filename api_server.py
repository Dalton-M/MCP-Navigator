#!/usr/bin/env python3
"""
MCP Stack Composer - API Server
FastAPI 服务，提供 RESTful API 和 Swagger UI
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
import uvicorn

from app.config import Config
from app.planner import get_capabilities_from_description
from app.matcher import load_catalog, match_mcp
from app.snippet_generator import generate_snippet
from app.mcp_client import call_mcp

# 初始化 FastAPI
app = FastAPI(
    title="MCP Stack Composer API",
    description="智能 MCP 编排服务 - 从自然语言需求到可执行代码",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS 配置（如果需要前端）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic Models ====================

class AgentRequest(BaseModel):
    """用户输入的 Agent 需求"""
    description: str = Field(
        ...,
        description="自然语言描述的 Agent 需求",
        json_schema_extra={"example": "I want an agent that reads GitHub issues, searches the web for solutions, and posts a daily summary"}
    )
    top_k: Optional[int] = Field(
        default=3,
        description="返回 Top K 个推荐的 MCP",
        ge=1,
        le=10
    )


class CapabilityAnalysis(BaseModel):
    """能力分析结果"""
    capabilities: List[str]
    reasoning: str
    confidence: float


class MCPRecommendation(BaseModel):
    """MCP 推荐"""
    mcp_id: str
    display_name: str
    description: str
    score: float
    exact_matches: List[str]
    partial_matches: List[str]
    env_vars: List[str]
    docker_image: str
    example_tools: List[str]


class CodeSnippet(BaseModel):
    """生成的代码片段"""
    markdown: str
    env_vars: List[str]


class MCPCallResult(BaseModel):
    """MCP 调用结果"""
    mcp_id: str
    tool: str
    success: bool
    result: Optional[Any] = None  # 可以是 Dict, List, 或其他类型
    error: Optional[str] = None


class AgentResponse(BaseModel):
    """完整的 Agent 编排响应"""
    request: str
    capabilities: CapabilityAnalysis
    recommended_mcps: List[MCPRecommendation]
    code_snippet: CodeSnippet
    demo_call: Optional[MCPCallResult] = None
    status: str


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """服务健康检查"""
    return {
        "service": "MCP Stack Composer",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "compose": "/api/v1/compose",
            "analyze": "/api/v1/analyze",
            "recommend": "/api/v1/recommend",
            "generate": "/api/v1/generate",
            "call": "/api/v1/call"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "groq_configured": bool(Config.GROQ_API_KEY),
        "github_configured": bool(Config.GITHUB_TOKEN),
        "mock_mode": Config.USE_MOCK_MODE
    }


@app.post("/api/v1/compose", response_model=AgentResponse)
async def compose_agent(request: AgentRequest):
    """
    完整的 Agent 编排流程（一站式）
    
    从用户的自然语言需求，到推荐的 MCP、生成的代码、以及演示调用
    """
    try:
        description = request.description
        
        # Step 1: 分析能力
        caps_result = get_capabilities_from_description(description)
        capabilities = caps_result.get("capabilities", [])
        
        if not capabilities:
            raise HTTPException(
                status_code=400, 
                detail="无法从描述中提取有效的 capabilities"
            )
        
        # Step 2: 匹配 MCP
        catalog = load_catalog()
        matched = match_mcp(capabilities, catalog, top_k=request.top_k)
        
        if not matched:
            raise HTTPException(
                status_code=404,
                detail="没有找到匹配的 MCP 服务器"
            )
        
        # 转换为 response model
        mcp_recommendations = []
        for m in matched:
            mcp_recommendations.append(MCPRecommendation(
                mcp_id=m['mcp_id'],
                display_name=m.get('display_name', ''),
                description=m.get('description', ''),
                score=m['score'],
                exact_matches=m.get('exact_matches', []),
                partial_matches=m.get('partial_matches', []),
                env_vars=m.get('env_vars', []),
                docker_image=m.get('docker_image', ''),
                example_tools=m.get('example_tools', [])
            ))
        
        # Step 3: 生成代码
        snippet_md = generate_snippet(description, matched[:3])
        
        # 提取环境变量
        all_env_vars = []
        for m in matched[:3]:
            all_env_vars.extend(m.get('env_vars', []))
        unique_env_vars = list(dict.fromkeys(all_env_vars))
        
        # Step 4: 演示调用（可选）
        demo_call = None
        try:
            # 尝试调用第一个 MCP
            first_mcp = matched[0]['mcp_id']
            if first_mcp == 'github':
                result = call_mcp('github', 'list_issues', {
                    'owner': 'microsoft',
                    'repo': 'vscode',
                    'per_page': 3
                })
                demo_call = MCPCallResult(
                    mcp_id=result.get('mcp_id', first_mcp),
                    tool=result.get('tool', 'list_issues'),
                    success=result.get('success', False),
                    result=result.get('result', None),
                    error=None
                )
        except Exception as e:
            demo_call = MCPCallResult(
                mcp_id=first_mcp if 'first_mcp' in locals() else 'unknown',
                tool='demo',
                success=False,
                result=None,
                error=str(e)
            )
        
        # 构建响应
        return AgentResponse(
            request=description,
            capabilities=CapabilityAnalysis(
                capabilities=capabilities,
                reasoning=caps_result.get("reasoning", ""),
                confidence=caps_result.get("confidence", 0.0)
            ),
            recommended_mcps=mcp_recommendations,
            code_snippet=CodeSnippet(
                markdown=snippet_md,
                env_vars=unique_env_vars
            ),
            demo_call=demo_call,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze")
async def analyze_capabilities(request: AgentRequest):
    """
    步骤 1: 分析用户需求，提取 capability 标签
    """
    try:
        result = get_capabilities_from_description(request.description)
        return {
            "description": request.description,
            "capabilities": result.get("capabilities", []),
            "reasoning": result.get("reasoning", ""),
            "confidence": result.get("confidence", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recommend")
async def recommend_mcps(capabilities: List[str], top_k: int = 5):
    """
    步骤 2: 根据 capabilities 推荐 MCP 服务器
    """
    try:
        catalog = load_catalog()
        matched = match_mcp(capabilities, catalog, top_k=top_k)
        
        return {
            "capabilities": capabilities,
            "matched_count": len(matched),
            "recommendations": matched
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateRequest(BaseModel):
    description: str
    mcp_ids: List[str] = Field(description="要生成代码的 MCP IDs")


@app.post("/api/v1/generate")
async def generate_code(request: GenerateRequest):
    """
    步骤 3: 生成环境配置和代码示例
    """
    try:
        # 加载 MCP 信息
        catalog = load_catalog()
        selected_mcps = []
        
        for mcp_id in request.mcp_ids:
            if mcp_id in catalog:
                mcp_info = catalog[mcp_id]
                mcp_info['mcp_id'] = mcp_id
                selected_mcps.append(mcp_info)
        
        if not selected_mcps:
            raise HTTPException(
                status_code=404,
                detail="未找到指定的 MCP"
            )
        
        snippet = generate_snippet(request.description, selected_mcps)
        
        return {
            "description": request.description,
            "mcps": request.mcp_ids,
            "code_snippet": snippet
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MCPCallRequest(BaseModel):
    mcp_id: str = Field(description="MCP 标识符", json_schema_extra={"example": "github"})
    tool: str = Field(description="工具名称", json_schema_extra={"example": "list_issues"})
    args: Dict = Field(
        default={},
        description="工具参数",
        json_schema_extra={"example": {"owner": "microsoft", "repo": "vscode", "per_page": 5}}
    )
    use_mock: Optional[bool] = Field(
        default=None,
        description="强制使用 mock 模式"
    )


@app.post("/api/v1/call")
async def call_mcp_tool(request: MCPCallRequest):
    """
    步骤 4: 调用 MCP 工具（真实或 mock）
    """
    try:
        result = call_mcp(
            mcp_id=request.mcp_id,
            tool=request.tool,
            args=request.args,
            use_mock=request.use_mock
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"MCP 调用失败: {str(e)}"
        )


@app.get("/api/v1/mcps")
async def list_mcps():
    """
    列出所有可用的 MCP 服务器
    """
    try:
        catalog = load_catalog()
        return {
            "total": len(catalog),
            "mcps": catalog
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/mcps/{mcp_id}")
async def get_mcp_info(mcp_id: str):
    """
    获取特定 MCP 的详细信息
    """
    try:
        catalog = load_catalog()
        if mcp_id not in catalog:
            raise HTTPException(
                status_code=404,
                detail=f"MCP '{mcp_id}' 不存在"
            )
        
        return {
            "mcp_id": mcp_id,
            **catalog[mcp_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 启动服务 ====================

if __name__ == "__main__":
    # Set UTF-8 encoding for console output
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 验证配置
    Config.validate()

    print("=" * 70)
    print("MCP Stack Composer API Server")
    print("=" * 70)
    print(f"\nServer starting...")
    print(f"Groq API: {'Configured' if Config.GROQ_API_KEY else 'Mock Mode'}")
    print(f"GitHub Token: {'Configured' if Config.GITHUB_TOKEN else 'Not set'}")
    print(f"\nDocumentation:")
    print(f"   - Swagger UI: http://localhost:8000/docs")
    print(f"   - ReDoc: http://localhost:8000/redoc")
    print(f"\nEndpoints:")
    print(f"   - Health: http://localhost:8000/health")
    print(f"   - Compose: POST http://localhost:8000/api/v1/compose")
    print(f"   - List MCPs: http://localhost:8000/api/v1/mcps")
    print(f"\n" + "=" * 70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

