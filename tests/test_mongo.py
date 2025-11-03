import os
import sys
import pytest
import pymongo
from dotenv import load_dotenv

# Add the project root to sys.path to enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.key_vault_client import get_secret_client

@pytest.fixture(scope="module")
def mongo_client():
    load_dotenv()
    secret_client = get_secret_client()
    cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
    client = pymongo.MongoClient(cosmos_db_connection_string)
    yield client
    client.close()

@pytest.fixture(scope="module")
def up2d8_db(mongo_client):
    return mongo_client.up2d8

def test_mongo_connection(mongo_client):
    # Simply connecting and closing should be enough to test connection
    assert mongo_client.admin.command('ping')['ok'] == 1

def test_collections_exist(up2d8_db):
    collections = up2d8_db.list_collection_names()
    assert "users" in collections
    assert "articles" in collections
    assert "rss_feeds" in collections

def test_users_collection_schema(up2d8_db):
    users_collection = up2d8_db.users
    sample_user = users_collection.find_one()
    if sample_user:
        assert "email" in sample_user
        assert "subscribed_tags" in sample_user # Updated from 'topics'
        assert isinstance(sample_user["subscribed_tags"], list)
        assert "preferences" in sample_user
    else:
        pytest.skip("No user documents found to test schema.")

def test_articles_collection_schema(up2d8_db):
    articles_collection = up2d8_db.articles
    sample_article = articles_collection.find_one()
    if sample_article:
        assert "title" in sample_article
        assert "link" in sample_article
        assert "summary" in sample_article
        assert "published" in sample_article
        assert "processed" in sample_article
        assert "tags" in sample_article # New field
        assert isinstance(sample_article["tags"], list)
    else:
        pytest.skip("No article documents found to test schema.")

def test_rss_feeds_collection_schema(up2d8_db):
    rss_feeds_collection = up2d8_db.rss_feeds
    sample_feed = rss_feeds_collection.find_one()
    if sample_feed:
        assert "url" in sample_feed
    else:
        pytest.skip("No RSS feed documents found to test schema.")