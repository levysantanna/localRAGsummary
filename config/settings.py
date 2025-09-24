"""
Configuration settings for LocalRAG system
"""
import os
from pathlib import Path
from typing import List, Optional

class Settings:
    """Configuration settings for the RAG system"""
    
    # Model configurations
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.pdf', '.txt', '.md', '.docx', '.doc', '.xlsx', '.xls',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        '.html', '.css', '.xml', '.json', '.yaml', '.yml'
    }
    
    # OCR settings
    OCR_LANGUAGES = ['eng', 'por']  # English and Portuguese
    OCR_ENGINE = 'tesseract'
    
    # Vector store settings
    VECTOR_STORE_TYPE = 'chromadb'  # or 'faiss'
    COLLECTION_NAME = 'university_documents'
    
    # GPU/CPU settings
    DEVICE = 'auto'  # 'auto', 'cpu', 'cuda', 'mps'
    MAX_WORKERS = 4
    
    # Output settings
    OUTPUT_DIR = 'RAGfiles'
    MARKDOWN_TEMPLATE = 'notes_template.md'
    
    # Language settings
    DEFAULT_LANGUAGE = 'pt'  # Portuguese as default
    SUPPORTED_LANGUAGES = ['pt', 'en']
    
    @classmethod
    def get_device(cls) -> str:
        """Automatically detect the best available device"""
        if cls.DEVICE == 'auto':
            try:
                import torch
                if torch.cuda.is_available():
                    return 'cuda'
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    return 'mps'
                else:
                    return 'cpu'
            except ImportError:
                return 'cpu'
        return cls.DEVICE
    
    @classmethod
    def get_embedding_model(cls) -> str:
        """Get the embedding model based on language support"""
        return cls.EMBEDDING_MODEL
    
    @classmethod
    def get_supported_extensions(cls) -> set:
        """Get supported file extensions"""
        return cls.SUPPORTED_EXTENSIONS.copy()
    
    @classmethod
    def get_ocr_languages(cls) -> List[str]:
        """Get OCR language codes"""
        return cls.OCR_LANGUAGES.copy()


