"""PDF Upload and Processing routes Blueprint."""
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import sys

# Add parent directory to path for ai module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pdf_bp = Blueprint('pdf', __name__, url_prefix='/api/pdf')

# Will be injected from main app
advertisements_collection = None
items_collection = None
serialize_doc = None

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}


def init_pdf_routes(adv_col, items_col, serializer):
    """Initialize the blueprint with database collections."""
    global advertisements_collection, items_collection, serialize_doc
    advertisements_collection = adv_col
    items_collection = items_col
    serialize_doc = serializer
    
    # Create uploads folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@pdf_bp.route('/upload', methods=['POST'])
def upload_advertisement_pdf():
    """
    Upload and process an advertisement PDF.
    Extracts data and creates advertisement + items in database.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
    
    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract data from PDF
        from ai.pdf_extractor import extract_advertisement
        extracted_data = extract_advertisement(filepath)
        
        # Check if advertisement already exists
        existing_adv = advertisements_collection.find_one({
            'advertisementNo': extracted_data['advertisementNo']
        })
        
        if existing_adv:
            return jsonify({
                'error': f"Advertisement No. {extracted_data['advertisementNo']} already exists.",
                'existingId': str(existing_adv['_id'])
            }), 409
        
        # Create advertisement in database
        advertisement = {
            'advertisementNo': extracted_data['advertisementNo'],
            'title': extracted_data['title'],
            'totalVacancies': extracted_data['totalVacancies'],
            'closingDate': extracted_data['closingDate'],
            'organizations': extracted_data.get('organizations', {}),
            'generalInfo': extracted_data.get('generalInfo', {}),
            'status': 'active',
            'pdfFile': filename,
            'extractedData': extracted_data,
            'createdAt': datetime.now()
        }
        
        adv_result = advertisements_collection.insert_one(advertisement)
        adv_id = adv_result.inserted_id
        
        # Create items (job roles) in database
        items_created = []
        for item_data in extracted_data.get('items', []):
            item = {
                'itemNo': item_data['itemNo'],
                'advertisementId': adv_id,
                'discipline': item_data.get('discipline', ''),
                'title': f"Scientist 'B' - {item_data.get('discipline', 'Unknown')}",
                'description': item_data.get('essentialQualification', ''),
                'essentialQualification': item_data.get('essentialQualification', ''),
                'organization': item_data.get('organization', 'DRDO'),
                'vacancies': item_data.get('vacancies', {}),
                'subOrganizations': item_data.get('subOrganizations', []),
                'gateCode': item_data.get('gateCode'),
                'equivalentDegrees': item_data.get('equivalentDegrees', []),
                'requiredBoardSize': 5,
                'createdAt': datetime.now()
            }
            
            item_result = items_collection.insert_one(item)
            item['_id'] = str(item_result.inserted_id)
            items_created.append(item)
        
        return jsonify({
            'message': 'Advertisement uploaded and processed successfully!',
            'advertisement': {
                '_id': str(adv_id),
                'advertisementNo': extracted_data['advertisementNo'],
                'title': extracted_data['title'],
                'totalVacancies': extracted_data['totalVacancies'],
                'closingDate': extracted_data['closingDate'],
                'itemsCount': len(items_created)
            },
            'itemsCreated': len(items_created),
            'extractedData': extracted_data
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to process PDF: {str(e)}'
        }), 500


@pdf_bp.route('/preview', methods=['POST'])
def preview_pdf_extraction():
    """
    Preview extraction from PDF without saving to database.
    Useful for admin to verify data before confirming upload.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
    
    try:
        # Save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"preview_{filename}")
        file.save(filepath)
        
        # Extract data
        from ai.pdf_extractor import extract_advertisement
        extracted_data = extract_advertisement(filepath)
        
        # Clean up preview file
        try:
            os.remove(filepath)
        except:
            pass
        
        # Check if advertisement already exists
        existing = None
        if extracted_data.get('advertisementNo'):
            existing = advertisements_collection.find_one({
                'advertisementNo': extracted_data['advertisementNo']
            })
        
        return jsonify({
            'preview': True,
            'alreadyExists': existing is not None,
            'existingId': str(existing['_id']) if existing else None,
            'extractedData': extracted_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to extract PDF data: {str(e)}'
        }), 500


@pdf_bp.route('/reprocess/<advertisement_id>', methods=['POST'])
def reprocess_advertisement(advertisement_id):
    """
    Reprocess an existing advertisement's PDF to update items.
    """
    try:
        advertisement = advertisements_collection.find_one({
            '_id': ObjectId(advertisement_id)
        })
        
        if not advertisement:
            return jsonify({'error': 'Advertisement not found'}), 404
        
        pdf_file = advertisement.get('pdfFile')
        if not pdf_file:
            return jsonify({'error': 'No PDF file associated with this advertisement'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, pdf_file)
        if not os.path.exists(filepath):
            return jsonify({'error': 'PDF file not found on server'}), 404
        
        # Re-extract data
        from ai.pdf_extractor import extract_advertisement
        extracted_data = extract_advertisement(filepath)
        
        # Update advertisement
        advertisements_collection.update_one(
            {'_id': ObjectId(advertisement_id)},
            {
                '$set': {
                    'extractedData': extracted_data,
                    'totalVacancies': extracted_data['totalVacancies'],
                    'updatedAt': datetime.now()
                }
            }
        )
        
        # Delete old items and recreate
        items_collection.delete_many({'advertisementId': ObjectId(advertisement_id)})
        
        items_created = []
        for item_data in extracted_data.get('items', []):
            item = {
                'itemNo': item_data['itemNo'],
                'advertisementId': ObjectId(advertisement_id),
                'discipline': item_data.get('discipline', ''),
                'title': f"Scientist 'B' - {item_data.get('discipline', 'Unknown')}",
                'description': item_data.get('essentialQualification', ''),
                'essentialQualification': item_data.get('essentialQualification', ''),
                'organization': item_data.get('organization', 'DRDO'),
                'vacancies': item_data.get('vacancies', {}),
                'subOrganizations': item_data.get('subOrganizations', []),
                'gateCode': item_data.get('gateCode'),
                'equivalentDegrees': item_data.get('equivalentDegrees', []),
                'requiredBoardSize': 5,
                'createdAt': datetime.now()
            }
            
            item_result = items_collection.insert_one(item)
            items_created.append(item)
        
        return jsonify({
            'message': 'Advertisement reprocessed successfully!',
            'itemsUpdated': len(items_created)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
