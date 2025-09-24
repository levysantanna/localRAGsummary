#!/usr/bin/env python3
"""
Exemplo de Uso do Sistema Temático com Audiobooks
"""
import sys
from pathlib import Path
import logging

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from thematic_summary_generator import ThematicSummaryGenerator
from document_processor import DocumentProcessor
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def exemplo_sistema_tematico():
    """Exemplo de uso do sistema temático"""
    
    print("🎯 Exemplo de Uso do Sistema Temático com Audiobooks")
    print("=" * 60)
    
    try:
        # 1. Inicializa o sistema
        print("\n🔧 Passo 1: Inicializando sistema temático...")
        
        thematic_generator = ThematicSummaryGenerator()
        document_processor = DocumentProcessor()
        
        print("  ✅ Sistema temático inicializado")
        
        # 2. Processa documentos de exemplo
        print("\n📄 Passo 2: Processando documentos de exemplo...")
        
        # Cria documentos de exemplo
        example_documents = create_example_documents()
        
        print(f"  ✅ {len(example_documents)} documentos de exemplo criados")
        
        # 3. Processa documentos tematicamente
        print("\n🎯 Passo 3: Processando documentos tematicamente...")
        
        result = thematic_generator.process_documents_thematically(example_documents)
        
        if result['success']:
            print("  ✅ Processamento temático concluído com sucesso")
            
            # Mostra estatísticas
            stats = result['stats']
            print(f"  📊 Estatísticas:")
            print(f"    - Documentos processados: {stats['total_documents']}")
            print(f"    - Temas identificados: {stats['total_themes']}")
            print(f"    - Resumos gerados: {stats['successful_summaries']}")
            print(f"    - Audiobooks gerados: {stats['successful_audiobooks']}")
            
            # Mostra temas identificados
            thematic_groups = result['thematic_groups']
            print(f"\n  🎯 Temas identificados:")
            for theme, docs in thematic_groups.items():
                print(f"    - {theme}: {len(docs)} documentos")
            
            # Mostra estrutura criada
            thematic_dirs = result['thematic_dirs']
            print(f"\n  📁 Estrutura criada:")
            for theme, theme_dir in thematic_dirs.items():
                print(f"    - {theme}: {theme_dir}")
            
        else:
            print(f"  ❌ Erro no processamento: {result.get('error')}")
            return False
        
        # 4. Mostra resultados
        print("\n📋 Passo 4: Mostrando resultados...")
        
        print(f"  📄 Resumo geral: {result['general_summary_path']}")
        
        # Mostra resumos temáticos
        summary_results = result['summary_results']
        print(f"\n  📚 Resumos temáticos gerados:")
        for theme, summary_info in summary_results.items():
            if summary_info['success']:
                print(f"    - {theme}: {summary_info['summary_path']}")
        
        # Mostra audiobooks
        audiobook_results = result['audiobook_results']
        print(f"\n  🎧 Audiobooks gerados:")
        for theme, audio_info in audiobook_results.items():
            if audio_info['success']:
                print(f"    - {theme}: {audio_info['output_path']}")
            else:
                print(f"    - {theme}: Erro - {audio_info.get('error')}")
        
        # 5. Resumo final
        print(f"\n🎉 Sistema Temático com Audiobooks Funcionando!")
        print("=" * 60)
        print(f"✅ Análise temática automática")
        print(f"✅ Separação de documentos por temas")
        print(f"✅ Geração de resumos temáticos")
        print(f"✅ Geração de audiobooks em português")
        print(f"✅ Estrutura organizacional por temas")
        print(f"✅ Estatísticas detalhadas")
        
        print(f"\n🚀 Funcionalidades implementadas:")
        print(f"  🎯 Classificação automática de temas")
        print(f"  📚 Agrupamento de documentos por tema")
        print(f"  📄 Resumos temáticos em Markdown")
        print(f"  🎧 Audiobooks em português (MP3)")
        print(f"  📁 Estrutura organizacional")
        print(f"  📊 Análise de confiança temática")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in thematic system example: {e}")
        print(f"❌ Erro no exemplo: {e}")
        return False

def create_example_documents():
    """Cria documentos de exemplo para demonstração"""
    try:
        documents = []
        
        # Documento sobre IA
        ia_doc = {
            'file_path': 'documents/curso_ia.txt',
            'content': {
                'text': '''
                Curso de Inteligência Artificial - Universidade

                Módulo 1: Fundamentos da Inteligência Artificial
                A Inteligência Artificial (IA) é um campo da ciência da computação que se dedica à criação de sistemas capazes de realizar tarefas que normalmente requerem inteligência humana.

                Conceitos fundamentais:
                - Algoritmos inteligentes
                - Aprendizado de máquina
                - Processamento de linguagem natural
                - Visão computacional
                - Sistemas especialistas

                Módulo 2: Machine Learning
                Machine Learning é um subcampo da IA que permite aos sistemas aprenderem e melhorarem automaticamente através da experiência, sem serem explicitamente programados.

                Algoritmos principais:
                - Regressão Linear
                - Árvores de Decisão
                - Random Forest
                - Support Vector Machines
                - Redes Neurais
                '''
            },
            'metadata': {
                'filename': 'curso_ia.txt',
                'size_bytes': 1500
            }
        }
        documents.append(ia_doc)
        
        # Documento sobre programação
        prog_doc = {
            'file_path': 'documents/algoritmos_ml.txt',
            'content': {
                'text': '''
                Algoritmos de Machine Learning - Guia Completo

                1. Algoritmos de Classificação
                Regressão Logística: Usado para classificação binária e multiclasse, baseado em probabilidades.

                Árvores de Decisão: Fáceis de interpretar com regras if-then, não requerem normalização.

                Random Forest: Combinação de múltiplas árvores que reduz overfitting através de bagging.

                SVM: Encontra o hiperplano de separação ótimo, funciona bem em espaços de alta dimensão.

                2. Algoritmos de Regressão
                Regressão Linear: Para previsão de valores contínuos.

                Ridge Regression: Adiciona regularização L2 para reduzir overfitting.

                Lasso Regression: Adiciona regularização L1 para seleção de features.
                '''
            },
            'metadata': {
                'filename': 'algoritmos_ml.txt',
                'size_bytes': 2000
            }
        }
        documents.append(prog_doc)
        
        # Documento sobre matemática
        math_doc = {
            'file_path': 'documents/deep_learning.txt',
            'content': {
                'text': '''
                Deep Learning e Redes Neurais - Fundamentos e Aplicações

                1. Introdução ao Deep Learning
                Deep Learning é um subcampo do Machine Learning que utiliza redes neurais artificiais com múltiplas camadas para aprender representações hierárquicas dos dados.

                2. Arquiteturas de Redes Neurais
                Perceptron Multicamadas (MLP): Múltiplas camadas densas para classificação e regressão.

                Redes Neurais Convolucionais (CNN): Especializadas em dados espaciais como imagens.

                Redes Neurais Recorrentes (RNN): Para processar sequências temporais.

                Transformers: Arquitetura baseada em atenção para processamento de linguagem natural.

                3. Aplicações Práticas
                Visão Computacional: Classificação de imagens, detecção de objetos.

                Processamento de Linguagem Natural: Tradução, sumarização, chatbots.

                Reconhecimento de Fala: Conversão de fala para texto.
                '''
            },
            'metadata': {
                'filename': 'deep_learning.txt',
                'size_bytes': 1800
            }
        }
        documents.append(math_doc)
        
        return documents
        
    except Exception as e:
        logger.error(f"Error creating example documents: {e}")
        return []

def main():
    """Função principal"""
    print("🧪 Iniciando exemplo do sistema temático...")
    
    # Executa exemplo
    success = exemplo_sistema_tematico()
    
    if success:
        print("\n✅ Exemplo do sistema temático concluído com sucesso!")
        print("🎉 Sistema temático com audiobooks funcionando!")
    else:
        print("\n❌ Exemplo falhou. Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
