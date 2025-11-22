"""
MCP Stack Composer - Main CLI Entry Point

Orchestrates the entire workflow:
1. Accept user requirements
2. Extract capabilities (via Groq)
3. Match MCP servers
4. Generate setup code (via Groq)
5. Demo a real MCP call
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint

from app.config import Config
from app.planner import get_capabilities_from_description, format_capabilities_output
from app.matcher import load_catalog, match_mcp, format_matches_output
from app.snippet_generator import generate_snippet, format_snippet_output
from app.mcp_client import call_mcp, format_mcp_result


console = Console()


def print_banner():
    """Display welcome banner"""
    banner = """
[bold cyan]╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🚀 MCP Stack Composer                                ║
║                                                                   ║
║    Intelligent MCP orchestrator powered by Groq + Docker Hub     ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)
    
    if Config.USE_MOCK_MODE:
        console.print("[yellow]⚠️  Running in MOCK MODE (set GROQ_API_KEY for full experience)[/yellow]\n")
    else:
        console.print("[green]✓ Groq API connected[/green]\n")


def get_user_input() -> str:
    """
    Get agent requirements from user.
    """
    console.print("[bold]Describe the agent you want to build:[/bold]")
    console.print("[dim]Example: \"I want an agent that reads GitHub issues, searches the web[/dim]")
    console.print("[dim]         for similar solutions, and posts a daily summary to Slack.\"[/dim]\n")
    
    description = Prompt.ask("[cyan]Your agent description[/cyan]")
    
    if not description.strip():
        console.print("[red]Error: Description cannot be empty[/red]")
        sys.exit(1)
    
    return description


def run_demo_mcp_call(matched_mcps: list) -> dict:
    """
    Run a demo MCP call to show live integration.
    Choose the best MCP from matches.
    """
    if not matched_mcps:
        return None
    
    # Try to find GitHub or Brave Search MCP for demo
    demo_mcp = None
    demo_tool = None
    demo_args = {}
    
    for mcp in matched_mcps:
        mcp_id = mcp['mcp_id']
        
        if mcp_id == 'github':
            demo_mcp = 'github'
            demo_tool = 'list_issues'
            demo_args = {
                'owner': 'microsoft',
                'repo': 'vscode',
                'state': 'open',
                'per_page': 3
            }
            break
        elif mcp_id in ['brave-search', 'brave']:
            demo_mcp = mcp_id
            demo_tool = 'search'
            demo_args = {
                'query': 'AI agent automation best practices',
                'num_results': 3
            }
            break
    
    # Fallback to first MCP
    if not demo_mcp and matched_mcps:
        first_mcp = matched_mcps[0]
        demo_mcp = first_mcp['mcp_id']
        tools = first_mcp.get('example_tools', [])
        demo_tool = tools[0] if tools else 'search'
        demo_args = {}
    
    if demo_mcp and demo_tool:
        console.print(f"\n[bold cyan]🎬 Live Demo: Calling {demo_mcp}.{demo_tool}...[/bold cyan]")
        try:
            result = call_mcp(demo_mcp, demo_tool, demo_args)
            return result
        except Exception as e:
            console.print(f"[red]Demo call failed: {e}[/red]")
            return None
    
    return None


def main():
    """
    Main CLI workflow
    """
    try:
        # Validate configuration
        Config.validate()
        
        # Step 0: Welcome
        print_banner()
        
        # Step 1: Get user input
        description = get_user_input()
        
        console.print("\n[bold]Processing your request...[/bold]\n")
        
        # Step 2: Extract capabilities using Groq
        console.print("[cyan]Step 1/4:[/cyan] Analyzing requirements with Groq...")
        capabilities_result = get_capabilities_from_description(description)
        console.print(format_capabilities_output(capabilities_result))
        
        capabilities = capabilities_result.get("capabilities", [])
        
        if not capabilities:
            console.print("[red]No capabilities extracted. Please try a different description.[/red]")
            sys.exit(1)
        
        # Step 3: Match MCP servers
        console.print("\n[cyan]Step 2/4:[/cyan] Matching MCP servers from Docker Hub...")
        catalog = load_catalog()
        matched_mcps = match_mcp(capabilities, catalog, top_k=5)
        console.print(format_matches_output(matched_mcps))
        
        if not matched_mcps:
            console.print("[yellow]No matching MCPs found. Try different requirements.[/yellow]")
            sys.exit(0)
        
        # Step 4: Generate setup instructions and code
        console.print("[cyan]Step 3/4:[/cyan] Generating setup instructions and code with Groq...")
        snippet = generate_snippet(description, matched_mcps[:3])
        console.print(format_snippet_output(snippet))
        
        # Step 5: Run a live demo MCP call
        console.print("[cyan]Step 4/4:[/cyan] Running live MCP demo...")
        demo_result = run_demo_mcp_call(matched_mcps)
        
        if demo_result:
            console.print(format_mcp_result(demo_result))
        else:
            console.print("[yellow]No demo call executed.[/yellow]")
        
        # Final summary
        console.print("\n" + "="*70)
        console.print("[bold green]✨ MCP Stack Composer Complete![/bold green]")
        console.print("="*70 + "\n")
        
        console.print("[bold]What's Next?[/bold]")
        console.print("1. Copy the environment variables to your .env file")
        console.print("2. Install and configure the recommended MCP servers")
        console.print("3. Use the generated code as a starting point")
        console.print("4. Deploy to E2B for cloud execution\n")
        
        console.print("[dim]💡 Tip: Set GROQ_API_KEY in .env for real-time LLM analysis[/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        if Config.USE_MOCK_MODE:
            console.print("\n[dim]Full traceback:[/dim]")
            console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

