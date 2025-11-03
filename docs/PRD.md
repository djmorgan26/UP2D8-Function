# PRD: UP2D8 Automated Tasks Service

**Version:** 1.0
**Status:** Definition

## 1. Objective

This document outlines the product requirements for the UP2D8 Automated Tasks service, which runs on Azure Functions. The objective of this service is to perform all the background, scheduled work required to deliver the core product: a personalized daily news digest. It operates autonomously without direct user interaction.

## 2. User Personas & Stories

-   **As a subscribed user,** I want to receive a high-quality, relevant, and timely news digest in my email every morning so I can stay informed.
-   **As a product owner,** I want the system to automatically gather fresh content from across the web daily to ensure newsletters are always current.
-   **As a system administrator,** I want the automated tasks to be reliable, to handle errors gracefully, and to provide clear logs so I can monitor their health.

## 3. Functional Requirements

This service consists of two independent, time-triggered functions.

### 3.1. Function 1: Daily Article Scraper

-   **Trigger:** Time-based, runs once daily at 08:00 UTC.
-   **Objective:** To populate the `articles` collection in the database with new content from the web.
-   **Requirements:**
    -   Must read from a configurable list of public RSS feeds.
    -   Must parse each article to extract its title, link, summary, and publication date.
    -   Must store each article as a new document in the `articles` collection in Cosmos DB.
    -   Must gracefully handle unreachable feeds or parsing errors without crashing.
    -   Must not insert duplicate articles (enforced by a unique index on the article link).
    -   Must log the outcome of each run, including the number of new articles added.

### 3.2. Function 2: Newsletter Generator & Sender

-   **Trigger:** Time-based, runs once daily at 09:00 UTC (one hour after the scraper).
-   **Objective:** To create and send personalized newsletters to all subscribed users.
-   **Requirements:**
    -   Must fetch all users from the `users` collection.
    -   Must fetch all articles from the `articles` collection that have not yet been processed (`processed: false`).
    -   For each user, it must:
        1.  Filter the new articles to find ones relevant to their subscribed `topics`.
        2.  Read the user's `preferences` (e.g., "concise" vs "detailed" format).
        3.  If relevant articles exist, construct a detailed prompt for the Gemini API that includes the articles and the user's preferences.
        4.  Call the Gemini API to generate the newsletter content in Markdown.
        5.  Connect to the Brevo SMTP service and send the generated content to the user's email.
    -   After processing all users, it must update the `processed` flag to `true` on all articles used in this run to prevent them from being sent again.
    -   Must log the number of newsletters successfully sent and any individual sending failures.

## 4. Non-Functional Requirements

-   **Reliability:** The functions must be robust and run to completion even if some external resources (like one of the RSS feeds) are unavailable.
-   **Security:** All secrets (database connection strings, API keys) must be loaded securely from Azure Key Vault at runtime.
-   **Observability:** The service must produce clear, structured logs in Azure Application Insights for monitoring and debugging.

## 5. Success Metrics

-   Daily function execution success rate: > 99%
-   Newsletter delivery success rate: > 98%
-   End-to-end processing time (start of scraper to last email sent): < 30 minutes.
