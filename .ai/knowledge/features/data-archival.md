---
type: feature
name: Data Archival
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - DataArchival/__init__.py
  - DataArchival/function.json
related:
  - .ai/knowledge/components/backend-api-client.md
tags: [timer-trigger, data-lifecycle, archival, cleanup, maintenance]
---

# Data Archival

## What It Does
Weekly timer-triggered Azure Function that automatically archives and deletes old data from Cosmos DB. Removes processed articles older than 90 days and analytics events older than 180 days. Logs archival metrics to backend analytics for monitoring and reporting. Implements automated data lifecycle management to control storage costs and maintain database performance.

## How It Works
Runs every Sunday at midnight UTC (CRON: `0 0 * * 0`). Connects to Cosmos DB, calculates cutoff dates, executes bulk delete operations, and logs metrics to backend API. Includes error handling to prevent partial failures and logs all failures to analytics when possible.

**Key files:**
- `DataArchival/__init__.py:1-86` - Main archival logic
- `DataArchival/function.json:1-11` - Timer trigger binding configuration

## Architecture

### Function Trigger
**Type**: Timer Trigger
**Schedule**: `0 0 * * 0` (Weekly: Every Sunday at midnight UTC)
**Execution**: Automatic (no manual intervention)

### Archival Flow
```
Timer Trigger (Sundays at 00:00 UTC)
    ↓
Load environment variables
    ↓
Connect to Cosmos DB
    ↓
Calculate cutoff dates (90 days, 180 days)
    ↓
Delete old processed articles → Count deleted
    ↓
Delete old analytics events → Count deleted
    ↓
Log metrics to backend API
    ↓
Log completion to structured logs
```

## Archival Rules

### Rule 1: Processed Articles (90-Day Retention)
**File**: `DataArchival/__init__.py:37-46`

```python
article_cutoff_date = datetime.now(UTC) - timedelta(days=90)

result = db.articles.delete_many({
    "processed": True,
    "created_at": {"$lt": article_cutoff_date}
})

archived_articles_count = result.deleted_count
```

**Criteria**:
- Must have `processed: True` (already used in newsletters)
- `created_at` must be older than 90 days
- Unprocessed articles are preserved indefinitely

**Rationale**:
- Processed articles have already been delivered to users
- Users are unlikely to need articles older than 3 months
- Keeps database focused on recent, actionable content
- Reduces storage costs and improves query performance

**What Gets Deleted**:
- Articles from RSS scraping that were included in newsletters
- Articles from intelligent crawler that were processed
- Articles manually marked as processed

**What Gets Preserved**:
- Articles scraped within last 90 days
- Unprocessed articles (regardless of age)
- Articles with `processed: False` or missing field

### Rule 2: Analytics Events (180-Day Retention)
**File**: `DataArchival/__init__.py:48-56`

```python
analytics_cutoff = datetime.now(UTC) - timedelta(days=180)

analytics_result = db.analytics.delete_many({
    "timestamp": {"$lt": analytics_cutoff}
})

archived_analytics_count = analytics_result.deleted_count
```

**Criteria**:
- `timestamp` must be older than 180 days (6 months)
- All events are eligible (no filtering by type)

**Rationale**:
- Analytics are for operational monitoring, not long-term storage
- 6 months provides sufficient historical data for trend analysis
- Longer retention requires dedicated analytics warehouse
- Prevents unbounded analytics collection growth

**What Gets Deleted**:
- System events (daily_scrape_completed, data_archival_completed, etc.)
- User events (if any)
- Health check events (if logged)

**What Gets Preserved**:
- Analytics events from last 6 months
- Recent trend data for dashboards

## Metrics Logging

### Backend Analytics Event
**File**: `DataArchival/__init__.py:58-66`

```python
backend_client.log_analytics("data_archival_completed", {
    "articles_archived": archived_articles_count,
    "analytics_archived": archived_analytics_count,
    "article_cutoff_days": 90,
    "analytics_cutoff_days": 180,
    "article_cutoff_date": article_cutoff_date.isoformat(),
    "analytics_cutoff_date": analytics_cutoff.isoformat()
})
```

**Logged Data**:
- Count of articles deleted
- Count of analytics events deleted
- Retention policies (90/180 days)
- Exact cutoff dates used

**Purpose**:
- Track archival effectiveness over time
- Monitor data growth patterns
- Alert on unexpected deletions (e.g., too many or too few)
- Historical record of data lifecycle operations

### Failure Logging
**File**: `DataArchival/__init__.py:74-83`

```python
except Exception as e:
    logger.error("DataArchival failed", error=str(e))
    try:
        backend_client = BackendAPIClient()
        backend_client.log_analytics("data_archival_failed", {
            "error": str(e)
        })
    except:
        pass  # Don't fail the function if analytics logging fails
```

**Error Handling**:
- Catches all exceptions during archival
- Logs to structured logs with error details
- Attempts to log failure to backend analytics
- Silent failure on analytics logging (don't cascade errors)

## Important Decisions

### Decision 1: Different Retention Periods for Different Data
**Rationale**:
- Articles (90 days): User-facing content, valuable for longer
- Analytics (180 days): Operational metrics, less critical long-term
- Balances data value with storage costs
- Can adjust retention periods independently

### Decision 2: Only Archive Processed Articles
**Rationale**: `DataArchival/__init__.py:41-42`
- Unprocessed articles may still be useful for future newsletters
- Prevents deletion of articles scraped but not yet delivered
- User preference changes could make old articles relevant again
- Conservative approach to data deletion

### Decision 3: Weekly Execution at Midnight Sunday
**Rationale**: `DataArchival/function.json:7`
- Low traffic period (users mostly inactive)
- Consistent, predictable schedule
- Weekly is frequent enough to prevent excessive data accumulation
- Midnight UTC avoids business hours in all timezones

### Decision 4: Bulk Delete Instead of Archive to Separate Collection
**Rationale**:
- No current need for long-term article storage
- Simplifies implementation (no archive collection management)
- Reduces Cosmos DB throughput costs (one collection instead of two)
- Can implement true archival (to Azure Blob Storage) later if needed

## Usage Examples

### Manual Execution (Testing)
**Azure Portal**:
1. Navigate to Function App → DataArchival
2. Click "Code + Test"
3. Click "Test/Run"
4. View execution logs and results

**Azure CLI**:
```bash
az functionapp function invoke \
  --resource-group <rg> \
  --name <function-app-name> \
  --function-name DataArchival
```

### Monitoring Archival Activity
**Query Analytics Collection**:
```javascript
db.analytics.find({
    event_type: "data_archival_completed"
}).sort({ timestamp: -1 }).limit(10)
```

**Expected Result**:
```json
[
  {
    "event_type": "data_archival_completed",
    "details": {
      "articles_archived": 47,
      "analytics_archived": 328,
      "article_cutoff_days": 90,
      "analytics_cutoff_days": 180,
      "article_cutoff_date": "2024-08-09T00:00:00Z",
      "analytics_cutoff_date": "2024-05-11T00:00:00Z"
    },
    "timestamp": "2025-11-08T00:00:00Z"
  }
]
```

### Adjusting Retention Periods
**To change article retention to 60 days**:
```python
# Line 38
article_cutoff_date = datetime.now(UTC) - timedelta(days=60)
```

**To change analytics retention to 1 year**:
```python
# Line 49
analytics_cutoff = datetime.now(UTC) - timedelta(days=365)
```

## Testing

### Test Setup
1. **Create test data**:
```javascript
// Old processed article (should be deleted)
db.articles.insertOne({
    title: "Test Old Article",
    link: "https://example.com/old",
    processed: true,
    created_at: new Date("2024-01-01")
})

// Recent processed article (should be preserved)
db.articles.insertOne({
    title: "Test Recent Article",
    link: "https://example.com/recent",
    processed: true,
    created_at: new Date()
})

// Old unprocessed article (should be preserved)
db.articles.insertOne({
    title: "Test Old Unprocessed",
    link: "https://example.com/unprocessed",
    processed: false,
    created_at: new Date("2024-01-01")
})
```

2. **Run function** (manually or wait for scheduled run)

3. **Verify results**:
```javascript
// Should be deleted
db.articles.findOne({ link: "https://example.com/old" })  // null

// Should exist
db.articles.findOne({ link: "https://example.com/recent" })  // exists
db.articles.findOne({ link: "https://example.com/unprocessed" })  // exists
```

### Test Files
None yet (manual testing recommended with test data)

## Common Issues

### Issue: Too Many Articles Deleted
**Symptoms**: Large spike in `articles_archived` count
**Solution**:
1. Check if `processed` field is being set correctly by NewsletterGenerator
2. Verify cutoff date calculation is correct
3. Review article creation timestamps
4. Check for mass updates to `processed` field

### Issue: No Articles Deleted Despite Old Data
**Symptoms**: `articles_archived: 0` but old articles exist
**Causes**:
1. Articles have `processed: False` (intentional)
2. Articles missing `created_at` field (won't match query)
3. Articles have `created_at` in wrong format (not Date object)

**Solution**:
1. Query articles manually: `db.articles.find({ processed: true, created_at: { $lt: new Date("2024-08-01") } })`
2. Check field types: `db.articles.findOne({}, { created_at: 1, processed: 1 })`
3. Fix data schema if needed

### Issue: Archival Function Fails Silently
**Symptoms**: No logs, no analytics events
**Solution**:
1. Check Function App logs in Azure Portal
2. Verify timer trigger is enabled (not disabled)
3. Check Cosmos DB connection string in Key Vault
4. Verify Managed Identity has Key Vault access

### Issue: Analytics Logging Fails But Archival Succeeds
**Symptoms**: Articles deleted but no `data_archival_completed` event
**Solution**:
1. Check backend API connectivity (expected non-critical failure)
2. Verify `BACKEND_API_URL` environment variable
3. Review backend API logs for errors
4. Not critical - archival still occurred

## Related Knowledge
- [Backend API Client](../components/backend-api-client.md) - Used for analytics logging
- [DailyArticleScraper](./daily-article-scraper.md) - Creates articles with `created_at` field
- [NewsletterGenerator](./newsletter-generator.md) - Sets `processed: True` on articles

## Future Ideas
- [ ] Archive to Azure Blob Storage instead of deleting (for compliance/audit)
- [ ] Configurable retention periods via environment variables
- [ ] Per-tag retention policies (e.g., keep "AI" articles longer)
- [ ] Alerting when archival deletes unexpectedly large amounts
- [ ] Export archived data to Azure Data Lake for long-term analytics
- [ ] Add user-specific article retention (e.g., favorite articles never deleted)
- [ ] Implement soft delete with `archived: True` flag instead of hard delete
- [ ] Add metrics for storage savings (estimated cost reduction)
- [ ] Create manual archival endpoint for ad-hoc cleanup
- [ ] Add dry-run mode to preview what would be deleted
