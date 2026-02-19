"""Item routes Blueprint."""
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

item_bp = Blueprint('items', __name__, url_prefix='/api/items')

# Import email utility
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.email_sender import send_invitation_email

# Will be injected from main app
# Will be injected from main app
items_collection = None
advertisements_collection = None
panels_collection = None
experts_collection = None
serialize_doc = None

def init_item_routes(items_col, serializer, adv_col=None, panels_col=None, experts_col=None):
    """Initialize the blueprint with database collection."""
    global items_collection, serialize_doc, advertisements_collection, panels_collection, experts_collection
    items_collection = items_col
    serialize_doc = serializer
    advertisements_collection = adv_col
    panels_collection = panels_col
    experts_collection = experts_col


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
        # Get the expert IDs or detailed objects from the request
        expert_ids = data.get('expertIds', [])
        detailed_experts = data.get('detailedExperts', []) # New field for full data
        panel_type = data.get('panelType', 'Final Interview Panel')
        
        # Create panel record
        if panels_collection is not None and (expert_ids or detailed_experts):
            # Create panelists structure matching panel_routes schema
            panelists = []
            
            if detailed_experts and len(detailed_experts) > 0:
                # Use detailed info if available
                for expert in detailed_experts:
                    panelists.append({
                        'expertId': ObjectId(expert.get('expertId') or expert.get('_id')),
                        'status': 'invited',
                        'panel_role': expert.get('panelRole', 'Member'),
                        'relevanceScore': expert.get('relevanceScore'),
                        'reason': expert.get('reason'),
                        'invitedAt': datetime.now(),
                        'respondedAt': None
                    })
                    # Ensure expert_ids list is populated for email sending later
                    eid = str(expert.get('expertId') or expert.get('_id'))
                    if eid not in expert_ids:
                        expert_ids.append(eid)
                        
            else:
                 # Fallback to just IDs (legacy support)
                for eid in expert_ids:
                    panelists.append({
                        'expertId': ObjectId(eid),
                        'status': 'invited',
                        'panel_role': 'Member',
                        'invitedAt': datetime.now(),
                        'respondedAt': None
                    })

            panel = {
                'itemId': ObjectId(item_id),
                'boardType': panel_type,
                'panelists': panelists,
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
        

        
        # Send emails to accepted experts (Fire and forget)
        try:
            if experts_collection is not None:
                # Fetch item details for email subject
                item = items_collection.find_one({'_id': ObjectId(item_id)})
                item_title = item.get('title', 'Interview Board') if item else 'Interview Board'
                
                print(f"📧 triggering emails for {len(expert_ids)} experts...")
                
                for eid in expert_ids:
                    expert = experts_collection.find_one({'_id': ObjectId(eid)})
                    if expert and expert.get('email'):
                        # Send email
                        print(f"📧 Sending to {expert['name']} <{expert['email']}>")
                        send_invitation_email(
                            expert['email'], 
                            expert['name'], 
                            item_title, 
                            panel_type
                        )
        except Exception as e:
            print(f"❌ Error in email dispatch: {e}")
            # Don't fail the request just because email failed
            
        return jsonify({
            'message': 'Board completed successfully. Emails sent.',
            'itemId': item_id,
            'panelSize': len(expert_ids)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@item_bp.route('/<item_id>/panel', methods=['GET', 'DELETE'])
def handle_item_panel(item_id):
    """Get or Delete the panel for an item."""
    if request.method == 'GET':
        try:
            if panels_collection is None:
                return jsonify({'error': 'Panels not available'}), 500
            
            # Find any panel for this item
            panel = panels_collection.find_one({
                'itemId': ObjectId(item_id)
            }, sort=[('createdAt', -1)])
            
            if not panel:
                # 404 is fine for GET if no panel exists
                return jsonify({'error': 'No accepted panel found for this item'}), 404
            
            return jsonify(serialize_doc(panel))
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    elif request.method == 'DELETE':
        try:
            if panels_collection is None:
                return jsonify({'error': 'Database error'}), 500
                
            # Delete the panel
            result = panels_collection.delete_many({'itemId': ObjectId(item_id)})
            
            # Reset item status
            if items_collection is not None:
                items_collection.update_one(
                    {'_id': ObjectId(item_id)},
                    {'$set': {
                        'boardStatus': 'pending',
                        'boardCompletedAt': None,
                        'acceptedPanelSize': None
                    }}
                )
                
            return jsonify({'message': f'Panel reset successfully. Deleted {result.deleted_count} panels.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400


@item_bp.route('/<item_id>/panel/expert/<expert_id>', methods=['DELETE'])
def remove_expert_from_panel(item_id, expert_id):
    """Remove a specific expert from the panel (emergency edit)."""
    try:
        if panels_collection is None:
            return jsonify({'error': 'Database error'}), 500
            
        print(f"=== REMOVE EXPERT REQUEST ===")
        print(f"Item ID: {item_id}")
        print(f"Expert ID to remove: {expert_id}")
        
        # Fetch the current panel
        current_panel = panels_collection.find_one({'itemId': ObjectId(item_id)})
        
        if not current_panel:
            print(f"ERROR: No panel found for item {item_id}")
            return jsonify({'error': 'Panel does not exist for this item'}), 404
        
        print(f"Found panel with {len(current_panel.get('panelists', []))} panelists")
        
        # Manual filter: Remove the expert from panelists array
        original_panelists = current_panel.get('panelists', [])
        original_count = len(original_panelists)
        
        # Normalize the expert_id from URL (remove any ObjectId wrapper formatting)
        expert_id_to_remove = str(expert_id).strip()
        print(f"Looking for expert ID: '{expert_id_to_remove}'")
        
        # Filter out the matching expert (check multiple possible ID formats)
        filtered_panelists = []
        removed = False
        for p in original_panelists:
            eid = p.get('expertId')
            
            # Extract ID string from various possible formats
            if isinstance(eid, dict) and '$oid' in eid:
                eid_str = eid['$oid']
            elif hasattr(eid, '__str__'):
                eid_str = str(eid)
            else:
                eid_str = str(eid) if eid else ''
            
            print(f"  Comparing: '{expert_id_to_remove}' vs '{eid_str}'")
            
            # Check if this is the expert to remove
            if eid_str == expert_id_to_remove:
                print(f"  -> MATCH! Removing expert: {eid_str}")
                removed = True
            else:
                filtered_panelists.append(p)
        
        if not removed:
            print(f"ERROR: Expert '{expert_id_to_remove}' not found in panelists")
            print(f"  Available IDs: {[str(p.get('expertId')) for p in original_panelists]}")
            return jsonify({'error': 'Expert not found in this panel'}), 404
        
        # Update the panel with filtered list
        panels_collection.update_one(
            {'_id': current_panel['_id']},
            {'$set': {'panelists': filtered_panelists}}
        )
        
        # Also update the item's acceptedPanelSize
        new_size = len(filtered_panelists)
        if items_collection is not None:
            items_collection.update_one(
                {'_id': ObjectId(item_id)},
                {'$set': {'acceptedPanelSize': new_size}}
            )
        
        print(f"SUCCESS: Expert removed. Panel size: {original_count} -> {new_size}")
        return jsonify({'message': 'Expert removed successfully', 'newSize': new_size})
        
    except Exception as e:
        print(f"EXCEPTION in remove_expert_from_panel: {e}")
        import traceback
        traceback.print_exc()
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


@item_bp.route('/<item_id>/invite', methods=['POST'])
def invite_expert(item_id):
    """Send an invitation email to a specific expert."""
    data = request.json
    expert_id = data.get('expertId')
    panel_role = data.get('panelRole', 'Member')
    
    if not expert_id:
        return jsonify({'error': 'Expert ID is required'}), 400
        
    try:
        if experts_collection is None:
            return jsonify({'error': 'Database error'}), 500
            
        expert = experts_collection.find_one({'_id': ObjectId(expert_id)})
        if not expert:
            return jsonify({'error': 'Expert not found'}), 404
            
        # Fetch item details
        item = items_collection.find_one({'_id': ObjectId(item_id)})
        item_title = item.get('title', 'Interview Board') if item else 'Interview Board'
        
        email = expert.get('email')
        if not email:
            return jsonify({'error': 'Expert has no email address'}), 400
            
        print(f"📧 Sending individual invite to {expert['name']} <{email}>")
        # Use result tuple
        success, message = send_invitation_email(
            email, 
            expert['name'], 
            item_title, 
            panel_role
        )
        
        if success:
            # Update panel status if panel exists, or create new panel
            if panels_collection is not None:
                panel = panels_collection.find_one({'itemId': ObjectId(item_id)})
                
                new_panelist = {
                    'expertId': ObjectId(expert_id),
                    'status': 'invited',
                    'panel_role': panel_role,
                    'invitedAt': datetime.now(),
                    'respondedAt': None
                }

                if panel:
                    # Check if expert already in panel
                    existing = next((p for p in panel.get('panelists', []) if str(p['expertId']) == str(expert_id)), None)
                    if existing:
                        panels_collection.update_one(
                            {'itemId': ObjectId(item_id), 'panelists.expertId': ObjectId(expert_id)},
                            {'$set': {'panelists.$.status': 'invited', 'panelists.$.invitedAt': datetime.now()}}
                        )
                    else:
                        panels_collection.update_one(
                            {'itemId': ObjectId(item_id)},
                            {'$push': {'panelists': new_panelist}}
                        )
                else:
                    # Create new panel
                    new_panel_doc = {
                        'itemId': ObjectId(item_id),
                        'boardType': 'Final Interview Panel', # Default
                        'panelists': [new_panelist],
                        'status': 'draft', # Draft until "Complete Board" or keeps as draft?
                        'createdAt': datetime.now(),
                        'expertIds': [] # Legacy field to prevent issues if referenced elsewhere, or omit
                    }
                    panels_collection.insert_one(new_panel_doc)
            
            return jsonify({'message': f'Invitation sent to {email}'})
        else:
            return jsonify({'error': f'Failed to send email: {message}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
