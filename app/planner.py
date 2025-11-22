"""
Planner module: Convert natural language requirements to structured capability tags using Groq
"""
import json
import requests
from typing import Dict, List
from app.config import Config


def get_capabilities_from_description(description: str) -> Dict:
    """
    Analyze user requirements and extract structured capability tags.
    
    Args:
        description: Natural language description of the agent requirements
        
    Returns:
        dict: {
            "capabilities": List[str],  # Standardized capability tags
            "reasoning": str,            # Why these capabilities were chosen
            "confidence": float          # Confidence score (0-1)
        }
    """
    if Config.USE_MOCK_MODE:
        return _mock_capability_extraction(description)
    
    try:
        return _call_groq_for_capabilities(description)
    except Exception as e:
        print(f"⚠️  Groq API error: {e}. Falling back to mock mode.")
        return _mock_capability_extraction(description)


def _call_groq_for_capabilities(description: str) -> Dict:
    """
    Call Groq API to extract capabilities from description.
    """
    system_prompt = """You are an expert MCP (Model Context Protocol) capability analyzer.

Your task is to analyze a user's natural language description of an agent they want to build, 
and output a structured JSON response with standardized capability tags.

CAPABILITY TAXONOMY:
- code_hosting.* : GitHub operations (read_issues, read_repos, create_issue, manage_pr, search_code)
- web_search : General web search capabilities
- web_discovery : Web content discovery and exploration
- search.* : Specialized search (images, news, full_text, analytics)
- payment.* : Payment processing (create_invoice, list_subscriptions, process_payment, manage_customers)
- database.* : Database operations (read, write, query, aggregate, index_management)
- productivity.* : Productivity tools (notes, workspace, database)
- collaboration.* : Team collaboration (documents, messaging)
- browser.* : Browser automation (automation, screenshot)
- testing.* : Testing capabilities (e2e)
- monitoring.* : Monitoring and observability (metrics, alerts, logs)
- notify.* : Notification systems (slack, email, team_chat)
- research.* : Research capabilities (academic, synthesis)

OUTPUT FORMAT (valid JSON only):
{
  "capabilities": ["capability1", "capability2", ...],
  "reasoning": "Brief explanation of why these capabilities were selected",
  "confidence": 0.95
}

RULES:
1. Use ONLY the capability tags from the taxonomy above
2. Select 2-6 capabilities that best match the user's needs
3. Be specific: prefer "code_hosting.read_issues" over just "code_hosting"
4. Include related capabilities (e.g., if they need notifications, add notify.slack or notify.email)
5. Output ONLY valid JSON, no markdown or extra text"""

    user_prompt = f"""User wants to build an agent with this description:

"{description}"

Analyze this and output the JSON response with capabilities."""

    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": Config.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1
    }
    
    response = requests.post(
        f"{Config.GROQ_API_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    
    response_data = response.json()
    content = response_data["choices"][0]["message"]["content"]
    
    # Try to extract JSON from the content (might be wrapped in markdown)
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    result = json.loads(content)
    
    # Validate structure
    if "capabilities" not in result:
        raise ValueError("Invalid response from Groq: missing 'capabilities' field")
    
    return result


def _mock_capability_extraction(description: str) -> Dict:
    """
    Mock capability extraction based on keyword matching.
    Used as fallback when Groq API is not available.
    """
    description_lower = description.lower()
    capabilities = []
    reasoning_parts = []
    
    # Keyword-based matching
    keyword_map = {
        "github": ["code_hosting.read_issues", "code_hosting.read_repos"],
        "issue": ["code_hosting.read_issues", "code_hosting.create_issue"],
        "repository": ["code_hosting.read_repos"],
        "pull request": ["code_hosting.manage_pr"],
        "pr": ["code_hosting.manage_pr"],
        "search": ["web_search"],
        "web": ["web_search", "web_discovery"],
        "browse": ["web_search"],
        "payment": ["payment.process_payment", "payment.manage_customers"],
        "invoice": ["payment.create_invoice"],
        "subscription": ["payment.list_subscriptions"],
        "stripe": ["payment.process_payment"],
        "database": ["database.read", "database.write"],
        "mongodb": ["database.read", "database.write"],
        "query": ["database.query"],
        "notion": ["productivity.notes", "productivity.workspace"],
        "note": ["productivity.notes"],
        "document": ["collaboration.documents"],
        "elasticsearch": ["search.full_text", "database.query"],
        "browser": ["browser.automation"],
        "automate": ["browser.automation"],
        "test": ["testing.e2e"],
        "monitor": ["monitoring.metrics", "monitoring.alerts"],
        "alert": ["monitoring.alerts"],
        "metric": ["monitoring.metrics"],
        "slack": ["notify.slack", "notify.team_chat"],
        "notification": ["notify.slack"],
        "notify": ["notify.slack"],
        "email": ["notify.email"],
        "summary": ["research.synthesis"],
        "research": ["research.academic", "web_search"],
    }
    
    for keyword, caps in keyword_map.items():
        if keyword in description_lower:
            for cap in caps:
                if cap not in capabilities:
                    capabilities.append(cap)
                    reasoning_parts.append(f"'{keyword}' → {cap}")
    
    # Default fallback
    if not capabilities:
        capabilities = ["web_search", "collaboration.documents"]
        reasoning_parts = ["Default: general web search and documentation capabilities"]
    
    reasoning = "Mock analysis: " + "; ".join(reasoning_parts[:5])
    
    return {
        "capabilities": capabilities[:6],  # Limit to 6
        "reasoning": reasoning,
        "confidence": 0.75
    }


def format_capabilities_output(result: Dict) -> str:
    """
    Format capability analysis result for CLI output.
    """
    output = []
    output.append("\n🎯 Capability Analysis:")
    output.append(f"   Confidence: {result.get('confidence', 0):.0%}")
    output.append(f"\n   Identified Capabilities:")
    
    for cap in result.get("capabilities", []):
        output.append(f"   • {cap}")
    
    if result.get("reasoning"):
        output.append(f"\n   Reasoning: {result['reasoning']}")
    
    return "\n".join(output)

