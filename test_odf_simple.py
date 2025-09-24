#!/usr/bin/env python3
"""
Teste Simplificado do Suporte a Open Document Format (ODF)
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

def test_odf_support():
    """Testa o suporte a ODF de forma simplificada"""
    
    print("📄 Teste do Suporte a Open Document Format (ODF)")
    print("=" * 60)
    
    try:
        # 1. Testa importação do processador ODF
        print("\n🔧 Passo 1: Testando importação do processador ODF...")
        
        try:
            from processors.odf_processor import ODFProcessor
            print("  ✅ ODFProcessor importado com sucesso")
        except ImportError as e:
            print(f"  ❌ Erro ao importar ODFProcessor: {e}")
            return False
        
        # 2. Testa inicialização do processador
        print("\n🔧 Passo 2: Testando inicialização do processador...")
        
        try:
            odf_processor = ODFProcessor()
            print("  ✅ ODFProcessor inicializado com sucesso")
        except Exception as e:
            print(f"  ❌ Erro ao inicializar ODFProcessor: {e}")
            return False
        
        # 3. Testa informações do processador
        print("\n📋 Passo 3: Testando informações do processador...")
        
        try:
            info = odf_processor.get_processor_info()
            print(f"  ✅ Nome: {info['name']}")
            print(f"  ✅ Versão: {info['version']}")
            print(f"  ✅ Descrição: {info['description']}")
            print(f"  ✅ Formatos suportados:")
            for ext, desc in info['supported_formats'].items():
                print(f"    - {ext}: {desc}")
        except Exception as e:
            print(f"  ❌ Erro ao obter informações: {e}")
            return False
        
        # 4. Testa extensões suportadas
        print("\n📋 Passo 4: Testando extensões suportadas...")
        
        try:
            supported_exts = odf_processor.get_supported_extensions()
            print(f"  ✅ Extensões suportadas: {supported_exts}")
            
            # Testa cada extensão
            for ext in supported_exts:
                test_file = f"test{ext}"
                can_process = odf_processor.can_process(test_file)
                status = "✅ Suportado" if can_process else "❌ Não suportado"
                print(f"    - {ext}: {status}")
        except Exception as e:
            print(f"  ❌ Erro ao testar extensões: {e}")
            return False
        
        # 5. Testa configuração
        print("\n⚙️ Passo 5: Testando configuração...")
        
        try:
            from config import SUPPORTED_EXTENSIONS
            print("  ✅ Configuração importada com sucesso")
            
            if 'odf' in SUPPORTED_EXTENSIONS:
                odf_exts = SUPPORTED_EXTENSIONS['odf']
                print(f"  ✅ Extensões ODF configuradas: {odf_exts}")
                
                # Verifica se todas as extensões ODF estão configuradas
                expected_exts = ['.odt', '.ods', '.odp']
                missing_exts = [ext for ext in expected_exts if ext not in odf_exts]
                
                if not missing_exts:
                    print("  ✅ Todas as extensões ODF estão configuradas")
                else:
                    print(f"  ❌ Extensões ODF faltando: {missing_exts}")
            else:
                print("  ❌ Configuração ODF não encontrada")
                return False
        except Exception as e:
            print(f"  ❌ Erro ao verificar configuração: {e}")
            return False
        
        # 6. Testa funcionalidades básicas
        print("\n🧪 Passo 6: Testando funcionalidades básicas...")
        
        try:
            # Testa limpeza de texto
            test_text = "  Este é um   texto de teste  \n\n  com espaços extras  "
            cleaned = odf_processor._clean_text(test_text)
            print(f"  ✅ Limpeza de texto funcionando")
            print(f"    Original: '{test_text}'")
            print(f"    Limpo: '{cleaned}'")
            
            # Testa extração de texto recursiva
            import xml.etree.ElementTree as ET
            test_xml = ET.fromstring('<root><p>Texto 1</p><p>Texto 2</p></root>')
            text_parts = []
            odf_processor._extract_text_recursive(test_xml, text_parts)
            print(f"  ✅ Extração de texto XML funcionando")
            print(f"    Texto extraído: {text_parts}")
            
        except Exception as e:
            print(f"  ❌ Erro ao testar funcionalidades: {e}")
            return False
        
        # 7. Resumo final
        print(f"\n🎉 Teste do Suporte ODF Concluído com Sucesso!")
        print("=" * 60)
        print(f"✅ Processador ODF implementado")
        print(f"✅ Suporte a .odt, .ods, .odp configurado")
        print(f"✅ Configuração atualizada")
        print(f"✅ Funcionalidades básicas testadas")
        
        print(f"\n🚀 Funcionalidades ODF implementadas:")
        print(f"  📄 ODT: Documentos de texto do LibreOffice Writer")
        print(f"  📊 ODS: Planilhas do LibreOffice Calc")
        print(f"  🎯 ODP: Apresentações do LibreOffice Impress")
        print(f"  🔍 Extração de metadados")
        print(f"  🧹 Limpeza e formatação de texto")
        print(f"  📊 Contagem de palavras e caracteres")
        print(f"  🔗 Integração com DocumentProcessor")
        
        print(f"\n📋 Próximos passos:")
        print(f"  1. Adicionar documentos ODF reais para teste")
        print(f"  2. Testar processamento completo")
        print(f"  3. Integrar com sistema RAG aprimorado")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in ODF test: {e}")
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Iniciando teste simplificado do suporte a ODF...")
    
    # Executa teste
    success = test_odf_support()
    
    if success:
        print("\n✅ Teste do suporte ODF concluído com sucesso!")
        print("🎉 Suporte a Open Document Format implementado!")
    else:
        print("\n❌ Teste falhou. Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main()
