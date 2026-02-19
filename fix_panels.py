
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client['mira_drdo']
panels_col = db['panels']

print("--- Fixing Malformed Panels ---")

# Find panels with 'expertIds' but no 'panelists'
bad_panels = list(panels_col.find({
    'expertIds': {'$exists': True},
    'panelists': {'$exists': False}
}))

print(f"Found {len(bad_panels)} malformed panels.")

for p in bad_panels:
    print(f"Fixing Panel {p['_id']} for Item {p.get('itemId')}")
    
    expert_ids = p.get('expertIds', [])
    panelists = []
    
    for eid in expert_ids:
        panelists.append({
            'expertId': eid, # Already ObjectId if stored correctly
            'status': 'invited',
            'panel_role': 'Member',
            'invitedAt': p.get('createdAt', datetime.now()),
            'respondedAt': None
        })
        
    result = panels_col.update_one(
        {'_id': p['_id']},
        {
            '$set': {'panelists': panelists},
            '$unset': {'expertIds': ""}
        }
    )
    print(f"  -> Updated: {result.modified_count}")

print("--- Fix Complete ---")
