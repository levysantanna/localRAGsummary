#!/usr/bin/env python3
"""
Script para executar o Sistema RAG Aprimorado completo
"""
import sys
import os
from pathlib import Path
import logging

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from enhanced_rag_system import EnhancedRAGSystem
from document_processor import DocumentProcessor
from chat_interface import create_gradio_interface, create_streamlit_interface
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_full_pipeline(documents_dir: str, output_dir: str = "trained_model"):
    """Executa o pipeline completo do sistema RAG aprimorado"""
    
    print("🚀 Sistema RAG Local Aprimorado - Pipeline Completo")
    print("=" * 60)
    
    try:
        # 1. Inicializa sistema
        print("\n📋 Passo 1: Inicializando sistema...")
        enhanced_rag = EnhancedRAGSystem()
        document_processor = DocumentProcessor()
        
        # 2. Processa documentos básicos
        print(f"\n📄 Passo 2: Processando documentos de {documents_dir}...")
        documents = document_processor.process_directory(documents_dir, recursive=True)
        
        if not documents:
            print("❌ Nenhum documento encontrado para processar")
            return False
        
        print(f"✅ {len(documents)} documentos encontrados")
        
        # 3. Aplica web scraping
        print("\n🔗 Passo 3: Aplicando web scraping...")
        enhanced_documents = enhanced_rag.process_documents_enhanced(documents)
        
        # Estatísticas do scraping
        total_urls = sum(len(doc.get('enhanced_content', {}).get('urls_found', [])) 
                        for doc in enhanced_documents)
        successful_scrapes = sum(1 for doc in enhanced_documents 
                               for scraped in doc.get('enhanced_content', {}).get('scraped_content', {}).values()
                               if scraped.get('status') == 'success')
        
        print(f"✅ URLs encontradas: {total_urls}")
        print(f"✅ URLs processadas com sucesso: {successful_scrapes}")
        print(f"✅ Taxa de sucesso: {(successful_scrapes/total_urls*100) if total_urls > 0 else 0:.1f}%")
        
        # 4. Treina modelo de linguagem
        print(f"\n🤖 Passo 4: Treinando modelo de linguagem...")
        model_path = enhanced_rag.train_llm(output_dir)
        print(f"✅ Modelo treinado salvo em: {model_path}")
        
        # 5. Gera relatório aprimorado
        print(f"\n📊 Passo 5: Gerando relatório aprimorado...")
        summary = enhanced_rag.generate_enhanced_summary()
        
        # Salva relatório
        report_path = RAGFILES_DIR / "relatorio_aprimorado_completo.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✅ Relatório salvo em: {report_path}")
        
        # 6. Inicia interface de chat
        print(f"\n💬 Passo 6: Iniciando interface de chat...")
        print("🎉 Sistema RAG Aprimorado configurado com sucesso!")
        print("\n📋 Resumo do que foi feito:")
        print(f"  - Documentos processados: {len(documents)}")
        print(f"  - URLs encontradas: {total_urls}")
        print(f"  - URLs processadas: {successful_scrapes}")
        print(f"  - Modelo treinado: {model_path}")
        print(f"  - Relatório gerado: {report_path}")
        
        print("\n🚀 Opções disponíveis:")
        print("1. Chat via terminal: python enhanced_main.py --mode chat")
        print("2. Interface Gradio: python run_enhanced_system.py --interface gradio")
        print("3. Interface Streamlit: python run_enhanced_system.py --interface streamlit")
        
        return enhanced_rag
        
    except Exception as e:
        logger.error(f"Error in full pipeline: {e}")
        print(f"❌ Erro no pipeline: {e}")
        return False

def start_gradio_interface(enhanced_rag: EnhancedRAGSystem):
    """Inicia interface Gradio"""
    try:
        print("🚀 Iniciando interface Gradio...")
        interface = create_gradio_interface(enhanced_rag)
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar interface Gradio: {e}")

def start_streamlit_interface(enhanced_rag: EnhancedRAGSystem):
    """Inicia interface Streamlit"""
    try:
        print("🚀 Iniciando interface Streamlit...")
        import subprocess
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "chat_interface.py", "--server.port", "8501"
        ])
    except Exception as e:
        print(f"❌ Erro ao iniciar interface Streamlit: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema RAG Aprimorado')
    parser.add_argument('--documents', type=str, default='documents', 
                       help='Directory with documents to process')
    parser.add_argument('--output', type=str, default='trained_model', 
                       help='Output directory for trained model')
    parser.add_argument('--interface', choices=['gradio', 'streamlit', 'terminal'], 
                       default='terminal', help='Chat interface to use')
    parser.add_argument('--skip-processing', action='store_true', 
                       help='Skip document processing (use existing data)')
    
    args = parser.parse_args()
    
    # Verifica se o diretório de documentos existe
    if not Path(args.documents).exists():
        print(f"❌ Diretório de documentos não encontrado: {args.documents}")
        print("💡 Dica: Coloque seus documentos na pasta 'documents' e execute novamente")
        return
    
    # Executa pipeline completo
    if not args.skip_processing:
        enhanced_rag = run_full_pipeline(args.documents, args.output)
        if not enhanced_rag:
            return
    else:
        print("⏭️ Pulando processamento de documentos...")
        # Aqui você carregaria um sistema já processado
        enhanced_rag = None
        print("❌ Sistema não encontrado. Execute sem --skip-processing primeiro.")
        return
    
    # Inicia interface de chat
    if args.interface == 'gradio':
        start_gradio_interface(enhanced_rag)
    elif args.interface == 'streamlit':
        start_streamlit_interface(enhanced_rag)
    else:
        print("\n💬 Iniciando chat via terminal...")
        enhanced_rag.start_chat()

if __name__ == "__main__":
    main()
