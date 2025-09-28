#!/usr/bin/env python3
"""
Script para testar processamento de todos os tipos de arquivo
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
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def test_file_type_processing():
    """Testar processamento por tipo de arquivo"""
    print("\n🔍 Testando processamento por tipo de arquivo...")
    
    documents_dir = Path(config.DOCUMENTS_DIR)
    
    # Obter todos os arquivos por categoria
    file_categories = {}
    for category, extensions in config.SUPPORTED_EXTENSIONS.items():
        category_files = []
        for extension in extensions:
            files = list(documents_dir.rglob(f"*{extension}"))
            category_files.extend(files)
        file_categories[category] = category_files
        print(f"📂 {category.upper()}: {len(category_files)} arquivos")
        for file in category_files:
            print(f"  📄 {file.name}")
    
    print(f"\n📊 Total de arquivos por categoria:")
    for category, files in file_categories.items():
        print(f"  {category}: {len(files)} arquivos")
    
    return file_categories

def test_processing_by_category():
    """Testar processamento por categoria"""
    print("\n🔍 Testando processamento por categoria...")
    
    try:
        processor = EnhancedDocumentProcessor()
        print("✅ Processador inicializado")
        
        documents_dir = Path(config.DOCUMENTS_DIR)
        
        # Processar cada categoria
        for category, extensions in config.SUPPORTED_EXTENSIONS.items():
            print(f"\n📂 Processando categoria: {category.upper()}")
            
            category_files = []
            for extension in extensions:
                files = list(documents_dir.rglob(f"*{extension}"))
                category_files.extend(files)
            
            if not category_files:
                print(f"  ⚠️ Nenhum arquivo {category} encontrado")
                continue
            
            print(f"  📊 {len(category_files)} arquivos encontrados")
            
            for file_path in category_files:
                print(f"  📄 Processando: {file_path.name}")
                
                try:
                    start_time = datetime.now()
                    result = processor.process_document_with_urls(file_path)
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    if result and result.get('text'):
                        text_length = len(result.get('text', ''))
                        urls_count = len(result.get('urls', []))
                        print(f"    ✅ Sucesso - {text_length} chars, {urls_count} URLs, {duration:.2f}s")
                    else:
                        print(f"    ❌ Falha - nenhum conteúdo extraído, {duration:.2f}s")
                        
                except Exception as e:
                    print(f"    ❌ Erro: {e}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def test_specific_file_types():
    """Testar tipos de arquivo específicos"""
    print("\n🔍 Testando tipos de arquivo específicos...")
    
    documents_dir = Path(config.DOCUMENTS_DIR)
    
    # Testar cada tipo específico
    test_patterns = [
        ("TXT", "*.txt"),
        ("PDF", "*.pdf"),
        ("PNG", "*.png"),
        ("JPG", "*.jpg"),
        ("JPEG", "*.jpeg"),
        ("DOCX", "*.docx"),
        ("DOC", "*.doc"),
        ("PPTX", "*.pptx"),
        ("PPT", "*.ppt"),
        ("ODT", "*.odt"),
        ("ODS", "*.ods"),
        ("ODP", "*.odp"),
        ("PY", "*.py"),
        ("JS", "*.js"),
        ("HTML", "*.html"),
        ("CSS", "*.css"),
        ("JSON", "*.json"),
        ("XML", "*.xml"),
        ("YAML", "*.yaml"),
        ("YML", "*.yml")
    ]
    
    for file_type, pattern in test_patterns:
        files = list(documents_dir.rglob(pattern))
        print(f"  {file_type}: {len(files)} arquivos")
        for file in files[:3]:  # Mostrar apenas os primeiros 3
            print(f"    📄 {file.name}")

def test_enhanced_processor():
    """Testar o processador aprimorado"""
    print("\n🔍 Testando processador aprimorado...")
    
    try:
        processor = EnhancedDocumentProcessor()
        print("✅ Processador aprimorado inicializado")
        
        # Obter todos os arquivos
        documents_dir = Path(config.DOCUMENTS_DIR)
        all_files = []
        for ext in config.SUPPORTED_EXTENSIONS.values():
            for extension in ext:
                all_files.extend(documents_dir.rglob(f"*{extension}"))
        
        print(f"📊 Total de arquivos encontrados: {len(all_files)}")
        
        if not all_files:
            print("❌ Nenhum arquivo encontrado para processar")
            return
        
        # Processar alguns arquivos
        for i, file_path in enumerate(all_files[:5]):  # Processar apenas os primeiros 5
            print(f"\n📄 Processando {i+1}/5: {file_path.name}")
            
            try:
                start_time = datetime.now()
                result = processor.process_document_with_urls(file_path)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                if result and result.get('text'):
                    text_length = len(result.get('text', ''))
                    urls_count = len(result.get('urls', []))
                    print(f"  ✅ Sucesso - {text_length} chars, {urls_count} URLs, {duration:.2f}s")
                else:
                    print(f"  ❌ Falha - nenhum conteúdo extraído, {duration:.2f}s")
                    
            except Exception as e:
                print(f"  ❌ Erro: {e}")
        
    except Exception as e:
        print(f"❌ Erro no processador aprimorado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando teste de todos os tipos de arquivo...")
    print("=" * 60)
    
    test_file_type_processing()
    test_specific_file_types()
    test_processing_by_category()
    test_enhanced_processor()
    
    print("\n✅ Teste concluído!")
