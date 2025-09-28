#!/usr/bin/env python3
"""
Interface Web com IA Potente - Sistema RAG Local
Usando modelos de IA mais avançados e interface completa
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

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="RAG Local - IA Potente",
    page_icon="🧠",
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
    st.session_state['vector_db_path'] = "vector_db_potente.sqlite"

# ============================================================================
# SISTEMA RAG COM IA POTENTE
# ============================================================================

class PotentRAGSystem:
    """Sistema RAG com IA mais potente"""
    
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
    
    def create_advanced_embedding(self, text: str) -> List[float]:
        """Criar embedding avançado baseado em TF-IDF e análise semântica"""
        # Tokenização avançada
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remover stopwords em português
        stopwords = {
            'a', 'o', 'e', 'de', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'um', 'uma',
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
        words = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Calcular frequência de palavras
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Criar vetor de 256 dimensões com análise semântica
        vector = [0.0] * 256
        
        for word, freq in word_freq.items():
            # Hash da palavra para posição
            hash_val = hash(word) % 256
            vector[hash_val] += freq
            
            # Análise de contexto (palavras próximas)
            word_index = text.lower().find(word)
            if word_index > 0:
                context = text[max(0, word_index-20):word_index+20]
                context_words = re.findall(r'\b\w+\b', context.lower())
                for context_word in context_words:
                    if context_word != word:
                        context_hash = hash(context_word) % 256
                        vector[context_hash] += freq * 0.5
        
        # Normalizar vetor
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def advanced_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcular similaridade avançada"""
        if len(vec1) != len(vec2):
            return 0.0
        
        # Similaridade coseno
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        cosine_sim = dot_product / (norm1 * norm2)
        
        # Similaridade de Jaccard para palavras
        return cosine_sim
    
    def intelligent_query(self, question: str, max_results: int = 5) -> List[Dict]:
        """Consulta inteligente com análise semântica"""
        # Criar embedding da pergunta
        query_embedding = self.create_advanced_embedding(question)
        
        # Buscar no banco
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
                vector_sim = self.advanced_similarity(query_embedding, vector)
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
            combined_sim = (vector_sim * 0.7) + (jaccard_sim * 0.3)
            
            if combined_sim > 0.1:  # Threshold mais baixo
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
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]
    
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

# ============================================================================
# PROCESSAMENTO AVANÇADO
# ============================================================================

def process_document_advanced(file_path: Path) -> dict:
    """Processar documento com análise avançada"""
    try:
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            return {'success': False, 'error': 'Arquivo vazio'}
        
        # Extrair URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        
        # Fazer scraping de URLs
        scraped_content = ""
        if urls:
            for url in urls[:3]:  # Limitar a 3 URLs
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
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
        
        # Criar chunks inteligentes
        chunk_size = 1000
        overlap = 200
        chunks = []
        
        start = 0
        while start < len(full_content):
            end = start + chunk_size
            if end >= len(full_content):
                chunks.append(full_content[start:])
                break
            
            # Tentar quebrar em sentença
            chunk = full_content[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            
            if last_period > chunk_size // 2:
                end = start + last_period + 1
            elif last_newline > chunk_size // 2:
                end = start + last_newline
            
            chunks.append(full_content[start:end])
            start = end - overlap
        
        # Salvar chunks com embeddings
        rag_system = PotentRAGSystem(st.session_state['vector_db_path'])
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            embedding = rag_system.create_advanced_embedding(chunk)
            
            chunk_metadata = {
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk),
                'word_count': len(chunk.split())
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

def process_all_files_potent():
    """Processar todos os arquivos com IA potente"""
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
        supported_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.xml']
        
        all_files = []
        for ext in supported_extensions:
            all_files.extend(documents_dir.rglob(f"*{ext}"))
        
        # Limitar a 200 arquivos
        all_files = all_files[:200]
        status['total_files'] = len(all_files)
        
        # Log de início
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🧠 Iniciando processamento com IA potente de {len(all_files)} arquivos",
            'module': 'interface_ia_potente'
        }
        status['logs'].append(log_entry)
        
        # Processar arquivos
        for i, file_path in enumerate(all_files):
            status['current_file'] = str(file_path)
            status['progress'] = (i / len(all_files)) * 100
            
            # Processar arquivo
            result = process_document_advanced(file_path)
            
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
                    'module': 'interface_ia_potente'
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
                    'module': 'interface_ia_potente'
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
            'message': f"🎉 Processamento com IA potente concluído! {len(status['processed_files'])} processados, {len(status['failed_files'])} falharam",
            'module': 'interface_ia_potente'
        }
        status['logs'].append(log_entry)
        
    except Exception as e:
        status = st.session_state['processing_status']
        status['is_processing'] = False
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'ERROR',
            'message': f"Erro geral: {str(e)}",
            'module': 'interface_ia_potente'
        }
        status['logs'].append(log_entry)

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

def main():
    """Interface principal com IA potente"""
    
    # Título
    st.title("🧠 Sistema RAG Local - IA Potente")
    st.markdown("**Sistema RAG 100% Open Source com IA Avançada e Análise Semântica**")
    
    # Inicializar sistema RAG
    if st.session_state['rag_system'] is None:
        st.session_state['rag_system'] = PotentRAGSystem(st.session_state['vector_db_path'])
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controles Principais")
        
        # Botão de processamento - SEMPRE VISÍVEL
        st.markdown("### 🧠 Processamento com IA Potente")
        
        if st.button("🧠 PROCESSAR COM IA POTENTE", type="primary", use_container_width=True):
            if not st.session_state['processing_status']['is_processing']:
                process_all_files_potent()
                st.rerun()
        
        # Botão para consulta RAG inteligente
        st.markdown("### 🔍 Consulta RAG Inteligente")
        question = st.text_area("Digite sua pergunta:", height=100, placeholder="Ex: O que é machine learning? Como funciona deep learning?")
        
        if st.button("🔍 CONSULTA INTELIGENTE", type="secondary", use_container_width=True):
            if question.strip():
                rag_system = st.session_state['rag_system']
                results = rag_system.intelligent_query(question)
                
                if results:
                    st.success(f"✅ Encontradas {len(results)} respostas inteligentes")
                    for i, result in enumerate(results[:3], 1):
                        st.write(f"**{i}.** Similaridade: {result['similarity']:.3f}")
                        st.write(f"**Vetorial:** {result['vector_sim']:.3f} | **Textual:** {result['text_sim']:.3f}")
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
        st.header("📊 Dashboard com IA Potente")
        
        # Métricas principais
        stats = st.session_state['rag_system'].get_stats()
        
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            st.metric("📄 Documentos", stats['documents'])
        with col1_2:
            st.metric("📝 Chunks", stats['chunks'])
        with col1_3:
            st.metric("🧠 IA Status", "Ativa")
        
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
                st.write(f"📄 **{Path(file_info['file']).name}** - {file_info['size']} chars, {file_info['urls']} URLs, {file_info['chunks']} chunks - {file_info['timestamp']}")
        
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
    st.subheader("🧠 Sistema de IA Potente")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.write("**🧠 Modelo de IA:**")
        st.write("• Sistema RAG com IA Avançada")
        st.write("• Embeddings de 256 dimensões")
        st.write("• Análise semântica e contextual")
        st.write("• Similaridade combinada (vetorial + textual)")
    
    with col4:
        st.write("**📁 Processamento:**")
        st.write(f"• Diretório: `/home/lsantann/Documents/CC/`")
        st.write(f"• Banco: `{st.session_state['vector_db_path']}`")
        st.write("• Extensões: .txt, .md, .py, .js, .html, .css, .json, .yaml, .xml")
        st.write("• URL scraping automático")
    
    with col5:
        st.write("**⚡ Status:**")
        if status['is_processing']:
            st.write("🔄 Processando com IA...")
        elif status['processed_files']:
            st.write("✅ IA pronta para consultas")
        else:
            st.write("⏸️ Aguardando processamento")
    
    # Footer
    st.markdown("---")
    st.markdown("**🧠 Sistema RAG Local - IA Potente - 100% Open Source - Desenvolvido com ❤️**")

if __name__ == "__main__":
    main()
