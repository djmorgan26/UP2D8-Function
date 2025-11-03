import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

_secret_client = None

def get_secret_client() -> SecretClient:
    global _secret_client
    if _secret_client is None:
        load_dotenv()
        key_vault_uri = os.environ["KEY_VAULT_URI"]
        credential = DefaultAzureCredential()
        _secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
    return _secret_client
