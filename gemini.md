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

# UP2D8 - Automated Tasks Service (Azure Functions)

This repository contains the scheduled, serverless tasks for the UP2D8 application. These functions are responsible for the daily scraping of articles and the generation and sending of personalized newsletters.

## 1. Prerequisites

-   Python 3.9+
-   Pip & venv
-   Azure Functions Core Tools
-   Azure CLI
-   An Azure Key Vault with the required secrets configured.

## 2. Configuration & Secrets

This service is designed for maximum security using Azure Key Vault.

### Secret Management
-   **In Azure:** The deployed Function App uses a **Managed Identity** to authenticate with Key Vault.
    -   **Locally:** The service uses `DefaultAzureCredential`, which will use the credentials of the developer currently logged into the Azure CLI.

### Local Setup
1.  **Log in to Azure:**
    ```bash
    az login
    ```
    Ensure the logged-in user has "Get" permissions on secrets in the project's Key Vault.

2.  **Create `.env` file:**
    This file stores your local environment variables. Create it in the root of the project and populate it with the following (replace placeholders with your actual values):

    ```
    KEY_VAULT_URI=https://personal-key-vault1.vault.azure.net/
    BREVO_SMTP_HOST=smtp-relay.brevo.com
    BREVO_SMTP_PORT=587
    BREVO_SMTP_USER=9a9964001@smtp-brevo.com
    SENDER_EMAIL=newsletter@your-domain.com
    ```

3.  **Create `rss_feeds.txt` file:**
    This file contains a list of RSS feed URLs, one per line. It is ignored by git. Create it in the root of the project.

    ```
    https://rss.cnn.com/rss/cnn_topstories.rss
    https://feeds.bbci.co.uk/news/rss.xml
    ```
## 3. Installation & Local Execution

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the functions locally:**
    ```bash
    func start
    ```
    The Functions host will start, and the timer triggers will fire according to their schedules (or you can invoke them manually via the local dashboard URL).

## 4. Function Details

This service contains two timer-triggered functions:

-   **`DailyArticleScraper`**: Runs at 08:00 UTC daily. Fetches articles from public RSS feeds and stores them in Cosmos DB.
-   **`NewsletterGenerator`**: Runs at 09:00 UTC daily. Generates and sends personalized newsletters to all subscribed users.

## 5. Deployment to Azure Function App

1.  **Create Function App:** In the Azure Portal, create a new "Function App" resource.
    -   **Publish:** Code
    -   **Runtime stack:** Python
    -   **Version:** 3.9 (or newer)
    -   **Hosting:** Consumption (Serverless) plan is recommended.

2.  **Enable Managed Identity:**
    -   Go to your new Function App.
    -   Under **Settings > Identity**, enable the **System assigned** identity.
    -   Grant this identity **"Get"** permissions on your Key Vault's Access Policies.

3.  **Configure Application Settings:**
    -   In your Function App, go to **Settings > Configuration**.
    -   Add new Application Settings for all the non-secret values that were previously in `local.settings.json` (e.g., `KEY_VAULT_URI`, `BREVO_SMTP_HOST`, `BREVO_SMTP_PORT`, `BREVO_SMTP_USER`, `SENDER_EMAIL`). These will be loaded as environment variables by the Function App.

4.  **Deploy Code:**
    -   The recommended method is to use the VS Code Azure extension, which handles the deployment process seamlessly.
    -   Alternatively, use the Azure Functions Core Tools CLI: `func azure functionapp publish <YourFunctionAppName>`

## 6. Development Notes

### Virtual Environment

-   **Creation:** To create a virtual environment, run the following command in the root of the project:
    ```bash
    python3 -m venv venv
    ```

-   **Activation:** To activate the virtual environment, use the following command:
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    -   **Windows:**
        ```bash
        venv\Scripts\activate
        ```

-   **Installation:** To install packages from `requirements.txt` into the active virtual environment, run:
    ```bash
    pip install -r requirements.txt
    ```

## 7. Other Repositories

This project spans 3 repositories (frontend, backend, function app). When doing work that involves integrating with the other repos of this greater project, refer to these handoff documents first.

- **UP2D8-FUNCTION** The handoff document for this repo is `docs/handoff/backend.md`.
- **UP2D8-FRONTEND** The handoff document for this repo is `docs/handoff/frontend.md`.