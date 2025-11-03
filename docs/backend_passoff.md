# Backend Pass-off for UP2D8 Automated Tasks Service

This document outlines the key integration points and data structures the backend application needs to manage to support the UP2D8 Automated Tasks Service (Azure Functions) and the frontend.

## 1. Cosmos DB Schema & Interaction

The backend will be the primary interface for managing data in Cosmos DB, which is consumed and produced by the Azure Functions.

### 1.1. `users` Collection

*   **Purpose:** Stores user profiles, including their subscription details and preferences.
*   **Schema:**
    ```json
    {
        "id": "<unique_user_id>",
        "email": "user@example.com",
        "subscribed_tags": ["Tech", "AI", "Science"], // List of tags the user is interested in
        "preferences": "concise", // or "detailed", controls newsletter length/style
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z"
        // ... other user-specific fields
    }
    ```
*   **Backend Responsibilities:**
    *   Provide API endpoints for the frontend to create, read, update, and delete user profiles.
    *   Manage user authentication and authorization.
    *   Ensure data integrity and validation for `subscribed_tags` and `preferences`.

### 1.2. `articles` Collection

*   **Purpose:** Stores scraped articles, consumed by `NewsletterGenerator`.
*   **Schema:**
    ```json
    {
        "id": "<unique_article_id>",
        "title": "Article Title",
        "link": "https://example.com/article",
        "summary": "Brief summary of the article.",
        "published": "2023-10-27T09:00:00Z",
        "processed": false, // Set to true after being included in a newsletter
        "tags": ["Tech", "AI"], // Tags assigned by DailyArticleScraper
        "created_at": "2023-10-27T09:30:00Z"
    }
    ```
*   **Backend Responsibilities:** (Primarily managed by `DailyArticleScraper` and `NewsletterGenerator`)
    *   The backend might provide read-only access to articles for administrative purposes or for displaying past content.

### 1.3. `rss_feeds` Collection

*   **Purpose:** Stores the list of RSS feed URLs for the `DailyArticleScraper`.
*   **Schema:**
    ```json
    {
        "id": "<unique_feed_id>",
        "url": "https://example.com/rss_feed",
        "category": "Tech", // Optional category for organization
        "last_scraped": "2023-10-27T08:00:00Z" // Optional: last time this feed was successfully scraped
    }
    ```
*   **Backend Responsibilities:**
    *   Provide API endpoints for administrators to add, update, or remove RSS feed URLs.
    *   Ensure validation of RSS feed URLs.

## 2. Key Vault Integration

*   The backend should securely retrieve sensitive information (e.g., Cosmos DB connection strings, Gemini API keys, Brevo SMTP credentials) from Azure Key Vault.
*   The `shared/key_vault_client.py` module can be adapted or used as a reference for this.

## 3. Environment Variables

*   Ensure that necessary environment variables (e.g., `BREVO_SMTP_USER`, `BREVO_SMTP_HOST`, `BREVO_SMTP_PORT`, `SENDER_EMAIL`) are configured in the backend's deployment environment.

## 4. Interaction with Azure Functions

*   The Azure Functions are designed to run autonomously on a schedule. Direct interaction from the backend with the functions (e.g., triggering them) is generally not required for the core functionality.
*   However, the backend might need to monitor the functions' logs (via Azure Application Insights) for operational insights.

## 5. General Considerations

*   **API Design:** Design RESTful APIs for managing user data and RSS feeds.
*   **Security:** Implement robust authentication, authorization, and data encryption practices.
*   **Scalability:** Design the backend to scale with the number of users and data volume.
*   **Error Handling & Logging:** Implement comprehensive error handling and structured logging for all backend operations.
