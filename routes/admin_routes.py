"""Admin routes Blueprint (users, seed)."""
from flask import Blueprint, jsonify
import bcrypt
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api')

# Will be injected from main app
users_collection = None
advertisements_collection = None
items_collection = None
experts_collection = None
panels_collection = None
serialize_doc = None

def init_admin_routes(users_col, adv_col, items_col, experts_col, panels_col, serializer):
    """Initialize the blueprint with database collections."""
    global users_collection, advertisements_collection, items_collection
    global experts_collection, panels_collection, serialize_doc
    users_collection = users_col
    advertisements_collection = adv_col
    items_collection = items_col
    experts_collection = experts_col
    panels_collection = panels_col
    serialize_doc = serializer


@admin_bp.route('/users', methods=['GET'])
def get_users():
    users = list(users_collection.find({}, {'password': 0}))  # Exclude passwords
    return jsonify(serialize_doc(users))


@admin_bp.route('/seed', methods=['POST'])
def seed_data():
    # Clear existing data
    users_collection.delete_many({})
    advertisements_collection.delete_many({})
    items_collection.delete_many({})
    experts_collection.delete_many({})
    panels_collection.delete_many({})
    
    # Create admin user
    admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
    users_collection.insert_one({
        'fullName': 'Admin User',
        'email': 'admin@drdo.gov.in',
        'password': admin_password,
        'role': 'admin',
        'createdAt': datetime.now()
    })
    
    # Create advertisements
    adv_156 = advertisements_collection.insert_one({
        'advertisementNo': 156,
        'title': 'Advertisement No. 156',
        'status': 'active',
        'createdAt': datetime.now()
    })
    
    advertisements_collection.insert_one({
        'advertisementNo': 152,
        'title': 'Advertisement No. 152',
        'status': 'active',
        'createdAt': datetime.now()
    })
    
    advertisements_collection.insert_one({
        'advertisementNo': 154,
        'title': 'Advertisement No. 154',
        'status': 'active',
        'createdAt': datetime.now()
    })
    
    advertisements_collection.insert_one({
        'advertisementNo': 153,
        'title': 'Advertisement No. 153',
        'status': 'completed',
        'createdAt': datetime.now()
    })
    
    advertisements_collection.insert_one({
        'advertisementNo': 151,
        'title': 'Advertisement No. 151',
        'status': 'completed',
        'createdAt': datetime.now()
    })
    
    # Create items for Advertisement 156
    items_data = [
        {'itemNo': 1, 'title': 'Scientist-B (Electronics & Communication)', 'description': 'Research in advanced electronics systems'},
        {'itemNo': 2, 'title': 'Scientist-B (Computer Science)', 'description': 'Software development and AI/ML research'},
        {'itemNo': 3, 'title': 'Scientist-B (Mechanical)', 'description': 'Design and development of mechanical systems'},
        {'itemNo': 4, 'title': 'Scientist-B (Electrical)', 'description': 'Power systems and electrical engineering'},
        {'itemNo': 5, 'title': 'Scientist-C (Physics)', 'description': 'Applied physics research'},
        {'itemNo': 6, 'title': 'Scientist-C (Chemistry)', 'description': 'Materials and chemical research'},
        {'itemNo': 7, 'title': 'Scientist-D (Aerospace)', 'description': 'Aerospace engineering and design'}
    ]
    
    for item_data in items_data:
        items_collection.insert_one({
            'itemNo': item_data['itemNo'],
            'advertisementId': adv_156.inserted_id,
            'title': item_data['title'],
            'description': item_data['description'],
            'documentUrl': f"item_{item_data['itemNo']}_document.pdf",
            'requiredBoardSize': 5,
            'createdAt': datetime.now()
        })
    
    # Create experts
    experts_data = [
        {'name': 'Dr. Ashok Kumar', 'role': 'Chief Scientist - E&C', 'category': 'chairperson', 'relevanceScore': 96, 'reason': 'Extensive experience in chairing high-level assessment boards. Deep knowledge of electronics and communication policies.'},
        {'name': 'Dr. Veena Rao', 'role': 'Director - Adv. Electronics Lab', 'category': 'chairperson', 'relevanceScore': 94, 'reason': 'Directorial experience and specific expertise in advanced electronics.'},
        {'name': 'Dr. Manoj Joshi', 'role': 'Senior Scientist - RF Systems', 'category': 'departmental', 'relevanceScore': 91, 'reason': 'Specialist in RF and microwave systems.'},
        {'name': 'Dr. Pooja Agarwal', 'role': 'Scientist-G - DSP', 'category': 'departmental', 'relevanceScore': 89, 'reason': 'Expert in Digital Signal Processing.'},
        {'name': 'Dr. Sanjay Kulkarni', 'role': 'Principal Scientist - Embedded', 'category': 'departmental', 'relevanceScore': 87, 'reason': 'Strong background in embedded systems.'},
        {'name': 'Prof. Deepak Sharma', 'role': 'Professor - IIT Delhi', 'category': 'external', 'affiliation': 'Academia', 'relevanceScore': 90, 'reason': 'Leading academic in communication systems.'},
        {'name': 'Dr. Rahul Bhatt', 'role': 'Chief Engineer - BEL', 'category': 'external', 'affiliation': 'Industry', 'relevanceScore': 88, 'reason': 'Industry expert in radar development.'},
        {'name': 'Prof. Sneha Iyengar', 'role': 'Assoc. Professor - IISc', 'category': 'external', 'affiliation': 'Academia', 'relevanceScore': 87, 'reason': 'Specialized in antenna design.'},
        {'name': 'Dr. Rajesh Kumar', 'role': 'Advanced Signal Processing', 'category': 'departmental', 'relevanceScore': 95, 'reason': 'Extensive background in advanced signal processing algorithms.'},
        {'name': 'Dr. Priya Sharma', 'role': 'Electromagnetic & Antenna Design', 'category': 'departmental', 'relevanceScore': 92, 'reason': '18 years of specialized experience in antenna design.'},
        {'name': 'Dr. Anil Verma', 'role': 'Digital Systems & Embedded', 'category': 'departmental', 'relevanceScore': 89, 'reason': '22 years in military electronics.'},
        {'name': 'Dr. Sunita Patel', 'role': 'Systems Engineering & Integration', 'category': 'departmental', 'relevanceScore': 94, 'reason': '30 years of experience in large-scale system integration.'},
        {'name': 'Dr. Vikram Singh', 'role': 'Radar Systems & Signal Intel', 'category': 'departmental', 'relevanceScore': 91, 'reason': 'Specialist in radar systems.'}
    ]
    
    for expert_data in experts_data:
        experts_collection.insert_one({
            **expert_data,
            'email': f"{expert_data['name'].lower().replace(' ', '.').replace('dr.', '').replace('prof.', '').strip('.')}@drdo.gov.in",
            'createdAt': datetime.now()
        })
    
    return jsonify({'message': 'Database seeded successfully!'})
