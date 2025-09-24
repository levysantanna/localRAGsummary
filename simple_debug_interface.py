#!/usr/bin/env python3
"""
Interface Web Simples com Debug
Sistema RAG Local - Versão Simplificada
"""

import streamlit as st
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import json

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar módulos do sistema
try:
    import config
    from enhanced_document_processor import EnhancedDocumentProcessor
    from embedding_system import EmbeddingSystem
    from rag_agent import RAGAgent
    from markdown_generator import MarkdownGenerator
    print("✅ Módulos importados com sucesso")
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configurar página
st.set_page_config(
    page_title="RAG Local - Debug Simples",
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

def process_single_file(file_path):
    """Processar um único arquivo"""
    try:
        # Inicializar processador se necessário
        if st.session_state['processor'] is None:
            st.session_state['processor'] = EnhancedDocumentProcessor()
        
        processor = st.session_state['processor']
        status = st.session_state['processing_status']
        
        # Log de início
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"Processando: {file_path.name}",
            'module': 'debug_interface'
        }
        status['logs'].append(log_entry)
        
        # Processar arquivo
        result = processor.process_document_with_urls(file_path)
        
        if result and result.get('text'):
            # Sucesso
            status['processed_files'].append({
                'file': str(file_path),
                'size': len(result.get('text', '')),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            log_entry = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'level': 'SUCCESS',
                'message': f"✅ Processado: {file_path.name} ({len(result.get('text', ''))} chars)",
                'module': 'debug_interface'
            }
        else:
            # Falha
            status['failed_files'].append({
                'file': str(file_path),
                'error': 'Nenhum conteúdo extraído',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            log_entry = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'level': 'WARNING',
                'message': f"⚠️ Falha: {file_path.name}",
                'module': 'debug_interface'
            }
        
        status['logs'].append(log_entry)
        
        # Manter apenas os últimos 50 logs
        if len(status['logs']) > 50:
            status['logs'] = status['logs'][-50:]
        
        return result
        
    except Exception as e:
        status = st.session_state['processing_status']
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'ERROR',
            'message': f"❌ Erro: {file_path.name} - {str(e)}",
            'module': 'debug_interface'
        }
        status['logs'].append(log_entry)
        return None

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
        
        # Obter lista de arquivos
        documents_dir = Path(config.DOCUMENTS_DIR)
        all_files = []
        for ext in config.SUPPORTED_EXTENSIONS.values():
            for extension in ext:
                all_files.extend(documents_dir.rglob(f"*{extension}"))
        
        status['total_files'] = len(all_files)
        
        # Processar cada arquivo
        for i, file_path in enumerate(all_files):
            status['current_file'] = str(file_path)
            status['progress'] = (i / len(all_files)) * 100
            
            # Processar arquivo
            result = process_single_file(file_path)
            
            # Atualizar progresso
            status['progress'] = ((i + 1) / len(all_files)) * 100
        
        # Finalizar processamento
        status['is_processing'] = False
        status['current_file'] = None
        status['progress'] = 100
        
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'INFO',
            'message': f"🎉 Processamento concluído! {len(status['processed_files'])} processados, {len(status['failed_files'])} falharam",
            'module': 'debug_interface'
        }
        status['logs'].append(log_entry)
        
    except Exception as e:
        status = st.session_state['processing_status']
        status['is_processing'] = False
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': 'ERROR',
            'message': f"Erro geral: {str(e)}",
            'module': 'debug_interface'
        }
        status['logs'].append(log_entry)

def main():
    """Função principal da interface"""
    
    # Título
    st.title("🤖 Sistema RAG Local - Debug Simples")
    st.markdown("**Interface simplificada com monitoramento em tempo real**")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("🎛️ Controles")
        
        # Botão para iniciar processamento
        if st.button("🚀 Processar Todos os Arquivos", type="primary"):
            if not st.session_state['processing_status']['is_processing']:
                process_all_files()
                st.rerun()
        
        # Botão para processar arquivo específico
        st.subheader("📄 Processar Arquivo Específico")
        documents_dir = Path(config.DOCUMENTS_DIR)
        if documents_dir.exists():
            all_files = []
            for ext in config.SUPPORTED_EXTENSIONS.values():
                for extension in ext:
                    all_files.extend(documents_dir.rglob(f"*{extension}"))
            
            if all_files:
                selected_file = st.selectbox("Selecionar arquivo:", [f.name for f in all_files])
                if st.button("📄 Processar Arquivo Selecionado"):
                    file_path = next(f for f in all_files if f.name == selected_file)
                    process_single_file(file_path)
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
