#!/bin/bash

echo "🤖 Configurando Sistema RAG com Ollama"
echo "======================================"

# Verificar se Ollama está instalado
if ! command -v ollama &> /dev/null; then
    echo "📥 Instalando Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama já está instalado"
fi

# Verificar se o servidor está rodando
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "🚀 Iniciando servidor Ollama..."
    ollama serve &
    sleep 3
fi

# Baixar modelos recomendados
echo "📦 Baixando modelos recomendados..."

echo "Baixando Llama 3.2 (recomendado)..."
ollama pull llama3.2

echo "Baixando Mistral 7B (alternativa)..."
ollama pull mistral

echo "Baixando Code Llama (para código)..."
ollama pull codellama

# Verificar modelos disponíveis
echo "📋 Modelos disponíveis:"
ollama list

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "Para iniciar a interface:"
echo "cd /home/lsantann/dev/localRAGsummary"
echo "source venv/bin/activate"
echo "streamlit run interface_ollama.py --server.port 8511"
echo ""
echo "Acesse: http://localhost:8511"
