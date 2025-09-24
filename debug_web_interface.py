#!/usr/bin/env python3
"""
Interface Web com Debug e Progresso em Tempo Real
Sistema RAG Local - Versão com Debug Avançado
"""

import streamlit as st
import os
import sys
import time
import threading
import queue
import logging
from pathlib import Path
from datetime import datetime
import json

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos do sistema
try:
    import config
    from enhanced_document_processor import EnhancedDocumentProcessor
    from embedding_system import EmbeddingSystem
    from rag_agent import RAGAgent
    from markdown_generator import MarkdownGenerator
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configurar página
st.set_page_config(
    page_title="RAG Local - Debug Interface",
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

if 'processor' not in st.session_state:
    st.session_state['processor'] = None

if 'log_queue' not in st.session_state:
    st.session_state['log_queue'] = queue.Queue()

class DebugLogHandler(logging.Handler):
    """Handler personalizado para capturar logs"""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        }
        self.log_queue.put(log_entry)

def setup_logging():
    """Configurar logging com handler personalizado"""
    # Limpar handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Adicionar handler personalizado
    debug_handler = DebugLogHandler(st.session_state['log_queue'])
    debug_handler.setLevel(logging.INFO)
    logging.root.addHandler(debug_handler)

def get_processing_stats():
    """Obter estatísticas de processamento"""
    status = st.session_state['processing_status']
    
    # Contar arquivos no diretório
    documents_dir = Path(config.DOCUMENTS_DIR)
    if documents_dir.exists():
        all_files = []
        for ext in config.SUPPORTED_EXTENSIONS.values():
            for extension in ext:
                all_files.extend(documents_dir.rglob(f"*{extension}"))
        total_files = len(all_files)
    else:
        total_files = 0
    
    processed_count = len(status['processed_files'])
    failed_count = len(status['failed_files'])
    progress = (processed_count / total_files * 100) if total_files > 0 else 0
    
    return {
        'total_files': total_files,
        'processed_files': processed_count,
        'failed_files': failed_count,
        'progress_percent': progress,
        'is_processing': status['is_processing'],
        'current_file': status['current_file'],
        'start_time': status['start_time']
    }

def process_documents_with_debug():
    """Processar documentos com debug detalhado"""
    try:
        # Inicializar processador se necessário
        if st.session_state['processor'] is None:
            st.session_state['processor'] = EnhancedDocumentProcessor()
        
        processor = st.session_state['processor']
        status = st.session_state['processing_status']
        
        # Resetar status
        status['is_processing'] = True
        status['processed_files'] = []
        status['failed_files'] = []
        status['logs'] = []
        status['start_time'] = datetime.now()
        
        # Obter lista de arquivos
        documents_dir = Path(config.DOCUMENTS_DIR)
        all_files = []
        for ext in config.SUPPORTED_EXTENSIONS.values():
            for extension in ext:
                all_files.extend(documents_dir.rglob(f"*{extension}"))
        
        status['total_files'] = len(all_files)
        
        # Processar cada arquivo
        for i, file_path in enumerate(all_files):
            try:
                status['current_file'] = str(file_path)
                status['progress'] = (i / len(all_files)) * 100
                
                # Log de início do processamento
                log_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'INFO',
                    'message': f"Processando arquivo {i+1}/{len(all_files)}: {file_path.name}",
                    'module': 'debug_interface'
                }
                status['logs'].append(log_entry)
                
                # Processar arquivo
                result = processor.process_document_with_urls(file_path)
                
                if result and result.get('text'):
                    status['processed_files'].append({
                        'file': str(file_path),
                        'size': len(result.get('text', '')),
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    log_entry = {
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'level': 'SUCCESS',
                        'message': f"✅ Processado com sucesso: {file_path.name} ({len(result.get('text', ''))} caracteres)",
                        'module': 'debug_interface'
                    }
                else:
                    status['failed_files'].append({
                        'file': str(file_path),
                        'error': 'Nenhum conteúdo extraído',
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    log_entry = {
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'level': 'WARNING',
                        'message': f"⚠️ Falha no processamento: {file_path.name}",
                        'module': 'debug_interface'
                    }
                
                status['logs'].append(log_entry)
                
                # Manter apenas os últimos 50 logs
                if len(status['logs']) > 50:
                    status['logs'] = status['logs'][-50:]
                
            except Exception as e:
                error_msg = f"Erro ao processar {file_path.name}: {str(e)}"
                status['failed_files'].append({
                    'file': str(file_path),
                    'error': str(e),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                
                log_entry = {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'ERROR',
                    'message': error_msg,
                    'module': 'debug_interface'
                }
                status['logs'].append(log_entry)
        
        # Finalizar processamento
        status['is_processing'] = False
        status['current_file'] = None
        status['progress'] = 100
        
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🎉 Processamento concluído! {len(status['processed_files'])} arquivos processados, {len(status['failed_files'])} falharam",
            'module': 'debug_interface'
        }
        status['logs'].append(log_entry)
        
    except Exception as e:
        status['is_processing'] = False
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'ERROR',
            'message': f"Erro geral no processamento: {str(e)}",
            'module': 'debug_interface'
        }
        status['logs'].append(log_entry)

def main():
    """Função principal da interface"""
    
    # Título
    st.title("🤖 Sistema RAG Local - Interface de Debug")
    st.markdown("**Interface com monitoramento em tempo real e logs detalhados**")
    
    # Configurar logging
    setup_logging()
    
    # Sidebar com controles
    with st.sidebar:
        st.header("🎛️ Controles")
        
        # Botão para iniciar processamento
        if st.button("🚀 Iniciar Processamento com Debug", type="primary"):
            if not st.session_state['processing_status']['is_processing']:
                # Executar em thread separada
                thread = threading.Thread(target=process_documents_with_debug)
                thread.daemon = True
                thread.start()
                st.rerun()
        
        # Botão para parar processamento
        if st.button("⏹️ Parar Processamento"):
            st.session_state['processing_status']['is_processing'] = False
            st.rerun()
        
        # Botão para limpar logs
        if st.button("🗑️ Limpar Logs"):
            st.session_state['processing_status']['logs'] = []
            st.rerun()
        
        # Estatísticas
        st.header("📊 Estatísticas")
        stats = get_processing_stats()
        
        st.metric("Total de Arquivos", stats['total_files'])
        st.metric("Processados", stats['processed_files'])
        st.metric("Falharam", stats['failed_files'])
        st.metric("Progresso", f"{stats['progress_percent']:.1f}%")
        
        if stats['start_time']:
            elapsed = datetime.now() - stats['start_time']
            st.metric("Tempo Decorrido", f"{elapsed.seconds}s")
    
    # Conteúdo principal
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📁 Arquivos", "📝 Logs", "⚙️ Configuração"])
    
    with tab1:
        st.header("📊 Dashboard de Processamento")
        
        stats = get_processing_stats()
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Arquivos", stats['total_files'])
        
        with col2:
            st.metric("Processados", stats['processed_files'])
        
        with col3:
            st.metric("Falharam", stats['failed_files'])
        
        with col4:
            st.metric("Progresso", f"{stats['progress_percent']:.1f}%")
        
        # Barra de progresso
        if stats['progress_percent'] > 0:
            st.progress(stats['progress_percent'] / 100)
        
        # Status atual
        if stats['is_processing']:
            st.info(f"🔄 Processando: {stats['current_file']}")
        elif stats['processed_files'] > 0:
            st.success("✅ Processamento concluído!")
        else:
            st.warning("⏸️ Nenhum processamento em andamento")
    
    with tab2:
        st.header("📁 Arquivos em Processamento")
        
        status = st.session_state['processing_status']
        
        # Arquivo atual
        if status['current_file']:
            st.subheader("🔄 Arquivo Atual")
            st.code(status['current_file'])
        
        # Arquivos processados
        if status['processed_files']:
            st.subheader("✅ Arquivos Processados")
            for file_info in status['processed_files'][-10:]:  # Mostrar últimos 10
                st.write(f"📄 {Path(file_info['file']).name} ({file_info['size']} chars) - {file_info['timestamp']}")
        
        # Arquivos com falha
        if status['failed_files']:
            st.subheader("❌ Arquivos com Falha")
            for file_info in status['failed_files'][-10:]:  # Mostrar últimos 10
                st.write(f"❌ {Path(file_info['file']).name} - {file_info['error']} - {file_info['timestamp']}")
    
    with tab3:
        st.header("📝 Logs de Debug")
        
        status = st.session_state['processing_status']
        
        # Filtros de log
        col1, col2 = st.columns(2)
        with col1:
            log_level = st.selectbox("Filtrar por nível:", ["TODOS", "INFO", "SUCCESS", "WARNING", "ERROR"])
        with col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        
        # Logs
        if status['logs']:
            # Filtrar logs
            filtered_logs = status['logs']
            if log_level != "TODOS":
                filtered_logs = [log for log in status['logs'] if log['level'] == log_level]
            
            # Mostrar logs
            for log in filtered_logs[-20:]:  # Mostrar últimos 20
                level_emoji = {
                    'INFO': 'ℹ️',
                    'SUCCESS': '✅',
                    'WARNING': '⚠️',
                    'ERROR': '❌'
                }.get(log['level'], '📝')
                
                st.write(f"{level_emoji} **{log['timestamp']}** [{log['level']}] {log['message']}")
        else:
            st.info("Nenhum log disponível ainda")
        
        # Auto-refresh
        if auto_refresh and status['is_processing']:
            time.sleep(1)
            st.rerun()
    
    with tab4:
        st.header("⚙️ Configuração")
        
        # Informações do sistema
        st.subheader("📁 Diretórios")
        st.code(f"""
Diretório de Documentos: {config.DOCUMENTS_DIR}
Diretório RAG: {config.RAGFILES_DIR}
Banco de Dados: {config.VECTOR_DB_DIR}
        """)
        
        # Extensões suportadas
        st.subheader("📄 Extensões Suportadas")
        for category, extensions in config.SUPPORTED_EXTENSIONS.items():
            st.write(f"**{category.title()}:** {', '.join(extensions)}")
        
        # Status dos módulos
        st.subheader("🔧 Status dos Módulos")
        modules_status = {
            'EnhancedDocumentProcessor': st.session_state['processor'] is not None,
            'EmbeddingSystem': True,  # Será verificado quando necessário
            'RAGAgent': True,  # Será verificado quando necessário
        }
        
        for module, status in modules_status.items():
            status_emoji = "✅" if status else "❌"
            st.write(f"{status_emoji} {module}")
    
    # Footer
    st.markdown("---")
    st.markdown("**Desenvolvido com ❤️ para a comunidade brasileira**")

if __name__ == "__main__":
    main()
