#!/usr/bin/env python3
"""
Interface Streamlit para Fine-Tuning com Ollama
Sistema completo de treinamento de modelos customizados
"""

import streamlit as st
import json
import sqlite3
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime
import PyPDF2
from docx import Document
import re

# Configurações
DOCUMENTS_DIR = Path("/home/lsantann/Documents/CC/")
FINE_TUNING_DIR = Path("/home/lsantann/dev/localRAGsummary/fine_tuning")
OLLAMA_BASE_URL = "http://localhost:11434"

# Criar diretórios
FINE_TUNING_DIR.mkdir(exist_ok=True)
(FINE_TUNING_DIR / "data").mkdir(exist_ok=True)
(FINE_TUNING_DIR / "models").mkdir(exist_ok=True)
(FINE_TUNING_DIR / "modelfiles").mkdir(exist_ok=True)

class FineTuningInterface:
    def __init__(self):
        self.documents_dir = DOCUMENTS_DIR
        self.output_dir = FINE_TUNING_DIR
        
    def extract_document_content(self, file_path):
        """Extrai conteúdo de documentos"""
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
                return None
                
        except Exception as e:
            return None
    
    def create_instruction_pairs(self, content, file_name):
        """Cria pares de instrução-resposta"""
        pairs = []
        
        # Dividir conteúdo em chunks
        chunks = self.split_content(content, max_length=1000)
        
        for chunk in chunks:
            if len(chunk.strip()) < 50:
                continue
                
            instructions = [
                f"Explique o conteúdo do documento {file_name}",
                f"Resuma as informações de {file_name}",
                f"Quais são os principais pontos de {file_name}?",
                f"Descreva o que está no arquivo {file_name}",
                f"Analise o conteúdo de {file_name}"
            ]
            
            for instruction in instructions:
                pairs.append({
                    "instruction": instruction,
                    "input": "",
                    "output": chunk.strip()
                })
        
        return pairs
    
    def split_content(self, content, max_length=1000):
        """Divide conteúdo em chunks"""
        chunks = []
        sentences = re.split(r'[.!?]\s+', content)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk + sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def prepare_training_data(self, selected_files):
        """Prepara dados de treinamento"""
        all_pairs = []
        processed_files = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file_path in enumerate(selected_files):
            status_text.text(f"Processando: {Path(file_path).name}")
            progress_bar.progress((i + 1) / len(selected_files))
            
            content = self.extract_document_content(file_path)
            if content and len(content.strip()) > 100:
                pairs = self.create_instruction_pairs(content, Path(file_path).name)
                all_pairs.extend(pairs)
                processed_files += 1
        
        # Salvar dados
        jsonl_path = self.output_dir / "data" / "training_data.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
        
        json_path = self.output_dir / "data" / "training_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_pairs, f, ensure_ascii=False, indent=2)
        
        progress_bar.empty()
        status_text.empty()
        
        return jsonl_path, len(all_pairs), processed_files
    
    def create_modelfile(self, base_model, custom_name, system_prompt):
        """Cria Modelfile"""
        modelfile_content = f"""FROM {base_model}

SYSTEM {system_prompt}

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER repeat_penalty 1.1
"""
        
        modelfile_path = self.output_dir / "modelfiles" / f"{custom_name}.Modelfile"
        with open(modelfile_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        return modelfile_path
    
    def create_training_script(self, model_name, num_epochs, learning_rate):
        """Cria script de treinamento"""
        script_content = f'''#!/usr/bin/env python3
"""
Script de Fine-Tuning com Unsloth
Execute no Google Colab ou ambiente com GPU
"""

import json
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset

# Configurações
base_model = "{model_name}"
max_seq_length = 2048
dtype = None
load_in_4bit = True

# Carregar modelo
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=base_model,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# Configurar LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

# Carregar dados
def load_training_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

training_data = load_training_data("training_data.jsonl")
dataset = Dataset.from_list(training_data)

# Configurar treinamento
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="output",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps={num_epochs * 10},
        learning_rate={learning_rate},
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
    ),
)

# Treinar
trainer_stats = trainer.train()

# Salvar modelo
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")

print("✅ Fine-tuning concluído!")
'''
        
        script_path = self.output_dir / "train_model.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path
    
    def check_ollama_connection(self):
        """Verifica conexão com Ollama"""
        try:
            import requests
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Obtém modelos disponíveis"""
        try:
            import requests
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
        except:
            pass
        return []
    
    def create_ollama_model(self, modelfile_path, model_name):
        """Cria modelo Ollama"""
        try:
            result = subprocess.run([
                "ollama", "create", model_name, "-f", str(modelfile_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Modelo criado com sucesso!"
            else:
                return False, f"Erro: {result.stderr}"
        except Exception as e:
            return False, f"Erro: {e}"

def main():
    st.set_page_config(
        page_title="Fine-Tuning com Ollama",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Sistema de Fine-Tuning com Ollama")
    st.markdown("**Treine modelos customizados com seus documentos universitários**")
    
    # Inicializar interface
    if 'ft_interface' not in st.session_state:
        st.session_state['ft_interface'] = FineTuningInterface()
    
    ft_interface = st.session_state['ft_interface']
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Status Ollama
        if ft_interface.check_ollama_connection():
            st.success("✅ Ollama Conectado")
        else:
            st.error("❌ Ollama Desconectado")
            st.info("Execute: `ollama serve`")
        
        # Modelos disponíveis
        available_models = ft_interface.get_available_models()
        if available_models:
            st.subheader("🧠 Modelos Base")
            for model in available_models[:5]:  # Mostrar apenas os primeiros 5
                st.text(f"• {model}")
        
        st.divider()
        
        # Estatísticas
        st.subheader("📊 Estatísticas")
        if (ft_interface.output_dir / "data" / "training_data.jsonl").exists():
            with open(ft_interface.output_dir / "data" / "training_data.jsonl", 'r') as f:
                num_lines = sum(1 for _ in f)
            st.metric("Pares de Treinamento", num_lines)
        else:
            st.metric("Pares de Treinamento", 0)
    
    # Área principal
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Preparar Dados", "⚙️ Configurar Treinamento", "🚀 Executar Treinamento", "📊 Resultados"])
    
    with tab1:
        st.header("📚 Preparação de Dados")
        
        # Seleção de arquivos
        st.subheader("Selecionar Arquivos para Treinamento")
        
        # Listar arquivos disponíveis
        available_files = []
        if ft_interface.documents_dir.exists():
            for file_path in ft_interface.documents_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.pdf', '.docx', '.py', '.js', '.html']:
                    available_files.append(str(file_path))
        
        if available_files:
            selected_files = st.multiselect(
                "Escolha os arquivos:",
                available_files,
                default=available_files[:5] if len(available_files) > 5 else available_files,
                format_func=lambda x: Path(x).name
            )
            
            if selected_files:
                st.info(f"Selecionados: {len(selected_files)} arquivos")
                
                if st.button("🔄 Preparar Dados de Treinamento", type="primary"):
                    with st.spinner("Preparando dados..."):
                        jsonl_path, num_pairs, processed_files = ft_interface.prepare_training_data(selected_files)
                        
                        st.success(f"✅ Dados preparados!")
                        st.metric("Arquivos Processados", processed_files)
                        st.metric("Pares de Treinamento", num_pairs)
                        
                        # Mostrar preview dos dados
                        with st.expander("📄 Preview dos Dados"):
                            with open(jsonl_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()[:3]  # Primeiras 3 linhas
                                for i, line in enumerate(lines):
                                    data = json.loads(line)
                                    st.json(data)
        else:
            st.warning("Nenhum arquivo encontrado no diretório de documentos")
    
    with tab2:
        st.header("⚙️ Configuração do Treinamento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Modelo Base")
            base_model = st.selectbox(
                "Escolha o modelo base:",
                ["llama3.2", "llama3.1", "mistral", "codellama", "phi3"],
                index=0
            )
            
            st.subheader("Parâmetros de Treinamento")
            num_epochs = st.slider("Épocas", 1, 10, 3)
            learning_rate = st.selectbox(
                "Taxa de Aprendizado:",
                [1e-4, 2e-4, 5e-4, 1e-3],
                index=1
            )
        
        with col2:
            st.subheader("Modelo Customizado")
            custom_name = st.text_input(
                "Nome do modelo:",
                value="universitario-custom",
                help="Nome que será usado no Ollama"
            )
            
            st.subheader("Prompt do Sistema")
            system_prompt = st.text_area(
                "Prompt do sistema:",
                value="""Você é um assistente especializado em documentos universitários. Você tem conhecimento profundo sobre:
- Conceitos acadêmicos e científicos
- Metodologias de pesquisa
- Análise de dados e estatística
- Programação e tecnologia
- Documentos técnicos e científicos

Sempre responda de forma precisa, detalhada e acadêmica, baseando-se no contexto dos documentos fornecidos.""",
                height=150
            )
        
        if st.button("📝 Gerar Scripts de Treinamento", type="primary"):
            # Criar Modelfile
            modelfile_path = ft_interface.create_modelfile(base_model, custom_name, system_prompt)
            
            # Criar script de treinamento
            script_path = ft_interface.create_training_script(base_model, num_epochs, learning_rate)
            
            st.success("✅ Scripts gerados!")
            st.info(f"Modelfile: {modelfile_path}")
            st.info(f"Script: {script_path}")
    
    with tab3:
        st.header("🚀 Executar Treinamento")
        
        st.warning("⚠️ **Atenção**: O treinamento deve ser executado em ambiente com GPU (Google Colab recomendado)")
        
        # Verificar se os dados estão prontos
        data_file = ft_interface.output_dir / "data" / "training_data.jsonl"
        if data_file.exists():
            st.success("✅ Dados de treinamento prontos")
            
            # Instruções para Google Colab
            st.subheader("📋 Instruções para Google Colab")
            
            colab_code = f'''
# 1. Instalar dependências
!pip install unsloth transformers datasets trl

# 2. Fazer upload dos dados
# Faça upload do arquivo training_data.jsonl

# 3. Executar treinamento
!python train_model.py

# 4. Baixar modelo treinado
# Baixe a pasta lora_model/
'''
            
            st.code(colab_code, language="python")
            
            # Botão para baixar dados
            if st.button("📥 Baixar Dados de Treinamento"):
                st.download_button(
                    label="Download training_data.jsonl",
                    data=open(data_file, 'rb').read(),
                    file_name="training_data.jsonl",
                    mime="application/json"
                )
        
        else:
            st.error("❌ Dados de treinamento não encontrados")
            st.info("Execute primeiro a preparação de dados na aba anterior")
    
    with tab4:
        st.header("📊 Resultados e Testes")
        
        # Listar modelos Ollama
        st.subheader("🧠 Modelos Ollama Disponíveis")
        
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                st.code(result.stdout)
            else:
                st.error("Erro ao listar modelos")
        except:
            st.error("Ollama não encontrado")
        
        # Testar modelo customizado
        st.subheader("🧪 Testar Modelo Customizado")
        
        test_question = st.text_input(
            "Pergunta de teste:",
            value="Explique os conceitos de inteligência artificial"
        )
        
        model_name = st.text_input(
            "Nome do modelo:",
            value="universitario-custom"
        )
        
        if st.button("🚀 Testar Modelo"):
            try:
                result = subprocess.run([
                    "ollama", "run", model_name, test_question
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    st.success("✅ Modelo funcionando!")
                    st.text_area("Resposta:", result.stdout, height=200)
                else:
                    st.error(f"❌ Erro: {result.stderr}")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
        
        # Criar modelo Ollama
        st.subheader("🔧 Criar Modelo Ollama")
        
        modelfile_path = ft_interface.output_dir / "modelfiles" / f"{model_name}.Modelfile"
        
        if modelfile_path.exists():
            st.success("✅ Modelfile encontrado")
            
            if st.button("🏗️ Criar Modelo no Ollama"):
                success, message = ft_interface.create_ollama_model(modelfile_path, model_name)
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
        else:
            st.warning("⚠️ Modelfile não encontrado")
            st.info("Execute primeiro a configuração do treinamento")

if __name__ == "__main__":
    main()
