#!/usr/bin/env python3
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
