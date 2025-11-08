# DailyArticleScraper Function

**Type**: Azure Timer-Triggered Function
**Schedule**: Daily at 08:00 UTC (CRON: `0 0 8 * * *`)
**Purpose**: Automated RSS feed scraping and article aggregation
**File**: `DailyArticleScraper/__init__.py`

---

## Overview

DailyArticleScraper is a timer-triggered Azure Function that automatically fetches articles from RSS feeds stored in Cosmos DB, parses them, assigns tags based on content analysis, and stores new articles in the database. It runs daily at 08:00 UTC to ensure fresh content is available for newsletter generation.

---

## What It Does

1. **Fetches RSS Feed URLs** from Cosmos DB (`rss_feeds` collection)
2. **Parses Each Feed** using `feedparser` library
3. **Assigns Content Tags** using keyword-based classification
4. **Stores Articles** in Cosmos DB (`articles` collection)
5. **Prevents Duplicates** using unique index on `link` field
6. **Logs Progress** using structured logging

---

## Key Features

### Automatic Tag Assignment

Uses keyword-based tagging system to categorize articles:

```python
TAG_KEYWORDS = {
    "AI": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],
    "Tech": ["technology", "software", "hardware", "startup", "innovation"],
    "Science": ["science", "research", "discovery", "biology", "physics", "chemistry"],
    "Business": ["business", "economy", "finance", "market", "investment"],
    "Health": ["health", "medical", "medicine", "wellness", "fitness"],
    "Environment": ["environment", "climate", "sustainability", "ecology"],
}
```

**Function**: `assign_tags(title: str, summary: str) -> list[str]`
- Combines title and summary
- Searches for keywords in lowercase content
- Returns list of matching tags

### Duplicate Prevention

Creates unique index on `link` field:
```python
articles_collection.create_index([("link", pymongo.ASCENDING)], unique=True)
```

Handles duplicates gracefully:
```python
except pymongo.errors.DuplicateKeyError:
    logger.warning('Article already exists', link=entry.link)
```

### Dynamic Feed Configuration

RSS feed URLs are stored in Cosmos DB, not hardcoded:
```python
rss_feeds = [feed['url'] for feed in rss_feeds_collection.find({})]
```

This allows feeds to be added/removed without code changes.

---

## Article Schema

Each article stored in Cosmos DB has the following structure:

```python
{
    'title': str,           # Article title
    'link': str,            # URL (unique identifier)
    'summary': str,         # Article summary/description
    'published': str,       # Publication date from RSS feed
    'processed': False,     # Flag for newsletter generation
    'tags': list[str]       # Auto-assigned content tags
}
```

---

## Configuration

### Environment Variables
- Loaded via `dotenv` from `.env` file

### Secrets from Azure Key Vault
- **`COSMOS-DB-CONNECTION-STRING-UP2D8`**: MongoDB connection string for Cosmos DB

### Trigger Schedule
- **CRON Expression**: `0 0 8 * * *`
- **Human Readable**: Daily at 08:00 UTC
- **Defined In**: `DailyArticleScraper/function.json`

---

## Error Handling

### Feed-Level Errors
```python
if feed.bozo:
    logger.warning('Malformed feed detected', feed_url=feed_url, bozo_exception=str(feed.bozo_exception))
    continue
```

Skips malformed feeds and continues processing others.

### Article-Level Errors
```python
except Exception as e:
    logger.error('Error processing article', link=entry.link, error=str(e))
```

Logs errors for individual articles but continues processing remaining entries.

### Top-Level Exception Handling
```python
except Exception as e:
    logger.error('An error occurred in DailyArticleScraper', error=str(e))
```

Catches any unexpected errors to prevent function crashes.

---

## Logging

Uses **structured logging** with `structlog`:

```python
from shared.logger_config import configure_logger
configure_logger()
logger = structlog.get_logger()
```

**Key Log Events**:
- Function start/end
- Feed parsing progress
- Malformed feed warnings
- Duplicate article warnings
- Final count of new articles added

**Example Logs**:
```python
logger.info('Parsing feed', feed_url=feed_url)
logger.warning('Article already exists', link=entry.link)
logger.info('Added new articles', count=new_articles_count)
```

---

## Dependencies

**Core Libraries**:
- `feedparser` - RSS feed parsing
- `pymongo` - Cosmos DB (MongoDB API) access
- `azure.functions` - Azure Functions runtime
- `azure.identity` - Azure authentication
- `azure.keyvault.secrets` - Key Vault integration
- `structlog` - Structured logging
- `python-dotenv` - Environment configuration

**Shared Modules**:
- `shared.key_vault_client.get_secret_client()` - Key Vault client initialization
- `shared.logger_config.configure_logger()` - Logging setup

---

## Workflow

```
Timer Trigger (08:00 UTC)
    ↓
Load Environment & Configuration
    ↓
Connect to Key Vault → Get Secrets
    ↓
Connect to Cosmos DB
    ↓
Fetch RSS Feed URLs from DB
    ↓
For each feed:
    ├─ Parse feed with feedparser
    ├─ For each article entry:
    │   ├─ Assign tags (keyword-based)
    │   ├─ Create article document
    │   └─ Insert into Cosmos DB (skip duplicates)
    └─ Log results
    ↓
Log total new articles count
    ↓
Function Complete
```

---

## Usage Context

**Runs Before**: `NewsletterGenerator` (which runs at 09:00 UTC)
**Data Flow**: RSS Feeds → Articles Collection → Newsletter Generation
**Purpose**: Ensures fresh articles are available for daily newsletters

---

## Integration Points

### Cosmos DB Collections

**Input**: `rss_feeds` collection
```javascript
{ url: "https://example.com/feed.xml" }
```

**Output**: `articles` collection
```javascript
{
    title: "Article Title",
    link: "https://example.com/article",
    summary: "Article summary...",
    published: "2025-11-08T08:00:00Z",
    processed: false,
    tags: ["AI", "Tech"]
}
```

### Downstream Consumers

**NewsletterGenerator** function:
- Queries `articles` collection for `processed: false`
- Uses `tags` field to match user preferences
- Marks articles as `processed: true` after newsletter generation

---

## Performance Considerations

- **Unique Index**: Prevents duplicate processing, improves query performance
- **Batch Processing**: Processes all feeds in sequence (not parallelized)
- **Error Isolation**: Feed/article errors don't stop processing
- **No Rate Limiting**: Consider adding delays for external feed providers

---

## Potential Improvements

1. **Parallel Feed Processing**: Use async/await for concurrent feed parsing
2. **Rate Limiting**: Add delays between requests to respect feed providers
3. **Advanced Tagging**: Use AI/ML for more accurate tag assignment
4. **Feed Health Monitoring**: Track failed feeds over time
5. **Content Deduplication**: Check for similar articles with different URLs
6. **Scheduling Flexibility**: Allow per-feed custom schedules

---

## Related Documentation

- [NewsletterGenerator](./newsletter-generator.md) - Consumes articles for newsletter generation
- [orchestration_logic.py](../components/orchestration-logic.md) - Complementary article discovery via search
- [Key Vault Integration](../../context/decisions/) - Secrets management approach

---

**Last Updated**: 2025-11-08
**Status**: Active, Production
