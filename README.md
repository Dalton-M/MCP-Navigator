# MCP Stack Composer

> 🚀 An intelligent orchestrator that recommends and wires MCP (Model Context Protocol) servers based on natural language requirements.

## Overview

MCP Stack Composer is a hackathon project that demonstrates the power of combining:
- **E2B** (cloud sandbox environment)
- **Docker MCP Hub** (containerized MCP servers)
- **Groq** (fast LLM inference for capability analysis and code generation)
- **Multiple MCPs** (GitHub, Brave Search, Stripe, etc.)

## Features

1. **Natural Language → Capabilities**: Describe your agent in plain English, get structured capability tags via Groq
2. **Smart MCP Matching**: Automatically match your needs to the right MCP servers from Docker Hub
3. **Code Generation**: Get ready-to-use configuration and code snippets
4. **Live Demo**: Real MCP calls to demonstrate actual integration

## Quick Start

### Prerequisites

- Python 3.9+
- Docker Desktop (optional, for running real MCP servers)
- Groq API Key (free tier: https://console.groq.com/)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd MCP-Navigator

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Run (Mock Mode)

```bash
python app/main.py
```

Example input:
```
I want an agent that reads GitHub issues, searches the web for similar solutions, and posts a daily summary.
```

## Project Structure

```
MCP-Navigator/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   └── mcp_catalog.json      # MCP catalog with capabilities
├── app/
│   ├── main.py               # CLI entry point
│   ├── config.py             # Configuration management
│   ├── planner.py            # Groq: requirements → capabilities
│   ├── matcher.py            # MCP matching logic
│   ├── snippet_generator.py  # Groq: generate config & code
│   └── mcp_client.py         # MCP invocation wrapper
└── tests/
    └── test_data/            # Mock response data
```

## How It Works

1. **User Input**: Describe your agent's requirements in natural language
2. **Capability Extraction**: Groq analyzes the description and outputs standardized capability tags
3. **MCP Matching**: Rule-based algorithm matches capabilities to MCP servers
4. **Code Generation**: Groq generates environment setup instructions and code snippets
5. **Live Demo**: Execute a real MCP call to demonstrate integration

## API Keys Required

### Essential
- **Groq API Key**: For LLM-based analysis and code generation
  - Register at: https://console.groq.com/
  - Free tier: 14,400 requests/day

### For Demo (at least 1)
- **GitHub Token**: For code hosting capabilities
  - Get at: https://github.com/settings/tokens
  - Scopes: `repo`, `read:org`
  
- **Brave Search API**: For web search capabilities
  - Register at: https://brave.com/search/api/
  - Free tier: 2,000 queries/month

## Deployment to E2B

1. Create an E2B account at https://e2b.dev/
2. Create a new Python Sandbox
3. Configure environment variables in E2B UI
4. Clone repo and run:

```bash
git clone <your-repo-url>
cd MCP-Navigator
pip install -r requirements.txt
python app/main.py
```

## Supported MCPs

- GitHub (code hosting, issue management)
- Brave Search (web search)
- Stripe (payment processing)
- MongoDB (database operations)
- Notion (productivity & notes)
- Elasticsearch (full-text search)
- Playwright (browser automation)
- Perplexity (web research)

## License

MIT

## Hackathon Credits

Built for [Hackathon Name] demonstrating:
- E2B cloud sandbox
- Docker MCP Hub integration
- Groq LLM capabilities
- Real MCP server orchestration

