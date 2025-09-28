# 🤖 Sistema RAG com Ollama

Interface Streamlit com integração completa ao Ollama para resultados de alta qualidade.

## ✨ Características

- **Seletor de Modelo**: Escolha entre diferentes modelos Ollama
- **Integração Ollama**: Respostas de alta qualidade usando LLMs locais
- **Busca Inteligente**: Busca semântica em documentos processados
- **Geração de Resumos**: Resumos automáticos com contexto relevante
- **Interface Intuitiva**: Controles claros e feedback visual

## 🚀 Instalação Rápida

```bash
# 1. Executar script de configuração
./setup_ollama.sh

# 2. Iniciar interface
cd /home/lsantann/dev/localRAGsummary
source venv/bin/activate
streamlit run interface_ollama.py --server.port 8511
```

## 🧠 Modelos Disponíveis

### Modelos Recomendados:
- **llama3.2** - Melhor equilíbrio qualidade/velocidade
- **llama3.1** - Versão anterior estável
- **mistral** - Alternativa eficiente
- **codellama** - Especializado em código

### Modelos Especializados:
- **phi3** - Microsoft Phi-3
- **gemma** - Google Gemma
- **qwen** - Alibaba Qwen
- **deepseek-coder** - Especializado em programação

## 📋 Como Usar

### 1. Configuração Inicial
- Acesse a interface em `http://localhost:8511`
- Verifique se o Ollama está conectado (✅ verde)
- Selecione o modelo desejado no sidebar

### 2. Fazer Consultas
- Digite sua pergunta no campo de texto
- Clique em "🔍 Buscar" para encontrar documentos relevantes
- Clique em "📝 Gerar Resumo" para criar resumo com IA

### 3. Resumos Salvos
- Todos os resumos são salvos automaticamente
- Visualize resumos anteriores na seção "📚 Resumos Salvos"
- Cada resumo inclui metadados e timestamp

## 🔧 Configurações Avançadas

### Modelos Personalizados
```bash
# Baixar modelo específico
ollama pull nome-do-modelo

# Listar modelos disponíveis
ollama list

# Remover modelo
ollama rm nome-do-modelo
```

### Configuração de Performance
- **Temperature**: 0.7 (criatividade)
- **Top-p**: 0.9 (diversidade)
- **Max Tokens**: 2048 (tamanho da resposta)

## 📊 Recursos da Interface

### Sidebar
- **Status Ollama**: Verificação de conexão
- **Seletor de Modelo**: Escolha do modelo ativo
- **Estatísticas**: Contadores de arquivos
- **Configurações**: Caminhos do sistema

### Área Principal
- **Campo de Consulta**: Input para perguntas
- **Botões de Ação**: Buscar e Gerar Resumo
- **Resultados**: Lista de documentos encontrados
- **Resumo Gerado**: Output da IA

### Seção de Resumos
- **Lista de Resumos**: Últimos 5 resumos gerados
- **Preview**: Visualização rápida do conteúdo
- **Metadados**: Data, tamanho, arquivo

## 🛠️ Solução de Problemas

### Ollama não conecta
```bash
# Verificar se está rodando
curl http://localhost:11434/api/tags

# Iniciar servidor
ollama serve

# Verificar logs
journalctl -u ollama
```

### Modelo não carrega
```bash
# Verificar modelos disponíveis
ollama list

# Baixar modelo específico
ollama pull llama3.2

# Verificar espaço em disco
df -h
```

### Interface não abre
```bash
# Verificar porta
netstat -tlnp | grep 8511

# Matar processo
pkill -f "streamlit run interface_ollama.py"

# Reiniciar
streamlit run interface_ollama.py --server.port 8511
```

## 📈 Melhorias de Qualidade

### Para Melhores Resultados:
1. **Use modelos maiores** (llama3.2, mistral)
2. **Faça perguntas específicas** e detalhadas
3. **Processe mais documentos** para maior contexto
4. **Ajuste temperatura** para diferentes tipos de resposta

### Dicas de Uso:
- Perguntas abertas: "Explique o conceito de..."
- Perguntas específicas: "Quais são os 3 principais..."
- Comparações: "Compare X com Y..."
- Listas: "Liste os principais..."

## 🔗 URLs Importantes

- **Interface**: http://localhost:8511
- **Ollama API**: http://localhost:11434
- **Documentos**: /home/lsantann/Documents/CC/
- **Resumos**: /home/lsantann/dev/localRAGsummary/summaries/

## 📝 Logs e Monitoramento

```bash
# Ver logs do Ollama
journalctl -u ollama -f

# Ver logs da interface
tail -f /tmp/streamlit.log

# Monitorar uso de memória
htop | grep ollama
```

---

**🎯 Resultado**: Interface completa com seleção de modelo e integração Ollama para respostas de alta qualidade!
