#!/usr/bin/env python3
"""
Script para testar o processamento com debug detalhado
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import config
    from enhanced_document_processor import EnhancedDocumentProcessor
    print("✅ Módulos importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def test_single_file_processing():
    """Testar processamento de um único arquivo"""
    print("\n🔍 Testando processamento de arquivo único...")
    
    documents_dir = Path(config.DOCUMENTS_DIR)
    txt_files = list(documents_dir.rglob("*.txt"))
    
    if not txt_files:
        print("❌ Nenhum arquivo .txt encontrado")
        return
    
    # Pegar o primeiro arquivo
    test_file = txt_files[0]
    print(f"📄 Testando arquivo: {test_file}")
    print(f"📊 Tamanho: {test_file.stat().st_size} bytes")
    
    try:
        # Inicializar processador
        processor = EnhancedDocumentProcessor()
        print("✅ Processador inicializado")
        
        # Processar arquivo
        print("🔄 Iniciando processamento...")
        start_time = datetime.now()
        
        result = processor.process_document_with_urls(test_file)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⏱️ Tempo de processamento: {duration:.2f}s")
        
        if result:
            print("✅ Processamento bem-sucedido!")
            print(f"📊 Texto extraído: {len(result.get('text', ''))} caracteres")
            print(f"📊 URLs encontradas: {len(result.get('urls', []))}")
            print(f"📊 Metadata: {result.get('metadata', {})}")
            
            if result.get('urls'):
                print("🔗 URLs encontradas:")
                for url in result['urls']:
                    print(f"  - {url}")
        else:
            print("❌ Processamento falhou - resultado vazio")
            
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        import traceback
        traceback.print_exc()

def test_all_files_processing():
    """Testar processamento de todos os arquivos"""
    print("\n🔍 Testando processamento de todos os arquivos...")
    
    documents_dir = Path(config.DOCUMENTS_DIR)
    
    # Obter todos os arquivos suportados
    all_files = []
    for ext in config.SUPPORTED_EXTENSIONS.values():
        for extension in ext:
            all_files.extend(documents_dir.rglob(f"*{extension}"))
    
    print(f"📊 Total de arquivos encontrados: {len(all_files)}")
    
    if not all_files:
        print("❌ Nenhum arquivo encontrado")
        return
    
    try:
        # Inicializar processador
        processor = EnhancedDocumentProcessor()
        print("✅ Processador inicializado")
        
        processed_count = 0
        failed_count = 0
        total_text_length = 0
        total_urls = 0
        
        for i, file_path in enumerate(all_files):
            print(f"\n📄 Processando {i+1}/{len(all_files)}: {file_path.name}")
            
            try:
                start_time = datetime.now()
                result = processor.process_document_with_urls(file_path)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if result and result.get('text'):
                    processed_count += 1
                    text_length = len(result.get('text', ''))
                    total_text_length += text_length
                    urls_count = len(result.get('urls', []))
                    total_urls += urls_count
                    
                    print(f"✅ Sucesso - {text_length} chars, {urls_count} URLs, {duration:.2f}s")
                else:
                    failed_count += 1
                    print(f"❌ Falha - nenhum conteúdo extraído, {duration:.2f}s")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Erro: {e}")
        
        print(f"\n📊 Resumo do processamento:")
        print(f"✅ Processados com sucesso: {processed_count}")
        print(f"❌ Falharam: {failed_count}")
        print(f"📊 Total de caracteres: {total_text_length}")
        print(f"🔗 Total de URLs: {total_urls}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def test_embedding_storage():
    """Testar armazenamento de embeddings"""
    print("\n🔍 Testando armazenamento de embeddings...")
    
    try:
        from embedding_system import EmbeddingSystem
        
        # Inicializar sistema de embeddings
        embedding_system = EmbeddingSystem()
        print("✅ Sistema de embeddings inicializado")
        
        # Verificar se há documentos no banco
        collection = embedding_system.collection
        count = collection.count()
        print(f"📊 Documentos no banco: {count}")
        
        if count > 0:
            # Obter alguns documentos
            results = collection.get(limit=5)
            print(f"📄 Primeiros {len(results['ids'])} documentos:")
            for i, doc_id in enumerate(results['ids']):
                print(f"  {i+1}. {doc_id}")
        
    except Exception as e:
        print(f"❌ Erro no sistema de embeddings: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando teste de processamento com debug...")
    print("=" * 60)
    
    test_single_file_processing()
    test_all_files_processing()
    test_embedding_storage()
    
    print("\n✅ Teste concluído!")
