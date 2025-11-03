import os
import sys
import pymongo
from dotenv import load_dotenv

# Add the project root to sys.path to enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.key_vault_client import get_secret_client

def run_migration():
    load_dotenv()
    print("Running database migration...")
    try:
        # Get configuration
        secret_client = get_secret_client()

        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

        # Connect to Cosmos DB
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8

        print("Successfully connected to MongoDB.")

        # Migrate 'users' collection
        print("\n--- Migrating 'users' collection ---")
        users_collection = db.users
        users_collection.update_many({'topics': {'$exists': False}}, {'$set': {'topics': []}})
        users_collection.update_many({'preferences': {'$exists': False}}, {'$set': {'preferences': 'concise'}})
        print("'users' collection migration complete.")

        # Migrate 'articles' collection
        print("\n--- Migrating 'articles' collection ---")
        articles_collection = db.articles
        articles_collection.update_many({}, {
            '$rename': {
                'source_url': 'link',
                'content': 'summary',
                'published_at': 'published'
            }
        })
        articles_collection.update_many({'processed': {'$exists': False}}, {'$set': {'processed': False}})
        articles_collection.update_many({}, {
            '$unset': {
                'id': "",
                'source_id': "",
                'fetched_at': "",
                'processing_status': "",
                'companies': "",
                'industries': ""
            }
        })
        print("'articles' collection migration complete.")

        print("\nDatabase migration finished successfully.")

    except Exception as e:
        print(f"Database migration failed: {e}")

if __name__ == "__main__":
    run_migration()
