"""
Mermaid diagram generator for workflow visualization
"""

def generate_workflow_diagram(mcps, workflow_execution=None):
    """
    Generate Mermaid flowchart for MCP workflow
    
    Args:
        mcps: List of MCP recommendations
        workflow_execution: Optional execution results
    
    Returns:
        str: Mermaid diagram code
    """
    mcp_ids = [m.get('mcp_id') for m in mcps[:3]]
    
    # Build mermaid code
    lines = ["graph TD"]
    lines.append("    A[User Input] --> B[Groq LLM Analysis]")
    lines.append("    B --> C{MCP Matching}")
    
    # Add MCP nodes
    for idx, mcp_id in enumerate(mcp_ids):
        node_id = chr(68 + idx)  # D, E, F, ...
        mcp_name = mcp_id.replace('-', ' ').title()
        lines.append(f"    C --> {node_id}[{mcp_name} MCP]")
    
    # Add aggregation
    agg_node = chr(68 + len(mcp_ids))
    lines.append(f"    {' --> '.join([chr(68 + i) for i in range(len(mcp_ids))])} --> {agg_node}[Data Aggregation]")
    
    # Add final steps
    next_node = chr(68 + len(mcp_ids) + 1)
    lines.append(f"    {agg_node} --> {next_node}[Groq Code Generation]")
    
    last_node = chr(68 + len(mcp_ids) + 2)
    lines.append(f"    {next_node} --> {last_node}[Complete Response]")
    
    # Add styling
    lines.append("")
    lines.append("    style A fill:#e1f5ff,stroke:#0288d1")
    lines.append("    style B fill:#fff3cd,stroke:#ffc107")
    lines.append("    style C fill:#f3e5f5,stroke:#9c27b0")
    
    for idx in range(len(mcp_ids)):
        node_id = chr(68 + idx)
        lines.append(f"    style {node_id} fill:#c8e6c9,stroke:#4caf50")
    
    lines.append(f"    style {agg_node} fill:#bbdefb,stroke:#2196f3")
    lines.append(f"    style {next_node} fill:#fff3cd,stroke:#ffc107")
    lines.append(f"    style {last_node} fill:#c8e6c9,stroke:#4caf50")
    
    return "\n".join(lines)


def generate_execution_diagram(workflow_execution):
    """
    Generate Mermaid sequence diagram for execution flow
    
    Args:
        workflow_execution: Execution results with timing
    
    Returns:
        str: Mermaid sequence diagram code
    """
    if not workflow_execution or not workflow_execution.get('results'):
        return None
    
    results = workflow_execution['results']
    
    lines = ["sequenceDiagram"]
    lines.append("    participant User")
    lines.append("    participant API")
    lines.append("    participant Groq")
    
    if 'github' in results:
        lines.append("    participant GitHub")
    
    if 'brave-search' in results:
        lines.append("    participant Brave")
    
    lines.append("    participant Analysis")
    lines.append("")
    lines.append("    User->>API: POST /api/v1/compose")
    lines.append("    API->>Groq: Analyze requirements")
    lines.append("    Groq-->>API: Capabilities")
    lines.append("    API->>API: Match MCPs")
    lines.append("    API->>Groq: Generate code")
    lines.append("    Groq-->>API: Setup code")
    
    if 'github' in results:
        lines.append("    API->>GitHub: Get issues")
        if results['github'].get('success'):
            count = len(results['github'].get('result', []))
            lines.append(f"    GitHub-->>API: {count} issues")
    
    if 'brave-search' in results:
        lines.append("    API->>Brave: Search solutions")
        if results['brave-search'].get('success'):
            count = results['brave-search'].get('total_searches', 0)
            lines.append(f"    Brave-->>API: {count} results")
    
    lines.append("    API->>Analysis: Generate insights")
    lines.append("    Analysis-->>API: Report")
    lines.append("    API-->>User: Complete response")
    
    return "\n".join(lines)


def generate_cost_breakdown_diagram(cost_estimate):
    """
    Generate Mermaid pie chart for cost breakdown
    
    Args:
        cost_estimate: Cost estimate data
    
    Returns:
        str: Mermaid pie chart code
    """
    if not cost_estimate or not cost_estimate.get('breakdown'):
        return None
    
    breakdown = cost_estimate['breakdown']
    
    lines = ["pie title Cost Breakdown"]
    
    for service, info in breakdown.items():
        cost = info.get('cost', 0)
        if cost > 0:
            # Convert to percentage or absolute value
            lines.append(f'    "{service.title()}" : {cost * 1000:.2f}')
    
    # If all costs are 0, show placeholder
    if len(lines) == 1:
        lines.append('    "Free Services" : 100')
    
    return "\n".join(lines)

