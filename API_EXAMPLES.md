# 📖 API Usage Examples (Simple Guide)

> Quick examples showing input → output for each endpoint

---

## 🌟 Main Endpoint: `/api/v1/compose` (All-in-One)

### Input

```json
{
  "description": "I want an agent that reads GitHub issues and searches for solutions",
  "top_k": 3
}
```

### Output (Complete Response)

```json
{
  "request": "I want an agent that reads GitHub issues and searches for solutions",
  
  "capabilities": {
    "capabilities": ["code_hosting.read_issues", "web_search"],
    "reasoning": "User needs GitHub integration and web search",
    "confidence": 0.95
  },
  
  "recommended_mcps": [
    {
      "mcp_id": "github",
      "display_name": "GitHub Official",
      "score": 2.0,
      "docker_image": "mcp/github",
      "env_vars": ["GITHUB_TOKEN"]
    },
    {
      "mcp_id": "brave-search",
      "display_name": "Brave Search",
      "score": 1.5,
      "docker_image": "mcp/brave",
      "env_vars": ["BRAVE_API_KEY"]
    }
  ],
  
  "code_snippet": {
    "markdown": "## Setup instructions...",
    "env_vars": ["GITHUB_TOKEN", "BRAVE_API_KEY"]
  },
  
  "cost_estimate": {
    "per_run": 0.0150,
    "monthly_cost": 0.45,
    "breakdown": {
      "groq": {"cost": 0.0020},
      "github": {"cost": 0.0000},
      "brave-search": {"cost": 0.0500}
    }
  },
  
  "workflow_execution": {
    "status": "success",
    "total_time": 8.5,
    "steps_completed": 3,
    "results": {
      "github": {
        "result": [
          {"number": 215432, "title": "[Bug] Extension host crashed"}
        ]
      },
      "brave-search": {
        "results": [
          {
            "issue_number": 215432,
            "solutions": {
              "web": {
                "results": [
                  {"title": "How to fix...", "url": "https://..."}
                ]
              }
            }
          }
        ]
      },
      "analysis": {
        "total_issues": 5,
        "summary": "Processed 5 issues, found solutions for 5"
      }
    }
  },
  
  "status": "success"
}
```

**What you get:**
- ✅ Capability analysis
- ✅ MCP recommendations
- ✅ Setup code
- ✅ **Cost estimate (automatic!)**
- ✅ **Real execution results (automatic!)**

---

## 💰 Cost Estimation: `/api/v1/estimate-cost`

### Input

```json
{
  "mcps": ["github", "brave-search"],
  "daily_runs": 5
}
```

**Fields:**
- `mcps`: Array of MCP IDs you plan to use
- `daily_runs`: How many times per day (default: 1)

### Output

```json
{
  "mcps": ["github", "brave-search"],
  "daily_runs": 5,
  "cost_estimate": {
    "per_run": 0.0150,
    "daily_cost": 0.0750,
    "monthly_cost": 2.25,
    "yearly_cost": 27.38,
    "breakdown": {
      "groq": {
        "cost": 0.0020,
        "calls": 2,
        "note": "LLM analysis and code generation"
      },
      "github": {
        "cost": 0.0000,
        "calls": 5,
        "note": "Free (rate limit: 5000/hour)"
      },
      "brave-search": {
        "cost": 0.0500,
        "queries": 10,
        "note": "First 2000 free, then $0.005/query"
      }
    }
  }
}
```

**Meaning:**
- `per_run`: Cost for 1 execution
- `daily_cost`: per_run × daily_runs
- `monthly_cost`: daily_cost × 30
- `yearly_cost`: daily_cost × 365
- `breakdown`: Cost per service with explanations

---

## 🔄 Workflow Execution: `/api/v1/workflows/execute`

### Input

```json
{
  "template_id": "github_daily_report",
  "config": {
    "owner": "facebook",
    "repo": "react"
  }
}
```

**Fields:**
- `template_id`: Which template to run
  - Available: `github_daily_report`, `competitor_monitoring`, `code_review_assistant`, etc.
- `config`: Custom parameters for the workflow
  - For GitHub: `{"owner": "...", "repo": "..."}`

### Output

```json
{
  "template_id": "github_daily_report",
  "template_name": "📊 GitHub Daily Report",
  "status": "completed",
  "steps": [
    {
      "step": 1,
      "mcp": "github",
      "action": "list_issues",
      "status": "success",
      "result": [
        {"number": 28000, "title": "Feature request", "comments": 45}
      ]
    },
    {
      "step": 2,
      "mcp": "brave-search",
      "action": "search",
      "status": "success",
      "result": {
        "web": {"results": [...]}
      }
    }
  ]
}
```

**Meaning:**
- `status`: "completed" | "failed" | "partial"
- `steps`: Array of execution results for each step
- Each step shows what MCP was called and what it returned

---

## 📋 List Templates: `/api/v1/templates`

### Input

No input required (GET request)

### Output

```json
{
  "templates": {
    "github_daily_report": {
      "name": "📊 GitHub Daily Report",
      "description": "Fetch issues, search solutions, generate report",
      "estimated_cost": "$0.02",
      "difficulty": "easy",
      "mcps": ["github", "brave-search"]
    }
  },
  "summary": {
    "total": 5,
    "by_category": {"productivity": 1, "development": 1}
  }
}
```

---

## 🎯 The Key Improvement

### Before (Old /api/v1/compose):

```
Input: description
  ↓
Output: recommendations + code
```

### Now (New /api/v1/compose):

```
Input: description
  ↓
Output: recommendations + code + COST + REAL EXECUTION RESULTS
```

**One API call, complete automation!** 🚀

---

## 💻 Test Commands

```bash
# 1. Compose (gets everything)
curl -X POST http://localhost:8000/api/v1/compose \
  -H "Content-Type: application/json" \
  -d '{"description":"I want an agent that reads GitHub issues","top_k":3}'

# 2. Estimate cost
curl -X POST http://localhost:8000/api/v1/estimate-cost \
  -H "Content-Type: application/json" \
  -d '{"mcps":["github","brave-search"],"daily_runs":5}'

# 3. List templates
curl http://localhost:8000/api/v1/templates

# 4. Execute template
curl -X POST http://localhost:8000/api/v1/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{"template_id":"github_daily_report","config":{"owner":"facebook","repo":"react"}}'
```

---

**Now you understand what each endpoint does!** 🎉

The main `/api/v1/compose` endpoint automatically:
1. Analyzes your description
2. Recommends MCPs  
3. Generates code
4. **Estimates costs**
5. **Executes the workflow**
6. **Returns actual results**

All in one API call! 🚀

