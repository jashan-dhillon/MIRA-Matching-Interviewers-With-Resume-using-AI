
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

client = MongoClient('mongodb://localhost:27017/')
db = client['mira_db']
users = db['users']

print("--- Checking Users ---")
for user in users.find():
    print(f"User: {user.get('username', 'N/A')} | Email: {user.get('email')} | Role: {user.get('role')}")
    if user.get('username') == 'expert1':
        print(f"   -> Found expert1. checking password 'expert123'...")
        if bcrypt.checkpw(b'expert123', user['password']):
            print("   -> Password MATCHES!")
        else:
            print("   -> Password DOES NOT MATCH!")

print("--- End ---")
