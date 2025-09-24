#!/bin/bash

# Script de instalação da Interface Web do Sistema RAG
# Inspirada no PrivateGPT

echo "🚀 Instalando Interface Web do Sistema RAG Local"
echo "=================================================="

# Verificar se estamos no diretório correto
if [ ! -f "web_interface.py" ]; then
    echo "❌ Execute este script no diretório do projeto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "🔧 Ativando ambiente virtual..."
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
else
    echo "⚠️  Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual criado e ativado"
fi

# Instalar dependências básicas primeiro
echo "📦 Instalando dependências básicas..."
pip install --upgrade pip

# Instalar dependências do sistema RAG
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependências do sistema RAG..."
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt não encontrado. Instalando dependências básicas..."
    pip install torch torchvision sentence-transformers chromadb faiss-cpu
    pip install pypdf2 python-docx python-pptx pillow pytesseract
    pip install nltk spacy transformers
fi

# Instalar dependências da interface web
echo "🌐 Instalando dependências da interface web..."
pip install streamlit plotly pandas

# Verificar instalação
echo "🔍 Verificando instalação..."
python3 -c "
import streamlit
import plotly
import pandas
print('✅ Todas as dependências instaladas com sucesso!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Instalação concluída com sucesso!"
    echo ""
    echo "🚀 Para iniciar a interface web, execute:"
    echo "   python run_web_interface.py"
    echo ""
    echo "📱 A interface será aberta em: http://localhost:8501"
    echo ""
    echo "🛠️  Funcionalidades disponíveis:"
    echo "   • Chat com documentos"
    echo "   • Upload e processamento de arquivos"
    echo "   • Análise e estatísticas"
    echo "   • Configurações do sistema"
    echo "   • Interface inspirada no PrivateGPT"
    echo ""
else
    echo "❌ Erro na instalação. Verifique as dependências."
    exit 1
fi
