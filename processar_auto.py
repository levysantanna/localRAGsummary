#!/usr/bin/env python3
"""
Processador Automático de Documentos RAG Local
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import time

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos do sistema
try:
    import config
    from enhanced_document_processor import EnhancedDocumentProcessor
    print("✅ Módulos importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def list_files_in_directory(directory_path):
    """Listar arquivos suportados em um diretório"""
    if not directory_path or not Path(directory_path).exists():
        return []
    
    all_files = []
    for ext in config.SUPPORTED_EXTENSIONS.values():
        for extension in ext:
            all_files.extend(Path(directory_path).rglob(f"*{extension}"))
    
    return all_files

def process_single_file(file_path, processor):
    """Processar um único arquivo"""
    try:
        print(f"📄 Processando: {file_path.name}")
        
        # Processar arquivo
        result = processor.process_document_with_urls(file_path)
        
        if result and result.get('text'):
            text_length = len(result.get('text', ''))
            urls_count = result.get('urls_scraped', 0)
            print(f"✅ Sucesso: {file_path.name} ({text_length} chars, {urls_count} URLs)")
            return True
        else:
            print(f"❌ Falha: {file_path.name} (nenhum conteúdo extraído)")
            return False
        
    except Exception as e:
        print(f"❌ Erro: {file_path.name} - {str(e)}")
        return False

def process_all_files_auto(directory_path, max_files=50):
    """Processar todos os arquivos de um diretório automaticamente"""
    print(f"\n🚀 Processamento automático do diretório: {directory_path}")
    print("=" * 60)
    
    # Verificar se o diretório existe
    if not Path(directory_path).exists():
        print(f"❌ Diretório não encontrado: {directory_path}")
        return
    
    # Listar arquivos
    all_files = list_files_in_directory(directory_path)
    print(f"📊 Encontrados {len(all_files)} arquivos suportados")
    
    if not all_files:
        print("❌ Nenhum arquivo suportado encontrado")
        return
    
    # Limitar número de arquivos para teste
    if len(all_files) > max_files:
        print(f"⚠️ Limitando processamento aos primeiros {max_files} arquivos")
        all_files = all_files[:max_files]
    
    # Mostrar alguns arquivos
    print("\n📄 Arquivos que serão processados:")
    for i, file_path in enumerate(all_files[:10]):
        print(f"  {i+1}. {file_path.name}")
    if len(all_files) > 10:
        print(f"  ... e mais {len(all_files) - 10} arquivos")
    
    # Inicializar processador
    print("\n🔧 Inicializando processador...")
    processor = EnhancedDocumentProcessor()
    
    # Processar arquivos
    print("\n📝 Iniciando processamento...")
    start_time = time.time()
    
    processed_count = 0
    failed_count = 0
    
    for i, file_path in enumerate(all_files):
        print(f"\n[{i+1}/{len(all_files)}] ", end="")
        
        if process_single_file(file_path, processor):
            processed_count += 1
        else:
            failed_count += 1
        
        # Mostrar progresso a cada 5 arquivos
        if (i + 1) % 5 == 0:
            progress = ((i + 1) / len(all_files)) * 100
            print(f"📊 Progresso: {i+1}/{len(all_files)} ({progress:.1f}%)")
    
    # Resultados finais
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINAIS")
    print("=" * 60)
    print(f"✅ Arquivos processados com sucesso: {processed_count}")
    print(f"❌ Arquivos com falha: {failed_count}")
    print(f"📊 Total de arquivos: {len(all_files)}")
    print(f"⏱️ Tempo total: {total_time:.2f} segundos")
    print(f"📈 Taxa de sucesso: {(processed_count/len(all_files)*100):.1f}%")
    
    if processed_count > 0:
        print(f"\n🎉 Processamento concluído! {processed_count} arquivos foram processados com sucesso.")
    else:
        print(f"\n⚠️ Nenhum arquivo foi processado com sucesso.")

def main():
    """Função principal"""
    print("🤖 Sistema RAG Local - Processador Automático")
    print("=" * 60)
    
    # Diretório padrão
    directory = "/home/lsantann/Documents/CC/"
    
    print(f"📁 Processando diretório: {directory}")
    
    # Verificar se o diretório existe
    if not Path(directory).exists():
        print(f"❌ Diretório não encontrado: {directory}")
        return
    
    # Listar arquivos encontrados
    all_files = list_files_in_directory(directory)
    print(f"📊 Encontrados {len(all_files)} arquivos suportados no diretório")
    
    if not all_files:
        print("❌ Nenhum arquivo suportado encontrado")
        print("💡 Verifique se o diretório contém arquivos nos formatos suportados:")
        for file_type, extensions in config.SUPPORTED_EXTENSIONS.items():
            print(f"  - {file_type.upper()}: {', '.join(extensions)}")
        return
    
    # Processar automaticamente
    process_all_files_auto(directory)

if __name__ == "__main__":
    main()
