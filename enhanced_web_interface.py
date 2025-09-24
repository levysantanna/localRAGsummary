#!/usr/bin/env python3
"""
Interface Web Aprimorada para o Sistema RAG Local
- Processamento em tempo real
- Contagem dinâmica de documentos
- Scraping de URLs
- Suporte completo para imagens
- Atualização automática
"""

import streamlit as st
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_document_processor import EnhancedDocumentProcessor
from embedding_system import EmbeddingSystem
from rag_agent import RAGAgent
import config

# Configuração da página
st.set_page_config(
    page_title="Local RAG System - Enhanced",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado aprimorado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .processing-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 20px;
        margin: 1rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    .file-list {
        max-height: 300px;
        overflow-y: auto;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .url-item {
        background: white;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        border-left: 3px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do sistema
@st.cache_resource
def initialize_enhanced_system():
    """Inicializa o sistema RAG aprimorado"""
    try:
        processor = EnhancedDocumentProcessor()
        embedding_system = EmbeddingSystem()
        rag_agent = RAGAgent(embedding_system)
        
        return {
            'processor': processor,
            'embedding_system': embedding_system,
            'rag_agent': rag_agent
        }
    except Exception as e:
        st.error(f"Erro ao inicializar o sistema: {e}")
        return None

def get_file_stats(directory: Path) -> Dict[str, Any]:
    """Obtém estatísticas dos arquivos no diretório"""
    if not directory.exists():
        return {'total': 0, 'by_type': {}, 'files': []}
    
    all_files = []
    by_type = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            all_files.append({
                'name': file,
                'path': str(file_path),
                'extension': ext,
                'size': file_path.stat().st_size if file_path.exists() else 0
            })
            
            if ext not in by_type:
                by_type[ext] = 0
            by_type[ext] += 1
    
    return {
        'total': len(all_files),
        'by_type': by_type,
        'files': all_files
    }

def main():
    """Função principal da interface aprimorada"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Local RAG System - Enhanced</h1>
        <p>Sistema de Recuperação e Geração Aumentada Local - Processamento Completo</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema
    system = initialize_enhanced_system()
    if not system:
        st.error("❌ Falha ao inicializar o sistema. Verifique as dependências.")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configurações")
        
        # Configurações de busca
        st.markdown("### 🔍 Parâmetros de Busca")
        top_k = st.slider("Número de documentos relevantes", 1, 20, 10)
        similarity_threshold = st.slider("Threshold de similaridade", -100.0, 0.0, -50.0)
        language = st.selectbox("Idioma", ["pt", "en"], index=0)
        
        # Configurações do processamento
        st.markdown("### 🔄 Processamento")
        auto_process = st.checkbox("Processamento automático", value=True)
        scrape_urls = st.checkbox("Scraping de URLs", value=True)
        process_images = st.checkbox("Processar imagens com OCR", value=True)
        
        # Ações
        st.markdown("### 🛠️ Ações")
        if st.button("🔄 Processar Todos os Documentos"):
            st.session_state['process_all'] = True
        
        if st.button("🧹 Limpar Cache"):
            st.cache_resource.clear()
            st.rerun()
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "🔄 Processamento", 
        "💬 Chat", 
        "📄 Documentos",
        "ℹ️ Sobre"
    ])
    
    # Tab 1: Dashboard
    with tab1:
        st.markdown("## 📊 Dashboard do Sistema")
        
        # Estatísticas dos arquivos
        file_stats = get_file_stats(config.DOCUMENTS_DIR)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Arquivos", file_stats['total'])
        
        with col2:
            st.metric("Arquivos Processados", st.session_state.get('processed_count', 0))
        
        with col3:
            st.metric("URLs Scraped", st.session_state.get('scraped_urls_count', 0))
        
        with col4:
            st.metric("Progresso", f"{st.session_state.get('progress_percent', 0):.1f}%")
        
        # Gráfico de tipos de arquivo
        if file_stats['by_type']:
            st.markdown("### 📁 Tipos de Arquivo")
            df_types = pd.DataFrame(list(file_stats['by_type'].items()), columns=['Tipo', 'Quantidade'])
            fig = px.pie(df_types, values='Quantidade', names='Tipo', title="Distribuição por Tipo de Arquivo")
            st.plotly_chart(fig, use_container_width=True)
        
        # Lista de arquivos
        if file_stats['files']:
            st.markdown("### 📄 Arquivos Encontrados")
            with st.expander(f"Ver todos os {len(file_stats['files'])} arquivos"):
                for file_info in file_stats['files'][:20]:  # Mostrar apenas os primeiros 20
                    st.write(f"📄 {file_info['name']} ({file_info['extension']})")
                
                if len(file_stats['files']) > 20:
                    st.write(f"... e mais {len(file_stats['files']) - 20} arquivos")
    
    # Tab 2: Processamento
    with tab2:
        st.markdown("## 🔄 Processamento de Documentos")
        
        # Processamento automático
        if auto_process and st.session_state.get('process_all', False):
            st.markdown("### 🚀 Processamento em Andamento")
            
            # Container para progresso
            progress_container = st.container()
            
            with progress_container:
                st.markdown("""
                <div class="processing-card">
                    <h3>🔄 Processando Documentos...</h3>
                    <p>O sistema está processando todos os documentos do diretório.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Processar documentos
                def progress_callback(progress):
                    progress_bar.progress(progress['progress_percent'] / 100)
                    status_text.text(f"Processando: {progress['current_file']} ({progress['processed']}/{progress['total']})")
                
                try:
                    results = system['processor'].process_all_documents(
                        config.DOCUMENTS_DIR,
                        callback=progress_callback
                    )
                    
                    # Atualizar session state
                    st.session_state['processed_count'] = results['processed_count']
                    st.session_state['scraped_urls_count'] = results['scraped_urls_count']
                    st.session_state['progress_percent'] = 100.0
                    st.session_state['process_all'] = False
                    
                    # Mostrar resultados
                    st.markdown("""
                    <div class="success-card">
                        <h3>✅ Processamento Concluído!</h3>
                        <p>Todos os documentos foram processados com sucesso.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Métricas de resultado
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Documentos Processados", results['processed_count'])
                    with col2:
                        st.metric("URLs Scraped", results['scraped_urls_count'])
                    with col3:
                        st.metric("Falhas", results['failed_count'])
                    
                    if results['failed_files']:
                        st.markdown("### ❌ Arquivos que Falharam")
                        for file in results['failed_files']:
                            st.write(f"- {file}")
                    
                    if results['scraped_urls_count'] > 0:
                        st.markdown("### 🌐 URLs Scraped")
                        for url in system['processor'].scraped_urls:
                            st.write(f"🔗 {url}")
                
                except Exception as e:
                    st.error(f"Erro durante o processamento: {e}")
                    st.session_state['process_all'] = False
        
        else:
            st.markdown("### 📋 Status do Processamento")
            
            # Estatísticas atuais
            stats = system['processor'].get_processing_stats()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Estatísticas")
                st.metric("Total de Arquivos", stats['total_files'])
                st.metric("Processados", stats['processed_count'])
                st.metric("URLs Scraped", stats['scraped_urls_count'])
            
            with col2:
                st.markdown("#### 📈 Progresso")
                progress_percent = stats['progress_percent']
                st.progress_bar(progress_percent / 100)
                st.write(f"Progresso: {progress_percent:.1f}%")
            
            # Botão para processar
            if st.button("🚀 Iniciar Processamento Completo", type="primary"):
                st.session_state['process_all'] = True
                st.rerun()
    
    # Tab 3: Chat
    with tab3:
        st.markdown("## 💬 Chat com Documentos")
        
        # Área de chat
        chat_container = st.container()
        
        # Input de pergunta
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input(
                "Faça uma pergunta sobre seus documentos:",
                placeholder="Ex: O que é machine learning?",
                key="question_input"
            )
        
        with col2:
            ask_button = st.button("🔍 Perguntar", type="primary", use_container_width=True)
        
        # Processar pergunta
        if ask_button and question:
            with st.spinner("🤔 Processando pergunta..."):
                try:
                    result = system['rag_agent'].query(
                        question, 
                        language=language,
                        context_limit=top_k
                    )
                    
                    # Exibir resultado
                    st.markdown("### 💡 Resposta")
                    st.markdown(f"**Pergunta:** {result['question']}")
                    st.markdown(f"**Resposta:** {result['answer']}")
                    st.markdown(f"**Confiança:** {result['confidence']:.2f}")
                    
                    # Exibir fontes
                    if result['sources']:
                        st.markdown("### 📚 Fontes")
                        for i, source in enumerate(result['sources'], 1):
                            with st.expander(f"Fonte {i}: {source.get('file_path', 'N/A')}"):
                                st.markdown(f"**Tipo:** {source.get('file_type', 'N/A')}")
                                st.markdown(f"**Similaridade:** {source.get('similarity', 0):.2f}")
                                st.markdown(f"**Preview:** {source.get('text_preview', 'N/A')}")
                    
                    # Salvar conversa
                    if 'chat_history' not in st.session_state:
                        st.session_state.chat_history = []
                    
                    st.session_state.chat_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'question': question,
                        'answer': result['answer'],
                        'confidence': result['confidence'],
                        'sources': len(result['sources'])
                    })
                    
                except Exception as e:
                    st.error(f"❌ Erro ao processar pergunta: {e}")
        
        # Histórico de chat
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            st.markdown("### 📝 Histórico de Conversas")
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
                with st.expander(f"Conversa {i} - {chat['timestamp'][:19]}"):
                    st.markdown(f"**Pergunta:** {chat['question']}")
                    st.markdown(f"**Resposta:** {chat['answer']}")
                    st.markdown(f"**Confiança:** {chat['confidence']:.2f} | **Fontes:** {chat['sources']}")
    
    # Tab 4: Documentos
    with tab4:
        st.markdown("## 📄 Gerenciamento de Documentos")
        
        # Upload de arquivos
        st.markdown("### 📤 Upload de Novos Documentos")
        uploaded_files = st.file_uploader(
            "Faça upload de documentos",
            type=['txt', 'pdf', 'docx', 'pptx', 'odt', 'ods', 'odp', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("📤 Processar Documentos Uploaded"):
                with st.spinner("🔄 Processando documentos..."):
                    # Processar arquivos uploaded
                    for file in uploaded_files:
                        # Salvar arquivo temporariamente
                        temp_path = config.DOCUMENTS_DIR / file.name
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        
                        # Processar documento
                        document = system['processor'].process_document_with_urls(temp_path)
                        
                        if document:
                            st.success(f"✅ Processado: {file.name}")
                        else:
                            st.error(f"❌ Falhou: {file.name}")
        
        # Lista de documentos processados
        st.markdown("### 📋 Documentos Processados")
        ragfiles_dir = Path(config.RAGFILES_DIR)
        if ragfiles_dir.exists():
            md_files = list(ragfiles_dir.glob("*.md"))
            st.metric("Resumos Gerados", len(md_files))
            
            if md_files:
                for file in md_files[:10]:  # Mostrar apenas os primeiros 10
                    st.write(f"📝 {file.name}")
                
                if len(md_files) > 10:
                    st.write(f"... e mais {len(md_files) - 10} resumos")
        else:
            st.info("Nenhum documento processado ainda")
    
    # Tab 5: Sobre
    with tab5:
        st.markdown("## ℹ️ Sobre o Sistema Aprimorado")
        
        st.markdown("""
        ### 🤖 Local RAG System - Enhanced
        
        Sistema de Recuperação e Geração Aumentada (RAG) local com processamento completo.
        
        #### ✨ Funcionalidades Aprimoradas:
        - **Processamento Completo**: Processa TODOS os arquivos do diretório
        - **Scraping de URLs**: Detecta e faz scraping automático de URLs nos documentos
        - **Suporte Completo para Imagens**: OCR em PNG, JPEG, GIF, BMP, TIFF
        - **Atualização Dinâmica**: Contagem em tempo real do processamento
        - **Processamento Contínuo**: Não para até processar todos os arquivos
        - **Interface Moderna**: Design inspirado no PrivateGPT
        
        #### 🛠️ Tecnologias:
        - **Python 3.13+**
        - **Streamlit** para interface web
        - **BeautifulSoup** para scraping de URLs
        - **ChromaDB** para banco de dados vetorial
        - **Sentence Transformers** para embeddings
        - **OCR** para processamento de imagens
        
        #### 📊 Métricas Disponíveis:
        - Total de arquivos encontrados
        - Arquivos processados com sucesso
        - URLs detectadas e scraped
        - Progresso em tempo real
        - Estatísticas por tipo de arquivo
        
        #### 🎯 Inspirado em:
        - [PrivateGPT](https://github.com/zylon-ai/private-gpt) - Interface e conceitos
        - [LlamaIndex](https://github.com/run-llama/llama_index) - Framework RAG
        - [ChromaDB](https://github.com/chroma-core/chroma) - Banco de dados vetorial
        """)
        
        st.markdown("---")
        st.markdown("**Desenvolvido com ❤️ para a comunidade brasileira de IA**")

if __name__ == "__main__":
    main()
