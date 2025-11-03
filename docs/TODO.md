# UP2D8 Function App - Development TODO

This document tracks the planned improvements and further development for the UP2D8 Azure Function App.

## High Priority (Robustness/Completeness)

-   **More Robust Error Handling for External APIs/Services:** (Completed)
    -   **`DailyArticleScraper`**: Enhanced error handling for `feedparser` (e.g., network issues, malformed RSS feeds).
    -   **`NewsletterGenerator`**: Implemented more specific error handling for Gemini API calls (e.g., API rate limits, content filtering issues, network errors) and confirmed SMTP error logging is sufficient.

-   **HTML Conversion for Newsletters:** (Completed) Converted Markdown output from Gemini into proper HTML before sending the email.

-   **Retry Mechanisms:** Implement more robust retry policies with exponential backoff for external API calls (Gemini, SMTP, Cosmos DB) to improve reliability.

## Medium Priority (Enhancements/Refinements)

-   **Advanced Topic Filtering (NewsletterGenerator):** (Completed) Implemented tag-based filtering for articles and user subscriptions.

-   **Configuration for RSS Feeds:** (Completed) RSS feed URLs are now managed dynamically from Cosmos DB instead of `rss_feeds.txt`.

-   **User Management API:** Develop an API for users to manage their `subscribed_tags` and `preferences` in Cosmos DB.

## Low Priority (Good Practices/Future-proofing)

-   **Structured Logging:** (Completed) Implemented structured logging using `structlog` across the function app.

-   **Comprehensive Unit and Integration Tests:** (In Progress) Converted `test_mongo.py` to `pytest` and updated for new schema. Still need to expand coverage for new features and edge cases.

## Observability

-   **Alerting:** Set up alerts for critical issues such as Function App failures, high error rates, or anomalies in article scraping/newsletter delivery.
