#!/usr/bin/env python3
"""
Script de teste para coleta de URLs
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from coletar_urls import URLCollector

def main():
    print("🧪 TESTE - COLETOR DE URLs")
    print("=" * 50)
    
    # Criar coletor
    collector = URLCollector(headless=False)  # Modo visual para debug
    
    # Executar coleta
    urls = collector.run()
    
    if urls:
        print(f"\n✅ Sucesso! {len(urls)} URLs coletadas")
        
        # Salvar também em arquivo de teste
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file = f"teste_urls_{timestamp}.txt"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(f"{url}\n")
        
        print(f"📁 Arquivo de teste salvo: {test_file}")
    else:
        print("❌ Nenhuma URL foi coletada")
    
    return urls

if __name__ == "__main__":
    main() 