# CrawlerWorker Function

**Type**: Azure Queue-Triggered Function (Async)
**Trigger**: Messages on `crawling-tasks-queue`
**Purpose**: Headless browser-based web scraping and content extraction
**File**: `CrawlerWorker/__init__.py`

---

## Overview

CrawlerWorker is an asynchronous, queue-triggered Azure Function that processes individual URLs from the crawling queue. It uses Playwright for headless browser automation, BeautifulSoup for HTML parsing, and stores extracted article content in Cosmos DB. Each worker instance handles one URL, enabling parallel processing of multiple articles.

---

## What It Does

1. **Receives URL from Queue** via Azure Queue trigger
2. **Launches Headless Browser** using Playwright (Chromium)
3. **Fetches Page Content** with DOM load waiting
4. **Extracts Article Text** using BeautifulSoup heuristics
5. **Stores Article in Cosmos DB** with full content
6. **Prevents Duplicates** using unique index on link field

---

## Key Features

### Asynchronous Execution

Uses Python's `async/await` for efficient I/O handling:

```python
async def main(msg: func.QueueMessage) -> None:
```

**Benefits**:
- Non-blocking browser operations
- Better resource utilization
- Required by Playwright async API

### Headless Browser Automation

Uses **Playwright** for JavaScript-rendered pages:

```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
    html_content = await page.content()
    await browser.close()
```

**Why Playwright?**
- Handles JavaScript-heavy sites
- Waits for DOM content to load
- More reliable than simple HTTP requests
- Supports modern web standards

**Timeout**: 60 seconds (60000ms)

### Intelligent Content Extraction

Uses **BeautifulSoup** with heuristic-based article detection:

```python
# Try common article tags/selectors
for tag in ['article', 'main', '.post-content', '.article-body', '#content']:
    element = soup.select_one(tag)
    if element:
        article_text = element.get_text(separator='\n', strip=True)
        break

# Fallback to all text if no article element found
if not article_text:
    article_text = soup.get_text(separator='\n', strip=True)
```

**Extraction Strategy**:
1. Check semantic HTML tags: `<article>`, `<main>`
2. Check common CSS classes: `.post-content`, `.article-body`
3. Check common IDs: `#content`
4. Fallback: Extract all page text

### Summary Generation

Creates summary from first 15 lines:

```python
summary = ' '.join(article_text.splitlines()[:15]) + '...'
```

Simple but effective for preview purposes.

### Duplicate Prevention

Ensures articles aren't re-crawled:

```python
articles_collection.create_index([("link", pymongo.ASCENDING)], unique=True)

try:
    articles_collection.insert_one(article_doc)
except pymongo.errors.DuplicateKeyError:
    logger.warning("Article already exists, skipping.", link=url)
```

---

## Article Schema

Crawled articles have extended schema compared to RSS articles:

```python
{
    'title': str,                    # Extracted from <title> tag
    'link': str,                     # URL (unique identifier)
    'summary': str,                  # First 15 lines of content
    'published': str,                # ISO-8601 timestamp (UTC now)
    'processed': False,              # Flag for newsletter generation
    'source': 'intelligent_crawler', # Distinguishes from RSS articles
    'content': str                   # Full article text (not in RSS articles)
}
```

**Key Differences from RSS Articles**:
- No `tags` field (could be added via AI classification)
- Includes `source` field to track origin
- Includes full `content` for future analysis
- `published` is crawl time, not original publish date

---

## Configuration

### Environment Variables
- Loaded via `dotenv` from `.env` file

### Secrets from Azure Key Vault
- **`COSMOS-DB-CONNECTION-STRING-UP2D8`**: MongoDB connection string

### Queue Configuration
- **Queue Name**: `crawling-tasks-queue`
- **Connection String**: From `UP2D8_STORAGE_CONNECTION_STRING` environment variable
- **Message Format**: Plain text URL (UTF-8 encoded)
- **Defined In**: `CrawlerWorker/function.json`

---

## Error Handling

### Playwright Failures

```python
try:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(url, wait_until='domcontentloaded', timeout=60000)
    html_content = await page.content()
    await browser.close()
except Exception as e:
    logger.error("Playwright failed to get content", url=url, error=str(e))
    return  # Exit early, message removed from queue
```

**Failure Cases**:
- Timeout (page load > 60 seconds)
- Network errors
- Invalid URLs
- Server errors (404, 500, etc.)

**Behavior**: Exits early, message acknowledged (not retried)

### Empty Content

```python
if not html_content:
    logger.warning("No HTML content found.", url=url)
    return
```

Prevents storing empty articles.

### Duplicate Articles

```python
except pymongo.errors.DuplicateKeyError:
    logger.warning("Article already exists, skipping.", link=url)
```

Gracefully handles re-crawling of existing URLs.

### Unexpected Errors

```python
except Exception as e:
    logger.error("An unexpected error occurred in CrawlerWorker", url=url, error=str(e))
```

Logs unexpected errors for debugging.

---

## Logging

Uses **structured logging** with `structlog`:

```python
from shared.logger_config import configure_logger
configure_logger()
logger = structlog.get_logger()
```

**Key Log Events**:
- Function start with URL
- Playwright failures
- No HTML content warnings
- Successful article insertion
- Duplicate article warnings
- Unexpected errors

**Example Logs**:
```python
logger.info("CrawlerWorker function executing.", url=url)
logger.error("Playwright failed to get content", url=url, error=str(e))
logger.info("Successfully inserted new article", link=url)
logger.warning("Article already exists, skipping.", link=url)
```

---

## Dependencies

**Core Libraries**:
- `playwright.async_api` - Headless browser automation
- `beautifulsoup4` - HTML parsing (imported as `bs4`)
- `lxml` - XML/HTML parser (BeautifulSoup backend)
- `pymongo` - Cosmos DB access
- `azure.functions` - Azure Functions runtime
- `structlog` - Structured logging
- `python-dotenv` - Environment configuration

**Shared Modules**:
- `shared.key_vault_client.get_secret_client()` - Key Vault client
- `shared.logger_config.configure_logger()` - Logging setup

**System Dependencies**:
- Playwright browser binaries (Chromium)

---

## Workflow

```
Queue Message Received (URL)
    ↓
Decode URL from message body
    ↓
Log Function Start
    ↓
Get Cosmos DB Connection String from Key Vault
    ↓
Connect to Cosmos DB
    ↓
Ensure Unique Index on 'link' Field
    ↓
Launch Playwright Browser (Chromium)
    ↓
Navigate to URL (wait for DOM load, 60s timeout)
    ↓
Get Page HTML Content
    ↓
Close Browser
    ↓
If Playwright Failed → Log Error → Exit
    ↓
Parse HTML with BeautifulSoup (lxml parser)
    ↓
Extract Title (<title> tag)
    ↓
Extract Article Text (heuristic-based)
    ↓
Generate Summary (first 15 lines)
    ↓
Create Article Document
    ↓
Insert into Cosmos DB
    ├─ Success → Log Success
    └─ DuplicateKeyError → Log Warning
    ↓
Function Complete → Message Removed from Queue
```

---

## Usage Context

**Triggered By**: `CrawlerOrchestrator` or `ManualTrigger`
**Data Flow**: Queue Message (URL) → Web Scraping → Cosmos DB Storage
**Purpose**: Intelligent discovery of articles beyond RSS feeds
**Parallelization**: Multiple worker instances process queue messages concurrently

---

## Integration Points

### Upstream Producers

**CrawlerOrchestrator**:
- Timer-triggered (11:00 UTC)
- Sends URLs via queue binding

**ManualTrigger**:
- HTTP-triggered
- Sends URLs via explicit queue client

### Queue Input

**Queue**: `crawling-tasks-queue`
**Message Format**:
```
https://example.com/article-url
```
Simple UTF-8 encoded URL string.

### Cosmos DB Output

**Collection**: `articles`
**Document**:
```javascript
{
    title: "Extracted Article Title",
    link: "https://example.com/article-url",
    summary: "First 15 lines of content...",
    published: "2025-11-08T11:05:23.123456",
    processed: false,
    source: "intelligent_crawler",
    content: "Full article text content..."
}
```

### Downstream Consumers

**NewsletterGenerator**:
- Queries `articles` where `processed: false`
- Includes crawler-sourced articles in newsletters
- Note: Crawler articles lack `tags` field (potential enhancement)

---

## Performance Considerations

### Execution Time
- **Average**: 5-15 seconds per URL
- **Factors**: Page load time, content size, network speed
- **Timeout**: 60 seconds maximum

### Resource Usage
- **Memory**: ~200-300 MB per instance (browser overhead)
- **CPU**: Moderate (rendering, parsing)
- **Network**: Heavy (downloading full page + resources)

### Scaling
- **Concurrent Instances**: Azure Functions auto-scales based on queue depth
- **Max Instances**: Configurable in function app settings
- **Queue Processing**: One message per instance

### Cost Optimization
- Consider reducing timeout for faster failures
- Use queue visibility timeout to prevent re-processing
- Monitor execution time and optimize selectors

---

## Potential Improvements

### Content Extraction
1. **AI-Based Extraction**: Use LLM to extract main content more accurately
2. **Article Metadata**: Extract author, publish date, tags from meta tags
3. **Image Extraction**: Store featured images
4. **Smart Summarization**: Use AI for better summaries instead of first 15 lines

### Tagging
1. **Auto-Tagging**: Use Gemini/GPT to assign tags (like DailyArticleScraper)
2. **Topic Classification**: ML-based topic detection
3. **Keyword Extraction**: Extract key terms from content

### Error Handling
1. **Retry Logic**: Retry transient failures (network issues)
2. **Dead Letter Queue**: Move permanently failing URLs to separate queue
3. **Circuit Breaker**: Skip problematic domains after multiple failures

### Performance
1. **Browser Pooling**: Reuse browser instances across invocations
2. **Lightweight Mode**: Disable images/CSS for faster loads
3. **Selective Waiting**: Smart wait strategies based on page type
4. **Caching**: Cache crawled content with TTL

### Content Quality
1. **Quality Scoring**: Rate article quality before storing
2. **Duplicate Content Detection**: Check for similar content, not just URLs
3. **Language Detection**: Filter by user language preferences
4. **Paywall Detection**: Skip paywalled content

---

## Browser Configuration

Current: Minimal configuration, default Chromium

**Potential Customizations**:
```python
browser = await p.chromium.launch(
    headless=True,          # Headless mode
    args=[
        '--disable-dev-shm-usage',  # Reduce memory usage
        '--no-sandbox',             # Required in some containers
        '--disable-gpu',            # Disable GPU hardware acceleration
    ]
)

# User agent spoofing
page = await browser.new_page(user_agent="Custom User Agent")

# Viewport settings
await page.set_viewport_size({"width": 1280, "height": 720})

# Block resources for faster loads
await page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
```

---

## Testing

### Local Testing
```bash
# Start function locally
func start

# Send test message to queue (Azure Storage Explorer or Python script)
from azure.storage.queue import QueueClient
queue_client = QueueClient.from_connection_string(conn_str, "crawling-tasks-queue")
queue_client.send_message("https://example.com/test-article")
```

### Test Cases
1. **Standard Article**: News website with clear article tag
2. **JavaScript-Heavy**: React/Vue app that requires JS rendering
3. **Slow Loading**: Page that takes >10 seconds to load
4. **Duplicate URL**: URL already in database
5. **Invalid URL**: Malformed or unreachable URL
6. **Paywall**: Content behind authentication
7. **No Content**: Empty or minimal content page

---

## Monitoring

**Key Metrics**:
- Queue depth (messages waiting)
- Function execution count
- Success/failure rate
- Average execution duration
- Playwright timeout rate
- Duplicate article rate

**Azure Portal**:
- Function App → CrawlerWorker → Monitor
- Storage Account → Queues → crawling-tasks-queue
- Application Insights (recommended)

**Alerts**:
- Queue depth > threshold (backlog)
- Error rate > X%
- Average duration > Y seconds

---

## Related Documentation

- [CrawlerOrchestrator](./crawler-orchestrator.md) - Timer-triggered orchestrator
- [ManualTrigger](./manual-trigger.md) - HTTP-triggered orchestrator
- [orchestration_logic.py](../components/orchestration-logic.md) - Shared logic
- [Queue-Based Pattern](../patterns/queue-based-processing.md) - Architecture pattern

---

**Last Updated**: 2025-11-08
**Status**: Active, Production
