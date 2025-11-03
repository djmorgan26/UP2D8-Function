import os
import sys
import pymongo
from dotenv import load_dotenv

# Add the project root to sys.path to enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.key_vault_client import get_secret_client

def test_mongo_connection():
    load_dotenv()
    print("Running MongoDB connection test...")
    try:
        # Get configuration
        secret_client = get_secret_client()

        cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

        # Connect to Cosmos DB
        client = pymongo.MongoClient(cosmos_db_connection_string)
        db = client.up2d8

        print("Successfully connected to MongoDB.")

        # Inspect collections
        collections = db.list_collection_names()
        print(f"Collections found: {collections}")

        # Inspect 'users' collection
        if 'users' in collections:
            print("\n--- Inspecting 'users' collection ---")
            users_collection = db.users
            user_count = users_collection.count_documents({})
            print(f"Found {user_count} documents in 'users'.")
            if user_count > 0:
                sample_user = users_collection.find_one()
                print(f"Sample user document: {sample_user}")
                expected_keys = ['email', 'topics', 'preferences']
                missing_keys = [k for k in expected_keys if k not in sample_user]
                if missing_keys:
                    print(f"WARNING: Sample user document is missing expected keys: {missing_keys}")
                else:
                    print("Sample user document has the expected keys.")
        else:
            print("\n'users' collection not found.")

        # Inspect 'articles' collection
        if 'articles' in collections:
            print("\n--- Inspecting 'articles' collection ---")
            articles_collection = db.articles
            article_count = articles_collection.count_documents({})
            print(f"Found {article_count} documents in 'articles'.")
            if article_count > 0:
                sample_article = articles_collection.find_one()
                print(f"Sample article document: {sample_article}")
                expected_keys = ['title', 'link', 'summary', 'published', 'processed']
                missing_keys = [k for k in expected_keys if k not in sample_article]
                if missing_keys:
                    print(f"WARNING: Sample article document is missing expected keys: {missing_keys}")
                else:
                    print("Sample article document has the expected keys.")
        else:
            print("\n'articles' collection not found.")

    except Exception as e:
        print(f"MongoDB test failed: {e}")

if __name__ == "__main__":
    test_mongo_connection()
