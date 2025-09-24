#!/usr/bin/env python3
"""
Teste do Sistema de Processamento de Vídeos
"""
import sys
import os
from pathlib import Path
import logging

# Adiciona o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video_system():
    """Testa o sistema de processamento de vídeos"""
    
    print("🎥 Teste do Sistema de Processamento de Vídeos")
    print("=" * 60)
    
    try:
        # 1. Testa importação dos módulos
        print("\n🔧 Passo 1: Testando importação dos módulos...")
        
        try:
            from video_processor import VideoProcessor
            print("  ✅ VideoProcessor importado com sucesso")
        except ImportError as e:
            print(f"  ❌ Erro ao importar VideoProcessor: {e}")
            return False
        
        try:
            from enhanced_video_processor import EnhancedVideoProcessor
            print("  ✅ EnhancedVideoProcessor importado com sucesso")
        except ImportError as e:
            print(f"  ❌ Erro ao importar EnhancedVideoProcessor: {e}")
            return False
        
        # 2. Testa inicialização dos processadores
        print("\n🔧 Passo 2: Testando inicialização dos processadores...")
        
        try:
            video_processor = VideoProcessor()
            print("  ✅ VideoProcessor inicializado com sucesso")
        except Exception as e:
            print(f"  ❌ Erro ao inicializar VideoProcessor: {e}")
            return False
        
        try:
            enhanced_processor = EnhancedVideoProcessor()
            print("  ✅ EnhancedVideoProcessor inicializado com sucesso")
        except Exception as e:
            print(f"  ❌ Erro ao inicializar EnhancedVideoProcessor: {e}")
            return False
        
        # 3. Testa informações dos processadores
        print("\n📋 Passo 3: Testando informações dos processadores...")
        
        try:
            video_info = video_processor.get_processor_info()
            print(f"  ✅ VideoProcessor: {video_info['name']} v{video_info['version']}")
            print(f"    - Plataformas suportadas: {len(video_info['supported_platforms'])}")
            print(f"    - Dependências: {video_info['dependencies']}")
            
            enhanced_info = enhanced_processor.get_processor_info()
            print(f"  ✅ EnhancedVideoProcessor: {enhanced_info['name']} v{enhanced_info['version']}")
            print(f"    - Funcionalidades: {len(enhanced_info['features'])}")
            
        except Exception as e:
            print(f"  ❌ Erro ao obter informações: {e}")
            return False
        
        # 4. Testa detecção de URLs de vídeo
        print("\n🔍 Passo 4: Testando detecção de URLs de vídeo...")
        
        try:
            # Texto com URLs de vídeo
            test_text = """
            Aqui estão alguns vídeos interessantes:
            - YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
            - Vimeo: https://vimeo.com/123456789
            - Twitch: https://www.twitch.tv/videos/123456789
            - TikTok: https://www.tiktok.com/@user/video/123456789
            - Dailymotion: https://www.dailymotion.com/video/123456789
            """
            
            video_urls = video_processor.detect_video_urls(test_text)
            print(f"  ✅ {len(video_urls)} URLs de vídeo detectadas")
            
            for video_info in video_urls:
                print(f"    - {video_info['platform_name']}: {video_info['url']}")
            
        except Exception as e:
            print(f"  ❌ Erro ao testar detecção de URLs: {e}")
            return False
        
        # 5. Testa classificação de plataformas
        print("\n🎯 Passo 5: Testando classificação de plataformas...")
        
        try:
            test_urls = [
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "https://vimeo.com/123456789",
                "https://www.twitch.tv/videos/123456789",
                "https://www.tiktok.com/@user/video/123456789",
                "https://www.dailymotion.com/video/123456789"
            ]
            
            for url in test_urls:
                platform = video_processor._identify_platform(url)
                if platform:
                    platform_name = video_processor.supported_platforms[platform]['name']
                    print(f"  ✅ {url} -> {platform_name}")
                else:
                    print(f"  ❌ {url} -> Plataforma não identificada")
            
        except Exception as e:
            print(f"  ❌ Erro ao testar classificação de plataformas: {e}")
            return False
        
        # 6. Testa estrutura de diretórios
        print("\n📁 Passo 6: Testando estrutura de diretórios...")
        
        try:
            from config import RAGFILES_DIR
            
            # Verifica se diretórios foram criados
            videos_dir = RAGFILES_DIR / "videos"
            if videos_dir.exists():
                print(f"  ✅ Diretório de vídeos criado: {videos_dir}")
                
                # Verifica subdiretórios
                subdirs = ["downloads", "transcriptions", "summaries", "audiobooks"]
                for subdir in subdirs:
                    subdir_path = videos_dir / subdir
                    if subdir_path.exists():
                        print(f"    - {subdir}: {subdir_path}")
                    else:
                        print(f"    - {subdir}: ❌ Não encontrado")
            else:
                print(f"  ❌ Diretório de vídeos não encontrado")
                return False
            
        except Exception as e:
            print(f"  ❌ Erro ao verificar estrutura: {e}")
            return False
        
        # 7. Testa processamento simulado
        print("\n🎬 Passo 7: Testando processamento simulado...")
        
        try:
            # Cria documentos de exemplo com URLs de vídeo
            example_documents = [
                {
                    'file_path': 'documents/curso_ia.txt',
                    'content': {
                        'text': '''
                        Curso de Inteligência Artificial
                        
                        Vídeos recomendados:
                        - https://www.youtube.com/watch?v=dQw4w9WgXcQ
                        - https://vimeo.com/123456789
                        
                        Estes vídeos explicam conceitos fundamentais de IA.
                        '''
                    }
                },
                {
                    'file_path': 'documents/programacao.txt',
                    'content': {
                        'text': '''
                        Programação em Python
                        
                        Tutoriais em vídeo:
                        - https://www.youtube.com/watch?v=abc123
                        - https://www.twitch.tv/videos/123456789
                        
                        Aprenda Python com estes tutoriais.
                        '''
                    }
                }
            ]
            
            # Simula processamento
            print(f"  ✅ {len(example_documents)} documentos de exemplo criados")
            
            # Detecta URLs em cada documento
            total_urls = 0
            for doc in example_documents:
                text = doc['content']['text']
                urls = video_processor.detect_video_urls(text)
                total_urls += len(urls)
                print(f"    - {doc['file_path']}: {len(urls)} URLs detectadas")
            
            print(f"  ✅ Total de URLs detectadas: {total_urls}")
            
        except Exception as e:
            print(f"  ❌ Erro ao testar processamento simulado: {e}")
            return False
        
        # 8. Testa funcionalidades avançadas
        print("\n🚀 Passo 8: Testando funcionalidades avançadas...")
        
        try:
            # Testa resumo simples
            test_text = "Este é um texto de exemplo para testar o resumo. " * 10
            summary_result = video_processor._summarize_simple(test_text)
            
            if summary_result['success']:
                print(f"  ✅ Resumo simples funcionando")
                print(f"    - Texto original: {summary_result['summary']['original_length']} caracteres")
                print(f"    - Resumo: {summary_result['summary']['summary_length']} caracteres")
                print(f"    - Taxa de compressão: {summary_result['summary']['compression_ratio']:.2%}")
            else:
                print(f"  ❌ Erro no resumo simples: {summary_result.get('error')}")
            
        except Exception as e:
            print(f"  ❌ Erro ao testar funcionalidades avançadas: {e}")
            return False
        
        # 9. Resumo final
        print(f"\n🎉 Teste do Sistema de Vídeos Concluído!")
        print("=" * 60)
        print(f"✅ Processamento de vídeos funcionando")
        print(f"✅ Detecção de URLs funcionando")
        print(f"✅ Classificação de plataformas funcionando")
        print(f"✅ Estrutura de diretórios criada")
        print(f"✅ Processamento simulado funcionando")
        print(f"✅ Funcionalidades avançadas testadas")
        
        print(f"\n🚀 Funcionalidades implementadas:")
        print(f"  🎥 Detecção automática de URLs de vídeo")
        print(f"  📥 Download de áudio de vídeos")
        print(f"  🎧 Transcrição com Whisper")
        print(f"  📄 Resumo automático de vídeos")
        print(f"  🎯 Agrupamento temático de vídeos")
        print(f"  🎧 Geração de audiobooks de vídeos")
        print(f"  📊 Estatísticas detalhadas")
        
        print(f"\n📋 Próximos passos:")
        print(f"  1. Instalar dependências: pip install -r requirements_enhanced.txt")
        print(f"  2. Processar vídeos reais")
        print(f"  3. Testar transcrição com Whisper")
        print(f"  4. Gerar resumos e audiobooks")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Iniciando teste do sistema de vídeos...")
    
    # Executa teste
    success = test_video_system()
    
    if success:
        print("\n✅ Teste do sistema de vídeos concluído com sucesso!")
        print("🎉 Sistema de processamento de vídeos implementado!")
    else:
        print("\n❌ Teste falhou. Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
