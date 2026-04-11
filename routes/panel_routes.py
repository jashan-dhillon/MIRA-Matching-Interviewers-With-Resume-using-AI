"""Panel routes Blueprint."""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

panel_bp = Blueprint('panels', __name__, url_prefix='/api/panels')

# Will be injected from main app
panels_collection = None
serialize_doc = None

def init_panel_routes(panels_col, serializer):
    """Initialize the blueprint with database collection."""
    global panels_collection, serialize_doc
    panels_collection = panels_col
    serialize_doc = serializer


@panel_bp.route('', methods=['GET'])
def get_panels():
    item_id = request.args.get('itemId')
    
    query = {}
    if item_id:
        try:
            query['itemId'] = ObjectId(item_id)
        except:
            pass
    
    panels = list(panels_collection.find(query))
    return jsonify(serialize_doc(panels))


@panel_bp.route('/<panel_id>', methods=['GET'])
def get_panel(panel_id):
    try:
        panel = panels_collection.find_one({'_id': ObjectId(panel_id)})
    except:
        return jsonify({'error': 'Invalid panel ID'}), 400
    
    if not panel:
        return jsonify({'error': 'Panel not found'}), 404
    return jsonify(serialize_doc(panel))


@panel_bp.route('', methods=['POST'])
def create_panel():
    data = request.json
    
    panelists = []
    for expert_id in data.get('expertIds', []):
        panelists.append({
            'expertId': ObjectId(expert_id),
            'status': 'pending',
            'invitedAt': datetime.now(),
            'respondedAt': None
        })
    
    panel = {
        'itemId': ObjectId(data['itemId']),
        'boardType': data.get('boardType', 'Final Interview Panel'),
        'panelists': panelists,
        'createdAt': datetime.now(),
        'status': 'draft'
    }
    
    result = panels_collection.insert_one(panel)
    panel['_id'] = str(result.inserted_id)
    
    return jsonify(serialize_doc(panel)), 201


@panel_bp.route('/<panel_id>/invite', methods=['PUT'])
def update_panelist_status(panel_id):
    data = request.json
    expert_id = data.get('expertId')
    status = data.get('status')  # 'accepted' or 'declined'
    reason = data.get('reason', '') # Reason for decline/accept
    
    try:
        result = panels_collection.update_one(
            {
                '_id': ObjectId(panel_id),
                'panelists.expertId': ObjectId(expert_id)
            },
            {
                '$set': {
                    'panelists.$.status': status,
                    'panelists.$.reason': reason,
                    'panelists.$.respondedAt': datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Panel or expert not found'}), 404
        
        return jsonify({'message': 'Status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
