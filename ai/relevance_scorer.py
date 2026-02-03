"""
MIRA DRDO - Relevance Score Calculator

This module calculates the final relevance score for each expert using:
- w1: Item-Expert Cosine Similarity
- w2: Item-Expert LLM Similarity  
- w3: Expert-Candidates Avg Cosine Similarity
- w4: Expert-Candidates Avg LLM Similarity

Final Score = weighted_avg(w1, w2, w3, w4)

The weights can be customized based on requirements.
"""

from typing import List, Dict, Any, Optional
from .embedding_generator import (
    generate_item_embedding,
    generate_expert_embedding,
    generate_candidate_embedding,
    generate_item_text,
    generate_expert_text,
    generate_candidate_text
)
from .similarity_calculator import (
    calculate_expert_item_similarity,
    calculate_expert_candidates_similarity,
    llm_generate_reason
)


# Default weights for each component
DEFAULT_WEIGHTS = {
    'w1_item_expert_cosine': 0.35,      # Item-Expert Cosine
    'w2_item_expert_llm': 0.35,         # Item-Expert LLM
    'w3_expert_candidates_cosine': 0.15, # Expert-Candidates Cosine
    'w4_expert_candidates_llm': 0.15     # Expert-Candidates LLM
}


def calculate_relevance_score(
    item: Dict[str, Any],
    expert: Dict[str, Any],
    candidates: List[Dict[str, Any]] = None,
    weights: Dict[str, float] = None,
    use_llm: bool = True,
    use_cached_embeddings: bool = True
) -> Dict[str, Any]:
    """
    Calculate the comprehensive relevance score for an expert-item pair.
    
    Args:
        item: Item document from MongoDB
        expert: Expert document from MongoDB
        candidates: List of candidate documents for this item
        weights: Custom weights for each component (default: DEFAULT_WEIGHTS)
        use_llm: Whether to use LLM for semantic similarity
        use_cached_embeddings: Whether to use pre-computed embeddings from DB
        
    Returns:
        Dictionary containing:
        - final_score: Weighted average score (0-100)
        - component_scores: Individual w1, w2, w3, w4 scores
        - reason: AI-generated explanation
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Generate or retrieve embeddings
    if use_cached_embeddings and expert.get('skillEmbedding'):
        expert_embedding = expert['skillEmbedding']
    else:
        expert_embedding = generate_expert_embedding(expert)
    
    if use_cached_embeddings and item.get('embedding'):
        item_embedding = item['embedding']
    else:
        item_embedding = generate_item_embedding(item)
    
    # Generate text representations
    item_text = generate_item_text(item)
    expert_text = generate_expert_text(expert)
    
    # Calculate Item-Expert similarity (w1, w2)
    item_expert_sim = calculate_expert_item_similarity(
        item_embedding,
        expert_embedding,
        item_text,
        expert_text,
        use_llm=use_llm
    )
    
    w1 = item_expert_sim['cosine_score'] * 100  # Scale to 0-100
    w2 = item_expert_sim['llm_score']
    
    # Calculate Expert-Candidates similarity (w3, w4)
    w3 = 0.0
    w4 = 0.0
    
    if candidates and len(candidates) > 0:
        # Get candidate embeddings
        candidate_embeddings = []
        candidate_texts = []
        
        for cand in candidates:
            if use_cached_embeddings and cand.get('skillEmbedding'):
                candidate_embeddings.append(cand['skillEmbedding'])
            else:
                emb = generate_candidate_embedding(cand)
                if emb:
                    candidate_embeddings.append(emb)
            candidate_texts.append(generate_candidate_text(cand))
        
        if candidate_embeddings:
            expert_cand_sim = calculate_expert_candidates_similarity(
                expert_embedding,
                candidate_embeddings,
                expert_text,
                candidate_texts,
                use_llm=False  # Disable LLM for performance with many candidates
            )
            
            w3 = expert_cand_sim['avg_cosine_score'] * 100
            w4 = expert_cand_sim['avg_llm_score']
    else:
        # No candidates: use item-expert scores as proxy
        w3 = w1
        w4 = w2
    
    # Calculate weighted final score
    final_score = (
        weights['w1_item_expert_cosine'] * w1 +
        weights['w2_item_expert_llm'] * w2 +
        weights['w3_expert_candidates_cosine'] * w3 +
        weights['w4_expert_candidates_llm'] * w4
    )
    
    # Generate AI reason - pure LLM evaluation without appending score breakdown
    # (Score breakdown is already displayed separately in the UI)
    if use_llm and item_text and expert_text:
        reason = llm_generate_reason(
            item_text, 
            expert_text,
            expert_name=expert.get('name'),
            component_scores={
                'w1_item_expert_cosine': w1,
                'w2_item_expert_llm': w2,
                'w3_expert_candidates_cosine': w3,
                'w4_expert_candidates_llm': w4
            },
            final_score=final_score
        )
    else:
        reason = expert.get('reason', 'Expert has relevant skills and domain expertise.')
    
    # Return pure LLM reason without appending score breakdown
    # The UI already displays component scores separately
    return {
        'final_score': round(final_score, 2),
        'component_scores': {
            'w1_item_expert_cosine': round(w1, 2),
            'w2_item_expert_llm': round(w2, 2),
            'w3_expert_candidates_cosine': round(w3, 2),
            'w4_expert_candidates_llm': round(w4, 2)
        },
        'reason': reason,  # Pure LLM explanation
        'weights_used': weights
    }


def batch_calculate_relevance_scores(
    item: Dict[str, Any],
    experts: List[Dict[str, Any]],
    candidates: List[Dict[str, Any]] = None,
    weights: Dict[str, float] = None,
    use_llm: bool = False  # Disable LLM by default for batch (performance)
) -> List[Dict[str, Any]]:
    """
    Calculate relevance scores for multiple experts at once.
    
    Args:
        item: Item document
        experts: List of expert documents
        candidates: List of candidate documents for this item
        weights: Custom weights
        use_llm: Whether to use LLM (disabled by default for performance)
        
    Returns:
        List of score results, each containing expert_id and scores
    """
    results = []
    
    for expert in experts:
        try:
            score_data = calculate_relevance_score(
                item,
                expert,
                candidates,
                weights,
                use_llm=use_llm
            )
            
            results.append({
                'expert_id': str(expert.get('_id', '')),
                'expert_name': expert.get('name', ''),
                'category': expert.get('category', ''),
                **score_data
            })
        except Exception as e:
            print(f"Error calculating score for expert {expert.get('name')}: {e}")
            results.append({
                'expert_id': str(expert.get('_id', '')),
                'expert_name': expert.get('name', ''),
                'category': expert.get('category', ''),
                'final_score': 0,
                'error': str(e)
            })
    
    # Sort by final score descending
    results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
    
    return results


def rank_experts(scored_experts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank experts by their final score and add rank position.
    
    Args:
        scored_experts: List of experts with calculated scores
        
    Returns:
        Ranked list with rank positions added
    """
    sorted_experts = sorted(
        scored_experts, 
        key=lambda x: x.get('final_score', 0), 
        reverse=True
    )
    
    for i, expert in enumerate(sorted_experts):
        expert['rank'] = i + 1
    
    return sorted_experts


# Export functions
__all__ = [
    'calculate_relevance_score',
    'batch_calculate_relevance_scores',
    'rank_experts',
    'DEFAULT_WEIGHTS'
]
