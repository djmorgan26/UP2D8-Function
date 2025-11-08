# UP2D8 Integration Deployment Guide

**Last Updated**: 2025-11-08
**Purpose**: Step-by-step guide to deploy integrated UP2D8-Function and UP2D8-BACKEND

---

## Prerequisites

- Azure subscription with access to:
  - Azure Functions
  - Azure App Service
  - Azure Cosmos DB (MongoDB API)
  - Azure Key Vault
  - Azure Storage (for queues)
- Azure CLI installed and logged in
- Python 3.9+ for both repos
- Node.js 18+ for frontend (future integration)

---

## Phase 1: Backend Deployment (UP2D8-BACKEND)

### 1.1 Update Dependencies

```bash
cd /path/to/UP2D8-BACKEND
pip install azure-storage-queue
pip freeze > requirements.txt
```

### 1.2 Environment Variables

Add to Azure App Service Configuration → Application Settings:

```ini
# Existing
KEY_VAULT_URI=https://your-key-vault.vault.azure.net/

# NEW - Add this for Azure Storage Queue integration
AZURE_STORAGE_CONNECTION_STRING=<your-azure-storage-connection-string>
```

### 1.3 Deploy Backend

```bash
# Option 1: Via Azure CLI
az webapp up --name up2d8-backend --resource-group <your-rg>

# Option 2: Via GitHub Actions (recommended)
# Configure deployment center in Azure Portal to connect to GitHub repo
```

### 1.4 Verify Backend Health

```bash
curl https://up2d8-backend.azurewebsites.net/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T...",
  "database": "connected",
  "collections": {
    "articles": { "total": 0, "unprocessed": 0 },
    "users": 0,
    "rss_feeds": 0
  }
}
```

---

## Phase 2: Function App Configuration

### 2.1 Update Dependencies

```bash
cd /path/to/UP2D8-Function
pip install requests
pip freeze > requirements.txt
```

### 2.2 Environment Variables

Add to Azure Functions → Configuration → Application Settings:

```ini
# Existing
KEY_VAULT_URI=https://your-key-vault.vault.azure.net/
BREVO_SMTP_USER=<your-smtp-user>
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
SENDER_EMAIL=<your-sender-email>

# NEW - Backend Integration
BACKEND_API_URL=https://up2d8-backend.azurewebsites.net

# NEW - Azure Storage (for queues)
AzureWebJobsStorage=<your-azure-storage-connection-string>
```

### 2.3 Azure Key Vault Secrets

Ensure these secrets exist in your Key Vault:

```
COSMOS-DB-CONNECTION-STRING-UP2D8
UP2D8-GEMINI-API-Key
UP2D8-SMTP-KEY
```

### 2.4 Deploy Functions

```bash
# Option 1: Via Azure Functions Core Tools
func azure functionapp publish <your-function-app-name>

# Option 2: Via VS Code Azure Extension
# Right-click function app → Deploy to Function App
```

### 2.5 Verify Function Health

```bash
curl https://<your-function-app>.azurewebsites.net/api/HealthMonitor
```

Expected response:
```json
{
  "function_app": "healthy",
  "checks": {
    "cosmos_db": "connected",
    "backend_api": {
      "status": "healthy",
      "database": "connected"
    },
    "key_vault": "accessible"
  }
}
```

---

## Phase 3: Integration Testing

### 3.1 Test Article Creation Flow

1. **Add RSS Feed** (via backend):
```bash
curl -X POST https://up2d8-backend.azurewebsites.net/api/rss_feeds \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://techcrunch.com/feed/",
    "category": "Tech News"
  }'
```

2. **Manually Trigger DailyArticleScraper**:
```bash
# Via Azure Portal: Functions → DailyArticleScraper → Code + Test → Run
```

3. **Verify Articles Created**:
```bash
curl https://up2d8-backend.azurewebsites.net/api/articles
```

4. **Check Analytics**:
```bash
# Query Cosmos DB analytics collection to see "article_scraped" events
```

### 3.2 Test Health Monitoring

```bash
# Test Functions health
curl https://<function-app>.azurewebsites.net/api/HealthMonitor

# Test Backend health
curl https://up2d8-backend.azurewebsites.net/api/health
```

### 3.3 Test Data Archival (Manual Trigger)

```bash
# Via Azure Portal: Functions → DataArchival → Code + Test → Run
# Verify analytics event "data_archival_completed" is logged
```

---

## Phase 4: Monitoring Setup

### 4.1 Application Insights

1. Enable Application Insights for both Function App and App Service
2. Create custom dashboards for:
   - Article scraping metrics (new, duplicates, failures)
   - Function execution times
   - API request rates
   - Error rates

### 4.2 Alerts

Configure alerts for:
- Function failures (>5 in 5 minutes)
- Backend API 5xx errors (>10 in 5 minutes)
- Health check failures
- Cosmos DB throttling

### 4.3 Custom Queries (Application Insights)

**Article Scraping Metrics**:
```kusto
customEvents
| where name == "article_scraped"
| summarize count() by source
| render piechart
```

**Daily Scraping Performance**:
```kusto
customEvents
| where name == "daily_scrape_completed"
| project timestamp, new_articles = toint(customDimensions.new_articles)
| render timechart
```

---

## Phase 5: Scheduled Tasks Verification

### 5.1 Timer Schedules

Verify these functions run at correct times (all UTC):

| Function | Schedule | CRON | Purpose |
|----------|----------|------|---------|
| DailyArticleScraper | 08:00 UTC | `0 0 8 * * *` | Scrape RSS feeds |
| NewsletterGenerator | 09:00 UTC | `0 0 9 * * *` | Send newsletters |
| CrawlerOrchestrator | 11:00 UTC | `0 0 11 * * *` | Intelligent crawling |
| DataArchival | Sunday 00:00 UTC | `0 0 * * 0` | Archive old data |

### 5.2 Monitor First Runs

After deployment, monitor logs for each function's first scheduled execution:

```bash
# Via Azure CLI
az functionapp log tail --name <function-app-name> --resource-group <rg>
```

---

## Troubleshooting

### Issue: "Failed to create article via API"

**Check**:
1. BACKEND_API_URL environment variable is set correctly
2. Backend health endpoint responds
3. Network connectivity between Function App and App Service
4. Backend logs for errors

**Solution**:
```bash
# Verify backend URL
az functionapp config appsettings list \
  --name <function-app> \
  --resource-group <rg> \
  | grep BACKEND_API_URL

# Test connectivity from Function App
# Use Kudu console (Advanced Tools) → Debug Console
curl https://up2d8-backend.azurewebsites.net/api/health
```

### Issue: "Key Vault access denied"

**Check**:
1. Managed Identity is enabled on Function App
2. Managed Identity has "Get" permissions on Key Vault secrets
3. Correct Key Vault URI in environment

**Solution**:
```bash
# Enable managed identity
az functionapp identity assign \
  --name <function-app> \
  --resource-group <rg>

# Grant access to Key Vault (get the principal ID from above command)
az keyvault set-policy \
  --name <key-vault-name> \
  --object-id <principal-id> \
  --secret-permissions get list
```

### Issue: "Backend API health check fails"

**Check**:
1. App Service is running
2. Cosmos DB connection string is correct
3. Database is accessible

**Solution**:
```bash
# Check App Service status
az webapp show --name up2d8-backend --resource-group <rg> --query state

# Restart if needed
az webapp restart --name up2d8-backend --resource-group <rg>

# Check logs
az webapp log tail --name up2d8-backend --resource-group <rg>
```

---

## Configuration Checklist

### Backend (UP2D8-BACKEND)

- [ ] Deployed to Azure App Service
- [ ] Managed Identity enabled
- [ ] Key Vault access granted
- [ ] Environment variables configured:
  - [ ] KEY_VAULT_URI
  - [ ] AZURE_STORAGE_CONNECTION_STRING (if using queues)
- [ ] Health endpoint returns "healthy"
- [ ] POST /api/articles endpoint works
- [ ] Application Insights enabled

### Function App (UP2D8-Function)

- [ ] Deployed to Azure Functions
- [ ] Managed Identity enabled
- [ ] Key Vault access granted
- [ ] Environment variables configured:
  - [ ] KEY_VAULT_URI
  - [ ] BACKEND_API_URL
  - [ ] BREVO_SMTP_USER, BREVO_SMTP_HOST, BREVO_SMTP_PORT
  - [ ] SENDER_EMAIL
  - [ ] AzureWebJobsStorage
- [ ] All 8 functions deployed:
  - [ ] DailyArticleScraper
  - [ ] NewsletterGenerator
  - [ ] CrawlerOrchestrator
  - [ ] CrawlerWorker
  - [ ] ManualTrigger
  - [ ] HealthMonitor
  - [ ] DataArchival
- [ ] Health endpoint returns "healthy"
- [ ] Application Insights enabled
- [ ] Timer schedules verified

### Cosmos DB

- [ ] Articles collection exists
- [ ] Users collection exists
- [ ] RSS feeds collection exists
- [ ] Analytics collection exists
- [ ] Unique index on articles.link
- [ ] Connection accessible from both Function App and App Service

### Azure Storage

- [ ] Storage account created
- [ ] Queue `user-preference-changes` created (for future use)
- [ ] Queue `crawling-tasks-queue` exists (for CrawlerWorker)

---

## Next Steps

1. ✅ **Monitor First 24 Hours**: Watch logs for any errors
2. ✅ **Verify Scheduled Runs**: Ensure all timer functions execute
3. ✅ **Test Article Flow**: RSS feed → Scraper → Backend API → Cosmos DB
4. ✅ **Check Analytics**: Verify events are being logged
5. ⏭️ **Frontend Integration**: Connect React Native app to backend
6. ⏭️ **User Preference Webhooks**: Implement UserPreferenceListener
7. ⏭️ **Push Notifications**: Add mobile notification service

---

## Rollback Plan

If integration causes issues:

1. **Revert Functions** to direct Cosmos DB writes:
   - Comment out `backend_client.create_article()` calls
   - Uncomment original `articles_collection.insert_one()` code
   - Redeploy functions

2. **Keep Backend** running (existing endpoints still work)

3. **Re-test** integration in staging environment

---

## Success Metrics

After deployment, you should see:

- **Article creation**: Articles flow from scrapers → Backend API → Cosmos DB
- **Analytics events**: "article_scraped", "daily_scrape_completed" logged
- **Health checks**: Both Function App and Backend return "healthy"
- **No direct DB writes**: All writes go through backend API
- **Centralized monitoring**: Single analytics collection tracks all events

**Integration is successful when all metrics are green!**

