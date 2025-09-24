# 🌐 Interface Web do Sistema RAG Local

Interface web moderna inspirada no [PrivateGPT](https://github.com/zylon-ai/private-gpt) para o sistema RAG local.

## ✨ Funcionalidades

### 💬 Chat Inteligente
- Interface de chat moderna e intuitiva
- Processamento de perguntas em tempo real
- Exibição de fontes e confiança das respostas
- Histórico de conversas

### 📄 Gerenciamento de Documentos
- Upload de múltiplos arquivos
- Suporte a PDF, DOCX, TXT, ODF, imagens
- Processamento automático
- Geração de resumos em Markdown

### 📊 Análise e Estatísticas
- Métricas do sistema em tempo real
- Gráficos de performance
- Evolução da confiança das respostas
- Estatísticas de uso

### ⚙️ Configurações Avançadas
- Parâmetros de busca personalizáveis
- Configurações do sistema
- Ações de manutenção
- Relatórios detalhados

## 🚀 Instalação Rápida

### 1. Instalar Dependências
```bash
# Tornar o script executável
chmod +x install_web_interface.sh

# Executar instalação
./install_web_interface.sh
```

### 2. Iniciar Interface
```bash
# Método 1: Script automático
python run_web_interface.py

# Método 2: Streamlit direto
streamlit run web_interface.py
```

### 3. Acessar Interface
- Abra seu navegador em: `http://localhost:8501`
- A interface será carregada automaticamente

## 🎯 Características da Interface

### 🎨 Design Moderno
- Interface inspirada no PrivateGPT
- Design responsivo e intuitivo
- Cores e gradientes modernos
- Componentes interativos

### 📱 Layout Responsivo
- Sidebar com configurações
- Tabs organizadas por funcionalidade
- Cards informativos
- Gráficos interativos

### 🔧 Funcionalidades Avançadas
- Cache inteligente do sistema
- Processamento em background
- Feedback visual em tempo real
- Tratamento de erros elegante

## 📋 Estrutura da Interface

### Tab 1: 💬 Chat
- **Área de Chat**: Interface principal para perguntas
- **Input de Pergunta**: Campo de texto com botão de envio
- **Exibição de Respostas**: Respostas formatadas com fontes
- **Histórico**: Últimas 5 conversas

### Tab 2: 📄 Documentos
- **Upload de Arquivos**: Drag & drop de múltiplos arquivos
- **Processamento**: Botão para processar documentos
- **Lista de Documentos**: Documentos já processados
- **Status**: Feedback do processamento

### Tab 3: 📊 Análise
- **Estatísticas**: Métricas do sistema
- **Gráficos**: Visualizações interativas
- **Performance**: Evolução da confiança
- **Métricas**: Dados em tempo real

### Tab 4: ⚙️ Configurações
- **Parâmetros de Busca**: Top K, threshold, idioma
- **Configurações do Sistema**: Caminhos e configurações
- **Ações**: Limpar histórico, recarregar sistema
- **Relatórios**: Geração de relatórios

### Tab 5: ℹ️ Sobre
- **Informações do Sistema**: Descrição e funcionalidades
- **Tecnologias**: Stack tecnológico
- **Documentação**: Links para documentação
- **Créditos**: Inspiração e tecnologias

## 🛠️ Configurações Avançadas

### Sidebar
- **Número de Documentos**: Slider de 1-10
- **Threshold de Similaridade**: Slider de -100 a 0
- **Idioma**: Seleção entre PT/EN
- **Reinicialização**: Botão para reiniciar sistema

### Parâmetros de Busca
```python
top_k = 5                    # Número de documentos relevantes
similarity_threshold = -50.0 # Threshold de similaridade
language = "pt"              # Idioma das respostas
```

## 📊 Métricas Disponíveis

### Sistema
- **Documentos Processados**: Contagem de arquivos
- **Resumos Gerados**: Arquivos Markdown criados
- **Consultas Realizadas**: Número de perguntas

### Performance
- **Confiança Média**: Média das confianças
- **Evolução da Confiança**: Gráfico temporal
- **Taxa de Sucesso**: Percentual de respostas válidas

## 🎨 Personalização

### CSS Customizado
```css
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    /* Gradiente moderno */
}

.metric-card {
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    /* Cards com sombra */
}
```

### Tema
- **Cores Principais**: Azul (#667eea) e Roxo (#764ba2)
- **Gradientes**: Linear gradients modernos
- **Sombras**: Box-shadows sutis
- **Bordas**: Border-radius arredondado

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Dependências
```bash
# Reinstalar dependências
pip install --upgrade streamlit plotly pandas
```

#### 2. Porta Ocupada
```bash
# Usar porta diferente
streamlit run web_interface.py --server.port 8502
```

#### 3. Cache do Sistema
```bash
# Limpar cache do Streamlit
streamlit cache clear
```

### Logs e Debug
- **Console**: Logs do sistema no terminal
- **Streamlit**: Logs da interface no navegador
- **Sistema**: Logs do RAG no console

## 🚀 Deploy e Produção

### Local
```bash
# Desenvolvimento
streamlit run web_interface.py

# Produção
streamlit run web_interface.py --server.headless true
```

### Docker (Futuro)
```dockerfile
# Dockerfile para containerização
FROM python:3.13-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements_web.txt
EXPOSE 8501
CMD ["streamlit", "run", "web_interface.py"]
```

## 📚 Documentação Relacionada

- [README.md](README.md) - Documentação principal
- [THEMATIC_SYSTEM_DOCS.md](THEMATIC_SYSTEM_DOCS.md) - Sistema temático
- [VIDEO_SYSTEM_DOCS.md](VIDEO_SYSTEM_DOCS.md) - Processamento de vídeos
- [ODF_SUPPORT_DEMO.md](ODF_SUPPORT_DEMO.md) - Suporte ODF

## 🎯 Inspiração

Esta interface foi inspirada no [PrivateGPT](https://github.com/zylon-ai/private-gpt), mantendo:
- **Design moderno e intuitivo**
- **Funcionalidades similares**
- **Experiência de usuário consistente**
- **Interface responsiva e acessível**

## 🤝 Contribuição

Para contribuir com a interface:
1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Teste a interface
5. Submeta um Pull Request

## 📄 Licença

GPL-3.0 - Veja [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ para a comunidade brasileira de IA**
