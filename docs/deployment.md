## Azure Function App Deployment Configuration

This document outlines the crucial configurations required in Azure and GitHub for the Azure Function App deployment to work correctly and securely.

### 1. GitHub Secrets for Azure Authentication

The GitHub Actions workflow uses an Azure Service Principal to authenticate and deploy to your Azure resources. You need to create this Service Principal and store its credentials as a GitHub Secret.

*   **Create an Azure Service Principal:**
    You can do this via the Azure CLI. Run the following command in your terminal:
    ```bash
    az ad sp create-for-rbac --name "github-actions-up2d8" --role contributor --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID>/resourceGroups/<YOUR_RESOURCE_GROUP> --json-auth
    ```
    *   Replace `<YOUR_SUBSCRIPTION_ID>` with your Azure subscription ID.
    *   Replace `<YOUR_RESOURCE_GROUP>` with the name of the resource group where your Function App is located (e.g., `up2d8-resource-group`).
    *   This command will output a JSON object. **Copy this entire JSON object.**

*   **Add to GitHub Secrets:**
    1.  Go to your GitHub repository.
    2.  Navigate to **Settings > Secrets and variables > Actions**.
    3.  Click on **New repository secret**.
    4.  Name the secret `AZURE_CREDENTIALS`.
    5.  Paste the JSON output you copied from the Azure CLI into the "Secret value" field.
    6.  Click **Add secret**.

### 2. Azure Function App Settings

Ensure your Function App in Azure is correctly configured:

*   **Python Version:**
    *   Verify that your Azure Function App's runtime stack is set to **Python 3.9** (or whatever version you specify in `deploy.yml`). You can check this in the Azure Portal under your Function App's **Configuration > General settings**.

*   **Managed Identity (for Key Vault Access):**
    *   The Function App uses a Managed Identity to securely access secrets from Azure Key Vault.
    *   Go to your Function App in the Azure Portal.
    *   Under **Settings > Identity**, enable the **System assigned** identity.

*   **Key Vault Access Policy:**
    *   After enabling the Managed Identity, you need to grant it permissions to your Key Vault.
    *   Go to your Azure Key Vault resource.
    *   Navigate to **Access policies**.
    *   Click **Create**.
    *   Under "Secret permissions", select **Get**.
    *   Under "Principal", search for the name of your Function App (it will appear as a Managed Identity).
    *   Click **Review + create** and then **Create**.

*   **Application Settings (Environment Variables):**
    *   The Function App relies on several environment variables for its operation (e.g., SMTP details, sender email). These need to be configured as Application Settings in your Azure Function App.
    *   Go to your Function App in the Azure Portal.
    *   Navigate to **Configuration > Application settings**.
    *   Add the following settings (and any others your application might need), ensuring their values are correct:
        *   `BREVO_SMTP_USER`
        *   `BREVO_SMTP_HOST`
        *   `BREVO_SMTP_PORT`
        *   `SENDER_EMAIL`
        *   (Note: `COSMOS-DB-CONNECTION-STRING-UP2D8`, `UP2D8-GEMINI-API-Key`, and `UP2D8-SMTP-KEY` are fetched from Key Vault, so they don't need to be directly in Application Settings, but the Key Vault URL might be needed if not implicitly handled by `DefaultAzureCredential` in Azure environment).

By configuring these items, your GitHub Actions workflow will be able to deploy the Function App, and the deployed Function App will have the necessary permissions and settings to run correctly and access your Key Vault secrets.
