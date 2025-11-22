"""
Snippet Generator: Generate environment configuration and code examples using Groq
"""
import json
import requests
from typing import List, Dict
from app.config import Config


def generate_snippet(description: str, mcps: List[Dict]) -> str:
    """
    Generate environment setup instructions and code snippets for selected MCPs.
    
    Args:
        description: Original user requirement description
        mcps: List of selected MCP info dicts
        
    Returns:
        str: Markdown-formatted snippet with setup and code
    """
    if Config.USE_MOCK_MODE or not Config.GROQ_API_KEY:
        return _mock_snippet_generation(description, mcps)
    
    try:
        return _call_groq_for_snippet(description, mcps)
    except Exception as e:
        print(f"⚠️  Groq API error: {e}. Falling back to mock mode.")
        return _mock_snippet_generation(description, mcps)


def _call_groq_for_snippet(description: str, mcps: List[Dict]) -> str:
    """
    Call Groq API to generate configuration and code snippet.
    """
    # Prepare MCP information
    mcps_text = []
    for m in mcps:
        mcps_text.append(f"""
MCP: {m.get('display_name', m['mcp_id'])}
- ID: {m['mcp_id']}
- Docker Image: {m.get('docker_image', 'N/A')}
- Description: {m.get('description', 'N/A')}
- Capabilities: {', '.join(m.get('capabilities', [])[:5])}
- Required Env Vars: {', '.join(m.get('env_vars', [])) or 'None'}
- Example Tools: {', '.join(m.get('example_tools', [])[:5])}
""")
    
    mcps_block = "\n".join(mcps_text[:5])  # Limit to top 5
    
    system_prompt = """You are an expert DevOps engineer and MCP integration specialist.

Your task is to generate clear, actionable documentation for setting up and using MCP servers.

OUTPUT FORMAT (Markdown):
Generate a well-structured markdown document with these sections:

## 🎯 Why These MCPs?
Brief explanation (2-3 sentences) of why each MCP was selected for this use case.

## 🔧 Environment Setup
List all required environment variables with:
- Variable name
- Purpose
- Where to obtain it (with URL if possible)

## 📦 Docker Setup
Show how to run each MCP server using Docker commands.

## 💻 Code Example
Provide a practical Python code example (15-30 lines) showing:
- How to call each MCP's main tool
- Error handling
- A simple workflow combining the MCPs

Use realistic function calls and show the orchestration pattern.

STYLE GUIDELINES:
- Be concise but complete
- Use code blocks with language tags
- Add helpful comments in code
- Focus on practical, copy-pasteable examples"""

    user_prompt = f"""User requirement:
"{description}"

Selected MCP servers:
{mcps_block}

Generate the setup and code documentation."""

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
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    response = requests.post(
        f"{Config.GROQ_API_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    
    content = response.json()["choices"][0]["message"]["content"]
    return content


def _mock_snippet_generation(description: str, mcps: List[Dict]) -> str:
    """
    Generate a mock snippet without calling Groq API.
    """
    if not mcps:
        return "No MCPs selected. Cannot generate snippet."
    
    # Build sections
    sections = []
    
    # Section 1: Why these MCPs?
    sections.append("## 🎯 Why These MCPs?\n")
    reasons = []
    for mcp in mcps[:3]:
        name = mcp.get('display_name', mcp['mcp_id'])
        caps = mcp.get('capabilities', [])
        if caps:
            reasons.append(f"**{name}** provides {caps[0]} capabilities, essential for your use case.")
    sections.append("\n".join(reasons) if reasons else "Selected MCPs match your requirements.")
    
    # Section 2: Environment Setup
    sections.append("\n\n## 🔧 Environment Setup\n")
    sections.append("Create a `.env` file with the following variables:\n")
    
    all_env_vars = set()
    env_docs = []
    for mcp in mcps:
        for var in mcp.get('env_vars', []):
            if var not in all_env_vars:
                all_env_vars.add(var)
                if 'GITHUB' in var:
                    env_docs.append(f"- `{var}`: GitHub Personal Access Token (get it from https://github.com/settings/tokens)")
                elif 'BRAVE' in var:
                    env_docs.append(f"- `{var}`: Brave Search API Key (register at https://brave.com/search/api/)")
                elif 'SLACK' in var:
                    env_docs.append(f"- `{var}`: Slack webhook URL or bot token (see https://api.slack.com/)")
                else:
                    env_docs.append(f"- `{var}`: API key for {mcp.get('display_name', '')}")
    
    sections.append("\n".join(env_docs) if env_docs else "No environment variables required.")
    
    # Section 3: Docker Setup
    sections.append("\n\n## 📦 Docker Setup\n")
    sections.append("Run the MCP servers using Docker:\n")
    
    docker_cmds = []
    for mcp in mcps[:3]:
        docker_image = mcp.get('docker_image', 'mcp/unknown')
        env_vars = mcp.get('env_vars', [])
        env_flags = " ".join([f"-e {var}=${var}" for var in env_vars[:2]])
        docker_cmds.append(f"```bash\n# {mcp.get('display_name')}\ndocker run -i --rm {env_flags} {docker_image}\n```")
    
    sections.append("\n\n".join(docker_cmds) if docker_cmds else "No Docker setup required.")
    
    # Section 4: Code Example
    sections.append("\n\n## 💻 Code Example\n")
    sections.append("Here's a Python example orchestrating the selected MCPs:\n")
    
    # Generate sample code
    code_lines = [
        "```python",
        "import os",
        "from mcp_client import call_mcp",
        "",
        "# Load environment variables",
        "from dotenv import load_dotenv",
        "load_dotenv()",
        ""
    ]
    
    # Add MCP-specific code
    if any('github' in mcp['mcp_id'] for mcp in mcps):
        code_lines.extend([
            "# Step 1: Fetch GitHub issues",
            "github_result = call_mcp(",
            "    mcp_id='github',",
            "    tool='list_issues',",
            "    args={'owner': 'your-org', 'repo': 'your-repo', 'state': 'open'}",
            ")",
            "issues = github_result.get('result', [])",
            "print(f'Found {len(issues)} open issues')",
            ""
        ])
    
    if any('search' in mcp['mcp_id'] or 'brave' in mcp['mcp_id'] for mcp in mcps):
        code_lines.extend([
            "# Step 2: Search the web for solutions",
            "for issue in issues[:3]:",
            "    search_result = call_mcp(",
            "        mcp_id='brave-search',",
            "        tool='search',",
            "        args={'query': f\"{issue['title']} solution\", 'num_results': 3}",
            "    )",
            "    print(f\"Issue #{issue['number']}: Found {len(search_result['result'])} results\")",
            ""
        ])
    
    if any('slack' in mcp['mcp_id'] or 'notify' in str(mcp.get('capabilities', [])) for mcp in mcps):
        code_lines.extend([
            "# Step 3: Post summary to Slack",
            "summary = f\"Daily summary: {len(issues)} issues reviewed\"",
            "slack_result = call_mcp(",
            "    mcp_id='slack',",
            "    tool='send_message',",
            "    args={'channel': '#dev', 'text': summary}",
            ")",
            "print('Summary posted to Slack!')",
        ])
    else:
        code_lines.extend([
            "# Process results",
            "print('Agent workflow completed successfully!')",
        ])
    
    code_lines.append("```")
    sections.append("\n".join(code_lines))
    
    return "\n".join(sections)


def format_snippet_output(snippet: str) -> str:
    """
    Format the generated snippet for CLI output.
    """
    return f"\n{'='*70}\n📝 Generated Setup & Code\n{'='*70}\n\n{snippet}\n"

