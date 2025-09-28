#!/usr/bin/env python3
"""
Sistema de Fine-Tuning com Ollama
Prepara dados e cria modelos customizados
"""

import json
import sqlite3
import os
from pathlib import Path
import PyPDF2
from docx import Document
import re
from datetime import datetime
import subprocess
import shutil

class FineTuningSystem:
    def __init__(self, documents_dir="/home/lsantann/Documents/CC/", 
                 output_dir="/home/lsantann/dev/localRAGsummary/fine_tuning"):
        self.documents_dir = Path(documents_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Criar subdiretórios
        (self.output_dir / "data").mkdir(exist_ok=True)
        (self.output_dir / "models").mkdir(exist_ok=True)
        (self.output_dir / "modelfiles").mkdir(exist_ok=True)
        
    def extract_document_content(self, file_path):
        """Extrai conteúdo de documentos para treinamento"""
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
            print(f"Erro ao processar {file_path}: {e}")
            return None
    
    def create_instruction_pairs(self, content, file_name):
        """Cria pares de instrução-resposta para fine-tuning"""
        pairs = []
        
        # Dividir conteúdo em chunks menores
        chunks = self.split_content(content, max_length=1000)
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:  # Pular chunks muito pequenos
                continue
                
            # Criar diferentes tipos de instruções
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
        """Divide conteúdo em chunks menores"""
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
    
    def prepare_training_data(self):
        """Prepara dados de treinamento dos documentos"""
        print("📚 Preparando dados de treinamento...")
        
        all_pairs = []
        processed_files = 0
        
        # Processar todos os arquivos do diretório
        for file_path in self.documents_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.pdf', '.docx', '.py', '.js', '.html']:
                print(f"Processando: {file_path.name}")
                
                content = self.extract_document_content(file_path)
                if content and len(content.strip()) > 100:
                    pairs = self.create_instruction_pairs(content, file_path.name)
                    all_pairs.extend(pairs)
                    processed_files += 1
        
        print(f"✅ Processados {processed_files} arquivos")
        print(f"✅ Gerados {len(all_pairs)} pares de treinamento")
        
        # Salvar dados em formato JSONL
        jsonl_path = self.output_dir / "data" / "training_data.jsonl"
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')
        
        # Salvar também em formato JSON para análise
        json_path = self.output_dir / "data" / "training_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_pairs, f, ensure_ascii=False, indent=2)
        
        return jsonl_path, len(all_pairs)
    
    def create_modelfile(self, base_model="llama3.2", custom_name="universitario-custom"):
        """Cria Modelfile para modelo customizado"""
        modelfile_content = f"""FROM {base_model}

SYSTEM Você é um assistente especializado em documentos universitários. Você tem conhecimento profundo sobre:
- Conceitos acadêmicos e científicos
- Metodologias de pesquisa
- Análise de dados e estatística
- Programação e tecnologia
- Documentos técnicos e científicos

Sempre responda de forma precisa, detalhada e acadêmica, baseando-se no contexto dos documentos fornecidos.

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER repeat_penalty 1.1
"""
        
        modelfile_path = self.output_dir / "modelfiles" / f"{custom_name}.Modelfile"
        with open(modelfile_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        return modelfile_path
    
    def create_training_script(self):
        """Cria script para fine-tuning com Unsloth"""
        script_content = '''#!/usr/bin/env python3
"""
Script de Fine-Tuning com Unsloth
Execute este script no Google Colab ou ambiente com GPU
"""

import json
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset

# Configurações
model_name = "unsloth/llama-3-8b-bnb-4bit"  # Modelo base
max_seq_length = 2048
dtype = None  # Auto-detect
load_in_4bit = True

# Carregar modelo
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
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

# Carregar dados de treinamento
def load_training_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

# Preparar dataset
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
        max_steps=100,
        learning_rate=2e-4,
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

# Treinar modelo
trainer_stats = trainer.train()

# Salvar modelo
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")

print("✅ Fine-tuning concluído!")
print("📁 Modelo salvo em: lora_model/")
'''
        
        script_path = self.output_dir / "train_model.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return script_path
    
    def create_conversion_script(self):
        """Cria script para converter modelo para GGUF"""
        script_content = '''#!/bin/bash
"""
Script para converter modelo fine-tuned para GGUF
Execute após o fine-tuning
"""

# Instalar dependências
pip install llama.cpp

# Converter para GGUF
python -m llama_cpp.llama_convert_hf_to_gguf \\
    --outfile modelo_customizado.gguf \\
    --outtype f16 \\
    --model-dir lora_model

echo "✅ Conversão concluída!"
echo "📁 Arquivo GGUF: modelo_customizado.gguf"
'''
        
        script_path = self.output_dir / "convert_to_gguf.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        return script_path
    
    def create_ollama_model(self, modelfile_path, model_name="universitario-custom"):
        """Cria modelo Ollama a partir do Modelfile"""
        try:
            # Criar modelo no Ollama
            result = subprocess.run([
                "ollama", "create", model_name, "-f", str(modelfile_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Modelo '{model_name}' criado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao criar modelo: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def test_custom_model(self, model_name="universitario-custom"):
        """Testa modelo customizado"""
        try:
            result = subprocess.run([
                "ollama", "run", model_name, "Olá, como você pode me ajudar com documentos universitários?"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Modelo funcionando!")
                print(f"Resposta: {result.stdout}")
                return True
            else:
                print(f"❌ Erro no teste: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def generate_training_report(self, num_pairs):
        """Gera relatório do processo de treinamento"""
        report = f"""# Relatório de Fine-Tuning

## 📊 Estatísticas
- **Pares de treinamento**: {num_pairs}
- **Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- **Diretório**: {self.documents_dir}

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
"""
        
        report_path = self.output_dir / "TRAINING_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_path

def main():
    """Função principal"""
    print("🤖 Sistema de Fine-Tuning com Ollama")
    print("=" * 50)
    
    # Inicializar sistema
    ft_system = FineTuningSystem()
    
    # Preparar dados
    jsonl_path, num_pairs = ft_system.prepare_training_data()
    
    # Criar Modelfile
    modelfile_path = ft_system.create_modelfile()
    
    # Criar scripts
    training_script = ft_system.create_training_script()
    conversion_script = ft_system.create_conversion_script()
    
    # Gerar relatório
    report_path = ft_system.generate_training_report(num_pairs)
    
    print(f"\n✅ Preparação concluída!")
    print(f"📁 Diretório: {ft_system.output_dir}")
    print(f"📊 Pares de treinamento: {num_pairs}")
    print(f"📄 Relatório: {report_path}")
    
    print(f"\n🚀 Próximos passos:")
    print(f"1. Execute: python {training_script}")
    print(f"2. Execute: bash {conversion_script}")
    print(f"3. Crie modelo: ollama create universitario-custom -f {modelfile_path}")

if __name__ == "__main__":
    main()
