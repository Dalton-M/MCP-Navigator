#!/usr/bin/env python3
"""
Multi-MCP 工作流执行器
展示真正的 MCP 编排能力 - 多个 MCP 协同工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp_client import call_mcp
from app.config import Config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import time

console = Console()

def multi_mcp_workflow_demo():
    """
    完整的 Multi-MCP 工作流演示
    
    工作流：
    1. GitHub MCP: 获取 issues
    2. Brave Search MCP: 为每个 issue 搜索解决方案
    3. 智能分析: 生成报告和建议
    
    这展示了真正的 MCP 编排能力！
    """
    
    console.print(Panel(
        "[bold cyan]🚀 Multi-MCP 智能工作流[/bold cyan]\n"
        "展示多个 MCP 协同工作，自动化完整流程",
        title="Outstanding Feature Demo",
        border_style="cyan"
    ))
    print()
    
    # 工作流统计
    workflow_stats = {
        "total_time": 0,
        "api_calls": 0,
        "estimated_cost": 0.0,
        "mcps_used": []
    }
    
    results = {}
    
    # ========== Step 1: GitHub MCP ==========
    console.print("[bold]📋 Step 1/3: GitHub MCP - 获取 Issues[/bold]")
    console.print("[dim]调用: github.list_issues[/dim]\n")
    
    start_time = time.time()
    
    try:
        github_result = call_mcp('github', 'list_issues', {
            'owner': 'microsoft',
            'repo': 'vscode',
            'state': 'open',
            'per_page': 5
        })
        
        issues = github_result.get('result', [])
        step1_time = time.time() - start_time
        
        workflow_stats['total_time'] += step1_time
        workflow_stats['api_calls'] += 1
        workflow_stats['estimated_cost'] += 0.0  # GitHub free
        workflow_stats['mcps_used'].append('GitHub')
        
        console.print(f"[green]✓ 成功获取 {len(issues)} 个 issues[/green]")
        console.print(f"[dim]耗时: {step1_time:.2f}s | 成本: $0.00[/dim]\n")
        
        # 展示 issues 表格
        if issues:
            table = Table(title="获取的 Issues", show_header=True, header_style="bold cyan")
            table.add_column("#", style="dim", width=8)
            table.add_column("标题", width=50)
            table.add_column("评论", justify="right", width=6)
            
            for issue in issues[:5]:
                table.add_row(
                    f"#{issue.get('number')}",
                    (issue.get('title', '')[:47] + "...") if len(issue.get('title', '')) > 50 else issue.get('title', ''),
                    str(issue.get('comments', 0))
                )
            
            console.print(table)
            print()
        
        results['github'] = issues
        
    except Exception as e:
        console.print(f"[red]✗ GitHub 调用失败: {e}[/red]\n")
        results['github'] = []
    
    # ========== Step 2: Brave Search MCP ==========
    console.print("[bold]🔍 Step 2/3: Brave Search MCP - 搜索解决方案[/bold]")
    console.print("[dim]为每个 issue 搜索相关解决方案[/dim]\n")
    
    search_results = []
    
    if results.get('github') and len(results['github']) > 0:
        # 为前 3 个 issues 搜索
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            transient=True
        ) as progress:
            
            task = progress.add_task("搜索中...", total=min(3, len(results['github'])))
            
            for i, issue in enumerate(results['github'][:3]):
                issue_title = issue.get('title', '')
                
                try:
                    start_time = time.time()
                    
                    search_result = call_mcp('brave-search', 'search', {
                        'query': f"{issue_title} solution",
                        'num_results': 3
                    })
                    
                    step2_time = time.time() - start_time
                    workflow_stats['total_time'] += step2_time
                    workflow_stats['api_calls'] += 1
                    workflow_stats['estimated_cost'] += 0.005  # Brave ~$0.005 per query
                    
                    if 'Brave Search' not in workflow_stats['mcps_used']:
                        workflow_stats['mcps_used'].append('Brave Search')
                    
                    search_data = search_result.get('result', {}).get('web', {}).get('results', [])
                    
                    search_results.append({
                        'issue_number': issue.get('number'),
                        'issue_title': issue_title,
                        'solutions': search_data
                    })
                    
                    console.print(f"[green]✓ Issue #{issue.get('number')}: 找到 {len(search_data)} 个解决方案[/green]")
                    
                except Exception as e:
                    console.print(f"[yellow]⚠  Issue #{issue.get('number')}: 搜索失败 ({e})[/yellow]")
                
                progress.update(task, advance=1)
        
        print()
        results['search'] = search_results
        
        # 展示搜索结果
        if search_results:
            console.print("[bold cyan]搜索结果示例:[/bold cyan]")
            first_result = search_results[0]
            console.print(f"\n[bold]Issue #{first_result['issue_number']}:[/bold] {first_result['issue_title'][:60]}...")
            
            for i, solution in enumerate(first_result['solutions'][:2], 1):
                console.print(f"\n  {i}. [cyan]{solution.get('title', 'N/A')}[/cyan]")
                console.print(f"     {solution.get('url', 'N/A')}")
                desc = solution.get('description', 'N/A')
                console.print(f"     [dim]{desc[:100]}...[/dim]" if len(desc) > 100 else f"     [dim]{desc}[/dim]")
            print()
    else:
        console.print("[yellow]⚠  跳过搜索（GitHub 数据不可用）[/yellow]\n")
    
    # ========== Step 3: 智能分析和报告生成 ==========
    console.print("[bold]📊 Step 3/3: 智能分析 - 生成报告[/bold]")
    console.print("[dim]基于 GitHub + Brave Search 数据生成洞察[/dim]\n")
    
    start_time = time.time()
    
    # 生成分析报告
    report = generate_intelligent_report(results)
    
    step3_time = time.time() - start_time
    workflow_stats['total_time'] += step3_time
    
    console.print(Panel(
        report,
        title="📋 智能分析报告",
        border_style="green"
    ))
    print()
    
    # ========== 工作流统计 ==========
    console.print("[bold yellow]📈 工作流执行统计[/bold yellow]\n")
    
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("指标", style="cyan")
    stats_table.add_column("数值", style="bold")
    
    stats_table.add_row("⏱️  总执行时间", f"{workflow_stats['total_time']:.2f} 秒")
    stats_table.add_row("🔌 MCP 使用", " → ".join(workflow_stats['mcps_used']))
    stats_table.add_row("📞 API 调用次数", str(workflow_stats['api_calls']))
    stats_table.add_row("💰 预估成本", f"${workflow_stats['estimated_cost']:.4f}")
    stats_table.add_row("📦 处理的 Issues", str(len(results.get('github', []))))
    stats_table.add_row("🔍 搜索查询", str(len(results.get('search', []))))
    
    console.print(stats_table)
    print()
    
    # ========== 价值展示 ==========
    console.print(Panel(
        "[bold green]💡 Multi-MCP 编排的价值[/bold green]\n\n"
        "✅ [bold]自动化完整工作流[/bold]\n"
        "   传统方式需要 30 分钟手动操作，现在只需 {:.1f} 秒\n\n"
        "✅ [bold]多个 MCP 无缝协同[/bold]\n"
        "   GitHub → Brave Search → 智能分析，端到端自动化\n\n"
        "✅ [bold]实时执行和反馈[/bold]\n"
        "   不只是推荐，而是真正运行并展示结果\n\n"
        "✅ [bold]成本透明可控[/bold]\n"
        "   每次执行成本: ${:.4f}，完全可预测".format(
            workflow_stats['total_time'],
            workflow_stats['estimated_cost']
        ),
        border_style="green",
        title="🌟 Outstanding Feature"
    ))


def generate_intelligent_report(results):
    """
    基于 GitHub 和 Search 结果生成智能报告
    """
    github_data = results.get('github', [])
    search_data = results.get('search', [])
    
    if not github_data:
        return "⚠️  无法生成报告：缺少 GitHub 数据"
    
    # 分析 issues
    total_issues = len(github_data)
    with_comments = sum(1 for issue in github_data if issue.get('comments', 0) > 0)
    no_comments = total_issues - with_comments
    
    # 分类
    urgent_keywords = ['crash', 'critical', 'urgent', 'blocker']
    urgent_count = sum(1 for issue in github_data 
                      if any(kw in issue.get('title', '').lower() for kw in urgent_keywords))
    
    report_lines = []
    report_lines.append("[bold]📊 GitHub Issues 分析[/bold]")
    report_lines.append("─" * 50)
    report_lines.append(f"• 总计: [bold]{total_issues}[/bold] 个 open issues")
    report_lines.append(f"• 有评论: {with_comments} 个")
    report_lines.append(f"• 待回复: {no_comments} 个")
    report_lines.append(f"• 紧急: [red]{urgent_count}[/red] 个")
    report_lines.append("")
    
    if search_data:
        report_lines.append("[bold]🔍 解决方案搜索结果[/bold]")
        report_lines.append("─" * 50)
        report_lines.append(f"• 搜索查询: {len(search_data)} 次")
        total_solutions = sum(len(s.get('solutions', [])) for s in search_data)
        report_lines.append(f"• 找到解决方案: {total_solutions} 个")
        report_lines.append("")
    
    report_lines.append("[bold]💡 智能建议[/bold]")
    report_lines.append("─" * 50)
    
    if urgent_count > 0:
        report_lines.append(f"🔴 有 {urgent_count} 个紧急 issue 需要立即处理")
    
    if no_comments > 0:
        report_lines.append(f"🟡 有 {no_comments} 个 issue 尚未回复，建议优先回复")
    
    if search_data:
        report_lines.append(f"🟢 已为 {len(search_data)} 个 issue 找到潜在解决方案")
    
    return "\n".join(report_lines)


if __name__ == "__main__":
    if not Config.GITHUB_TOKEN:
        console.print("[yellow]⚠️  未检测到 GITHUB_TOKEN，将使用模拟数据[/yellow]")
        console.print("[dim]设置方法: export GITHUB_TOKEN='your_token'[/dim]\n")
    
    if not Config.BRAVE_API_KEY:
        console.print("[yellow]⚠️  未检测到 BRAVE_API_KEY，搜索将使用模拟数据[/yellow]")
        console.print("[dim]设置方法: export BRAVE_API_KEY='your_key'[/dim]\n")
    
    try:
        multi_mcp_workflow_demo()
        
        console.print("\n[bold green]✨ Multi-MCP 工作流演示完成！[/bold green]")
        console.print("[dim]这展示了真正的 MCP 编排能力 - 不只是推荐，而是真正执行！[/dim]\n")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]演示已中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        import traceback
        traceback.print_exc()

