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

2.  **Create `local.settings.json` file:**
    This file is the local equivalent of Application Settings in Azure and is ignored by git. Create it in the root of the project.

    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "KEY_VAULT_URI": "https://personal-key-vault1.vault.azure.net/",
        "BREVO_SMTP_HOST": "smtp-relay.brevo.com",
        "BREVO_SMTP_PORT": "587",
        "BREVO_SMTP_USER": "9a9964001@smtp-brevo.com",
        "SENDER_EMAIL": "newsletter@your-domain.com"
      }
    }
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
    *(Note: a `requirements.txt` file will need to be created containing `azure-functions`, `pymongo`, `feedparser`, `google-generativeai`, `azure-identity`, `azure-keyvault-secrets`)*

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
    -   Grant this identity **"Get"** permissions on secrets in your Key Vault's Access Policies.

3.  **Configure Application Settings:**
    -   In your Function App, go to **Settings > Configuration**.
    -   Add new Application Settings for all the non-secret values listed in `local.settings.json` (e.g., `KEY_VAULT_URI`, `BREVO_SMTP_HOST`, etc.).

4.  **Deploy Code:**
    -   The recommended method is to use the VS Code Azure extension, which handles the deployment process seamlessly.
    -   Alternatively, use the Azure Functions Core Tools CLI: `func azure functionapp publish <YourFunctionAppName>`
