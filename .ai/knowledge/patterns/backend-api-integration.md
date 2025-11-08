---
type: pattern
name: Backend API Integration Pattern
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - shared/backend_client.py
  - DailyArticleScraper/__init__.py
  - CrawlerWorker/__init__.py
  - HealthMonitor/__init__.py
  - DataArchival/__init__.py
related:
  - .ai/knowledge/components/backend-api-client.md
  - .ai/context/decisions/002-backend-api-integration.md
tags: [integration, api, http, architecture, centralization]
---

# Backend API Integration Pattern

## What It Is
Architectural pattern for centralizing all data writes through the UP2D8-BACKEND FastAPI service instead of direct Cosmos DB writes. Establishes a single source of truth, enables centralized analytics, and provides better monitoring and control over data operations.

## Problem It Solves

### Before Integration
**Issues**:
- ❌ Multiple services writing directly to Cosmos DB (data integrity risks)
- ❌ No centralized analytics or metrics tracking
- ❌ Duplicate logic across services (validation, deduplication)
- ❌ Hard to track where data originates
- ❌ No health monitoring or system observability
- ❌ No automated data lifecycle management

**Architecture**:
```
DailyArticleScraper → Cosmos DB
CrawlerWorker → Cosmos DB
Frontend → Cosmos DB
Backend API → Cosmos DB
```
(Multiple paths to same data = potential conflicts)

### After Integration
**Benefits**:
- ✅ Single source of truth for all data writes (backend API)
- ✅ Automatic analytics tracking for all operations
- ✅ Centralized validation and business logic
- ✅ Comprehensive health monitoring
- ✅ Automated data archival and cleanup
- ✅ Better error tracking and observability

**Architecture**:
```
DailyArticleScraper → Backend API → Cosmos DB
CrawlerWorker → Backend API → Cosmos DB
Frontend → Backend API → Cosmos DB
HealthMonitor → Backend API (health checks)
DataArchival → Cosmos DB (read-only cleanup)
```
(Single path for writes, controlled data flow)

## How It Works

### Core Principle
**Centralize writes, allow read fallbacks**

1. **All article creation** goes through `BackendAPIClient.create_article()`
2. **All analytics** go through `BackendAPIClient.log_analytics()`
3. **Reads can still use Cosmos DB** directly for performance (RSS feeds, users)
4. **Health checks** use both backend API and Cosmos DB
5. **Archival operations** use direct Cosmos DB access (administrative operations)

### Implementation Steps

#### Step 1: Create Shared HTTP Client
**File**: `shared/backend_client.py`

```python
class BackendAPIClient:
    def __init__(self):
        self.base_url = os.environ.get(
            "BACKEND_API_URL",
            "https://up2d8-backend.azurewebsites.net"
        )

    def create_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """All article creation goes through here"""
        response = requests.post(
            f"{self.base_url}/api/articles",
            json=article_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def log_analytics(self, event_type: str, details: Dict[str, Any]) -> None:
        """All analytics logging goes through here"""
        # Non-critical, silent failures
```

**Key Design Choices**:
- Single class, instantiate per function execution
- Environment-configurable base URL
- Typed method signatures for clarity
- Separate timeouts per operation type (30s for articles, 10s for analytics)
- Silent failures for analytics (non-critical)

#### Step 2: Update Article-Creating Functions
**Pattern**: Replace direct DB writes with API calls

**Before** (Direct Cosmos DB write):
```python
articles_collection = db.articles
articles_collection.insert_one({
    "title": entry.title,
    "link": entry.link,
    "summary": entry.summary,
    # ... more fields
})
```

**After** (Backend API integration):
```python
backend_client = BackendAPIClient()

article_data = {
    'title': entry.title,
    'link': entry.link,
    'summary': entry.summary,
    'published': entry.published,
    'tags': tags,
    'source': 'rss'
}

result = backend_client.create_article(article_data)

if "created successfully" in result.get("message", ""):
    new_articles_count += 1
elif "already exists" in result.get("message", ""):
    duplicate_articles_count += 1
```

**Files Updated**:
- `DailyArticleScraper/__init__.py:91` - RSS article creation
- `CrawlerWorker/__init__.py:85` - Crawled article creation

#### Step 3: Add Analytics Tracking
**Pattern**: Log operational metrics after significant operations

```python
# At end of function execution
backend_client.log_analytics("daily_scrape_completed", {
    "new_articles": new_articles_count,
    "feeds_processed": len(rss_feeds),
    "execution_time_seconds": (datetime.now() - start_time).total_seconds(),
    "failed_articles": failed_articles_count,
    "duplicate_articles": duplicate_articles_count
})
```

**Common Event Types**:
- `daily_scrape_completed` - After DailyArticleScraper runs
- `data_archival_completed` - After DataArchival runs
- `data_archival_failed` - When archival encounters errors
- `newsletter_generated` - After NewsletterGenerator completes
- Custom events as needed

**Where to Add**:
- End of successful function execution
- In exception handlers (for failure events)
- After significant milestones (e.g., batch processing complete)

#### Step 4: Create Health Monitoring
**Pattern**: Expose HTTP endpoint that tests all critical dependencies

```python
def main(req: func.HttpRequest) -> func.HttpResponse:
    health_status = {
        "function_app": "healthy",
        "checks": {}
    }

    # Test each dependency
    try:
        # Cosmos DB
        client.server_info()
        health_status["checks"]["cosmos_db"] = "connected"
    except Exception as e:
        health_status["function_app"] = "unhealthy"
        health_status["checks"]["cosmos_db"] = f"failed: {str(e)}"

    # Repeat for backend API, Key Vault, etc.

    status_code = 200 if health_status["function_app"] == "healthy" else 503
    return func.HttpResponse(json.dumps(health_status), status_code=status_code)
```

**Implementation**: `HealthMonitor/__init__.py`

#### Step 5: Implement Data Lifecycle Management
**Pattern**: Scheduled cleanup of old data

```python
def main(timer: func.TimerRequest) -> None:
    # Calculate cutoff dates
    article_cutoff = datetime.now(UTC) - timedelta(days=90)
    analytics_cutoff = datetime.now(UTC) - timedelta(days=180)

    # Delete old data
    article_result = db.articles.delete_many({
        "processed": True,
        "created_at": {"$lt": article_cutoff}
    })

    # Log metrics
    backend_client.log_analytics("data_archival_completed", {
        "articles_archived": article_result.deleted_count,
        # ... more metrics
    })
```

**Implementation**: `DataArchival/__init__.py`

## When to Use This Pattern

### ✅ Use Backend API Integration When:
- Creating new articles (from any source)
- Logging operational metrics or analytics
- Implementing new features that modify data
- Building new Azure Functions that write data
- Need centralized validation or business logic

### ❌ Direct Cosmos DB Access When:
- Reading configuration data (RSS feeds, users) - performance optimization
- Administrative operations (archival, bulk updates) - direct control
- Health checks that verify database connectivity - testing actual dependency
- One-time migration scripts - operational necessity

## Configuration Requirements

### Environment Variables
```bash
# Required
BACKEND_API_URL=https://up2d8-backend.azurewebsites.net

# Already exists (for direct DB access where needed)
COSMOS_DB_CONNECTION_STRING=<from Key Vault>
```

### Backend API Endpoints Required
```
POST /api/articles       - Article creation with deduplication
POST /api/analytics      - Analytics event logging
GET  /api/health         - Backend health status
GET  /api/users          - User data (optional, can still read from DB)
GET  /api/rss_feeds      - RSS feeds (optional, can still read from DB)
```

### Backend API Response Formats

**Article Creation Success**:
```json
{
    "message": "Article created successfully.",
    "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Article Already Exists**:
```json
{
    "message": "Article already exists.",
    "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Health Check**:
```json
{
    "status": "healthy",
    "database": "connected",
    "collections": {
        "articles": 1247,
        "users": 34,
        "rss_feeds": 8
    },
    "timestamp": "2025-11-08T12:00:00Z"
}
```

## Error Handling Pattern

### Critical Operations (Article Creation)
```python
try:
    result = backend_client.create_article(article_data)
    # Handle result
except requests.RequestException as e:
    logger.error("Failed to create article via API", error=str(e))
    # Optionally: fall back to direct DB write (if needed)
    # Optionally: add to retry queue
    # Increment failure counter
```

**Behavior**:
- Raise exceptions for visibility
- Log with context (link, error, status code)
- Don't silently drop data
- Consider retry mechanisms for transient failures

### Non-Critical Operations (Analytics)
```python
try:
    backend_client.log_analytics(event_type, details)
except:
    pass  # Silent failure, analytics shouldn't block operations
```

**Behavior**:
- Silent failures (analytics is non-critical)
- Log warnings for monitoring
- Don't block main operations
- No retries (keep functions fast)

## Testing the Integration

### Manual Testing Checklist
- [ ] Articles created via DailyArticleScraper appear in backend database
- [ ] Duplicate articles are detected and handled correctly
- [ ] Analytics events are logged to analytics collection
- [ ] Health check endpoint returns correct status
- [ ] Health check detects backend API failures (returns degraded)
- [ ] Health check detects Cosmos DB failures (returns unhealthy)
- [ ] Data archival deletes old articles correctly
- [ ] Archival metrics are logged to analytics

### Integration Testing
```python
# Test article creation
article_data = {
    "title": "Test Article",
    "link": "https://test.com/article-1",
    "summary": "Test summary",
    "published": datetime.utcnow().isoformat(),
    "tags": ["Test"],
    "source": "test"
}

client = BackendAPIClient()
result = client.create_article(article_data)
assert "created successfully" in result["message"]
assert result["id"] is not None

# Test duplicate detection
result2 = client.create_article(article_data)
assert "already exists" in result2["message"]
assert result2["id"] == result["id"]
```

## Migration Guide

### For New Functions
1. Import `BackendAPIClient`: `from shared.backend_client import BackendAPIClient`
2. Initialize client: `backend_client = BackendAPIClient()`
3. Use client methods instead of direct DB writes
4. Add analytics logging at key milestones
5. Test locally with `BACKEND_API_URL` pointed to dev environment

### For Existing Functions
1. Identify direct Cosmos DB write operations
2. Extract data being written into dict format
3. Replace `collection.insert_one()` with `backend_client.create_article()`
4. Update error handling to catch `requests.RequestException`
5. Add analytics logging for operational metrics
6. Test thoroughly (especially duplicate handling)

### For Read Operations
**Decision**: Keep reading from Cosmos DB directly for now
**Rationale**:
- Reads are more frequent than writes (performance matters)
- No validation or business logic needed for reads
- Direct DB access is faster (no HTTP overhead)
- Can migrate to API later if needed (e.g., for access control)

## Benefits Realized

### 1. Single Source of Truth
- All article writes go through backend API
- Centralized validation and deduplication logic
- No conflicting writes from multiple services
- Easier to audit and track data flow

### 2. Automatic Analytics Tracking
- Every scrape operation is logged
- Archival metrics tracked over time
- System health events recorded
- Operational insights from analytics collection

### 3. Comprehensive Health Monitoring
- Proactive health checks for all dependencies
- Degraded vs. unhealthy state differentiation
- Integration with monitoring tools (Azure Monitor, Uptime Robot)
- Quick issue detection and diagnosis

### 4. Automated Data Lifecycle Management
- Old data automatically archived
- Predictable storage costs
- Performance maintained with smaller dataset
- Compliance with data retention policies

### 5. Better Scalability
- Clear separation of concerns (functions vs. backend)
- Backend can scale independently
- Easier to add new data sources (just use client)
- API can implement rate limiting, caching, etc.

### 6. Improved Maintainability
- Business logic centralized in backend
- Functions focus on scheduling and data collection
- Single client library for all API interactions
- Consistent error handling across functions

## Common Issues

### Issue: Backend API Unavailable
**Symptoms**: All article creation fails
**Solution**:
- HealthMonitor will detect and report degraded state
- Consider fallback to direct DB writes (with feature flag)
- Check backend logs and restart if needed
- Monitor analytics for `create_article` failures

### Issue: Slow API Response Times
**Symptoms**: Functions timing out or taking longer
**Solution**:
- Review backend API performance (database queries, indexing)
- Check network latency (Azure region mismatches)
- Consider increasing function timeout
- Implement retry with exponential backoff

### Issue: Analytics Not Logging
**Symptoms**: No analytics events in database
**Solution**:
- Expected behavior (silent failures)
- Check backend API `/api/analytics` endpoint
- Review backend logs for errors
- Not critical - main operations should continue

## Related Knowledge
- [Backend API Client](../components/backend-api-client.md) - HTTP client implementation
- [Decision: Backend API Integration](../../context/decisions/002-backend-api-integration.md) - ADR
- [DailyArticleScraper](../features/daily-article-scraper.md) - First function to integrate
- [CrawlerWorker](../features/crawler-worker.md) - Second function to integrate
- [HealthMonitor](../features/health-monitor.md) - System health checks
- [DataArchival](../features/data-archival.md) - Data lifecycle management

## Future Enhancements
- [ ] Add circuit breaker pattern for backend API failures
- [ ] Implement retry queue for failed article creations
- [ ] Add request caching for GET operations
- [ ] Implement bulk article creation endpoint (for batch operations)
- [ ] Add API key authentication for security
- [ ] Migrate read operations to backend API (for access control)
- [ ] Add Prometheus metrics export from functions
- [ ] Implement event streaming (Azure Event Grid) for real-time updates
- [ ] Add distributed tracing (Application Insights correlation)
- [ ] Create admin dashboard showing integration health
