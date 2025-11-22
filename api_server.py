#!/usr/bin/env python3
"""
MCPilot - API Server
FastAPI service providing RESTful API and Swagger UI
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
import uvicorn
from pathlib import Path
import markdown

from app.config import Config
from app.planner import get_capabilities_from_description
from app.matcher import load_catalog, match_mcp
from app.snippet_generator import generate_snippet
from app.mcp_client import call_mcp
from app.workflow_templates import WORKFLOW_TEMPLATES, get_template_summary, get_template
from app.cost_estimator import CostEstimator
from app.mermaid_generator import generate_workflow_diagram, generate_execution_diagram, generate_cost_breakdown_diagram

# Initialize FastAPI
app = FastAPI(
    title="MCPilot API",
    description="Intelligent MCP orchestration service - from natural language to executable code",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS configuration (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates setup
BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))


# ==================== Pydantic Models ====================

class AgentRequest(BaseModel):
    """User's agent requirements input"""
    description: str = Field(
        ..., 
        description="Natural language description of agent requirements",
        json_schema_extra={"example": "I want an agent that reads GitHub issues, searches the web for solutions, and posts a daily summary"}
    )
    top_k: Optional[int] = Field(
        default=3,
        description="Number of top MCP recommendations to return",
        ge=1,
        le=10
    )


class CapabilityAnalysis(BaseModel):
    """Capability analysis result"""
    capabilities: List[str]
    reasoning: str
    confidence: float


class MCPRecommendation(BaseModel):
    """MCP recommendation"""
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
    """Generated code snippet"""
    markdown: str
    env_vars: List[str]


class MCPCallResult(BaseModel):
    """MCP call result"""
    mcp_id: str
    tool: str
    success: bool
    result: Optional[Any] = None  # Can be Dict, List, or other types
    error: Optional[str] = None


class WorkflowExecutionResult(BaseModel):
    """Multi-MCP workflow execution result"""
    status: str
    total_time: float
    steps_completed: int
    total_steps: int
    results: Dict[str, Any]
    error: Optional[str] = None


class AgentResponse(BaseModel):
    """Complete Agent Composition Response"""
    request: str
    capabilities: CapabilityAnalysis
    recommended_mcps: List[MCPRecommendation]
    code_snippet: CodeSnippet
    cost_estimate: Optional[Dict] = None
    workflow_execution: Optional[WorkflowExecutionResult] = None
    mermaid_diagram: Optional[str] = None  # NEW! Workflow visualization
    demo_call: Optional[MCPCallResult] = None
    status: str


# ==================== Helper Functions ====================

async def execute_multi_mcp_workflow(matched_mcps: List[Dict], description: str) -> Dict:
    """
    Execute Multi-MCP workflow automatically
    
    Args:
        matched_mcps: List of matched MCP servers
        description: Original user description
    
    Returns:
        dict: {
            "status": "success" | "partial" | "failed",
            "total_time": 8.5,
            "steps_completed": 2,
            "total_steps": 3,
            "results": {
                "github": {...},
                "brave-search": {...},
                "analysis": {...}
            }
        }
    """
    import time
    
    start_time = time.time()
    results = {}
    steps_completed = 0
    total_steps = 0
    
    # Identify which MCPs to call
    has_github = any('github' in m['mcp_id'].lower() for m in matched_mcps)
    has_search = any('search' in m['mcp_id'].lower() or 'brave' in m['mcp_id'].lower() 
                     for m in matched_mcps)
    
    total_steps = (1 if has_github else 0) + (1 if has_search else 0) + 1  # +1 for analysis
    
    # Step 1: GitHub MCP (if available)
    if has_github:
        try:
            github_result = call_mcp('github', 'list_issues', {
                'owner': 'microsoft',
                'repo': 'vscode',
                'state': 'open',
                'per_page': 5
            })
            results['github'] = github_result
            steps_completed += 1
        except Exception as e:
            results['github'] = {"error": str(e)}
    
    # Step 2: Brave Search MCP (if available and GitHub succeeded)
    if has_search and results.get('github', {}).get('success'):
        try:
            github_issues = results['github'].get('result', [])
            search_results = []
            
            # RATE LIMIT PROTECTION: Only search for 1 issue
            max_searches = 1  # Limit to 1 search to avoid rate limits
            
            for idx, issue in enumerate(github_issues[:max_searches]):
                try:
                    # NO delay needed for first search
                    # For subsequent searches (if any), wait 5 seconds
                    if idx > 0:
                        time.sleep(5)
                    
                    search_result = call_mcp('brave-search', 'search', {
                        'query': f"{issue.get('title', '')} solution",
                        'num_results': 3
                    })
                    search_results.append({
                        'issue_number': issue.get('number'),
                        'solutions': search_result.get('result', {})
                    })
                except Exception as e:
                    search_results.append({
                        'issue_number': issue.get('number'),
                        'error': str(e),
                        'note': 'Rate limit or API error'
                    })
            
            results['brave-search'] = {
                'success': True,
                'total_searches': len(search_results),
                'results': search_results
            }
            steps_completed += 1
        except Exception as e:
            results['brave-search'] = {"error": str(e)}
    
    # Step 3: Generate analysis
    try:
        github_data = results.get('github', {}).get('result', [])
        search_data = results.get('brave-search', {}).get('results', [])
        
        analysis = {
            "total_issues": len(github_data),
            "issues_with_solutions": len(search_data),
            "summary": f"Processed {len(github_data)} GitHub issues, found solutions for {len(search_data)} of them"
        }
        
        results['analysis'] = analysis
        steps_completed += 1
    except Exception as e:
        results['analysis'] = {"error": str(e)}
    
    total_time = time.time() - start_time
    
    status = "success" if steps_completed == total_steps else (
        "partial" if steps_completed > 0 else "failed"
    )
    
    return {
        "status": status,
        "total_time": round(total_time, 2),
        "steps_completed": steps_completed,
        "total_steps": total_steps,
        "results": results
    }


# ==================== API Endpoints ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main frontend page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api")
async def api_root():
    """API service information"""
    return {
        "service": "MCPilot",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "compose": "/api/v1/compose",
            "analyze": "/api/v1/analyze",
            "recommend": "/api/v1/recommend",
            "generate": "/api/v1/generate",
            "call": "/api/v1/call",
            "templates": "/api/v1/templates",
            "estimate-cost": "/api/v1/estimate-cost",
            "execute-workflow": "/api/v1/workflows/execute"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "groq_configured": bool(Config.GROQ_API_KEY),
        "github_configured": bool(Config.GITHUB_TOKEN),
        "brave_configured": bool(Config.BRAVE_API_KEY),
        "mock_mode": Config.USE_MOCK_MODE
    }


@app.post("/api/v1/compose")
async def compose_agent(request_obj: Request):
    """
    Complete Agent Orchestration Workflow

    Supports both JSON API calls and HTMX form submissions
    - HTMX: multipart/form-data with agent_description and top_k
    - JSON: {"description": "...", "top_k": 3}
    """
    try:
        # Check if this is an HTMX request
        is_htmx = request_obj.headers.get("HX-Request") == "true"

        # Determine content type and parse accordingly
        content_type = request_obj.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            # JSON API request
            body = await request_obj.json()
            description = body.get("description")
            top_k_val = body.get("top_k", 3)
        else:
            # Form data (HTMX or multipart)
            form_data = await request_obj.form()
            description = form_data.get("agent_description")
            top_k_val = int(form_data.get("top_k", 3))

        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
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
        matched = match_mcp(capabilities, catalog, top_k=top_k_val)
        
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
        
        # Step 3: Generate code (use top_k_val MCPs)
        snippet_md = generate_snippet(description, matched[:top_k_val])

        # Extract environment variables
        all_env_vars = []
        for m in matched[:top_k_val]:
            all_env_vars.extend(m.get('env_vars', []))
        unique_env_vars = list(dict.fromkeys(all_env_vars))

        # Step 4: Cost Estimation (NEW!)
        mcp_ids = [m['mcp_id'] for m in matched[:top_k_val]]
        estimator = CostEstimator()
        cost_estimate = estimator.estimate_by_mcps(mcp_ids, daily_runs=1)

        # Step 5: Multi-MCP Workflow Execution (NEW!)
        workflow_execution = await execute_multi_mcp_workflow(matched[:top_k_val], description)

        # Step 6: Generate Mermaid Diagram (NEW!)
        mermaid_diagram = generate_workflow_diagram(matched[:top_k_val], workflow_execution)

        # Step 7: Demo call (backward compatibility, only if workflow failed)
        demo_call = None
        if not workflow_execution or workflow_execution.get("status") == "failed":
            github_mcp = None
            for mcp in matched:
                if 'github' in mcp['mcp_id'].lower():
                    github_mcp = mcp
                    break

            if github_mcp:
                try:
                    result = call_mcp('github', 'list_issues', {
                        'owner': 'microsoft',
                        'repo': 'vscode',
                        'per_page': 3
                    })
                    demo_call = MCPCallResult(
                        mcp_id=result.get('mcp_id', 'github'),
                        tool=result.get('tool', 'list_issues'),
                        success=result.get('success', False),
                        result=result.get('result', None),
                        error=None
                    )
                except Exception as e:
                    demo_call = MCPCallResult(
                        mcp_id='github',
                        tool='list_issues',
                        success=False,
                        result=None,
                        error=str(e)
                    )

        # Parse markdown to HTML for better rendering (HTMX)
        code_snippet_html = markdown.markdown(
            snippet_md,
            extensions=['fenced_code', 'tables', 'nl2br']
        )

        # Build response data for HTMX template
        template_data = {
            "user_description": description,
            "capabilities": capabilities,
            "reasoning": caps_result.get("reasoning", ""),
            "confidence": caps_result.get("confidence", 0.0),
            "matched_mcps": matched,
            "code_snippet": code_snippet_html,
            "code_snippet_raw": snippet_md,  # Keep raw for copy functionality
            "env_vars": unique_env_vars,
            "cost_estimate": cost_estimate,  # NEW: Cost estimation
            "workflow_execution": workflow_execution,  # NEW: Workflow execution results
            "mermaid_diagram": mermaid_diagram,  # NEW: Mermaid visualization
            "demo_call": None,
            "status": "success"
        }

        # Add demo call if available
        if demo_call:
            template_data["demo_call"] = {
                "mcp_id": demo_call.mcp_id,
                "tool_name": demo_call.tool,
                "status": "success" if demo_call.success else "error",
                "params": {"owner": "microsoft", "repo": "vscode", "per_page": 3},
                "result": demo_call.result if demo_call.success else demo_call.error
            }

        # Return HTML for HTMX requests, JSON for API requests
        if is_htmx:
            from fastapi.responses import HTMLResponse
            html_content = templates.TemplateResponse(
                "components/results.html",
                {
                    "request": request_obj,
                    **template_data
                }
            )
            return html_content
        else:
            # Return JSON for API calls (with all new features)
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
                cost_estimate=cost_estimate,
                workflow_execution=workflow_execution,
                mermaid_diagram=mermaid_diagram,
                demo_call=demo_call,
                status="success"
            )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERROR in compose_agent: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze")
async def analyze_capabilities(request: AgentRequest):
    """
    Step 1: Analyze user requirements and extract capability tags
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
    Step 2: Recommend MCP servers based on capabilities
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
    mcp_ids: List[str] = Field(description="MCP IDs to generate code for")


@app.post("/api/v1/generate")
async def generate_code(request: GenerateRequest):
    """
    Step 3: Generate environment configuration and code examples
    """
    try:
        # Load MCP information
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
                detail="Specified MCPs not found"
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
    mcp_id: str = Field(description="MCP identifier", json_schema_extra={"example": "github"})
    tool: str = Field(description="Tool name", json_schema_extra={"example": "list_issues"})
    args: Dict = Field(
        default={},
        description="Tool arguments",
        json_schema_extra={"example": {"owner": "microsoft", "repo": "vscode", "per_page": 5}}
    )
    use_mock: Optional[bool] = Field(
        default=None,
        description="Force mock mode"
    )


@app.post("/api/v1/call")
async def call_mcp_tool(request: MCPCallRequest):
    """
    Step 4: Call MCP tool (real or mock)
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
            detail=f"MCP call failed: {str(e)}"
        )


@app.get("/api/v1/mcps")
async def list_mcps():
    """
    List all available MCP servers
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
    Get detailed information for a specific MCP
    """
    try:
        catalog = load_catalog()
        if mcp_id not in catalog:
            raise HTTPException(
                status_code=404,
                detail=f"MCP '{mcp_id}' not found"
            )
        
        return {
            "mcp_id": mcp_id,
            **catalog[mcp_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Outstanding Features ====================

@app.get("/api/v1/templates")
async def list_workflow_templates():
    """
    🌟 Outstanding Feature 1: List all pre-built workflow templates
    
    Returns available workflow templates that users can use directly
    """
    try:
        return {
            "templates": WORKFLOW_TEMPLATES,
            "summary": get_template_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/templates/{template_id}")
async def get_workflow_template(template_id: str):
    """
    🌟 Get detailed information for a specific template
    """
    try:
        template = get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{template_id}' not found"
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CostEstimateRequest(BaseModel):
    mcps: List[str] = Field(description="List of MCP IDs", example=["github", "brave-search"])
    daily_runs: int = Field(default=1, description="Number of runs per day", ge=1, le=1000)


@app.post("/api/v1/estimate-cost")
async def estimate_workflow_cost(request: CostEstimateRequest):
    """
    🌟 Outstanding Feature 2: Cost Estimation
    
    Estimate costs based on MCP combination
    """
    try:
        estimator = CostEstimator()
        cost_data = estimator.estimate_by_mcps(request.mcps, request.daily_runs)
        
        return {
            "mcps": request.mcps,
            "daily_runs": request.daily_runs,
            "cost_estimate": cost_data,
            "currency": "USD"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WorkflowExecuteRequest(BaseModel):
    template_id: str = Field(description="Template ID", example="github_daily_report")
    config: Dict = Field(
        default={},
        description="Workflow configuration parameters",
        example={"owner": "microsoft", "repo": "vscode"}
    )


@app.post("/api/v1/workflows/execute")
async def execute_workflow_template(request: WorkflowExecuteRequest):
    """
    🌟 Outstanding Feature 3: Execute pre-built workflow
    
    Directly execute preset templates, demonstrating Multi-MCP orchestration capability
    """
    try:
        template = get_template(request.template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{request.template_id}' not found"
            )
        
        # Execute workflow (simplified version)
        results = {
            "template_id": request.template_id,
            "template_name": template["name"],
            "status": "completed",
            "steps": []
        }
        
        # Execute each step
        for step in template["workflow_steps"][:2]:  # Demo first 2 steps
            mcp_id = step.get("mcp")
            action = step.get("action")
            
            if mcp_id and action:
                try:
                    # Build parameters
                    step_config = step.get("config", {})
                    step_config.update(request.config)
                    
                    # Call MCP
                    result = call_mcp(mcp_id, action, step_config)
                    
                    results["steps"].append({
                        "step": step["step"],
                        "mcp": mcp_id,
                        "action": action,
                        "status": "success",
                        "result": result.get("result")
                    })
                except Exception as e:
                    results["steps"].append({
                        "step": step["step"],
                        "mcp": mcp_id,
                        "action": action,
                        "status": "failed",
                        "error": str(e)
                    })
        
        return results
        
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
    print("🚀 MCPilot API Server")
    print("=" * 70)
    print(f"\n✓ Server starting...")
    print(f"✓ Groq API: {'Configured' if Config.GROQ_API_KEY else 'Mock Mode'}")
    print(f"✓ GitHub Token: {'Configured' if Config.GITHUB_TOKEN else 'Not set'}")
    print(f"✓ Brave API: {'Configured' if Config.BRAVE_API_KEY else 'Not set'}")
    print(f"\n📚 Documentation:")
    print(f"   - Swagger UI: http://localhost:8000/docs")
    print(f"   - ReDoc: http://localhost:8000/redoc")
    print(f"\n🔗 Core Endpoints:")
    print(f"   - Health: GET /health")
    print(f"   - Compose: POST /api/v1/compose")
    print(f"   - List MCPs: GET /api/v1/mcps")
    print(f"\n🌟 Outstanding Features:")
    print(f"   - Templates: GET /api/v1/templates")
    print(f"   - Cost Estimate: POST /api/v1/estimate-cost")
    print(f"   - Execute Workflow: POST /api/v1/workflows/execute")
    print(f"\n" + "=" * 70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

