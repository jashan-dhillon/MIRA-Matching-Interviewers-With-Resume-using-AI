
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

load_dotenv()

mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client['mira_drdo']
users = db['users']
experts = db['experts']

# Find Dr. Ashok Kumar
ashok = experts.find_one({'name': 'Dr. Ashok Kumar'})
if not ashok:
    print("❌ Dr. Ashok Kumar expert profile not found! Run seed first.")
    exit()

print(f"Found Expert: {ashok['name']} (ID: {ashok['_id']})")

# Check if user already exists (by email or username)
username = 'expert1'
email = ashok.get('email', 'nehalsingh01704@gmail.com')

existing_user = users.find_one({'$or': [{'username': username}, {'email': email}]})

if existing_user:
    print(f"⚠️ User already exists: {existing_user.get('username')} / {existing_user.get('email')}")
    # Force update password just in case
    hashed = bcrypt.hashpw('expert123'.encode('utf-8'), bcrypt.gensalt())
    users.update_one({'_id': existing_user['_id']}, {'$set': {'password': hashed, 'role': 'expert', 'username': username}})
    print("✅ Password and Role updated to 'expert123' / 'expert'")
else:
    # Create User
    hashed = bcrypt.hashpw('expert123'.encode('utf-8'), bcrypt.gensalt())
    new_user = {
        'username': username,
        'email': email,
        'password': hashed,
        'role': 'expert',
        'expertId': str(ashok['_id']),
        'fullName': ashok['name'],
        'createdAt': datetime.now()
    }
    users.insert_one(new_user)
    print(f"✅ User '{username}' created successfully!")

print("\nTry logging in now with:\nUsername: expert1\nPassword: expert123")
