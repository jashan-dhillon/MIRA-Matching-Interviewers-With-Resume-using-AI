
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client['mira_drdo']
experts_col = db['experts']
panels_col = db['panels']
users_col = db['users']

print("--- Debugging Invites ---")

# 1. Get Expert1
user = users_col.find_one({'username': 'expert1'})
if not user:
    print("❌ User 'expert1' not found!")
    exit()

expert_id_str = user.get('expertId')
print(f"User: {user['username']}")
print(f"Expert ID (from user): {expert_id_str}")

if not expert_id_str:
    print("❌ User has no expertId linked!")
    exit()
    
# Dump ALL Panels
print(f"\n--- Checking ALL Panels in DB ---")
all_p = list(panels_col.find())
print(f"Total Panels: {len(all_p)}")
for p in all_p:
    print(f"Panel ID: {p['_id']}")
    print(f"  Item ID: {p.get('itemId')}")
    print(f"  Status: {p.get('status')}")
    if 'panelists' in p:
        print(f"  Panelists Count: {len(p['panelists'])}")
        # Check IDs
        ids = [str(x.get('expertId')) for x in p['panelists']]
        print(f"  Expert IDs in Panel: {ids}")
    else:
        print(f"  ❌ No 'panelists' key!")
        print(f"  Keys found: {list(p.keys())}")
        
print("--- End Dump ---")
