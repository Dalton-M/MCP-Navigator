"""
成本估算器
计算使用 MCP 的预估成本
"""

# MCP 和 API 服务的定价信息
PRICING = {
    "groq": {
        "llama-3.3-70b": {
            "input_per_1m_tokens": 0.59,   # $0.59 per 1M input tokens
            "output_per_1m_tokens": 0.79,  # $0.79 per 1M output tokens
        },
        "llama-3.1-70b": {
            "input_per_1m_tokens": 0.59,
            "output_per_1m_tokens": 0.79,
        }
    },
    "github": {
        "api_calls": 0.0,  # 免费
        "rate_limit": 5000,  # per hour
        "note": "免费但有速率限制"
    },
    "brave-search": {
        "per_query": 0.005,  # $0.005 per query ($5 per 1000 queries)
        "free_tier": 2000,   # 2000 queries/month free
        "note": "前 2000 次免费"
    },
    "stripe": {
        "per_request": 0.0,  # 免费
        "transaction_fee": 0.029,  # 2.9% + $0.30
        "note": "API 免费，交易收手续费"
    },
    "notion": {
        "per_request": 0.0,  # 免费
        "note": "Notion API 免费使用"
    },
    "mongodb": {
        "atlas_free": 0.0,  # 免费层
        "atlas_paid": 0.08,  # per GB per month
        "note": "Atlas 有免费层"
    }
}


class CostEstimator:
    """成本估算器"""
    
    def __init__(self):
        self.pricing = PRICING
    
    def estimate_groq_cost(self, input_tokens: int, output_tokens: int, model: str = "llama-3.3-70b"):
        """
        估算 Groq API 成本
        
        Args:
            input_tokens: 输入 token 数
            output_tokens: 输出 token 数
            model: 模型名称
        
        Returns:
            float: 预估成本（美元）
        """
        if model not in self.pricing["groq"]:
            model = "llama-3.3-70b"  # 默认
        
        pricing = self.pricing["groq"][model]
        
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m_tokens"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m_tokens"]
        
        return input_cost + output_cost
    
    def estimate_brave_cost(self, num_queries: int):
        """
        估算 Brave Search 成本
        
        Args:
            num_queries: 搜索查询次数
        
        Returns:
            float: 预估成本（美元）
        """
        free_tier = self.pricing["brave-search"]["free_tier"]
        
        if num_queries <= free_tier:
            return 0.0
        
        paid_queries = num_queries - free_tier
        return paid_queries * self.pricing["brave-search"]["per_query"]
    
    def estimate_workflow_cost(self, workflow_config: dict):
        """
        估算完整工作流的成本
        
        Args:
            workflow_config: {
                "groq_calls": 2,
                "groq_input_tokens": 1000,
                "groq_output_tokens": 500,
                "github_calls": 5,
                "brave_queries": 10,
                "other_mcps": []
            }
        
        Returns:
            dict: 详细的成本估算
        """
        breakdown = {}
        total_cost = 0.0
        
        # Groq 成本
        if workflow_config.get("groq_calls", 0) > 0:
            groq_cost = self.estimate_groq_cost(
                workflow_config.get("groq_input_tokens", 1000),
                workflow_config.get("groq_output_tokens", 500)
            )
            breakdown["groq"] = {
                "cost": groq_cost,
                "calls": workflow_config.get("groq_calls"),
                "note": "LLM cost"
            }
            total_cost += groq_cost
        
        # GitHub 成本
        if workflow_config.get("github_calls", 0) > 0:
            breakdown["github"] = {
                "cost": 0.0,
                "calls": workflow_config.get("github_calls"),
                "note": "Free (with rate limit: 5000/hour)"
            }
        
        # Brave Search 成本
        if workflow_config.get("brave_queries", 0) > 0:
            brave_cost = self.estimate_brave_cost(workflow_config.get("brave_queries"))
            breakdown["brave-search"] = {
                "cost": brave_cost,
                "queries": workflow_config.get("brave_queries"),
                "note": f"Free for first 2000 queries, then $0.005/query"
            }
            total_cost += brave_cost
        
        return {
            "total_cost": round(total_cost, 4),
            "breakdown": breakdown,
            "currency": "USD",
            "estimated_monthly_cost": round(total_cost * 30, 2),  # 假设每天运行一次
            "recommendations": self._get_cost_optimization_tips(breakdown)
        }
    
    def estimate_by_mcps(self, mcps: list, daily_runs: int = 1):
        """
        基于 MCP 列表估算成本
        
        Args:
            mcps: MCP ID 列表
            daily_runs: 每天运行次数
        
        Returns:
            dict: 成本估算
        """
        # 典型用量假设
        config = {
            "groq_calls": 2,  # 分析 + 生成
            "groq_input_tokens": 2000,
            "groq_output_tokens": 1000,
            "github_calls": 5 if "github" in mcps else 0,
            "brave_queries": 10 if any(m in ["brave-search", "brave"] for m in mcps) else 0
        }
        
        single_run = self.estimate_workflow_cost(config)
        
        return {
            "per_run": single_run["total_cost"],
            "daily_cost": single_run["total_cost"] * daily_runs,
            "monthly_cost": single_run["total_cost"] * daily_runs * 30,
            "yearly_cost": single_run["total_cost"] * daily_runs * 365,
            "breakdown": single_run["breakdown"]
        }
    
    def _get_cost_optimization_tips(self, breakdown: dict):
        """生成成本优化建议"""
        tips = []
        
        if "groq" in breakdown and breakdown["groq"]["cost"] > 0.01:
            tips.append("💡 启用响应缓存可减少 40% Groq 调用成本")
        
        if "brave-search" in breakdown and breakdown["brave-search"]["queries"] > 2000:
            tips.append("💡 使用结果缓存避免重复搜索，节省 Brave API 成本")
        
        if "github" in breakdown and breakdown["github"]["calls"] > 1000:
            tips.append("💡 批量 API 调用减少请求次数，避免速率限制")
        
        if not tips:
            tips.append("✅ 成本已经很优化了！")
        
        return tips


def format_cost_display(cost_data: dict) -> str:
    """
    格式化成本数据用于显示
    """
    lines = []
    
    lines.append("\n💰 成本估算")
    lines.append("─" * 50)
    lines.append(f"单次运行: ${cost_data['per_run']:.4f}")
    lines.append(f"每日成本: ${cost_data['daily_cost']:.4f}")
    lines.append(f"每月成本: ${cost_data['monthly_cost']:.2f}")
    lines.append(f"每年成本: ${cost_data['yearly_cost']:.2f}")
    lines.append("")
    
    lines.append("📊 成本明细")
    for service, info in cost_data.get('breakdown', {}).items():
        lines.append(f"• {service}: ${info['cost']:.4f} - {info.get('note', '')}")
    
    return "\n".join(lines)

