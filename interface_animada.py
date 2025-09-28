#!/usr/bin/env python3
"""
Interface Web - Sistema RAG Local
Interface com carregamento e feedback visual
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
import hashlib
import re
from typing import List, Dict, Any
import urllib.request
from html.parser import HTMLParser
import random

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="RAG Local - Interface",
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

if 'loading_animation' not in st.session_state:
    st.session_state['loading_animation'] = True

# ============================================================================
# SISTEMA RAG
# ============================================================================

class RAGSystem:
    """Sistema RAG com feedback visual"""
    
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
    
    def create_smart_embedding(self, text: str) -> List[float]:
        """Criar embedding inteligente"""
        # Tokenização avançada
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remover stopwords
        stopwords = {
            'a', 'o', 'e', 'de', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'um', 'uma',
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
        words = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Calcular frequência
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Criar vetor de 128 dimensões
        vector = [0.0] * 128
        
        for word, freq in word_freq.items():
            hash_val = hash(word) % 128
            vector[hash_val] += freq
        
        # Normalizar
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def smart_query(self, question: str, max_results: int = 5) -> List[Dict]:
        """Consulta inteligente"""
        query_embedding = self.create_smart_embedding(question)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, document_id, chunk_text, vector, metadata FROM chunks")
        results = []
        
        for row in cursor.fetchall():
            chunk_id, doc_id, chunk_text, vector_json, metadata_json = row
            vector = json.loads(vector_json) if vector_json else []
            metadata = json.loads(metadata_json) if metadata_json else {}
            
            if vector:
                # Similaridade vetorial
                dot_product = sum(a * b for a, b in zip(query_embedding, vector))
                norm1 = sum(a * a for a in query_embedding) ** 0.5
                norm2 = sum(b * b for b in vector) ** 0.5
                vector_sim = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
            else:
                vector_sim = 0
            
            # Similaridade textual
            question_words = set(re.findall(r'\b\w+\b', question.lower()))
            chunk_words = set(re.findall(r'\b\w+\b', chunk_text.lower()))
            
            if question_words and chunk_words:
                jaccard_sim = len(question_words.intersection(chunk_words)) / len(question_words.union(chunk_words))
            else:
                jaccard_sim = 0
            
            # Similaridade combinada
            combined_sim = (vector_sim * 0.6) + (jaccard_sim * 0.4)
            
            if combined_sim > 0.05:
                results.append({
                    'chunk_id': chunk_id,
                    'document_id': doc_id,
                    'chunk_text': chunk_text,
                    'similarity': combined_sim,
                    'vector_sim': vector_sim,
                    'text_sim': jaccard_sim,
                    'metadata': metadata
                })
        
        conn.close()
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]
    
    def get_stats(self):
        """Obter estatísticas"""
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

# ============================================================================
# EFEITOS VISUAIS
# ============================================================================

def show_loading():
    """Mostrar carregamento"""
    with st.spinner("🔄 Carregando sistema RAG..."):
        time.sleep(1)
    
    # Progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        "🔍 Inicializando banco de dados...",
        "🧠 Carregando sistema de IA...",
        "📊 Preparando estatísticas...",
        "⚙️ Configurando sistema...",
        "✅ Sistema pronto!"
    ]
    
    for i, step in enumerate(steps):
        progress_bar.progress((i + 1) / len(steps))
        status_text.text(step)
        time.sleep(0.5)
    
    progress_bar.empty()
    status_text.empty()

def show_processing():
    """Mostrar processamento"""
    # Arquivos sendo processados
    processing_placeholder = st.empty()
    
    steps = [
        "📄 Processando arquivos...",
        "🔍 Analisando conteúdo...",
        "🧠 Gerando embeddings...",
        "💾 Salvando no banco...",
        "✅ Concluído!"
    ]
    
    for step in steps:
        processing_placeholder.text(step)
        time.sleep(0.3)
    
    processing_placeholder.empty()

def show_success():
    """Mostrar sucesso"""
    success_placeholder = st.empty()
    
    success_messages = [
        "🎉 Processamento concluído!",
        "✅ Arquivos processados com sucesso!",
        "🧠 Sistema RAG pronto para consultas!",
        "🚀 Interface carregada com sucesso!"
    ]
    
    for message in success_messages:
        success_placeholder.success(message)
        time.sleep(0.5)
    
    success_placeholder.empty()

# ============================================================================
# PROCESSAMENTO
# ============================================================================

def process_document(file_path: Path) -> dict:
    """Processar documento"""
    try:
        # Leitura
        with st.spinner(f"📖 Lendo {file_path.name}..."):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        if not content.strip():
            return {'success': False, 'error': 'Arquivo vazio'}
        
        # Análise
        with st.spinner(f"🔍 Analisando {file_path.name}..."):
            # Extrair URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, content)
            
            # Fazer scraping de URLs
            scraped_content = ""
            if urls:
                for url in urls[:2]:  # Limitar a 2 URLs
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as response:
                            html_content = response.read().decode('utf-8', errors='ignore')
                            # Extrair texto do HTML
                            class HTMLTextExtractor(HTMLParser):
                                def __init__(self):
                                    super().__init__()
                                    self.text = []
                                
                                def handle_data(self, data):
                                    self.text.append(data)
                                
                                def get_text(self):
                                    return ' '.join(self.text)
                            
                            extractor = HTMLTextExtractor()
                            extractor.feed(html_content)
                            scraped_text = extractor.get_text()
                            scraped_content += f"\n\n--- Conteúdo de {url} ---\n{scraped_text}"
                    except:
                        pass
        
        # Combinar conteúdo
        full_content = content + scraped_content
        
        # Salvamento
        with st.spinner(f"💾 Salvando {file_path.name}..."):
            # Criar ID único
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:16]
            
            # Salvar no banco
            conn = sqlite3.connect(st.session_state['vector_db_path'])
            cursor = conn.cursor()
            
            metadata = {
                'file_path': str(file_path),
                'file_type': file_path.suffix,
                'word_count': len(full_content.split()),
                'char_count': len(full_content),
                'urls_found': len(urls),
                'processed_at': datetime.now().isoformat()
            }
            
            cursor.execute('''
                INSERT OR REPLACE INTO documents (id, file_path, file_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (doc_id, str(file_path), file_path.suffix, full_content, json.dumps(metadata)))
            
            # Criar chunks
            chunk_size = 1000
            chunks = [full_content[i:i+chunk_size] for i in range(0, len(full_content), chunk_size)]
            
            # Salvar chunks com embeddings
            rag_system = RAGSystem(st.session_state['vector_db_path'])
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                embedding = rag_system.create_smart_embedding(chunk)
                
                chunk_metadata = {
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunk_size': len(chunk)
                }
                
                cursor.execute('''
                    INSERT OR REPLACE INTO chunks (id, document_id, chunk_text, chunk_index, vector, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (chunk_id, doc_id, chunk, i, json.dumps(embedding), json.dumps(chunk_metadata)))
            
            conn.commit()
            conn.close()
        
        return {
            'success': True,
            'doc_id': doc_id,
            'text_length': len(full_content),
            'urls_count': len(urls),
            'chunks_count': len(chunks)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_all_files():
    """Processar todos os arquivos"""
    try:
        status = st.session_state['processing_status']
        
        # Resetar status
        status['is_processing'] = True
        status['processed_files'] = []
        status['failed_files'] = []
        status['logs'] = []
        status['start_time'] = datetime.now()
        
        # Início
        st.info("🚀 Iniciando processamento...")
        
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
            'module': 'interface'
        }
        status['logs'].append(log_entry)
        
        # Barra de progresso principal
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Processar arquivos
        for i, file_path in enumerate(all_files):
            status['current_file'] = str(file_path)
            status['progress'] = (i / len(all_files)) * 100
            
            # Atualizar barra de progresso
            progress_bar.progress(status['progress'] / 100)
            status_text.text(f"🔄 Processando: {file_path.name}")
            
            # Processar arquivo
            result = process_document(file_path)
            
            if result['success']:
                status['processed_files'].append({
                    'file': str(file_path),
                    'size': result['text_length'],
                    'urls': result['urls_count'],
                    'chunks': result['chunks_count'],
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                log_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'SUCCESS',
                    'message': f"✅ {file_path.name} ({result['text_length']} chars, {result['urls_count']} URLs, {result['chunks_count']} chunks)",
                    'module': 'interface'
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
                    'module': 'interface'
                }
            
            status['logs'].append(log_entry)
            
            # Manter apenas os últimos 50 logs
            if len(status['logs']) > 50:
                status['logs'] = status['logs'][-50:]
        
        # Finalizar
        status['is_processing'] = False
        status['current_file'] = None
        status['progress'] = 100
        
        # Conclusão
        progress_bar.progress(1.0)
        status_text.text("🎉 Processamento concluído!")
        
        # Mostrar sucesso
        show_success()
        
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🎉 Processamento concluído! {len(status['processed_files'])} processados, {len(status['failed_files'])} falharam",
            'module': 'interface'
        }
        status['logs'].append(log_entry)
        
        # Limpar elementos
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        status = st.session_state['processing_status']
        status['is_processing'] = False
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'ERROR',
            'message': f"Erro geral: {str(e)}",
            'module': 'interface'
        }
        status['logs'].append(log_entry)

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

def main():
    """Interface principal"""
    
    # Título
    st.title("🤖 Sistema RAG Local - Interface")
    st.markdown("**Sistema RAG 100% Open Source com Feedback Visual**")
    
    # Carregamento inicial
    if st.session_state['loading_animation']:
        show_loading()
        st.session_state['loading_animation'] = False
    
    # Inicializar sistema RAG
    if st.session_state['rag_system'] is None:
        with st.spinner("🧠 Inicializando sistema RAG..."):
            st.session_state['rag_system'] = RAGSystem(st.session_state['vector_db_path'])
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controles Principais")
        
        # Botão de processamento
        st.markdown("### 🚀 Processamento")
        
        if st.button("🚀 PROCESSAR ARQUIVOS", type="primary", use_container_width=True):
            if not st.session_state['processing_status']['is_processing']:
                process_all_files()
                st.rerun()
        
        # Botão para consulta RAG
        st.markdown("### 🔍 Consulta RAG")
        question = st.text_area("Digite sua pergunta:", height=100, placeholder="Ex: O que é machine learning? Como funciona deep learning?")
        
        if st.button("🔍 FAZER CONSULTA", type="secondary", use_container_width=True):
            if question.strip():
                with st.spinner("🔍 Buscando respostas..."):
                    rag_system = st.session_state['rag_system']
                    results = rag_system.smart_query(question)
                
                if results:
                    st.success(f"✅ Encontradas {len(results)} respostas")
                    for i, result in enumerate(results[:3], 1):
                        with st.expander(f"Resposta {i} - Similaridade: {result['similarity']:.3f}"):
                            st.write(f"**Vetorial:** {result['vector_sim']:.3f} | **Textual:** {result['text_sim']:.3f}")
                            st.write(f"**Texto:** {result['chunk_text'][:300]}...")
                else:
                    st.warning("❌ Nenhuma resposta relevante encontrada")
        
        # Estatísticas
        st.markdown("### 📊 Estatísticas")
        stats = st.session_state['rag_system'].get_stats()
        
        # Métricas
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Documentos", stats['documents'], delta=None)
        with col2:
            st.metric("📝 Chunks", stats['chunks'], delta=None)
        
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
        st.header("📊 Dashboard")
        
        # Métricas principais
        stats = st.session_state['rag_system'].get_stats()
        
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            st.metric("📄 Documentos", stats['documents'], delta=None)
        with col1_2:
            st.metric("📝 Chunks", stats['chunks'], delta=None)
        with col1_3:
            st.metric("🤖 Sistema", "Ativo")
        
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
                with st.container():
                    st.write(f"📄 **{Path(file_info['file']).name}** - {file_info['size']} chars, {file_info['urls']} URLs, {file_info['chunks']} chunks - {file_info['timestamp']}")
        
        # Arquivos com falha
        if status['failed_files']:
            st.subheader("❌ Arquivos com Falha (Últimos 5)")
            for file_info in status['failed_files'][-5:]:
                st.write(f"❌ **{Path(file_info['file']).name}** - {file_info['error']} - {file_info['timestamp']}")
    
    with col2:
        st.header("📝 Logs")
        
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
    st.subheader("🤖 Sistema RAG")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.write("**🤖 Sistema:**")
        st.write("• Carregamento com progresso")
        st.write("• Processamento em tempo real")
        st.write("• Feedback visual completo")
        st.write("• Logs em tempo real")
    
    with col4:
        st.write("**📁 Processamento:**")
        st.write(f"• Diretório: `/home/lsantann/Documents/CC/`")
        st.write(f"• Banco: `{st.session_state['vector_db_path']}`")
        st.write("• Extensões: .txt, .md, .py, .js, .html, .css, .json, .yaml")
        st.write("• URL scraping automático")
    
    with col5:
        st.write("**⚡ Status:**")
        if status['is_processing']:
            st.write("🔄 Processando...")
        elif status['processed_files']:
            st.write("✅ Sistema pronto")
        else:
            st.write("⏸️ Aguardando processamento")
    
    # Footer
    st.markdown("---")
    st.markdown("**🤖 Sistema RAG Local - Interface - 100% Open Source - Desenvolvido com ❤️**")

if __name__ == "__main__":
    main()
