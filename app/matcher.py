"""
Matcher module: Match user capabilities to appropriate MCP servers
"""
import json
from typing import List, Dict
from pathlib import Path
from app.config import Config


def load_catalog(path: Path = None) -> Dict:
    """
    Load MCP catalog from JSON file.
    
    Args:
        path: Path to catalog file (defaults to Config.MCP_CATALOG_PATH)
        
    Returns:
        dict: MCP catalog with mcp_id as keys
    """
    if path is None:
        path = Config.MCP_CATALOG_PATH
    
    if not path.exists():
        raise FileNotFoundError(f"MCP catalog not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_mcp(capabilities: List[str], catalog: Dict = None, top_k: int = 5) -> List[Dict]:
    """
    Match capabilities to MCP servers using rule-based algorithm.
    
    Args:
        capabilities: List of capability tags (e.g., ["code_hosting.read_issues", "web_search"])
        catalog: MCP catalog dict (will load from file if not provided)
        top_k: Number of top matches to return
        
    Returns:
        List[dict]: Ranked list of MCP matches with scores
    """
    if catalog is None:
        catalog = load_catalog()
    
    results = []
    capabilities_set = set(capabilities)
    
    for mcp_id, info in catalog.items():
        mcp_caps = set(info.get("capabilities", []))
        
        # Calculate exact matches
        exact_matches = mcp_caps.intersection(capabilities_set)
        exact_score = len(exact_matches)
        
        # Calculate partial matches (e.g., "web_search" matches "web_discovery")
        partial_score = 0
        partial_matches = set()
        
        for cap in capabilities:
            cap_prefix = cap.split(".")[0] if "." in cap else cap
            for mcp_cap in mcp_caps:
                mcp_cap_prefix = mcp_cap.split(".")[0] if "." in mcp_cap else mcp_cap
                if cap_prefix == mcp_cap_prefix and mcp_cap not in exact_matches:
                    partial_matches.add(mcp_cap)
                    partial_score += 0.5
        
        # Total score: exact matches are worth 1.0, partial matches 0.5
        total_score = exact_score + partial_score
        
        if total_score > 0:
            results.append({
                "mcp_id": mcp_id,
                "score": total_score,
                "exact_matches": list(exact_matches),
                "partial_matches": list(partial_matches),
                **info  # Include all MCP info
            })
    
    # Sort by score (descending) and then by display name
    results.sort(key=lambda x: (-x["score"], x.get("display_name", "")))
    
    return results[:top_k]


def format_matches_output(matches: List[Dict]) -> str:
    """
    Format MCP matches for CLI output.
    """
    if not matches:
        return "\n❌ No matching MCPs found for the specified capabilities."
    
    output = []
    output.append("\n🔧 Recommended MCP Servers:")
    output.append("")
    
    for i, match in enumerate(matches, 1):
        score = match["score"]
        display_name = match.get("display_name", match["mcp_id"])
        description = match.get("description", "No description available")
        exact = match.get("exact_matches", [])
        partial = match.get("partial_matches", [])
        
        output.append(f"{i}. {display_name} (Score: {score:.1f})")
        output.append(f"   {description[:100]}{'...' if len(description) > 100 else ''}")
        
        if exact:
            output.append(f"   ✓ Exact matches: {', '.join(exact[:3])}")
        if partial:
            output.append(f"   ~ Partial matches: {', '.join(partial[:2])}")
        
        output.append("")
    
    return "\n".join(output)


def get_mcp_summary(matches: List[Dict]) -> Dict:
    """
    Generate a summary of selected MCPs for code generation.
    
    Returns:
        dict: Summary with env_vars, tools, and descriptions
    """
    if not matches:
        return {
            "mcp_count": 0,
            "total_env_vars": [],
            "mcp_list": []
        }
    
    all_env_vars = []
    mcp_list = []
    
    for match in matches:
        env_vars = match.get("env_vars", [])
        all_env_vars.extend(env_vars)
        
        mcp_list.append({
            "mcp_id": match["mcp_id"],
            "display_name": match.get("display_name", ""),
            "description": match.get("description", ""),
            "env_vars": env_vars,
            "example_tools": match.get("example_tools", []),
            "docker_image": match.get("docker_image", ""),
            "capabilities": match.get("exact_matches", []) + match.get("partial_matches", [])
        })
    
    # Remove duplicates while preserving order
    unique_env_vars = []
    for var in all_env_vars:
        if var not in unique_env_vars:
            unique_env_vars.append(var)
    
    return {
        "mcp_count": len(matches),
        "total_env_vars": unique_env_vars,
        "mcp_list": mcp_list
    }

