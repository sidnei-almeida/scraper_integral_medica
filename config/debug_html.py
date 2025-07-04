#!/usr/bin/env python3
"""
Script para debugar o HTML da página e encontrar o botão "Ver mais produtos +"
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def debug_page():
    """
    Função para debugar a página e encontrar o botão
    """
    print("🔍 DEBUGANDO A PÁGINA...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Acessar página
        url = "https://www.integralmedica.com.br/todos-os-produtos"
        print(f"🌐 Acessando: {url}")
        driver.get(url)
        
        # Aguardar carregamento
        print("⏳ Aguardando carregamento...")
        time.sleep(5)
        
        # Ajustar zoom
        print("🔍 Ajustando zoom para 75%...")
        driver.execute_script("document.body.style.zoom='75%'")
        time.sleep(2)
        
        # Rolar até o final
        print("📄 Rolando até o final...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Obter HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Procurar por todos os elementos que contenham "Ver mais", "mais produtos" ou "+"
        print("\n🔍 PROCURANDO POR ELEMENTOS COM TEXTO RELACIONADO:")
        
        # Procurar por "Ver mais"
        elementos_ver_mais = soup.find_all(text=lambda text: text and "ver mais" in text.lower())
        print(f"\n📋 Elementos com 'ver mais': {len(elementos_ver_mais)}")
        for i, elem in enumerate(elementos_ver_mais):
            print(f"   {i+1}. '{elem.strip()}' - Tag pai: {elem.parent.name if elem.parent else 'None'}")
        
        # Procurar por "mais produtos"
        elementos_mais_produtos = soup.find_all(text=lambda text: text and "mais produtos" in text.lower())
        print(f"\n📋 Elementos com 'mais produtos': {len(elementos_mais_produtos)}")
        for i, elem in enumerate(elementos_mais_produtos):
            print(f"   {i+1}. '{elem.strip()}' - Tag pai: {elem.parent.name if elem.parent else 'None'}")
        
        # Procurar por "+"
        elementos_mais = soup.find_all(text=lambda text: text and "+" in text)
        print(f"\n📋 Elementos com '+': {len(elementos_mais)}")
        for i, elem in enumerate(elementos_mais[:10]):  # Limitar a 10 para não poluir
            print(f"   {i+1}. '{elem.strip()}' - Tag pai: {elem.parent.name if elem.parent else 'None'}")
        
        # Procurar especificamente por "Ver mais produtos"
        elementos_completos = soup.find_all(text=lambda text: text and "ver mais produtos" in text.lower())
        print(f"\n📋 Elementos com 'ver mais produtos': {len(elementos_completos)}")
        for i, elem in enumerate(elementos_completos):
            print(f"   {i+1}. '{elem.strip()}' - Tag pai: {elem.parent.name if elem.parent else 'None'}")
            # Mostrar HTML do elemento pai
            if elem.parent:
                print(f"      HTML pai: {elem.parent}")
        
        # Procurar links (a tags)
        print(f"\n🔗 PROCURANDO LINKS (A TAGS):")
        links = soup.find_all('a')
        links_interessantes = []
        for link in links:
            texto = link.get_text(strip=True).lower()
            if any(termo in texto for termo in ['ver mais', 'mais produtos', 'mostrar', 'carregar']):
                links_interessantes.append(link)
        
        print(f"📋 Links interessantes encontrados: {len(links_interessantes)}")
        for i, link in enumerate(links_interessantes):
            print(f"   {i+1}. Texto: '{link.get_text(strip=True)}'")
            print(f"      Href: {link.get('href', 'N/A')}")
            print(f"      Classes: {link.get('class', 'N/A')}")
            print(f"      HTML: {link}")
            print()
        
        # Procurar botões
        print(f"\n🔘 PROCURANDO BOTÕES:")
        botoes = soup.find_all('button')
        botoes_interessantes = []
        for botao in botoes:
            texto = botao.get_text(strip=True).lower()
            if any(termo in texto for termo in ['ver mais', 'mais produtos', 'mostrar', 'carregar']):
                botoes_interessantes.append(botao)
        
        print(f"📋 Botões interessantes encontrados: {len(botoes_interessantes)}")
        for i, botao in enumerate(botoes_interessantes):
            print(f"   {i+1}. Texto: '{botao.get_text(strip=True)}'")
            print(f"      Classes: {botao.get('class', 'N/A')}")
            print(f"      HTML: {botao}")
            print()
        
        # Salvar HTML para análise
        with open('debug_html.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("💾 HTML salvo em 'debug_html.html'")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        driver.quit()
        print("🔚 Driver fechado")

if __name__ == "__main__":
    debug_page() 