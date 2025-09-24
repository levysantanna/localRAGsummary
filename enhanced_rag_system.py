"""
Sistema RAG Aprimorado com Web Scraping, Treinamento de LLM e Chat Interface
"""
import logging
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    pipeline
)
from datasets import Dataset
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from datetime import datetime
import asyncio
import aiohttp
from tqdm import tqdm
import threading
import queue

from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLProcessor:
    """Processador de URLs encontradas nos documentos"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.processed_urls = set()
        self.url_content = {}
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extrai URLs do texto"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return list(set(urls))  # Remove duplicatas
    
    def is_valid_url(self, url: str) -> bool:
        """Verifica se a URL é válida"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ['http', 'https']
        except:
            return False
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Faz scraping de uma URL"""
        try:
            if url in self.processed_urls:
                return self.url_content.get(url, {})
            
            logger.info(f"Scraping URL: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrai conteúdo
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extrai texto principal
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                text_content = main_content.get_text(separator=' ', strip=True)
            else:
                text_content = soup.get_text(separator=' ', strip=True)
            
            # Limpa o texto
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Extrai links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    links.append(href)
                elif href.startswith('/'):
                    links.append(urljoin(url, href))
            
            # Extrai imagens
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http'):
                    images.append(src)
                elif src.startswith('/'):
                    images.append(urljoin(url, src))
            
            content = {
                'url': url,
                'title': title_text,
                'content': text_content,
                'links': list(set(links)),
                'images': list(set(images)),
                'scraped_at': datetime.now().isoformat(),
                'status': 'success'
            }
            
            self.processed_urls.add(url)
            self.url_content[url] = content
            
            return content
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'title': '',
                'content': '',
                'links': [],
                'images': [],
                'scraped_at': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def scrape_urls_batch(self, urls: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """Faz scraping de múltiplas URLs em paralelo"""
        results = {}
        
        def worker():
            while True:
                try:
                    url = url_queue.get()
                    if url is None:
                        break
                    results[url] = self.scrape_url(url)
                    url_queue.task_done()
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    url_queue.task_done()
        
        url_queue = queue.Queue()
        for url in urls:
            url_queue.put(url)
        
        # Inicia workers
        threads = []
        for _ in range(min(max_workers, len(urls))):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        
        # Adiciona sentinelas para parar workers
        for _ in range(max_workers):
            url_queue.put(None)
        
        # Espera todos os workers terminarem
        for t in threads:
            t.join()
        
        return results

class EnhancedDocumentProcessor:
    """Processador de documentos aprimorado com web scraping"""
    
    def __init__(self):
        self.url_processor = URLProcessor()
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    
    def process_document_with_urls(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Processa documento e extrai URLs para scraping"""
        content = doc.get('content', {})
        text = content.get('text', '')
        
        # Extrai URLs do texto
        urls = self.url_processor.extract_urls_from_text(text)
        valid_urls = [url for url in urls if self.url_processor.is_valid_url(url)]
        
        logger.info(f"Found {len(valid_urls)} URLs in document: {doc.get('file_path', '')}")
        
        # Faz scraping das URLs
        scraped_content = {}
        if valid_urls:
            scraped_content = self.url_processor.scrape_urls_batch(valid_urls)
        
        # Combina conteúdo original com conteúdo scraped
        enhanced_content = {
            'original_text': text,
            'urls_found': valid_urls,
            'scraped_content': scraped_content,
            'total_content_length': len(text),
            'scraped_content_length': sum(len(sc['content']) for sc in scraped_content.values() if sc.get('status') == 'success')
        }
        
        # Gera embedding combinado
        all_text = text
        for url, scraped in scraped_content.items():
            if scraped.get('status') == 'success':
                all_text += f"\n\n--- Conteúdo de {url} ---\n{scraped.get('content', '')}"
        
        if all_text:
            embedding = self.embedding_model.encode(all_text)
            enhanced_content['embedding'] = embedding.tolist()
        
        return enhanced_content

class LLMTrainer:
    """Treinador de modelo de linguagem local"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.trained_model = None
        
    def load_model(self):
        """Carrega o modelo base"""
        logger.info(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Adiciona padding token se não existir
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def prepare_training_data(self, documents: List[Dict[str, Any]]) -> Dataset:
        """Prepara dados de treinamento dos documentos"""
        training_texts = []
        
        for doc in documents:
            # Texto original
            content = doc.get('content', {})
            original_text = content.get('text', '')
            if original_text:
                training_texts.append(original_text)
            
            # Conteúdo scraped
            enhanced_content = doc.get('enhanced_content', {})
            scraped_content = enhanced_content.get('scraped_content', {})
            
            for url, scraped in scraped_content.items():
                if scraped.get('status') == 'success':
                    scraped_text = scraped.get('content', '')
                    if scraped_text:
                        training_texts.append(f"Conteúdo de {url}: {scraped_text}")
        
        # Tokeniza os textos
        tokenized_texts = []
        for text in training_texts:
            tokens = self.tokenizer.encode(text, truncation=True, max_length=512)
            tokenized_texts.append(tokens)
        
        # Cria dataset
        dataset = Dataset.from_dict({
            'input_ids': tokenized_texts
        })
        
        return dataset
    
    def train_model(self, documents: List[Dict[str, Any]], output_dir: str = "trained_model"):
        """Treina o modelo com os documentos"""
        if not self.model or not self.tokenizer:
            self.load_model()
        
        logger.info("Preparing training data...")
        dataset = self.prepare_training_data(documents)
        
        # Configurações de treinamento
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="no",
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        logger.info("Starting model training...")
        trainer.train()
        
        # Salva o modelo treinado
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Model trained and saved to {output_dir}")
        
        # Carrega o modelo treinado
        self.trained_model = AutoModelForCausalLM.from_pretrained(output_dir)
        
        return output_dir

class ChatInterface:
    """Interface de chat com o modelo treinado"""
    
    def __init__(self, model_path: str, documents: List[Dict[str, Any]]):
        self.model_path = model_path
        self.documents = documents
        self.model = None
        self.tokenizer = None
        self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.chroma_client = None
        self.collection = None
        
        self.load_model()
        self.setup_vector_store()
    
    def load_model(self):
        """Carrega o modelo treinado"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
            logger.info("Trained model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading trained model: {e}")
            # Fallback para modelo base
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
    
    def setup_vector_store(self):
        """Configura o banco vetorial para busca de contexto"""
        try:
            self.chroma_client = chromadb.PersistentClient(path="vector_db")
            self.collection = self.chroma_client.get_or_create_collection("documents")
            
            # Adiciona documentos ao banco vetorial
            for i, doc in enumerate(self.documents):
                content = doc.get('content', {})
                text = content.get('text', '')
                
                if text:
                    embedding = self.embedding_model.encode(text)
                    self.collection.add(
                        ids=[f"doc_{i}"],
                        embeddings=[embedding.tolist()],
                        documents=[text],
                        metadatas=[{"file_path": doc.get('file_path', '')}]
                    )
            
            logger.info("Vector store setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {e}")
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """Busca contexto relevante para a query"""
        try:
            if not self.collection:
                return ""
            
            query_embedding = self.embedding_model.encode(query)
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            context_parts = []
            for i, doc in enumerate(results['documents'][0]):
                context_parts.append(f"Documento {i+1}: {doc}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return ""
    
    def generate_response(self, query: str) -> str:
        """Gera resposta usando o modelo treinado"""
        try:
            # Busca contexto relevante
            context = self.get_context(query)
            
            # Cria prompt
            prompt = f"""Você é um assistente especializado em responder perguntas sobre documentos universitários. 
Use o contexto fornecido para responder de forma precisa e detalhada.

Contexto:
{context}

Pergunta: {query}

Resposta:"""
            
            # Tokeniza o prompt
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=1024)
            
            # Gera resposta
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decodifica resposta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove o prompt da resposta
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}"
    
    def chat(self):
        """Interface de chat interativa"""
        print("🤖 Chat com o Sistema RAG Local")
        print("=" * 50)
        print("Digite 'sair' para encerrar o chat")
        print("Digite 'ajuda' para ver comandos disponíveis")
        print()
        
        while True:
            try:
                query = input("Você: ").strip()
                
                if query.lower() == 'sair':
                    print("👋 Até logo!")
                    break
                
                if query.lower() == 'ajuda':
                    print("""
Comandos disponíveis:
- Digite qualquer pergunta sobre os documentos
- 'sair' - Encerrar o chat
- 'ajuda' - Mostrar esta ajuda
- 'contexto' - Mostrar contexto da última pergunta
                    """)
                    continue
                
                if not query:
                    continue
                
                print("🤖 Processando...")
                response = self.generate_response(query)
                print(f"Assistente: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Chat encerrado!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

class EnhancedRAGSystem:
    """Sistema RAG aprimorado com todas as funcionalidades"""
    
    def __init__(self):
        self.document_processor = EnhancedDocumentProcessor()
        self.llm_trainer = LLMTrainer()
        self.chat_interface = None
        self.processed_documents = []
    
    def process_documents_enhanced(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa documentos com web scraping"""
        logger.info("Processing documents with web scraping...")
        
        enhanced_documents = []
        
        for doc in tqdm(documents, desc="Processing documents"):
            try:
                enhanced_content = self.document_processor.process_document_with_urls(doc)
                doc['enhanced_content'] = enhanced_content
                enhanced_documents.append(doc)
                
                logger.info(f"Enhanced document: {doc.get('file_path', '')}")
                logger.info(f"  - URLs found: {len(enhanced_content.get('urls_found', []))}")
                logger.info(f"  - Scraped content: {enhanced_content.get('scraped_content_length', 0)} chars")
                
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                enhanced_documents.append(doc)
        
        self.processed_documents = enhanced_documents
        return enhanced_documents
    
    def train_llm(self, output_dir: str = "trained_model") -> str:
        """Treina modelo de linguagem"""
        if not self.processed_documents:
            raise ValueError("No processed documents available for training")
        
        logger.info("Training LLM with documents...")
        model_path = self.llm_trainer.train_model(self.processed_documents, output_dir)
        
        # Cria interface de chat
        self.chat_interface = ChatInterface(model_path, self.processed_documents)
        
        return model_path
    
    def start_chat(self):
        """Inicia interface de chat"""
        if not self.chat_interface:
            raise ValueError("Chat interface not initialized. Train the model first.")
        
        self.chat_interface.chat()
    
    def generate_enhanced_summary(self, language: str = 'pt') -> str:
        """Gera resumo aprimorado com mais detalhes"""
        if not self.processed_documents:
            return "Nenhum documento processado."
        
        summary_parts = []
        
        # Estatísticas gerais
        total_docs = len(self.processed_documents)
        total_urls = sum(len(doc.get('enhanced_content', {}).get('urls_found', [])) for doc in self.processed_documents)
        total_scraped = sum(1 for doc in self.processed_documents 
                           for scraped in doc.get('enhanced_content', {}).get('scraped_content', {}).values()
                           if scraped.get('status') == 'success')
        
        summary_parts.append(f"# Resumo Aprimorado do Sistema RAG Local")
        summary_parts.append(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        summary_parts.append("")
        
        summary_parts.append(f"## 📊 Estatísticas Gerais")
        summary_parts.append(f"- **Total de documentos:** {total_docs}")
        summary_parts.append(f"- **URLs encontradas:** {total_urls}")
        summary_parts.append(f"- **URLs processadas com sucesso:** {total_scraped}")
        summary_parts.append(f"- **Taxa de sucesso do scraping:** {(total_scraped/total_urls*100) if total_urls > 0 else 0:.1f}%")
        summary_parts.append("")
        
        # Detalhes por documento
        summary_parts.append(f"## 📄 Detalhes por Documento")
        summary_parts.append("")
        
        for i, doc in enumerate(self.processed_documents, 1):
            file_path = doc.get('file_path', 'Desconhecido')
            enhanced_content = doc.get('enhanced_content', {})
            urls_found = enhanced_content.get('urls_found', [])
            scraped_content = enhanced_content.get('scraped_content', {})
            
            summary_parts.append(f"### {i}. {Path(file_path).name}")
            summary_parts.append(f"- **Caminho:** {file_path}")
            summary_parts.append(f"- **URLs encontradas:** {len(urls_found)}")
            
            if urls_found:
                summary_parts.append(f"- **URLs:**")
                for url in urls_found:
                    status = scraped_content.get(url, {}).get('status', 'unknown')
                    status_emoji = "✅" if status == 'success' else "❌"
                    summary_parts.append(f"  - {status_emoji} {url}")
            
            # Conteúdo scraped
            successful_scrapes = [sc for sc in scraped_content.values() if sc.get('status') == 'success']
            if successful_scrapes:
                summary_parts.append(f"- **Conteúdo adicional obtido:**")
                for scraped in successful_scrapes:
                    title = scraped.get('title', 'Sem título')
                    content_preview = scraped.get('content', '')[:200] + '...' if len(scraped.get('content', '')) > 200 else scraped.get('content', '')
                    summary_parts.append(f"  - **{title}:** {content_preview}")
            
            summary_parts.append("")
        
        # URLs mais relevantes
        if total_urls > 0:
            summary_parts.append(f"## 🔗 URLs Mais Relevantes")
            summary_parts.append("")
            
            url_stats = {}
            for doc in self.processed_documents:
                scraped_content = doc.get('enhanced_content', {}).get('scraped_content', {})
                for url, content in scraped_content.items():
                    if content.get('status') == 'success':
                        url_stats[url] = {
                            'title': content.get('title', ''),
                            'content_length': len(content.get('content', '')),
                            'links_count': len(content.get('links', [])),
                            'images_count': len(content.get('images', []))
                        }
            
            # Ordena por relevância (comprimento do conteúdo)
            sorted_urls = sorted(url_stats.items(), key=lambda x: x[1]['content_length'], reverse=True)
            
            for url, stats in sorted_urls[:10]:  # Top 10
                summary_parts.append(f"### {stats['title'] or 'Sem título'}")
                summary_parts.append(f"- **URL:** {url}")
                summary_parts.append(f"- **Tamanho do conteúdo:** {stats['content_length']} caracteres")
                summary_parts.append(f"- **Links encontrados:** {stats['links_count']}")
                summary_parts.append(f"- **Imagens encontradas:** {stats['images_count']}")
                summary_parts.append("")
        
        # Recomendações
        summary_parts.append(f"## 💡 Recomendações")
        summary_parts.append("")
        summary_parts.append(f"- **Modelo treinado:** {'✅ Sim' if self.chat_interface else '❌ Não'}")
        summary_parts.append(f"- **Interface de chat:** {'✅ Disponível' if self.chat_interface else '❌ Não disponível'}")
        summary_parts.append(f"- **Próximos passos:**")
        if not self.chat_interface:
            summary_parts.append(f"  1. Treinar modelo de linguagem")
            summary_parts.append(f"  2. Iniciar interface de chat")
        else:
            summary_parts.append(f"  1. Usar interface de chat para perguntas")
            summary_parts.append(f"  2. Fazer perguntas sobre os documentos")
        summary_parts.append("")
        
        summary_parts.append("---")
        summary_parts.append("*Resumo gerado automaticamente pelo Sistema RAG Local Aprimorado*")
        
        return "\n".join(summary_parts)

def main():
    """Função principal para demonstrar o sistema aprimorado"""
    print("🚀 Sistema RAG Local Aprimorado")
    print("=" * 50)
    
    # Exemplo de uso
    enhanced_rag = EnhancedRAGSystem()
    
    # Aqui você adicionaria seus documentos
    # documents = load_your_documents()
    # enhanced_docs = enhanced_rag.process_documents_enhanced(documents)
    # model_path = enhanced_rag.train_llm()
    # enhanced_rag.start_chat()
    
    print("Sistema aprimorado configurado com sucesso!")

if __name__ == "__main__":
    main()
