"""
Gerador de Resumos Temáticos e Audiobooks
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from thematic_analyzer import ThematicAnalyzer
from audio_generator import AudioGenerator
from markdown_generator import MarkdownGenerator
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThematicSummaryGenerator:
    """Gerador de resumos temáticos e audiobooks"""
    
    def __init__(self):
        self.thematic_analyzer = ThematicAnalyzer()
        self.audio_generator = AudioGenerator()
        self.markdown_generator = MarkdownGenerator()
        
        # Cria diretório de temas
        self.themes_dir = RAGFILES_DIR / "temas"
        self.themes_dir.mkdir(exist_ok=True)
    
    def process_documents_thematically(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa documentos e gera resumos temáticos com audiobooks"""
        try:
            logger.info(f"Processando {len(documents)} documentos tematicamente...")
            
            # 1. Análise temática
            logger.info("Analisando temas dos documentos...")
            thematic_groups = self.thematic_analyzer.analyze_document_themes(documents)
            
            if not thematic_groups:
                return {
                    'success': False,
                    'error': 'Nenhum tema identificado nos documentos',
                    'thematic_groups': {},
                    'thematic_dirs': {},
                    'audiobook_results': {}
                }
            
            # 2. Cria estrutura de diretórios
            logger.info("Criando estrutura de diretórios por tema...")
            thematic_dirs = self.thematic_analyzer.create_thematic_structure(thematic_groups)
            
            # 3. Gera resumos temáticos
            logger.info("Gerando resumos temáticos...")
            summary_results = self._generate_thematic_summaries(thematic_groups, thematic_dirs)
            
            # 4. Gera audiobooks
            logger.info("Gerando audiobooks...")
            audiobook_results = self.audio_generator.generate_thematic_audiobooks(
                thematic_groups, thematic_dirs
            )
            
            # 5. Gera resumo geral
            logger.info("Gerando resumo geral...")
            general_summary = self.thematic_analyzer.generate_thematic_summary(thematic_groups)
            
            # Salva resumo geral
            general_summary_path = RAGFILES_DIR / "resumo_tematico_geral.md"
            with open(general_summary_path, 'w', encoding='utf-8') as f:
                f.write(general_summary)
            
            # 6. Estatísticas finais
            stats = self._calculate_final_stats(thematic_groups, summary_results, audiobook_results)
            
            return {
                'success': True,
                'thematic_groups': thematic_groups,
                'thematic_dirs': thematic_dirs,
                'summary_results': summary_results,
                'audiobook_results': audiobook_results,
                'general_summary_path': str(general_summary_path),
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar documentos tematicamente: {e}")
            return {
                'success': False,
                'error': str(e),
                'thematic_groups': {},
                'thematic_dirs': {},
                'audiobook_results': {}
            }
    
    def _generate_thematic_summaries(self, thematic_groups: Dict[str, List[Dict[str, Any]]], 
                                    thematic_dirs: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Gera resumos para cada tema"""
        try:
            summary_results = {}
            
            for theme, docs in thematic_groups.items():
                if theme not in thematic_dirs:
                    continue
                
                logger.info(f"Gerando resumo para tema: {theme}")
                
                # Combina conteúdo dos documentos do tema
                combined_content = self._combine_documents_content(docs)
                
                # Gera resumo usando o gerador de markdown
                theme_dir = Path(thematic_dirs[theme])
                summary_path = theme_dir / "resumos" / f"{theme}_resumo.md"
                
                # Cria resumo temático
                thematic_summary = self._create_thematic_summary(theme, docs, combined_content)
                
                # Salva resumo
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(thematic_summary)
                
                summary_results[theme] = {
                    'success': True,
                    'summary_path': str(summary_path),
                    'documents_count': len(docs),
                    'content_length': len(combined_content)
                }
                
                logger.info(f"Resumo gerado: {summary_path}")
            
            return summary_results
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumos temáticos: {e}")
            return {}
    
    def _combine_documents_content(self, docs: List[Dict[str, Any]]) -> str:
        """Combina conteúdo de múltiplos documentos"""
        try:
            combined_parts = []
            
            for doc in docs:
                content = doc.get('content', {})
                text = content.get('text', '')
                
                if text:
                    # Adiciona cabeçalho do documento
                    file_path = Path(doc.get('file_path', '')).name
                    combined_parts.append(f"\n## {file_path}\n")
                    combined_parts.append(text)
                    combined_parts.append("\n---\n")
            
            return "\n".join(combined_parts)
            
        except Exception as e:
            logger.error(f"Erro ao combinar conteúdo: {e}")
            return ""
    
    def _create_thematic_summary(self, theme: str, docs: List[Dict[str, Any]], 
                                combined_content: str) -> str:
        """Cria resumo temático"""
        try:
            # Informações do tema
            theme_info = self.thematic_analyzer.predefined_themes.get(theme, {})
            theme_description = theme_info.get('description', 'Tema Geral')
            
            # Estatísticas
            total_docs = len(docs)
            total_chars = len(combined_content)
            total_words = len(combined_content.split())
            
            # Cria resumo
            summary_parts = []
            
            summary_parts.append(f"# 📚 Resumo Temático: {theme_description}")
            summary_parts.append(f"**Tema:** {theme}")
            summary_parts.append(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            summary_parts.append("")
            
            # Estatísticas do tema
            summary_parts.append(f"## 📊 Estatísticas do Tema")
            summary_parts.append(f"- **Documentos processados:** {total_docs}")
            summary_parts.append(f"- **Caracteres totais:** {total_chars:,}")
            summary_parts.append(f"- **Palavras totais:** {total_words:,}")
            summary_parts.append("")
            
            # Lista de documentos
            summary_parts.append(f"## 📄 Documentos do Tema")
            summary_parts.append("")
            
            for i, doc in enumerate(docs, 1):
                file_path = Path(doc.get('file_path', '')).name
                confidence = doc.get('theme_confidence', 0)
                content = doc.get('content', {})
                doc_chars = len(content.get('text', ''))
                
                summary_parts.append(f"### {i}. {file_path}")
                summary_parts.append(f"- **Confiança temática:** {confidence:.2f}")
                summary_parts.append(f"- **Tamanho:** {doc_chars:,} caracteres")
                summary_parts.append("")
            
            # Conteúdo combinado
            summary_parts.append(f"## 📖 Conteúdo Combinado")
            summary_parts.append("")
            summary_parts.append(combined_content)
            summary_parts.append("")
            
            # Audiobook
            summary_parts.append(f"## 🎧 Audiobook")
            summary_parts.append("")
            summary_parts.append(f"Um audiobook foi gerado automaticamente para este tema.")
            summary_parts.append(f"Arquivo: `{theme}_audiobook.mp3`")
            summary_parts.append("")
            
            # Recomendações
            summary_parts.append(f"## 💡 Recomendações de Estudo")
            summary_parts.append("")
            summary_parts.append(f"- **Foque nos conceitos principais** do tema {theme_description}")
            summary_parts.append(f"- **Use o audiobook** para revisão durante deslocamentos")
            summary_parts.append(f"- **Combine leitura e audição** para melhor retenção")
            summary_parts.append("")
            
            summary_parts.append("---")
            summary_parts.append("*Resumo temático gerado automaticamente pelo Sistema RAG Local*")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Erro ao criar resumo temático: {e}")
            return f"Erro ao criar resumo temático: {str(e)}"
    
    def _calculate_final_stats(self, thematic_groups: Dict[str, List[Dict[str, Any]]], 
                              summary_results: Dict[str, Dict[str, Any]], 
                              audiobook_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estatísticas finais"""
        try:
            total_docs = sum(len(docs) for docs in thematic_groups.values())
            total_themes = len(thematic_groups)
            
            successful_summaries = sum(1 for result in summary_results.values() if result.get('success'))
            successful_audiobooks = sum(1 for result in audiobook_results.values() if result.get('success'))
            
            return {
                'total_documents': total_docs,
                'total_themes': total_themes,
                'successful_summaries': successful_summaries,
                'successful_audiobooks': successful_audiobooks,
                'summary_success_rate': (successful_summaries / total_themes * 100) if total_themes > 0 else 0,
                'audiobook_success_rate': (successful_audiobooks / total_themes * 100) if total_themes > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o gerador temático"""
        return {
            'name': 'ThematicSummaryGenerator',
            'version': '1.0.0',
            'description': 'Gerador de resumos temáticos e audiobooks',
            'features': [
                'Análise temática automática',
                'Geração de resumos por tema',
                'Criação de audiobooks em português',
                'Estrutura organizacional por temas',
                'Estatísticas detalhadas'
            ],
            'dependencies': {
                'thematic_analyzer': self.thematic_analyzer.get_processor_info(),
                'audio_generator': self.audio_generator.get_processor_info()
            }
        }
