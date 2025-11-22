#!/usr/bin/env python3
"""
展示 Outstanding Features
运行这个脚本看到增强功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from app.workflow_templates import WORKFLOW_TEMPLATES, get_template_summary
from app.cost_estimator import CostEstimator, format_cost_display

console = Console()


def showcase_templates():
    """展示预置模板功能"""
    
    console.print(Panel(
        "[bold cyan]🌟 Feature 1: 预置工作流模板[/bold cyan]\n"
        "快速开始，无需从头配置",
        title="Outstanding Feature",
        border_style="cyan"
    ))
    print()
    
    # 创建模板表格
    table = Table(title="可用模板", show_header=True, header_style="bold cyan")
    table.add_column("模板", style="bold", width=30)
    table.add_column("说明", width=40)
    table.add_column("难度", width=8)
    table.add_column("成本", justify="right", width=10)
    
    for template_id, template in WORKFLOW_TEMPLATES.items():
        difficulty_color = {
            "easy": "green",
            "medium": "yellow",
            "hard": "red"
        }.get(template['difficulty'], "white")
        
        table.add_row(
            template['name'],
            template['description'][:37] + "..." if len(template['description']) > 40 else template['description'],
            f"[{difficulty_color}]{template['difficulty']}[/{difficulty_color}]",
            template['estimated_cost']
        )
    
    console.print(table)
    print()
    
    # 展示模板详情
    console.print("[bold]📋 模板示例: GitHub 每日报告[/bold]\n")
    
    template = WORKFLOW_TEMPLATES['github_daily_report']
    
    console.print(f"[cyan]用例:[/cyan] {template['use_case']}\n")
    console.print("[cyan]工作流步骤:[/cyan]")
    
    for step in template['workflow_steps']:
        step_num = step['step']
        mcp = step.get('mcp', 'System')
        action = step['action']
        desc = step['description']
        
        console.print(f"  {step_num}. [bold]{mcp}[/bold].{action}")
        console.print(f"     {desc}")
        
        if step.get('depends_on'):
            console.print(f"     [dim]依赖: Step {step['depends_on']}[/dim]")
        print()
    
    console.print(f"[green]✅ 预期输出:[/green] {template['expected_output']}\n")
    
    # 统计
    summary = get_template_summary()
    console.print(f"[dim]📊 模板统计: {summary['total']} 个模板，覆盖 {len(summary['by_category'])} 个类别[/dim]\n")


def showcase_cost_estimation():
    """展示成本估算功能"""
    
    console.print(Panel(
        "[bold cyan]🌟 Feature 2: 智能成本估算[/bold cyan]\n"
        "透明的成本信息，帮助做出明智决策",
        title="Outstanding Feature",
        border_style="cyan"
    ))
    print()
    
    estimator = CostEstimator()
    
    # 示例 1: 单次工作流
    console.print("[bold]💰 示例 1: GitHub 每日报告工作流[/bold]\n")
    
    workflow_config = {
        "groq_calls": 2,
        "groq_input_tokens": 2000,
        "groq_output_tokens": 1000,
        "github_calls": 5,
        "brave_queries": 10
    }
    
    cost = estimator.estimate_workflow_cost(workflow_config)
    
    console.print(f"单次运行成本: [bold green]${cost['total_cost']:.4f}[/bold green]")
    console.print(f"每月成本 (每日运行): [bold]${cost['estimated_monthly_cost']:.2f}[/bold]\n")
    
    console.print("[cyan]成本明细:[/cyan]")
    for service, info in cost['breakdown'].items():
        console.print(f"  • {service}: ${info['cost']:.4f}")
        console.print(f"    {info['note']}")
    
    print()
    
    # 优化建议
    console.print("[bold yellow]💡 优化建议:[/bold yellow]")
    for tip in cost['recommendations']:
        console.print(f"  {tip}")
    print()
    
    # 示例 2: 不同 MCP 组合对比
    console.print("[bold]📊 示例 2: MCP 组合成本对比[/bold]\n")
    
    comparison_table = Table(show_header=True, header_style="bold cyan")
    comparison_table.add_column("MCP 组合", width=30)
    comparison_table.add_column("单次", justify="right", width=12)
    comparison_table.add_column("每日", justify="right", width=12)
    comparison_table.add_column("每月", justify="right", width=12)
    
    combinations = [
        (["github"], "GitHub only"),
        (["github", "brave-search"], "GitHub + Brave"),
        (["github", "brave-search", "notion"], "完整工作流")
    ]
    
    for mcps, name in combinations:
        cost_data = estimator.estimate_by_mcps(mcps, daily_runs=1)
        comparison_table.add_row(
            name,
            f"${cost_data['per_run']:.4f}",
            f"${cost_data['daily_cost']:.4f}",
            f"${cost_data['monthly_cost']:.2f}"
        )
    
    console.print(comparison_table)
    print()
    
    console.print("[dim]💡 成本优化可以节省 40-60% 的开支[/dim]\n")


def showcase_workflow_visualization():
    """展示工作流可视化"""
    
    console.print(Panel(
        "[bold cyan]🌟 Feature 3: 工作流可视化[/bold cyan]\n"
        "直观展示 MCP 之间的数据流和依赖关系",
        title="Outstanding Feature",
        border_style="cyan"
    ))
    print()
    
    console.print("[bold]📊 工作流图示 (Mermaid 格式):[/bold]\n")
    
    mermaid_code = """
graph LR
    A[用户输入] --> B[Groq LLM 分析]
    B --> C[MCP 匹配]
    C --> D[GitHub MCP]
    C --> E[Brave Search MCP]
    D --> F[数据聚合]
    E --> F
    F --> G[Groq 生成报告]
    G --> H[输出结果]
    
    style A fill:#e1f5ff
    style B fill:#fff3cd
    style D fill:#d4edda
    style E fill:#d4edda
    style G fill:#fff3cd
    style H fill:#d1ecf1
"""
    
    console.print(Panel(mermaid_code, title="Mermaid Diagram", border_style="blue"))
    
    console.print("\n[dim]💡 在前端可以使用 Mermaid.js 渲染为可视化图表[/dim]")
    console.print("[dim]💡 显示：数据流向、依赖关系、执行顺序[/dim]\n")


def showcase_all():
    """展示所有 Outstanding Features"""
    
    console.print("\n" + "="*70)
    console.print("[bold green]✨ MCP Stack Composer - Outstanding Features Showcase[/bold green]")
    console.print("="*70 + "\n")
    
    # Feature 1: 预置模板
    showcase_templates()
    
    input("\n按 Enter 继续查看下一个功能...")
    print("\n")
    
    # Feature 2: 成本估算
    showcase_cost_estimation()
    
    input("\n按 Enter 继续查看下一个功能...")
    print("\n")
    
    # Feature 3: 工作流可视化
    showcase_workflow_visualization()
    
    print("\n" + "="*70)
    console.print("[bold green]🎉 Outstanding Features 演示完成！[/bold green]")
    console.print("="*70 + "\n")
    
    console.print("[bold]这些功能让项目从"能用"变成"卓越"：[/bold]")
    console.print("  1. ✅ 预置模板 - 降低使用门槛")
    console.print("  2. ✅ 成本估算 - 透明和可预测")
    console.print("  3. ✅ 工作流可视化 - 直观易懂")
    console.print("  4. ✅ Multi-MCP 执行 - 真正的编排能力")
    print()
    
    console.print("[cyan]💡 下一步：[/cyan]")
    console.print("  • 运行: python multi_mcp_workflow.py（查看多 MCP 协同）")
    console.print("  • 查看: OUTSTANDING_FEATURES.md（完整路线图）")
    console.print("  • 集成到 API Server（api_server.py）\n")


if __name__ == "__main__":
    try:
        showcase_all()
    except KeyboardInterrupt:
        console.print("\n[yellow]演示已中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")

