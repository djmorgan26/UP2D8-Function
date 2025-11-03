# UP2D8 Function App - Development TODO

This document tracks the planned improvements and further development for the UP2D8 Azure Function App.

## High Priority (Robustness/Completeness)

-   **More Robust Error Handling for External APIs/Services:** (Completed)
    -   **`DailyArticleScraper`**: Enhanced error handling for `feedparser` (e.g., network issues, malformed RSS feeds).
    -   **`NewsletterGenerator`**: Implemented more specific error handling for Gemini API calls (e.g., API rate limits, content filtering issues, network errors) and confirmed SMTP error logging is sufficient.

-   **HTML Conversion for Newsletters:** (Completed) Converted Markdown output from Gemini into proper HTML before sending the email.

## Medium Priority (Enhancements/Refinements)

-   **Advanced Topic Filtering (NewsletterGenerator):** (Completed) Implemented tag-based filtering for articles and user subscriptions.

-   **Configuration for RSS Feeds:** (Completed) RSS feed URLs are now managed dynamically from Cosmos DB instead of `rss_feeds.txt`.

## Low Priority (Good Practices/Future-proofing)

-   **Structured Logging:** (Completed) Implemented structured logging using `structlog` across the function app.

-   **Comprehensive Unit and Integration Tests:** (In Progress) Converted `test_mongo.py` to `pytest` and updated for new schema. Still need to expand coverage for new features and edge cases.
