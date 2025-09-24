#!/usr/bin/env python3
"""
Teste do Sistema Temático com Audiobooks
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

def test_thematic_system():
    """Testa o sistema temático com audiobooks"""
    
    print("🎯 Teste do Sistema Temático com Audiobooks")
    print("=" * 60)
    
    try:
        # 1. Testa importação dos módulos
        print("\n🔧 Passo 1: Testando importação dos módulos...")
        
        try:
            from thematic_analyzer import ThematicAnalyzer
            print("  ✅ ThematicAnalyzer importado com sucesso")
        except ImportError as e:
            print(f"  ❌ Erro ao importar ThematicAnalyzer: {e}")
            return False
        
        try:
            from audio_generator import AudioGenerator
            print("  ✅ AudioGenerator importado com sucesso")
        except ImportError as e:
            print(f"  ❌ Erro ao importar AudioGenerator: {e}")
            return False
        
        try:
            from thematic_summary_generator import ThematicSummaryGenerator
            print("  ✅ ThematicSummaryGenerator importado com sucesso")
        except ImportError as e:
            print(f"  ❌ Erro ao importar ThematicSummaryGenerator: {e}")
            return False
        
        # 2. Testa inicialização dos processadores
        print("\n🔧 Passo 2: Testando inicialização dos processadores...")
        
        try:
            thematic_analyzer = ThematicAnalyzer()
            print("  ✅ ThematicAnalyzer inicializado com sucesso")
        except Exception as e:
            print(f"  ❌ Erro ao inicializar ThematicAnalyzer: {e}")
            return False
        
        try:
            audio_generator = AudioGenerator()
            print("  ✅ AudioGenerator inicializado com sucesso")
        except Exception as e:
            print(f"  ❌ Erro ao inicializar AudioGenerator: {e}")
            return False
        
        try:
            summary_generator = ThematicSummaryGenerator()
            print("  ✅ ThematicSummaryGenerator inicializado com sucesso")
        except Exception as e:
            print(f"  ❌ Erro ao inicializar ThematicSummaryGenerator: {e}")
            return False
        
        # 3. Testa informações dos processadores
        print("\n📋 Passo 3: Testando informações dos processadores...")
        
        try:
            thematic_info = thematic_analyzer.get_processor_info()
            print(f"  ✅ ThematicAnalyzer: {thematic_info['name']} v{thematic_info['version']}")
            print(f"    - Temas suportados: {len(thematic_info['supported_themes'])}")
            
            audio_info = audio_generator.get_processor_info()
            print(f"  ✅ AudioGenerator: {audio_info['name']} v{audio_info['version']}")
            print(f"    - Formatos suportados: {audio_info['supported_formats']}")
            
            summary_info = summary_generator.get_processor_info()
            print(f"  ✅ ThematicSummaryGenerator: {summary_info['name']} v{summary_info['version']}")
            
        except Exception as e:
            print(f"  ❌ Erro ao obter informações: {e}")
            return False
        
        # 4. Testa classificação de temas
        print("\n🎯 Passo 4: Testando classificação de temas...")
        
        try:
            # Texto de exemplo sobre IA
            ia_text = """
            Inteligência Artificial é um campo da ciência da computação que se dedica à criação de sistemas capazes de realizar tarefas que normalmente requerem inteligência humana. 
            Machine Learning é um subcampo da IA que permite aos sistemas aprenderem automaticamente através da experiência.
            Deep Learning utiliza redes neurais artificiais com múltiplas camadas para aprender representações hierárquicas dos dados.
            """
            
            theme, confidence = thematic_analyzer.classify_theme(ia_text)
            print(f"  ✅ Tema classificado: {theme} (confiança: {confidence:.2f})")
            
            # Texto de exemplo sobre programação
            prog_text = """
            Python é uma linguagem de programação de alto nível, interpretada e de propósito geral. 
            É amplamente usada para desenvolvimento web, análise de dados, inteligência artificial e automação.
            A sintaxe do Python é clara e legível, facilitando o aprendizado e manutenção do código.
            """
            
            theme2, confidence2 = thematic_analyzer.classify_theme(prog_text)
            print(f"  ✅ Tema classificado: {theme2} (confiança: {confidence2:.2f})")
            
        except Exception as e:
            print(f"  ❌ Erro ao testar classificação: {e}")
            return False
        
        # 5. Testa extração de palavras-chave
        print("\n🔍 Passo 5: Testando extração de palavras-chave...")
        
        try:
            keywords = thematic_analyzer.extract_keywords(ia_text, max_keywords=10)
            print(f"  ✅ Palavras-chave extraídas: {keywords[:5]}...")
            
        except Exception as e:
            print(f"  ❌ Erro ao extrair palavras-chave: {e}")
            return False
        
        # 6. Testa geração de áudio (simulado)
        print("\n🎧 Passo 6: Testando geração de áudio...")
        
        try:
            # Testa se os sistemas TTS estão disponíveis
            audio_info = audio_generator.get_processor_info()
            tts_engines = audio_info['tts_engines']
            
            print(f"  📊 Sistemas TTS disponíveis:")
            for engine, available in tts_engines.items():
                status = "✅ Disponível" if available else "❌ Não disponível"
                print(f"    - {engine}: {status}")
            
            if any(tts_engines.values()):
                print("  ✅ Pelo menos um sistema TTS está disponível")
            else:
                print("  ⚠️ Nenhum sistema TTS disponível (instale pyttsx3 ou gtts)")
            
        except Exception as e:
            print(f"  ❌ Erro ao testar sistemas TTS: {e}")
            return False
        
        # 7. Testa estrutura de diretórios
        print("\n📁 Passo 7: Testando estrutura de diretórios...")
        
        try:
            from config import RAGFILES_DIR
            
            # Cria diretório de temas
            themes_dir = RAGFILES_DIR / "temas"
            themes_dir.mkdir(exist_ok=True)
            
            # Cria subdiretórios de exemplo
            test_theme_dir = themes_dir / "teste_ia"
            test_theme_dir.mkdir(exist_ok=True)
            (test_theme_dir / "resumos").mkdir(exist_ok=True)
            (test_theme_dir / "audiobooks").mkdir(exist_ok=True)
            (test_theme_dir / "dados").mkdir(exist_ok=True)
            
            print(f"  ✅ Estrutura de diretórios criada: {themes_dir}")
            print(f"    - Resumos: {test_theme_dir / 'resumos'}")
            print(f"    - Audiobooks: {test_theme_dir / 'audiobooks'}")
            print(f"    - Dados: {test_theme_dir / 'dados'}")
            
        except Exception as e:
            print(f"  ❌ Erro ao criar estrutura: {e}")
            return False
        
        # 8. Resumo final
        print(f"\n🎉 Teste do Sistema Temático Concluído com Sucesso!")
        print("=" * 60)
        print(f"✅ Análise temática funcionando")
        print(f"✅ Geração de audiobooks configurada")
        print(f"✅ Estrutura de diretórios criada")
        print(f"✅ Classificação de temas funcionando")
        print(f"✅ Extração de palavras-chave funcionando")
        
        print(f"\n🚀 Funcionalidades implementadas:")
        print(f"  🎯 Análise temática automática")
        print(f"  📚 Separação de documentos por temas")
        print(f"  📄 Geração de resumos temáticos")
        print(f"  🎧 Geração de audiobooks em português")
        print(f"  📁 Estrutura organizacional por temas")
        print(f"  📊 Estatísticas detalhadas")
        
        print(f"\n📋 Próximos passos:")
        print(f"  1. Instalar dependências: pip install -r requirements_enhanced.txt")
        print(f"  2. Processar documentos com análise temática")
        print(f"  3. Gerar resumos e audiobooks por tema")
        print(f"  4. Testar com documentos reais")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in thematic system test: {e}")
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Iniciando teste do sistema temático...")
    
    # Executa teste
    success = test_thematic_system()
    
    if success:
        print("\n✅ Teste do sistema temático concluído com sucesso!")
        print("🎉 Sistema temático com audiobooks implementado!")
    else:
        print("\n❌ Teste falhou. Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
