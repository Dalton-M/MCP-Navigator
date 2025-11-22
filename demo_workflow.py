#!/usr/bin/env python3
"""
展示真实的 Agent 工作流价值
演示：智能 GitHub Issue 管理助手
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp_client import call_github_mcp, call_mcp
from app.config import Config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def demo_intelligent_issue_manager():
    """
    演示场景：每天早上 9:00，Agent 自动运行：
    1. 获取昨天新增的 issues
    2. 分析并分类
    3. 搜索解决方案
    4. 生成每日报告
    """
    
    console.print(Panel(
        "[bold cyan]🤖 智能 Issue 管理 Agent[/bold cyan]\n"
        "场景：开发团队每天早上收到自动生成的 Issue 分析报告",
        title="Demo Workflow",
        border_style="cyan"
    ))
    print()
    
    # Step 1: 获取最新 issues
    console.print("[bold]Step 1:[/bold] 获取 GitHub issues")
    console.print("→ 调用 GitHub MCP: list_issues(state='open', per_page=5)")
    print()
    
    try:
        result = call_github_mcp('list_issues', {
            'owner': 'microsoft',
            'repo': 'vscode',
            'state': 'open',
            'per_page': 5
        })
        
        issues = result['result']
        console.print(f"[green]✓[/green] 成功获取 {len(issues)} 个 issues\n")
        
        # 创建表格展示
        table = Table(title="今日新 Issues", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=8)
        table.add_column("标题", width=50)
        table.add_column("评论", justify="right", width=8)
        table.add_column("标签", width=20)
        
        for issue in issues:
            table.add_row(
                f"#{issue['number']}",
                issue['title'][:47] + "..." if len(issue['title']) > 50 else issue['title'],
                str(issue['comments']),
                ", ".join(issue.get('labels', [])[:2])
            )
        
        console.print(table)
        print()
        
        # Step 2: 智能分析
        console.print("[bold]Step 2:[/bold] AI 分析和分类")
        print()
        
        # 模拟分析结果
        analysis = {
            'urgent': [],
            'needs_response': [],
            'can_auto_close': []
        }
        
        for issue in issues:
            title_lower = issue['title'].lower()
            if 'crash' in title_lower or 'critical' in title_lower:
                analysis['urgent'].append(issue)
            elif issue['comments'] == 0:
                analysis['needs_response'].append(issue)
        
        console.print(f"[red]🔴 紧急 issues:[/red] {len(analysis['urgent'])} 个")
        for issue in analysis['urgent']:
            console.print(f"   #{issue['number']}: {issue['title'][:60]}")
        print()
        
        console.print(f"[yellow]🟡 待回复 issues:[/yellow] {len(analysis['needs_response'])} 个")
        for issue in analysis['needs_response'][:3]:
            console.print(f"   #{issue['number']}: {issue['title'][:60]}")
        print()
        
        # Step 3: 搜索解决方案（演示第一个紧急 issue）
        if analysis['urgent']:
            urgent_issue = analysis['urgent'][0]
            console.print(f"[bold]Step 3:[/bold] 为紧急 issue 搜索解决方案")
            console.print(f"→ 分析: #{urgent_issue['number']} - {urgent_issue['title'][:50]}...")
            print()
            
            # 真实搜索（如果有 Brave API key）
            if Config.BRAVE_API_KEY:
                console.print("[cyan]→ 调用 Brave Search MCP...[/cyan]")
                try:
                    search_result = call_mcp('brave-search', 'search', {
                        'query': f"{urgent_issue['title']} solution",
                        'num_results': 3
                    })
                    
                    if search_result.get('success'):
                        results = search_result.get('result', {}).get('web', {}).get('results', [])
                        console.print(f"[green]✓[/green] 找到 {len(results)} 个解决方案:\n")
                        
                        for i, result in enumerate(results[:3], 1):
                            console.print(f"   {i}. {result['title']}")
                            console.print(f"      {result['url']}")
                            console.print(f"      {result['description'][:80]}...\n")
                    else:
                        console.print("[yellow]⚠️  搜索未返回结果[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]⚠️  搜索失败: {e}[/yellow]")
            else:
                console.print("[dim]→ (模拟) 搜索 Stack Overflow, GitHub discussions...[/dim]")
                console.print("[dim]   找到 3 个相关解决方案[/dim]")
            print()
        
        # Step 4: 生成每日报告
        console.print("[bold]Step 4:[/bold] 生成每日报告")
        print()
        
        report = f"""
📊 **GitHub Issues 每日报告**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 总览
  • 待处理 issues: {len(issues)} 个
  • 🔴 紧急: {len(analysis['urgent'])} 个
  • 🟡 待回复: {len(analysis['needs_response'])} 个

🔥 需要立即关注
  {f"• #{analysis['urgent'][0]['number']}: {analysis['urgent'][0]['title']}" if analysis['urgent'] else "  无"}

💡 建议行动
  1. 优先处理紧急 crash 问题
  2. 回复昨天无人回复的 issues
  3. 检查重复 issues 并合并

🤖 本报告由 MCP Stack Composer 自动生成
"""
        
        console.print(Panel(report, title="每日报告预览", border_style="green"))
        print()
        
        # Step 5: 展示价值
        console.print("[bold yellow]💡 这个 Agent 的价值：[/bold yellow]")
        console.print("""
  ✅ 每天节省 30 分钟人工分类时间
  ✅ 紧急问题第一时间通知（Slack）
  ✅ 减少 issues 积压，提升响应速度
  ✅ 自动生成 FAQ，减少重复咨询
  ✅ 数据驱动的团队效率分析
        """)
        
        console.print("\n[bold cyan]🚀 这就是 MCP Stack Composer 的真正价值：[/bold cyan]")
        console.print("   [dim]不是简单地列出数据，而是[/dim] [bold]自动化整个工作流！[/bold]")
        
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        console.print("\n[yellow]提示:[/yellow] 设置 GITHUB_TOKEN 环境变量可以看到真实数据")


if __name__ == "__main__":
    if not Config.GITHUB_TOKEN:
        console.print("[yellow]⚠️  未检测到 GITHUB_TOKEN，将使用模拟数据[/yellow]")
        console.print("[dim]设置方法: export GITHUB_TOKEN='your_token'[/dim]\n")
    
    demo_intelligent_issue_manager()

