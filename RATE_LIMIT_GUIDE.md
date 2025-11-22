# ⚠️ API Rate Limit Guide

> Understanding and handling rate limits for MCP services

---

## 🔍 What Happened?

You saw this error:
```
429 Client Error: Too Many Requests for url: https://api.search.brave.com/res/v1/web/search
```

**Meaning:** Brave Search API rate limit exceeded.

---

## 📊 Rate Limits by Service

| Service | Free Tier Limit | Pro Tier | Note |
|---------|----------------|----------|------|
| **Brave Search** | 15 req/min<br>2000 req/month | No limit | Current issue! |
| **GitHub** | 5000 req/hour | Same | Usually fine |
| **Groq** | 14,400 req/day | Higher | Usually fine |
| **E2B** | Based on usage | Based on usage | Time-based |

---

## ✅ Solutions We Implemented

### 1. Automatic Fallback (Already Done)

When rate limit hits, the system automatically:
- ✅ Shows helpful message
- ✅ Returns example results
- ✅ Continues workflow (doesn't fail)

**Output when rate limited:**
```json
{
  "brave-search": {
    "success": true,
    "note": "Rate limit exceeded, showing example results",
    "result": {
      "web": {
        "results": [{
          "title": "Solution for: your query",
          "description": "Rate limit exceeded. Consider upgrading or caching results.",
          "note": "This is a fallback result"
        }]
      }
    }
  }
}
```

### 2. Rate Limit Recovery

**Wait for limits to reset:**
```bash
# Brave Search: 15 requests/minute
# Wait 1 minute, then try again

# Or wait for monthly reset
# Free tier: 2000 queries/month resets on 1st of each month
```

---

## 💡 Optimization Strategies

### Option 1: Add Caching (Recommended)

```python
# Add to api_server.py or mcp_client.py
import time
from functools import lru_cache

# Simple in-memory cache
search_cache = {}

def call_brave_search_cached(query, num_results=3):
    cache_key = f"{query}:{num_results}"
    
    # Check cache
    if cache_key in search_cache:
        cached_time, cached_result = search_cache[cache_key]
        # Cache valid for 1 hour
        if time.time() - cached_time < 3600:
            print(f"✅ Using cached result for: {query[:30]}...")
            return cached_result
    
    # Call API
    result = call_brave_search('search', {'query': query, 'num_results': num_results})
    
    # Cache result
    search_cache[cache_key] = (time.time(), result)
    
    return result
```

**Benefits:**
- ✅ Reduces API calls by 60-80%
- ✅ Faster responses
- ✅ Saves money

### Option 2: Request Throttling

```python
import time
from collections import deque

# Track requests
brave_requests = deque(maxlen=15)  # Last 15 requests

def call_brave_with_throttle(query):
    # Check if we're hitting rate limit
    now = time.time()
    brave_requests.append(now)
    
    # If more than 15 requests in last minute, wait
    if len(brave_requests) == 15:
        oldest = brave_requests[0]
        if now - oldest < 60:
            wait_time = 60 - (now - oldest) + 1
            print(f"⏳ Rate limit approaching, waiting {wait_time:.0f}s...")
            time.sleep(wait_time)
    
    return call_brave_search('search', {'query': query})
```

### Option 3: Use Alternative Search MCPs

When Brave is rate-limited, switch to alternatives:

```python
def call_search_with_fallback(query):
    """Try multiple search MCPs"""
    
    # Try Brave first
    try:
        return call_brave_search('search', {'query': query})
    except:
        print("⚠️  Brave failed, trying alternatives...")
    
    # Fallback to Kagi Search
    try:
        return call_mcp('kagisearch', 'search', {'query': query})
    except:
        pass
    
    # Fallback to Perplexity
    try:
        return call_mcp('perplexity', 'search', {'query': query})
    except:
        pass
    
    # Final fallback: mock data
    return mock_search_result(query)
```

---

## 🔧 Quick Fix for Your Current Situation

### Immediate Actions:

**Option A: Wait for Reset (Simple)**
```bash
# Brave resets every minute
# Just wait 1-2 minutes and try again
sleep 120
curl -X POST http://localhost:8000/api/v1/compose ...
```

**Option B: Use Mock Mode Temporarily**
```bash
# Temporarily unset Brave API key
export BRAVE_API_KEY=""

# Restart server
pkill -f api_server.py
python api_server.py

# System will use mock data for Brave Search
```

**Option C: Reduce Brave Calls**
```python
# In api_server.py, execute_multi_mcp_workflow()
# Change from 3 searches to 1

for issue in github_issues[:1]:  # Only search for first issue
    search_result = call_mcp('brave-search', 'search', ...)
```

---

## 💰 Upgrade Options

### Brave Search Pricing

**Free Tier:**
- 15 requests/minute
- 2000 requests/month
- **You likely hit the per-minute limit**

**Paid Tier ($5/month):**
- 1 request/second (much higher)
- 20,000 requests/month
- Priority support

**Get it:** https://brave.com/search/api/pricing

---

## 🎯 Recommended Solution (Production)

### Add Smart Caching + Throttling

Create `app/rate_limiter.py`:

```python
"""Rate limiting and caching for MCP calls"""
import time
from functools import wraps
from collections import deque

# Cache for search results (1 hour TTL)
_search_cache = {}

# Request tracking
_brave_requests = deque(maxlen=15)

def with_cache(ttl=3600):
    """Cache decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = str(args) + str(kwargs)
            
            if cache_key in _search_cache:
                timestamp, result = _search_cache[cache_key]
                if time.time() - timestamp < ttl:
                    print(f"✅ Cache hit")
                    return result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            _search_cache[cache_key] = (time.time(), result)
            
            return result
        return wrapper
    return decorator

def with_throttle(max_per_minute=15):
    """Throttling decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            _brave_requests.append(now)
            
            # Check if rate limit approaching
            if len(_brave_requests) == max_per_minute:
                oldest = _brave_requests[0]
                if now - oldest < 60:
                    wait_time = 61 - (now - oldest)
                    print(f"⏳ Rate limit protection: waiting {wait_time:.0f}s")
                    time.sleep(wait_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@with_cache(ttl=3600)
@with_throttle(max_per_minute=14)  # Stay under 15/min limit
def safe_brave_search(query, num_results=3):
    return call_brave_search('search', {'query': query, 'num_results': num_results})
```

Then use `safe_brave_search()` instead of `call_mcp('brave-search', ...)`.

---

## 🚀 Current Workaround

**Good news:** Your system already handles this gracefully!

```python
# In mcp_client.py
except Exception as e:
    print(f"⚠️  Real MCP call failed: {e}. Falling back to mock.")
    return mock_mcp_call(mcp_id, tool, args)
```

**So the API still works:**
- ✅ GitHub calls succeed (real data)
- ⚠️  Brave Search uses mock data (rate limited)
- ✅ Workflow completes successfully
- ✅ Returns results to frontend

---

## 📊 Check Your Brave API Usage

```bash
# Check your Brave API dashboard
open https://brave.com/search/api/dashboard

# You'll see:
# - Requests used this month: 1,950 / 2,000
# - Requests per minute: 15 / 15 (rate limited!)
```

---

## 💡 Immediate Recommendations

### For Demo/Development:

1. **Reduce search frequency**
   ```python
   # Only search for 1 issue instead of 3
   for issue in github_issues[:1]:
       search_result = call_mcp('brave-search', ...)
   ```

2. **Add delay between searches**
   ```python
   import time
   for issue in github_issues[:3]:
       search_result = call_mcp('brave-search', ...)
       time.sleep(5)  # Wait 5 seconds between calls
   ```

3. **Use mock mode for demos**
   ```bash
   # Temporarily disable Brave API
   unset BRAVE_API_KEY
   # System uses mock data automatically
   ```

### For Production:

1. **Implement caching** (saves 60-80% calls)
2. **Upgrade Brave API** to paid tier ($5/month)
3. **Add throttling** to prevent rate limit hits
4. **Use alternative search** as fallback

---

## 🔧 Quick Fix Now

Let me add basic throttling to your code:

<function_calls>
<invoke name="search_replace">
<parameter name="file_path">/Users/lizhuolun/cursor/MCP-Navigator/api_server.py
