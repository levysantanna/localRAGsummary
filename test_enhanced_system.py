#!/usr/bin/env python3
"""
Teste do Sistema RAG Aprimorado
"""
import sys
import os
from pathlib import Path
import logging

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from enhanced_rag_system import EnhancedRAGSystem
from document_processor import DocumentProcessor
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_system():
    """Testa o sistema RAG aprimorado"""
    
    print("🚀 Teste do Sistema RAG Local Aprimorado")
    print("=" * 60)
    
    try:
        # 1. Inicializa sistema
        print("\n📋 Passo 1: Inicializando sistema...")
        enhanced_rag = EnhancedRAGSystem()
        document_processor = DocumentProcessor()
        
        # 2. Processa documentos básicos
        print("\n📄 Passo 2: Processando documentos...")
        documents = document_processor.process_directory("documents", recursive=True)
        
        if not documents:
            print("❌ Nenhum documento encontrado para processar")
            return False
        
        print(f"✅ {len(documents)} documentos encontrados")
        
        # Mostra documentos encontrados
        for i, doc in enumerate(documents, 1):
            file_path = doc.get('file_path', 'Desconhecido')
            print(f"  {i}. {Path(file_path).name}")
        
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
        if total_urls > 0:
            print(f"✅ Taxa de sucesso: {(successful_scrapes/total_urls*100):.1f}%")
        
        # Mostra URLs encontradas
        if total_urls > 0:
            print("\n🔗 URLs encontradas nos documentos:")
            for doc in enhanced_documents:
                urls = doc.get('enhanced_content', {}).get('urls_found', [])
                if urls:
                    file_name = Path(doc.get('file_path', '')).name
                    print(f"  📄 {file_name}:")
                    for url in urls[:3]:  # Mostra apenas as primeiras 3
                        print(f"    - {url}")
                    if len(urls) > 3:
                        print(f"    ... e mais {len(urls) - 3} URLs")
        
        # 4. Gera relatório aprimorado
        print(f"\n📊 Passo 4: Gerando relatório aprimorado...")
        summary = enhanced_rag.generate_enhanced_summary()
        
        # Salva relatório
        report_path = RAGFILES_DIR / "teste_relatorio_aprimorado.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✅ Relatório salvo em: {report_path}")
        
        # 5. Mostra preview do relatório
        print(f"\n📖 Preview do relatório gerado:")
        print("-" * 40)
        lines = summary.split('\n')[:20]  # Primeiras 20 linhas
        for line in lines:
            print(line)
        if len(summary.split('\n')) > 20:
            print("... (relatório completo salvo no arquivo)")
        
        # 6. Testa funcionalidades básicas
        print(f"\n🧪 Passo 5: Testando funcionalidades básicas...")
        
        # Testa busca de contexto
        if enhanced_rag.chat_interface:
            print("✅ Interface de chat disponível")
        else:
            print("ℹ️ Interface de chat não disponível (modelo não treinado)")
        
        # Testa embedding
        if enhanced_documents:
            doc = enhanced_documents[0]
            enhanced_content = doc.get('enhanced_content', {})
            if 'embedding' in enhanced_content:
                embedding_dim = len(enhanced_content['embedding'])
                print(f"✅ Embeddings gerados: dimensão {embedding_dim}")
            else:
                print("ℹ️ Embeddings não gerados")
        
        # 7. Resumo final
        print(f"\n🎉 Teste do Sistema RAG Aprimorado Concluído!")
        print("=" * 60)
        print(f"📊 Resumo dos resultados:")
        print(f"  - Documentos processados: {len(documents)}")
        print(f"  - URLs encontradas: {total_urls}")
        print(f"  - URLs processadas: {successful_scrapes}")
        print(f"  - Relatório gerado: {report_path}")
        print(f"  - Sistema funcionando: ✅")
        
        print(f"\n🚀 Próximos passos:")
        print(f"  1. Treinar modelo: python enhanced_main.py --mode train")
        print(f"  2. Iniciar chat: python enhanced_main.py --mode chat")
        print(f"  3. Interface web: python run_enhanced_system.py --interface gradio")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in enhanced system test: {e}")
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Iniciando teste do sistema RAG aprimorado...")
    
    # Verifica se os documentos existem
    if not Path("documents").exists():
        print("❌ Diretório 'documents' não encontrado")
        print("💡 Dica: Crie o diretório e adicione seus documentos")
        return
    
    # Executa teste
    success = test_enhanced_system()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou. Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
