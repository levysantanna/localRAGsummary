"""
Configuration settings for the Local RAG system
"""
import os
from pathlib import Path
from typing import List, Dict, Any

# Base paths
BASE_DIR = Path(__file__).parent
DOCUMENTS_DIR = BASE_DIR / "documents"
RAGFILES_DIR = BASE_DIR / "RAGfiles"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

# Create directories if they don't exist
DOCUMENTS_DIR.mkdir(exist_ok=True)
RAGFILES_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'text': ['.txt', '.md', '.rst'],
    'pdf': ['.pdf'],
    'images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'],
    'documents': ['.docx', '.doc', '.pptx', '.ppt'],
    'odf': ['.odt', '.ods', '.odp'],  # Open Document Format (LibreOffice)
    'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.pl', '.sh', '.sql', '.html', '.css', '.xml', '.json', '.yaml', '.yml']
}

# Model configurations
MODEL_CONFIG = {
    'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    'llm_model': 'microsoft/DialoGPT-medium',
    'portuguese_model': 'neuralmind/bert-base-portuguese-cased',
    'ocr_languages': ['pt', 'en'],
    'chunk_size': 1000,
    'chunk_overlap': 200
}

# Processing settings
PROCESSING_CONFIG = {
    'max_file_size_mb': 50,
    'enable_ocr': True,
    'enable_code_analysis': True,
    'enable_image_processing': True,
    'parallel_processing': True,
    'max_workers': 4
}

# Vector database settings
VECTOR_DB_CONFIG = {
    'collection_name': 'university_documents',
    'distance_metric': 'cosine',
    'embedding_dimension': 384
}

# Language settings
LANGUAGE_CONFIG = {
    'default_language': 'pt',
    'supported_languages': ['pt', 'en'],
    'portuguese_stemming': True,
    'portuguese_stopwords': True
}

# GPU/CPU settings
DEVICE_CONFIG = {
    'use_gpu': True,
    'gpu_memory_fraction': 0.8,
    'fallback_to_cpu': True,
    'batch_size': 32
}

# RAG settings
RAG_CONFIG = {
    'top_k_results': 5,
    'similarity_threshold': -50.0,  # Ajustado para similaridades negativas
    'max_context_length': 4000,
    'enable_reranking': True,
    'response_language': 'pt'
}

# Markdown generation settings
MARKDOWN_CONFIG = {
    'include_metadata': True,
    'include_sources': True,
    'include_timestamps': True,
    'auto_generate_summaries': True,
    'summary_length': 500
}
