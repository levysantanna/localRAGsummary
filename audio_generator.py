"""
Gerador de Audiobooks em Português
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Text-to-Speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 não disponível. Instale com: pip install pyttsx3")

# Alternative TTS
try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS não disponível. Instale com: pip install gtts pygame")

# Audio processing
try:
    import pydub
    from pydub import AudioSegment
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
    logger.warning("pydub não disponível. Instale com: pip install pydub")

from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioGenerator:
    """Gerador de audiobooks em português"""
    
    def __init__(self):
        self.setup_tts()
        self.audio_quality = {
            'sample_rate': 22050,
            'channels': 1,
            'format': 'mp3',
            'bitrate': '128k'
        }
        
        # Configurações de voz em português
        self.voice_settings = {
            'language': 'pt-br',
            'rate': 180,  # Velocidade da fala
            'volume': 0.9,  # Volume
            'pitch': 0.5  # Tom da voz
        }
    
    def setup_tts(self):
        """Configura o sistema de text-to-speech"""
        try:
            if TTS_AVAILABLE:
                self.tts_engine = pyttsx3.init()
                self._configure_voice()
                logger.info("Sistema TTS configurado com sucesso")
            else:
                self.tts_engine = None
                logger.warning("Sistema TTS não disponível")
        except Exception as e:
            logger.error(f"Erro ao configurar TTS: {e}")
            self.tts_engine = None
    
    def _configure_voice(self):
        """Configura a voz em português"""
        try:
            if not self.tts_engine:
                return
            
            # Configura propriedades da voz
            self.tts_engine.setProperty('rate', self.voice_settings['rate'])
            self.tts_engine.setProperty('volume', self.voice_settings['volume'])
            
            # Tenta encontrar uma voz em português
            voices = self.tts_engine.getProperty('voices')
            portuguese_voice = None
            
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                    portuguese_voice = voice
                    break
            
            if portuguese_voice:
                self.tts_engine.setProperty('voice', portuguese_voice.id)
                logger.info(f"Voz em português configurada: {portuguese_voice.name}")
            else:
                logger.warning("Voz em português não encontrada. Usando voz padrão.")
                
        except Exception as e:
            logger.error(f"Erro ao configurar voz: {e}")
    
    def generate_audiobook(self, text: str, output_path: str, title: str = "Audiobook") -> Dict[str, Any]:
        """Gera audiobook a partir do texto"""
        try:
            # Limpa e formata o texto
            cleaned_text = self._clean_text_for_speech(text)
            
            if not cleaned_text:
                return {
                    'success': False,
                    'error': 'Texto vazio ou inválido',
                    'output_path': None
                }
            
            # Gera áudio
            if TTS_AVAILABLE and self.tts_engine:
                return self._generate_with_pyttsx3(cleaned_text, output_path, title)
            elif GTTS_AVAILABLE:
                return self._generate_with_gtts(cleaned_text, output_path, title)
            else:
                return {
                    'success': False,
                    'error': 'Nenhum sistema TTS disponível',
                    'output_path': None
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar audiobook: {e}")
            return {
                'success': False,
                'error': str(e),
                'output_path': None
            }
    
    def _generate_with_pyttsx3(self, text: str, output_path: str, title: str) -> Dict[str, Any]:
        """Gera audiobook usando pyttsx3"""
        try:
            # Divide o texto em chunks para evitar problemas de memória
            chunks = self._split_text_into_chunks(text, max_length=1000)
            
            # Gera áudio para cada chunk
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processando chunk {i+1}/{len(chunks)}")
                
                # Gera áudio do chunk
                chunk_path = f"{output_path}_chunk_{i}.wav"
                self.tts_engine.save_to_file(chunk, chunk_path)
                self.tts_engine.runAndWait()
                
                # Carrega o áudio gerado
                if os.path.exists(chunk_path):
                    if AUDIO_PROCESSING_AVAILABLE:
                        audio_segments.append(AudioSegment.from_wav(chunk_path))
                    os.remove(chunk_path)  # Remove arquivo temporário
            
            # Combina todos os chunks
            if audio_segments and AUDIO_PROCESSING_AVAILABLE:
                final_audio = sum(audio_segments)
                final_audio.export(output_path, format="mp3", bitrate="128k")
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'duration': len(final_audio) / 1000,  # Duração em segundos
                    'method': 'pyttsx3'
                }
            else:
                return {
                    'success': False,
                    'error': 'Erro ao processar áudio',
                    'output_path': None
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar audiobook com pyttsx3: {e}")
            return {
                'success': False,
                'error': str(e),
                'output_path': None
            }
    
    def _generate_with_gtts(self, text: str, output_path: str, title: str) -> Dict[str, Any]:
        """Gera audiobook usando gTTS (Google Text-to-Speech)"""
        try:
            # Divide o texto em chunks
            chunks = self._split_text_into_chunks(text, max_length=500)
            
            # Gera áudio para cada chunk
            audio_segments = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processando chunk {i+1}/{len(chunks)} com gTTS")
                
                # Gera áudio do chunk
                tts = gTTS(text=chunk, lang='pt-br', slow=False)
                chunk_path = f"{output_path}_chunk_{i}.mp3"
                tts.save(chunk_path)
                
                # Carrega o áudio gerado
                if os.path.exists(chunk_path):
                    if AUDIO_PROCESSING_AVAILABLE:
                        audio_segments.append(AudioSegment.from_mp3(chunk_path))
                    os.remove(chunk_path)  # Remove arquivo temporário
            
            # Combina todos os chunks
            if audio_segments and AUDIO_PROCESSING_AVAILABLE:
                final_audio = sum(audio_segments)
                final_audio.export(output_path, format="mp3", bitrate="128k")
                
                return {
                    'success': True,
                    'output_path': output_path,
                    'duration': len(final_audio) / 1000,  # Duração em segundos
                    'method': 'gTTS'
                }
            else:
                return {
                    'success': False,
                    'error': 'Erro ao processar áudio',
                    'output_path': None
                }
                
        except Exception as e:
            logger.error(f"Erro ao gerar audiobook com gTTS: {e}")
            return {
                'success': False,
                'error': str(e),
                'output_path': None
            }
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Limpa e formata o texto para síntese de voz"""
        try:
            # Remove caracteres especiais
            text = re.sub(r'[^\w\s.,!?;:]', '', text)
            
            # Remove quebras de linha excessivas
            text = re.sub(r'\n+', '\n', text)
            
            # Remove espaços extras
            text = re.sub(r'\s+', ' ', text)
            
            # Remove URLs
            text = re.sub(r'http[s]?://\S+', '', text)
            
            # Remove emails
            text = re.sub(r'\S+@\S+', '', text)
            
            # Remove números excessivos
            text = re.sub(r'\d+', '', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erro ao limpar texto: {e}")
            return text
    
    def _split_text_into_chunks(self, text: str, max_length: int = 1000) -> List[str]:
        """Divide o texto em chunks menores"""
        try:
            sentences = text.split('. ')
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk + sentence) < max_length:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks
            
        except Exception as e:
            logger.error(f"Erro ao dividir texto: {e}")
            return [text]
    
    def generate_thematic_audiobooks(self, thematic_groups: Dict[str, List[Dict[str, Any]]], 
                                   thematic_dirs: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Gera audiobooks para cada tema"""
        try:
            audiobook_results = {}
            
            for theme, docs in thematic_groups.items():
                if theme not in thematic_dirs:
                    continue
                
                logger.info(f"Gerando audiobook para tema: {theme}")
                
                # Combina texto de todos os documentos do tema
                combined_text = self._combine_documents_text(docs)
                
                if not combined_text:
                    continue
                
                # Gera audiobook
                theme_dir = Path(thematic_dirs[theme])
                audiobook_path = theme_dir / "audiobooks" / f"{theme}_audiobook.mp3"
                
                result = self.generate_audiobook(
                    combined_text, 
                    str(audiobook_path),
                    f"Audiobook - {theme}"
                )
                
                audiobook_results[theme] = result
                
                if result['success']:
                    logger.info(f"Audiobook gerado: {audiobook_path}")
                else:
                    logger.error(f"Erro ao gerar audiobook para {theme}: {result.get('error')}")
            
            return audiobook_results
            
        except Exception as e:
            logger.error(f"Erro ao gerar audiobooks temáticos: {e}")
            return {}
    
    def _combine_documents_text(self, docs: List[Dict[str, Any]]) -> str:
        """Combina texto de múltiplos documentos"""
        try:
            combined_parts = []
            
            for doc in docs:
                content = doc.get('content', {})
                text = content.get('text', '')
                
                if text:
                    # Adiciona título do documento
                    file_path = Path(doc.get('file_path', '')).name
                    combined_parts.append(f"\n--- {file_path} ---\n")
                    combined_parts.append(text)
                    combined_parts.append("\n")
            
            return "\n".join(combined_parts)
            
        except Exception as e:
            logger.error(f"Erro ao combinar textos: {e}")
            return ""
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o gerador de áudio"""
        return {
            'name': 'AudioGenerator',
            'version': '1.0.0',
            'description': 'Gerador de audiobooks em português',
            'supported_formats': ['mp3', 'wav'],
            'tts_engines': {
                'pyttsx3': TTS_AVAILABLE,
                'gTTS': GTTS_AVAILABLE
            },
            'features': [
                'Síntese de voz em português',
                'Geração de audiobooks',
                'Processamento de áudio',
                'Divisão de texto em chunks',
                'Limpeza automática de texto'
            ]
        }
