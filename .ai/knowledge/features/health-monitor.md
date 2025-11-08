---
type: feature
name: Health Monitor
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - HealthMonitor/__init__.py
  - HealthMonitor/function.json
related:
  - .ai/knowledge/components/backend-api-client.md
tags: [monitoring, health-check, http-trigger, diagnostics]
---

# Health Monitor

## What It Does
HTTP-triggered Azure Function that performs comprehensive health checks on system components. Tests connectivity to Cosmos DB, backend API, and Azure Key Vault, returning a JSON response with health status. Designed for monitoring tools, alerting systems, and operations dashboards.

## How It Works
When invoked via HTTP GET request, the function runs three independent health checks in sequence. Each check is wrapped in try-except to ensure one failure doesn't prevent other checks from running. Returns HTTP 200 for healthy/degraded states, HTTP 503 for unhealthy states.

**Key files:**
- `HealthMonitor/__init__.py:1-90` - Main health check logic
- `HealthMonitor/function.json:1-17` - HTTP trigger binding configuration

## Architecture

### Function Trigger
**Type**: HTTP Trigger (anonymous authentication)
**Method**: GET
**URL Pattern**: `https://<function-app>.azurewebsites.net/api/HealthMonitor`

### Health Check Flow
```
HTTP GET Request
    ↓
Load environment variables (.env)
    ↓
Initialize health_status dict
    ↓
Check 1: Cosmos DB → Update health_status
    ↓
Check 2: Backend API → Update health_status
    ↓
Check 3: Key Vault → Update health_status
    ↓
Determine HTTP status code
    ↓
Return JSON response
```

## Health Checks

### Check 1: Cosmos DB Connectivity
**File**: `HealthMonitor/__init__.py:35-45`

```python
secret_client = get_secret_client()
cosmos_connection = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
client = pymongo.MongoClient(cosmos_connection, serverSelectionTimeoutMS=5000)
client.server_info()  # Raises exception if can't connect
health_status["checks"]["cosmos_db"] = "connected"
```

**Tests**:
- Connection string retrieval from Key Vault
- MongoDB connection within 5 seconds
- Server ping to verify active connection

**On Success**: `"cosmos_db": "connected"`
**On Failure**: `"cosmos_db": "failed: <error message>"` + sets `function_app: "unhealthy"`

### Check 2: Backend API Health
**File**: `HealthMonitor/__init__.py:47-63`

```python
backend_client = BackendAPIClient()
backend_health = backend_client.health_check()
health_status["checks"]["backend_api"] = {
    "status": backend_health.get("status", "unknown"),
    "database": backend_health.get("database", "unknown")
}

if backend_health.get("status") != "healthy":
    health_status["function_app"] = "degraded"
```

**Tests**:
- Backend API reachability
- Backend database connectivity
- Backend service health

**On Success**:
```json
"backend_api": {
    "status": "healthy",
    "database": "connected"
}
```

**On Degraded**: Backend unhealthy → Function app marked as `"degraded"` (still operational)
**On Failure**: `"backend_api": "failed: <error message>"` + sets `function_app: "degraded"`

### Check 3: Azure Key Vault Access
**File**: `HealthMonitor/__init__.py:65-74`

```python
secret_client = get_secret_client()
secret_client.get_secret("UP2D8-GEMINI-API-Key")
health_status["checks"]["key_vault"] = "accessible"
```

**Tests**:
- Key Vault authentication (Managed Identity)
- Secret retrieval permissions
- Key Vault availability

**On Success**: `"key_vault": "accessible"`
**On Failure**: `"key_vault": "failed: <error message>"` + sets `function_app: "unhealthy"`

## Health States

### 1. Healthy (HTTP 200)
**Condition**: All checks pass
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

### 2. Degraded (HTTP 200)
**Condition**: Backend API unhealthy, but Cosmos DB and Key Vault work
```json
{
    "function_app": "degraded",
    "checks": {
        "cosmos_db": "connected",
        "backend_api": {
            "status": "unhealthy",
            "database": "disconnected"
        },
        "key_vault": "accessible"
    }
}
```

**Interpretation**: Function app can still operate (scraping, crawling), but API integration unavailable. Articles may queue up for later processing.

### 3. Unhealthy (HTTP 503)
**Condition**: Cosmos DB or Key Vault failure
```json
{
    "function_app": "unhealthy",
    "checks": {
        "cosmos_db": "failed: Connection timeout",
        "backend_api": {...},
        "key_vault": "accessible"
    }
}
```

**Interpretation**: Critical dependency failure. Function app cannot operate properly.

## Important Decisions

### Decision 1: Backend API Failures Are Non-Critical
**Rationale**: `HealthMonitor/__init__.py:56-57`
- Backend API is new integration (recent addition)
- Functions can still read/write to Cosmos DB directly if needed
- Degraded state allows monitoring without false alarms
- HTTP 200 for degraded ensures load balancers don't remove instance

### Decision 2: 5-Second Cosmos DB Timeout
**Rationale**: `HealthMonitor/__init__.py:38`
- Health checks should be fast (monitoring polls frequently)
- 5 seconds is sufficient for healthy connections
- Prevents health check from hanging indefinitely
- Allows quick failure detection

### Decision 3: Anonymous Authentication
**Rationale**: `HealthMonitor/function.json:6`
- Health endpoints are meant to be public for monitoring tools
- No sensitive data in response (just connection states)
- Simplifies integration with external monitoring services
- Can add IP whitelisting at network level if needed

### Decision 4: Test Specific Secret for Key Vault
**Rationale**: `HealthMonitor/__init__.py:68`
- Uses `UP2D8-GEMINI-API-Key` as test secret
- Confirms not just Key Vault access, but also secret permissions
- This secret is required by NewsletterGenerator (critical function)
- If this fails, major functionality is impacted

## Usage Examples

### Manual Health Check
```bash
curl https://up2d8-function.azurewebsites.net/api/HealthMonitor
```

### Integration with Azure Monitor
**Alert Rule**:
- Condition: `function_app != "healthy"`
- Frequency: Every 5 minutes
- Action: Send notification to ops team

### Integration with Uptime Monitoring (e.g., Uptime Robot)
- Monitor URL: `https://up2d8-function.azurewebsites.net/api/HealthMonitor`
- Interval: 5 minutes
- Success Condition: HTTP 200 AND response contains `"function_app": "healthy"`

### Load Balancer Health Probe
**Azure Load Balancer Config**:
- Protocol: HTTP
- Path: `/api/HealthMonitor`
- Interval: 15 seconds
- Unhealthy threshold: 2 consecutive failures (HTTP 503)

## Testing

**Manual Testing**:
1. Deploy function to Azure
2. Navigate to `https://<app>.azurewebsites.net/api/HealthMonitor`
3. Verify JSON response with all checks passing
4. Test failure scenarios:
   - Temporarily remove Key Vault permissions → Expect HTTP 503
   - Temporarily change Cosmos DB connection string → Expect HTTP 503
   - Stop backend API → Expect HTTP 200 with "degraded"

**Test Files**: None yet (manual testing only)

## Common Issues

### Issue: HTTP 503 Even Though Everything Seems Fine
**Symptoms**: Health check returns unhealthy, but functions work
**Solution**:
1. Check structured logs for specific check failures
2. Verify Managed Identity has Key Vault permissions
3. Verify Cosmos DB connection string is current
4. Check network security groups (NSGs) for blocked traffic

### Issue: Health Check Times Out
**Symptoms**: No response or very slow response
**Solution**:
1. Check Cosmos DB timeout setting (5 seconds)
2. Verify backend API is responding (not hanging)
3. Check Function App scaling (cold starts can delay initial requests)
4. Review Function App logs for startup errors

### Issue: Backend API Shows as Unhealthy
**Symptoms**: `backend_api.status: "unhealthy"` but function_app is "degraded"
**Solution**:
1. This is expected behavior if backend has issues
2. Check backend logs and database connectivity
3. Scraping/crawling functions may still work via direct Cosmos DB access
4. Not critical - monitor backend separately

## Related Knowledge
- [Backend API Client](../components/backend-api-client.md) - Used for backend health check
- [Key Vault Client](../../shared/key_vault_client.py) - Used for secret retrieval
- [Logger Config](../../shared/logger_config.py) - Structured logging configuration

## Future Ideas
- [ ] Add individual function health checks (test each timer/queue trigger)
- [ ] Include last successful execution times for each function
- [ ] Add queue depth metrics (crawling-tasks-queue)
- [ ] Implement detailed Cosmos DB collection statistics
- [ ] Add response time metrics for each check
- [ ] Include system resource metrics (CPU, memory)
- [ ] Add historical health data tracking
- [ ] Implement health check caching (don't hammer dependencies)
- [ ] Add webhook notifications for state changes
- [ ] Include dependency version information in response
