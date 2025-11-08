# ManualTrigger Function

**Type**: Azure HTTP-Triggered Function
**Trigger**: HTTP POST/GET request
**Purpose**: On-demand article discovery and queue distribution
**File**: `ManualTrigger/__init__.py`

---

## Overview

ManualTrigger is an HTTP-triggered Azure Function that provides on-demand execution of the crawler orchestration logic. It shares the same core logic as CrawlerOrchestrator but is invoked via HTTP requests instead of a timer. This enables manual testing, debugging, and ad-hoc article discovery without waiting for scheduled runs.

---

## What It Does

1. **Receives HTTP Request** (GET or POST)
2. **Invokes Shared Orchestration Logic** via `find_new_articles()`
3. **Manually Queues URLs** using Azure Storage Queue SDK
4. **Returns HTTP Response** with count of queued URLs

---

## Key Features

### HTTP-Triggered Execution

Provides RESTful interface for orchestration:

```python
def main(req: func.HttpRequest) -> func.HttpResponse:
    new_urls = find_new_articles()
    # ... queue URLs ...
    return func.HttpResponse(f"Orchestration complete. Found and queued {queued_count} new URLs for crawling.", status_code=200)
```

**Use Cases**:
- Manual testing during development
- Debugging orchestration logic
- Forcing immediate crawl without waiting for timer
- Admin/operator-triggered discovery

### Shared Core Logic

Reuses `find_new_articles()` from `shared/orchestration_logic.py`:

```python
from shared.orchestration_logic import find_new_articles

new_urls = find_new_articles()
```

**Benefits**:
- DRY principle (Don't Repeat Yourself)
- Consistent behavior with CrawlerOrchestrator
- Single source of truth for orchestration logic
- Easier testing and maintenance

### Explicit Queue Client

Unlike CrawlerOrchestrator (which uses queue output binding), ManualTrigger explicitly manages queue operations:

```python
from azure.storage.queue import QueueClient, TextBase64EncodePolicy

connection_string = os.getenv("UP2D8_STORAGE_CONNECTION_STRING")
queue_client = QueueClient.from_connection_string(
    conn_str=connection_string,
    queue_name="crawling-tasks-queue",
    message_encode_policy=TextBase64EncodePolicy()
)

for url in new_urls:
    queue_client.send_message(url)
    queued_count += 1
```

**Why Explicit?**
- HTTP functions don't support queue output bindings on return value
- Provides more control over queue operations
- Enables detailed error handling per message

### TextBase64EncodePolicy

Encodes messages in Base64 (recommended by Azure):

```python
message_encode_policy=TextBase64EncodePolicy()
```

**Why?**
- Prevents issues with special characters in URLs
- Compatible with Azure Functions queue trigger
- Azure best practice for text messages

---

## HTTP Interface

### Endpoint
```
POST /api/ManualTrigger
GET /api/ManualTrigger
```

**Note**: Default Azure Functions HTTP endpoint path is `/api/{function_name}`

### Request
- **Method**: GET or POST (both supported)
- **Headers**: None required
- **Body**: None required (orchestration logic uses Cosmos DB for topics)

### Response

**Success** (200 OK):
```
Orchestration complete. Found and queued 15 new URLs for crawling.
```

**Error - Missing Connection String** (500 Internal Server Error):
```
Error: Orchestration ran, but failed to queue messages for crawling.
```

**Error - Queue Send Failure** (500 Internal Server Error):
```
Error: Orchestration ran, but failed to queue messages for crawling.
```

---

## Configuration

### Environment Variables

**Required**:
- `UP2D8_STORAGE_CONNECTION_STRING` - Azure Storage connection string for queue access

**Optional** (loaded by `dotenv`):
- Other environment variables used by `find_new_articles()`

### Secrets
- Handled by `shared/orchestration_logic.py`
- See [orchestration_logic.py documentation](../components/orchestration-logic.md)

### HTTP Configuration
- **Authorization**: None (⚠️ Security concern, see improvements)
- **Methods**: All (GET, POST, PUT, etc.)
- **Route**: Default `/api/ManualTrigger`

---

## Error Handling

### Missing Connection String

```python
connection_string = os.getenv("UP2D8_STORAGE_CONNECTION_STRING")
if not connection_string:
    raise ValueError("UP2D8_STORAGE_CONNECTION_STRING is not set.")
```

Returns 500 error with message.

### Queue Send Failures

```python
try:
    for url in new_urls:
        queue_client.send_message(url)
        queued_count += 1
    logger.info("Successfully sent messages to the queue", count=queued_count)
except Exception as e:
    logger.error("Failed to send messages to queue", error=str(e))
    return func.HttpResponse(
        "Error: Orchestration ran, but failed to queue messages for crawling.",
        status_code=500
    )
```

Catches and reports queue operation failures.

### Orchestration Errors

Handled by `find_new_articles()`:
- Returns empty list on errors
- Errors logged but don't fail HTTP request
- HTTP response shows `0` queued URLs

---

## Logging

Uses **structured logging** with `structlog`:

```python
logger = structlog.get_logger()
logger.info("ManualTrigger function executing via HTTP trigger.")
logger.info("Successfully sent messages to the queue", count=queued_count)
logger.error("Failed to send messages to queue", error=str(e))
```

**Key Log Events**:
- HTTP trigger execution
- Successful queue message sending
- Queue operation failures

---

## Dependencies

**Core Libraries**:
- `azure.functions` - Azure Functions runtime
- `azure.storage.queue` - Queue client SDK
- `structlog` - Structured logging
- `python-dotenv` - Environment configuration

**Shared Modules**:
- `shared.orchestration_logic.find_new_articles()` - Core logic
- `shared.logger_config.configure_logger()` - Logging setup

---

## Workflow

```
HTTP Request Received
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
If URLs Found:
    ├─ Get Storage Connection String
    ├─ Create Queue Client
    ├─ For each URL:
    │   └─ Send message to queue
    │       └─ Increment queued_count
    └─ Log success
    ↓
Return HTTP Response
    └─ Status: 200
    └─ Body: "Orchestration complete. Found and queued {count} new URLs for crawling."
    ↓
Function Complete
```

---

## Usage Context

**Trigger**: On-demand via HTTP
**Data Flow**: HTTP Request → Google Search → Queue → CrawlerWorker
**Purpose**: Manual/ad-hoc article discovery
**Alternative To**: `CrawlerOrchestrator` (timer-triggered)

---

## Comparison: ManualTrigger vs CrawlerOrchestrator

| Aspect | ManualTrigger | CrawlerOrchestrator |
|--------|---------------|---------------------|
| **Trigger** | HTTP (on-demand) | Timer (scheduled) |
| **Invocation** | Manual/API call | Automatic (daily) |
| **Queue Output** | Explicit SDK | Automatic binding |
| **Error Response** | HTTP 500 | Logged only |
| **Use Case** | Testing, debugging | Production automation |
| **Shared Logic** | ✅ `find_new_articles()` | ✅ `find_new_articles()` |
| **Authorization** | ❌ None (security risk) | N/A (timer) |

---

## Integration Points

### HTTP Clients

**Direct API Call**:
```bash
curl -X POST https://<your-function-app>.azurewebsites.net/api/ManualTrigger
```

**Python**:
```python
import requests
response = requests.post("https://<app>.azurewebsites.net/api/ManualTrigger")
print(response.text)  # "Orchestration complete. Found and queued 15 new URLs..."
```

**JavaScript/Node.js**:
```javascript
fetch('https://<app>.azurewebsites.net/api/ManualTrigger', { method: 'POST' })
    .then(res => res.text())
    .then(console.log);
```

### Queue Output

Same as CrawlerOrchestrator:
- **Queue**: `crawling-tasks-queue`
- **Message Format**: URL strings
- **Consumer**: `CrawlerWorker` function

---

## Security Considerations

### ⚠️ Current State: No Authentication

Function is publicly accessible:
- Anyone with URL can trigger orchestration
- No API key required
- No authentication mechanism

### Recommended Improvements

1. **Function Key Authentication**:
```python
# Azure automatically checks function key if configured
# No code changes needed, configure in Azure Portal
```

Access with key:
```bash
curl -X POST "https://<app>.azurewebsites.net/api/ManualTrigger?code=<function-key>"
```

2. **Azure AD Authentication**:
```python
# Require Azure AD token
# Configure in function.json
{
    "authLevel": "anonymous",  # Change to "function" or use Azure AD
}
```

3. **IP Whitelisting**:
Configure in Azure Function App networking settings.

4. **Request Validation**:
```python
# Validate request headers/body
api_key = req.headers.get('X-API-Key')
if api_key != expected_key:
    return func.HttpResponse("Unauthorized", status_code=401)
```

---

## Performance Considerations

### Synchronous Execution

HTTP request waits for entire orchestration to complete:
- Google search API calls
- Cosmos DB queries
- Queue message sending

**Typical Duration**: 10-30 seconds

### Alternative: Async Pattern

For better UX, consider:
```python
# Immediately return, process in background
return func.HttpResponse("Orchestration started", status_code=202)
# Process in separate thread/task
```

---

## Testing

### Local Development

```bash
# Start function locally
func start

# Trigger via HTTP
curl http://localhost:7071/api/ManualTrigger
```

### Production Testing

```bash
# Replace with your function app URL
curl -X POST https://your-app.azurewebsites.net/api/ManualTrigger
```

### Monitoring Results

1. **Check HTTP Response**: Should show count of queued URLs
2. **Monitor Queue**: Check `crawling-tasks-queue` depth in Azure Portal
3. **Watch CrawlerWorker Logs**: Verify workers are processing URLs
4. **Query Cosmos DB**: Confirm new articles appear in `articles` collection

---

## Potential Improvements

### 1. Enhanced HTTP Interface

**Request Body Parameters**:
```python
req_body = req.get_json()
topics = req_body.get('topics', [])  # Custom topics instead of DB fetch
max_results = req_body.get('max_results', 5)  # Configurable result count
```

**Response JSON**:
```python
return func.HttpResponse(
    json.dumps({
        "status": "success",
        "urls_found": len(new_urls),
        "urls_queued": queued_count,
        "urls": new_urls[:10]  # Sample of URLs
    }),
    mimetype="application/json"
)
```

### 2. Asynchronous Processing

```python
import asyncio

async def orchestrate_async():
    # Run orchestration in background
    pass

# Return immediately
return func.HttpResponse("Orchestration started", status_code=202)
```

### 3. Rate Limiting

Prevent abuse:
```python
# Check last execution time
if time_since_last_run < 60:  # 1 minute cooldown
    return func.HttpResponse("Rate limited", status_code=429)
```

### 4. Webhook Callbacks

Notify completion:
```python
webhook_url = req.params.get('webhook')
# After orchestration
requests.post(webhook_url, json={"status": "complete", "count": queued_count})
```

### 5. Dry Run Mode

Test without queuing:
```python
dry_run = req.params.get('dry_run', 'false') == 'true'
if not dry_run:
    queue_client.send_message(url)
```

---

## Use Cases

### Development
- Test orchestration logic changes
- Verify Google Search API configuration
- Debug queue message format

### Operations
- Force immediate crawl after adding new user topics
- Recover from scheduled run failures
- Populate database with initial content

### Integration
- Trigger from admin dashboard
- Integrate with external workflows
- Part of CI/CD pipelines

---

## Related Documentation

- [CrawlerOrchestrator](./crawler-orchestrator.md) - Timer-triggered equivalent
- [orchestration_logic.py](../components/orchestration-logic.md) - Shared core logic
- [CrawlerWorker](./crawler-worker.md) - Queue consumer
- [HTTP Trigger Pattern](../patterns/http-trigger.md) - Azure Functions HTTP patterns

---

**Last Updated**: 2025-11-08
**Status**: Active, Production (⚠️ Security improvement needed)
