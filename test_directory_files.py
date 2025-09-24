#!/usr/bin/env python3
"""
Script para testar e diagnosticar arquivos no diretório
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import config
    print("✅ Config importado com sucesso")
    print(f"📁 Diretório de documentos: {config.DOCUMENTS_DIR}")
    print(f"📁 Diretório RAG: {config.RAGFILES_DIR}")
    print(f"📁 Banco de dados: {config.VECTOR_DB_DIR}")
    print()
except Exception as e:
    print(f"❌ Erro ao importar config: {e}")
    sys.exit(1)

def test_directory_files():
    """Testar arquivos no diretório"""
    documents_dir = Path(config.DOCUMENTS_DIR)
    
    print("🔍 Verificando diretório de documentos...")
    print(f"📁 Caminho: {documents_dir}")
    print(f"📁 Existe: {documents_dir.exists()}")
    
    if not documents_dir.exists():
        print("❌ Diretório não existe! Criando...")
        documents_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Diretório criado")
        return
    
    print(f"📁 É diretório: {documents_dir.is_dir()}")
    print()
    
    # Listar todos os arquivos
    print("📄 Listando todos os arquivos:")
    all_files = list(documents_dir.rglob("*"))
    print(f"📊 Total de itens: {len(all_files)}")
    
    for item in all_files:
        if item.is_file():
            print(f"📄 {item.relative_to(documents_dir)} ({item.stat().st_size} bytes)")
        elif item.is_dir():
            print(f"📁 {item.relative_to(documents_dir)}/")
    
    print()
    
    # Verificar por extensões suportadas
    print("🔍 Verificando extensões suportadas:")
    supported_files = []
    
    for category, extensions in config.SUPPORTED_EXTENSIONS.items():
        print(f"\n📂 {category.upper()}:")
        category_files = []
        
        for extension in extensions:
            files = list(documents_dir.rglob(f"*{extension}"))
            if files:
                print(f"  {extension}: {len(files)} arquivos")
                for file in files:
                    print(f"    📄 {file.relative_to(documents_dir)}")
                    category_files.extend(files)
            else:
                print(f"  {extension}: 0 arquivos")
        
        supported_files.extend(category_files)
        print(f"  📊 Total {category}: {len(category_files)}")
    
    print(f"\n📊 Total de arquivos suportados: {len(supported_files)}")
    
    # Verificar arquivos específicos
    print("\n🔍 Verificando arquivos específicos:")
    test_files = [
        "*.txt", "*.pdf", "*.png", "*.jpg", "*.jpeg", 
        "*.docx", "*.odt", "*.py", "*.js", "*.html"
    ]
    
    for pattern in test_files:
        files = list(documents_dir.rglob(pattern))
        print(f"  {pattern}: {len(files)} arquivos")
        for file in files[:3]:  # Mostrar apenas os primeiros 3
            print(f"    📄 {file.relative_to(documents_dir)}")
        if len(files) > 3:
            print(f"    ... e mais {len(files) - 3} arquivos")

def test_rag_directory():
    """Testar diretório RAG"""
    rag_dir = Path(config.RAGFILES_DIR)
    
    print("\n🔍 Verificando diretório RAG...")
    print(f"📁 Caminho: {rag_dir}")
    print(f"📁 Existe: {rag_dir.exists()}")
    
    if not rag_dir.exists():
        print("❌ Diretório RAG não existe! Criando...")
        rag_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Diretório RAG criado")
        return
    
    # Listar arquivos RAG
    rag_files = list(rag_dir.rglob("*.md"))
    print(f"📄 Arquivos RAG encontrados: {len(rag_files)}")
    
    for file in rag_files:
        print(f"📄 {file.relative_to(rag_dir)}")

def test_vector_db():
    """Testar banco de dados vetorial"""
    vector_dir = Path(config.VECTOR_DB_DIR)
    
    print("\n🔍 Verificando banco de dados vetorial...")
    print(f"📁 Caminho: {vector_dir}")
    print(f"📁 Existe: {vector_dir.exists()}")
    
    if vector_dir.exists():
        db_files = list(vector_dir.rglob("*"))
        print(f"📄 Arquivos do banco: {len(db_files)}")
        
        for file in db_files:
            print(f"📄 {file.relative_to(vector_dir)}")

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de arquivos...")
    print("=" * 50)
    
    test_directory_files()
    test_rag_directory()
    test_vector_db()
    
    print("\n✅ Diagnóstico concluído!")
