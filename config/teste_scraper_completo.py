#!/usr/bin/env python3
"""
Script de teste para validar o funcionamento do scraper completo
"""

import sys
import os
import logging

# Configurar logging para teste
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_scraper():
    """
    Testa o scraper completo
    """
    print("🧪 Iniciando teste do scraper completo...")
    
    try:
        # Importar o scraper
        from scraper_completo import CompleteNutritionalScraper
        
        # Configurar scraper para teste (não headless para ver funcionamento)
        scraper = CompleteNutritionalScraper(headless=False)
        
        print("✅ Scraper importado com sucesso")
        print("🔧 Configuração:")
        print("   - Máximo de 8 cliques no botão 'Ver mais produtos'")
        print("   - 5 segundos de espera entre cliques")
        print("   - Modo visual (headless=False) para acompanhar execução")
        
        # Executar apenas o carregamento de produtos (sem scraping completo)
        print("\n🚀 Iniciando teste de carregamento de produtos...")
        
        # Carregar produtos
        soup = scraper.load_all_products()
        
        # Extrair URLs
        product_urls = scraper.extract_product_urls(soup)
        
        print(f"\n📊 Resultados do teste:")
        print(f"   - URLs encontradas: {len(product_urls)}")
        print(f"   - Primeiras 5 URLs:")
        for i, url in enumerate(product_urls[:5]):
            print(f"     {i+1}. {url}")
        
        # Fechar driver
        if scraper.driver:
            scraper.driver.quit()
            print("🔒 WebDriver fechado")
        
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se todas as dependências estão instaladas")
        return False
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1) 