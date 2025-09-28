#!/usr/bin/env python3
"""
Interface Web Simples para RAG Local
"""

import streamlit as st
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
    st.error(f"Erro ao importar módulos: {e}")
    st.stop()

# Configurar página
st.set_page_config(
    page_title="RAG Local - Interface Simples",
    page_icon="🤖",
    layout="wide"
)

# Estado da sessão
if 'processor' not in st.session_state:
    st.session_state['processor'] = None

if 'processing_status' not in st.session_state:
    st.session_state['processing_status'] = {
        'is_processing': False,
        'processed_files': [],
        'failed_files': [],
        'logs': []
    }

def list_files_in_directory(directory_path):
    """Listar arquivos suportados em um diretório"""
    if not directory_path or not Path(directory_path).exists():
        return []
    
    all_files = []
    for ext in config.SUPPORTED_EXTENSIONS.values():
        for extension in ext:
            all_files.extend(Path(directory_path).rglob(f"*{extension}"))
    
    return all_files

def process_single_file(file_path):
    """Processar um único arquivo"""
    try:
        # Inicializar processador se necessário
        if st.session_state['processor'] is None:
            st.session_state['processor'] = EnhancedDocumentProcessor()
        
        processor = st.session_state['processor']
        status = st.session_state['processing_status']
        
        # Log de início
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] Processando: {file_path.name}"
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
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Sucesso: {file_path.name} ({len(result.get('text', ''))} chars)"
        else:
            # Falha
            status['failed_files'].append({
                'file': str(file_path),
                'error': 'Nenhum conteúdo extraído',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Falha: {file_path.name}"
        
        status['logs'].append(log_entry)
        
        # Manter apenas os últimos 50 logs
        if len(status['logs']) > 50:
            status['logs'] = status['logs'][-50:]
        
        return result
        
    except Exception as e:
        status = st.session_state['processing_status']
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro: {file_path.name} - {str(e)}"
        status['logs'].append(log_entry)
        return None

def process_all_files(directory_path):
    """Processar todos os arquivos de um diretório"""
    try:
        status = st.session_state['processing_status']
        
        # Inicializar processador se necessário
        if st.session_state['processor'] is None:
            st.session_state['processor'] = EnhancedDocumentProcessor()
        
        # Resetar status
        status['is_processing'] = True
        status['processed_files'] = []
        status['failed_files'] = []
        status['logs'] = []
        
        # Obter lista de arquivos
        all_files = list_files_in_directory(directory_path)
        
        # Log de início
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Iniciando processamento de {len(all_files)} arquivos"
        status['logs'].append(log_entry)
        
        # Processar cada arquivo
        for i, file_path in enumerate(all_files):
            # Processar arquivo
            result = process_single_file(file_path)
            
            # Atualizar progresso
            progress = ((i + 1) / len(all_files)) * 100
            st.progress(progress / 100)
            st.write(f"Progresso: {i+1}/{len(all_files)} ({progress:.1f}%)")
        
        # Finalizar processamento
        status['is_processing'] = False
        
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Processamento concluído!"
        status['logs'].append(log_entry)
        
    except Exception as e:
        status = st.session_state['processing_status']
        status['is_processing'] = False
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro geral: {str(e)}"
        status['logs'].append(log_entry)

def main():
    """Função principal da interface"""
    
    # Título
    st.title("🤖 Sistema RAG Local - Interface Simples")
    st.markdown("**Interface simplificada para processamento de documentos**")
    
    # Layout em colunas
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("🎛️ Configuração")
        
        # Configuração do diretório
        st.subheader("📁 Diretório dos Arquivos")
        current_dir = st.text_input(
            "Diretório dos documentos:", 
            value="/home/lsantann/Documents/CC/",
            help="Caminho para o diretório com os arquivos a serem processados"
        )
        
        # Verificar se o diretório existe
        if current_dir and Path(current_dir).exists():
            st.success(f"✅ Diretório encontrado: {current_dir}")
            
            # Listar arquivos encontrados
            all_files = list_files_in_directory(current_dir)
            st.info(f"📊 Encontrados {len(all_files)} arquivos suportados")
            
            # Mostrar alguns arquivos como exemplo
            if all_files:
                st.subheader("📄 Arquivos Encontrados (primeiros 10)")
                for i, file_path in enumerate(all_files[:10]):
                    st.write(f"• {file_path.name}")
                if len(all_files) > 10:
                    st.write(f"... e mais {len(all_files) - 10} arquivos")
            
            # Botões de processamento
            st.subheader("🚀 Processamento")
            
            if st.button("🚀 Processar Todos os Arquivos", type="primary", disabled=st.session_state['processing_status']['is_processing']):
                if not st.session_state['processing_status']['is_processing']:
                    with st.spinner("Processando arquivos..."):
                        process_all_files(current_dir)
                    st.rerun()
            
            # Processar arquivo específico
            if all_files:
                st.subheader("📄 Processar Arquivo Específico")
                selected_file = st.selectbox("Selecionar arquivo:", [f.name for f in all_files])
                if st.button("📄 Processar Arquivo Selecionado"):
                    file_path = next(f for f in all_files if f.name == selected_file)
                    with st.spinner(f"Processando {file_path.name}..."):
                        process_single_file(file_path)
                    st.rerun()
        
        else:
            st.error(f"❌ Diretório não encontrado: {current_dir}")
            st.info("💡 Verifique se o caminho está correto")
        
        # Botão para limpar logs
        if st.button("🗑️ Limpar Logs"):
            st.session_state['processing_status']['logs'] = []
            st.rerun()
    
    with col2:
        st.header("📊 Status e Logs")
        
        status = st.session_state['processing_status']
        
        # Estatísticas
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Processados", len(status['processed_files']))
        with col_stats2:
            st.metric("Falharam", len(status['failed_files']))
        with col_stats3:
            st.metric("Total Logs", len(status['logs']))
        
        # Status de processamento
        if status['is_processing']:
            st.info("🔄 Processamento em andamento...")
        else:
            st.success("✅ Sistema pronto")
        
        # Logs
        st.subheader("📝 Logs de Processamento")
        if status['logs']:
            # Mostrar logs em ordem reversa (mais recentes primeiro)
            for log in reversed(status['logs'][-20:]):  # Últimos 20 logs
                if "✅" in log or "Sucesso" in log:
                    st.success(log)
                elif "❌" in log or "Erro" in log or "Falha" in log:
                    st.error(log)
                else:
                    st.info(log)
        else:
            st.info("Nenhum log ainda")
        
        # Arquivos processados
        if status['processed_files']:
            st.subheader("✅ Arquivos Processados com Sucesso")
            for file_info in status['processed_files'][-10:]:  # Últimos 10
                st.write(f"• {Path(file_info['file']).name} ({file_info['size']} chars) - {file_info['timestamp']}")
        
        # Arquivos com falha
        if status['failed_files']:
            st.subheader("❌ Arquivos com Falha")
            for file_info in status['failed_files'][-10:]:  # Últimos 10
                st.write(f"• {Path(file_info['file']).name} - {file_info['error']} - {file_info['timestamp']}")

if __name__ == "__main__":
    main()
