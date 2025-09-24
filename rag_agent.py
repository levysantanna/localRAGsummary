"""
RAG Agent for query processing and response generation with Portuguese support
"""
import logging
import torch
from typing import List, Dict, Any, Optional, Union
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
from datetime import datetime
import json

from config import *
from embedding_system import EmbeddingSystem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGAgent:
    """RAG Agent for document querying and response generation"""
    
    def __init__(self, embedding_system: EmbeddingSystem):
        self.embedding_system = embedding_system
        self.device = self._setup_device()
        self.llm_model = None
        self.tokenizer = None
        self.portuguese_llm = None
        
        self._load_llm_models()
    
    def _setup_device(self) -> str:
        """Setup device for LLM inference"""
        if DEVICE_CONFIG['use_gpu'] and torch.cuda.is_available():
            device = 'cuda'
            logger.info(f"Using GPU for LLM: {torch.cuda.get_device_name()}")
        else:
            device = 'cpu'
            logger.info("Using CPU for LLM")
        
        return device
    
    def _load_llm_models(self):
        """Load language models for text generation"""
        try:
            # Load main LLM model
            logger.info("Loading LLM model...")
            
            # Try to load a Portuguese model first
            try:
                # Try to load a Portuguese-specific model
            try:
                self.portuguese_llm = pipeline(
                    "text-generation",
                    model="neuralmind/bert-base-portuguese-cased",
                    device=0 if self.device == 'cuda' else -1,
                    max_length=512,
                    do_sample=True,
                    temperature=0.7
                )
                logger.info("Portuguese LLM model loaded")
            except Exception as e:
                logger.warning(f"Could not load Portuguese LLM: {e}")
                self.portuguese_llm = None
            
            # Fallback to general model
            try:
                self.llm_model = pipeline(
                    "text-generation",
                    model=MODEL_CONFIG['llm_model'],
                    device=0 if self.device == 'cuda' else -1,
                    max_length=512,
                    do_sample=True,
                    temperature=0.7
                )
                logger.info("General LLM model loaded")
            except Exception as e:
                logger.warning(f"Could not load general LLM: {e}")
                # Use a simpler approach
                self.llm_model = None
            
            logger.info("LLM models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LLM models: {e}")
            # Continue without LLM for basic functionality
    
    def query(self, question: str, language: str = 'pt', context_limit: int = 5) -> Dict[str, Any]:
        """Process a query and generate response"""
        try:
            logger.info(f"Processing query: {question}")
            
            # Search for relevant documents
            similar_docs = self.embedding_system.search_similar(
                question, 
                top_k=context_limit,
                language=language
            )
            
            if not similar_docs:
                return {
                    'question': question,
                    'answer': "Desculpe, não encontrei informações relevantes nos documentos.",
                    'sources': [],
                    'confidence': 0.0,
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Filter by similarity threshold
            relevant_docs = [
                doc for doc in similar_docs 
                if doc.get('similarity', 0) >= RAG_CONFIG['similarity_threshold']
            ]
            
            if not relevant_docs:
                return {
                    'question': question,
                    'answer': "Não encontrei informações suficientemente relevantes nos documentos.",
                    'sources': [],
                    'confidence': 0.0,
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Generate response
            response = self._generate_response(question, relevant_docs, language)
            
            return {
                'question': question,
                'answer': response['answer'],
                'sources': self._format_sources(relevant_docs),
                'confidence': response['confidence'],
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'context_documents': len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'question': question,
                'answer': f"Erro ao processar a consulta: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'language': language,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_response(self, question: str, relevant_docs: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """Generate response based on relevant documents"""
        try:
            # Prepare context
            context = self._prepare_context(relevant_docs)
            
            # Create prompt
            prompt = self._create_prompt(question, context, language)
            
            # Generate response using LLM
            if self.portuguese_llm and language == 'pt':
                response_text = self._generate_with_llm(prompt, self.portuguese_llm)
            elif self.llm_model:
                response_text = self._generate_with_llm(prompt, self.llm_model)
            else:
                # Fallback to template-based response
                response_text = self._generate_template_response(question, context, language)
            
            # Calculate confidence based on document similarities
            confidence = self._calculate_confidence(relevant_docs)
            
            return {
                'answer': response_text,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'answer': f"Erro ao gerar resposta: {str(e)}",
                'confidence': 0.0
            }
    
    def _prepare_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Prepare context from relevant documents"""
        context_parts = []
        
        for i, doc in enumerate(relevant_docs, 1):
            text = doc.get('text', '')[:RAG_CONFIG['max_context_length']]
            metadata = doc.get('metadata', {})
            file_path = metadata.get('file_path', 'Documento desconhecido')
            
            context_parts.append(f"Documento {i} ({file_path}):\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str, language: str) -> str:
        """Create prompt for LLM"""
        if language == 'pt':
            prompt = f"""Com base nos documentos fornecidos, responda à pergunta de forma clara e precisa.

Documentos:
{context}

Pergunta: {question}

Resposta:"""
        else:
            prompt = f"""Based on the provided documents, answer the question clearly and accurately.

Documents:
{context}

Question: {question}

Answer:"""
        
        return prompt
    
    def _generate_with_llm(self, prompt: str, llm_model) -> str:
        """Generate response using LLM"""
        try:
            # Truncate prompt if too long
            max_length = RAG_CONFIG['max_context_length']
            if len(prompt) > max_length:
                prompt = prompt[:max_length]
            
            # Generate response
            response = llm_model(
                prompt,
                max_length=min(len(prompt) + 200, 1024),
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=llm_model.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            
            # Remove the original prompt from response
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating with LLM: {e}")
            return "Erro ao gerar resposta com o modelo de linguagem."
    
    def _generate_template_response(self, question: str, context: str, language: str) -> str:
        """Generate template-based response as fallback"""
        if language == 'pt':
            return f"""Com base nos documentos encontrados, posso fornecer as seguintes informações:

{context}

Esta resposta foi gerada com base na análise dos documentos disponíveis. Para informações mais específicas, consulte os documentos originais."""
        else:
            return f"""Based on the found documents, I can provide the following information:

{context}

This response was generated based on the analysis of available documents. For more specific information, please refer to the original documents."""
    
    def _calculate_confidence(self, relevant_docs: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on document similarities"""
        if not relevant_docs:
            return 0.0
        
        similarities = [doc.get('similarity', 0) for doc in relevant_docs]
        avg_similarity = sum(similarities) / len(similarities)
        
        # Normalize to 0-1 range
        confidence = min(avg_similarity, 1.0)
        return confidence
    
    def _format_sources(self, relevant_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for response"""
        sources = []
        
        for doc in relevant_docs:
            metadata = doc.get('metadata', {})
            source = {
                'file_path': metadata.get('file_path', ''),
                'file_type': metadata.get('file_type', ''),
                'similarity': doc.get('similarity', 0),
                'text_preview': doc.get('text', '')[:200] + '...' if len(doc.get('text', '')) > 200 else doc.get('text', '')
            }
            sources.append(source)
        
        return sources
    
    def batch_query(self, questions: List[str], language: str = 'pt') -> List[Dict[str, Any]]:
        """Process multiple queries in batch"""
        results = []
        
        for question in questions:
            try:
                result = self.query(question, language)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing batch query '{question}': {e}")
                results.append({
                    'question': question,
                    'answer': f"Erro ao processar: {str(e)}",
                    'sources': [],
                    'confidence': 0.0,
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def get_document_summary(self, file_path: str, language: str = 'pt') -> Dict[str, Any]:
        """Get summary of a specific document"""
        try:
            # Search for the specific document
            similar_docs = self.embedding_system.search_similar(
                f"resumo do documento {file_path}",
                top_k=1,
                language=language
            )
            
            if not similar_docs:
                return {
                    'file_path': file_path,
                    'summary': "Documento não encontrado na base de dados.",
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Generate summary
            doc = similar_docs[0]
            summary_prompt = f"Faça um resumo do seguinte documento:\n\n{doc.get('text', '')[:1000]}"
            
            if self.portuguese_llm and language == 'pt':
                summary = self._generate_with_llm(summary_prompt, self.portuguese_llm)
            elif self.llm_model:
                summary = self._generate_with_llm(summary_prompt, self.llm_model)
            else:
                # Template summary
                summary = f"Resumo do documento {file_path}:\n\n{doc.get('text', '')[:500]}..."
            
            return {
                'file_path': file_path,
                'summary': summary,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'metadata': doc.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error generating document summary: {e}")
            return {
                'file_path': file_path,
                'summary': f"Erro ao gerar resumo: {str(e)}",
                'language': language,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_collection_overview(self, language: str = 'pt') -> Dict[str, Any]:
        """Get overview of the document collection"""
        try:
            stats = self.embedding_system.get_collection_stats()
            
            if language == 'pt':
                overview = {
                    'total_documents': stats.get('total_documents', 0),
                    'database_type': stats.get('database_type', 'Desconhecido'),
                    'description': f"Coleção contém {stats.get('total_documents', 0)} documentos",
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                overview = {
                    'total_documents': stats.get('total_documents', 0),
                    'database_type': stats.get('database_type', 'Unknown'),
                    'description': f"Collection contains {stats.get('total_documents', 0)} documents",
                    'language': language,
                    'timestamp': datetime.now().isoformat()
                }
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting collection overview: {e}")
            return {
                'total_documents': 0,
                'database_type': 'Error',
                'description': f"Erro ao obter informações: {str(e)}",
                'language': language,
                'timestamp': datetime.now().isoformat()
            }
