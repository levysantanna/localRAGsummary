"""
Analisador Temático para Separação de Conteúdo por Temas
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import json
from datetime import datetime

# Text processing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import RSLPStemmer
import spacy

# ML for topic classification
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThematicAnalyzer:
    """Analisador temático para classificação e separação de conteúdo"""
    
    def __init__(self):
        self.setup_nltk()
        self.setup_spacy()
        self.stemmer = RSLPStemmer()
        self.stop_words = set(stopwords.words('portuguese'))
        
        # Temas predefinidos para classificação
        self.predefined_themes = {
            'inteligencia_artificial': {
                'keywords': ['ia', 'inteligência artificial', 'machine learning', 'deep learning', 
                           'neural network', 'algoritmo', 'modelo', 'treinamento', 'dados'],
                'description': 'Inteligência Artificial e Machine Learning'
            },
            'programacao': {
                'keywords': ['programação', 'código', 'python', 'javascript', 'java', 'algoritmo',
                           'função', 'variável', 'loop', 'condição', 'debugging'],
                'description': 'Programação e Desenvolvimento de Software'
            },
            'matematica': {
                'keywords': ['matemática', 'cálculo', 'álgebra', 'geometria', 'estatística',
                           'probabilidade', 'derivada', 'integral', 'equação', 'função'],
                'description': 'Matemática e Estatística'
            },
            'fisica': {
                'keywords': ['física', 'mecânica', 'termodinâmica', 'eletromagnetismo', 'óptica',
                           'energia', 'força', 'velocidade', 'aceleração', 'onda'],
                'description': 'Física e Ciências Naturais'
            },
            'quimica': {
                'keywords': ['química', 'molécula', 'átomo', 'reação', 'composto', 'elemento',
                           'tabela periódica', 'ligação', 'solução', 'ácido', 'base'],
                'description': 'Química e Ciências Químicas'
            },
            'biologia': {
                'keywords': ['biologia', 'célula', 'DNA', 'proteína', 'organismo', 'evolução',
                           'genética', 'ecossistema', 'biodiversidade', 'anatomia'],
                'description': 'Biologia e Ciências Biológicas'
            },
            'historia': {
                'keywords': ['história', 'histórico', 'passado', 'antigo', 'medieval', 'moderno',
                           'guerra', 'revolução', 'civilização', 'cultura', 'sociedade'],
                'description': 'História e Ciências Humanas'
            },
            'literatura': {
                'keywords': ['literatura', 'livro', 'poesia', 'romance', 'autor', 'escritor',
                           'narrativa', 'personagem', 'enredo', 'estilo', 'linguagem'],
                'description': 'Literatura e Língua Portuguesa'
            },
            'economia': {
                'keywords': ['economia', 'financeiro', 'mercado', 'capital', 'investimento',
                           'inflação', 'PIB', 'moeda', 'banco', 'crédito'],
                'description': 'Economia e Finanças'
            },
            'filosofia': {
                'keywords': ['filosofia', 'filosófico', 'ética', 'moral', 'lógica', 'razão',
                           'conhecimento', 'verdade', 'existência', 'pensamento'],
                'description': 'Filosofia e Ética'
            }
        }
    
    def setup_nltk(self):
        """Configura recursos do NLTK"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('rslp', quiet=True)
        except Exception as e:
            logger.warning(f"Erro ao configurar NLTK: {e}")
    
    def setup_spacy(self):
        """Configura spaCy para português"""
        try:
            self.nlp = spacy.load('pt_core_news_sm')
        except OSError:
            logger.warning("Modelo spaCy português não encontrado. Usando processamento básico.")
            self.nlp = None
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extrai palavras-chave do texto"""
        try:
            # Tokenização e limpeza
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and len(word) > 2]
            words = [word for word in words if word not in self.stop_words]
            
            # Stemming
            stemmed_words = [self.stemmer.stem(word) for word in words]
            
            # Contagem de frequência
            word_freq = Counter(stemmed_words)
            
            # Retorna as palavras mais frequentes
            return [word for word, freq in word_freq.most_common(max_keywords)]
            
        except Exception as e:
            logger.error(f"Erro ao extrair palavras-chave: {e}")
            return []
    
    def classify_theme(self, text: str) -> Tuple[str, float]:
        """Classifica o tema do texto"""
        try:
            # Extrai palavras-chave do texto
            keywords = self.extract_keywords(text)
            
            # Calcula similaridade com temas predefinidos
            theme_scores = {}
            
            for theme_name, theme_info in self.predefined_themes.items():
                score = 0
                theme_keywords = [kw.lower() for kw in theme_info['keywords']]
                
                # Conta correspondências de palavras-chave
                for keyword in keywords:
                    for theme_keyword in theme_keywords:
                        if keyword in theme_keyword or theme_keyword in keyword:
                            score += 1
                
                # Normaliza o score
                if len(keywords) > 0:
                    theme_scores[theme_name] = score / len(keywords)
                else:
                    theme_scores[theme_name] = 0
            
            # Retorna o tema com maior score
            if theme_scores:
                best_theme = max(theme_scores, key=theme_scores.get)
                confidence = theme_scores[best_theme]
                
                # Se a confiança for muito baixa, classifica como 'geral'
                if confidence < 0.1:
                    return 'geral', confidence
                else:
                    return best_theme, confidence
            else:
                return 'geral', 0.0
                
        except Exception as e:
            logger.error(f"Erro ao classificar tema: {e}")
            return 'geral', 0.0
    
    def analyze_document_themes(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Analisa temas dos documentos e os agrupa"""
        try:
            thematic_groups = {}
            
            for doc in documents:
                content = doc.get('content', {})
                text = content.get('text', '')
                
                if not text:
                    continue
                
                # Classifica o tema
                theme, confidence = self.classify_theme(text)
                
                # Adiciona informações do tema ao documento
                doc['theme'] = theme
                doc['theme_confidence'] = confidence
                doc['theme_description'] = self.predefined_themes.get(theme, {}).get('description', 'Tema Geral')
                
                # Agrupa por tema
                if theme not in thematic_groups:
                    thematic_groups[theme] = []
                
                thematic_groups[theme].append(doc)
            
            return thematic_groups
            
        except Exception as e:
            logger.error(f"Erro ao analisar temas dos documentos: {e}")
            return {}
    
    def generate_thematic_summary(self, thematic_groups: Dict[str, List[Dict[str, Any]]]) -> str:
        """Gera resumo temático dos grupos"""
        try:
            summary_parts = []
            
            summary_parts.append("# 📚 Análise Temática dos Documentos")
            summary_parts.append(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            summary_parts.append("")
            
            # Estatísticas gerais
            total_docs = sum(len(docs) for docs in thematic_groups.values())
            total_themes = len(thematic_groups)
            
            summary_parts.append(f"## 📊 Estatísticas Gerais")
            summary_parts.append(f"- **Total de documentos:** {total_docs}")
            summary_parts.append(f"- **Temas identificados:** {total_themes}")
            summary_parts.append("")
            
            # Análise por tema
            summary_parts.append(f"## 🎯 Análise por Tema")
            summary_parts.append("")
            
            for theme, docs in thematic_groups.items():
                theme_info = self.predefined_themes.get(theme, {})
                theme_description = theme_info.get('description', 'Tema Geral')
                
                summary_parts.append(f"### {theme_description}")
                summary_parts.append(f"- **Tema:** {theme}")
                summary_parts.append(f"- **Documentos:** {len(docs)}")
                
                # Lista documentos do tema
                for i, doc in enumerate(docs, 1):
                    file_path = Path(doc.get('file_path', '')).name
                    confidence = doc.get('theme_confidence', 0)
                    summary_parts.append(f"  {i}. {file_path} (confiança: {confidence:.2f})")
                
                summary_parts.append("")
            
            # Recomendações
            summary_parts.append(f"## 💡 Recomendações")
            summary_parts.append("")
            summary_parts.append(f"- **Temas mais frequentes:** {self._get_most_frequent_themes(thematic_groups)}")
            summary_parts.append(f"- **Diversidade temática:** {'Alta' if total_themes > 5 else 'Média' if total_themes > 2 else 'Baixa'}")
            summary_parts.append(f"- **Próximos passos:** Gerar resumos e audiobooks por tema")
            summary_parts.append("")
            
            summary_parts.append("---")
            summary_parts.append("*Análise temática gerada automaticamente pelo Sistema RAG Local*")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo temático: {e}")
            return f"Erro ao gerar resumo temático: {str(e)}"
    
    def _get_most_frequent_themes(self, thematic_groups: Dict[str, List[Dict[str, Any]]]) -> str:
        """Retorna os temas mais frequentes"""
        try:
            theme_counts = {theme: len(docs) for theme, docs in thematic_groups.items()}
            sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
            
            if len(sorted_themes) >= 2:
                return f"{sorted_themes[0][0]} ({sorted_themes[0][1]} docs), {sorted_themes[1][0]} ({sorted_themes[1][1]} docs)"
            elif len(sorted_themes) == 1:
                return f"{sorted_themes[0][0]} ({sorted_themes[0][1]} docs)"
            else:
                return "Nenhum tema identificado"
                
        except Exception as e:
            logger.error(f"Erro ao calcular temas frequentes: {e}")
            return "Erro na análise"
    
    def create_thematic_structure(self, thematic_groups: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """Cria estrutura de diretórios por tema"""
        try:
            thematic_dirs = {}
            
            for theme, docs in thematic_groups.items():
                # Cria diretório do tema
                theme_dir = RAGFILES_DIR / f"temas/{theme}"
                theme_dir.mkdir(parents=True, exist_ok=True)
                
                thematic_dirs[theme] = str(theme_dir)
                
                # Cria subdiretórios
                (theme_dir / "resumos").mkdir(exist_ok=True)
                (theme_dir / "audiobooks").mkdir(exist_ok=True)
                (theme_dir / "dados").mkdir(exist_ok=True)
            
            return thematic_dirs
            
        except Exception as e:
            logger.error(f"Erro ao criar estrutura temática: {e}")
            return {}
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o analisador temático"""
        return {
            'name': 'ThematicAnalyzer',
            'version': '1.0.0',
            'description': 'Analisador temático para classificação e separação de conteúdo',
            'supported_themes': list(self.predefined_themes.keys()),
            'features': [
                'Classificação automática de temas',
                'Agrupamento de documentos por tema',
                'Geração de resumos temáticos',
                'Criação de estrutura de diretórios',
                'Análise de confiança temática'
            ]
        }
