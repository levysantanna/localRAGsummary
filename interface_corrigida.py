#!/usr/bin/env python3
"""
Interface Web Corrigida - Sistema RAG Local
Interface com configuração de diretório, listagem de arquivos e resultados úteis
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
    page_title="RAG Local - Interface Corrigida",
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

if 'documents_dir' not in st.session_state:
    st.session_state['documents_dir'] = "/home/lsantann/Documents/CC/"

if 'selected_files' not in st.session_state:
    st.session_state['selected_files'] = []

# ============================================================================
# SISTEMA RAG CORRIGIDO
# ============================================================================

class RAGSystem:
    """Sistema RAG corrigido com melhor qualidade de resultados"""
    
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
    
    def create_embedding(self, text: str) -> List[float]:
        """Criar embedding melhorado"""
        # Tokenização e limpeza
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remover stopwords
        stopwords = {
            'a', 'o', 'e', 'de', 'do', 'da', 'em', 'para', 'com', 'por', 'que', 'um', 'uma',
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'é', 'são', 'foi', 'ser', 'ter', 'estar', 'ter', 'fazer', 'poder', 'querer'
        }
        words = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Calcular frequência
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Criar vetor de 256 dimensões
        vector = [0.0] * 256
        
        for word, freq in word_freq.items():
            hash_val = hash(word) % 256
            vector[hash_val] += freq
        
        # Normalizar
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def query(self, question: str, max_results: int = 5) -> List[Dict]:
        """Consulta melhorada com resultados úteis"""
        query_embedding = self.create_embedding(question)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar chunks com informações do documento
        cursor.execute("""
            SELECT c.id, c.document_id, c.chunk_text, c.vector, c.metadata, d.file_path, d.file_type
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
        """)
        results = []
        
        for row in cursor.fetchall():
            chunk_id, doc_id, chunk_text, vector_json, metadata_json, file_path, file_type = row
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
            
            # Similaridade textual melhorada
            question_words = set(re.findall(r'\b\w+\b', question.lower()))
            chunk_words = set(re.findall(r'\b\w+\b', chunk_text.lower()))
            
            if question_words and chunk_words:
                jaccard_sim = len(question_words.intersection(chunk_words)) / len(question_words.union(chunk_words))
            else:
                jaccard_sim = 0
            
            # Similaridade combinada
            combined_sim = (vector_sim * 0.6) + (jaccard_sim * 0.4)
            
            if combined_sim > 0.05:  # Threshold mais baixo
                results.append({
                    'chunk_id': chunk_id,
                    'document_id': doc_id,
                    'chunk_text': chunk_text,
                    'similarity': combined_sim,
                    'vector_sim': vector_sim,
                    'text_sim': jaccard_sim,
                    'metadata': metadata,
                    'file_path': file_path,
                    'file_type': file_type
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
        
        cursor.execute("SELECT file_path, file_type, COUNT(*) FROM documents GROUP BY file_path, file_type")
        file_info = cursor.fetchall()
        
        conn.close()
        
        return {
            'documents': doc_count,
            'chunks': chunk_count,
            'file_info': file_info
        }
    
    def generate_summary(self, question: str, results: List[Dict]) -> str:
        """Gerar resumo em markdown dos resultados"""
        if not results:
            return "Nenhum resultado encontrado."
        
        summary = f"# Resumo da Consulta: {question}\n\n"
        summary += f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        summary += f"**Total de resultados:** {len(results)}\n\n"
        
        for i, result in enumerate(results, 1):
            file_name = Path(result['file_path']).name
            summary += f"## Resultado {i}\n\n"
            summary += f"**Arquivo:** {file_name}\n"
            summary += f"**Tipo:** {result['file_type']}\n"
            summary += f"**Similaridade:** {result['similarity']:.3f}\n"
            summary += f"**Vetorial:** {result['vector_sim']:.3f} | **Textual:** {result['text_sim']:.3f}\n\n"
            summary += f"**Conteúdo:**\n```\n{result['chunk_text'][:500]}...\n```\n\n"
            summary += "---\n\n"
        
        return summary
    
    def save_summary(self, question: str, results: List[Dict]) -> str:
        """Salvar resumo em arquivo markdown"""
        summary = self.generate_summary(question, results)
        
        # Criar diretório de resumos
        summaries_dir = Path("summaries")
        summaries_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo baseado na pergunta
        safe_question = re.sub(r'[^\w\s-]', '', question).strip()
        safe_question = re.sub(r'[-\s]+', '-', safe_question)
        filename = f"resumo_{safe_question[:50]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = summaries_dir / filename
        
        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return str(file_path)

# ============================================================================
# PROCESSAMENTO CORRIGIDO
# ============================================================================

def get_available_files(directory: str) -> List[Path]:
    """Obter arquivos disponíveis no diretório"""
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    # Todas as extensões suportadas
    supported_extensions = [
        # Texto
        '.txt', '.md', '.rst',
        # PDF
        '.pdf',
        # Imagens
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
        # Documentos
        '.docx', '.doc', '.pptx', '.ppt',
        # ODF
        '.odt', '.ods', '.odp',
        # Código
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.pl', '.sh', '.sql', '.html', '.css', '.xml', '.json', '.yaml', '.yml'
    ]
    
    all_files = []
    
    for ext in supported_extensions:
        all_files.extend(dir_path.rglob(f"*{ext}"))
    
    return all_files

def extract_content_from_file(file_path: Path) -> str:
    """Extrair conteúdo de diferentes tipos de arquivo"""
    try:
        file_ext = file_path.suffix.lower()
        
        # Arquivos de texto
        if file_ext in ['.txt', '.md', '.rst', '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.pl', '.sh', '.sql', '.html', '.css', '.xml', '.json', '.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        # PDF
        elif file_ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                return f"Arquivo PDF {file_path.name} - PyPDF2 não disponível"
            except Exception as e:
                return f"Erro ao processar PDF {file_path.name}: {str(e)}"
        
        # Imagens
        elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']:
            return f"Arquivo de imagem {file_path.name} - OCR não implementado ainda"
        
        # Documentos Word
        elif file_ext in ['.docx', '.doc']:
            try:
                import docx
                doc = docx.Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                return f"Arquivo Word {file_path.name} - python-docx não disponível"
            except Exception as e:
                return f"Erro ao processar Word {file_path.name}: {str(e)}"
        
        # PowerPoint
        elif file_ext in ['.pptx', '.ppt']:
            return f"Arquivo PowerPoint {file_path.name} - Processamento não implementado ainda"
        
        # ODF
        elif file_ext in ['.odt', '.ods', '.odp']:
            return f"Arquivo ODF {file_path.name} - Processamento não implementado ainda"
        
        # Fallback para outros tipos
        else:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                return f"Arquivo {file_path.name} - Tipo não suportado para extração de texto"
    
    except Exception as e:
        return f"Erro ao processar {file_path.name}: {str(e)}"

def process_document(file_path: Path) -> dict:
    """Processar documento"""
    try:
        with st.spinner(f"📖 Processando {file_path.name}..."):
            # Extrair conteúdo baseado no tipo de arquivo
            content = extract_content_from_file(file_path)
            
            if not content.strip():
                return {'success': False, 'error': 'Nenhum conteúdo extraído'}
            
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
            
            # Criar ID único
            doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:16]
            
            # Salvar no banco com timeout
            conn = sqlite3.connect(st.session_state['vector_db_path'], timeout=30.0)
            cursor = conn.cursor()
            
            # Configurar para WAL mode para evitar locks
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            
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
                embedding = rag_system.create_embedding(chunk)
                
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

def process_selected_files():
    """Processar arquivos selecionados"""
    try:
        status = st.session_state['processing_status']
        selected_files = st.session_state['selected_files']
        
        if not selected_files:
            st.error("❌ Nenhum arquivo selecionado!")
            return
        
        # Resetar status
        status['is_processing'] = True
        status['processed_files'] = []
        status['failed_files'] = []
        status['logs'] = []
        status['start_time'] = datetime.now()
        status['total_files'] = len(selected_files)
        
        # Log de início
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🚀 Iniciando processamento de {len(selected_files)} arquivos selecionados",
            'module': 'interface_corrigida'
        }
        status['logs'].append(log_entry)
        
        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Processar arquivos sequencialmente para evitar locks
        for i, file_path in enumerate(selected_files):
            status['current_file'] = str(file_path)
            status['progress'] = (i / len(selected_files)) * 100
            
            # Atualizar progresso
            progress_bar.progress(status['progress'] / 100)
            status_text.text(f"🔄 Processando: {file_path.name}")
            
            # Processar arquivo
            result = process_document(file_path)
            
            # Pequeno delay para evitar locks
            time.sleep(0.5)
            
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
                    'module': 'interface_corrigida'
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
                    'module': 'interface_corrigida'
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
        
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🎉 Processamento concluído! {len(status['processed_files'])} processados, {len(status['failed_files'])} falharam",
            'module': 'interface_corrigida'
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
            'module': 'interface_corrigida'
        }
        status['logs'].append(log_entry)

# ============================================================================
# INTERFACE PRINCIPAL CORRIGIDA
# ============================================================================

def main():
    """Interface principal corrigida"""
    
    # Título
    st.title("🤖 Sistema RAG Local - Interface Corrigida")
    st.markdown("**Sistema RAG 100% Open Source com Configuração e Resultados Úteis**")
    
    # Inicializar sistema RAG
    if st.session_state['rag_system'] is None:
        with st.spinner("🧠 Inicializando sistema RAG..."):
            st.session_state['rag_system'] = RAGSystem(st.session_state['vector_db_path'])
    
    # Sidebar com configuração
    with st.sidebar:
        st.header("🎛️ Configuração")
        
        # Configuração do diretório
        st.subheader("📁 Diretório de Documentos")
        current_dir = st.text_input(
            "Diretório dos documentos:", 
            value=st.session_state['documents_dir'],
            help="Caminho para o diretório com os arquivos a serem processados"
        )
        
        if st.button("🔄 Atualizar Diretório"):
            st.session_state['documents_dir'] = current_dir
            st.success(f"Diretório atualizado para: {current_dir}")
            st.rerun()
        
        # Listar arquivos disponíveis
        st.subheader("📄 Arquivos Disponíveis")
        available_files = get_available_files(st.session_state['documents_dir'])
        
        if available_files:
            # Agrupar por tipo
            file_types = {}
            for file_path in available_files:
                ext = file_path.suffix.lower()
                if ext not in file_types:
                    file_types[ext] = []
                file_types[ext].append(file_path)
            
            # Mostrar estatísticas por tipo
            st.info(f"📊 Encontrados {len(available_files)} arquivos no diretório")
            
            # Mostrar tipos encontrados
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Tipos encontrados:**")
                for ext, files in sorted(file_types.items()):
                    st.write(f"• {ext}: {len(files)} arquivos")
            
            # Seleção de arquivos
            file_options = [f.name for f in available_files]
            selected_file_names = st.multiselect(
                "Selecionar arquivos para processar:",
                file_options,
                default=file_options[:10] if len(file_options) > 10 else file_options,
                help="Selecione os arquivos que deseja processar"
            )
            
            # Atualizar arquivos selecionados
            if selected_file_names:
                st.session_state['selected_files'] = [
                    f for f in available_files if f.name in selected_file_names
                ]
                st.success(f"✅ {len(st.session_state['selected_files'])} arquivos selecionados")
            else:
                st.session_state['selected_files'] = []
                st.warning("⚠️ Nenhum arquivo selecionado")
        else:
            st.error(f"❌ Nenhum arquivo encontrado em: {st.session_state['documents_dir']}")
            st.session_state['selected_files'] = []
        
        # Botão de processamento
        st.subheader("🚀 Processamento")
        if st.button("🚀 PROCESSAR ARQUIVOS SELECIONADOS", type="primary", use_container_width=True):
            if not st.session_state['processing_status']['is_processing']:
                process_selected_files()
                st.rerun()
        
        # Botão para consulta RAG
        st.subheader("🔍 Consulta RAG")
        question = st.text_area("Digite sua pergunta:", height=100, placeholder="Ex: O que é machine learning? Como funciona deep learning?")
        
        if st.button("🔍 FAZER CONSULTA", type="secondary", use_container_width=True):
            if question.strip():
                with st.spinner("🔍 Buscando respostas..."):
                    rag_system = st.session_state['rag_system']
                    results = rag_system.query(question)
                
                if results:
                    st.success(f"✅ Encontradas {len(results)} respostas")
                    
                    # Mostrar resultados melhorados
                    for i, result in enumerate(results[:3], 1):
                        with st.expander(f"Resposta {i} - Similaridade: {result['similarity']:.3f}"):
                            st.write(f"**Arquivo:** {Path(result['file_path']).name}")
                            st.write(f"**Tipo:** {result['file_type']}")
                            st.write(f"**Vetorial:** {result['vector_sim']:.3f} | **Textual:** {result['text_sim']:.3f}")
                            st.write(f"**Conteúdo:**")
                            st.text(result['chunk_text'][:800])
                    
                    # Gerar e salvar resumo
                    with st.spinner("📝 Gerando resumo..."):
                        try:
                            summary_path = rag_system.save_summary(question, results)
                            st.success(f"📄 Resumo salvo em: {summary_path}")
                            
                            # Mostrar resumo
                            with open(summary_path, 'r', encoding='utf-8') as f:
                                summary_content = f.read()
                            st.markdown("**Resumo gerado:**")
                            st.markdown(summary_content)
                        except Exception as e:
                            st.error(f"Erro ao gerar resumo: {str(e)}")
                            # Mostrar resumo básico mesmo com erro
                            summary_text = rag_system.generate_summary(question, results)
                            st.markdown("**Resumo básico:**")
                            st.markdown(summary_text)
                else:
                    st.warning("❌ Nenhuma resposta relevante encontrada")
        
        # Estatísticas
        st.subheader("📊 Estatísticas")
        stats = st.session_state['rag_system'].get_stats()
        
        st.metric("📄 Documentos", stats['documents'])
        st.metric("📝 Chunks", stats['chunks'])
        
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
            st.metric("📄 Documentos", stats['documents'])
        with col1_2:
            st.metric("📝 Chunks", stats['chunks'])
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
                st.write(f"📄 **{Path(file_info['file']).name}** - {file_info['size']} chars, {file_info['urls']} URLs, {file_info['chunks']} chunks - {file_info['timestamp']}")
        
        # Arquivos com falha
        if status['failed_files']:
            st.subheader("❌ Arquivos com Falha (Últimos 5)")
            for file_info in status['failed_files'][-5:]:
                st.write(f"❌ **{Path(file_info['file']).name}** - {file_info['error']} - {file_info['timestamp']}")
        
        # Informações do banco de dados
        st.subheader("💾 Banco de Dados")
        st.info(f"**Localização:** `{st.session_state['vector_db_path']}`")
        st.info(f"**Diretório processado:** `{st.session_state['documents_dir']}`")
        
        if stats['file_info']:
            st.write("**Arquivos no banco:**")
            for file_path, file_type, count in stats['file_info'][:10]:
                st.write(f"• {Path(file_path).name} ({file_type}) - {count} registros")
        
        # Resumos gerados
        st.subheader("📄 Resumos Gerados")
        summaries_dir = Path("summaries")
        if summaries_dir.exists():
            summary_files = list(summaries_dir.glob("*.md"))
            if summary_files:
                st.info(f"📊 {len(summary_files)} resumos encontrados")
                for summary_file in sorted(summary_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    st.write(f"📄 **{summary_file.name}**")
                    st.write(f"   Criado: {datetime.fromtimestamp(summary_file.stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S')}")
                    st.write(f"   Tamanho: {summary_file.stat().st_size} bytes")
            else:
                st.info("Nenhum resumo gerado ainda")
        else:
            st.info("Diretório de resumos não existe ainda")
    
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
        st.write("• Configuração de diretório")
        st.write("• Seleção de arquivos")
        st.write("• Processamento controlado")
        st.write("• Resultados úteis")
    
    with col4:
        st.write("**📁 Processamento:**")
        st.write(f"• Diretório: `{st.session_state['documents_dir']}`")
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
    st.markdown("**🤖 Sistema RAG Local - Interface Corrigida - 100% Open Source - Desenvolvido com ❤️**")

if __name__ == "__main__":
    main()
