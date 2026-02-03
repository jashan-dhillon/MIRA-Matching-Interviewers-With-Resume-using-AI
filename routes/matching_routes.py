"""
MIRA DRDO - Matching Routes Blueprint

API endpoints for AI-powered expert matching:
- POST /api/matching/calculate/{itemId} - Calculate scores for all experts
- POST /api/matching/generate-panel/{itemId} - Auto-generate optimal panel
- GET /api/matching/score/{itemId}/{expertId} - Get score breakdown
- POST /api/matching/update-embeddings - Update embeddings for all entities
"""

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
import traceback

matching_bp = Blueprint('matching', __name__, url_prefix='/api/matching')

# Will be injected from main app
items_collection = None
experts_collection = None
candidates_collection = None
serialize_doc = None

# AI module imports (lazy loaded)
_ai_modules_loaded = False


def init_matching_routes(items_col, experts_col, candidates_col, serializer):
    """Initialize the blueprint with database collections."""
    global items_collection, experts_collection, candidates_collection, serialize_doc
    items_collection = items_col
    experts_collection = experts_col
    candidates_collection = candidates_col
    serialize_doc = serializer


def _load_ai_modules():
    """Lazy load AI modules to avoid slow startup."""
    global _ai_modules_loaded
    if not _ai_modules_loaded:
        try:
            from ai import (
                generate_optimal_panel,
                get_expert_score_breakdown,
                batch_calculate_relevance_scores,
                generate_expert_embedding,
                generate_item_embedding,
                generate_candidate_embedding
            )
            _ai_modules_loaded = True
            return True
        except Exception as e:
            print(f"⚠️ Could not load AI modules: {e}")
            traceback.print_exc()
            return False
    return True


@matching_bp.route('/calculate/<item_id>', methods=['POST'])
def calculate_scores(item_id):
    """
    Calculate relevance scores for all experts for a given item.
    
    Request body (optional):
    {
        "use_llm": false,  // Use LLM for semantic scoring (slower)
        "weights": {       // Custom weights
            "w1_item_expert_cosine": 0.35,
            "w2_item_expert_llm": 0.35,
            "w3_expert_candidates_cosine": 0.15,
            "w4_expert_candidates_llm": 0.15
        }
    }
    """
    try:
        # Load AI modules
        if not _load_ai_modules():
            return jsonify({'error': 'AI modules not available'}), 500
        
        from ai import batch_calculate_relevance_scores
        
        # Get item
        try:
            item = items_collection.find_one({'_id': ObjectId(item_id)})
        except:
            item = items_collection.find_one({'itemNo': int(item_id)})
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get all experts
        experts = list(experts_collection.find())
        if not experts:
            return jsonify({'error': 'No experts found'}), 404
        
        # Get candidates for this item (if any)
        candidates = []
        if candidates_collection is not None:
            candidates = list(candidates_collection.find({
                'appliedItemId': item.get('_id')
            }))
        
        # Parse request options
        data = request.json or {}
        use_llm = data.get('use_llm', False)
        weights = data.get('weights', None)
        
        # Calculate scores
        scored_experts = batch_calculate_relevance_scores(
            item,
            experts,
            candidates,
            weights=weights,
            use_llm=use_llm
        )
        
        # Update experts in database with new scores
        for scored in scored_experts:
            try:
                experts_collection.update_one(
                    {'_id': ObjectId(scored['expert_id'])},
                    {'$set': {
                        'relevanceScore': round(scored['final_score']),
                        'scoreDetails': scored.get('component_scores', {}),
                        'reason': scored.get('reason', ''),
                        'scoredAt': datetime.now(),
                        'scoredForItem': item_id
                    }}
                )
            except Exception as e:
                print(f"Error updating expert {scored.get('expert_name')}: {e}")
        
        return jsonify({
            'item_id': item_id,
            'experts_scored': len(scored_experts),
            'scored_experts': scored_experts,
            'calculated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@matching_bp.route('/generate-panel/<item_id>', methods=['POST'])
def generate_panel(item_id):
    """
    Generate optimal panel for an item.
    
    Request body (optional):
    {
        "panel_size": 5,   // 3, 5, or 7
        "use_llm": false,
        "weights": {...}
    }
    """
    try:
        if not _load_ai_modules():
            return jsonify({'error': 'AI modules not available'}), 500
        
        from ai import generate_optimal_panel
        
        # Get item
        try:
            item = items_collection.find_one({'_id': ObjectId(item_id)})
        except:
            item = items_collection.find_one({'itemNo': int(item_id)})
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get all experts
        experts = list(experts_collection.find())
        
        # Get candidates
        candidates = []
        if candidates_collection is not None:
            candidates = list(candidates_collection.find({
                'appliedItemId': item.get('_id')
            }))
        
        # Parse options
        data = request.json or {}
        panel_size = data.get('panel_size', 5)
        use_llm = data.get('use_llm', False)
        weights = data.get('weights', None)
        
        # Generate panel
        panel_result = generate_optimal_panel(
            item,
            experts,
            candidates,
            panel_size=panel_size,
            weights=weights,
            use_llm=use_llm
        )
        
        return jsonify(serialize_doc(panel_result))
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@matching_bp.route('/score/<item_id>/<expert_id>', methods=['GET'])
def get_score(item_id, expert_id):
    """
    Get detailed score breakdown for a specific expert-item pair.
    """
    try:
        if not _load_ai_modules():
            return jsonify({'error': 'AI modules not available'}), 500
        
        from ai import get_expert_score_breakdown
        
        # Get item
        try:
            item = items_collection.find_one({'_id': ObjectId(item_id)})
        except:
            item = items_collection.find_one({'itemNo': int(item_id)})
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get expert
        try:
            expert = experts_collection.find_one({'_id': ObjectId(expert_id)})
        except:
            return jsonify({'error': 'Invalid expert ID'}), 400
        
        if not expert:
            return jsonify({'error': 'Expert not found'}), 404
        
        # Get candidates
        candidates = []
        if candidates_collection is not None:
            candidates = list(candidates_collection.find({
                'appliedItemId': item.get('_id')
            }))
        
        # Use LLM for detailed single-expert scoring
        use_llm = request.args.get('use_llm', 'true').lower() == 'true'
        
        # Get detailed breakdown
        breakdown = get_expert_score_breakdown(
            item,
            expert,
            candidates,
            use_llm=use_llm
        )
        
        return jsonify(serialize_doc(breakdown))
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@matching_bp.route('/update-embeddings', methods=['POST'])
def update_embeddings():
    """
    Update embeddings for all experts, items, and candidates.
    This should be run after adding new data or periodically.
    """
    try:
        if not _load_ai_modules():
            return jsonify({'error': 'AI modules not available'}), 500
        
        from ai import (
            generate_expert_embedding,
            generate_item_embedding,
            generate_candidate_embedding
        )
        
        results = {
            'experts_updated': 0,
            'items_updated': 0,
            'candidates_updated': 0,
            'errors': []
        }
        
        # Update expert embeddings
        experts = list(experts_collection.find())
        for expert in experts:
            try:
                embedding = generate_expert_embedding(expert)
                if embedding:
                    experts_collection.update_one(
                        {'_id': expert['_id']},
                        {'$set': {'skillEmbedding': embedding, 'embeddingUpdatedAt': datetime.now()}}
                    )
                    results['experts_updated'] += 1
            except Exception as e:
                results['errors'].append(f"Expert {expert.get('name')}: {str(e)}")
        
        # Update item embeddings
        items = list(items_collection.find())
        for item in items:
            try:
                embedding = generate_item_embedding(item)
                if embedding:
                    items_collection.update_one(
                        {'_id': item['_id']},
                        {'$set': {'embedding': embedding, 'embeddingUpdatedAt': datetime.now()}}
                    )
                    results['items_updated'] += 1
            except Exception as e:
                results['errors'].append(f"Item {item.get('itemNo')}: {str(e)}")
        
        # Update candidate embeddings
        if candidates_collection is not None:
            candidates = list(candidates_collection.find())
            for candidate in candidates:
                try:
                    embedding = generate_candidate_embedding(candidate)
                    if embedding:
                        candidates_collection.update_one(
                            {'_id': candidate['_id']},
                            {'$set': {'skillEmbedding': embedding, 'embeddingUpdatedAt': datetime.now()}}
                        )
                        results['candidates_updated'] += 1
                except Exception as e:
                    results['errors'].append(f"Candidate {candidate.get('name')}: {str(e)}")
        
        results['updated_at'] = datetime.now().isoformat()
        
        return jsonify(results)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@matching_bp.route('/experts-with-scores/<item_id>', methods=['GET'])
def get_experts_with_scores(item_id):
    """
    Get all experts with their cached scores for an item.
    Returns experts sorted by relevance score.
    """
    try:
        # Get item to validate
        try:
            item = items_collection.find_one({'_id': ObjectId(item_id)})
        except:
            item = items_collection.find_one({'itemNo': int(item_id)})
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Get all experts sorted by relevance score
        experts = list(experts_collection.find().sort('relevanceScore', -1))
        
        # Group by category
        grouped = {
            'chairperson': [],
            'departmental': [],
            'external': []
        }
        
        for expert in experts:
            category = expert.get('category', 'departmental')
            if category in grouped:
                grouped[category].append(serialize_doc(expert))
        
        return jsonify({
            'item_id': item_id,
            'experts_by_category': grouped,
            'total_experts': len(experts)
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@matching_bp.route('/ollama-status', methods=['GET'])
def ollama_status():
    """
    Check if Ollama is available for local LLM inference.
    Returns status, available models, and default model.
    """
    try:
        from ai import get_ollama_status
        status = get_ollama_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e),
            'message': 'Install Ollama from https://ollama.ai and run: ollama pull llama3.2'
        })

