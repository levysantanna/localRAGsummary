"""
Example usage of Local RAG System
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import LocalRAGSystem

def example_basic_usage():
    """Example of basic usage"""
    print("🚀 Local RAG System - Basic Usage Example")
    print("=" * 50)
    
    # Initialize the system
    print("Initializing RAG system...")
    rag_system = LocalRAGSystem()
    
    # Check system status
    print("\n📊 System Status:")
    status = rag_system.get_system_status()
    print(f"  Ready: {status['system_ready']}")
    print(f"  Documents: {status['collection_stats']['total_documents']}")
    print(f"  Notes: {status['notes_count']}")
    
    return rag_system

def example_process_documents(rag_system):
    """Example of processing documents"""
    print("\n📁 Processing Documents Example")
    print("-" * 30)
    
    # Create example documents directory if it doesn't exist
    docs_dir = Path("documents")
    docs_dir.mkdir(exist_ok=True)
    
    # Create a sample text file
    sample_file = docs_dir / "sample_course.txt"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("""
Curso de Inteligência Artificial

Módulo 1: Introdução à IA
- Definição de Inteligência Artificial
- História da IA
- Aplicações modernas

Módulo 2: Machine Learning
- Algoritmos de classificação
- Regressão linear
- Redes neurais

Módulo 3: Deep Learning
- Perceptron multicamadas
- Convolução neural
- Processamento de linguagem natural

Conceitos importantes:
- Supervised Learning: Aprendizado com dados rotulados
- Unsupervised Learning: Aprendizado sem supervisão
- Reinforcement Learning: Aprendizado por reforço
""")
    
    print(f"Created sample document: {sample_file}")
    
    # Process documents
    print("\nProcessing documents...")
    result = rag_system.process_documents(
        directory_path=str(docs_dir),
        recursive=True,
        language='pt'
    )
    
    if result['success']:
        print(f"✅ Successfully processed {result['documents_processed']} documents")
        print(f"📝 Generated {result['notes_generated']} notes")
        print(f"🔗 Created {result['embeddings_generated']} embeddings")
    else:
        print(f"❌ Error: {result['message']}")
    
    return result

def example_query_documents(rag_system):
    """Example of querying documents"""
    print("\n❓ Querying Documents Example")
    print("-" * 30)
    
    # Example questions
    questions = [
        "O que é inteligência artificial?",
        "Quais são os tipos de machine learning?",
        "Explique deep learning",
        "O que é supervised learning?"
    ]
    
    for question in questions:
        print(f"\n🔍 Question: {question}")
        
        result = rag_system.query_documents(
            question=question,
            language='pt',
            context_limit=3
        )
        
        if result['success']:
            response = result['response']
            print(f"💡 Answer: {response['answer']}")
            print(f"🎯 Confidence: {response['confidence']:.2f}")
            print(f"📚 Sources: {len(response['sources'])}")
            
            # Show sources
            for i, source in enumerate(response['sources'][:2], 1):
                print(f"   {i}. {Path(source['file_path']).name} (similarity: {source['similarity']:.2f})")
        else:
            print(f"❌ Error: {result['message']}")

def example_batch_queries(rag_system):
    """Example of batch queries"""
    print("\n📋 Batch Queries Example")
    print("-" * 30)
    
    # Create questions file
    questions_data = {
        "questions": [
            "Quais são os principais algoritmos de machine learning?",
            "Como funciona uma rede neural?",
            "O que é processamento de linguagem natural?",
            "Explique a diferença entre IA e machine learning"
        ]
    }
    
    import json
    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(questions_data, f, indent=2, ensure_ascii=False)
    
    print("Created questions.json file")
    
    # Process batch queries
    result = rag_system.batch_query(
        questions=questions_data["questions"],
        language='pt'
    )
    
    if result['success']:
        print(f"✅ Processed {len(result['responses'])} queries")
        
        for i, response in enumerate(result['responses'], 1):
            print(f"\n{i}. Question: {response['question']}")
            print(f"   Answer: {response['answer'][:100]}...")
            print(f"   Confidence: {response['confidence']:.2f}")
    else:
        print(f"❌ Error: {result['message']}")

def example_markdown_notes():
    """Example of markdown notes generation"""
    print("\n📝 Markdown Notes Example")
    print("-" * 30)
    
    from markdown_generator import MarkdownGenerator
    
    # Initialize markdown generator
    md_generator = MarkdownGenerator()
    
    # Get list of notes
    notes = md_generator.get_note_list()
    
    print(f"📄 Found {len(notes)} markdown notes:")
    
    for note in notes[:5]:  # Show first 5 notes
        print(f"  - {note['filename']}")
        print(f"    Size: {note['size_bytes']} bytes")
        print(f"    Modified: {note['modified_at']}")
        print()

def example_system_management():
    """Example of system management"""
    print("\n⚙️ System Management Example")
    print("-" * 30)
    
    # Get system status
    rag_system = LocalRAGSystem()
    status = rag_system.get_system_status()
    
    print("📊 Current System Status:")
    print(f"  Database: {status['collection_stats']['database_type']}")
    print(f"  Documents: {status['collection_stats']['total_documents']}")
    print(f"  Notes: {status['notes_count']}")
    print(f"  System Ready: {status['system_ready']}")
    
    # Show recent notes
    if status['notes']:
        print("\n📄 Recent Notes:")
        for note in status['notes'][:3]:
            print(f"  - {note['filename']} ({note['modified_at']})")

def main():
    """Main example function"""
    print("🎯 Local RAG System - Complete Example")
    print("=" * 60)
    
    try:
        # Initialize system
        rag_system = example_basic_usage()
        
        # Process documents
        process_result = example_process_documents(rag_system)
        
        if process_result['success']:
            # Query documents
            example_query_documents(rag_system)
            
            # Batch queries
            example_batch_queries(rag_system)
            
            # Show markdown notes
            example_markdown_notes()
            
            # System management
            example_system_management()
        
        print("\n🎉 Example completed successfully!")
        print("\n📚 Next steps:")
        print("1. Add your own documents to the 'documents' directory")
        print("2. Run: python main.py --mode process --directory documents")
        print("3. Query with: python main.py --mode query --question 'Your question'")
        print("4. Check generated notes in the 'RAGfiles' directory")
        
    except Exception as e:
        print(f"❌ Error running example: {e}")
        print("Make sure all dependencies are installed correctly.")

if __name__ == "__main__":
    main()
