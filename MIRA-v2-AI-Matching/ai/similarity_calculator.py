"""
MIRA DRDO - Similarity Calculator Module

This module calculates similarity scores using:
1. Cosine similarity (fast, mathematical comparison of embeddings)
2. LLM similarity (semantic comparison using LOCAL Ollama models)

The combination provides both speed and accuracy for expert matching.
Works completely OFFLINE with no external API dependencies.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from scipy.spatial.distance import cosine
import re

# Ollama setup - lazy loading
_ollama_client = None
_ollama_available = None
_default_model = 'llama3.2'  # Can be changed to mistral, phi, etc.


def _check_ollama_available():
    """Check if Ollama is running and available."""
    global _ollama_available
    if _ollama_available is not None:
        return _ollama_available
    
    try:
        import ollama
        # Try to list models to verify connection
        ollama.list()
        _ollama_available = True
        print("✅ Ollama is available for local LLM inference")
        return True
    except Exception as e:
        print(f"⚠️ Ollama not available: {e}")
        print("   Install Ollama from https://ollama.ai and run: ollama pull llama3.2")
        _ollama_available = False
        return False


def _get_ollama_response(prompt: str, model: str = None) -> Optional[str]:
    """Get response from Ollama."""
    if not _check_ollama_available():
        return None
    
    try:
        import ollama
        model = model or os.getenv('OLLAMA_MODEL', _default_model)
        
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                'temperature': 0.1,  # Low temperature for consistent scoring
                'num_predict': 300,  # Increased to allow complete explanations (was 50)
            }
        )
        return response.get('response', '').strip()
    except Exception as e:
        print(f"Ollama error: {e}")
        return None


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embedding vectors.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Similarity score between 0 and 1 (1 = identical)
    """
    if not embedding1 or not embedding2:
        return 0.0
    
    try:
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Handle dimension mismatch
        if len(vec1) != len(vec2):
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
        
        # Calculate cosine similarity (1 - cosine distance)
        similarity = 1 - cosine(vec1, vec2)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, similarity))
    except Exception as e:
        print(f"Error calculating cosine similarity: {e}")
        return 0.0


def batch_cosine_similarity(target_embedding: List[float], 
                            embeddings: List[List[float]]) -> List[float]:
    """
    Calculate cosine similarity between a target and multiple embeddings.
    
    Args:
        target_embedding: The target embedding to compare against
        embeddings: List of embeddings to compare with
        
    Returns:
        List of similarity scores
    """
    return [cosine_similarity(target_embedding, emb) for emb in embeddings]


def llm_similarity(text1: str, text2: str, context: str = "job matching") -> float:
    """
    Calculate semantic similarity using local Ollama LLM.
    
    Args:
        text1: First text (e.g., item requirements)
        text2: Second text (e.g., expert profile)
        context: Context for the comparison
        
    Returns:
        Similarity score between 0 and 100
    """
    if not _check_ollama_available():
        # Fallback: Use enhanced heuristic
        return _fallback_text_similarity(text1, text2)
    
    try:
        prompt = f"""Rate the relevance match between these two profiles for {context} on a scale of 0-100.

**Job Requirements:**
{text1[:500]}

**Expert Profile:**
{text2[:500]}

Consider: technical skill match, domain expertise, qualification relevance.
Respond with ONLY a number between 0 and 100. Nothing else."""

        response = _get_ollama_response(prompt)
        
        if response:
            # Extract number from response
            numbers = re.findall(r'\d+', response)
            if numbers:
                score = int(numbers[0])
                return max(0, min(100, score))
        
        return _fallback_text_similarity(text1, text2)
        
    except Exception as e:
        print(f"Error in LLM similarity: {e}")
        return _fallback_text_similarity(text1, text2)


def _fallback_text_similarity(text1: str, text2: str) -> float:
    """
    Fallback text similarity when LLM is unavailable.
    Uses keyword matching with domain-specific weighting.
    """
    if not text1 or not text2:
        return 50.0
    
    # Tokenize and lowercase
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 
                  'or', 'is', 'are', 'was', 'were', 'with', 'by', 'as', 'this'}
    words1 = words1 - stop_words
    words2 = words2 - stop_words
    
    if not words1 or not words2:
        return 50.0
    
    # Technical keywords get higher weight
    tech_keywords = {
        'engineering', 'electronics', 'communication', 'signal', 'processing',
        'radar', 'embedded', 'vlsi', 'fpga', 'microwave', 'antenna', 'rf',
        'digital', 'analog', 'control', 'systems', 'software', 'hardware',
        'machine', 'learning', 'ai', 'ml', 'deep', 'neural', 'computer',
        'science', 'mechanical', 'aerospace', 'propulsion', 'physics',
        'chemistry', 'materials', 'design', 'research', 'development'
    }
    
    # Calculate weighted overlap
    common_words = words1 & words2
    common_tech = common_words & tech_keywords
    
    # Base Jaccard similarity
    jaccard = len(common_words) / len(words1 | words2)
    
    # Boost for technical keyword matches
    tech_boost = len(common_tech) * 5  # Each tech match adds 5%
    
    # Scale to 0-100
    score = (jaccard * 60) + tech_boost + 20  # Base 20%, max ~100%
    
    return min(100.0, round(score, 2))


def llm_generate_reason(
    item_text: str, 
    expert_text: str,
    expert_name: str = None,
    component_scores: Dict[str, float] = None,
    final_score: float = None
) -> str:
    """
    Generate a human-readable reason for why an expert matches an item.
    Uses local Ollama with score context for specific explanations.
    
    Args:
        item_text: Text representation of the item
        expert_text: Text representation of the expert
        expert_name: Expert's name for personalized explanation
        component_scores: Dictionary with w1, w2, w3, w4 scores
        final_score: Final weighted relevance score (0-100)
        
    Returns:
        Explanation string
    """
    if not _check_ollama_available():
        return _generate_fallback_reason(item_text, expert_text)
    
    try:
        # Build score context for the prompt
        score_context = ""
        if component_scores and final_score is not None:
            w1 = component_scores.get('w1_item_expert_cosine', 0)
            w2 = component_scores.get('w2_item_expert_llm', 0)
            w3 = component_scores.get('w3_expert_candidates_cosine', 0)
            w4 = component_scores.get('w4_expert_candidates_llm', 0)
            
            score_context = f"""
**CALCULATED SCORES (Explain each):**
- JD-Expert Cosine Match: {w1:.1f}% (How well do embeddings match?)
- JD-Expert Semantic Match: {w2:.1f}% (How well does meaning align?)
- Expert-Candidates Cosine: {w3:.1f}% (Can they evaluate candidates?)
- Expert-Candidates Semantic: {w4:.1f}% (Domain fit for evaluation?)
- **Final Weighted Score: {final_score:.1f}%**
"""
        
        expert_ref = expert_name if expert_name else "this expert"
        
        prompt = f"""Analyze why {expert_ref} received a {final_score:.1f}% relevance score for evaluating candidates for this position.

**JOB REQUIREMENTS:**
{item_text[:800]}

**EXPERT PROFILE:**
{expert_text[:800]}
{score_context}

Provide your analysis in this EXACT format:

**✅ STRENGTHS (What Matches):**
List 2-3 specific points where the expert's qualifications match the job requirements:
- Quote exact degrees, certifications, or experience years
- Mention specific technical skills or domain expertise that align
- Reference relevant achievements or research areas

**⚠️ GAPS/WEAKNESSES (What's Missing):**
Identify 1-2 specific gaps or mismatches that prevent a higher score:
- What specific job requirements are not met?
- Any domain mismatch or missing qualifications?
- If score is high (>80%), explain what prevents it from being perfect

**🎯 SCORE BREAKDOWN ({final_score:.1f}%):**
Explain why this exact percentage:
- How do the matching strengths and gaps lead to this score?
- Reference the component scores (JD-Expert Cosine: {w1:.1f}%, Semantic: {w2:.1f}%, etc.)
- Final verdict on suitability

Be specific and detailed. This is your professional evaluation."""

        response = _get_ollama_response(prompt)
        
        if response and len(response) > 30:
            # Don't truncate - return full response to avoid mid-sentence cuts
            return response.strip()  # Full detailed explanation
        
        return _generate_fallback_reason(item_text, expert_text)
        
    except Exception as e:
        print(f"Error generating reason: {e}")
        return _generate_fallback_reason(item_text, expert_text)


def _generate_fallback_reason(item_text: str, expert_text: str) -> str:
    """Generate a reason without LLM using keyword extraction."""
    # Extract key terms
    item_words = set(item_text.lower().split())
    expert_words = set(expert_text.lower().split())
    
    tech_terms = {
        'electronics', 'communication', 'signal', 'processing', 'radar',
        'embedded', 'vlsi', 'rf', 'antenna', 'digital', 'systems',
        'machine learning', 'ai', 'software', 'mechanical', 'aerospace'
    }
    
    matching_terms = (item_words & expert_words) & tech_terms
    
    if matching_terms:
        terms_str = ', '.join(list(matching_terms)[:3])
        return f"Expert has relevant experience in {terms_str} which aligns with the position requirements."
    
    return "Expert has relevant domain expertise and experience for evaluating candidates in this field."


def calculate_expert_item_similarity(
    item_embedding: List[float],
    expert_embedding: List[float],
    item_text: str,
    expert_text: str,
    use_llm: bool = True
) -> Dict[str, float]:
    """
    Calculate comprehensive similarity between an item and expert.
    
    Args:
        item_embedding: Item embedding vector
        expert_embedding: Expert embedding vector
        item_text: Item text representation
        expert_text: Expert text representation
        use_llm: Whether to use LLM for semantic similarity
        
    Returns:
        Dictionary with cosine_score and llm_score
    """
    result = {
        'cosine_score': 0.0,
        'llm_score': 0.0
    }
    
    # Calculate cosine similarity
    if item_embedding and expert_embedding:
        result['cosine_score'] = cosine_similarity(item_embedding, expert_embedding)
    
    # Calculate LLM similarity (only if requested and texts available)
    if use_llm and item_text and expert_text:
        result['llm_score'] = llm_similarity(item_text, expert_text)
    else:
        # Fallback LLM score based on cosine
        result['llm_score'] = result['cosine_score'] * 100
    
    return result


def calculate_expert_candidates_similarity(
    expert_embedding: List[float],
    candidate_embeddings: List[List[float]],
    expert_text: str = None,
    candidate_texts: List[str] = None,
    use_llm: bool = False
) -> Dict[str, float]:
    """
    Calculate average similarity between an expert and all candidates for an item.
    
    This represents how well the expert can evaluate the candidate pool.
    
    Args:
        expert_embedding: Expert embedding vector
        candidate_embeddings: List of candidate embedding vectors
        expert_text: Expert text representation
        candidate_texts: List of candidate text representations
        use_llm: Whether to use LLM (disabled by default for performance)
        
    Returns:
        Dictionary with avg_cosine_score and avg_llm_score
    """
    result = {
        'avg_cosine_score': 0.0,
        'avg_llm_score': 0.0
    }
    
    if not candidate_embeddings:
        return result
    
    # Calculate cosine similarities
    cosine_scores = batch_cosine_similarity(expert_embedding, candidate_embeddings)
    result['avg_cosine_score'] = np.mean(cosine_scores) if cosine_scores else 0.0
    
    # Calculate LLM similarities if requested
    if use_llm and expert_text and candidate_texts:
        llm_scores = []
        for cand_text in candidate_texts[:3]:  # Limit to first 3 for performance
            score = llm_similarity(expert_text, cand_text, "candidate evaluation")
            llm_scores.append(score)
        result['avg_llm_score'] = np.mean(llm_scores) if llm_scores else 0.0
    else:
        # Use cosine-based estimate for performance
        result['avg_llm_score'] = result['avg_cosine_score'] * 100
    
    return result


def get_ollama_status() -> Dict[str, Any]:
    """Get the status of Ollama connection."""
    available = _check_ollama_available()
    
    result = {
        'available': available,
        'model': os.getenv('OLLAMA_MODEL', _default_model)
    }
    
    if available:
        try:
            import ollama
            models = ollama.list()
            result['installed_models'] = [m['name'] for m in models.get('models', [])]
        except:
            result['installed_models'] = []
    
    return result


# Export functions
__all__ = [
    'cosine_similarity',
    'batch_cosine_similarity',
    'llm_similarity',
    'llm_generate_reason',
    'calculate_expert_item_similarity',
    'calculate_expert_candidates_similarity',
    'get_ollama_status'
]
