# Orchestration Logic - Shared Module

**Type**: Shared Python Module
**Purpose**: Reusable article discovery logic for orchestrator functions
**File**: `shared/orchestration_logic.py`

---

## Overview

`orchestration_logic.py` contains the core business logic for intelligent article discovery. It provides the `find_new_articles()` function that is shared between `CrawlerOrchestrator` (timer-triggered) and `ManualTrigger` (HTTP-triggered) functions. This module implements the complete workflow: fetching user topics, searching Google, and deduplicating against existing articles.

---

## Core Function: `find_new_articles()`

**Signature**:
```python
def find_new_articles() -> list[str]:
```

**Returns**: List of unique URLs to crawl (empty list on errors)

**Purpose**:
- Aggregate all user topics from Cosmos DB
- Search Google for latest articles on each topic
- Deduplicate against existing articles in database
- Return new URLs ready for crawling

---

## What It Does

1. **Retrieves Configuration** from Key Vault and environment
2. **Connects to Cosmos DB** to access user and article data
3. **Aggregates User Topics** across all users
4. **Searches Google** for articles on each topic
5. **Deduplicates URLs** against existing articles
6. **Returns New URLs** for crawling

---

## Detailed Workflow

### 1. Configuration Retrieval

```python
secret_client = get_secret_client()

cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
google_api_key = secret_client.get_secret("GOOGLE-CUSTOM-SEARCH-API").value
google_cse_id = os.getenv("GOOGLE_CSE_ID")
```

**Sources**:
- **Key Vault**: Cosmos DB connection, Google API key (sensitive)
- **Environment**: Google Custom Search Engine ID (non-sensitive)

**Validation**:
```python
if not google_cse_id:
    logger.warning("GOOGLE_CSE_ID is not set. Orchestration cannot run.")
    return []
```

### 2. Environment Setup for Google Search

```python
os.environ["GOOGLE_API_KEY"] = google_api_key
os.environ["GOOGLE_CSE_ID"] = google_cse_id
```

**Why?** LangChain's `GoogleSearchAPIWrapper` reads from environment variables.

### 3. User Topic Aggregation

```python
all_topics = set()
for user in users_collection.find({}, {"topics": 1}):
    for topic in user.get("topics", []):
        all_topics.add(topic)

if not all_topics:
    logger.warning("No user topics found. Orchestrator finished without searching.")
    return []
```

**Logic**:
- Query all users, project only `topics` field
- Use `set()` to deduplicate topics across users
- Multiple users with same topic → searched once
- Early exit if no topics configured

**Example**:
```javascript
// User 1
{ topics: ["AI", "startups"] }

// User 2
{ topics: ["AI", "climate tech"] }

// Aggregated
all_topics = {"AI", "startups", "climate tech"}  // 3 unique topics
```

### 4. Google Search Execution

```python
search = GoogleSearchAPIWrapper()
all_found_urls = set()

for topic in all_topics:
    logger.info("Searching for articles", topic=topic)
    try:
        search_results = search.results(f"latest articles about {topic}", num_results=5)
        for res in search_results:
            if "link" in res:
                all_found_urls.add(res["link"])
    except Exception as e:
        logger.error("Error during search for topic", topic=topic, error=str(e))
```

**Search Configuration**:
- **Query Template**: `"latest articles about {topic}"`
- **Results per Topic**: 5 URLs
- **Error Handling**: Skip failed topics, continue with others

**LangChain Integration**:
- Uses `GoogleSearchAPIWrapper` from `langchain_community.utilities`
- Returns list of result dictionaries with `link`, `title`, `snippet` fields

**URL Deduplication**:
- Uses `set()` to automatically deduplicate URLs across topics
- Same article appearing in multiple searches → counted once

### 5. Database Deduplication

```python
existing_links = {
    article["link"]
    for article in articles_collection.find(
        {"link": {"$in": list(all_found_urls)}},
        {"link": 1}
    )
}

logger.info("Found existing articles in DB", count=len(existing_links))

new_urls_to_crawl = list(all_found_urls - existing_links)

logger.info("Queuing new URLs for crawling", count=len(new_urls_to_crawl))
```

**Process**:
1. Query Cosmos DB for articles with URLs in search results
2. Extract just the `link` field (projection for efficiency)
3. Create set of existing links
4. Set difference: `all_found_urls - existing_links` = new URLs
5. Convert to list for return

**Efficiency**:
- Single DB query with `$in` operator (batch lookup)
- Projection (`{"link": 1}`) reduces data transfer
- Set operations are O(1) average case

---

## Configuration Requirements

### Environment Variables

**Required**:
- `GOOGLE_CSE_ID` - Google Custom Search Engine ID

**Set Dynamically** (from Key Vault):
- `GOOGLE_API_KEY` - Set in function body for LangChain
- Note: These are temporary, function-scoped environment variables

### Azure Key Vault Secrets

**Required Secrets**:
- `COSMOS-DB-CONNECTION-STRING-UP2D8`
- `GOOGLE-CUSTOM-SEARCH-API`

**Retrieved via**:
```python
from shared.key_vault_client import get_secret_client
secret_client = get_secret_client()
```

### Google Custom Search API Setup

**Prerequisites**:
1. Google Cloud Project with Custom Search API enabled
2. API Key created in Google Cloud Console
3. Custom Search Engine (CSE) created at https://cse.google.com/
4. CSE configured to search entire web (not specific sites)

**API Limits**:
- Free tier: 100 queries/day
- Paid: Up to 10,000 queries/day
- Consider: With 10 topics × 5 results, uses 10 queries per run

---

## Error Handling

### Missing Configuration

```python
if not google_cse_id:
    logger.warning("GOOGLE_CSE_ID is not set. Orchestration cannot run.")
    return []
```

Returns empty list, allowing calling function to complete successfully.

### No User Topics

```python
if not all_topics:
    logger.warning("No user topics found. Orchestrator finished without searching.")
    return []
```

Graceful exit when no topics configured.

### Search API Failures

```python
try:
    search_results = search.results(f"latest articles about {topic}", num_results=5)
    # ... process results ...
except Exception as e:
    logger.error("Error during search for topic", topic=topic, error=str(e))
```

**Behavior**:
- Skip failed topic
- Continue with remaining topics
- Partial results returned

**Possible Errors**:
- API quota exceeded
- Network failures
- Invalid API credentials
- Rate limiting

### No Search Results

```python
if not all_found_urls:
    logger.warning("Search did not return any URLs.")
    return []
```

Handles case where all searches return empty results.

### Unexpected Errors

```python
except Exception as e:
    logger.error("An unexpected error occurred in orchestration logic", error=str(e))
    return []
```

Top-level catch-all prevents function crashes.

---

## Logging

Uses **structured logging** with `structlog`:

```python
import structlog
logger = structlog.get_logger()
```

**Key Log Events**:

**Info Level**:
- `"Found unique user topics"` - Lists aggregated topics
- `"Searching for articles"` - Per-topic search start
- `"Found total URLs from search"` - Search result count
- `"Found existing articles in DB"` - Deduplication count
- `"Queuing new URLs for crawling"` - Final new URL count

**Warning Level**:
- `"GOOGLE_CSE_ID is not set"` - Missing configuration
- `"No user topics found"` - No topics in database
- `"Search did not return any URLs"` - Empty search results

**Error Level**:
- `"Error during search for topic"` - Per-topic search failures
- `"An unexpected error occurred in orchestration logic"` - Unexpected exceptions

**Example Log Output**:
```python
logger.info("Found unique user topics", topics=["AI", "startups", "climate tech"])
logger.info("Searching for articles", topic="AI")
logger.info("Found total URLs from search", count=15)
logger.info("Found existing articles in DB", count=3)
logger.info("Queuing new URLs for crawling", count=12)
```

---

## Dependencies

**Core Libraries**:
- `pymongo` - Cosmos DB access
- `langchain_community.utilities.GoogleSearchAPIWrapper` - Google search integration
- `structlog` - Structured logging
- `os` - Environment variable access

**Shared Modules**:
- `shared.key_vault_client.get_secret_client()` - Key Vault integration

**External APIs**:
- Google Custom Search API
- Azure Cosmos DB (MongoDB API)
- Azure Key Vault

---

## Data Models

### User Document (Cosmos DB)

**Collection**: `users`

**Schema** (relevant fields):
```javascript
{
    topics: ["string", "array"],  // User's interests
    // ... other user fields ...
}
```

**Example**:
```javascript
{
    email: "user@example.com",
    topics: ["artificial intelligence", "robotics", "quantum computing"],
    subscribed_tags: ["AI", "Tech"],
    preferences: "detailed"
}
```

### Article Document (Cosmos DB)

**Collection**: `articles`

**Schema** (relevant fields):
```javascript
{
    link: "string"  // Unique URL, indexed
}
```

**Example**:
```javascript
{
    title: "Latest AI Breakthrough",
    link: "https://example.com/article",
    // ... other article fields ...
}
```

### Google Search Result

**Format** (from LangChain):
```python
{
    "link": "https://example.com/article",
    "title": "Article Title",
    "snippet": "Preview text..."
}
```

Only `link` field is used in current implementation.

---

## Performance Characteristics

### Time Complexity
- **User topic aggregation**: O(n × m) where n=users, m=avg topics per user
- **Search**: O(t × k) where t=unique topics, k=results per topic (API latency)
- **Deduplication**: O(r) where r=total search results (set operations)
- **Overall**: Dominated by API calls (~2-5 seconds per search)

### Space Complexity
- **all_topics**: O(t) for unique topics
- **all_found_urls**: O(r) for search results
- **existing_links**: O(e) for existing articles
- **Overall**: O(r) in most cases

### API Usage
- **Cosmos DB Queries**: 2 (users, articles)
- **Google Search API Calls**: 1 per unique topic
- **Example**: 10 topics = 10 API calls

### Estimated Runtime
- **10 topics × 5 results**:
  - User query: ~0.5s
  - Searches: ~20s (2s per topic)
  - Deduplication: ~0.5s
  - **Total**: ~20-25 seconds

---

## Integration Points

### Consumers

**CrawlerOrchestrator** (Timer-Triggered):
```python
new_urls = find_new_articles()
return new_urls  # Sent to queue via binding
```

**ManualTrigger** (HTTP-Triggered):
```python
new_urls = find_new_articles()
for url in new_urls:
    queue_client.send_message(url)
```

### External Services

**Google Custom Search API**:
- Searches entire web (configurable in CSE settings)
- Returns top results for each query
- Rate limits apply (check quota)

**Cosmos DB**:
- Reads user topics
- Queries existing articles for deduplication

---

## Testing

### Unit Testing

Mock external dependencies:

```python
from unittest.mock import Mock, patch

@patch('shared.orchestration_logic.get_secret_client')
@patch('shared.orchestration_logic.GoogleSearchAPIWrapper')
@patch('pymongo.MongoClient')
def test_find_new_articles(mock_mongo, mock_search, mock_kv):
    # Mock setup
    mock_search.return_value.results.return_value = [
        {"link": "http://example.com/1"}
    ]

    # Execute
    urls = find_new_articles()

    # Assert
    assert "http://example.com/1" in urls
```

### Integration Testing

Test with real services (dev environment):

```python
# Set environment variables
os.environ["GOOGLE_CSE_ID"] = "dev-cse-id"

# Call function
urls = find_new_articles()

# Verify
assert isinstance(urls, list)
assert all(url.startswith("http") for url in urls)
```

### Local Testing

```python
# In separate test file
from shared.orchestration_logic import find_new_articles

if __name__ == "__main__":
    urls = find_new_articles()
    print(f"Found {len(urls)} URLs:")
    for url in urls[:10]:  # Print first 10
        print(f"  - {url}")
```

---

## Potential Improvements

### 1. Advanced Search Queries

**Date Filtering**:
```python
query = f"latest articles about {topic} after:2025-01-01"
```

**Site Restrictions**:
```python
query = f"{topic} site:techcrunch.com OR site:wired.com"
```

### 2. Caching

Avoid redundant searches:
```python
# Cache search results for X hours
cache_key = f"search_{topic}_{date.today()}"
if cache_key in cache:
    return cache[cache_key]
```

### 3. Parallel Searching

Speed up multiple topic searches:
```python
import asyncio
from langchain.utilities import GoogleSearchAPIWrapper

async def search_topic(topic):
    # Async search implementation
    pass

results = await asyncio.gather(*[search_topic(t) for t in all_topics])
```

### 4. Smart Topic Expansion

Use AI to expand/relate topics:
```python
# "AI" → ["artificial intelligence", "machine learning", "neural networks"]
expanded_topics = expand_with_ai(topic)
```

### 5. Result Ranking

Prioritize high-quality sources:
```python
# Score results by domain authority, recency, relevance
ranked_urls = rank_search_results(search_results)
```

### 6. Configurable Results Count

Per-topic result limits:
```python
def find_new_articles(results_per_topic: int = 5):
    search_results = search.results(query, num_results=results_per_topic)
```

### 7. Content Filtering

Filter out known low-quality domains:
```python
blacklist = ["example-spam-site.com"]
urls = [url for url in urls if not any(domain in url for domain in blacklist)]
```

### 8. Quota Management

Track and limit API usage:
```python
if daily_search_count >= quota_limit:
    logger.warning("Google API quota limit reached")
    return []
```

---

## Cost Considerations

### Google Custom Search API

**Free Tier**:
- 100 queries/day
- $5/1000 queries after free tier

**Example**:
- 10 topics × 1 run/day = 10 queries/day (within free tier)
- 50 topics × 3 runs/day = 150 queries/day ($0.25/day = ~$7.50/month)

**Optimization**:
- Cache results
- Deduplicate topics before searching
- Limit results per topic
- Schedule runs strategically

### Cosmos DB

**Request Units (RUs)**:
- User topic query: ~2-5 RUs
- Article deduplication query: ~5-10 RUs (depends on result count)

**Cost**: Minimal compared to search API

---

## Related Documentation

- [CrawlerOrchestrator](../features/crawler-orchestrator.md) - Timer-triggered consumer
- [ManualTrigger](../features/manual-trigger.md) - HTTP-triggered consumer
- [GoogleSearchAPIWrapper](https://python.langchain.com/docs/integrations/tools/google_search) - LangChain docs
- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview) - Google docs

---

**Last Updated**: 2025-11-08
**Status**: Active, Production
