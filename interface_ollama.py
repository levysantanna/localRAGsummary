#!/usr/bin/env python3
"""
Interface Streamlit com Integração Ollama
Sistema RAG com seleção de modelo de linguagem
"""

import streamlit as st
import requests
import json
import sqlite3
import os
from pathlib import Path
import time
from datetime import datetime
import PyPDF2
from docx import Document

# Configurações
DOCUMENTS_DIR = Path("/home/lsantann/Documents/CC/")
VECTOR_DB_PATH = Path("/home/lsantann/dev/localRAGsummary/vector_db.sqlite")
SUMMARIES_DIR = Path("/home/lsantann/dev/localRAGsummary/summaries")
OLLAMA_BASE_URL = "http://localhost:11434"

# Criar diretórios se não existirem
SUMMARIES_DIR.mkdir(exist_ok=True)

# Modelos disponíveis
AVAILABLE_MODELS = {
    "llama3.2": "Llama 3.2 (Recomendado)",
    "llama3.1": "Llama 3.1", 
    "llama3": "Llama 3",
    "mistral": "Mistral 7B",
    "codellama": "Code Llama",
    "phi3": "Phi-3",
    "gemma": "Gemma 2B",
    "qwen": "Qwen 2.5",
    "deepseek-coder": "DeepSeek Coder",
    "starcoder": "StarCoder"
}

class OllamaRAG:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.base_url = OLLAMA_BASE_URL
        
    def check_ollama_connection(self):
        """Verifica se o Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Obtém modelos disponíveis no Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
        except:
            pass
        return []
    
    def generate_response(self, prompt, context=""):
        """Gera resposta usando Ollama"""
        try:
            full_prompt = f"""Contexto dos documentos:
{context}

Pergunta: {prompt}

Responda de forma detalhada e precisa baseado no contexto fornecido. Se não houver informação suficiente no contexto, indique isso claramente."""
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'Erro ao gerar resposta')
            else:
                return f"Erro na API Ollama: {response.status_code}"
                
        except Exception as e:
            return f"Erro ao conectar com Ollama: {str(e)}"

def get_database_files():
    """Obtém arquivos do banco de dados"""
    try:
        conn = sqlite3.connect(VECTOR_DB_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        
        cursor = conn.execute("""
            SELECT file_path, file_type, COUNT(*) as count
            FROM documents 
            GROUP BY file_path, file_type
            ORDER BY file_path
        """)
        
        files = cursor.fetchall()
        conn.close()
        return files
    except Exception as e:
        st.error(f"Erro ao acessar banco de dados: {e}")
        return []

def get_available_files():
    """Obtém arquivos disponíveis no diretório"""
    if not DOCUMENTS_DIR.exists():
        return []
    
    supported_extensions = [
        '.txt', '.md', '.rst', '.py', '.js', '.html', '.css', '.json', '.xml',
        '.pdf', '.docx', '.doc', '.odt', '.rtf',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
        '.pptx', '.ppt', '.odp'
    ]
    
    files = []
    for ext in supported_extensions:
        files.extend(DOCUMENTS_DIR.rglob(f"*{ext}"))
    
    return files

def extract_content_from_file(file_path):
    """Extrai conteúdo de arquivo baseado na extensão"""
    try:
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        if ext in ['.txt', '.md', '.rst']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        
        elif ext in ['.docx']:
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        elif ext in ['.py', '.js', '.html', '.css', '.json', '.xml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        else:
            return f"[Arquivo {ext} - processamento não implementado]"
            
    except Exception as e:
        return f"[Erro ao processar arquivo: {e}]"

def search_documents(query, limit=5):
    """Busca documentos relevantes"""
    try:
        conn = sqlite3.connect(VECTOR_DB_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Busca simples por texto
        cursor = conn.execute("""
            SELECT file_path, file_type, content, metadata
            FROM documents 
            WHERE content LIKE ? OR file_path LIKE ?
            ORDER BY LENGTH(content) DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        st.error(f"Erro na busca: {e}")
        return []

def generate_summary(question, results, rag_system):
    """Gera resumo usando Ollama"""
    if not results:
        return "Nenhum documento relevante encontrado."
    
    context = ""
    for i, (file_path, file_type, content, metadata) in enumerate(results, 1):
        context += f"\n--- Documento {i}: {Path(file_path).name} ({file_type}) ---\n"
        context += content[:1000] + "..." if len(content) > 1000 else content
        context += "\n"
    
    summary = rag_system.generate_response(
        f"Resuma os seguintes documentos em resposta à pergunta: {question}",
        context
    )
    
    return summary

def save_summary(question, summary):
    """Salva resumo em arquivo markdown"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_question = "".join(c for c in question if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_question = safe_question[:50]  # Limita tamanho
    
    filename = f"resumo_{safe_question}_{timestamp}.md"
    filepath = SUMMARIES_DIR / filename
    
    content = f"""# Resumo: {question}

**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## Resumo Gerado

{summary}

---
*Gerado automaticamente pelo sistema RAG com Ollama*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    st.set_page_config(
        page_title="RAG System com Ollama",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Sistema RAG com Ollama")
    st.markdown("**Sistema de Recuperação e Geração com Modelos Ollama**")
    
    # Sidebar - Configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Verificar conexão Ollama
        ollama_status = st.empty()
        if 'ollama_rag' not in st.session_state:
            st.session_state['ollama_rag'] = OllamaRAG()
        
        if st.session_state['ollama_rag'].check_ollama_connection():
            ollama_status.success("✅ Ollama Conectado")
            
            # Seletor de modelo
            available_models = st.session_state['ollama_rag'].get_available_models()
            if available_models:
                st.subheader("🧠 Modelo de Linguagem")
                selected_model = st.selectbox(
                    "Escolha o modelo:",
                    available_models,
                    index=0 if 'llama3.2' not in available_models else available_models.index('llama3.2')
                )
                
                if st.button("🔄 Atualizar Modelo"):
                    st.session_state['ollama_rag'] = OllamaRAG(selected_model)
                    st.success(f"Modelo atualizado: {selected_model}")
            else:
                st.warning("Nenhum modelo encontrado no Ollama")
        else:
            ollama_status.error("❌ Ollama Desconectado")
            st.error("**Instale e inicie o Ollama:**")
            st.code("""
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar modelo
ollama pull llama3.2

# Iniciar servidor
ollama serve
            """)
        
        st.divider()
        
        # Configurações do sistema
        st.subheader("📁 Diretórios")
        st.text(f"Documentos: {DOCUMENTS_DIR}")
        st.text(f"Banco: {VECTOR_DB_PATH}")
        st.text(f"Resumos: {SUMMARIES_DIR}")
        
        # Estatísticas
        db_files = get_database_files()
        st.subheader("📊 Estatísticas")
        st.metric("Arquivos no Banco", len(db_files))
        
        available_files = get_available_files()
        st.metric("Arquivos Disponíveis", len(available_files))
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🔍 Consulta RAG")
        
        # Campo de consulta
        question = st.text_area(
            "Digite sua pergunta:",
            placeholder="Ex: Quais são os principais conceitos de inteligência artificial?",
            height=100
        )
        
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            if st.button("🔍 Buscar", type="primary", use_container_width=True):
                if question.strip():
                    with st.spinner("Buscando documentos..."):
                        results = search_documents(question, limit=5)
                        
                        if results:
                            st.session_state['search_results'] = results
                            st.session_state['current_question'] = question
                            st.success(f"Encontrados {len(results)} documentos relevantes")
                        else:
                            st.warning("Nenhum documento relevante encontrado")
                else:
                    st.warning("Digite uma pergunta")
        
        with col_btn2:
            if st.button("📝 Gerar Resumo", use_container_width=True):
                if 'search_results' in st.session_state and st.session_state['search_results']:
                    with st.spinner("Gerando resumo com Ollama..."):
                        summary = generate_summary(
                            st.session_state['current_question'],
                            st.session_state['search_results'],
                            st.session_state['ollama_rag']
                        )
                        
                        st.session_state['generated_summary'] = summary
                        st.success("Resumo gerado com sucesso!")
                else:
                    st.warning("Execute uma busca primeiro")
    
    with col2:
        st.header("📋 Resultados")
        
        # Mostrar resultados da busca
        if 'search_results' in st.session_state and st.session_state['search_results']:
            st.subheader("📄 Documentos Encontrados")
            
            for i, (file_path, file_type, content, metadata) in enumerate(st.session_state['search_results'], 1):
                with st.expander(f"📄 {Path(file_path).name} ({file_type})"):
                    st.text(f"Arquivo: {file_path}")
                    st.text(f"Tipo: {file_type}")
                    st.text(f"Tamanho: {len(content)} caracteres")
                    
                    # Mostrar preview do conteúdo
                    preview = content[:300] + "..." if len(content) > 300 else content
                    st.text_area(f"Preview {i}:", preview, height=100, disabled=True)
        
        # Mostrar resumo gerado
        if 'generated_summary' in st.session_state:
            st.subheader("📝 Resumo Gerado")
            
            st.markdown(st.session_state['generated_summary'])
            
            # Botão para salvar resumo
            if st.button("💾 Salvar Resumo"):
                if 'current_question' in st.session_state:
                    filepath = save_summary(
                        st.session_state['current_question'],
                        st.session_state['generated_summary']
                    )
                    st.success(f"Resumo salvo: {filepath}")
    
    # Seção de resumos gerados
    st.header("📚 Resumos Salvos")
    
    try:
        summary_files = list(SUMMARIES_DIR.glob("*.md"))
        summary_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if summary_files:
            st.subheader("Últimos 5 Resumos")
            
            for i, filepath in enumerate(summary_files[:5]):
                with st.expander(f"📄 {filepath.name}"):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Mostrar metadados
                        st.text(f"Arquivo: {filepath}")
                        st.text(f"Tamanho: {len(content)} caracteres")
                        st.text(f"Modificado: {datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%d/%m/%Y %H:%M')}")
                        
                        # Mostrar preview
                        preview = content[:500] + "..." if len(content) > 500 else content
                        st.markdown(preview)
                        
                        # Botão para ver completo
                        if st.button(f"Ver Completo {i+1}"):
                            st.markdown("---")
                            st.markdown(content)
                            
                    except Exception as e:
                        st.error(f"Erro ao ler arquivo: {e}")
        else:
            st.info("Nenhum resumo gerado ainda")
            
    except Exception as e:
        st.error(f"Erro ao listar resumos: {e}")

if __name__ == "__main__":
    main()
