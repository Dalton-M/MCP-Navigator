"""
预置工作流模板
提供常用的 MCP 组合和配置
"""

WORKFLOW_TEMPLATES = {
    "github_daily_report": {
        "id": "github_daily_report",
        "name": "📊 GitHub 每日报告",
        "description": "自动获取 GitHub issues，搜索解决方案，生成每日分析报告",
        "category": "productivity",
        "difficulty": "easy",
        "estimated_time": "10s",
        "estimated_cost": "$0.02",
        "mcps": ["github", "brave-search"],
        "capabilities": [
            "code_hosting.read_issues",
            "web_search",
            "research.synthesis"
        ],
        "workflow_steps": [
            {
                "step": 1,
                "mcp": "github",
                "action": "list_issues",
                "description": "获取 GitHub repository 的 open issues",
                "config": {
                    "owner": "microsoft",
                    "repo": "vscode",
                    "state": "open",
                    "per_page": 10
                }
            },
            {
                "step": 2,
                "mcp": "brave-search",
                "action": "search",
                "description": "为每个 issue 搜索相关解决方案",
                "depends_on": [1],
                "config": {
                    "query": "{{issue.title}} solution",
                    "num_results": 3
                }
            },
            {
                "step": 3,
                "action": "generate_report",
                "description": "基于 GitHub 和搜索数据生成智能报告",
                "depends_on": [1, 2]
            }
        ],
        "expected_output": {
            "github_issues": 10,
            "search_queries": 10,
            "report": "Markdown format"
        },
        "use_case": "开发团队每天早上自动收到 issues 分析报告，节省 30 分钟手动工作"
    },
    
    "competitor_monitoring": {
        "id": "competitor_monitoring",
        "name": "🔍 竞品监控 Agent",
        "description": "监控竞品 GitHub 活动，搜索市场动态，生成竞品分析",
        "category": "business_intelligence",
        "difficulty": "medium",
        "estimated_time": "20s",
        "estimated_cost": "$0.05",
        "mcps": ["github", "brave-search"],
        "capabilities": [
            "code_hosting.read_repos",
            "code_hosting.read_issues",
            "web_search",
            "research.synthesis"
        ],
        "workflow_steps": [
            {
                "step": 1,
                "mcp": "github",
                "action": "list_repos",
                "description": "获取竞品的 GitHub repositories"
            },
            {
                "step": 2,
                "mcp": "github",
                "action": "list_recent_commits",
                "description": "获取最近的代码更新"
            },
            {
                "step": 3,
                "mcp": "brave-search",
                "action": "search",
                "description": "搜索竞品的新闻和讨论",
                "config": {
                    "query": "{{competitor_name}} product updates"
                }
            },
            {
                "step": 4,
                "action": "generate_competitor_report",
                "description": "生成竞品分析报告"
            }
        ],
        "use_case": "产品经理每周自动获得竞品动态分析，了解市场趋势"
    },
    
    "code_review_assistant": {
        "id": "code_review_assistant",
        "name": "👨‍💻 AI 代码审查助手",
        "description": "自动审查 Pull Requests，搜索最佳实践，提供改进建议",
        "category": "development",
        "difficulty": "medium",
        "estimated_time": "15s",
        "estimated_cost": "$0.03",
        "mcps": ["github", "brave-search"],
        "capabilities": [
            "code_hosting.manage_pr",
            "code_hosting.search_code",
            "web_search"
        ],
        "workflow_steps": [
            {
                "step": 1,
                "mcp": "github",
                "action": "list_pull_requests",
                "description": "获取待审查的 PRs"
            },
            {
                "step": 2,
                "mcp": "github",
                "action": "get_pr_diff",
                "description": "获取代码变更"
            },
            {
                "step": 3,
                "mcp": "brave-search",
                "action": "search",
                "description": "搜索代码最佳实践",
                "config": {
                    "query": "{{language}} best practices {{topic}}"
                }
            },
            {
                "step": 4,
                "action": "generate_review_comments",
                "description": "生成审查意见"
            }
        ],
        "use_case": "自动化初步代码审查，提高团队效率"
    },
    
    "issue_auto_triage": {
        "id": "issue_auto_triage",
        "name": "🏷️  Issue 自动分类",
        "description": "自动分类和标记 issues，搜索相似问题，建议解决方案",
        "category": "automation",
        "difficulty": "easy",
        "estimated_time": "12s",
        "estimated_cost": "$0.03",
        "mcps": ["github", "brave-search"],
        "capabilities": [
            "code_hosting.read_issues",
            "code_hosting.create_issue",
            "web_search"
        ],
        "workflow_steps": [
            {
                "step": 1,
                "mcp": "github",
                "action": "list_issues",
                "description": "获取未分类的 issues",
                "config": {
                    "labels": "needs-triage"
                }
            },
            {
                "step": 2,
                "mcp": "brave-search",
                "action": "search",
                "description": "搜索相似问题",
                "config": {
                    "query": "{{issue.title}} similar issues"
                }
            },
            {
                "step": 3,
                "action": "auto_label",
                "description": "基于搜索结果自动添加标签"
            }
        ],
        "use_case": "减少人工分类时间，快速处理大量 issues"
    },
    
    "documentation_generator": {
        "id": "documentation_generator",
        "name": "📝 文档自动生成",
        "description": "基于代码库和搜索结果自动生成文档",
        "category": "documentation",
        "difficulty": "hard",
        "estimated_time": "30s",
        "estimated_cost": "$0.10",
        "mcps": ["github", "brave-search"],
        "capabilities": [
            "code_hosting.read_repos",
            "code_hosting.search_code",
            "web_search",
            "research.synthesis"
        ],
        "workflow_steps": [
            {
                "step": 1,
                "mcp": "github",
                "action": "get_repo_structure",
                "description": "分析代码库结构"
            },
            {
                "step": 2,
                "mcp": "brave-search",
                "action": "search",
                "description": "搜索相关技术文档",
                "config": {
                    "query": "{{framework}} documentation best practices"
                }
            },
            {
                "step": 3,
                "action": "generate_documentation",
                "description": "生成完整的 API 文档和使用指南"
            }
        ],
        "use_case": "自动化文档维护，确保文档始终与代码同步"
    }
}


def get_template(template_id: str):
    """获取特定模板"""
    return WORKFLOW_TEMPLATES.get(template_id)


def list_templates(category=None):
    """列出所有模板，可选按分类过滤"""
    if category:
        return {
            k: v for k, v in WORKFLOW_TEMPLATES.items()
            if v.get('category') == category
        }
    return WORKFLOW_TEMPLATES


def get_templates_by_difficulty(difficulty):
    """按难度筛选模板"""
    return {
        k: v for k, v in WORKFLOW_TEMPLATES.items()
        if v.get('difficulty') == difficulty
    }


def get_template_summary():
    """获取模板统计摘要"""
    return {
        "total": len(WORKFLOW_TEMPLATES),
        "by_category": {
            "productivity": 1,
            "business_intelligence": 1,
            "development": 1,
            "automation": 1,
            "documentation": 1
        },
        "by_difficulty": {
            "easy": 2,
            "medium": 2,
            "hard": 1
        }
    }

