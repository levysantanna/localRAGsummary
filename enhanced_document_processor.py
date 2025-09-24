#!/usr/bin/env python3
"""
Processador de Documentos Aprimorado
- Processa TODOS os arquivos do diretório
- Detecta e faz scraping de URLs
- Processa imagens com OCR
- Atualização dinâmica da contagem
- Processamento contínuo
"""

import os
import sys
import time
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_processor import DocumentProcessor
from embedding_system import EmbeddingSystem
from markdown_generator import MarkdownGenerator
import config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """Processador de documentos aprimorado com scraping de URLs"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_system = EmbeddingSystem()
        self.markdown_generator = MarkdownGenerator()
        self.processed_files = set()
        self.scraped_urls = set()
        self.total_files = 0
        self.processed_count = 0
        
    def get_all_files(self, directory: Path) -> List[Path]:
        """Obtém TODOS os arquivos do diretório e subdiretórios"""
        all_files = []
        
        # Extensões suportadas expandidas
        supported_extensions = {
            '.txt', '.md', '.rst', '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', 
            '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', 
            '.r', '.m', '.pl', '.sh', '.sql', '.html', '.css', '.xml', '.json', 
            '.yaml', '.yml', '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.odt', 
            '.ods', '.odp', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', 
            '.svg', '.webp'
        }
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in supported_extensions:
                    all_files.append(file_path)
        
        return all_files
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extrai URLs do texto"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def scrape_url_content(self, url: str) -> Dict[str, Any]:
        """Faz scraping do conteúdo de uma URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair título
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Sem título"
            
            # Extrair meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Extrair texto principal
            # Remover scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrair texto dos parágrafos
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            text_content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Se não há parágrafos, extrair todo o texto
            if not text_content:
                text_content = soup.get_text()
            
            # Limpar texto
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            return {
                'url': url,
                'title': title_text,
                'description': description,
                'content': text_content[:5000],  # Limitar a 5000 caracteres
                'scraped_at': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Erro ao fazer scraping da URL {url}: {e}")
            return {
                'url': url,
                'title': f"Erro: {str(e)}",
                'description': "",
                'content': "",
                'scraped_at': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def process_document_with_urls(self, file_path: Path) -> Dict[str, Any]:
        """Processa um documento e extrai URLs para scraping"""
        try:
            # Processar documento normal
            document = self.document_processor.process_document(file_path)
            
            if not document or not document.get('content', {}).get('text'):
                return document
            
            # Converter estrutura do DocumentProcessor para estrutura esperada
            document = {
                'text': document['content']['text'],
                'metadata': document['metadata'],
                'file_path': document['file_path'],
                'file_type': document['file_type']
            }
            
            # Adicionar ID único se não existir
            if 'id' not in document:
                import hashlib
                content_hash = hashlib.md5(document['text'].encode()).hexdigest()
                document['id'] = f"{file_path.stem}_{content_hash[:8]}"
            
            # Garantir que metadata existe
            if 'metadata' not in document:
                document['metadata'] = {}
            
            # Extrair URLs do texto
            urls = self.extract_urls_from_text(document['text'])
            
            if urls:
                logger.info(f"Encontradas {len(urls)} URLs em {file_path.name}")
                
                # Fazer scraping das URLs
                scraped_content = []
                for url in urls[:5]:  # Limitar a 5 URLs por documento
                    if url not in self.scraped_urls:
                        logger.info(f"Fazendo scraping de: {url}")
                        scraped_data = self.scrape_url_content(url)
                        scraped_content.append(scraped_data)
                        self.scraped_urls.add(url)
                        time.sleep(1)  # Pausa entre requests
                
                # Adicionar conteúdo scraped ao documento
                if scraped_content:
                    document['scraped_urls'] = scraped_content
                    document['urls_found'] = len(urls)
                    document['urls_scraped'] = len(scraped_content)
                    
                    # Adicionar conteúdo scraped ao texto principal
                    scraped_text = "\n\n".join([
                        f"URL: {item['url']}\nTítulo: {item['title']}\nConteúdo: {item['content']}"
                        for item in scraped_content if item['status'] == 'success'
                    ])
                    
                    if scraped_text:
                        document['text'] += f"\n\n--- CONTEÚDO SCRAPED ---\n{scraped_text}"
            
            return document
            
        except Exception as e:
            logger.error(f"Erro ao processar documento {file_path}: {e}")
            return None
    
    def process_all_documents(self, directory: Path, callback=None) -> Dict[str, Any]:
        """Processa TODOS os documentos do diretório"""
        logger.info(f"🔍 Iniciando processamento de TODOS os documentos em {directory}")
        
        # Obter todos os arquivos
        all_files = self.get_all_files(directory)
        self.total_files = len(all_files)
        self.processed_count = 0
        
        logger.info(f"📁 Encontrados {self.total_files} arquivos para processar")
        
        processed_documents = []
        failed_files = []
        
        for i, file_path in enumerate(all_files):
            try:
                logger.info(f"📄 Processando {i+1}/{self.total_files}: {file_path.name}")
                
                # Processar documento com URLs
                document = self.process_document_with_urls(file_path)
                
                if document:
                    processed_documents.append(document)
                    self.processed_count += 1
                    logger.info(f"✅ Processado: {file_path.name}")
                else:
                    failed_files.append(str(file_path))
                    logger.warning(f"❌ Falhou: {file_path.name}")
                
                # Callback para atualização dinâmica
                if callback:
                    progress = {
                        'total': self.total_files,
                        'processed': self.processed_count,
                        'current_file': file_path.name,
                        'progress_percent': (self.processed_count / self.total_files) * 100
                    }
                    callback(progress)
                
                # Pequena pausa para não sobrecarregar
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {e}")
                failed_files.append(str(file_path))
        
        # Gerar embeddings
        if processed_documents:
            logger.info(f"🧠 Gerando embeddings para {len(processed_documents)} documentos")
            success = self.embedding_system.store_embeddings(processed_documents)
            
            if success:
                logger.info("✅ Embeddings armazenados com sucesso!")
            else:
                logger.error("❌ Erro ao armazenar embeddings")
        
        # Gerar resumos
        if processed_documents:
            logger.info("📝 Gerando resumos...")
            try:
                self.markdown_generator.generate_query_notes(processed_documents)
                logger.info("✅ Resumos gerados!")
            except Exception as e:
                logger.error(f"Erro ao gerar resumos: {e}")
        
        return {
            'total_files': self.total_files,
            'processed_count': self.processed_count,
            'failed_count': len(failed_files),
            'failed_files': failed_files,
            'scraped_urls_count': len(self.scraped_urls),
            'documents': processed_documents
        }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do processamento"""
        return {
            'total_files': self.total_files,
            'processed_count': self.processed_count,
            'progress_percent': (self.processed_count / self.total_files * 100) if self.total_files > 0 else 0,
            'scraped_urls_count': len(self.scraped_urls),
            'scraped_urls': list(self.scraped_urls)
        }

def main():
    """Função principal para teste"""
    processor = EnhancedDocumentProcessor()
    
    # Processar documentos
    results = processor.process_all_documents(
        config.DOCUMENTS_DIR,
        callback=lambda progress: print(f"Progresso: {progress['progress_percent']:.1f}% - {progress['current_file']}")
    )
    
    print(f"\n📊 Resultados do Processamento:")
    print(f"Total de arquivos: {results['total_files']}")
    print(f"Processados com sucesso: {results['processed_count']}")
    print(f"Falharam: {results['failed_count']}")
    print(f"URLs scraped: {results['scraped_urls_count']}")
    
    if results['failed_files']:
        print(f"\n❌ Arquivos que falharam:")
        for file in results['failed_files']:
            print(f"  - {file}")

if __name__ == "__main__":
    main()
