
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
print(f"Connecting to: {mongo_uri}")

client = MongoClient(mongo_uri)
db_name = 'mira_drdo'
db = client[db_name]

print(f"Database: {db_name}")
print("Collections:", db.list_collection_names())

users_col = db['users']
count = users_col.count_documents({})
experts_col = db['experts']
exp_count = experts_col.count_documents({})
print(f"User Count: {count}")
print(f"Expert Count: {exp_count}")

import bcrypt

with open('debug_output.txt', 'w') as f:
    f.write(f"User Count: {count}\n")
    f.write(f"Expert Count: {exp_count}\n")

    expert = users_col.find_one({'username': 'expert1'})
    if expert:
        f.write(f"FOUND 'expert1'!\n")
        f.write(f"Email: {expert.get('email')}\n")
        f.write(f"Role: {expert.get('role')}\n")
        
        # Check password
        if bcrypt.checkpw(b'expert123', expert['password']):
            f.write("PASSWORD VALID: Yes\n")
        else:
            f.write("PASSWORD VALID: NO - Hash mismatch\n")
    else:
        f.write("User 'expert1' NOT FOUND\n")
        
    # Debug all users briefly
    f.write("\nAll Users:\n")
    for u in users_col.find({}, {'username': 1, 'email': 1}):
        f.write(f"- {u.get('username')} ({u.get('email')})\n")
    
print("Debug finished. Check debug_output.txt")
