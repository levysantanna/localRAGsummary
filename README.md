# Local RAG System para Documentos Universitários

Sistema de RAG (Retrieval-Augmented Generation) local para processamento e consulta de documentos universitários com suporte completo ao português brasileiro, OCR, análise de código, processamento de vídeos, sistema temático com audiobooks e geração automática de notas em Markdown.

## 🚀 Características Principais

- **Processamento Multimodal**: PDFs, imagens, documentos Word/PowerPoint, Open Document Format (LibreOffice), arquivos de código
- **OCR Avançado**: Extração de texto de imagens e PDFs escaneados
- **Suporte ao Português**: Modelos otimizados para português brasileiro
- **Análise de Código**: Processamento e análise de arquivos de código
- **GPU/CPU Compatível**: Funciona em GPUs simples e CPUs modernas
- **Notas Automáticas**: Geração de notas em Markdown editáveis
- **Interface Simples**: CLI e API para fácil uso
- **🎯 Sistema Temático**: Separação automática de resumos por temas com audiobooks
- **🎥 Processamento de Vídeos**: Scraping e resumo de vídeos de streaming
- **🎧 Audiobooks**: Geração automática de audiobooks em português
- **📊 Análise Inteligente**: Classificação temática e agrupamento automático

## 📋 Requisitos do Sistema

### Hardware Mínimo
- **CPU**: Processador moderno (Intel i5/AMD Ryzen 5 ou superior)
- **RAM**: 8GB (recomendado 16GB)
- **GPU**: Opcional, mas recomendado (NVIDIA GTX 1060 ou superior)
- **Armazenamento**: 10GB livres

### Software
- Python 3.8 ou superior
- CUDA (opcional, para aceleração GPU)
- Tesseract OCR
- Git

## 🛠️ Instalação

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd localrag
```

### 2. Instale as Dependências do Sistema

#### Ubuntu/Debian:
   ```bash
sudo apt update
sudo apt install python3-pip python3-venv tesseract-ocr tesseract-ocr-por
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
   ```

#### Fedora/CentOS:
   ```bash
sudo dnf install python3-pip python3-venv tesseract tesseract-langpack-por
sudo dnf install mesa-libGL glib2 libSM libXext libXrender libgomp
```

#### Windows:
```bash
# Instale o Tesseract OCR
# Baixe de: https://github.com/UB-Mannheim/tesseract/wiki
# Adicione ao PATH do sistema

# Instale o Visual C++ Redistributable
# Baixe de: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### 3. Configure o Ambiente Python
   ```bash
# Crie um ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Atualize o pip
pip install --upgrade pip

# Instale as dependências
pip install -r requirements.txt
```

### 4. Configure Modelos Adicionais (Opcional)
   ```bash
# Instale modelos spaCy para português
python -m spacy download pt_core_news_sm

# Baixe modelos NLTK
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('portuguese')"
```

## 📁 Estrutura do Projeto

```
localrag/
├── config.py                      # Configurações do sistema
├── document_processor.py           # Processamento de documentos
├── embedding_system.py             # Sistema de embeddings
├── rag_agent.py                   # Agente RAG principal
├── markdown_generator.py          # Gerador de notas Markdown
├── main.py                        # Aplicação principal
├── requirements.txt               # Dependências Python
├── requirements_enhanced.txt      # Dependências do sistema aprimorado
├── README.md                      # Este arquivo
├── documents/                     # Diretório para documentos (criado automaticamente)
├── RAGfiles/                      # Notas geradas (criado automaticamente)
│   ├── temas/                     # Sistema temático
│   │   ├── inteligencia_artificial/
│   │   ├── programacao/
│   │   └── [outros temas...]
│   └── videos/                     # Sistema de vídeos
│       ├── downloads/              # Áudios baixados
│       ├── transcriptions/         # Transcrições
│       ├── summaries/              # Resumos
│       └── audiobooks/            # Audiobooks
├── vector_db/                     # Banco de dados vetorial (criado automaticamente)
├── processors/                     # Processadores especializados
│   └── odf_processor.py           # Processador ODF
├── thematic_analyzer.py           # Analisador temático
├── audio_generator.py              # Gerador de audiobooks
├── thematic_summary_generator.py   # Gerador de resumos temáticos
├── video_processor.py             # Processador de vídeos
├── enhanced_video_processor.py    # Processador avançado de vídeos
├── enhanced_rag_system.py         # Sistema RAG aprimorado
├── enhanced_main.py               # Aplicação principal aprimorada
├── chat_interface.py              # Interface de chat
├── run_enhanced_system.py         # Executor do sistema aprimorado
├── THEMATIC_SYSTEM_DOCS.md        # Documentação do sistema temático
├── VIDEO_SYSTEM_DOCS.md           # Documentação do sistema de vídeos
├── ODF_SUPPORT_DEMO.md            # Documentação do suporte ODF
└── rag_system.log                 # Log do sistema
```

## 🚀 Uso Básico

### 1. Processar Documentos
```bash
# Processar todos os documentos em um diretório
python main.py --mode process --directory /caminho/para/documentos

# Processar recursivamente (padrão)
python main.py --mode process --directory /caminho/para/documentos --recursive

# Especificar idioma
python main.py --mode process --directory /caminho/para/documentos --language pt
```

### 2. Fazer Consultas
```bash
# Fazer uma pergunta
python main.py --mode query --question "Qual é o conceito de machine learning?"

# Consulta em inglês
python main.py --mode query --question "What is machine learning?" --language en

# Limitar contexto
python main.py --mode query --question "Explique algoritmos de classificação" --context-limit 3
```

### 3. Consultas em Lote
```bash
# Criar arquivo de perguntas (questions.json)
echo '{
  "questions": [
    "O que é inteligência artificial?",
    "Explique algoritmos de clustering",
    "Quais são as aplicações de deep learning?"
  ]
}' > questions.json

# Processar consultas em lote
python main.py --mode batch --questions questions.json
```

### 4. Verificar Status do Sistema
```bash
python main.py --mode status
```

### 5. Limpar Sistema
```bash
python main.py --mode clear
```

## 📝 Formatos de Arquivo Suportados

### Documentos de Texto
- `.txt`, `.md`, `.rst`

### PDFs
- PDFs com texto
- PDFs escaneados (com OCR)
- PDFs com tabelas

### Imagens
- `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`
- OCR automático para extração de texto

### Documentos Office
- `.docx`, `.doc` (Word)
- `.pptx`, `.ppt` (PowerPoint)

### Open Document Format (LibreOffice)
- `.odt` (LibreOffice Writer)
- `.ods` (LibreOffice Calc)
- `.odp` (LibreOffice Impress)

### Código
- Python: `.py`
- JavaScript: `.js`, `.ts`
- Java: `.java`
- C/C++: `.c`, `.cpp`, `.h`, `.hpp`
- E muitos outros...

### Vídeos de Streaming
- **YouTube**: youtube.com, youtu.be
- **Vimeo**: vimeo.com
- **Twitch**: twitch.tv
- **TikTok**: tiktok.com
- **Dailymotion**: dailymotion.com
- **Transcrição automática** com Whisper
- **Resumo automático** de vídeos
- **Audiobooks** dos resumos

## 🔧 Configuração Avançada

### Configuração de GPU
Edite `config.py` para ajustar o uso de GPU:

```python
DEVICE_CONFIG = {
    'use_gpu': True,              # Usar GPU se disponível
    'gpu_memory_fraction': 0.8,   # Fração de memória GPU a usar
    'fallback_to_cpu': True,      # Usar CPU se GPU falhar
    'batch_size': 32              # Tamanho do lote para processamento
}
```

### Configuração de Modelos
```python
MODEL_CONFIG = {
    'embedding_model': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    'llm_model': 'microsoft/DialoGPT-medium',
    'portuguese_model': 'neuralmind/bert-base-portuguese-cased',
    'chunk_size': 1000,          # Tamanho dos chunks de texto
    'chunk_overlap': 200          # Sobreposição entre chunks
}
```

### Configuração de Processamento
```python
PROCESSING_CONFIG = {
    'max_file_size_mb': 50,       # Tamanho máximo de arquivo
    'enable_ocr': True,           # Habilitar OCR
    'enable_code_analysis': True, # Análise de código
    'parallel_processing': True,   # Processamento paralelo
    'max_workers': 4             # Número de workers
}
```

## 📊 Notas em Markdown

O sistema gera automaticamente notas em Markdown na pasta `RAGfiles/`:

### Tipos de Notas
1. **Notas de Documentos**: Uma nota por documento processado
2. **Resumo Geral**: Resumo de todos os documentos
3. **Notas de Consulta**: Registro das consultas feitas

### Estrutura das Notas
```markdown
# Notas do Documento: exemplo.pdf

## Informações do Arquivo
- **Caminho do arquivo:** /caminho/arquivo.pdf
- **Tipo de arquivo:** pdf
- **Tamanho:** 2.5 MB
- **Modificado em:** 2024-01-15T10:30:00

## Conteúdo Extraído
[Conteúdo extraído do documento...]

## Análise de Código
[Se for arquivo de código...]

## Tabelas Extraídas
[Se houver tabelas...]

## Estatísticas
- **Número de palavras:** 1500
- **Número de caracteres:** 8500
- **Idioma detectado:** pt
```

## 🔍 Exemplos de Uso

### Exemplo 1: Processar Documentos de Curso
```bash
# Processar todos os documentos de um curso
python main.py --mode process --directory /home/usuario/curso_ia --language pt

# Fazer perguntas sobre o conteúdo
python main.py --mode query --question "Quais são os principais algoritmos de machine learning?"
```

### Exemplo 2: Análise de Código
```bash
# Processar código Python
python main.py --mode process --directory /home/usuario/projetos_python

# Perguntar sobre o código
python main.py --mode query --question "Como funciona a função de classificação?"
```

### Exemplo 3: OCR de Imagens
```bash
# Processar imagens com texto
python main.py --mode process --directory /home/usuario/notas_escaneadas

# Consultar texto extraído
python main.py --mode query --question "Qual é a fórmula matemática mencionada?"
```

### Exemplo 4: Documentos LibreOffice (ODF)
```bash
# Processar documentos ODT, ODS, ODP
python main.py --mode process --directory /home/usuario/documentos_libreoffice

# Consultar conteúdo de planilhas e apresentações
python main.py --mode query --question "Quais são os dados da planilha de vendas?"
python main.py --mode query --question "Resuma os pontos principais da apresentação"
```

### Exemplo 5: Sistema Temático com Audiobooks
```bash
# Processar documentos com análise temática
python enhanced_main.py --mode process --thematic

# Gerar audiobooks por tema
python enhanced_main.py --mode audiobooks

# Chat com sistema temático
python enhanced_main.py --mode chat
```

### Exemplo 6: Processamento de Vídeos
```bash
# Processar documentos com vídeos
python enhanced_main.py --mode process --videos

# Transcrição e resumo de vídeos
python enhanced_main.py --mode videos

# Gerar audiobooks de vídeos
python enhanced_main.py --mode video-audiobooks
```

## 🎯 Sistema Temático e Audiobooks

### **Funcionalidades Temáticas**
- **Análise automática** de temas (IA, Programação, Matemática, etc.)
- **Separação inteligente** de documentos por tema
- **Resumos temáticos** em Markdown
- **Audiobooks em português** para cada tema
- **Estrutura organizacional** por temas

### **Temas Suportados**
- **Inteligência Artificial**: IA, Machine Learning, Deep Learning
- **Programação**: Código, Python, JavaScript, Algoritmos
- **Matemática**: Cálculo, Álgebra, Estatística, Probabilidade
- **Física**: Mecânica, Termodinâmica, Eletromagnetismo
- **Química**: Moléculas, Reações, Tabela Periódica
- **Biologia**: Células, DNA, Genética, Evolução
- **História**: Passado, Civilizações, Guerras, Revoluções
- **Literatura**: Livros, Poesia, Autores, Narrativas
- **Economia**: Mercado, Capital, Investimentos, Finanças
- **Filosofia**: Ética, Moral, Lógica, Conhecimento

## 🎥 Sistema de Processamento de Vídeos

### **Plataformas Suportadas**
- **YouTube**: youtube.com, youtu.be
- **Vimeo**: vimeo.com
- **Twitch**: twitch.tv
- **TikTok**: tiktok.com
- **Dailymotion**: dailymotion.com

### **Funcionalidades de Vídeo**
- **Detecção automática** de URLs de vídeo
- **Download de áudio** com yt-dlp
- **Transcrição com Whisper** em português
- **Resumo automático** de vídeos
- **Geração de audiobooks** dos resumos
- **Agrupamento temático** de vídeos

## 🐛 Solução de Problemas

### Problema: Erro de GPU
```bash
# Desabilitar GPU no config.py
DEVICE_CONFIG = {'use_gpu': False}
```

### Problema: OCR não funciona
```bash
# Verificar instalação do Tesseract
tesseract --version

# Instalar idiomas adicionais
sudo apt install tesseract-ocr-por tesseract-ocr-eng
```

### Problema: Modelos não carregam
```bash
# Verificar conexão com internet
# Baixar modelos manualmente se necessário
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')"
```

### Problema: Memória insuficiente
```bash
# Reduzir batch_size no config.py
DEVICE_CONFIG = {'batch_size': 16}
```

## 📈 Performance

### Otimizações Recomendadas
1. **Use GPU**: Acelera significativamente o processamento
2. **Ajuste batch_size**: Baseado na sua GPU/RAM
3. **Processamento paralelo**: Habilite para múltiplos arquivos
4. **Chunk size**: Ajuste baseado no tipo de documento

### Benchmarks Aproximados
- **CPU**: ~10-20 documentos/minuto
- **GPU**: ~50-100 documentos/minuto
- **RAM**: ~2-4GB para 1000 documentos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença GPL-3.0. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
1. Abra uma issue no GitHub
2. Consulte a documentação
3. Verifique os logs em `rag_system.log`

## 🔄 Atualizações

Para atualizar o sistema:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 📚 Recursos Adicionais

### **Documentação do Sistema**
- [Sistema Temático](THEMATIC_SYSTEM_DOCS.md) - Documentação completa do sistema temático
- [Sistema de Vídeos](VIDEO_SYSTEM_DOCS.md) - Documentação do processamento de vídeos
- [Suporte ODF](ODF_SUPPORT_DEMO.md) - Documentação do suporte a LibreOffice

### **Bibliotecas e Frameworks**
- [Documentação do LangChain](https://python.langchain.com/)
- [Documentação do ChromaDB](https://docs.trychroma.com/)
- [Documentação do Sentence Transformers](https://www.sbert.net/)
- [Tesseract OCR](https://tesseract-ocr.github.io/)
- [Whisper AI](https://github.com/openai/whisper) - Transcrição de áudio
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Download de vídeos
- [pyttsx3](https://pyttsx3.readthedocs.io/) - Síntese de voz

---

**Desenvolvido para processamento inteligente de documentos universitários com foco em português brasileiro e análise multimodal.**