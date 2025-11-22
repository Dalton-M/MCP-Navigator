"""
MCP Client: Handles calling MCP servers (both mock and real)
"""
import json
import subprocess
import requests
from typing import Dict, Any
from pathlib import Path
from app.config import Config


def call_mcp(mcp_id: str, tool: str, args: Dict[str, Any] = None, use_mock: bool = None) -> Dict:
    """
    Call an MCP server tool.
    
    Args:
        mcp_id: MCP identifier (e.g., 'github', 'brave-search')
        tool: Tool/function name to call (e.g., 'list_issues', 'search')
        args: Arguments to pass to the tool
        use_mock: Force mock mode (default: auto-detect based on available keys)
        
    Returns:
        dict: Result from MCP call
    """
    if args is None:
        args = {}
    
    # Determine if we should use mock mode
    if use_mock is None:
        use_mock = _should_use_mock(mcp_id)
    
    if use_mock:
        return mock_mcp_call(mcp_id, tool, args)
    
    # Try real MCP call
    try:
        return call_mcp_docker(mcp_id, tool, args)
    except Exception as e:
        print(f"⚠️  Real MCP call failed: {e}. Falling back to mock.")
        return mock_mcp_call(mcp_id, tool, args)


def _should_use_mock(mcp_id: str) -> bool:
    """
    Determine if we should use mock mode for this MCP.
    """
    # Check if required API keys are available
    if mcp_id == 'github':
        return not bool(Config.GITHUB_TOKEN)
    elif mcp_id in ['brave-search', 'brave']:
        return not bool(Config.BRAVE_API_KEY)
    
    # Default to mock if we don't have a way to call it
    return True


def call_mcp_docker(mcp_id: str, tool: str, args: Dict[str, Any]) -> Dict:
    """
    Call MCP server running in Docker via stdio JSON-RPC protocol.
    
    This is the "real" MCP integration that communicates with Docker MCP Hub.
    """
    # Load catalog to get docker image
    catalog_path = Config.MCP_CATALOG_PATH
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    if mcp_id not in catalog:
        raise ValueError(f"Unknown MCP: {mcp_id}")
    
    mcp_info = catalog[mcp_id]
    docker_image = mcp_info.get('docker_image', f'mcp/{mcp_id}')
    
    # Prepare environment variables
    env_vars = {}
    for var in mcp_info.get('env_vars', []):
        value = getattr(Config, var, None) or os.getenv(var)
        if value:
            env_vars[var] = value
    
    # Build docker run command
    docker_cmd = ['docker', 'run', '-i', '--rm']
    for k, v in env_vars.items():
        docker_cmd.extend(['-e', f'{k}={v}'])
    docker_cmd.append(docker_image)
    
    # Prepare JSON-RPC request
    json_rpc_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": f"tools/{tool}",
        "params": args
    }
    
    # Execute docker command
    try:
        result = subprocess.run(
            docker_cmd,
            input=json.dumps(json_rpc_request).encode(),
            capture_output=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Docker command failed: {result.stderr.decode()}")
        
        # Parse response
        stdout = result.stdout.decode().strip()
        if not stdout:
            raise RuntimeError("Empty response from MCP server")
        
        response = json.loads(stdout)
        
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")
        
        return {
            "mcp_id": mcp_id,
            "tool": tool,
            "success": True,
            "result": response.get("result")
        }
        
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"MCP call timed out after 30 seconds")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse MCP response: {e}")


def call_github_mcp(tool: str, args: Dict[str, Any]) -> Dict:
    """
    Specialized function to call GitHub MCP directly via GitHub API.
    This is a fallback when Docker MCP is not available.
    """
    if not Config.GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not configured")
    
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    if tool == "list_issues":
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        state = args.get("state", "open")
        per_page = args.get("per_page", 10)
        
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": per_page}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        issues = response.json()
        
        return {
            "mcp_id": "github",
            "tool": tool,
            "success": True,
            "result": [
                {
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "url": issue["html_url"],
                    "created_at": issue["created_at"],
                    "labels": [label["name"] for label in issue.get("labels", [])],
                    "comments": issue.get("comments", 0)
                }
                for issue in issues
            ]
        }
    
    else:
        raise ValueError(f"Unsupported GitHub tool: {tool}")


def mock_mcp_call(mcp_id: str, tool: str, args: Dict[str, Any] = None) -> Dict:
    """
    Return mock data for MCP calls.
    Loads from test_data directory if available, otherwise returns generic mock.
    """
    if args is None:
        args = {}
    
    # Try to load from test data files
    test_data_dir = Config.TEST_DATA_DIR
    mock_file = test_data_dir / f"{mcp_id.replace('-', '_')}_{tool}_mock.json"
    
    # Also try without tool name
    if not mock_file.exists():
        mock_file = test_data_dir / f"{mcp_id.replace('-', '_')}_mock.json"
    
    if mock_file.exists():
        with open(mock_file, 'r') as f:
            return json.load(f)
    
    # Generic mock responses
    if mcp_id == 'github' and tool == 'list_issues':
        return {
            "mcp_id": "github",
            "tool": "list_issues",
            "success": True,
            "result": [
                {
                    "number": 42,
                    "title": "Example issue: Feature request",
                    "state": "open",
                    "url": "https://github.com/example/repo/issues/42",
                    "labels": ["enhancement"],
                    "comments": 5
                }
            ]
        }
    
    elif mcp_id in ['brave-search', 'brave'] and tool == 'search':
        query = args.get('query', 'example query')
        return {
            "mcp_id": mcp_id,
            "tool": "search",
            "success": True,
            "result": {
                "query": query,
                "web": {
                    "results": [
                        {
                            "title": f"Search result for: {query}",
                            "url": "https://example.com/result1",
                            "description": "This is a mock search result for demonstration purposes."
                        }
                    ]
                }
            }
        }
    
    else:
        # Generic mock for any other MCP/tool combination
        return {
            "mcp_id": mcp_id,
            "tool": tool,
            "success": True,
            "result": f"Mock result for {mcp_id}.{tool} with args: {args}"
        }


def format_mcp_result(result: Dict) -> str:
    """
    Format MCP call result for CLI output.
    """
    output = []
    output.append(f"\n{'='*70}")
    output.append(f"🔌 MCP Call Result: {result.get('mcp_id', 'unknown')}.{result.get('tool', 'unknown')}")
    output.append(f"{'='*70}\n")
    
    if not result.get('success', False):
        output.append("❌ Call failed")
        return "\n".join(output)
    
    # Format based on MCP type
    mcp_id = result.get('mcp_id', '')
    tool = result.get('tool', '')
    result_data = result.get('result', {})
    
    if mcp_id == 'github' and tool == 'list_issues':
        issues = result_data if isinstance(result_data, list) else []
        output.append(f"Found {len(issues)} issue(s):\n")
        for issue in issues[:5]:  # Show first 5
            output.append(f"  #{issue.get('number')}: {issue.get('title')}")
            output.append(f"  State: {issue.get('state')} | Comments: {issue.get('comments', 0)}")
            labels = issue.get('labels', [])
            if labels:
                output.append(f"  Labels: {', '.join(labels)}")
            output.append(f"  URL: {issue.get('url')}\n")
    
    elif 'search' in tool or 'brave' in mcp_id:
        if isinstance(result_data, dict):
            results = result_data.get('web', {}).get('results', [])
            output.append(f"Found {len(results)} search result(s):\n")
            for i, res in enumerate(results[:5], 1):
                output.append(f"  {i}. {res.get('title')}")
                output.append(f"     {res.get('description', '')[:100]}")
                output.append(f"     {res.get('url')}\n")
        else:
            output.append(str(result_data))
    
    else:
        # Generic formatting
        result_str = json.dumps(result_data, indent=2)
        if len(result_str) > 500:
            result_str = result_str[:500] + "\n... (truncated)"
        output.append(result_str)
    
    return "\n".join(output)


# Import os for environment variables in call_mcp_docker
import os

