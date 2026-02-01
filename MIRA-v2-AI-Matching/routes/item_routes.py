"""Item routes Blueprint."""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

item_bp = Blueprint('items', __name__, url_prefix='/api/items')

# Will be injected from main app
items_collection = None
serialize_doc = None

def init_item_routes(items_col, serializer):
    """Initialize the blueprint with database collection."""
    global items_collection, serialize_doc
    items_collection = items_col
    serialize_doc = serializer


@item_bp.route('/<item_id>', methods=['GET'])
def get_item(item_id):
    try:
        item = items_collection.find_one({'_id': ObjectId(item_id)})
    except:
        item = items_collection.find_one({'itemNo': int(item_id)})
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(serialize_doc(item))


@item_bp.route('', methods=['POST'])
def create_item():
    data = request.json
    
    item = {
        'itemNo': data['itemNo'],
        'advertisementId': ObjectId(data['advertisementId']),
        'title': data.get('title', f"Item No. {data['itemNo']}"),
        'description': data.get('description', ''),
        'documentUrl': data.get('documentUrl', ''),
        'requiredBoardSize': data.get('requiredBoardSize', 5),
        'createdAt': datetime.now()
    }
    
    result = items_collection.insert_one(item)
    item['_id'] = str(result.inserted_id)
    item['advertisementId'] = str(item['advertisementId'])
    
    return jsonify(item), 201


@item_bp.route('/<item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    try:
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'itemNo' in data:
            update_data['itemNo'] = data['itemNo']
        
        result = items_collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': update_data}
        )
        if result.matched_count == 0:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify({'message': 'Item updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@item_bp.route('/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        result = items_collection.delete_one({'_id': ObjectId(item_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
