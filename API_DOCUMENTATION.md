# 🔌 MCP Stack Composer - API Documentation

> Complete API reference with examples

---

## 🌟 Main Endpoint: Compose Agent (All-in-One)

### `POST /api/v1/compose`

**The only endpoint you need!** This automatically:
1. ✅ Analyzes your requirements
2. ✅ Recommends MCPs
3. ✅ Generates code
4. ✅ **Estimates cost** (NEW!)
5. ✅ **Executes Multi-MCP workflow** (NEW!)

#### Request

```json
{
  "description": "I want an agent that reads GitHub issues and searches for solutions",
  "top_k": 3
}
```

**Fields:**
- `description` (string, required): Natural language description of your agent
- `top_k` (integer, optional): Number of MCP recommendations to return (default: 3, max: 10)

#### Response

```json
{
  "request": "I want an agent that reads GitHub issues and searches for solutions",
  
  "capabilities": {
    "capabilities": [
      "code_hosting.read_issues",
      "web_search"
    ],
    "reasoning": "User needs GitHub integration and web search capabilities",
    "confidence": 0.95
  },
  
  "recommended_mcps": [
    {
      "mcp_id": "github",
      "display_name": "GitHub Official",
      "description": "Official GitHub MCP Server",
      "score": 2.0,
      "exact_matches": ["code_hosting.read_issues"],
      "partial_matches": [],
      "env_vars": ["GITHUB_TOKEN"],
      "docker_image": "mcp/github",
      "example_tools": ["list_issues", "create_issue"]
    },
    {
      "mcp_id": "brave-search",
      "display_name": "Brave Search",
      "description": "Search the Web using Brave Search API",
      "score": 1.5,
      "exact_matches": ["web_search"],
      "partial_matches": [],
      "env_vars": ["BRAVE_API_KEY"],
      "docker_image": "mcp/brave",
      "example_tools": ["search"]
    }
  ],
  
  "code_snippet": {
    "markdown": "## 🎯 Why These MCPs?\n\n**GitHub** provides code_hosting.read_issues...",
    "env_vars": ["GITHUB_TOKEN", "BRAVE_API_KEY"]
  },
  
  "cost_estimate": {
    "per_run": 0.0150,
    "daily_cost": 0.0150,
    "monthly_cost": 0.45,
    "yearly_cost": 5.48,
    "breakdown": {
      "groq": {
        "cost": 0.0020,
        "note": "LLM analysis and code generation"
      },
      "github": {
        "cost": 0.0000,
        "note": "Free (with rate limit: 5000/hour)"
      },
      "brave-search": {
        "cost": 0.0500,
        "note": "First 2000 queries free, then $0.005/query"
      }
    }
  },
  
  "workflow_execution": {
    "status": "success",
    "total_time": 8.5,
    "steps_completed": 3,
    "total_steps": 3,
    "results": {
      "github": {
        "mcp_id": "github",
        "tool": "list_issues",
        "success": true,
        "result": [
          {
            "number": 215432,
            "title": "[Bug] Extension host crashed",
            "state": "open",
            "comments": 12,
            "labels": ["bug", "investigating"]
          }
        ]
      },
      "brave-search": {
        "success": true,
        "total_searches": 5,
        "results": [
          {
            "issue_number": 215432,
            "solutions": {
              "query": "[Bug] Extension host crashed solution",
              "web": {
                "results": [
                  {
                    "title": "How to fix VSCode extension host crash",
                    "url": "https://stackoverflow.com/...",
                    "description": "This issue often occurs when..."
                  }
                ]
              }
            }
          }
        ]
      },
      "analysis": {
        "total_issues": 5,
        "issues_with_solutions": 5,
        "summary": "Processed 5 GitHub issues, found solutions for 5 of them"
      }
    }
  },
  
  "demo_call": null,
  "status": "success"
}
```

**Key Points:**
- ✅ Single API call returns everything
- ✅ Includes cost estimation automatically
- ✅ Executes actual Multi-MCP workflow
- ✅ Shows real results from GitHub and Brave Search

---

## 💰 Cost Estimation Endpoint

### `POST /api/v1/estimate-cost`

Estimate costs for using specific MCP combinations.

#### Request

```json
{
  "mcps": ["github", "brave-search", "notion"],
  "daily_runs": 3
}
```

**Fields:**
- `mcps` (array of strings, required): List of MCP IDs
  - Example values: "github", "brave-search", "stripe", "notion", "mongodb"
- `daily_runs` (integer, optional): Number of times the workflow runs per day (default: 1, min: 1, max: 1000)

#### Response

```json
{
  "mcps": ["github", "brave-search", "notion"],
  "daily_runs": 3,
  "cost_estimate": {
    "per_run": 0.0200,
    "daily_cost": 0.0600,
    "monthly_cost": 1.80,
    "yearly_cost": 21.90,
    "breakdown": {
      "groq": {
        "cost": 0.0020,
        "calls": 2,
        "note": "LLM analysis and code generation"
      },
      "github": {
        "cost": 0.0000,
        "calls": 5,
        "note": "Free (with rate limit: 5000/hour)"
      },
      "brave-search": {
        "cost": 0.0500,
        "queries": 10,
        "note": "First 2000 queries free, then $0.005/query"
      },
      "notion": {
        "cost": 0.0000,
        "note": "Notion API is free"
      }
    }
  },
  "currency": "USD"
}
```

**Use Cases:**
- 💡 Compare costs of different MCP combinations
- 💡 Budget planning
- 💡 Optimization decisions

**Example:**
```javascript
// Frontend: Show cost before executing
const cost = await fetch('https://your-api/api/v1/estimate-cost', {
  method: 'POST',
  body: JSON.stringify({
    mcps: ['github', 'brave-search'],
    daily_runs: 5  // Team runs it 5 times per day
  })
}).then(r => r.json());

alert(`Monthly cost: $${cost.cost_estimate.monthly_cost}`);
```

---

## 🔄 Workflow Execution Endpoint

### `POST /api/v1/workflows/execute`

Execute a pre-built workflow template with custom configuration.

#### Request

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
- `template_id` (string, required): Template identifier
  - Available templates: `github_daily_report`, `competitor_monitoring`, `code_review_assistant`, `issue_auto_triage`, `documentation_generator`
- `config` (object, optional): Custom configuration parameters
  - For GitHub templates: `{"owner": "org_name", "repo": "repo_name"}`
  - For search templates: `{"query": "search terms"}`

#### Response

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
        {
          "number": 28000,
          "title": "Feature: Add suspense support",
          "comments": 45
        }
      ]
    },
    {
      "step": 2,
      "mcp": "brave-search",
      "action": "search",
      "status": "success",
      "result": {
        "query": "Feature: Add suspense support solution",
        "web": {
          "results": [...]
        }
      }
    }
  ]
}
```

**Use Cases:**
- 💡 Quick start with pre-built templates
- 💡 Consistent workflow execution
- 💡 Best practice examples

---

## 📋 Templates Endpoint

### `GET /api/v1/templates`

List all available workflow templates.

#### Request

No parameters required.

#### Response

```json
{
  "templates": {
    "github_daily_report": {
      "id": "github_daily_report",
      "name": "📊 GitHub Daily Report",
      "description": "Automatically fetch GitHub issues, search solutions, generate daily report",
      "category": "productivity",
      "difficulty": "easy",
      "estimated_time": "10s",
      "estimated_cost": "$0.02",
      "mcps": ["github", "brave-search"],
      "capabilities": ["code_hosting.read_issues", "web_search"],
      "workflow_steps": [
        {
          "step": 1,
          "mcp": "github",
          "action": "list_issues",
          "description": "Fetch GitHub repository open issues"
        },
        {
          "step": 2,
          "mcp": "brave-search",
          "action": "search",
          "description": "Search solutions for each issue",
          "depends_on": [1]
        }
      ],
      "use_case": "Development team receives automated issue analysis every morning, saving 30 minutes of manual work"
    }
  },
  "summary": {
    "total": 5,
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
}
```

### `GET /api/v1/templates/{template_id}`

Get details for a specific template.

#### Response

```json
{
  "id": "github_daily_report",
  "name": "📊 GitHub Daily Report",
  "description": "...",
  "workflow_steps": [...],
  "expected_output": {
    "github_issues": 10,
    "search_queries": 10,
    "report": "Markdown format"
  }
}
```

---

## 🎯 Complete Frontend Integration Example

### All-in-One Compose

```javascript
// Single API call gets everything
const response = await fetch('https://your-api/api/v1/compose', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    description: "I want an agent that reads GitHub issues and searches for solutions",
    top_k: 3
  })
});

const data = await response.json();

// 1. Show capabilities
console.log('Capabilities:', data.capabilities.capabilities);
console.log('Confidence:', data.capabilities.confidence);

// 2. Show recommended MCPs
data.recommended_mcps.forEach(mcp => {
  console.log(`${mcp.display_name} (Score: ${mcp.score})`);
  console.log(`  Docker: ${mcp.docker_image}`);
  console.log(`  Env: ${mcp.env_vars.join(', ')}`);
});

// 3. Show generated code
console.log('Setup Code:', data.code_snippet.markdown);

// 4. Show cost estimate (NEW!)
console.log('Cost per run:', data.cost_estimate.per_run);
console.log('Monthly cost:', data.cost_estimate.monthly_cost);

// 5. Show workflow execution results (NEW!)
if (data.workflow_execution.status === 'success') {
  console.log('GitHub Issues:', data.workflow_execution.results.github.result);
  console.log('Search Results:', data.workflow_execution.results['brave-search'].results);
  console.log('Analysis:', data.workflow_execution.results.analysis);
}

// 6. Show execution time
console.log('Total execution time:', data.workflow_execution.total_time, 'seconds');
```

### Using Templates

```javascript
// 1. List available templates
const templates = await fetch('https://your-api/api/v1/templates')
  .then(r => r.json());

console.log('Available templates:', Object.keys(templates.templates));

// 2. Get template details
const template = await fetch('https://your-api/api/v1/templates/github_daily_report')
  .then(r => r.json());

console.log('Template:', template.name);
console.log('Estimated cost:', template.estimated_cost);
console.log('Steps:', template.workflow_steps);

// 3. Execute template
const result = await fetch('https://your-api/api/v1/workflows/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    template_id: 'github_daily_report',
    config: {
      owner: 'facebook',
      repo: 'react'
    }
  })
}).then(r => r.json());

console.log('Workflow status:', result.status);
console.log('Results:', result.steps);
```

### Cost Estimation

```javascript
// Compare costs of different MCP combinations
const combinations = [
  ['github'],
  ['github', 'brave-search'],
  ['github', 'brave-search', 'notion']
];

for (const mcps of combinations) {
  const cost = await fetch('https://your-api/api/v1/estimate-cost', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mcps: mcps,
      daily_runs: 1
    })
  }).then(r => r.json());
  
  console.log(`${mcps.join(' + ')}: $${cost.cost_estimate.monthly_cost}/month`);
}

// Output:
// github: $0.02/month
// github + brave-search: $0.45/month  
// github + brave-search + notion: $0.45/month
```

---

## 📊 Response Field Descriptions

### `capabilities`
- **capabilities** (array): Extracted capability tags
- **reasoning** (string): Why these capabilities were identified
- **confidence** (float): Confidence score 0-1

### `recommended_mcps` (array)
Each MCP contains:
- **mcp_id** (string): Unique identifier (e.g., "github")
- **display_name** (string): Human-readable name
- **description** (string): What this MCP does
- **score** (float): Match score (higher = better match)
- **exact_matches** (array): Capabilities that exactly match
- **partial_matches** (array): Capabilities that partially match
- **env_vars** (array): Required environment variables
- **docker_image** (string): Docker Hub image (e.g., "mcp/github")
- **example_tools** (array): Available tools/methods

### `code_snippet`
- **markdown** (string): Setup instructions and code examples
- **env_vars** (array): All required environment variables

### `cost_estimate` (NEW!)
- **per_run** (float): Cost per single execution ($)
- **daily_cost** (float): Cost if run once per day ($)
- **monthly_cost** (float): Cost per month ($)
- **yearly_cost** (float): Cost per year ($)
- **breakdown** (object): Detailed cost by service

### `workflow_execution` (NEW!)
- **status** (string): "success" | "partial" | "failed"
- **total_time** (float): Total execution time (seconds)
- **steps_completed** (int): Number of steps successfully completed
- **total_steps** (int): Total number of steps
- **results** (object): Results from each MCP
  - **github**: GitHub API results (issues, etc.)
  - **brave-search**: Search results
  - **analysis**: Generated insights

---

## 🔥 Advanced Examples

### Example 1: Complete Automation

```javascript
// One API call does everything
async function automateGitHubIssues() {
  const response = await fetch('https://your-api/api/v1/compose', {
    method: 'POST',
    body: JSON.stringify({
      description: "I want to monitor GitHub issues and search solutions automatically"
    })
  }).then(r => r.json());
  
  // Get real GitHub issues
  const issues = response.workflow_execution.results.github.result;
  
  // Get search results for each issue
  const searchResults = response.workflow_execution.results['brave-search'].results;
  
  // Show analysis
  console.log(response.workflow_execution.results.analysis);
  
  // Show cost
  console.log(`This workflow costs $${response.cost_estimate.per_run} per run`);
  
  return {
    issues,
    solutions: searchResults,
    cost: response.cost_estimate
  };
}
```

### Example 2: Template-Based Workflow

```javascript
// Use pre-built template for common scenario
async function runDailyReport() {
  // Step 1: Get template info
  const template = await fetch('https://your-api/api/v1/templates/github_daily_report')
    .then(r => r.json());
  
  console.log(`Running template: ${template.name}`);
  console.log(`Estimated cost: ${template.estimated_cost}`);
  
  // Step 2: Execute with custom config
  const result = await fetch('https://your-api/api/v1/workflows/execute', {
    method: 'POST',
    body: JSON.stringify({
      template_id: 'github_daily_report',
      config: {
        owner: 'microsoft',
        repo: 'vscode'
      }
    })
  }).then(r => r.json());
  
  console.log(`Status: ${result.status}`);
  console.log(`Steps completed: ${result.steps.length}`);
  
  return result;
}
```

### Example 3: Cost Comparison

```javascript
// Compare different MCP stacks
async function compareMCPCosts() {
  const stacks = [
    { name: 'Basic', mcps: ['github'] },
    { name: 'Enhanced', mcps: ['github', 'brave-search'] },
    { name: 'Complete', mcps: ['github', 'brave-search', 'notion', 'slack'] }
  ];
  
  const results = [];
  
  for (const stack of stacks) {
    const cost = await fetch('https://your-api/api/v1/estimate-cost', {
      method: 'POST',
      body: JSON.stringify({
        mcps: stack.mcps,
        daily_runs: 1
      })
    }).then(r => r.json());
    
    results.push({
      name: stack.name,
      mcps: stack.mcps,
      monthly_cost: cost.cost_estimate.monthly_cost
    });
  }
  
  // Show comparison
  results.forEach(r => {
    console.log(`${r.name}: $${r.monthly_cost}/month (${r.mcps.length} MCPs)`);
  });
  
  return results;
}
```

---

## 🌐 React Component Example

```tsx
import React, { useState } from 'react';

const MCPComposer: React.FC = () => {
  const [description, setDescription] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompose = async () => {
    setLoading(true);
    
    const response = await fetch('https://your-api/api/v1/compose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, top_k: 3 })
    });
    
    const data = await response.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div>
      <h1>MCP Stack Composer</h1>
      
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Describe your agent requirements..."
      />
      
      <button onClick={handleCompose} disabled={loading}>
        {loading ? 'Composing...' : 'Compose Agent'}
      </button>
      
      {result && (
        <div>
          {/* 1. Show capabilities */}
          <div>
            <h2>Identified Capabilities</h2>
            <ul>
              {result.capabilities.capabilities.map(cap => (
                <li key={cap}>{cap}</li>
              ))}
            </ul>
            <p>Confidence: {(result.capabilities.confidence * 100).toFixed(0)}%</p>
          </div>
          
          {/* 2. Show recommended MCPs */}
          <div>
            <h2>Recommended MCPs</h2>
            {result.recommended_mcps.map(mcp => (
              <div key={mcp.mcp_id}>
                <h3>{mcp.display_name} (Score: {mcp.score})</h3>
                <p>{mcp.description}</p>
                <p>Docker: {mcp.docker_image}</p>
              </div>
            ))}
          </div>
          
          {/* 3. Show cost estimate (NEW!) */}
          {result.cost_estimate && (
            <div>
              <h2>Cost Estimate</h2>
              <p>Per run: ${result.cost_estimate.per_run}</p>
              <p>Monthly: ${result.cost_estimate.monthly_cost}</p>
              <details>
                <summary>Cost Breakdown</summary>
                {Object.entries(result.cost_estimate.breakdown).map(([service, info]) => (
                  <div key={service}>
                    <strong>{service}:</strong> ${info.cost} - {info.note}
                  </div>
                ))}
              </details>
            </div>
          )}
          
          {/* 4. Show workflow execution (NEW!) */}
          {result.workflow_execution && result.workflow_execution.status === 'success' && (
            <div>
              <h2>Workflow Execution Results</h2>
              <p>Execution time: {result.workflow_execution.total_time}s</p>
              <p>Steps: {result.workflow_execution.steps_completed}/{result.workflow_execution.total_steps}</p>
              
              {/* GitHub results */}
              {result.workflow_execution.results.github && (
                <div>
                  <h3>GitHub Issues</h3>
                  <ul>
                    {result.workflow_execution.results.github.result?.map(issue => (
                      <li key={issue.number}>
                        #{issue.number}: {issue.title}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Search results */}
              {result.workflow_execution.results['brave-search'] && (
                <div>
                  <h3>Search Results</h3>
                  <p>Found solutions for {result.workflow_execution.results['brave-search'].total_searches} issues</p>
                </div>
              )}
              
              {/* Analysis */}
              {result.workflow_execution.results.analysis && (
                <div>
                  <h3>Analysis</h3>
                  <p>{result.workflow_execution.results.analysis.summary}</p>
                </div>
              )}
            </div>
          )}
          
          {/* 5. Show generated code */}
          <div>
            <h2>Generated Setup Code</h2>
            <pre>{result.code_snippet.markdown}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default MCPComposer;
```

---

## 📚 All Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| **`/api/v1/compose`** | **POST** | **All-in-one: Analysis + Recommendations + Cost + Execution** |
| `/api/v1/analyze` | POST | Capability analysis only |
| `/api/v1/recommend` | POST | MCP recommendations only |
| `/api/v1/generate` | POST | Code generation only |
| `/api/v1/call` | POST | Call specific MCP tool |
| `/api/v1/mcps` | GET | List all MCPs |
| `/api/v1/mcps/{mcp_id}` | GET | Get MCP details |
| **`/api/v1/templates`** | **GET** | **List workflow templates (NEW!)** |
| `/api/v1/templates/{id}` | GET | Get template details |
| **`/api/v1/estimate-cost`** | **POST** | **Cost estimation (NEW!)** |
| **`/api/v1/workflows/execute`** | **POST** | **Execute workflow template (NEW!)** |

---

## 💡 Best Practices

### 1. Use `/api/v1/compose` for most use cases
- Single API call
- Gets everything automatically
- Includes cost and execution results

### 2. Use templates for common scenarios
- Faster setup
- Pre-tested workflows
- Best practice examples

### 3. Check costs before scaling
- Use `/api/v1/estimate-cost`
- Plan your budget
- Optimize MCP selection

---

## 🚀 Quick Start

```bash
# Start API server
python api_server.py

# Open Swagger UI
http://localhost:8000/docs

# Try the compose endpoint with example request
```

---

**Now your API is truly Outstanding!** 🌟

One endpoint (`/api/v1/compose`) automatically:
- ✅ Analyzes requirements
- ✅ Recommends MCPs
- ✅ Generates code
- ✅ **Estimates costs**
- ✅ **Executes Multi-MCP workflow**
- ✅ **Returns actual results**

**From recommendation tool to orchestration platform!** 🚀

