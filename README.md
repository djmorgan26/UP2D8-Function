# UP2D8 - Automated Tasks Service

This repository houses the scheduled, serverless tasks for the UP2D8 application, built with Azure Functions. It automates daily article scraping and the generation and delivery of personalized newsletters.

## ✨ Features

-   **Daily Article Scraper**: Automatically fetches articles from public RSS feeds and stores them in Cosmos DB every day at 08:00 UTC.
-   **Newsletter Generator**: Generates and dispatches personalized newsletters to all subscribed users daily at 09:00 UTC.

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

-   Python 3.9+
-   Pip & `venv`
-   Azure Functions Core Tools (see installation instructions below for macOS)
    *   **macOS Installation:**
        If you are on macOS, you can install Azure Functions Core Tools using Homebrew:
        ```bash
        brew tap azure/functions
        brew install azure-functions-core-tools@4
        ```
        If you don't have Homebrew, install it first:
        ```bash
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ```
-   Azure CLI
-   Access to an Azure Key Vault with necessary secrets configured.

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd UP2D8-Function
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Authenticate with Azure:**
    ```bash
    az login
    ```
    Ensure your logged-in Azure account has "Get" permissions for secrets in the project's Key Vault. The service uses `DefaultAzureCredential` for local authentication.

5.  **Ensure Function App Configuration Files Exist:**
    For `func start` to correctly identify the project root and load settings, ensure `host.json` and `local.settings.json` files are present in the root directory of the repository. If they are missing, you can create minimal versions:
    *   `host.json`:
        ```json
        {
          "version": "2.0",
          "extensionBundle": {
            "id": "Microsoft.Azure.Functions.ExtensionBundle",
            "version": "[3.*, 4.0.0)"
          }
        }
        ```
    *   `local.settings.json`:
        ```json
        {
          "IsEncrypted": false,
          "Values": {
            "AzureWebJobsStorage": "useDevelopmentStorage=true",
            "FUNCTIONS_WORKER_RUNTIME": "python"
          }
        }
        ```

6.  **Run the functions locally:**
    ```bash
    func start
    ```
    The Azure Functions host will start, and timer-triggered functions will execute according to their schedules. You can also invoke them manually via the local dashboard.

## ☁️ Deployment to Azure

This service is designed to be deployed as an Azure Function App. Key considerations for deployment include:

-   **Azure Function App**: Create a Python-based Function App (version 3.9+) in the Azure Portal.
-   **Managed Identity**: Enable a System-assigned Managed Identity for your Function App and grant it "Get" permissions on secrets within your Azure Key Vault.
-   **Deployment Method**: Utilize the VS Code Azure extension for seamless deployment or use the Azure Functions Core Tools CLI: `func azure functionapp publish <YourFunctionAppName>`.

## 🤝 Contributing

Contributions are welcome! Please refer to `CONTRIBUTING.md` (if available) for guidelines.

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.
