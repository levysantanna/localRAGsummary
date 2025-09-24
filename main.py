"""
Main application for Local RAG system
"""
import logging
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Import our modules
from config import *
from document_processor import DocumentProcessor
from embedding_system import EmbeddingSystem
from rag_agent import RAGAgent
from markdown_generator import MarkdownGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LocalRAGSystem:
    """Main Local RAG System class"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_system = EmbeddingSystem()
        self.rag_agent = RAGAgent(self.embedding_system)
        self.markdown_generator = MarkdownGenerator(self.rag_agent)
        
        logger.info("Local RAG System initialized successfully")
    
    def process_documents(self, directory_path: str, recursive: bool = True, 
                         language: str = 'pt') -> Dict[str, Any]:
        """Process all documents in a directory"""
        try:
            logger.info(f"Processing documents in: {directory_path}")
            
            # Process documents
            documents = self.document_processor.process_directory(
                directory_path, 
                recursive=recursive
            )
            
            if not documents:
                logger.warning("No documents found to process")
                return {
                    'success': False,
                    'message': 'No documents found to process',
                    'documents_processed': 0
                }
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embedded_docs = self.embedding_system.embed_documents(documents)
            
            if not embedded_docs:
                logger.error("Failed to generate embeddings")
                return {
                    'success': False,
                    'message': 'Failed to generate embeddings',
                    'documents_processed': 0
                }
            
            # Store embeddings
            logger.info("Storing embeddings...")
            store_success = self.embedding_system.store_embeddings(embedded_docs)
            
            if not store_success:
                logger.error("Failed to store embeddings")
                return {
                    'success': False,
                    'message': 'Failed to store embeddings',
                    'documents_processed': len(documents)
                }
            
            # Generate markdown notes
            logger.info("Generating markdown notes...")
            notes = self.markdown_generator.generate_document_notes(documents, language)
            summary = self.markdown_generator.generate_summary_notes(documents, language)
            
            logger.info(f"Successfully processed {len(documents)} documents")
            
            return {
                'success': True,
                'message': f'Successfully processed {len(documents)} documents',
                'documents_processed': len(documents),
                'embeddings_generated': len(embedded_docs),
                'notes_generated': len(notes),
                'summary_created': summary is not None,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            return {
                'success': False,
                'message': f'Error processing documents: {str(e)}',
                'documents_processed': 0
            }
    
    def query_documents(self, question: str, language: str = 'pt', 
                       context_limit: int = 5) -> Dict[str, Any]:
        """Query the document collection"""
        try:
            logger.info(f"Processing query: {question}")
            
            # Get response from RAG agent
            response = self.rag_agent.query(question, language, context_limit)
            
            # Generate query notes
            query_notes = self.markdown_generator.generate_query_notes([response], language)
            
            return {
                'success': True,
                'response': response,
                'query_notes_created': query_notes is not None,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'message': f'Error processing query: {str(e)}',
                'response': None,
                'language': language
            }
    
    def batch_query(self, questions: List[str], language: str = 'pt') -> Dict[str, Any]:
        """Process multiple queries"""
        try:
            logger.info(f"Processing {len(questions)} queries")
            
            # Process queries
            responses = self.rag_agent.batch_query(questions, language)
            
            # Generate query notes
            query_notes = self.markdown_generator.generate_query_notes(responses, language)
            
            return {
                'success': True,
                'responses': responses,
                'query_notes_created': query_notes is not None,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Error processing batch queries: {e}")
            return {
                'success': False,
                'message': f'Error processing batch queries: {str(e)}',
                'responses': [],
                'language': language
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        try:
            # Get collection stats
            collection_stats = self.embedding_system.get_collection_stats()
            
            # Get note list
            notes = self.markdown_generator.get_note_list()
            
            # Get system info
            system_info = {
                'collection_stats': collection_stats,
                'notes_count': len(notes),
                'notes': notes[:10],  # Show first 10 notes
                'system_ready': True,
                'timestamp': datetime.now().isoformat()
            }
            
            return system_info
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'collection_stats': {'total_documents': 0, 'database_type': 'Error'},
                'notes_count': 0,
                'notes': [],
                'system_ready': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def clear_system(self) -> Dict[str, Any]:
        """Clear all data from the system"""
        try:
            logger.info("Clearing system data...")
            
            # Clear embeddings
            self.embedding_system.clear_collection()
            
            # Clear notes (optional - ask user first)
            notes = self.markdown_generator.get_note_list()
            for note in notes:
                self.markdown_generator.delete_note(note['path'])
            
            logger.info("System cleared successfully")
            
            return {
                'success': True,
                'message': 'System cleared successfully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error clearing system: {e}")
            return {
                'success': False,
                'message': f'Error clearing system: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(description='Local RAG System for University Documents')
    parser.add_argument('--mode', choices=['process', 'query', 'batch', 'status', 'clear'], 
                       required=True, help='Operation mode')
    parser.add_argument('--directory', type=str, help='Directory to process documents from')
    parser.add_argument('--question', type=str, help='Question to ask the system')
    parser.add_argument('--questions', type=str, help='JSON file with questions for batch processing')
    parser.add_argument('--language', type=str, default='pt', choices=['pt', 'en'], 
                       help='Language for processing and responses')
    parser.add_argument('--recursive', action='store_true', default=True, 
                       help='Process directories recursively')
    parser.add_argument('--context-limit', type=int, default=5, 
                       help='Number of context documents to use for queries')
    parser.add_argument('--output', type=str, help='Output file for results')
    
    args = parser.parse_args()
    
    # Initialize system
    rag_system = LocalRAGSystem()
    
    try:
        if args.mode == 'process':
            if not args.directory:
                print("Error: --directory is required for process mode")
                sys.exit(1)
            
            result = rag_system.process_documents(
                args.directory, 
                recursive=args.recursive,
                language=args.language
            )
            
            print(f"Processing result: {result['message']}")
            if result['success']:
                print(f"Documents processed: {result['documents_processed']}")
                print(f"Embeddings generated: {result['embeddings_generated']}")
                print(f"Notes generated: {result['notes_generated']}")
        
        elif args.mode == 'query':
            if not args.question:
                print("Error: --question is required for query mode")
                sys.exit(1)
            
            result = rag_system.query_documents(
                args.question,
                language=args.language,
                context_limit=args.context_limit
            )
            
            if result['success']:
                response = result['response']
                print(f"Question: {response['question']}")
                print(f"Answer: {response['answer']}")
                print(f"Confidence: {response['confidence']:.2f}")
                print(f"Sources: {len(response['sources'])}")
            else:
                print(f"Error: {result['message']}")
        
        elif args.mode == 'batch':
            if not args.questions:
                print("Error: --questions is required for batch mode")
                sys.exit(1)
            
            # Load questions from JSON file
            with open(args.questions, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            questions = questions_data.get('questions', [])
            if not questions:
                print("Error: No questions found in JSON file")
                sys.exit(1)
            
            result = rag_system.batch_query(questions, language=args.language)
            
            if result['success']:
                print(f"Processed {len(result['responses'])} queries")
                for i, response in enumerate(result['responses'], 1):
                    print(f"\nQuery {i}: {response['question']}")
                    print(f"Answer: {response['answer']}")
                    print(f"Confidence: {response['confidence']:.2f}")
            else:
                print(f"Error: {result['message']}")
        
        elif args.mode == 'status':
            status = rag_system.get_system_status()
            print(f"System Status:")
            print(f"  Ready: {status['system_ready']}")
            print(f"  Documents: {status['collection_stats']['total_documents']}")
            print(f"  Database: {status['collection_stats']['database_type']}")
            print(f"  Notes: {status['notes_count']}")
            
            if status['notes']:
                print(f"\nRecent Notes:")
                for note in status['notes'][:5]:
                    print(f"  - {note['filename']} ({note['modified_at']})")
        
        elif args.mode == 'clear':
            confirm = input("Are you sure you want to clear all system data? (yes/no): ")
            if confirm.lower() == 'yes':
                result = rag_system.clear_system()
                print(f"Clear result: {result['message']}")
            else:
                print("Operation cancelled")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Results saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
