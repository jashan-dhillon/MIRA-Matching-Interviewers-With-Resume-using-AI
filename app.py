"""
MIRA DRDO - Recruitment and Assessment System
Main Application Entry Point

This is the refactored version using Flask Blueprints for better organization.
"""
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import os
import random
import string
from dotenv import load_dotenv

# Import Blueprints
from routes.auth_routes import auth_bp, init_auth_routes
from routes.advertisement_routes import adv_bp, init_adv_routes
from routes.item_routes import item_bp, init_item_routes
from routes.expert_routes import expert_bp, init_expert_routes
from routes.panel_routes import panel_bp, init_panel_routes
from routes.admin_routes import admin_bp, init_admin_routes
from routes.pdf_routes import pdf_bp, init_pdf_routes
from routes.matching_routes import matching_bp, init_matching_routes

load_dotenv()

# ==================== APP CONFIGURATION ====================
app = Flask(__name__, static_folder='fe')

# Get secret key from environment (no fallback in production!)
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required!")
app.secret_key = SECRET_KEY

# CORS configuration
CORS(app, supports_credentials=True)

# ==================== DATABASE CONNECTION ====================
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is required!")
client = MongoClient(MONGODB_URI)
db = client['mira_drdo']

# Collections
users_collection = db['users']
advertisements_collection = db['advertisements']
items_collection = db['items']
experts_collection = db['experts']
panels_collection = db['panels']
candidates_collection = db['candidates']


# ==================== HELPER FUNCTIONS ====================
from bson import ObjectId

def serialize_doc(doc):
    """Convert MongoDB ObjectId to string for JSON serialization."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = [serialize_doc(item) for item in value]
            else:
                result[key] = value
        return result
    return doc


def generate_captcha_code(length=6):
    """Generate a random alphanumeric CAPTCHA code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def validate_captcha(user_input):
    """Validate the user's CAPTCHA input against the session-stored code."""
    if 'captcha_code' not in session:
        return False
    stored_code = session.get('captcha_code', '')
    # Clear the CAPTCHA after validation attempt (one-time use)
    session.pop('captcha_code', None)
    return user_input.upper() == stored_code.upper()


# ==================== STATIC FILE ROUTES ====================
@app.route('/')
def index():
    return send_from_directory('fe', 'login.html')


@app.route('/fe/<path:filename>')
def serve_static(filename):
    return send_from_directory('fe', filename)


@app.route('/styles/<path:filename>')
def serve_styles(filename):
    return send_from_directory('styles', filename)


@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Serve uploaded PDF files."""
    return send_from_directory('uploads', filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)


# ==================== CAPTCHA ROUTE ====================
@app.route('/api/captcha', methods=['GET'])
def get_captcha():
    """Generate a new CAPTCHA and store it in the session."""
    code = generate_captcha_code()
    session['captcha_code'] = code.upper()
    return jsonify({
        'captcha': code,
        'message': 'CAPTCHA generated. Submit this code with your login/signup request.'
    })


# ==================== INITIALIZE BLUEPRINTS ====================
# Initialize each blueprint with required dependencies
init_auth_routes(users_collection, validate_captcha)
init_adv_routes(advertisements_collection, items_collection, serialize_doc)
init_item_routes(items_collection, serialize_doc, advertisements_collection, panels_collection, experts_collection)
init_expert_routes(experts_collection, serialize_doc, panels_collection, items_collection)
init_panel_routes(panels_collection, serialize_doc)
init_admin_routes(
    users_collection,
    advertisements_collection,
    items_collection,
    experts_collection,
    panels_collection,
    serialize_doc
)
init_pdf_routes(advertisements_collection, items_collection, serialize_doc)
init_matching_routes(items_collection, experts_collection, candidates_collection, serialize_doc)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(adv_bp)
app.register_blueprint(item_bp)
app.register_blueprint(expert_bp)
app.register_blueprint(panel_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(pdf_bp)
app.register_blueprint(matching_bp)


# ==================== MAIN ====================
if __name__ == '__main__':
    print("\n🚀 MIRA DRDO Server Starting...")
    print(f"   MongoDB: {MONGODB_URI}")
    print(f"   Local: http://localhost:5001")
    print(f"   Login: http://localhost:5001/fe/login.html")
    print("\n📌 First time? Call POST /api/seed to populate database\n")
    app.run(debug=True, use_reloader=False, port=5001)

