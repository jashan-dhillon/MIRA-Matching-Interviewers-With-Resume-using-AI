"""Advertisement routes Blueprint."""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

adv_bp = Blueprint('advertisements', __name__, url_prefix='/api/advertisements')

# Will be injected from main app
advertisements_collection = None
items_collection = None
serialize_doc = None

def init_adv_routes(adv_col, items_col, serializer):
    """Initialize the blueprint with database collections."""
    global advertisements_collection, items_collection, serialize_doc
    advertisements_collection = adv_col
    items_collection = items_col
    serialize_doc = serializer


@adv_bp.route('', methods=['GET'])
def get_advertisements():
    status = request.args.get('status')
    
    query = {}
    if status:
        query['status'] = status
    
    advertisements = list(advertisements_collection.find(query).sort('advertisementNo', -1))
    return jsonify(serialize_doc(advertisements))


@adv_bp.route('/<advertisement_id>', methods=['GET'])
def get_advertisement(advertisement_id):
    try:
        advertisement = advertisements_collection.find_one({'_id': ObjectId(advertisement_id)})
        if not advertisement:
            return jsonify({'error': 'Advertisement not found'}), 404
        return jsonify(serialize_doc(advertisement))
    except:
        # Try finding by advertisementNo
        advertisement = advertisements_collection.find_one({'advertisementNo': int(advertisement_id)})
        if not advertisement:
            return jsonify({'error': 'Advertisement not found'}), 404
        return jsonify(serialize_doc(advertisement))


@adv_bp.route('', methods=['POST'])
def create_advertisement():
    data = request.json
    
    advertisement = {
        'advertisementNo': data['advertisementNo'],
        'title': data.get('title', f"Advertisement No. {data['advertisementNo']}"),
        'status': data.get('status', 'active'),
        'createdAt': datetime.now(),
        'closingDate': data.get('closingDate')
    }
    
    result = advertisements_collection.insert_one(advertisement)
    advertisement['_id'] = str(result.inserted_id)
    
    return jsonify(advertisement), 201


@adv_bp.route('/<advertisement_id>', methods=['PUT'])
def update_advertisement(advertisement_id):
    data = request.json
    try:
        update_data = {}
        if 'advertisementNo' in data:
            update_data['advertisementNo'] = data['advertisementNo']
        if 'title' in data:
            update_data['title'] = data['title']
        if 'status' in data:
            update_data['status'] = data['status']
        
        result = advertisements_collection.update_one(
            {'_id': ObjectId(advertisement_id)},
            {'$set': update_data}
        )
        if result.matched_count == 0:
            return jsonify({'error': 'Advertisement not found'}), 404
        return jsonify({'message': 'Advertisement updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@adv_bp.route('/<advertisement_id>', methods=['DELETE'])
def delete_advertisement(advertisement_id):
    try:
        result = advertisements_collection.delete_one({'_id': ObjectId(advertisement_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Advertisement not found'}), 404
        # Also delete related items
        items_collection.delete_many({'advertisementId': ObjectId(advertisement_id)})
        return jsonify({'message': 'Advertisement deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@adv_bp.route('/<advertisement_id>/items', methods=['GET'])
def get_items_by_advertisement(advertisement_id):
    try:
        query = {'advertisementId': ObjectId(advertisement_id)}
    except:
        # Try finding by advertisementNo
        adv = advertisements_collection.find_one({'advertisementNo': int(advertisement_id)})
        if adv:
            query = {'advertisementId': adv['_id']}
        else:
            return jsonify([])
    
    items = list(items_collection.find(query).sort('itemNo', 1))
    return jsonify(serialize_doc(items))
