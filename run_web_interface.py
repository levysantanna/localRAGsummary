#!/usr/bin/env python3
"""
Script para executar a interface web do sistema RAG
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependências faltando:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n💡 Instale com: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 Iniciando Interface Web do Sistema RAG Local")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar se o arquivo da interface existe
    interface_file = Path(__file__).parent / "web_interface.py"
    if not interface_file.exists():
        print("❌ Arquivo web_interface.py não encontrado!")
        sys.exit(1)
    
    print("✅ Dependências verificadas")
    print("🌐 Iniciando servidor web...")
    print("\n📱 A interface será aberta em: http://localhost:8501")
    print("🛑 Para parar o servidor, pressione Ctrl+C")
    print("=" * 50)
    
    try:
        # Executar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(interface_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
