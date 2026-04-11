"""
MIRA DRDO - AI Modules Package

This package contains AI/ML modules for:
- PDF Advertisement Extraction (pdf_extractor.py)
- Embedding Generation (embedding_generator.py)
- Similarity Calculation (similarity_calculator.py)
- Relevance Scoring (relevance_scorer.py)
- Panel Generation (panel_generator.py)

These modules work together to:
1. Generate semantic embeddings for items, experts, and candidates
2. Calculate similarity scores using cosine and LLM methods
3. Compute weighted relevance scores
4. Generate optimal interview panels
"""

from .pdf_extractor import extract_advertisement, AdvertisementExtractor

# Import embedding functions
from .embedding_generator import (
    generate_embedding,
    generate_item_embedding,
    generate_expert_embedding,
    generate_candidate_embedding,
    generate_item_text,
    generate_expert_text,
    generate_candidate_text,
    batch_generate_embeddings
)

# Import similarity functions
from .similarity_calculator import (
    cosine_similarity,
    batch_cosine_similarity,
    llm_similarity,
    llm_generate_reason,
    calculate_expert_item_similarity,
    calculate_expert_candidates_similarity,
    get_ollama_status
)

# Import relevance scoring functions
from .relevance_scorer import (
    calculate_relevance_score,
    batch_calculate_relevance_scores,
    rank_experts,
    DEFAULT_WEIGHTS
)

# Import panel generation functions
from .panel_generator import (
    generate_optimal_panel,
    get_expert_score_breakdown,
    validate_panel,
    suggest_replacements,
    PANEL_SIZES,
    DEFAULT_PANEL_COMPOSITION
)

__all__ = [
    # PDF Extraction
    'extract_advertisement',
    'AdvertisementExtractor',
    
    # Embedding Generation
    'generate_embedding',
    'generate_item_embedding',
    'generate_expert_embedding',
    'generate_candidate_embedding',
    'generate_item_text',
    'generate_expert_text',
    'generate_candidate_text',
    'batch_generate_embeddings',
    
    # Similarity Calculation
    'cosine_similarity',
    'batch_cosine_similarity',
    'llm_similarity',
    'llm_generate_reason',
    'calculate_expert_item_similarity',
    'calculate_expert_candidates_similarity',
    'get_ollama_status',
    
    # Relevance Scoring
    'calculate_relevance_score',
    'batch_calculate_relevance_scores',
    'rank_experts',
    'DEFAULT_WEIGHTS',
    
    # Panel Generation
    'generate_optimal_panel',
    'get_expert_score_breakdown',
    'validate_panel',
    'suggest_replacements',
    'PANEL_SIZES',
    'DEFAULT_PANEL_COMPOSITION'
]


