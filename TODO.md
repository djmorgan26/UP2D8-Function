# UP2D8 Function App - Development TODO

This document tracks the planned improvements and further development for the UP2D8 Azure Function App.

## High Priority (Robustness/Completeness)

-   **More Robust Error Handling for External APIs/Services:**
    -   **`DailyArticleScraper`**: Enhance error handling for `feedparser` (e.g., network issues, malformed RSS feeds). Currently, it logs a general exception.
    -   **`NewsletterGenerator`**: Implement more specific error handling for Gemini API calls (e.g., API rate limits, content filtering issues, network errors) and for the Brevo SMTP service to provide more detailed failure reasons.

-   **HTML Conversion for Newsletters:** The `NewsletterGenerator` currently sends Markdown content directly as the email body. For better and more consistent rendering across various email clients, convert the Markdown output from Gemini into proper HTML before sending the email.

## Medium Priority (Enhancements/Refinements)

-   **Advanced Topic Filtering (NewsletterGenerator):** The current article filtering based on user topics is a simple substring match. This could be enhanced for more accurate personalization.

-   **Configuration for RSS Feeds:** Explore options to manage RSS feed URLs dynamically (e.g., Cosmos DB, Azure App Configuration) instead of `rss_feeds.txt`.

## Low Priority (Good Practices/Future-proofing)

-   **Structured Logging:** Ensure all logs are structured (e.g., JSON) and include relevant contextual information for improved observability in Azure Application Insights.

-   **Comprehensive Unit and Integration Tests:** Expand test coverage for all features, especially API integrations and data processing logic.
