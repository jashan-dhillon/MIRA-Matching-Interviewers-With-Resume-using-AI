"""Admin routes Blueprint (users, seed)."""
from flask import Blueprint, jsonify
import bcrypt
from datetime import datetime
from bson import ObjectId

admin_bp = Blueprint('admin', __name__, url_prefix='/api')

# Will be injected from main app
users_collection = None
advertisements_collection = None
items_collection = None
experts_collection = None
panels_collection = None
candidates_collection = None
serialize_doc = None

def init_admin_routes(users_col, adv_col, items_col, experts_col, panels_col, serializer):
    """Initialize the blueprint with database collections."""
    global users_collection, advertisements_collection, items_collection
    global experts_collection, panels_collection, serialize_doc, candidates_collection
    users_collection = users_col
    advertisements_collection = adv_col
    items_collection = items_col
    experts_collection = experts_col
    panels_collection = panels_col
    serialize_doc = serializer
    # Get candidates collection from the same database
    candidates_collection = users_col.database['candidates']


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
    if candidates_collection is not None:
        candidates_collection.delete_many({})
    
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
    
    # Create items for Advertisement 156 with enhanced data
    items_data = [
        {
            'itemNo': 1, 
            'title': 'Scientist-B (Electronics & Communication)', 
            'discipline': 'Electronics & Communication Engineering',
            'description': 'Research in advanced electronics systems, radar technology, and signal processing',
            'essentialQualification': "Bachelor's degree in Electronics & Communication Engineering with valid GATE score",
            'gateCode': 'EC',
            'organization': 'DRDO',
            'equivalentDegrees': ['B.Tech ECE', 'B.E. Electronics', 'M.Tech Communication Systems'],
            'vacancies': {'UR': 5, 'EWS': 2, 'OBC': 3, 'SC': 2, 'ST': 1, 'Total': 13}
        },
        {
            'itemNo': 2, 
            'title': 'Scientist-B (Computer Science)', 
            'discipline': 'Computer Science & Engineering',
            'description': 'Software development, AI/ML research, cybersecurity, and defense applications',
            'essentialQualification': "Bachelor's degree in Computer Science with valid GATE score",
            'gateCode': 'CS',
            'organization': 'DRDO',
            'equivalentDegrees': ['B.Tech CSE', 'B.E. Computer Science', 'MCA', 'M.Tech AI/ML'],
            'vacancies': {'UR': 8, 'EWS': 3, 'OBC': 4, 'SC': 2, 'ST': 1, 'Total': 18}
        },
        {
            'itemNo': 3, 
            'title': 'Scientist-B (Mechanical)', 
            'discipline': 'Mechanical Engineering',
            'description': 'Design and development of mechanical systems, propulsion, and aerospace components',
            'essentialQualification': "Bachelor's degree in Mechanical Engineering with valid GATE score",
            'gateCode': 'ME',
            'organization': 'DRDO',
            'equivalentDegrees': ['B.Tech Mechanical', 'B.E. Mechanical', 'M.Tech Design'],
            'vacancies': {'UR': 4, 'EWS': 1, 'OBC': 2, 'SC': 1, 'ST': 1, 'Total': 9}
        },
        {
            'itemNo': 4, 
            'title': 'Scientist-B (Electrical)', 
            'discipline': 'Electrical Engineering',
            'description': 'Power systems, control systems, and electrical engineering for defense',
            'essentialQualification': "Bachelor's degree in Electrical Engineering with valid GATE score",
            'gateCode': 'EE',
            'organization': 'DRDO',
            'equivalentDegrees': ['B.Tech EE', 'B.E. Electrical', 'M.Tech Power Systems'],
            'vacancies': {'UR': 3, 'EWS': 1, 'OBC': 2, 'SC': 1, 'ST': 0, 'Total': 7}
        },
        {
            'itemNo': 5, 
            'title': 'Scientist-C (Physics)', 
            'discipline': 'Physics',
            'description': 'Applied physics research, optics, and materials science',
            'essentialQualification': "Master's degree in Physics with research experience",
            'gateCode': 'PH',
            'organization': 'DRDO',
            'equivalentDegrees': ['M.Sc Physics', 'M.Tech Applied Physics', 'PhD Physics'],
            'vacancies': {'UR': 2, 'EWS': 1, 'OBC': 1, 'SC': 1, 'ST': 0, 'Total': 5}
        },
        {
            'itemNo': 6, 
            'title': 'Scientist-C (Chemistry)', 
            'discipline': 'Chemistry',
            'description': 'Materials and chemical research, propellants, and explosives',
            'essentialQualification': "Master's degree in Chemistry with research experience",
            'gateCode': 'CY',
            'organization': 'DRDO',
            'equivalentDegrees': ['M.Sc Chemistry', 'M.Tech Materials', 'PhD Chemistry'],
            'vacancies': {'UR': 2, 'EWS': 0, 'OBC': 1, 'SC': 1, 'ST': 0, 'Total': 4}
        },
        {
            'itemNo': 7, 
            'title': 'Scientist-D (Aerospace)', 
            'discipline': 'Aerospace Engineering',
            'description': 'Aerospace engineering, missile systems, and flight dynamics',
            'essentialQualification': "Bachelor's degree in Aerospace Engineering with experience",
            'gateCode': 'AE',
            'organization': 'ADA',
            'equivalentDegrees': ['B.Tech Aerospace', 'M.Tech Aeronautics', 'PhD Aerospace'],
            'vacancies': {'UR': 3, 'EWS': 1, 'OBC': 2, 'SC': 1, 'ST': 0, 'Total': 7}
        }
    ]
    
    inserted_items = []
    for item_data in items_data:
        result = items_collection.insert_one({
            **item_data,
            'advertisementId': adv_156.inserted_id,
            'documentUrl': f"item_{item_data['itemNo']}_document.pdf",
            'requiredBoardSize': 5,
            'createdAt': datetime.now()
        })
        inserted_items.append({'id': result.inserted_id, **item_data})
    
    # Create experts with enhanced skill profiles
    experts_data = [
        {
            'name': 'Dr. Ashok Kumar', 
            'role': 'Chief Scientist - E&C', 
            'category': 'chairperson', 
            
            'skills': ['Electronics', 'Communication Systems', 'Radar Technology', 'Leadership', 'Strategic Planning'],
            'qualifications': ['PhD Electronics', 'M.Tech Communication', 'B.Tech ECE'],
            'specializations': ['Radar Systems', 'Defense Electronics', 'Signal Intelligence'],
            'experience': '30 years',
            'reason': 'Extensive experience in chairing high-level assessment boards. Deep knowledge of electronics and communication policies.'
        },
        {
            'name': 'Dr. Veena Rao', 
            'role': 'Director - Adv. Electronics Lab', 
            'category': 'chairperson', 
            
            'skills': ['Advanced Electronics', 'VLSI Design', 'Project Management', 'Team Leadership'],
            'qualifications': ['PhD VLSI', 'M.Tech Electronics', 'B.Tech ECE'],
            'specializations': ['VLSI Systems', 'Embedded Systems', 'Microelectronics'],
            'experience': '28 years',
            'reason': 'Directorial experience and specific expertise in advanced electronics.'
        },
        {
            'name': 'Dr. Manoj Joshi', 
            'role': 'Senior Scientist - RF Systems', 
            'category': 'departmental', 
            
            'skills': ['RF Engineering', 'Microwave Systems', 'Antenna Design', 'EMI/EMC'],
            'qualifications': ['PhD RF Engineering', 'M.Tech Microwave', 'B.Tech ECE'],
            'specializations': ['RF Systems', 'Microwave Engineering', 'Antenna Arrays'],
            'experience': '20 years',
            'reason': 'Specialist in RF and microwave systems.'
        },
        {
            'name': 'Dr. Pooja Agarwal', 
            'role': 'Scientist-G - DSP', 
            'category': 'departmental', 
            
            'skills': ['Digital Signal Processing', 'Image Processing', 'FPGA', 'Algorithm Design'],
            'qualifications': ['PhD Signal Processing', 'M.Tech DSP', 'B.Tech ECE'],
            'specializations': ['DSP Algorithms', 'Real-time Processing', 'Sensor Fusion'],
            'experience': '18 years',
            'reason': 'Expert in Digital Signal Processing.'
        },
        {
            'name': 'Dr. Sanjay Kulkarni', 
            'role': 'Principal Scientist - Embedded', 
            'category': 'departmental', 
            
            'skills': ['Embedded Systems', 'RTOS', 'Microcontrollers', 'System Integration'],
            'qualifications': ['PhD Embedded Systems', 'M.Tech Computer', 'B.Tech ECE'],
            'specializations': ['Embedded Linux', 'Real-time Systems', 'IoT'],
            'experience': '16 years',
            'reason': 'Strong background in embedded systems.'
        },
        {
            'name': 'Prof. Deepak Sharma', 
            'role': 'Professor - IIT Delhi', 
            'category': 'external', 
            'affiliation': 'Academia',
            
            'skills': ['Communication Theory', 'Wireless Networks', 'Information Theory', 'Research'],
            'qualifications': ['PhD Communications', 'M.Tech Wireless', 'B.Tech ECE'],
            'specializations': ['5G/6G', 'Wireless Communications', 'Network Security'],
            'experience': '22 years',
            'reason': 'Leading academic in communication systems.'
        },
        {
            'name': 'Dr. Rahul Bhatt', 
            'role': 'Chief Engineer - BEL', 
            'category': 'external', 
            'affiliation': 'Industry',
            
            'skills': ['Radar Development', 'System Engineering', 'Project Management', 'Quality Assurance'],
            'qualifications': ['PhD Radar Systems', 'M.Tech Electronics', 'B.Tech ECE'],
            'specializations': ['Phased Array Radar', 'Defense Electronics', 'System Integration'],
            'experience': '25 years',
            'reason': 'Industry expert in radar development.'
        },
        {
            'name': 'Prof. Sneha Iyengar', 
            'role': 'Assoc. Professor - IISc', 
            'category': 'external', 
            'affiliation': 'Academia',
            
            'skills': ['Antenna Design', 'Electromagnetics', 'Computational EM', 'Research'],
            'qualifications': ['PhD Electromagnetics', 'M.Tech Antenna', 'B.Tech ECE'],
            'specializations': ['Antenna Arrays', 'EM Modeling', 'Metamaterials'],
            'experience': '15 years',
            'reason': 'Specialized in antenna design.'
        },
        {
            'name': 'Dr. Rajesh Kumar', 
            'role': 'Advanced Signal Processing', 
            'category': 'departmental', 
            
            'skills': ['Signal Processing', 'Machine Learning', 'Adaptive Filters', 'Spectral Analysis'],
            'qualifications': ['PhD Signal Processing', 'M.Tech SP', 'B.Tech ECE'],
            'specializations': ['Adaptive Signal Processing', 'ML for Signals', 'Radar Signal Processing'],
            'experience': '20 years',
            'reason': 'Extensive background in advanced signal processing algorithms.'
        },
        {
            'name': 'Dr. Priya Sharma', 
            'role': 'Electromagnetic & Antenna Design', 
            'category': 'departmental', 
            
            'skills': ['EM Simulation', 'Antenna Design', 'RF Testing', 'Microwave Components'],
            'qualifications': ['PhD Antenna Engineering', 'M.Tech Microwaves', 'B.Tech ECE'],
            'specializations': ['Phased Arrays', 'Wideband Antennas', 'EMC'],
            'experience': '18 years',
            'reason': '18 years of specialized experience in antenna design.'
        },
        {
            'name': 'Dr. Anil Verma', 
            'role': 'Digital Systems & Embedded', 
            'category': 'departmental', 
            
            'skills': ['Digital Design', 'FPGA', 'Military Electronics', 'System Architecture'],
            'qualifications': ['PhD Digital Systems', 'M.Tech VLSI', 'B.Tech ECE'],
            'specializations': ['Military Grade Electronics', 'Ruggedized Systems', 'High-Rel Design'],
            'experience': '22 years',
            'reason': '22 years in military electronics.'
        },
        {
            'name': 'Dr. Sunita Patel', 
            'role': 'Systems Engineering & Integration', 
            'category': 'departmental', 
            
            'skills': ['Systems Engineering', 'Integration Testing', 'Requirements Management', 'V&V'],
            'qualifications': ['PhD Systems Engineering', 'M.Tech Systems', 'B.Tech ECE'],
            'specializations': ['Large-Scale Integration', 'Defense Systems', 'System Modeling'],
            'experience': '30 years',
            'reason': '30 years of experience in large-scale system integration.'
        },
        {
            'name': 'Dr. Vikram Singh', 
            'role': 'Radar Systems & Signal Intel', 
            'category': 'departmental', 
            
            'skills': ['Radar Systems', 'Signal Intelligence', 'EW Systems', 'Target Tracking'],
            'qualifications': ['PhD Radar Engineering', 'M.Tech Signal Processing', 'B.Tech ECE'],
            'specializations': ['SIGINT', 'Electronic Warfare', 'Tracking Algorithms'],
            'experience': '19 years',
            'reason': 'Specialist in radar systems.'
        },
        # Additional experts for Computer Science
        {
            'name': 'Dr. Amit Desai', 
            'role': 'Principal Scientist - AI/ML', 
            'category': 'departmental', 
            
            'skills': ['Machine Learning', 'Deep Learning', 'Computer Vision', 'NLP'],
            'qualifications': ['PhD Machine Learning', 'M.Tech AI', 'B.Tech CSE'],
            'specializations': ['Defense AI', 'Autonomous Systems', 'Neural Networks'],
            'experience': '15 years',
            'reason': 'Leading expert in AI/ML for defense applications.'
        },
        {
            'name': 'Prof. Kavita Menon', 
            'role': 'Professor - IIT Bombay', 
            'category': 'external', 
            'affiliation': 'Academia',
            
            'skills': ['Cybersecurity', 'Cryptography', 'Network Security', 'Research'],
            'qualifications': ['PhD Cryptography', 'M.Tech Security', 'B.Tech CSE'],
            'specializations': ['Post-Quantum Crypto', 'Secure Systems', 'Blockchain'],
            'experience': '20 years',
            'reason': 'Expert in cybersecurity and cryptography.'
        },
        # Additional experts for Mechanical/Aerospace
        {
            'name': 'Dr. Ravi Shankar', 
            'role': 'Chief Scientist - Propulsion', 
            'category': 'chairperson', 
            
            'skills': ['Propulsion Systems', 'Aerodynamics', 'CFD', 'Thermodynamics'],
            'qualifications': ['PhD Aerospace', 'M.Tech Propulsion', 'B.Tech Mechanical'],
            'specializations': ['Rocket Propulsion', 'Jet Engines', 'Missile Systems'],
            'experience': '28 years',
            'reason': 'Expert in propulsion and aerospace systems.'
        },
        {
            'name': 'Dr. Neha Gupta', 
            'role': 'Senior Scientist - Materials', 
            'category': 'departmental', 
            
            'skills': ['Materials Science', 'Composites', 'Metallurgy', 'Testing'],
            'qualifications': ['PhD Materials', 'M.Tech Metallurgy', 'B.Tech Mechanical'],
            'specializations': ['Aerospace Materials', 'Composites', 'Failure Analysis'],
            'experience': '14 years',
            'reason': 'Specialist in advanced materials for aerospace.'
        }
    ]
    
    for expert_data in experts_data:
        experts_collection.insert_one({
            **expert_data,
            'email': f"{expert_data['name'].lower().replace(' ', '.').replace('dr.', '').replace('prof.', '').strip('.')}@drdo.gov.in",
            'createdAt': datetime.now()
        })
    
    # Create sample candidates for testing AI matching
    candidates_data = [
        # Candidates for Item 1 (Electronics & Communication)
        {
            'name': 'Rahul Verma',
            'appliedItemId': inserted_items[0]['id'],
            'skills': ['VLSI Design', 'Signal Processing', 'Embedded Systems', 'FPGA'],
            'qualifications': ['B.Tech ECE - IIT Kharagpur'],
            'gateScore': 756,
            'gatePaper': 'EC',
            'experience': 'Intern at Samsung R&D',
            'education': 'B.Tech Electronics & Communication Engineering'
        },
        {
            'name': 'Priya Nair',
            'appliedItemId': inserted_items[0]['id'],
            'skills': ['RF Engineering', 'Antenna Design', 'EM Simulation', 'HFSS'],
            'qualifications': ['M.Tech Microwave - IISc'],
            'gateScore': 812,
            'gatePaper': 'EC',
            'experience': '2 years at ISRO',
            'education': 'M.Tech Microwave Engineering'
        },
        {
            'name': 'Amit Patel',
            'appliedItemId': inserted_items[0]['id'],
            'skills': ['DSP', 'Communication Systems', 'MATLAB', 'Python'],
            'qualifications': ['B.Tech ECE - NIT Trichy'],
            'gateScore': 698,
            'gatePaper': 'EC',
            'experience': 'Research project on 5G',
            'education': 'B.Tech Electronics & Communication Engineering'
        },
        # Candidates for Item 2 (Computer Science)
        {
            'name': 'Sneha Sharma',
            'appliedItemId': inserted_items[1]['id'],
            'skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow'],
            'qualifications': ['B.Tech CSE - IIT Delhi'],
            'gateScore': 845,
            'gatePaper': 'CS',
            'experience': 'ML Intern at Google',
            'education': 'B.Tech Computer Science Engineering'
        },
        {
            'name': 'Vikrant Singh',
            'appliedItemId': inserted_items[1]['id'],
            'skills': ['Cybersecurity', 'Penetration Testing', 'Network Security', 'Cryptography'],
            'qualifications': ['M.Tech Information Security - IIT Bombay'],
            'gateScore': 789,
            'gatePaper': 'CS',
            'experience': '1 year at Cisco',
            'education': 'M.Tech Information Security'
        },
        {
            'name': 'Ananya Reddy',
            'appliedItemId': inserted_items[1]['id'],
            'skills': ['Java', 'System Design', 'Distributed Systems', 'Cloud Computing'],
            'qualifications': ['B.Tech CSE - BITS Pilani'],
            'gateScore': 721,
            'gatePaper': 'CS',
            'experience': 'SDE Intern at Amazon',
            'education': 'B.Tech Computer Science Engineering'
        },
        # Candidates for Item 7 (Aerospace)
        {
            'name': 'Karthik Menon',
            'appliedItemId': inserted_items[6]['id'],
            'skills': ['CFD', 'Aerodynamics', 'ANSYS', 'Flight Dynamics'],
            'qualifications': ['M.Tech Aerospace - IIT Madras'],
            'gateScore': 834,
            'gatePaper': 'AE',
            'experience': '2 years at HAL',
            'education': 'M.Tech Aerospace Engineering'
        },
        {
            'name': 'Divya Krishnan',
            'appliedItemId': inserted_items[6]['id'],
            'skills': ['Propulsion', 'Rocket Design', 'Thermodynamics', 'CAD'],
            'qualifications': ['B.Tech Aerospace - IIT Bombay'],
            'gateScore': 778,
            'gatePaper': 'AE',
            'experience': 'Research at ISRO',
            'education': 'B.Tech Aerospace Engineering'
        }
    ]
    
    if candidates_collection is not None:
        for candidate_data in candidates_data:
            candidates_collection.insert_one({
                **candidate_data,
                'status': 'applied',
                'createdAt': datetime.now()
            })
    
    return jsonify({
        'message': 'Database seeded successfully!',
        'counts': {
            'users': 1,
            'advertisements': 5,
            'items': len(items_data),
            'experts': len(experts_data),
            'candidates': len(candidates_data)
        }
    })

