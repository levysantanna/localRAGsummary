#!/usr/bin/env python3
"""
Interface Web Melhorada - Sistema RAG Local
Com modelo de IA potente e interface completa
"""

import streamlit as st
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import json
import sqlite3

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="RAG Local - Interface Melhorada",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estado da sessão
if 'processing_status' not in st.session_state:
    st.session_state['processing_status'] = {
        'is_processing': False,
        'current_file': None,
        'processed_files': [],
        'failed_files': [],
        'total_files': 0,
        'progress': 0,
        'logs': [],
        'start_time': None
    }

if 'rag_system' not in st.session_state:
    st.session_state['rag_system'] = None

if 'vector_db_path' not in st.session_state:
    st.session_state['vector_db_path'] = "vector_db.sqlite"

# ============================================================================
# SISTEMA RAG PURO
# ============================================================================

class SimpleRAGSystem:
    """Sistema RAG simples e potente"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Inicializar banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                file_path TEXT,
                file_type TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                chunk_text TEXT,
                chunk_index INTEGER,
                vector TEXT,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Obter estatísticas do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT file_type, COUNT(*) FROM documents GROUP BY file_type")
        file_types = cursor.fetchall()
        
        conn.close()
        
        return {
            'documents': doc_count,
            'chunks': chunk_count,
            'file_types': file_types
        }
    
    def query(self, question: str, max_results: int = 5):
        """Fazer consulta RAG"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar chunks similares (busca simples por palavras-chave)
        question_words = question.lower().split()
        results = []
        
        cursor.execute("SELECT id, document_id, chunk_text, metadata FROM chunks")
        for row in cursor.fetchall():
            chunk_id, doc_id, chunk_text, metadata_json = row
            metadata = json.loads(metadata_json) if metadata_json else {}
            
            # Calcular similaridade simples
            chunk_words = chunk_text.lower().split()
            matches = sum(1 for word in question_words if word in chunk_text.lower())
            similarity = matches / len(question_words) if question_words else 0
            
            if similarity > 0.1:  # Threshold baixo para capturar mais resultados
                results.append({
                    'chunk_id': chunk_id,
                    'document_id': doc_id,
                    'chunk_text': chunk_text,
                    'similarity': similarity,
                    'metadata': metadata
                })
        
        conn.close()
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]

# ============================================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================================

def process_document_simple(file_path: Path) -> dict:
    """Processar documento de forma simples"""
    try:
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            return {'success': False, 'error': 'Arquivo vazio'}
        
        # Criar ID único
        import hashlib
        doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:16]
        
        # Salvar no banco
        conn = sqlite3.connect(st.session_state['vector_db_path'])
        cursor = conn.cursor()
        
        metadata = {
            'file_path': str(file_path),
            'file_type': file_path.suffix,
            'word_count': len(content.split()),
            'processed_at': datetime.now().isoformat()
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO documents (id, file_path, file_type, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (doc_id, str(file_path), file_path.suffix, content, json.dumps(metadata)))
        
        # Criar chunks
        chunk_size = 1000
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            cursor.execute('''
                INSERT OR REPLACE INTO chunks (id, document_id, chunk_text, chunk_index, vector, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (chunk_id, doc_id, chunk, i, json.dumps([]), json.dumps({'chunk_index': i})))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'doc_id': doc_id,
            'text_length': len(content),
            'chunks_count': len(chunks)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_all_files_improved():
    """Processar todos os arquivos com interface melhorada"""
    try:
        status = st.session_state['processing_status']
        
        # Resetar status
        status['is_processing'] = True
        status['processed_files'] = []
        status['failed_files'] = []
        status['logs'] = []
        status['start_time'] = datetime.now()
        
        # Obter arquivos
        documents_dir = Path("/home/lsantann/Documents/CC/")
        supported_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml']
        
        all_files = []
        for ext in supported_extensions:
            all_files.extend(documents_dir.rglob(f"*{ext}"))
        
        # Limitar a 100 arquivos
        all_files = all_files[:100]
        status['total_files'] = len(all_files)
        
        # Log de início
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🚀 Iniciando processamento de {len(all_files)} arquivos",
            'module': 'interface_melhorada'
        }
        status['logs'].append(log_entry)
        
        # Processar arquivos
        for i, file_path in enumerate(all_files):
            status['current_file'] = str(file_path)
            status['progress'] = (i / len(all_files)) * 100
            
            # Processar arquivo
            result = process_document_simple(file_path)
            
            if result['success']:
                status['processed_files'].append({
                    'file': str(file_path),
                    'size': result['text_length'],
                    'chunks': result['chunks_count'],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                log_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'SUCCESS',
                    'message': f"✅ {file_path.name} ({result['text_length']} chars, {result['chunks_count']} chunks)",
                    'module': 'interface_melhorada'
                }
            else:
                status['failed_files'].append({
                    'file': str(file_path),
                    'error': result['error'],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                log_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'WARNING',
                    'message': f"⚠️ {file_path.name} - {result['error']}",
                    'module': 'interface_melhorada'
                }
            
            status['logs'].append(log_entry)
            
            # Manter apenas os últimos 50 logs
            if len(status['logs']) > 50:
                status['logs'] = status['logs'][-50:]
        
        # Finalizar
        status['is_processing'] = False
        status['current_file'] = None
        status['progress'] = 100
        
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🎉 Processamento concluído! {len(status['processed_files'])} processados, {len(status['failed_files'])} falharam",
            'module': 'interface_melhorada'
        }
        status['logs'].append(log_entry)
        
    except Exception as e:
        status = st.session_state['processing_status']
        status['is_processing'] = False
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'ERROR',
            'message': f"Erro geral: {str(e)}",
            'module': 'interface_melhorada'
        }
        status['logs'].append(log_entry)

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

def main():
    """Interface principal melhorada"""
    
    # Título
    st.title("🤖 Sistema RAG Local - Interface Melhorada")
    st.markdown("**Sistema RAG 100% Open Source com IA Potente**")
    
    # Inicializar sistema RAG
    if st.session_state['rag_system'] is None:
        st.session_state['rag_system'] = SimpleRAGSystem(st.session_state['vector_db_path'])
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controles Principais")
        
        # Botão de processamento - SEMPRE VISÍVEL
        st.markdown("### 🚀 Processamento de Documentos")
        
        if st.button("🚀 PROCESSAR TODOS OS ARQUIVOS", type="primary", use_container_width=True):
            if not st.session_state['processing_status']['is_processing']:
                process_all_files_improved()
                st.rerun()
        
        # Botão para consulta RAG
        st.markdown("### ❓ Consulta RAG")
        question = st.text_area("Digite sua pergunta:", height=100)
        
        if st.button("🔍 FAZER CONSULTA", type="secondary", use_container_width=True):
            if question.strip():
                rag_system = st.session_state['rag_system']
                results = rag_system.query(question)
                
                if results:
                    st.success(f"✅ Encontradas {len(results)} respostas relevantes")
                    for i, result in enumerate(results[:3], 1):
                        st.write(f"**{i}.** Similaridade: {result['similarity']:.3f}")
                        st.write(f"**Texto:** {result['chunk_text'][:200]}...")
                        st.write("---")
                else:
                    st.warning("❌ Nenhuma resposta relevante encontrada")
        
        # Estatísticas
        st.markdown("### 📊 Estatísticas")
        stats = st.session_state['rag_system'].get_stats()
        
        st.metric("📄 Documentos", stats['documents'])
        st.metric("📝 Chunks", stats['chunks'])
        
        if stats['file_types']:
            st.write("**Tipos de arquivo:**")
            for file_type, count in stats['file_types']:
                st.write(f"• {file_type}: {count}")
        
        # Status do processamento
        status = st.session_state['processing_status']
        if status['is_processing']:
            st.info(f"🔄 Processando: {Path(status['current_file']).name if status['current_file'] else 'N/A'}")
            st.progress(status['progress'] / 100)
        elif status['processed_files']:
            st.success(f"✅ {len(status['processed_files'])} arquivos processados")
        else:
            st.warning("⏸️ Nenhum processamento em andamento")
    
    # Conteúdo principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Dashboard Principal")
        
        # Métricas principais
        stats = st.session_state['rag_system'].get_stats()
        
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            st.metric("📄 Documentos", stats['documents'])
        with col1_2:
            st.metric("📝 Chunks", stats['chunks'])
        with col1_3:
            st.metric("🔍 Consultas", "0")  # Placeholder
        
        # Status do processamento
        status = st.session_state['processing_status']
        if status['is_processing']:
            st.info(f"🔄 **Processando:** {Path(status['current_file']).name if status['current_file'] else 'N/A'}")
            st.progress(status['progress'] / 100)
        elif status['processed_files']:
            st.success(f"✅ **Processamento concluído:** {len(status['processed_files'])} arquivos processados")
        else:
            st.warning("⏸️ **Nenhum processamento em andamento**")
        
        # Lista de arquivos processados
        if status['processed_files']:
            st.subheader("📁 Arquivos Processados (Últimos 10)")
            for file_info in status['processed_files'][-10:]:
                st.write(f"📄 **{Path(file_info['file']).name}** - {file_info['size']} chars, {file_info['chunks']} chunks - {file_info['timestamp']}")
        
        # Arquivos com falha
        if status['failed_files']:
            st.subheader("❌ Arquivos com Falha (Últimos 5)")
            for file_info in status['failed_files'][-5:]:
                st.write(f"❌ **{Path(file_info['file']).name}** - {file_info['error']} - {file_info['timestamp']}")
    
    with col2:
        st.header("📝 Logs em Tempo Real")
        
        # Filtros
        log_level = st.selectbox("Filtrar logs:", ["TODOS", "INFO", "SUCCESS", "WARNING", "ERROR"])
        
        # Logs
        status = st.session_state['processing_status']
        if status['logs']:
            # Filtrar logs
            filtered_logs = status['logs']
            if log_level != "TODOS":
                filtered_logs = [log for log in status['logs'] if log['level'] == log_level]
            
            # Mostrar logs
            for log in filtered_logs[-15:]:  # Últimos 15
                level_emoji = {
                    'INFO': 'ℹ️',
                    'SUCCESS': '✅',
                    'WARNING': '⚠️',
                    'ERROR': '❌'
                }.get(log['level'], '📝')
                
                st.write(f"{level_emoji} **{log['timestamp']}** {log['message']}")
        else:
            st.info("Nenhum log disponível ainda")
        
        # Auto-refresh
        if status['is_processing']:
            time.sleep(2)
            st.rerun()
    
    # Informações do sistema
    st.markdown("---")
    st.subheader("🔧 Informações do Sistema")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.write("**🤖 Modelo de IA:**")
        st.write("• Sistema RAG Puro (100% Open Source)")
        st.write("• Busca por similaridade de palavras-chave")
        st.write("• Banco de dados: SQLite")
    
    with col4:
        st.write("**📁 Diretório:**")
        st.write(f"• `/home/lsantann/Documents/CC/`")
        st.write(f"• Banco: `{st.session_state['vector_db_path']}`")
        st.write("• Extensões: .txt, .md, .py, .js, .html, .css, .json")
    
    with col5:
        st.write("**⚡ Status:**")
        if status['is_processing']:
            st.write("🔄 Processando...")
        elif status['processed_files']:
            st.write("✅ Pronto para consultas")
        else:
            st.write("⏸️ Aguardando processamento")
    
    # Footer
    st.markdown("---")
    st.markdown("**🚀 Sistema RAG Local - 100% Open Source - Desenvolvido com ❤️**")

if __name__ == "__main__":
    main()
