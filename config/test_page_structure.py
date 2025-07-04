#!/usr/bin/env python3
"""
Script de teste para analisar a estrutura da página da Integralmedica
antes de fazer o scraping completo.
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

def analyze_page_structure():
    """
    Analisa a estrutura da página de produtos da Integralmedica
    """
    url = "https://www.integralmedica.com.br/todos-os-produtos"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        print(f"🔍 Analisando estrutura da página: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Página carregada com sucesso!")
        print(f"📄 Tamanho da página: {len(response.content)} bytes")
        print(f"🏷️  Título: {soup.title.get_text() if soup.title else 'N/A'}")
        
        # Analisar elementos comuns de produtos
        print("\n🔍 Analisando elementos de produtos...")
        
        # Procurar por diferentes tipos de containers
        containers = []
        
        # Teste 1: Containers com class contendo "product"
        all_divs = soup.find_all(['div', 'article', 'li'])
        product_divs = [div for div in all_divs if div.get('class') and any('product' in str(cls).lower() for cls in div.get('class', []))]
        if product_divs:
            containers.append(('class contendo "product"', len(product_divs)))
        
        # Teste 2: Containers com class contendo "item"
        item_divs = [div for div in all_divs if div.get('class') and any('item' in str(cls).lower() for cls in div.get('class', []))]
        if item_divs:
            containers.append(('class contendo "item"', len(item_divs)))
        
        # Teste 3: Containers com data-product
        data_product_divs = soup.find_all(['div', 'article', 'li'], attrs={'data-product-id': True})
        if data_product_divs:
            containers.append(('data-product-id', len(data_product_divs)))
        
        # Teste 4: Links para produtos
        all_links = soup.find_all('a', href=True)
        product_links = [link for link in all_links if link.get('href') and any(term in link.get('href', '').lower() for term in ['produto', 'product', '/p/'])]
        if product_links:
            containers.append(('links para produtos', len(product_links)))
        
        # Mostrar resultados
        print("\n📊 Elementos encontrados:")
        for desc, count in containers:
            print(f"   • {desc}: {count} elementos")
        
        # Analisar estrutura de paginação
        print("\n🔍 Analisando paginação...")
        
        # Procurar por elementos de paginação
        pagination_by_class = [elem for elem in soup.find_all() if elem.get('class') and any('pagination' in str(cls).lower() for cls in elem.get('class', []))]
        paging_by_class = [elem for elem in soup.find_all() if elem.get('class') and any('paging' in str(cls).lower() for cls in elem.get('class', []))]
        page_by_class = [elem for elem in soup.find_all() if elem.get('class') and any('page' in str(cls).lower() for cls in elem.get('class', []))]
        
        page_links = [link for link in all_links if link.get('href') and 'page=' in link.get('href', '').lower()]
        p_links = [link for link in all_links if link.get('href') and 'p=' in link.get('href', '').lower()]
        
        pagination_elements = [
            ('class="pagination"', pagination_by_class),
            ('class="paging"', paging_by_class),
            ('class="page"', page_by_class),
            ('href com "page="', page_links),
            ('href com "p="', p_links)
        ]
        
        for desc, elements in pagination_elements:
            if elements:
                print(f"   • {desc}: {len(elements)} elementos")
        
        # Analisar primeiro produto encontrado
        print("\n🔍 Analisando primeiro produto encontrado...")
        
        # Tentar encontrar um produto para análise detalhada
        first_product = None
        
        if product_divs:
            first_product = product_divs[0]
        elif item_divs:
            first_product = item_divs[0]
        elif data_product_divs:
            first_product = data_product_divs[0]
        
        if first_product:
            print(f"   🏷️  HTML do primeiro produto:")
            print(f"   {str(first_product)[:500]}...")
            
            # Analisar elementos dentro do produto
            name_candidates = first_product.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if name_candidates:
                print(f"\n   📝 Possíveis nomes do produto:")
                for i, candidate in enumerate(name_candidates[:3]):
                    print(f"      {i+1}. {candidate.get_text(strip=True)}")
            
            price_candidates = [elem for elem in first_product.find_all(['span', 'div']) if elem.get('class') and any(term in str(cls).lower() for cls in elem.get('class', []) for term in ['price', 'preco', 'valor'])]
            if price_candidates:
                print(f"\n   💰 Possíveis preços:")
                for i, candidate in enumerate(price_candidates[:3]):
                    print(f"      {i+1}. {candidate.get_text(strip=True)}")
            
            link_candidates = first_product.find_all('a', href=True)
            if link_candidates:
                print(f"\n   🔗 Possíveis links:")
                for i, candidate in enumerate(link_candidates[:3]):
                    href = candidate.get('href')
                    full_url = urljoin(url, href) if href else None
                    print(f"      {i+1}. {full_url}")
            
            img_candidates = first_product.find_all('img')
            if img_candidates:
                print(f"\n   🖼️  Possíveis imagens:")
                for i, candidate in enumerate(img_candidates[:3]):
                    src = candidate.get('src') or candidate.get('data-src')
                    if src:
                        full_url = urljoin(url, src)
                        print(f"      {i+1}. {full_url}")
        
        # Salvar HTML para análise manual
        with open('page_structure.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"\n💾 HTML da página salvo em 'page_structure.html' para análise manual")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao analisar página: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 Iniciando análise da estrutura da página...")
    
    success = analyze_page_structure()
    
    if success:
        print("\n✅ Análise concluída com sucesso!")
        print("📋 Próximos passos:")
        print("   1. Revisar o arquivo 'page_structure.html' para entender melhor a estrutura")
        print("   2. Executar o scraper principal: python scraper_integral_medica.py")
    else:
        print("\n❌ Análise falhou. Verifique a conexão com a internet e tente novamente.")

if __name__ == "__main__":
    main() 