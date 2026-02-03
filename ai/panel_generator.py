"""
MIRA DRDO - Panel Generator Module

This module generates optimal interview panels by:
1. Ranking all experts by their relevance scores
2. Selecting the best experts per category (Chairperson, Departmental, External)
3. Ensuring panel composition requirements are met

Returns both "AI Default Panel" and "All Scored Experts" for manual selection.
"""

from typing import List, Dict, Any, Optional, Tuple
from .relevance_scorer import batch_calculate_relevance_scores, rank_experts


# Default panel composition
DEFAULT_PANEL_COMPOSITION = {
    'chairperson': 1,
    'departmental': 2,
    'external': 2
}

# Panel size configurations
PANEL_SIZES = {
    3: {'chairperson': 1, 'departmental': 1, 'external': 1},
    5: {'chairperson': 1, 'departmental': 2, 'external': 2},
    7: {'chairperson': 1, 'departmental': 3, 'external': 3}
}


def generate_optimal_panel(
    item: Dict[str, Any],
    experts: List[Dict[str, Any]],
    candidates: List[Dict[str, Any]] = None,
    panel_size: int = 5,
    weights: Dict[str, float] = None,
    use_llm: bool = False
) -> Dict[str, Any]:
    """
    Generate the optimal interview panel for an item.
    
    Args:
        item: Item document from MongoDB
        experts: All available expert documents
        candidates: Candidate documents for this item
        panel_size: Target panel size (3, 5, or 7)
        weights: Custom scoring weights
        use_llm: Whether to use LLM for scoring (slower but more accurate)
        
    Returns:
        Dictionary containing:
        - recommended_panel: List of selected experts for the panel
        - all_scored_experts: All experts with their scores
        - panel_composition: Breakdown by category
        - item_id: Reference to the item
    """
    # Get panel composition for the size
    composition = PANEL_SIZES.get(panel_size, DEFAULT_PANEL_COMPOSITION)
    
    # Calculate scores for all experts
    scored_experts = batch_calculate_relevance_scores(
        item,
        experts,
        candidates,
        weights,
        use_llm=use_llm
    )
    
    # Rank all experts
    ranked_experts = rank_experts(scored_experts)
    
    # Select best experts per category
    recommended_panel = []
    selected_ids = set()
    
    # Group by category
    experts_by_category = {
        'chairperson': [],
        'departmental': [],
        'external': []
    }
    
    for expert in ranked_experts:
        category = expert.get('category', 'departmental').lower()
        if category in experts_by_category:
            experts_by_category[category].append(expert)
    
    # Select top experts from each category
    for category, count in composition.items():
        available = experts_by_category.get(category, [])
        for expert in available[:count]:
            if expert['expert_id'] not in selected_ids:
                recommended_panel.append({
                    **expert,
                    'panel_role': 'chairperson' if category == 'chairperson' else 'member',
                    'selection_type': 'ai_recommended'
                })
                selected_ids.add(expert['expert_id'])
    
    # If we couldn't fill all slots, add from remaining experts
    total_needed = sum(composition.values())
    while len(recommended_panel) < total_needed:
        for expert in ranked_experts:
            if expert['expert_id'] not in selected_ids:
                recommended_panel.append({
                    **expert,
                    'panel_role': 'member',
                    'selection_type': 'ai_recommended_fill'
                })
                selected_ids.add(expert['expert_id'])
                break
        else:
            break  # No more experts available
    
    # Sort recommended panel by category order
    category_order = {'chairperson': 0, 'departmental': 1, 'external': 2}
    recommended_panel.sort(
        key=lambda x: (category_order.get(x.get('category', ''), 99), -x.get('final_score', 0))
    )
    
    return {
        'item_id': str(item.get('_id', '')),
        'recommended_panel': recommended_panel,
        'all_scored_experts': ranked_experts,
        'panel_composition': {
            'target': composition,
            'actual': {
                cat: len([e for e in recommended_panel if e.get('category') == cat])
                for cat in composition.keys()
            }
        },
        'panel_size': len(recommended_panel),
        'average_score': round(
            sum(e.get('final_score', 0) for e in recommended_panel) / len(recommended_panel)
            if recommended_panel else 0,
            2
        )
    }


def get_expert_score_breakdown(
    item: Dict[str, Any],
    expert: Dict[str, Any],
    candidates: List[Dict[str, Any]] = None,
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    Get detailed score breakdown for a single expert-item pair.
    
    Args:
        item: Item document
        expert: Expert document
        candidates: Candidate documents
        use_llm: Whether to use LLM for detailed analysis
        
    Returns:
        Detailed score breakdown with explanations
    """
    from .relevance_scorer import calculate_relevance_score
    
    score_data = calculate_relevance_score(
        item,
        expert,
        candidates,
        use_llm=use_llm
    )
    
    return {
        'expert_id': str(expert.get('_id', '')),
        'expert_name': expert.get('name', ''),
        'item_id': str(item.get('_id', '')),
        'item_no': item.get('itemNo', ''),
        **score_data,
        'interpretation': _interpret_scores(score_data['component_scores'])
    }


def _interpret_scores(component_scores: Dict[str, float]) -> Dict[str, str]:
    """Generate human-readable interpretation of scores."""
    interpretations = {}
    
    for key, score in component_scores.items():
        if score >= 80:
            level = "Excellent"
        elif score >= 60:
            level = "Good"
        elif score >= 40:
            level = "Moderate"
        elif score >= 20:
            level = "Low"
        else:
            level = "Poor"
        
        if 'item_expert' in key:
            if 'cosine' in key:
                desc = f"{level} technical skill alignment with item requirements"
            else:
                desc = f"{level} semantic relevance to job description"
        else:
            if 'cosine' in key:
                desc = f"{level} ability to evaluate candidate skill sets"
            else:
                desc = f"{level} semantic match with candidate profiles"
        
        interpretations[key] = desc
    
    return interpretations


def validate_panel(panel: List[Dict[str, Any]], requirements: Dict[str, int] = None) -> Dict[str, Any]:
    """
    Validate that a panel meets composition requirements.
    
    Args:
        panel: List of selected experts
        requirements: Required count per category
        
    Returns:
        Validation result with any issues
    """
    if requirements is None:
        requirements = DEFAULT_PANEL_COMPOSITION
    
    # Count by category
    counts = {}
    for expert in panel:
        category = expert.get('category', 'unknown')
        counts[category] = counts.get(category, 0) + 1
    
    # Check requirements
    issues = []
    for category, required in requirements.items():
        actual = counts.get(category, 0)
        if actual < required:
            issues.append(f"Missing {required - actual} {category}(s)")
        elif actual > required:
            issues.append(f"Excess {actual - required} {category}(s)")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'counts': counts,
        'requirements': requirements
    }


def suggest_replacements(
    current_panel: List[Dict[str, Any]],
    expert_to_replace: str,
    all_scored_experts: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Suggest replacement experts for a panel member.
    
    Args:
        current_panel: Current panel composition
        expert_to_replace: ID of expert to replace
        all_scored_experts: All available experts with scores
        
    Returns:
        List of suggested replacements
    """
    # Find the expert to replace
    replacing = None
    for expert in current_panel:
        if expert.get('expert_id') == expert_to_replace:
            replacing = expert
            break
    
    if not replacing:
        return []
    
    # Get same category experts not in panel
    current_ids = {e.get('expert_id') for e in current_panel}
    suggestions = [
        e for e in all_scored_experts
        if e.get('expert_id') not in current_ids
        and e.get('category') == replacing.get('category')
    ]
    
    # Return top 3 suggestions
    return suggestions[:3]


# Export functions
__all__ = [
    'generate_optimal_panel',
    'get_expert_score_breakdown',
    'validate_panel',
    'suggest_replacements',
    'PANEL_SIZES',
    'DEFAULT_PANEL_COMPOSITION'
]
