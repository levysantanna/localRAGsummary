"""
Sistema RAG Aprimorado - Interface Principal
"""
import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json

from enhanced_rag_system import EnhancedRAGSystem
from document_processor import DocumentProcessor
from config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_rag_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnhancedRAGMain:
    """Interface principal do sistema RAG aprimorado"""
    
    def __init__(self):
        self.enhanced_rag = EnhancedRAGSystem()
        self.document_processor = DocumentProcessor()
    
    def process_documents_with_scraping(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Processa documentos com web scraping"""
        try:
            logger.info(f"Processing documents with web scraping: {directory_path}")
            
            # Processa documentos básicos
            documents = self.document_processor.process_directory(
                directory_path, 
                recursive=recursive
            )
            
            if not documents:
                return {
                    'success': False,
                    'message': 'No documents found to process',
                    'documents_processed': 0
                }
            
            # Aplica web scraping
            enhanced_documents = self.enhanced_rag.process_documents_enhanced(documents)
            
            # Gera resumo aprimorado
            summary = self.enhanced_rag.generate_enhanced_summary()
            
            # Salva resumo
            summary_path = RAGFILES_DIR / "resumo_aprimorado.md"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # Estatísticas
            total_urls = sum(len(doc.get('enhanced_content', {}).get('urls_found', [])) 
                           for doc in enhanced_documents)
            successful_scrapes = sum(1 for doc in enhanced_documents 
                                   for scraped in doc.get('enhanced_content', {}).get('scraped_content', {}).values()
                                   if scraped.get('status') == 'success')
            
            return {
                'success': True,
                'message': f'Successfully processed {len(documents)} documents with web scraping',
                'documents_processed': len(documents),
                'urls_found': total_urls,
                'successful_scrapes': successful_scrapes,
                'enhanced_summary': str(summary_path)
            }
            
        except Exception as e:
            logger.error(f"Error processing documents with scraping: {e}")
            return {
                'success': False,
                'message': f'Error processing documents: {str(e)}',
                'documents_processed': 0
            }
    
    def train_llm_model(self, output_dir: str = "trained_model") -> Dict[str, Any]:
        """Treina modelo de linguagem"""
        try:
            if not self.enhanced_rag.processed_documents:
                return {
                    'success': False,
                    'message': 'No processed documents available for training'
                }
            
            logger.info("Training LLM model...")
            model_path = self.enhanced_rag.train_llm(output_dir)
            
            return {
                'success': True,
                'message': f'Model trained successfully',
                'model_path': model_path
            }
            
        except Exception as e:
            logger.error(f"Error training LLM: {e}")
            return {
                'success': False,
                'message': f'Error training model: {str(e)}'
            }
    
    def start_chat_interface(self) -> Dict[str, Any]:
        """Inicia interface de chat"""
        try:
            if not self.enhanced_rag.chat_interface:
                return {
                    'success': False,
                    'message': 'Chat interface not available. Train the model first.'
                }
            
            logger.info("Starting chat interface...")
            self.enhanced_rag.start_chat()
            
            return {
                'success': True,
                'message': 'Chat interface started'
            }
            
        except Exception as e:
            logger.error(f"Error starting chat interface: {e}")
            return {
                'success': False,
                'message': f'Error starting chat: {str(e)}'
            }
    
    def generate_enhanced_report(self) -> Dict[str, Any]:
        """Gera relatório aprimorado"""
        try:
            if not self.enhanced_rag.processed_documents:
                return {
                    'success': False,
                    'message': 'No processed documents available'
                }
            
            summary = self.enhanced_rag.generate_enhanced_summary()
            
            # Salva relatório
            report_path = RAGFILES_DIR / f"relatorio_aprimorado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            return {
                'success': True,
                'message': 'Enhanced report generated',
                'report_path': str(report_path)
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced report: {e}")
            return {
                'success': False,
                'message': f'Error generating report: {str(e)}'
            }

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Sistema RAG Aprimorado')
    parser.add_argument('--mode', choices=['process', 'train', 'chat', 'report', 'full'], 
                       required=True, help='Operation mode')
    parser.add_argument('--directory', type=str, help='Directory to process documents from')
    parser.add_argument('--recursive', action='store_true', default=True, 
                       help='Process directories recursively')
    parser.add_argument('--output-dir', type=str, default='trained_model', 
                       help='Output directory for trained model')
    parser.add_argument('--language', type=str, default='pt', choices=['pt', 'en'], 
                       help='Language for processing')
    
    args = parser.parse_args()
    
    # Initialize system
    enhanced_main = EnhancedRAGMain()
    
    try:
        if args.mode == 'process':
            if not args.directory:
                print("Error: --directory is required for process mode")
                sys.exit(1)
            
            result = enhanced_main.process_documents_with_scraping(
                args.directory, 
                recursive=args.recursive
            )
            
            if result['success']:
                print(f"✅ Successfully processed {result['documents_processed']} documents")
                print(f"🔗 URLs found: {result['urls_found']}")
                print(f"✅ Successful scrapes: {result['successful_scrapes']}")
                print(f"📄 Enhanced summary: {result['enhanced_summary']}")
            else:
                print(f"❌ Error: {result['message']}")
        
        elif args.mode == 'train':
            result = enhanced_main.train_llm_model(args.output_dir)
            
            if result['success']:
                print(f"✅ Model trained successfully: {result['model_path']}")
            else:
                print(f"❌ Error: {result['message']}")
        
        elif args.mode == 'chat':
            result = enhanced_main.start_chat_interface()
            
            if result['success']:
                print("✅ Chat interface started")
            else:
                print(f"❌ Error: {result['message']}")
        
        elif args.mode == 'report':
            result = enhanced_main.generate_enhanced_report()
            
            if result['success']:
                print(f"✅ Enhanced report generated: {result['report_path']}")
            else:
                print(f"❌ Error: {result['message']}")
        
        elif args.mode == 'full':
            if not args.directory:
                print("Error: --directory is required for full mode")
                sys.exit(1)
            
            print("🚀 Running full enhanced RAG pipeline...")
            
            # 1. Process documents with scraping
            print("\n📄 Step 1: Processing documents with web scraping...")
            process_result = enhanced_main.process_documents_with_scraping(
                args.directory, 
                recursive=args.recursive
            )
            
            if not process_result['success']:
                print(f"❌ Document processing failed: {process_result['message']}")
                sys.exit(1)
            
            print(f"✅ Documents processed: {process_result['documents_processed']}")
            print(f"🔗 URLs found: {process_result['urls_found']}")
            print(f"✅ Successful scrapes: {process_result['successful_scrapes']}")
            
            # 2. Train LLM
            print("\n🤖 Step 2: Training LLM model...")
            train_result = enhanced_main.train_llm_model(args.output_dir)
            
            if not train_result['success']:
                print(f"❌ Model training failed: {train_result['message']}")
                sys.exit(1)
            
            print(f"✅ Model trained: {train_result['model_path']}")
            
            # 3. Generate enhanced report
            print("\n📊 Step 3: Generating enhanced report...")
            report_result = enhanced_main.generate_enhanced_report()
            
            if not report_result['success']:
                print(f"❌ Report generation failed: {report_result['message']}")
                sys.exit(1)
            
            print(f"✅ Enhanced report: {report_result['report_path']}")
            
            # 4. Start chat interface
            print("\n💬 Step 4: Starting chat interface...")
            print("You can now chat with your trained model!")
            enhanced_main.start_chat_interface()
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
