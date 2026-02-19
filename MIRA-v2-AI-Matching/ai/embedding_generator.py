"""
MIRA DRDO - Embedding Generator Module

This module generates embeddings for:
- Item requirements (discipline, qualifications, GATE code)
- Expert profiles (skills, role, specializations)
- Candidate profiles (skills, qualifications)

Uses sentence-transformers for creating semantic embeddings.
"""

import os
from typing import List, Dict, Any, Optional, Union
import numpy as np

# Lazy loading to avoid slow startup
_model = None
_model_name = 'all-MiniLM-L6-v2'  # 384-dimensional embeddings, fast and accurate


def _get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(_model_name)
            print(f"✅ Loaded embedding model: {_model_name}")
        except Exception as e:
            print(f"⚠️ Could not load embedding model: {e}")
            _model = None
    return _model


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding vector for a given text.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the embedding vector (384 dimensions)
        Returns None if embedding fails
    """
    if not text or not text.strip():
        return None
    
    model = _get_model()
    if model is None:
        # Fallback: return a random embedding for testing when model unavailable
        return list(np.random.randn(384).astype(float))
    
    try:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def generate_item_text(item: Dict[str, Any]) -> str:
    """
    Generate text representation of an item for embedding.
    
    Args:
        item: Item document from MongoDB
        
    Returns:
        Concatenated text representing the item
    """
    parts = []
    
    # Add discipline/title
    if item.get('discipline'):
        parts.append(f"Discipline: {item['discipline']}")
    if item.get('title'):
        parts.append(f"Title: {item['title']}")
    
    # Add essential qualification
    if item.get('essentialQualification'):
        parts.append(f"Qualification: {item['essentialQualification']}")
    if item.get('description'):
        parts.append(f"Description: {item['description']}")
    
    # Add GATE code
    if item.get('gateCode'):
        parts.append(f"GATE Paper: {item['gateCode']}")
    
    # Add equivalent degrees
    if item.get('equivalentDegrees'):
        degrees = ', '.join(item['equivalentDegrees'])
        parts.append(f"Equivalent Degrees: {degrees}")
    
    # Add organization
    if item.get('organization'):
        parts.append(f"Organization: {item['organization']}")
    
    return ' '.join(parts)


def generate_expert_text(expert: Dict[str, Any]) -> str:
    """
    Generate text representation of an expert for embedding.
    
    Args:
        expert: Expert document from MongoDB
        
    Returns:
        Concatenated text representing the expert
    """
    parts = []
    
    # Add name and role
    if expert.get('name'):
        parts.append(f"Name: {expert['name']}")
    if expert.get('role'):
        parts.append(f"Role: {expert['role']}")
    
    # Add skills if available
    if expert.get('skills'):
        if isinstance(expert['skills'], list):
            skills = ', '.join(expert['skills'])
        else:
            skills = expert['skills']
        parts.append(f"Skills: {skills}")
    
    # Add qualifications
    if expert.get('qualifications'):
        if isinstance(expert['qualifications'], list):
            quals = ', '.join(expert['qualifications'])
        else:
            quals = expert['qualifications']
        parts.append(f"Qualifications: {quals}")
    
    # Add specializations
    if expert.get('specializations'):
        if isinstance(expert['specializations'], list):
            specs = ', '.join(expert['specializations'])
        else:
            specs = expert['specializations']
        parts.append(f"Specializations: {specs}")
    
    # Add affiliation
    if expert.get('affiliation'):
        parts.append(f"Affiliation: {expert['affiliation']}")
    
    # Add category
    if expert.get('category'):
        parts.append(f"Category: {expert['category']}")
    
    # Add reason/description
    if expert.get('reason'):
        parts.append(f"Expertise: {expert['reason']}")
    
    return ' '.join(parts)


def generate_candidate_text(candidate: Dict[str, Any]) -> str:
    """
    Generate text representation of a candidate for embedding.
    
    Args:
        candidate: Candidate document from MongoDB
        
    Returns:
        Concatenated text representing the candidate
    """
    parts = []
    
    # Add name
    if candidate.get('name'):
        parts.append(f"Name: {candidate['name']}")
    
    # Add skills
    if candidate.get('skills'):
        if isinstance(candidate['skills'], list):
            skills = ', '.join(candidate['skills'])
        else:
            skills = candidate['skills']
        parts.append(f"Skills: {skills}")
    
    # Add qualifications
    if candidate.get('qualifications'):
        if isinstance(candidate['qualifications'], list):
            quals = ', '.join(candidate['qualifications'])
        else:
            quals = candidate['qualifications']
        parts.append(f"Qualifications: {quals}")
    
    # Add GATE score and paper
    if candidate.get('gateScore'):
        parts.append(f"GATE Score: {candidate['gateScore']}")
    if candidate.get('gatePaper'):
        parts.append(f"GATE Paper: {candidate['gatePaper']}")
    
    # Add experience
    if candidate.get('experience'):
        parts.append(f"Experience: {candidate['experience']}")
    
    # Add education
    if candidate.get('education'):
        parts.append(f"Education: {candidate['education']}")
    
    return ' '.join(parts)


def generate_item_embedding(item: Dict[str, Any]) -> Optional[List[float]]:
    """Generate embedding for an item."""
    text = generate_item_text(item)
    return generate_embedding(text)


def generate_expert_embedding(expert: Dict[str, Any]) -> Optional[List[float]]:
    """Generate embedding for an expert."""
    text = generate_expert_text(expert)
    return generate_embedding(text)


def generate_candidate_embedding(candidate: Dict[str, Any]) -> Optional[List[float]]:
    """Generate embedding for a candidate."""
    text = generate_candidate_text(candidate)
    return generate_embedding(text)


def batch_generate_embeddings(texts: List[str]) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts at once (more efficient).
    
    Args:
        texts: List of input texts
        
    Returns:
        List of embedding vectors
    """
    model = _get_model()
    if model is None:
        return [list(np.random.randn(384).astype(float)) for _ in texts]
    
    try:
        embeddings = model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        print(f"Error in batch embedding: {e}")
        return [None] * len(texts)


# Export functions
__all__ = [
    'generate_embedding',
    'generate_item_embedding',
    'generate_expert_embedding',
    'generate_candidate_embedding',
    'generate_item_text',
    'generate_expert_text',
    'generate_candidate_text',
    'batch_generate_embeddings'
]
