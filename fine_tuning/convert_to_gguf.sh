#!/bin/bash
"""
Script para converter modelo fine-tuned para GGUF
Execute após o fine-tuning
"""

# Instalar dependências
pip install llama.cpp

# Converter para GGUF
python -m llama_cpp.llama_convert_hf_to_gguf \
    --outfile modelo_customizado.gguf \
    --outtype f16 \
    --model-dir lora_model

echo "✅ Conversão concluída!"
echo "📁 Arquivo GGUF: modelo_customizado.gguf"
