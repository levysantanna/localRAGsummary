#!/usr/bin/env python3
"""
Teste simples do sistema RAG
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embedding_system import EmbeddingSystem
from rag_agent import RAGAgent
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_system():
    """Teste básico do sistema RAG"""
    print("🧪 Testando Sistema RAG Básico")
    print("=" * 50)
    
    try:
        # Inicializar sistema de embeddings
        print("📊 Inicializando sistema de embeddings...")
        embedding_system = EmbeddingSystem()
        
        # Inicializar agente RAG
        print("🤖 Inicializando agente RAG...")
        rag_agent = RAGAgent(embedding_system)
        
        # Testar consulta
        print("❓ Testando consulta...")
        query = "machine learning"
        result = rag_agent.query(query, language="pt")
        
        print(f"Pergunta: {query}")
        print(f"Resposta: {result['answer']}")
        print(f"Confiança: {result['confidence']}")
        print(f"Fontes: {result['sources']}")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_system()
