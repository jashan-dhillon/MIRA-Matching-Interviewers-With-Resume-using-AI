"""Item routes Blueprint."""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

item_bp = Blueprint('items', __name__, url_prefix='/api/items')

# Will be injected from main app
items_collection = None
advertisements_collection = None
panels_collection = None
serialize_doc = None

def init_item_routes(items_col, serializer, adv_col=None, panels_col=None):
    """Initialize the blueprint with database collection."""
    global items_collection, serialize_doc, advertisements_collection, panels_collection
    items_collection = items_col
    serialize_doc = serializer
    advertisements_collection = adv_col
    panels_collection = panels_col


@item_bp.route('', methods=['GET'])
def get_all_items():
    """Get all items, optionally filtered by status."""
    status = request.args.get('status')  # 'pending' or 'completed'
    
    query = {}
    if status:
        query['boardStatus'] = status
    
    items = list(items_collection.find(query).sort('itemNo', 1))
    
    # Enrich items with advertisement info
    for item in items:
        if 'advertisementId' in item:
            try:
                adv = advertisements_collection.find_one({'_id': item['advertisementId']})
                if adv:
                    item['advertisementNo'] = adv.get('advertisementNo')
            except:
                pass
    
    return jsonify(serialize_doc(items))


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
        'boardStatus': 'pending',  # pending or completed
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
        if 'boardStatus' in data:
            update_data['boardStatus'] = data['boardStatus']
            update_data['boardCompletedAt'] = datetime.now()
        
        result = items_collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': update_data}
        )
        if result.matched_count == 0:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify({'message': 'Item updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@item_bp.route('/<item_id>/complete-board', methods=['POST'])
def complete_item_board(item_id):
    """Mark an item's board as completed and save the accepted panel."""
    data = request.json
    
    try:
        # Get the expert IDs from the request
        expert_ids = data.get('expertIds', [])
        panel_type = data.get('panelType', 'Final Interview Panel')
        
        # Create panel record
        if panels_collection is not None and expert_ids:
            panel = {
                'itemId': ObjectId(item_id),
                'expertIds': [ObjectId(eid) for eid in expert_ids],
                'panelType': panel_type,
                'status': 'accepted',
                'createdAt': datetime.now(),
                'acceptedAt': datetime.now()
            }
            panels_collection.insert_one(panel)
        
        # Update item status to completed
        result = items_collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': {
                'boardStatus': 'completed',
                'boardCompletedAt': datetime.now(),
                'acceptedPanelSize': len(expert_ids)
            }}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Item not found'}), 404
        
        return jsonify({
            'message': 'Board completed successfully',
            'itemId': item_id,
            'panelSize': len(expert_ids)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@item_bp.route('/<item_id>/panel', methods=['GET'])
def get_item_panel(item_id):
    """Get the accepted panel for an item."""
    try:
        if panels_collection is None:
            return jsonify({'error': 'Panels not available'}), 500
        
        panel = panels_collection.find_one({
            'itemId': ObjectId(item_id),
            'status': 'accepted'
        })
        
        if not panel:
            return jsonify({'error': 'No accepted panel found for this item'}), 404
        
        return jsonify(serialize_doc(panel))
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

