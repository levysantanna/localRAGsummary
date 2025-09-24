#!/usr/bin/env python3
"""
Quick Start Script for Local RAG System
This script provides an easy way to get started with the system
"""
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("🎯 Local RAG System - Quick Start")
    print("=" * 50)
    print("Sistema RAG Local para Documentos Universitários")
    print("Com suporte completo ao português brasileiro")
    print("=" * 50)

def check_requirements():
    """Check if basic requirements are met"""
    print("\n🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} found")
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("⚠️  Virtual environment not found")
        print("   Run: ./install.sh or python -m venv venv")
        return False
    
    print("✅ Virtual environment found")
    return True

def activate_venv():
    """Activate virtual environment"""
    if sys.platform == "win32":
        activate_script = Path("venv/Scripts/activate.bat")
    else:
        activate_script = Path("venv/bin/activate")
    
    if activate_script.exists():
        print("✅ Virtual environment activated")
        return True
    else:
        print("❌ Virtual environment activation script not found")
        return False

def create_sample_documents():
    """Create sample documents for testing"""
    print("\n📁 Creating sample documents...")
    
    # Create documents directory
    docs_dir = Path("documents")
    docs_dir.mkdir(exist_ok=True)
    
    # Sample course document
    sample_course = docs_dir / "curso_ia.txt"
    with open(sample_course, "w", encoding="utf-8") as f:
        f.write("""
Curso de Inteligência Artificial - Universidade

Módulo 1: Fundamentos da IA
============================

1.1 Definição de Inteligência Artificial
A Inteligência Artificial (IA) é um campo da ciência da computação que se dedica 
à criação de sistemas capazes de realizar tarefas que normalmente requerem 
inteligência humana.

1.2 História da IA
- 1950: Teste de Turing
- 1956: Conferência de Dartmouth
- 1960s: Primeiros sistemas especialistas
- 1980s: Redes neurais artificiais
- 2000s: Deep Learning e Big Data

Módulo 2: Machine Learning
==========================

2.1 Tipos de Aprendizado
- Supervised Learning: Aprendizado supervisionado com dados rotulados
- Unsupervised Learning: Aprendizado não supervisionado sem rótulos
- Reinforcement Learning: Aprendizado por reforço através de recompensas

2.2 Algoritmos Principais
- Regressão Linear
- Árvores de Decisão
- Random Forest
- Support Vector Machines (SVM)
- K-Means Clustering

Módulo 3: Deep Learning
=======================

3.1 Redes Neurais Artificiais
- Perceptron
- Perceptron Multicamadas (MLP)
- Redes Neurais Convolucionais (CNN)
- Redes Neurais Recorrentes (RNN)
- Transformers

3.2 Aplicações
- Visão Computacional
- Processamento de Linguagem Natural (NLP)
- Reconhecimento de Fala
- Sistemas de Recomendação

Conceitos Importantes:
=====================

- Overfitting: Quando o modelo se ajusta demais aos dados de treinamento
- Underfitting: Quando o modelo é muito simples para os dados
- Cross-validation: Técnica para avaliar a performance do modelo
- Feature Engineering: Processo de seleção e transformação de características

Referências:
============
- Russell, S. & Norvig, P. (2020). Artificial Intelligence: A Modern Approach
- Goodfellow, I. et al. (2016). Deep Learning
- Mitchell, T. (2017). Machine Learning
""")
    
    # Sample code document
    sample_code = docs_dir / "exemplo_ml.py"
    with open(sample_code, "w", encoding="utf-8") as f:
        f.write("""
"""
Exemplo de Machine Learning em Python
Implementação de classificação usando scikit-learn
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.datasets import load_iris

def load_data():
    '''Carrega o dataset Iris'''
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    target_names = iris.target_names
    
    return X, y, feature_names, target_names

def train_model(X_train, y_train):
    '''Treina o modelo Random Forest'''
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=3
    )
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    '''Avalia o modelo'''
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Acurácia: {accuracy:.2f}")
    print("\\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred))
    
    return accuracy

def main():
    '''Função principal'''
    print("=== Exemplo de Machine Learning ===")
    
    # Carregar dados
    X, y, feature_names, target_names = load_data()
    print(f"Dataset carregado: {X.shape[0]} amostras, {X.shape[1]} características")
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Treinar modelo
    model = train_model(X_train, y_train)
    
    # Avaliar modelo
    accuracy = evaluate_model(model, X_test, y_test)
    
    # Mostrar importância das características
    feature_importance = model.feature_importances_
    print("\\nImportância das Características:")
    for name, importance in zip(feature_names, feature_importance):
        print(f"{name}: {importance:.3f}")

if __name__ == "__main__":
    main()
""")
    
    print(f"✅ Created sample documents in {docs_dir}")
    return True

def run_quick_test():
    """Run a quick test of the system"""
    print("\n🧪 Running quick test...")
    
    try:
        # Import and test basic functionality
        from main import LocalRAGSystem
        
        # Initialize system
        print("Initializing RAG system...")
        rag_system = LocalRAGSystem()
        
        # Check status
        status = rag_system.get_system_status()
        print(f"✅ System initialized. Status: {status['system_ready']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n🎉 Quick Start Completed!")
    print("\n📋 Next Steps:")
    print("1. Process your documents:")
    print("   python main.py --mode process --directory documents")
    print("\n2. Query your documents:")
    print("   python main.py --mode query --question 'O que é machine learning?'")
    print("\n3. Check generated notes in the 'RAGfiles' directory")
    print("\n4. For more examples, run:")
    print("   python example_usage.py")
    print("\n📚 For detailed documentation, see README.md")

def main():
    """Main quick start function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please run ./install.sh first")
        return
    
    # Activate virtual environment
    if not activate_venv():
        print("\n❌ Cannot activate virtual environment")
        return
    
    # Create sample documents
    create_sample_documents()
    
    # Run quick test
    if run_quick_test():
        show_next_steps()
    else:
        print("\n❌ Quick test failed. Please check the installation.")
        print("Run: ./install.sh to reinstall dependencies")

if __name__ == "__main__":
    main()
