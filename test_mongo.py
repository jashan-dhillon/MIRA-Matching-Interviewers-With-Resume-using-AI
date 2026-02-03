from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017')
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # List databases
    print("\nDatabases:", client.list_database_names())
    
    # Check MIRA database
    db = client['mira_drdo']
    print("MIRA Collections:", db.list_collection_names())
    
    # Count documents
    print(f"Users: {db.users.count_documents({})}")
    print(f"Advertisements: {db.advertisements.count_documents({})}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")