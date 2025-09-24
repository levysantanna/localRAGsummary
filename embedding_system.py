"""
Embedding system with multilingual support and GPU/CPU compatibility
"""
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import faiss
import chromadb
from chromadb.config import Settings
import pickle
import os
from pathlib import Path

from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingSystem:
    """Multilingual embedding system with GPU/CPU support"""
    
    def __init__(self):
        self.device = self._setup_device()
        self.embedding_model = None
        self.tokenizer = None
        self.vector_store = None
        self.chroma_client = None
        self.collection = None
        
        self._load_models()
        self._setup_vector_store()
    
    def _setup_device(self) -> str:
        """Setup device (GPU/CPU) based on availability"""
        if DEVICE_CONFIG['use_gpu'] and torch.cuda.is_available():
            device = 'cuda'
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
            # Set memory fraction to avoid OOM
            if DEVICE_CONFIG['gpu_memory_fraction'] < 1.0:
                torch.cuda.set_per_process_memory_fraction(DEVICE_CONFIG['gpu_memory_fraction'])
        else:
            device = 'cpu'
            logger.info("Using CPU")
        
        return device
    
    def _load_models(self):
        """Load embedding models"""
        try:
            # Load multilingual sentence transformer
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer(
                MODEL_CONFIG['embedding_model'],
                device=self.device
            )
            
            # Load Portuguese BERT for better Portuguese understanding
            if LANGUAGE_CONFIG['default_language'] == 'pt':
                try:
                    self.portuguese_model = SentenceTransformer(
                        'neuralmind/bert-base-portuguese-cased',
                        device=self.device
                    )
                    logger.info("Portuguese BERT model loaded")
                except Exception as e:
                    logger.warning(f"Could not load Portuguese BERT: {e}")
                    self.portuguese_model = None
            
            logger.info("Embedding models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading embedding models: {e}")
            raise
    
    def _setup_vector_store(self):
        """Setup vector database"""
        try:
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=str(VECTOR_DB_DIR),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=VECTOR_DB_CONFIG['collection_name']
                )
                logger.info(f"Loaded existing collection: {VECTOR_DB_CONFIG['collection_name']}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=VECTOR_DB_CONFIG['collection_name'],
                    metadata={"description": "University documents collection"}
                )
                logger.info(f"Created new collection: {VECTOR_DB_CONFIG['collection_name']}")
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {e}")
            # Fallback to FAISS
            self._setup_faiss_fallback()
    
    def _setup_faiss_fallback(self):
        """Setup FAISS as fallback vector store"""
        try:
            logger.info("Setting up FAISS fallback")
            self.faiss_index = faiss.IndexFlatIP(VECTOR_DB_CONFIG['embedding_dimension'])
            self.faiss_metadata = []
            self.faiss_vectors = []
        except Exception as e:
            logger.error(f"Error setting up FAISS fallback: {e}")
    
    def embed_text(self, text: str, language: str = 'pt') -> np.ndarray:
        """Generate embeddings for text"""
        try:
            if language == 'pt' and hasattr(self, 'portuguese_model') and self.portuguese_model:
                # Use Portuguese-specific model
                embedding = self.portuguese_model.encode(text, convert_to_tensor=True)
            else:
                # Use multilingual model
                embedding = self.embedding_model.encode(text, convert_to_tensor=True)
            
            # Convert to numpy array
            if isinstance(embedding, torch.Tensor):
                embedding = embedding.cpu().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(VECTOR_DB_CONFIG['embedding_dimension'])
    
    def embed_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Embed a list of documents"""
        embedded_docs = []
        
        for doc in documents:
            try:
                # Extract text content
                text = self._extract_text_from_document(doc)
                
                if not text.strip():
                    logger.warning(f"No text content found in document: {doc.get('file_path', 'unknown')}")
                    continue
                
                # Generate embedding
                embedding = self.embed_text(text, doc.get('language', 'pt'))
                
                # Create document with embedding
                embedded_doc = {
                    'id': doc.get('file_hash', f"doc_{len(embedded_docs)}"),
                    'text': text,
                    'embedding': embedding,
                    'metadata': {
                        'file_path': doc.get('file_path', ''),
                        'file_type': doc.get('file_type', ''),
                        'file_hash': doc.get('file_hash', ''),
                        'language': doc.get('language', 'pt'),
                        'processed_at': doc.get('processed_at', ''),
                        'statistics': doc.get('content', {}).get('statistics', {})
                    }
                }
                
                embedded_docs.append(embedded_doc)
                
            except Exception as e:
                logger.error(f"Error embedding document: {e}")
                continue
        
        logger.info(f"Successfully embedded {len(embedded_docs)} documents")
        return embedded_docs
    
    def _extract_text_from_document(self, doc: Dict[str, Any]) -> str:
        """Extract text content from document"""
        content = doc.get('content', {})
        
        # Extract main text
        text = content.get('text', '')
        
        # Add code content if available
        if content.get('code_structure'):
            code_text = self._extract_code_text(content['code_structure'])
            text += f"\n\n--- Code Content ---\n{code_text}"
        
        # Add table content if available
        if content.get('tables'):
            table_text = self._extract_table_text(content['tables'])
            text += f"\n\n--- Tables ---\n{table_text}"
        
        return text
    
    def _extract_code_text(self, code_structure: Dict[str, Any]) -> str:
        """Extract readable text from code structure"""
        # This would be implemented based on the code analysis results
        # For now, return empty string
        return ""
    
    def _extract_table_text(self, tables: List[Dict[str, Any]]) -> str:
        """Extract text from tables"""
        table_texts = []
        for table in tables:
            table_text = f"Table {table.get('table', '')} (Page {table.get('page', '')}):\n"
            for row in table.get('data', []):
                table_text += " | ".join(str(cell) for cell in row) + "\n"
            table_texts.append(table_text)
        return "\n".join(table_texts)
    
    def store_embeddings(self, embedded_docs: List[Dict[str, Any]]) -> bool:
        """Store embeddings in vector database"""
        try:
            if self.collection:
                # Use ChromaDB
                return self._store_in_chromadb(embedded_docs)
            else:
                # Use FAISS fallback
                return self._store_in_faiss(embedded_docs)
                
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            return False
    
    def _store_in_chromadb(self, embedded_docs: List[Dict[str, Any]]) -> bool:
        """Store embeddings in ChromaDB"""
        try:
            # Prepare data for ChromaDB
            ids = [doc['id'] for doc in embedded_docs]
            embeddings = [doc['embedding'].tolist() for doc in embedded_docs]
            documents = [doc['text'] for doc in embedded_docs]
            
            # Flatten metadata for ChromaDB compatibility
            metadatas = []
            for doc in embedded_docs:
                metadata = doc['metadata'].copy()
                
                # Debug: print metadata structure
                logger.info(f"Original metadata: {metadata}")
                
                # Ensure metadata is not empty
                if not metadata:
                    metadata = {
                        'word_count': '0',
                        'character_count': '0',
                        'language': 'pt'
                    }
                
                # Flatten nested dictionaries and ensure all values are strings
                filtered_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, dict):
                        # Skip nested dictionaries
                        continue
                    filtered_metadata[key] = str(value)
                
                metadata = filtered_metadata
                
                logger.info(f"Processed metadata: {metadata}")
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Stored {len(embedded_docs)} documents in ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error storing in ChromaDB: {e}")
            return False
    
    def _store_in_faiss(self, embedded_docs: List[Dict[str, Any]]) -> bool:
        """Store embeddings in FAISS"""
        try:
            embeddings = np.array([doc['embedding'] for doc in embedded_docs])
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to FAISS index
            self.faiss_index.add(embeddings)
            
            # Store metadata
            for doc in embedded_docs:
                self.faiss_metadata.append(doc['metadata'])
                self.faiss_vectors.append(doc['embedding'])
            
            # Save FAISS index and metadata
            self._save_faiss_data()
            
            logger.info(f"Stored {len(embedded_docs)} documents in FAISS")
            return True
            
        except Exception as e:
            logger.error(f"Error storing in FAISS: {e}")
            return False
    
    def _save_faiss_data(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.faiss_index, str(VECTOR_DB_DIR / "faiss_index.bin"))
            
            # Save metadata
            with open(VECTOR_DB_DIR / "faiss_metadata.pkl", "wb") as f:
                pickle.dump(self.faiss_metadata, f)
            
            logger.info("FAISS data saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving FAISS data: {e}")
    
    def _load_faiss_data(self):
        """Load FAISS index and metadata from disk"""
        try:
            # Load FAISS index
            if (VECTOR_DB_DIR / "faiss_index.bin").exists():
                self.faiss_index = faiss.read_index(str(VECTOR_DB_DIR / "faiss_index.bin"))
                
                # Load metadata
                with open(VECTOR_DB_DIR / "faiss_metadata.pkl", "rb") as f:
                    self.faiss_metadata = pickle.load(f)
                
                logger.info("FAISS data loaded from disk")
                return True
            
        except Exception as e:
            logger.error(f"Error loading FAISS data: {e}")
        
        return False
    
    def search_similar(self, query: str, top_k: int = 5, language: str = 'pt') -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query, language)
            
            if self.collection:
                # Search in ChromaDB
                return self._search_chromadb(query, query_embedding, top_k)
            else:
                # Search in FAISS
                return self._search_faiss(query, query_embedding, top_k)
                
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            return []
    
    def _search_chromadb(self, query: str, query_embedding: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Search in ChromaDB"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            similar_docs = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'query': query
                }
                similar_docs.append(doc)
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []
    
    def _search_faiss(self, query: str, query_embedding: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Search in FAISS"""
        try:
            # Normalize query embedding
            query_embedding = query_embedding.reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            
            # Search
            distances, indices = self.faiss_index.search(query_embedding, top_k)
            
            similar_docs = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.faiss_metadata):
                    doc = {
                        'id': f"doc_{idx}",
                        'text': self.faiss_vectors[idx].tolist() if idx < len(self.faiss_vectors) else "",
                        'metadata': self.faiss_metadata[idx],
                        'similarity': float(distance),
                        'query': query
                    }
                    similar_docs.append(doc)
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error searching FAISS: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            if self.collection:
                count = self.collection.count()
                return {
                    'total_documents': count,
                    'database_type': 'ChromaDB',
                    'collection_name': VECTOR_DB_CONFIG['collection_name']
                }
            elif hasattr(self, 'faiss_index'):
                return {
                    'total_documents': self.faiss_index.ntotal,
                    'database_type': 'FAISS',
                    'embedding_dimension': self.faiss_index.d
                }
            else:
                return {'total_documents': 0, 'database_type': 'None'}
                
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'total_documents': 0, 'database_type': 'Error'}
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            if self.collection:
                # Delete and recreate collection
                self.chroma_client.delete_collection(VECTOR_DB_CONFIG['collection_name'])
                self.collection = self.chroma_client.create_collection(
                    name=VECTOR_DB_CONFIG['collection_name'],
                    metadata={"description": "University documents collection"}
                )
                logger.info("ChromaDB collection cleared")
            elif hasattr(self, 'faiss_index'):
                # Clear FAISS
                self.faiss_index.reset()
                self.faiss_metadata.clear()
                self.faiss_vectors.clear()
                logger.info("FAISS collection cleared")
                
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
