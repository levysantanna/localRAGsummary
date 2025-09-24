"""
Processador Avançado de Vídeos - Integração com Sistema RAG
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from video_processor import VideoProcessor
from thematic_analyzer import ThematicAnalyzer
from audio_generator import AudioGenerator
from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedVideoProcessor:
    """Processador avançado de vídeos integrado ao sistema RAG"""
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.thematic_analyzer = ThematicAnalyzer()
        self.audio_generator = AudioGenerator()
        
        # Cria diretórios para vídeos
        self.videos_dir = RAGFILES_DIR / "videos"
        self.videos_dir.mkdir(exist_ok=True)
        
        # Subdiretórios
        (self.videos_dir / "downloads").mkdir(exist_ok=True)
        (self.videos_dir / "transcriptions").mkdir(exist_ok=True)
        (self.videos_dir / "summaries").mkdir(exist_ok=True)
        (self.videos_dir / "audiobooks").mkdir(exist_ok=True)
    
    def process_documents_with_videos(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa documentos e extrai/processa vídeos encontrados"""
        try:
            logger.info(f"Processando {len(documents)} documentos com vídeos...")
            
            # 1. Extrai URLs de vídeo de todos os documentos
            all_video_urls = []
            document_video_map = {}
            
            for i, doc in enumerate(documents):
                content = doc.get('content', {})
                text = content.get('text', '')
                
                if text:
                    video_urls = self.video_processor.detect_video_urls(text)
                    if video_urls:
                        all_video_urls.extend(video_urls)
                        document_video_map[i] = video_urls
            
            if not all_video_urls:
                logger.info("Nenhuma URL de vídeo encontrada nos documentos")
                return {
                    'success': True,
                    'video_results': [],
                    'thematic_groups': {},
                    'summary': 'Nenhum vídeo encontrado para processar'
                }
            
            logger.info(f"Encontradas {len(all_video_urls)} URLs de vídeo")
            
            # 2. Processa cada vídeo
            video_results = []
            for video_info in all_video_urls:
                url = video_info['url']
                platform = video_info['platform_name']
                
                logger.info(f"Processando {platform}: {url}")
                
                result = self.video_processor.process_video_url(
                    url, 
                    str(self.videos_dir / "downloads")
                )
                
                if result['success']:
                    # Salva transcrição
                    self._save_transcription(result)
                    
                    # Salva resumo
                    self._save_summary(result)
                    
                    # Gera audiobook do resumo
                    self._generate_video_audiobook(result)
                
                video_results.append(result)
            
            # 3. Agrupa vídeos por tema
            thematic_groups = self._group_videos_by_theme(video_results)
            
            # 4. Gera resumo geral
            general_summary = self._generate_video_summary(video_results, thematic_groups)
            
            return {
                'success': True,
                'video_results': video_results,
                'thematic_groups': thematic_groups,
                'general_summary': general_summary,
                'stats': self._calculate_video_stats(video_results)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar documentos com vídeos: {e}")
            return {
                'success': False,
                'error': str(e),
                'video_results': [],
                'thematic_groups': {}
            }
    
    def _save_transcription(self, video_result: Dict[str, Any]):
        """Salva transcrição do vídeo"""
        try:
            if not video_result.get('transcription'):
                return
            
            transcription = video_result['transcription']
            url = video_result['url']
            
            # Cria nome do arquivo baseado na URL
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')
            transcription_file = self.videos_dir / "transcriptions" / f"{safe_url}_transcription.txt"
            
            # Salva transcrição
            with open(transcription_file, 'w', encoding='utf-8') as f:
                f.write(f"# Transcrição do Vídeo\n")
                f.write(f"**URL:** {url}\n")
                f.write(f"**Título:** {video_result.get('video_info', {}).get('title', 'N/A')}\n")
                f.write(f"**Duração:** {video_result.get('video_info', {}).get('duration', 0)} segundos\n")
                f.write(f"**Método:** {video_result.get('processing_info', {}).get('transcription_method', 'N/A')}\n")
                f.write(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                f.write(f"## Transcrição Completa\n\n")
                f.write(transcription['text'])
                
                if transcription.get('segments'):
                    f.write(f"\n\n## Segmentos Detalhados\n\n")
                    for i, segment in enumerate(transcription['segments'], 1):
                        start = segment.get('start', 0)
                        end = segment.get('end', 0)
                        text = segment.get('text', '')
                        f.write(f"**{i}. [{start:.1f}s - {end:.1f}s]** {text}\n")
            
            logger.info(f"Transcrição salva: {transcription_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar transcrição: {e}")
    
    def _save_summary(self, video_result: Dict[str, Any]):
        """Salva resumo do vídeo"""
        try:
            if not video_result.get('summary'):
                return
            
            summary = video_result['summary']
            url = video_result['url']
            
            # Cria nome do arquivo baseado na URL
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')
            summary_file = self.videos_dir / "summaries" / f"{safe_url}_summary.md"
            
            # Salva resumo
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Resumo do Vídeo\n")
                f.write(f"**URL:** {url}\n")
                f.write(f"**Título:** {video_result.get('video_info', {}).get('title', 'N/A')}\n")
                f.write(f"**Duração:** {video_result.get('video_info', {}).get('duration', 0)} segundos\n")
                f.write(f"**Método:** {video_result.get('processing_info', {}).get('summary_method', 'N/A')}\n")
                f.write(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                f.write(f"## Resumo\n\n")
                f.write(summary['text'])
                
                f.write(f"\n\n## Estatísticas\n\n")
                f.write(f"- **Texto original:** {summary['original_length']} caracteres\n")
                f.write(f"- **Resumo:** {summary['summary_length']} caracteres\n")
                f.write(f"- **Taxa de compressão:** {summary['compression_ratio']:.2%}\n")
            
            logger.info(f"Resumo salvo: {summary_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resumo: {e}")
    
    def _generate_video_audiobook(self, video_result: Dict[str, Any]):
        """Gera audiobook do resumo do vídeo"""
        try:
            if not video_result.get('summary'):
                return
            
            summary_text = video_result['summary']['text']
            url = video_result['url']
            
            # Cria nome do arquivo baseado na URL
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')
            audiobook_path = self.videos_dir / "audiobooks" / f"{safe_url}_audiobook.mp3"
            
            # Gera audiobook
            result = self.audio_generator.generate_audiobook(
                summary_text,
                str(audiobook_path),
                f"Resumo do Vídeo: {video_result.get('video_info', {}).get('title', 'N/A')}"
            )
            
            if result['success']:
                logger.info(f"Audiobook gerado: {audiobook_path}")
            else:
                logger.error(f"Erro ao gerar audiobook: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar audiobook do vídeo: {e}")
    
    def _group_videos_by_theme(self, video_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa vídeos por tema"""
        try:
            thematic_groups = {}
            
            for video_result in video_results:
                if not video_result.get('summary'):
                    continue
                
                summary_text = video_result['summary']['text']
                
                # Classifica tema do resumo
                theme, confidence = self.thematic_analyzer.classify_theme(summary_text)
                
                # Adiciona informações do tema ao resultado
                video_result['theme'] = theme
                video_result['theme_confidence'] = confidence
                video_result['theme_description'] = self.thematic_analyzer.predefined_themes.get(theme, {}).get('description', 'Tema Geral')
                
                # Agrupa por tema
                if theme not in thematic_groups:
                    thematic_groups[theme] = []
                
                thematic_groups[theme].append(video_result)
            
            return thematic_groups
            
        except Exception as e:
            logger.error(f"Erro ao agrupar vídeos por tema: {e}")
            return {}
    
    def _generate_video_summary(self, video_results: List[Dict[str, Any]], 
                               thematic_groups: Dict[str, List[Dict[str, Any]]]) -> str:
        """Gera resumo geral dos vídeos processados"""
        try:
            summary_parts = []
            
            summary_parts.append("# 🎥 Resumo de Vídeos Processados")
            summary_parts.append(f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            summary_parts.append("")
            
            # Estatísticas gerais
            total_videos = len(video_results)
            successful_videos = sum(1 for v in video_results if v.get('success'))
            total_themes = len(thematic_groups)
            
            summary_parts.append(f"## 📊 Estatísticas Gerais")
            summary_parts.append(f"- **Total de vídeos:** {total_videos}")
            summary_parts.append(f"- **Vídeos processados com sucesso:** {successful_videos}")
            summary_parts.append(f"- **Temas identificados:** {total_themes}")
            summary_parts.append(f"- **Taxa de sucesso:** {successful_videos/total_videos*100:.1f}%" if total_videos > 0 else "0%")
            summary_parts.append("")
            
            # Análise por tema
            summary_parts.append(f"## 🎯 Análise por Tema")
            summary_parts.append("")
            
            for theme, videos in thematic_groups.items():
                theme_info = self.thematic_analyzer.predefined_themes.get(theme, {})
                theme_description = theme_info.get('description', 'Tema Geral')
                
                summary_parts.append(f"### {theme_description}")
                summary_parts.append(f"- **Tema:** {theme}")
                summary_parts.append(f"- **Vídeos:** {len(videos)}")
                
                # Lista vídeos do tema
                for i, video in enumerate(videos, 1):
                    title = video.get('video_info', {}).get('title', 'N/A')
                    url = video.get('url', 'N/A')
                    confidence = video.get('theme_confidence', 0)
                    summary_parts.append(f"  {i}. [{title}]({url}) (confiança: {confidence:.2f})")
                
                summary_parts.append("")
            
            # Lista de vídeos processados
            summary_parts.append(f"## 📹 Vídeos Processados")
            summary_parts.append("")
            
            for i, video in enumerate(video_results, 1):
                title = video.get('video_info', {}).get('title', 'N/A')
                url = video.get('url', 'N/A')
                duration = video.get('video_info', {}).get('duration', 0)
                success = video.get('success', False)
                
                status = "✅ Sucesso" if success else "❌ Erro"
                summary_parts.append(f"### {i}. {title}")
                summary_parts.append(f"- **URL:** {url}")
                summary_parts.append(f"- **Duração:** {duration} segundos")
                summary_parts.append(f"- **Status:** {status}")
                
                if success and video.get('summary'):
                    summary_text = video['summary']['text']
                    summary_parts.append(f"- **Resumo:** {summary_text[:200]}...")
                
                summary_parts.append("")
            
            # Recomendações
            summary_parts.append(f"## 💡 Recomendações")
            summary_parts.append("")
            summary_parts.append(f"- **Vídeos mais relevantes:** {self._get_most_relevant_videos(video_results)}")
            summary_parts.append(f"- **Diversidade temática:** {'Alta' if total_themes > 5 else 'Média' if total_themes > 2 else 'Baixa'}")
            summary_parts.append(f"- **Próximos passos:** Revisar resumos e audiobooks gerados")
            summary_parts.append("")
            
            summary_parts.append("---")
            summary_parts.append("*Resumo de vídeos gerado automaticamente pelo Sistema RAG Local*")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo de vídeos: {e}")
            return f"Erro ao gerar resumo de vídeos: {str(e)}"
    
    def _get_most_relevant_videos(self, video_results: List[Dict[str, Any]]) -> str:
        """Retorna os vídeos mais relevantes"""
        try:
            # Ordena por duração (vídeos mais longos tendem a ser mais relevantes)
            sorted_videos = sorted(
                [v for v in video_results if v.get('success')],
                key=lambda x: x.get('video_info', {}).get('duration', 0),
                reverse=True
            )
            
            if len(sorted_videos) >= 2:
                title1 = sorted_videos[0].get('video_info', {}).get('title', 'N/A')
                title2 = sorted_videos[1].get('video_info', {}).get('title', 'N/A')
                return f"{title1}, {title2}"
            elif len(sorted_videos) == 1:
                return sorted_videos[0].get('video_info', {}).get('title', 'N/A')
            else:
                return "Nenhum vídeo processado com sucesso"
                
        except Exception as e:
            logger.error(f"Erro ao calcular vídeos relevantes: {e}")
            return "Erro na análise"
    
    def _calculate_video_stats(self, video_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estatísticas dos vídeos processados"""
        try:
            total_videos = len(video_results)
            successful_videos = sum(1 for v in video_results if v.get('success'))
            
            # Duração total
            total_duration = sum(
                v.get('video_info', {}).get('duration', 0) 
                for v in video_results if v.get('success')
            )
            
            # Temas identificados
            themes = set()
            for video in video_results:
                if video.get('theme'):
                    themes.add(video['theme'])
            
            return {
                'total_videos': total_videos,
                'successful_videos': successful_videos,
                'success_rate': (successful_videos / total_videos * 100) if total_videos > 0 else 0,
                'total_duration': total_duration,
                'themes_identified': len(themes),
                'average_duration': total_duration / successful_videos if successful_videos > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o processador avançado de vídeos"""
        return {
            'name': 'EnhancedVideoProcessor',
            'version': '1.0.0',
            'description': 'Processador avançado de vídeos integrado ao sistema RAG',
            'features': [
                'Detecção automática de URLs de vídeo',
                'Download e transcrição de vídeos',
                'Resumo automático de vídeos',
                'Geração de audiobooks',
                'Agrupamento temático de vídeos',
                'Integração com sistema RAG'
            ],
            'dependencies': {
                'video_processor': self.video_processor.get_processor_info(),
                'thematic_analyzer': self.thematic_analyzer.get_processor_info(),
                'audio_generator': self.audio_generator.get_processor_info()
            }
        }
