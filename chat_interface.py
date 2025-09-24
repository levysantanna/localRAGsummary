"""
Interface de Chat Avançada para o Sistema RAG
"""
import gradio as gr
import streamlit as st
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

from enhanced_rag_system import EnhancedRAGSystem, ChatInterface

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedChatInterface:
    """Interface de chat avançada com múltiplas opções"""
    
    def __init__(self, enhanced_rag: EnhancedRAGSystem):
        self.enhanced_rag = enhanced_rag
        self.chat_history = []
    
    def gradio_interface(self):
        """Interface Gradio para chat"""
        
        def chat_function(message, history):
            """Função de chat para Gradio"""
            if not self.enhanced_rag.chat_interface:
                return "❌ Chat interface not available. Please train the model first."
            
            try:
                response = self.enhanced_rag.chat_interface.generate_response(message)
                return response
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def get_context_info():
            """Retorna informações sobre o contexto"""
            if not self.enhanced_rag.processed_documents:
                return "Nenhum documento processado."
            
            total_docs = len(self.enhanced_rag.processed_documents)
            total_urls = sum(len(doc.get('enhanced_content', {}).get('urls_found', [])) 
                           for doc in self.enhanced_rag.processed_documents)
            successful_scrapes = sum(1 for doc in self.enhanced_rag.processed_documents 
                                   for scraped in doc.get('enhanced_content', {}).get('scraped_content', {}).values()
                                   if scraped.get('status') == 'success')
            
            return f"""
📊 **Informações do Sistema:**
- Documentos processados: {total_docs}
- URLs encontradas: {total_urls}
- URLs processadas com sucesso: {successful_scrapes}
- Modelo treinado: {'✅ Sim' if self.enhanced_rag.chat_interface else '❌ Não'}
            """
        
        # Cria interface Gradio
        with gr.Blocks(title="Sistema RAG Local - Chat Interface") as interface:
            gr.Markdown("# 🤖 Sistema RAG Local - Chat Interface")
            gr.Markdown("Converse com o modelo treinado sobre seus documentos universitários.")
            
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="Chat",
                        height=400,
                        show_label=True
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Digite sua pergunta aqui...",
                            label="Mensagem",
                            lines=2
                        )
                        send_btn = gr.Button("Enviar", variant="primary")
                    
                    with gr.Row():
                        clear_btn = gr.Button("Limpar Chat")
                        context_btn = gr.Button("Ver Contexto")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Informações do Sistema")
                    context_info = gr.Markdown(get_context_info())
                    
                    gr.Markdown("### 💡 Dicas")
                    gr.Markdown("""
                    - Faça perguntas específicas sobre os documentos
                    - Use termos técnicos relacionados aos seus cursos
                    - O sistema pode responder sobre conteúdo web encontrado
                    - Digite 'ajuda' para ver comandos especiais
                    """)
            
            # Event handlers
            def user(user_message, history):
                return "", history + [[user_message, None]]
            
            def bot(history):
                if not history:
                    return history
                
                user_message = history[-1][0]
                if not self.enhanced_rag.chat_interface:
                    bot_message = "❌ Chat interface not available. Please train the model first."
                else:
                    try:
                        bot_message = self.enhanced_rag.chat_interface.generate_response(user_message)
                    except Exception as e:
                        bot_message = f"❌ Error: {str(e)}"
                
                history[-1][1] = bot_message
                return history
            
            def clear_chat():
                return []
            
            def show_context():
                return get_context_info()
            
            # Connect events
            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, chatbot, chatbot
            )
            send_btn.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, chatbot, chatbot
            )
            clear_btn.click(clear_chat, outputs=chatbot)
            context_btn.click(show_context, outputs=context_info)
        
        return interface
    
    def streamlit_interface(self):
        """Interface Streamlit para chat"""
        
        st.set_page_config(
            page_title="Sistema RAG Local",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 Sistema RAG Local - Chat Interface")
        st.markdown("Converse com o modelo treinado sobre seus documentos universitários.")
        
        # Sidebar com informações
        with st.sidebar:
            st.header("📊 Informações do Sistema")
            
            if not self.enhanced_rag.processed_documents:
                st.warning("Nenhum documento processado.")
            else:
                total_docs = len(self.enhanced_rag.processed_documents)
                total_urls = sum(len(doc.get('enhanced_content', {}).get('urls_found', [])) 
                               for doc in self.enhanced_rag.processed_documents)
                successful_scrapes = sum(1 for doc in self.enhanced_rag.processed_documents 
                                       for scraped in doc.get('enhanced_content', {}).get('scraped_content', {}).values()
                                       if scraped.get('status') == 'success')
                
                st.metric("Documentos processados", total_docs)
                st.metric("URLs encontradas", total_urls)
                st.metric("URLs processadas", successful_scrapes)
                
                if self.enhanced_rag.chat_interface:
                    st.success("✅ Modelo treinado disponível")
                else:
                    st.error("❌ Modelo não treinado")
            
            st.header("💡 Dicas")
            st.markdown("""
            - Faça perguntas específicas sobre os documentos
            - Use termos técnicos relacionados aos seus cursos
            - O sistema pode responder sobre conteúdo web encontrado
            - Digite 'ajuda' para ver comandos especiais
            """)
        
        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Digite sua pergunta aqui..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                if not self.enhanced_rag.chat_interface:
                    response = "❌ Chat interface not available. Please train the model first."
                else:
                    try:
                        with st.spinner("Processando..."):
                            response = self.enhanced_rag.chat_interface.generate_response(prompt)
                    except Exception as e:
                        response = f"❌ Error: {str(e)}"
                
                st.markdown(response)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Clear chat button
        if st.button("Limpar Chat"):
            st.session_state.messages = []
            st.rerun()

def create_gradio_interface(enhanced_rag: EnhancedRAGSystem):
    """Cria interface Gradio"""
    chat_interface = AdvancedChatInterface(enhanced_rag)
    return chat_interface.gradio_interface()

def create_streamlit_interface(enhanced_rag: EnhancedRAGSystem):
    """Cria interface Streamlit"""
    chat_interface = AdvancedChatInterface(enhanced_rag)
    chat_interface.streamlit_interface()

def main():
    """Função principal para testar interfaces"""
    print("🚀 Sistema RAG Local - Chat Interface")
    print("=" * 50)
    
    # Aqui você carregaria o sistema RAG treinado
    # enhanced_rag = load_trained_system()
    # interface = create_gradio_interface(enhanced_rag)
    # interface.launch()
    
    print("Interface de chat configurada com sucesso!")

if __name__ == "__main__":
    main()
