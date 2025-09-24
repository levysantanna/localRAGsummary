#!/usr/bin/env python3
"""
Interface Web para o Sistema RAG Local
Inspirada no PrivateGPT - Interface moderna e intuitiva
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

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embedding_system import EmbeddingSystem
from rag_agent import RAGAgent
from document_processor import DocumentProcessor
from markdown_generator import MarkdownGenerator
import config

# Configuração da página
st.set_page_config(
    page_title="Local RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
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
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    .user-message {
        background: #e3f2fd;
        margin-left: auto;
        border-bottom-right-radius: 0;
    }
    
    .bot-message {
        background: #f5f5f5;
        margin-right: auto;
        border-bottom-left-radius: 0;
    }
    
    .source-card {
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        border-left: 3px solid #28a745;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do sistema
@st.cache_resource
def initialize_system():
    """Inicializa o sistema RAG"""
    try:
        # Inicializar componentes
        embedding_system = EmbeddingSystem()
        rag_agent = RAGAgent(embedding_system)
        document_processor = DocumentProcessor()
        markdown_generator = MarkdownGenerator()
        
        return {
            'embedding_system': embedding_system,
            'rag_agent': rag_agent,
            'document_processor': document_processor,
            'markdown_generator': markdown_generator
        }
    except Exception as e:
        st.error(f"Erro ao inicializar o sistema: {e}")
        return None

def main():
    """Função principal da interface"""
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Local RAG System</h1>
        <p>Sistema de Recuperação e Geração Aumentada Local - 100% Privado</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema
    system = initialize_system()
    if not system:
        st.error("❌ Falha ao inicializar o sistema. Verifique as dependências.")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configurações")
        
        # Configurações de busca
        st.markdown("### 🔍 Parâmetros de Busca")
        top_k = st.slider("Número de documentos relevantes", 1, 10, 5)
        similarity_threshold = st.slider("Threshold de similaridade", -100.0, 0.0, -50.0)
        language = st.selectbox("Idioma", ["pt", "en"], index=0)
        
        # Configurações do sistema
        st.markdown("### 🛠️ Sistema")
        if st.button("🔄 Reinicializar Sistema"):
            st.cache_resource.clear()
            st.rerun()
        
        # Estatísticas
        st.markdown("### 📊 Estatísticas")
        try:
            # Contar documentos processados
            ragfiles_dir = Path(config.RAGFILES_DIR)
            if ragfiles_dir.exists():
                md_files = list(ragfiles_dir.glob("*.md"))
                st.metric("Documentos Processados", len(md_files))
            else:
                st.metric("Documentos Processados", 0)
        except:
            st.metric("Documentos Processados", "N/A")
    
    # Tabs principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat", 
        "📄 Documentos", 
        "📊 Análise", 
        "⚙️ Configurações",
        "ℹ️ Sobre"
    ])
    
    # Tab 1: Chat
    with tab1:
        st.markdown("## 💬 Chat com seus Documentos")
        
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
                    # Fazer consulta
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
    
    # Tab 2: Documentos
    with tab2:
        st.markdown("## 📄 Gerenciamento de Documentos")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📁 Processar Documentos")
            
            # Upload de arquivos
            uploaded_files = st.file_uploader(
                "Faça upload de documentos",
                type=['txt', 'pdf', 'docx', 'pptx', 'odt', 'ods', 'odp'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                if st.button("📤 Processar Documentos"):
                    with st.spinner("🔄 Processando documentos..."):
                        try:
                            # Criar diretório temporário
                            temp_dir = Path("temp_uploads")
                            temp_dir.mkdir(exist_ok=True)
                            
                            # Salvar arquivos
                            for file in uploaded_files:
                                file_path = temp_dir / file.name
                                with open(file_path, "wb") as f:
                                    f.write(file.getbuffer())
                            
                            # Processar documentos
                            documents = system['document_processor'].process_directory(
                                temp_dir, 
                                recursive=True
                            )
                            
                            if documents:
                                # Gerar embeddings
                                embeddings = system['embedding_system'].generate_embeddings(documents)
                                
                                # Armazenar embeddings
                                success = system['embedding_system'].store_embeddings(embeddings)
                                
                                if success:
                                    st.success(f"✅ {len(documents)} documentos processados com sucesso!")
                                    
                                    # Gerar resumos
                                    system['markdown_generator'].generate_notes(documents)
                                    st.success("📝 Resumos gerados!")
                                else:
                                    st.error("❌ Erro ao armazenar embeddings")
                            
                            # Limpar arquivos temporários
                            import shutil
                            shutil.rmtree(temp_dir)
                            
                        except Exception as e:
                            st.error(f"❌ Erro ao processar documentos: {e}")
        
        with col2:
            st.markdown("### 📊 Documentos Processados")
            
            # Listar documentos
            try:
                ragfiles_dir = Path(config.RAGFILES_DIR)
                if ragfiles_dir.exists():
                    md_files = list(ragfiles_dir.glob("*.md"))
                    
                    if md_files:
                        st.markdown(f"**Total:** {len(md_files)} documentos")
                        
                        for file in md_files[:5]:  # Mostrar apenas os 5 primeiros
                            st.markdown(f"• {file.name}")
                        
                        if len(md_files) > 5:
                            st.markdown(f"... e mais {len(md_files) - 5} documentos")
                    else:
                        st.info("Nenhum documento processado ainda")
                else:
                    st.info("Diretório de documentos não encontrado")
            except Exception as e:
                st.error(f"Erro ao listar documentos: {e}")
    
    # Tab 3: Análise
    with tab3:
        st.markdown("## 📊 Análise e Estatísticas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Estatísticas do Sistema")
            
            # Métricas básicas
            try:
                ragfiles_dir = Path(config.RAGFILES_DIR)
                if ragfiles_dir.exists():
                    md_files = list(ragfiles_dir.glob("*.md"))
                    
                    # Criar DataFrame para visualização
                    data = {
                        'Métrica': ['Documentos Processados', 'Resumos Gerados', 'Consultas Realizadas'],
                        'Valor': [
                            len(md_files),
                            len(md_files),
                            len(st.session_state.get('chat_history', []))
                        ]
                    }
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Gráfico de barras
                    fig = px.bar(df, x='Métrica', y='Valor', title="Estatísticas do Sistema")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nenhum dado disponível para análise")
            except Exception as e:
                st.error(f"Erro ao gerar estatísticas: {e}")
        
        with col2:
            st.markdown("### 🎯 Performance")
            
            # Métricas de performance
            if 'chat_history' in st.session_state and st.session_state.chat_history:
                # Calcular métricas
                confidences = [chat['confidence'] for chat in st.session_state.chat_history]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Gráfico de confiança
                fig = go.Figure(data=go.Scatter(
                    x=list(range(len(confidences))),
                    y=confidences,
                    mode='lines+markers',
                    name='Confiança'
                ))
                fig.update_layout(
                    title="Evolução da Confiança",
                    xaxis_title="Consulta",
                    yaxis_title="Confiança"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.metric("Confiança Média", f"{avg_confidence:.2f}")
            else:
                st.info("Nenhuma consulta realizada ainda")
    
    # Tab 4: Configurações
    with tab4:
        st.markdown("## ⚙️ Configurações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔧 Configurações de Busca")
            
            # Configurações do RAG
            st.markdown("**Parâmetros de Busca:**")
            st.code(f"""
Top K: {top_k}
Threshold: {similarity_threshold}
Idioma: {language}
            """)
            
            # Configurações do sistema
            st.markdown("**Configurações do Sistema:**")
            st.code(f"""
Diretório de Documentos: {config.DOCUMENTS_DIR}
Diretório RAG: {config.RAGFILES_DIR}
Banco de Dados: {config.VECTOR_DB_DIR}
            """)
        
        with col2:
            st.markdown("### 🛠️ Ações do Sistema")
            
            if st.button("🗑️ Limpar Histórico"):
                if 'chat_history' in st.session_state:
                    del st.session_state.chat_history
                st.success("Histórico limpo!")
            
            if st.button("🔄 Recarregar Sistema"):
                st.cache_resource.clear()
                st.rerun()
            
            if st.button("📊 Gerar Relatório"):
                st.info("Funcionalidade em desenvolvimento")
    
    # Tab 5: Sobre
    with tab5:
        st.markdown("## ℹ️ Sobre o Sistema")
        
        st.markdown("""
        ### 🤖 Local RAG System
        
        Sistema de Recuperação e Geração Aumentada (RAG) local, inspirado no [PrivateGPT](https://github.com/zylon-ai/private-gpt).
        
        #### ✨ Funcionalidades:
        - **100% Privado**: Todos os dados ficam no seu computador
        - **Suporte Multimodal**: PDF, DOCX, TXT, ODF, imagens
        - **Sistema Temático**: Separação automática por temas
        - **Audiobooks**: Geração de áudio em português
        - **Processamento de Vídeos**: Transcrição e resumo de vídeos
        - **Interface Web**: Interface moderna e intuitiva
        
        #### 🛠️ Tecnologias:
        - **Python 3.13+**
        - **Streamlit** para interface web
        - **ChromaDB** para banco de dados vetorial
        - **Sentence Transformers** para embeddings
        - **Transformers** para modelos de linguagem
        
        #### 📚 Documentação:
        - [README.md](README.md) - Documentação completa
        - [THEMATIC_SYSTEM_DOCS.md](THEMATIC_SYSTEM_DOCS.md) - Sistema temático
        - [VIDEO_SYSTEM_DOCS.md](VIDEO_SYSTEM_DOCS.md) - Processamento de vídeos
        - [ODF_SUPPORT_DEMO.md](ODF_SUPPORT_DEMO.md) - Suporte ODF
        
        #### 🎯 Inspirado em:
        - [PrivateGPT](https://github.com/zylon-ai/private-gpt) - Interface e conceitos
        - [LlamaIndex](https://github.com/run-llama/llama_index) - Framework RAG
        - [ChromaDB](https://github.com/chroma-core/chroma) - Banco de dados vetorial
        """)
        
        st.markdown("---")
        st.markdown("**Desenvolvido com ❤️ para a comunidade brasileira de IA**")

if __name__ == "__main__":
    main()
