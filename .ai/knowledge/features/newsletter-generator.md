# NewsletterGenerator Function

**Type**: Azure Timer-Triggered Function
**Schedule**: Daily at 09:00 UTC (CRON: `0 0 9 * * *`)
**Purpose**: AI-powered personalized newsletter generation and delivery
**File**: `NewsletterGenerator/__init__.py`

---

## Overview

NewsletterGenerator is a timer-triggered Azure Function that creates personalized newsletters for subscribed users using Google's Gemini AI. It fetches unprocessed articles, filters them based on user preferences, generates customized newsletter content, converts it to HTML, and sends emails via SMTP. Runs daily at 09:00 UTC, one hour after article scraping.

---

## What It Does

1. **Fetches Unprocessed Articles** from Cosmos DB (`processed: false`)
2. **Retrieves User Preferences** including subscribed tags and content style
3. **Filters Articles** based on user's tag subscriptions
4. **Generates Newsletter Content** using Google Gemini AI
5. **Converts Markdown to HTML** for email formatting
6. **Sends Emails** via Brevo SMTP service
7. **Marks Articles as Processed** after successful delivery

---

## Key Features

### Personalized Content Filtering

Filters articles based on user-subscribed tags:

```python
user_subscribed_tags = user.get('subscribed_tags', [])
relevant_articles = [a for a in articles if any(tag in a.get('tags', []) for tag in user_subscribed_tags)]
```

Each user receives only articles matching their interests.

### AI-Powered Newsletter Generation

Uses **Google Gemini Pro** for content generation:

```python
prompt = f"Create a {user_preferences} newsletter in Markdown from these articles:\n\n"
for article in relevant_articles:
    prompt += f"- **{article['title']}**: {article['summary']}\n"

response = model.generate_content(prompt)
newsletter_content_markdown = response.text
```

**User Preferences**:
- Style options: `"concise"`, `"detailed"`, etc.
- Stored in user document: `user.get('preferences', 'concise')`

### Markdown to HTML Conversion

Converts AI-generated Markdown to HTML for email:

```python
newsletter_content_html = markdown.markdown(newsletter_content_markdown)
```

Ensures rich formatting in email clients.

### Email Delivery via SMTP

Uses custom `SMTPProvider` from shared modules:

```python
smtp_provider = SMTPProvider(
    smtp_host=brevo_smtp_host,
    smtp_port=brevo_smtp_port,
    smtp_username=brevo_smtp_user,
    smtp_password=brevo_smtp_password
)

email_message = EmailMessage(
    to=user['email'],
    subject='Your Daily News Digest',
    html_body=newsletter_content_html,
    from_email=sender_email
)

smtp_provider.send_email(email_message)
```

---

## User Schema

Expected user document structure in Cosmos DB:

```python
{
    'email': str,                    # User email address
    'subscribed_tags': list[str],    # Tags user is interested in (e.g., ["AI", "Tech"])
    'preferences': str               # Newsletter style (e.g., "concise", "detailed")
}
```

---

## Configuration

### Environment Variables

**From `.env` file**:
- `BREVO_SMTP_USER` - SMTP username
- `BREVO_SMTP_HOST` - SMTP server hostname
- `BREVO_SMTP_PORT` - SMTP port (typically 587 or 465)
- `SENDER_EMAIL` - Newsletter sender email address

### Secrets from Azure Key Vault

- **`COSMOS-DB-CONNECTION-STRING-UP2D8`**: MongoDB connection string
- **`UP2D8-GEMINI-API-Key`**: Google Gemini API key
- **`UP2D8-SMTP-KEY`**: Brevo SMTP password

### Trigger Schedule

- **CRON Expression**: `0 0 9 * * *`
- **Human Readable**: Daily at 09:00 UTC
- **Defined In**: `NewsletterGenerator/function.json`

---

## Error Handling

### No Articles to Process

```python
if not articles:
    logger.info("No new articles to process.")
    return
```

Exits gracefully if no unprocessed articles exist.

### No Relevant Articles for User

```python
if not relevant_articles:
    logger.info("No relevant articles for user", user_email=user['email'], subscribed_tags=user_subscribed_tags)
    continue
```

Skips users with no matching content.

### Gemini API Failures

```python
try:
    response = model.generate_content(prompt)
    newsletter_content_markdown = response.text
except Exception as e:
    logger.error("Error generating content with Gemini for user", user_email=user['email'], error=str(e))
    continue
```

Skips to next user if AI generation fails.

### Empty AI Response

```python
if not newsletter_content_markdown:
    logger.warning("Gemini API returned empty content for user. Skipping email.", user_email=user['email'])
    continue
```

Prevents sending empty newsletters.

### Email Sending Failures

```python
if smtp_provider.send_email(email_message):
    sent_newsletters_count += 1
    logger.info("Newsletter sent", user_email=user['email'])
else:
    logger.error("Failed to send newsletter", user_email=user['email'])
```

Logs failures but continues processing other users.

### User-Level Error Isolation

```python
except Exception as e:
    logger.error("Error processing user", user_email=user['email'], error=str(e))
```

One user's error doesn't stop processing for others.

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
- No articles available
- No relevant articles per user
- Gemini API errors
- Empty AI responses
- Email send successes/failures
- Total newsletters sent

**Example Logs**:
```python
logger.info("No relevant articles for user", user_email=user['email'], subscribed_tags=user_subscribed_tags)
logger.error("Error generating content with Gemini for user", user_email=user['email'], error=str(e))
logger.info("Newsletter sent", user_email=user['email'])
logger.info('Sent newsletters', count=sent_newsletters_count)
```

---

## Dependencies

**Core Libraries**:
- `pymongo` - Cosmos DB access
- `google.generativeai` - Gemini AI integration
- `markdown` - Markdown to HTML conversion
- `azure.functions` - Azure Functions runtime
- `structlog` - Structured logging
- `python-dotenv` - Environment configuration

**Shared Modules**:
- `shared.email_service.EmailMessage` - Email message data structure
- `shared.email_service.SMTPProvider` - SMTP email sending
- `shared.key_vault_client.get_secret_client()` - Key Vault client
- `shared.logger_config.configure_logger()` - Logging setup

---

## Workflow

```
Timer Trigger (09:00 UTC)
    ↓
Load Environment & Configuration
    ↓
Connect to Key Vault → Get Secrets
    ↓
Initialize Gemini AI Model (gemini-pro)
    ↓
Initialize SMTP Provider (Brevo)
    ↓
Connect to Cosmos DB
    ↓
Fetch All Users & Unprocessed Articles
    ↓
For each user:
    ├─ Get user's subscribed tags & preferences
    ├─ Filter articles by tags
    ├─ If no relevant articles → Skip user
    ├─ Generate newsletter with Gemini AI
    │   └─ Prompt includes user style preference
    ├─ Convert Markdown → HTML
    ├─ Send email via SMTP
    └─ Log success/failure
    ↓
Mark all articles as processed
    ↓
Log total sent newsletters count
    ↓
Function Complete
```

---

## Usage Context

**Runs After**: `DailyArticleScraper` (which runs at 08:00 UTC)
**Data Flow**: Articles Collection → AI Generation → Email Delivery → Mark Processed
**Purpose**: Delivers daily personalized newsletters to all subscribed users

---

## Integration Points

### Cosmos DB Collections

**Input - Users**:
```javascript
{
    email: "user@example.com",
    subscribed_tags: ["AI", "Tech"],
    preferences: "concise"
}
```

**Input - Articles** (from DailyArticleScraper):
```javascript
{
    title: "Article Title",
    summary: "Summary...",
    tags: ["AI", "Tech"],
    processed: false
}
```

**Output - Articles** (marked as processed):
```javascript
{
    // ... same fields ...
    processed: true
}
```

### External Services

**Google Gemini AI**:
- Model: `gemini-pro`
- Purpose: Generate personalized newsletter content
- API Key: From Azure Key Vault

**Brevo SMTP**:
- Purpose: Email delivery service
- Authentication: Username + password (from Key Vault)
- Port: Configurable (typically 587 for TLS)

---

## Performance Considerations

- **Sequential User Processing**: Processes users one at a time (not parallelized)
- **AI API Latency**: Gemini generation adds ~2-5 seconds per user
- **SMTP Rate Limits**: Brevo has sending limits (check plan)
- **Article Processing**: All articles marked processed in single batch update

**Estimated Runtime**:
- 100 users × 3 seconds (AI + email) = ~5 minutes
- Suitable for daily schedules

---

## Potential Improvements

1. **Parallel Processing**: Use async/await for concurrent newsletter generation
2. **Email Queuing**: Offload email sending to a queue for better reliability
3. **Retry Logic**: Implement retries for transient failures (AI, SMTP)
4. **Email Templates**: Use HTML templates for better design
5. **Unsubscribe Links**: Add unsubscribe functionality to emails
6. **Analytics**: Track open rates, click rates (via tracking pixels/links)
7. **A/B Testing**: Test different newsletter styles
8. **Fallback Content**: Use pre-generated summaries if AI fails
9. **User Timezone Support**: Send newsletters at user's preferred local time
10. **Dry Run Mode**: Test newsletter generation without sending

---

## AI Prompt Engineering

Current prompt structure:
```python
prompt = f"Create a {user_preferences} newsletter in Markdown from these articles:\n\n"
for article in relevant_articles:
    prompt += f"- **{article['title']}**: {article['summary']}\n"
```

**Best Practices**:
- Clear instruction: "Create a {style} newsletter"
- Structured input: Bulleted list of articles
- Format specification: "in Markdown"
- User preference: Dynamic style based on user data

**Potential Enhancements**:
- Add examples of desired output format
- Include user's name for personalization
- Add section headers guidance
- Specify tone/voice preferences

---

## Related Documentation

- [DailyArticleScraper](./daily-article-scraper.md) - Provides articles for newsletters
- [Email Service Pattern](../patterns/email-service.md) - SMTP integration approach
- [AI Integration Pattern](../patterns/ai-integration.md) - Gemini usage patterns

---

**Last Updated**: 2025-11-08
**Status**: Active, Production
