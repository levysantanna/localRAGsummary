#!/usr/bin/env python3
"""
Sistema RAG Local Puro - 100% Open Source - VERSÃO AUTOMÁTICA
Sem frameworks proprietários, sem lock-in
"""

import os
import sys
import json
import sqlite3
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Configuração do sistema"""
    DOCUMENTS_DIR = Path("/home/lsantann/Documents/CC/")
    RAGFILES_DIR = Path("RAGfiles")
    VECTOR_DB_PATH = Path("vector_db.sqlite")
    
    # Extensões suportadas
    SUPPORTED_EXTENSIONS = {
        'text': ['.txt', '.md', '.rst'],
        'pdf': ['.pdf'],
        'images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'],
        'documents': ['.docx', '.doc', '.pptx', '.ppt'],
        'odf': ['.odt', '.ods', '.odp'],
        'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.pl', '.sh', '.sql', '.html', '.css', '.xml', '.json', '.yaml', '.yml']
    }
    
    # Configurações RAG
    CHUNK_SIZE = 1000
    OVERLAP_SIZE = 200
    SIMILARITY_THRESHOLD = 0.7

# ============================================================================
# BANCO DE DADOS VETORIAL SIMPLES
# ============================================================================

class VectorDB:
    """Banco de dados vetorial simples usando SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Inicializar banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de documentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                file_path TEXT,
                file_type TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de chunks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                chunk_text TEXT,
                chunk_index INTEGER,
                vector TEXT,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_document(self, doc_id: str, file_path: str, file_type: str, content: str, metadata: Dict):
        """Adicionar documento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO documents (id, file_path, file_type, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (doc_id, str(file_path), file_type, content, json.dumps(metadata)))
        
        conn.commit()
        conn.close()
    
    def add_chunk(self, chunk_id: str, document_id: str, chunk_text: str, chunk_index: int, vector: List[float], metadata: Dict):
        """Adicionar chunk"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO chunks (id, document_id, chunk_text, chunk_index, vector, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (chunk_id, document_id, chunk_text, chunk_index, json.dumps(vector), json.dumps(metadata)))
        
        conn.commit()
        conn.close()
    
    def search_similar(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """Buscar chunks similares"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar todos os chunks
        cursor.execute('SELECT id, document_id, chunk_text, vector, metadata FROM chunks')
        results = []
        
        for row in cursor.fetchall():
            chunk_id, doc_id, chunk_text, vector_json, metadata_json = row
            vector = json.loads(vector_json)
            metadata = json.loads(metadata_json)
            
            # Calcular similaridade simples (produto escalar)
            similarity = self._cosine_similarity(query_vector, vector)
            
            if similarity >= Config.SIMILARITY_THRESHOLD:
                results.append({
                    'chunk_id': chunk_id,
                    'document_id': doc_id,
                    'chunk_text': chunk_text,
                    'similarity': similarity,
                    'metadata': metadata
                })
        
        conn.close()
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcular similaridade coseno"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

# ============================================================================
# PROCESSAMENTO DE DOCUMENTOS
# ============================================================================

class DocumentProcessor:
    """Processador de documentos puro"""
    
    def __init__(self):
        self.vector_db = VectorDB(Config.VECTOR_DB_PATH)
    
    def get_supported_files(self, directory: Path) -> List[Path]:
        """Obter arquivos suportados"""
        all_files = []
        for ext_list in Config.SUPPORTED_EXTENSIONS.values():
            for ext in ext_list:
                all_files.extend(directory.rglob(f"*{ext}"))
        return all_files
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """Extrair texto de arquivo"""
        try:
            if file_path.suffix.lower() in ['.txt', '.md', '.rst']:
                return self._extract_text_file(file_path)
            elif file_path.suffix.lower() == '.json':
                return self._extract_json_file(file_path)
            elif file_path.suffix.lower() in ['.py', '.js', '.html', '.css', '.xml', '.yaml', '.yml']:
                return self._extract_code_file(file_path)
            else:
                return f"Arquivo {file_path.name} - tipo não suportado para extração de texto"
        except Exception as e:
            return f"Erro ao processar {file_path.name}: {str(e)}"
    
    def _extract_text_file(self, file_path: Path) -> str:
        """Extrair texto de arquivo de texto"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _extract_json_file(self, file_path: Path) -> str:
        """Extrair texto de arquivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _extract_code_file(self, file_path: Path) -> str:
        """Extrair texto de arquivo de código"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extrair URLs do texto"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def scrape_url_content(self, url: str) -> str:
        """Fazer scraping de URL"""
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return self._extract_text_from_html(content)
        except Exception as e:
            return f"Erro ao acessar {url}: {str(e)}"
    
    def _extract_text_from_html(self, html: str) -> str:
        """Extrair texto de HTML"""
        class HTMLTextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
            
            def handle_data(self, data):
                self.text.append(data)
            
            def get_text(self):
                return ' '.join(self.text)
        
        extractor = HTMLTextExtractor()
        extractor.feed(html)
        return extractor.get_text()
    
    def create_simple_embedding(self, text: str) -> List[float]:
        """Criar embedding simples baseado em frequência de palavras"""
        # Tokenização simples
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Contar frequência de palavras
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Criar vetor de 100 dimensões baseado em hash das palavras
        vector = [0.0] * 100
        for word, freq in word_freq.items():
            # Usar hash da palavra para determinar posição no vetor
            hash_val = hash(word) % 100
            vector[hash_val] += freq
        
        # Normalizar vetor
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def chunk_text(self, text: str) -> List[str]:
        """Dividir texto em chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + Config.CHUNK_SIZE
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Tentar quebrar em quebra de linha ou espaço
            chunk = text[start:end]
            last_newline = chunk.rfind('\n')
            last_space = chunk.rfind(' ')
            
            if last_newline > Config.CHUNK_SIZE // 2:
                end = start + last_newline
            elif last_space > Config.CHUNK_SIZE // 2:
                end = start + last_space
            
            chunks.append(text[start:end])
            start = end - Config.OVERLAP_SIZE
        
        return chunks
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Processar documento"""
        print(f"📄 Processando: {file_path.name}")
        
        # Extrair texto
        text = self.extract_text_from_file(file_path)
        
        if not text.strip():
            return {'success': False, 'error': 'Nenhum conteúdo extraído'}
        
        # Extrair URLs
        urls = self.extract_urls_from_text(text)
        scraped_content = ""
        
        if urls:
            print(f"🔗 Encontradas {len(urls)} URLs, fazendo scraping...")
            for url in urls[:5]:  # Limitar a 5 URLs
                scraped = self.scrape_url_content(url)
                scraped_content += f"\n\n--- Conteúdo de {url} ---\n{scraped}"
        
        # Combinar texto original com conteúdo scraped
        full_text = text + scraped_content
        
        # Criar ID único
        doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:16]
        
        # Salvar documento
        metadata = {
            'file_path': str(file_path),
            'file_type': file_path.suffix,
            'word_count': len(full_text.split()),
            'urls_found': len(urls),
            'processed_at': datetime.now().isoformat()
        }
        
        self.vector_db.add_document(doc_id, str(file_path), file_path.suffix, full_text, metadata)
        
        # Criar chunks
        chunks = self.chunk_text(full_text)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            embedding = self.create_simple_embedding(chunk)
            
            chunk_metadata = {
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk)
            }
            
            self.vector_db.add_chunk(chunk_id, doc_id, chunk, i, embedding, chunk_metadata)
        
        print(f"✅ Sucesso: {file_path.name} ({len(full_text)} chars, {len(urls)} URLs, {len(chunks)} chunks)")
        return {
            'success': True,
            'doc_id': doc_id,
            'text_length': len(full_text),
            'urls_count': len(urls),
            'chunks_count': len(chunks)
        }
    
    def process_all_files(self, directory: Path, max_files: int = 100):
        """Processar todos os arquivos"""
        print(f"\n🚀 Processamento do diretório: {directory}")
        print("=" * 60)
        
        if not directory.exists():
            print(f"❌ Diretório não encontrado: {directory}")
            return
        
        # Obter arquivos
        all_files = self.get_supported_files(directory)
        print(f"📊 Encontrados {len(all_files)} arquivos suportados")
        
        if not all_files:
            print("❌ Nenhum arquivo suportado encontrado")
            return
        
        # Limitar número de arquivos
        if len(all_files) > max_files:
            print(f"⚠️ Limitando processamento aos primeiros {max_files} arquivos")
            all_files = all_files[:max_files]
        
        # Mostrar alguns arquivos
        print("\n📄 Arquivos que serão processados:")
        for i, file_path in enumerate(all_files[:10]):
            print(f"  {i+1}. {file_path.name}")
        if len(all_files) > 10:
            print(f"  ... e mais {len(all_files) - 10} arquivos")
        
        # Processar arquivos
        print("\n📝 Iniciando processamento...")
        start_time = datetime.now()
        
        processed_count = 0
        failed_count = 0
        
        for i, file_path in enumerate(all_files):
            print(f"\n[{i+1}/{len(all_files)}] ", end="")
            
            try:
                result = self.process_document(file_path)
                if result['success']:
                    processed_count += 1
                else:
                    failed_count += 1
                    print(f"❌ Falha: {result.get('error', 'Erro desconhecido')}")
            except Exception as e:
                failed_count += 1
                print(f"❌ Erro: {str(e)}")
            
            # Mostrar progresso
            if (i + 1) % 10 == 0:
                progress = ((i + 1) / len(all_files)) * 100
                print(f"📊 Progresso: {i+1}/{len(all_files)} ({progress:.1f}%)")
        
        # Resultados finais
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("📊 RESULTADOS FINAIS")
        print("=" * 60)
        print(f"✅ Arquivos processados com sucesso: {processed_count}")
        print(f"❌ Arquivos com falha: {failed_count}")
        print(f"📊 Total de arquivos: {len(all_files)}")
        print(f"⏱️ Tempo total: {total_time:.2f} segundos")
        print(f"📈 Taxa de sucesso: {(processed_count/len(all_files)*100):.1f}%")
        
        if processed_count > 0:
            print(f"\n🎉 Processamento concluído! {processed_count} arquivos foram processados com sucesso.")
        else:
            print(f"\n⚠️ Nenhum arquivo foi processado com sucesso.")

# ============================================================================
# SISTEMA RAG
# ============================================================================

class RAGSystem:
    """Sistema RAG puro"""
    
    def __init__(self):
        self.vector_db = VectorDB(Config.VECTOR_DB_PATH)
    
    def query(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """Fazer consulta RAG"""
        print(f"❓ Consulta: {question}")
        
        # Criar embedding da pergunta
        query_embedding = self._create_simple_embedding(question)
        
        # Buscar chunks similares
        similar_chunks = self.vector_db.search_similar(query_embedding, max_results)
        
        if not similar_chunks:
            return {
                'answer': 'Nenhum documento relevante encontrado.',
                'sources': [],
                'confidence': 0.0
            }
        
        # Combinar chunks relevantes
        context = "\n\n".join([chunk['chunk_text'] for chunk in similar_chunks])
        
        # Gerar resposta simples
        answer = self._generate_simple_answer(question, context)
        
        # Preparar fontes
        sources = []
        for chunk in similar_chunks:
            sources.append({
                'document_id': chunk['document_id'],
                'similarity': chunk['similarity'],
                'text_preview': chunk['chunk_text'][:200] + "..."
            })
        
        confidence = max([chunk['similarity'] for chunk in similar_chunks]) if similar_chunks else 0.0
        
        print(f"✅ Resposta gerada com {len(similar_chunks)} fontes (confiança: {confidence:.2f})")
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': confidence
        }
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Criar embedding simples"""
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        vector = [0.0] * 100
        for word, freq in word_freq.items():
            hash_val = hash(word) % 100
            vector[hash_val] += freq
        
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def _generate_simple_answer(self, question: str, context: str) -> str:
        """Gerar resposta simples baseada no contexto"""
        # Resposta baseada em palavras-chave
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        
        # Encontrar sentenças relevantes
        sentences = re.split(r'[.!?]+', context)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
            overlap = len(question_words.intersection(sentence_words))
            if overlap > 0:
                relevant_sentences.append((sentence.strip(), overlap))
        
        # Ordenar por relevância
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Combinar as melhores sentenças
        if relevant_sentences:
            answer = " ".join([sent[0] for sent in relevant_sentences[:3]])
            return answer[:500] + "..." if len(answer) > 500 else answer
        else:
            return "Baseado nos documentos disponíveis, não foi possível encontrar uma resposta específica para sua pergunta."

# ============================================================================
# EXECUÇÃO AUTOMÁTICA
# ============================================================================

def main():
    """Função principal automática"""
    print("🤖 Sistema RAG Local Puro - 100% Open Source")
    print("=" * 60)
    print("✅ Sem frameworks proprietários")
    print("✅ Sem dependências complexas")
    print("✅ 100% Python puro")
    print("=" * 60)
    
    # Criar diretórios
    Config.RAGFILES_DIR.mkdir(exist_ok=True)
    
    # 1. Processar documentos
    print("\n📁 PROCESSANDO DOCUMENTOS...")
    processor = DocumentProcessor()
    processor.process_all_files(Config.DOCUMENTS_DIR, max_files=50)
    
    # 2. Fazer algumas consultas de teste
    print("\n❓ TESTANDO CONSULTAS RAG...")
    rag = RAGSystem()
    
    test_questions = [
        "O que é inteligência artificial?",
        "Como funciona machine learning?",
        "Quais são os algoritmos de classificação?",
        "O que é deep learning?",
        "Como implementar redes neurais?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*50}")
        result = rag.query(question)
        print(f"💬 Resposta: {result['answer']}")
        print(f"📊 Confiança: {result['confidence']:.3f}")
        print(f"📚 Fontes: {len(result['sources'])}")
    
    # 3. Mostrar estatísticas
    print(f"\n{'='*60}")
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 60)
    
    # Conectar ao banco
    conn = sqlite3.connect(Config.VECTOR_DB_PATH)
    cursor = conn.cursor()
    
    # Contar documentos
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    # Contar chunks
    cursor.execute("SELECT COUNT(*) FROM chunks")
    chunk_count = cursor.fetchone()[0]
    
    # Tipos de arquivo
    cursor.execute("SELECT file_type, COUNT(*) FROM documents GROUP BY file_type")
    file_types = cursor.fetchall()
    
    conn.close()
    
    print(f"📄 Total de documentos: {doc_count}")
    print(f"📝 Total de chunks: {chunk_count}")
    print(f"📊 Tipos de arquivo:")
    for file_type, count in file_types:
        print(f"  - {file_type}: {count}")
    
    print(f"\n🎉 Sistema RAG puro executado com sucesso!")
    print(f"💾 Banco de dados: {Config.VECTOR_DB_PATH}")

if __name__ == "__main__":
    main()
