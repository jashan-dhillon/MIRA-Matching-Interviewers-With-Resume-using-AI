"""Authentication routes Blueprint."""
from flask import Blueprint, request, jsonify, session
import bcrypt
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# These will be injected from main app
users_collection = None
validate_captcha = None

def init_auth_routes(users_col, captcha_validator):
    """Initialize the blueprint with database collection and captcha validator."""
    global users_collection, validate_captcha
    users_collection = users_col
    validate_captcha = captcha_validator


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Validate CAPTCHA first
    captcha_input = data.get('captcha', '')
    if not validate_captcha(captcha_input):
        return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400
    
    # Check if user exists
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400
    
    # Hash password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user = {
        'fullName': data['fullName'],
        'email': data['email'],
        'password': hashed_password,
        'role': data.get('role', 'candidate'),
        'createdAt': datetime.now()
    }
    
    result = users_collection.insert_one(user)
    
    return jsonify({
        'message': 'User registered successfully',
        'userId': str(result.inserted_id)
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    # Validate CAPTCHA first
    captcha_input = data.get('captcha', '')
    if not validate_captcha(captcha_input):
        return jsonify({'error': 'Invalid CAPTCHA. Please try again.'}), 400
    
    user = users_collection.find_one({'email': data['email']})
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Set session
    session['user_id'] = str(user['_id'])
    session['email'] = user['email']
    session['role'] = user['role']
    session['fullName'] = user['fullName']
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': str(user['_id']),
            'fullName': user['fullName'],
            'email': user['email'],
            'role': user['role']
        }
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'user': {
            'id': session['user_id'],
            'fullName': session['fullName'],
            'email': session['email'],
            'role': session['role']
        }
    })
