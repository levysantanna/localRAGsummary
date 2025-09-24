"""
Processador de Vídeos de Streaming - Transcrição e Resumo
"""
import logging
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

# Video processing
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logger.warning("yt-dlp não disponível. Instale com: pip install yt-dlp")

# Audio processing
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("whisper não disponível. Instale com: pip install openai-whisper")

# Alternative transcription
try:
    from speech_recognition import AudioFile, Recognizer
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition não disponível. Instale com: pip install SpeechRecognition")

# Text processing
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers não disponível. Instale com: pip install transformers")

from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """Processador de vídeos de streaming com transcrição e resumo"""
    
    def __init__(self):
        self.setup_whisper()
        self.setup_transformers()
        
        # Configurações de download
        self.download_config = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'extractaudio': True,
            'audioformat': 'wav',
            'audioquality': '0'
        }
        
        # Plataformas suportadas
        self.supported_platforms = {
            'youtube': {
                'patterns': [
                    r'youtube\.com/watch\?v=',
                    r'youtu\.be/',
                    r'youtube\.com/embed/',
                    r'youtube\.com/v/'
                ],
                'name': 'YouTube'
            },
            'vimeo': {
                'patterns': [
                    r'vimeo\.com/',
                    r'player\.vimeo\.com/'
                ],
                'name': 'Vimeo'
            },
            'twitch': {
                'patterns': [
                    r'twitch\.tv/',
                    r'twitch\.tv/videos/'
                ],
                'name': 'Twitch'
            },
            'dailymotion': {
                'patterns': [
                    r'dailymotion\.com/',
                    r'dai\.ly/'
                ],
                'name': 'Dailymotion'
            },
            'tiktok': {
                'patterns': [
                    r'tiktok\.com/',
                    r'vm\.tiktok\.com/'
                ],
                'name': 'TikTok'
            }
        }
    
    def setup_whisper(self):
        """Configura o modelo Whisper para transcrição"""
        try:
            if WHISPER_AVAILABLE:
                # Carrega modelo Whisper (baseado no tamanho disponível)
                self.whisper_model = whisper.load_model("base")
                logger.info("Modelo Whisper carregado com sucesso")
            else:
                self.whisper_model = None
                logger.warning("Whisper não disponível")
        except Exception as e:
            logger.error(f"Erro ao configurar Whisper: {e}")
            self.whisper_model = None
    
    def setup_transformers(self):
        """Configura pipeline de resumo"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Pipeline de resumo em português
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    tokenizer="facebook/bart-large-cnn"
                )
                logger.info("Pipeline de resumo configurado")
            else:
                self.summarizer = None
                logger.warning("Transformers não disponível")
        except Exception as e:
            logger.error(f"Erro ao configurar pipeline de resumo: {e}")
            self.summarizer = None
    
    def detect_video_urls(self, text: str) -> List[Dict[str, Any]]:
        """Detecta URLs de vídeo no texto"""
        try:
            video_urls = []
            
            # Padrões de URL de vídeo
            url_patterns = [
                r'https?://[^\s]+',
                r'www\.[^\s]+',
                r'[^\s]+\.(com|org|net|tv|io)/[^\s]+'
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # Verifica se é uma URL de vídeo
                    platform = self._identify_platform(match)
                    if platform:
                        video_urls.append({
                            'url': match,
                            'platform': platform,
                            'platform_name': self.supported_platforms[platform]['name']
                        })
            
            return video_urls
            
        except Exception as e:
            logger.error(f"Erro ao detectar URLs de vídeo: {e}")
            return []
    
    def _identify_platform(self, url: str) -> Optional[str]:
        """Identifica a plataforma de vídeo"""
        try:
            for platform, info in self.supported_platforms.items():
                for pattern in info['patterns']:
                    if re.search(pattern, url, re.IGNORECASE):
                        return platform
            return None
        except Exception as e:
            logger.error(f"Erro ao identificar plataforma: {e}")
            return None
    
    def download_video_audio(self, url: str, output_dir: str) -> Dict[str, Any]:
        """Baixa o áudio de um vídeo"""
        try:
            if not YT_DLP_AVAILABLE:
                return {
                    'success': False,
                    'error': 'yt-dlp não disponível',
                    'audio_path': None
                }
            
            # Configura yt-dlp
            ydl_opts = self.download_config.copy()
            ydl_opts['outtmpl'] = os.path.join(output_dir, '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extrai informações do vídeo
                info = ydl.extract_info(url, download=False)
                
                # Baixa o áudio
                ydl.download([url])
                
                # Encontra o arquivo baixado
                audio_files = list(Path(output_dir).glob("*.wav"))
                if not audio_files:
                    audio_files = list(Path(output_dir).glob("*.mp3"))
                
                if audio_files:
                    audio_path = str(audio_files[0])
                    return {
                        'success': True,
                        'audio_path': audio_path,
                        'video_info': {
                            'title': info.get('title', ''),
                            'duration': info.get('duration', 0),
                            'uploader': info.get('uploader', ''),
                            'description': info.get('description', ''),
                            'view_count': info.get('view_count', 0)
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Arquivo de áudio não encontrado',
                        'audio_path': None
                    }
                    
        except Exception as e:
            logger.error(f"Erro ao baixar áudio do vídeo: {e}")
            return {
                'success': False,
                'error': str(e),
                'audio_path': None
            }
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcreve áudio para texto"""
        try:
            if not audio_path or not os.path.exists(audio_path):
                return {
                    'success': False,
                    'error': 'Arquivo de áudio não encontrado',
                    'transcription': None
                }
            
            # Tenta usar Whisper primeiro
            if WHISPER_AVAILABLE and self.whisper_model:
                return self._transcribe_with_whisper(audio_path)
            
            # Fallback para speech_recognition
            elif SPEECH_RECOGNITION_AVAILABLE:
                return self._transcribe_with_speech_recognition(audio_path)
            
            else:
                return {
                    'success': False,
                    'error': 'Nenhum sistema de transcrição disponível',
                    'transcription': None
                }
                
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcription': None
            }
    
    def _transcribe_with_whisper(self, audio_path: str) -> Dict[str, Any]:
        """Transcreve usando Whisper"""
        try:
            logger.info(f"Transcrevendo com Whisper: {audio_path}")
            
            # Transcreve o áudio
            result = self.whisper_model.transcribe(audio_path, language='pt')
            
            # Extrai texto e segmentos
            transcription_text = result['text']
            segments = result.get('segments', [])
            
            return {
                'success': True,
                'transcription': {
                    'text': transcription_text,
                    'segments': segments,
                    'language': result.get('language', 'pt'),
                    'duration': result.get('duration', 0)
                },
                'method': 'whisper'
            }
            
        except Exception as e:
            logger.error(f"Erro na transcrição com Whisper: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcription': None
            }
    
    def _transcribe_with_speech_recognition(self, audio_path: str) -> Dict[str, Any]:
        """Transcreve usando speech_recognition"""
        try:
            logger.info(f"Transcrevendo com speech_recognition: {audio_path}")
            
            recognizer = Recognizer()
            
            with AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            
            # Tenta reconhecer em português
            try:
                text = recognizer.recognize_google(audio, language='pt-BR')
            except:
                # Fallback para inglês
                text = recognizer.recognize_google(audio, language='en-US')
            
            return {
                'success': True,
                'transcription': {
                    'text': text,
                    'segments': [],
                    'language': 'pt-BR',
                    'duration': 0
                },
                'method': 'speech_recognition'
            }
            
        except Exception as e:
            logger.error(f"Erro na transcrição com speech_recognition: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcription': None
            }
    
    def summarize_transcription(self, transcription: str) -> Dict[str, Any]:
        """Resume a transcrição"""
        try:
            if not transcription or len(transcription.strip()) < 100:
                return {
                    'success': False,
                    'error': 'Transcrição muito curta para resumir',
                    'summary': None
                }
            
            # Usa pipeline de resumo se disponível
            if TRANSFORMERS_AVAILABLE and self.summarizer:
                return self._summarize_with_transformers(transcription)
            
            # Fallback para resumo simples
            else:
                return self._summarize_simple(transcription)
                
        except Exception as e:
            logger.error(f"Erro ao resumir transcrição: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }
    
    def _summarize_with_transformers(self, text: str) -> Dict[str, Any]:
        """Resume usando transformers"""
        try:
            # Divide texto em chunks se muito longo
            max_length = 1024
            if len(text) > max_length:
                chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
                summaries = []
                
                for chunk in chunks:
                    summary = self.summarizer(chunk, max_length=150, min_length=50, do_sample=False)
                    summaries.append(summary[0]['summary_text'])
                
                final_summary = ' '.join(summaries)
            else:
                summary = self.summarizer(text, max_length=150, min_length=50, do_sample=False)
                final_summary = summary[0]['summary_text']
            
            return {
                'success': True,
                'summary': {
                    'text': final_summary,
                    'original_length': len(text),
                    'summary_length': len(final_summary),
                    'compression_ratio': len(final_summary) / len(text)
                },
                'method': 'transformers'
            }
            
        except Exception as e:
            logger.error(f"Erro no resumo com transformers: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }
    
    def _summarize_simple(self, text: str) -> Dict[str, Any]:
        """Resumo simples baseado em sentenças"""
        try:
            # Divide em sentenças
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Seleciona as primeiras sentenças (resumo simples)
            summary_sentences = sentences[:3] if len(sentences) > 3 else sentences
            summary_text = '. '.join(summary_sentences) + '.'
            
            return {
                'success': True,
                'summary': {
                    'text': summary_text,
                    'original_length': len(text),
                    'summary_length': len(summary_text),
                    'compression_ratio': len(summary_text) / len(text)
                },
                'method': 'simple'
            }
            
        except Exception as e:
            logger.error(f"Erro no resumo simples: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }
    
    def process_video_url(self, url: str, output_dir: str) -> Dict[str, Any]:
        """Processa um vídeo completo: download, transcrição e resumo"""
        try:
            logger.info(f"Processando vídeo: {url}")
            
            # 1. Baixa o áudio
            download_result = self.download_video_audio(url, output_dir)
            if not download_result['success']:
                return download_result
            
            # 2. Transcreve o áudio
            transcription_result = self.transcribe_audio(download_result['audio_path'])
            if not transcription_result['success']:
                return transcription_result
            
            # 3. Resume a transcrição
            summary_result = self.summarize_transcription(
                transcription_result['transcription']['text']
            )
            
            # 4. Combina resultados
            return {
                'success': True,
                'url': url,
                'video_info': download_result.get('video_info', {}),
                'transcription': transcription_result['transcription'],
                'summary': summary_result.get('summary', {}),
                'audio_path': download_result['audio_path'],
                'processing_info': {
                    'download_success': download_result['success'],
                    'transcription_success': transcription_result['success'],
                    'summary_success': summary_result['success'],
                    'transcription_method': transcription_result.get('method', 'unknown'),
                    'summary_method': summary_result.get('method', 'unknown')
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar vídeo: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def process_video_urls_from_text(self, text: str, output_dir: str) -> List[Dict[str, Any]]:
        """Processa todas as URLs de vídeo encontradas no texto"""
        try:
            # Detecta URLs de vídeo
            video_urls = self.detect_video_urls(text)
            
            if not video_urls:
                logger.info("Nenhuma URL de vídeo encontrada no texto")
                return []
            
            logger.info(f"Encontradas {len(video_urls)} URLs de vídeo")
            
            # Processa cada URL
            results = []
            for video_info in video_urls:
                url = video_info['url']
                platform = video_info['platform_name']
                
                logger.info(f"Processando {platform}: {url}")
                
                result = self.process_video_url(url, output_dir)
                result['platform'] = platform
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao processar URLs de vídeo: {e}")
            return []
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o processador de vídeo"""
        return {
            'name': 'VideoProcessor',
            'version': '1.0.0',
            'description': 'Processador de vídeos de streaming com transcrição e resumo',
            'supported_platforms': list(self.supported_platforms.keys()),
            'features': [
                'Detecção automática de URLs de vídeo',
                'Download de áudio de vídeos',
                'Transcrição com Whisper',
                'Resumo automático de transcrições',
                'Suporte a múltiplas plataformas'
            ],
            'dependencies': {
                'yt_dlp': YT_DLP_AVAILABLE,
                'whisper': WHISPER_AVAILABLE,
                'speech_recognition': SPEECH_RECOGNITION_AVAILABLE,
                'transformers': TRANSFORMERS_AVAILABLE
            }
        }
