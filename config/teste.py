#!/usr/bin/env python3
"""
Script de teste rápido para verificar se o projeto está funcionando
"""

import sys
import os

# Adicionar pasta config ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

def teste_rapido():
    """Testa se consegue importar e criar o scraper"""
    print("🧪 Testando importação dos módulos...")
    
    try:
        # Testar importações básicas
        import requests
        print("✅ requests importado com sucesso")
        
        import selenium
        print("✅ selenium importado com sucesso")
        
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 importado com sucesso")
        
        # Testar importação do scraper
        from scraper_completo import CompleteNutritionalScraper
        print("✅ scraper_completo importado com sucesso")
        
        # Testar criação do scraper
        scraper = CompleteNutritionalScraper(headless=True)
        print("✅ scraper criado com sucesso")
        
        print("\n🎉 Todos os testes passaram!")
        print("✅ O projeto está funcionando corretamente!")
        print("🚀 Você pode executar: python main.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("🔧 Execute: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    sucesso = teste_rapido()
    sys.exit(0 if sucesso else 1) 