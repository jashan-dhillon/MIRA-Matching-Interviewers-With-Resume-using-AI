"""
MIRA DRDO - AI Modules Package

This package contains AI/ML modules for:
- PDF Advertisement Extraction (pdf_extractor.py)
- Expert recommendation engine (planned)
- Skill matching algorithms (planned)
- Panel optimization (planned)

Add your AI modules here as separate Python files.
"""

from .pdf_extractor import extract_advertisement, AdvertisementExtractor

__all__ = ['extract_advertisement', 'AdvertisementExtractor']

