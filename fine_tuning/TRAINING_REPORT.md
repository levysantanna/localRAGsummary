# Relatório de Fine-Tuning

## 📊 Estatísticas
- **Pares de treinamento**: 10190
- **Data**: 26/09/2025 09:23:40
- **Diretório**: /home/lsantann/Documents/CC

## 📁 Arquivos Gerados
- `data/training_data.jsonl` - Dados de treinamento
- `data/training_data.json` - Dados em formato JSON
- `modelfiles/universitario-custom.Modelfile` - Modelfile
- `train_model.py` - Script de treinamento
- `convert_to_gguf.sh` - Script de conversão

## 🚀 Próximos Passos

### 1. Executar Fine-Tuning
```bash
# No Google Colab ou ambiente com GPU
python train_model.py
```

### 2. Converter para GGUF
```bash
bash convert_to_gguf.sh
```

### 3. Criar Modelo Ollama
```bash
ollama create universitario-custom -f modelfiles/universitario-custom.Modelfile
```

### 4. Testar Modelo
```bash
ollama run universitario-custom
```

## 📈 Recomendações
- Use pelo menos 50-100 exemplos para bons resultados
- Ajuste parâmetros de treinamento conforme necessário
- Teste o modelo com diferentes tipos de perguntas
- Monitore a qualidade das respostas

---
*Gerado automaticamente pelo sistema de fine-tuning*
