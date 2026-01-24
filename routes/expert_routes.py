"""Expert routes Blueprint."""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

expert_bp = Blueprint('experts', __name__, url_prefix='/api/experts')

# Will be injected from main app
experts_collection = None
serialize_doc = None

def init_expert_routes(experts_col, serializer):
    """Initialize the blueprint with database collection."""
    global experts_collection, serialize_doc
    experts_collection = experts_col
    serialize_doc = serializer


@expert_bp.route('', methods=['GET'])
def get_experts():
    category = request.args.get('category')
    
    query = {}
    if category:
        query['category'] = category
    
    experts = list(experts_collection.find(query).sort('relevanceScore', -1))
    return jsonify(serialize_doc(experts))


@expert_bp.route('/<expert_id>', methods=['GET'])
def get_expert(expert_id):
    try:
        expert = experts_collection.find_one({'_id': ObjectId(expert_id)})
    except:
        return jsonify({'error': 'Invalid expert ID'}), 400
    
    if not expert:
        return jsonify({'error': 'Expert not found'}), 404
    return jsonify(serialize_doc(expert))


@expert_bp.route('', methods=['POST'])
def create_expert():
    data = request.json
    
    expert = {
        'name': data['name'],
        'role': data['role'],
        'category': data['category'],
        'affiliation': data.get('affiliation', ''),
        'relevanceScore': data.get('relevanceScore', 0),
        'reason': data.get('reason', ''),
        'email': data.get('email', ''),
        'createdAt': datetime.now()
    }
    
    result = experts_collection.insert_one(expert)
    expert['_id'] = str(result.inserted_id)
    
    return jsonify(expert), 201


@expert_bp.route('/<expert_id>', methods=['PUT'])
def update_expert(expert_id):
    data = request.json
    try:
        update_data = {}
        for field in ['name', 'role', 'category', 'affiliation', 'relevanceScore', 'reason', 'email']:
            if field in data:
                update_data[field] = data[field]
        
        result = experts_collection.update_one(
            {'_id': ObjectId(expert_id)},
            {'$set': update_data}
        )
        if result.matched_count == 0:
            return jsonify({'error': 'Expert not found'}), 404
        return jsonify({'message': 'Expert updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@expert_bp.route('/<expert_id>', methods=['DELETE'])
def delete_expert(expert_id):
    try:
        result = experts_collection.delete_one({'_id': ObjectId(expert_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Expert not found'}), 404
        return jsonify({'message': 'Expert deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
