"""Expert routes Blueprint."""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

expert_bp = Blueprint('experts', __name__, url_prefix='/api/experts')

# Will be injected from main app
experts_collection = None
panels_collection = None
items_collection = None
serialize_doc = None

def init_expert_routes(experts_col, serializer, panels_col=None, items_col=None):
    """Initialize the blueprint with database collection."""
    global experts_collection, serialize_doc, panels_collection, items_collection
    experts_collection = experts_col
    serialize_doc = serializer
    panels_collection = panels_col
    items_collection = items_col


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


        return jsonify({'message': 'Expert deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@expert_bp.route('/<expert_id>/invitations', methods=['GET'])
def get_expert_invitations(expert_id):
    """Get all invitations for a specific expert."""
    print(f"DEBUG INVITATIONS: expert_id={expert_id}")
    print(f"DEBUG COLLECTIONS: panels={panels_collection is not None}, items={items_collection is not None}")
    
    if panels_collection is None or items_collection is None:
        print("ERROR: Collections not initialized in expert_routes")
        return jsonify({'error': 'Database collections not initialized'}), 500
        
    try:
        # Find panels where this expert is a panelist
        panels = list(panels_collection.find({
            'panelists.expertId': ObjectId(expert_id)
        }))
        
        results = {
            'pending': [],
            'upcoming': [],
            'history': []
        }
        
        for panel in panels:
            # Find the panelist entry for this expert
            panelist_entry = next((p for p in panel['panelists'] if str(p['expertId']) == expert_id), None)
            if not panelist_entry:
                continue
                
            # Fetch item details
            item = items_collection.find_one({'_id': panel['itemId']})
            if not item:
                continue
                
            # Construct display object
            invite_obj = {
                'panelId': str(panel['_id']),
                'itemId': str(item['_id']),
                'itemTitle': item.get('title', 'Unknown Position'),
                'advertisementNo': item.get('advertisementNo', 'N/A'),
                'itemNo': item.get('itemNo', 'N/A'),
                'role': panelist_entry.get('panel_role', 'Member'),
                'status': panelist_entry.get('status', 'pending'),
                'invitedAt': panelist_entry.get('invitedAt'),
                # Mock date for now (in real app, this would be in the panel/item)
                'date': 'February 15, 2026', 
                'venue': 'RAC, DRDO Headquarters, New Delhi',
                'reason': panelist_entry.get('reason', '')
            }
            
            status = panelist_entry.get('status', 'pending').lower()
            
            if status == 'invited' or status == 'pending':
                results['pending'].append(invite_obj)
            elif status == 'accepted':
                results['upcoming'].append(invite_obj)
            else:
                results['history'].append(invite_obj)
                
        return jsonify(results)
        
    except Exception as e:
        print(f"Error fetching invitations: {e}")
        return jsonify({'error': str(e)}), 400
