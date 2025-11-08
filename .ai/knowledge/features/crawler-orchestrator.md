# CrawlerOrchestrator Function

**Type**: Azure Timer-Triggered Function with Queue Output
**Schedule**: Daily at 11:00 UTC (CRON: `0 0 11 * * *`)
**Purpose**: Intelligent article discovery via Google search and queue distribution
**File**: `CrawlerOrchestrator/__init__.py`

---

## Overview

CrawlerOrchestrator is a timer-triggered Azure Function that discovers new articles based on user topics using Google Custom Search API. It delegates the core orchestration logic to a shared module and outputs discovered URLs to an Azure Storage Queue for processing by CrawlerWorker functions. This implements a fan-out pattern for distributed web crawling.

---

## What It Does

1. **Invokes Shared Orchestration Logic** via `find_new_articles()`
2. **Returns List of New URLs** to be crawled
3. **Outputs URLs to Queue** via Azure Functions queue binding
4. **Triggers CrawlerWorker Functions** (queue-triggered)

---

## Key Features

### Minimal Function Logic

Delegates to shared module for reusability:

```python
def main(timer: func.TimerRequest):
    load_dotenv()
    logger.info("CrawlerOrchestrator function executing via timer trigger.")

    new_urls = find_new_articles()

    return new_urls
```

**Why This Pattern?**
- Core logic in `shared/orchestration_logic.py` can be reused by `ManualTrigger`
- Function file only handles trigger-specific concerns
- Easier to test shared logic independently

### Queue Output Binding

Automatically sends URLs to queue via function return value:

**Configuration** (`function.json`):
```json
{
  "name": "$return",
  "type": "queue",
  "direction": "out",
  "queueName": "crawling-tasks-queue",
  "connection": "UP2D8_STORAGE_CONNECTION_STRING"
}
```

**Behavior**:
- Function returns `list[str]` of URLs
- Azure Functions runtime sends each URL as a separate queue message
- No manual queue client code needed in orchestrator

---

## Configuration

### Environment Variables
- Loaded via `dotenv` from `.env` file
- Passed through to `find_new_articles()`

### Secrets & Settings
- Handled by `shared/orchestration_logic.py`
- See [orchestration_logic.py documentation](../components/orchestration-logic.md)

### Trigger Schedule
- **CRON Expression**: `0 0 11 * * *`
- **Human Readable**: Daily at 11:00 UTC
- **Rationale**: Runs after morning scraping/newsletters to discover trending content
- **Defined In**: `CrawlerOrchestrator/function.json`

### Queue Configuration
- **Queue Name**: `crawling-tasks-queue`
- **Connection String**: From `UP2D8_STORAGE_CONNECTION_STRING` environment variable
- **Message Format**: Plain text URL (one per message)

---

## Function Bindings

### Input Binding (Timer)
```json
{
  "name": "timer",
  "type": "timerTrigger",
  "direction": "in",
  "schedule": "0 0 11 * * *"
}
```

### Output Binding (Queue)
```json
{
  "name": "$return",
  "type": "queue",
  "direction": "out",
  "queueName": "crawling-tasks-queue",
  "connection": "UP2D8_STORAGE_CONNECTION_STRING"
}
```

**Important**: The `$return` binding means the function's return value is sent to the queue.

---

## Error Handling

All error handling delegated to `find_new_articles()`:
- Returns empty list `[]` on errors
- Logs errors via `structlog`
- Function completes successfully even if no URLs found

---

## Logging

Uses **structured logging** with `structlog`:

```python
from shared.logger_config import configure_logger
configure_logger()
logger = structlog.get_logger()
```

**Key Log Events**:
- Function start: `"CrawlerOrchestrator function executing via timer trigger."`
- Detailed logging in `shared/orchestration_logic.py`

---

## Dependencies

**Core Libraries**:
- `azure.functions` - Azure Functions runtime
- `structlog` - Structured logging
- `python-dotenv` - Environment configuration

**Shared Modules**:
- `shared.orchestration_logic.find_new_articles()` - Core orchestration logic
- `shared.logger_config.configure_logger()` - Logging setup

---

## Workflow

```
Timer Trigger (11:00 UTC)
    ↓
Load Environment (.env)
    ↓
Log Function Start
    ↓
Call find_new_articles()
    ├─ Fetch user topics from Cosmos DB
    ├─ Search Google for articles
    ├─ Deduplicate against existing articles
    └─ Return list of new URLs
    ↓
Return URLs (function return value)
    ↓
Azure Functions Runtime:
    └─ For each URL:
        └─ Send message to crawling-tasks-queue
    ↓
CrawlerWorker Functions Triggered
    └─ One function instance per URL
    ↓
Function Complete
```

---

## Usage Context

**Runs At**: 11:00 UTC (after morning scraping & newsletters)
**Data Flow**: User Topics → Google Search → Queue → CrawlerWorker
**Purpose**: Discover trending articles beyond RSS feeds
**Complements**: `DailyArticleScraper` (RSS-based discovery)

---

## Integration Points

### Upstream Dependencies

**Cosmos DB - Users Collection**:
```javascript
{
    topics: ["AI", "machine learning", "startups"]
}
```

Used by `find_new_articles()` to determine search queries.

### Downstream Consumers

**Azure Storage Queue**: `crawling-tasks-queue`
- Receives URL strings as messages
- Triggers `CrawlerWorker` function for each URL

**CrawlerWorker Function**:
- Queue-triggered for each URL
- Crawls webpage with Playwright
- Extracts content and stores in Cosmos DB

---

## Design Pattern: Fan-Out

This function implements a **fan-out pattern**:

```
1 Orchestrator
    ↓
N Queue Messages (URLs)
    ↓
N CrawlerWorker Instances (parallel)
```

**Benefits**:
- Parallel processing of URLs
- Automatic scaling (Azure Functions scales workers)
- Decoupled components (orchestrator doesn't know about workers)
- Resilience (individual crawl failures don't affect others)

---

## Comparison: Orchestrator vs ManualTrigger

| Aspect | CrawlerOrchestrator | ManualTrigger |
|--------|---------------------|---------------|
| Trigger | Timer (daily) | HTTP (on-demand) |
| Queue Output | Automatic (binding) | Manual (SDK) |
| Use Case | Scheduled discovery | Testing, manual runs |
| Shared Logic | ✅ `find_new_articles()` | ✅ `find_new_articles()` |

Both use the same core logic but different triggers and queue mechanisms.

---

## Performance Considerations

- **Lightweight Function**: Minimal processing, delegates to shared module
- **Queue Binding**: No explicit queue client overhead
- **Automatic Scaling**: CrawlerWorker instances scale based on queue depth
- **Execution Time**: Depends on `find_new_articles()` (Google API calls, DB queries)

**Typical Runtime**:
- Search 10 topics × 5 results = 50 URLs
- Deduplication against DB
- ~10-30 seconds total orchestration time

---

## Potential Improvements

1. **Conditional Execution**: Skip if no users have topics defined
2. **Rate Limit Awareness**: Check Google API quota before running
3. **Priority Queuing**: High-priority topics to separate queue
4. **Metrics Tracking**: Store orchestration metrics (URLs found, duplicates, etc.)
5. **Batching**: Group URLs into batches for worker efficiency
6. **Dead Letter Queue**: Handle permanently failing URLs
7. **Schedule Flexibility**: User-configurable run times

---

## Testing

**Manual Testing**:
1. Use `ManualTrigger` to test logic without waiting for timer
2. Monitor `crawling-tasks-queue` depth in Azure portal
3. Check CrawlerWorker logs for processing confirmation

**Local Testing**:
```bash
func start
# Wait for timer or invoke manually
```

---

## Monitoring

**Key Metrics**:
- Function execution count (should be ~1/day)
- Queue messages sent (URLs discovered)
- Execution duration
- Error rate from `find_new_articles()`

**Azure Portal**:
- Function App → CrawlerOrchestrator → Monitor
- Storage Account → Queues → crawling-tasks-queue (message count)
- Application Insights (if enabled)

---

## Related Documentation

- [orchestration_logic.py](../components/orchestration-logic.md) - Shared orchestration implementation
- [CrawlerWorker](./crawler-worker.md) - Queue-triggered worker function
- [ManualTrigger](./manual-trigger.md) - HTTP-triggered alternative
- [Fan-Out Pattern](../patterns/fan-out-pattern.md) - Design pattern explanation

---

**Last Updated**: 2025-11-08
**Status**: Active, Production
