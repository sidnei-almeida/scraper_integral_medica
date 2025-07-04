#!/usr/bin/env python3
"""
Scraper para coletar URLs dos produtos da Integralmedica
Focado apenas na coleta de URLs com feedback visual
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
from datetime import datetime
import platform

# Importar webdriver-manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logging.warning("⚠️ webdriver-manager não encontrado. Usando ChromeDriver padrão.")

# Configuração do logging
dados_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(dados_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, 'coleta_urls.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class URLCollector:
    """
    Coletor de URLs focado apenas na coleta de URLs dos produtos
    """
    
    def __init__(self, headless: bool = False):
        self.base_url = "https://www.integralmedica.com.br"
        self.products_url = f"{self.base_url}/todos-os-produtos"
        self.headless = headless
        self.driver = None
        self.collected_urls = []
        
    def detect_browser_path(self):
        """Detecta automaticamente qual navegador está disponível no sistema"""
        system = platform.system().lower()
        
        if system == "linux":
            # No Linux, testar Chromium primeiro, depois Chrome
            paths = [
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser", 
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable"
            ]
        elif system == "windows":
            # No Windows, testar Chrome primeiro, depois Chromium
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Chromium\Application\chrome.exe",
                r"C:\Program Files (x86)\Chromium\Application\chrome.exe"
            ]
        elif system == "darwin":  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ]
        else:
            return None
        
        for path in paths:
            if os.path.exists(path):
                logging.info(f"🌐 Navegador encontrado: {path}")
                return path
        
        return None
    
    def setup_driver(self):
        """Configura o WebDriver Chrome com compatibilidade multiplataforma"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        try:
            # Primeira tentativa: detectar navegador automaticamente
            browser_path = self.detect_browser_path()
            if browser_path:
                chrome_options.binary_location = browser_path
                self.driver = webdriver.Chrome(options=chrome_options)
                logging.info("✅ WebDriver configurado com navegador detectado automaticamente")
                return True
            
            # Segunda tentativa: WebDriver Manager
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logging.info("✅ WebDriver configurado com WebDriver Manager")
                return True
            
            # Terceira tentativa: ChromeDriver padrão
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("✅ WebDriver configurado com ChromeDriver padrão")
            return True
                
        except Exception as e:
            logging.error(f"❌ Erro ao configurar WebDriver: {e}")
            return False
    
    def scroll_to_bottom(self):
        """
        Rola a página até o final para garantir que o botão apareça
        """
        print("📄 Rolando página até o final para carregar todo o conteúdo...")
        logging.info("Rolando página até o final")
        
        # Scroll em etapas para garantir que tudo carregue
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll até o final
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Aguardar carregamento
            time.sleep(2)
            
            # Verificar se a página cresceu
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        print("✅ Página rolada até o final")
        logging.info("Página rolada até o final")
    
    def find_load_more_button(self):
        """
        Encontra o botão/link "Ver mais produtos +" com múltiplas estratégias
        """
        # Estratégias para encontrar o botão "Mostrar mais" com as classes CSS exatas
        selectors = [
            # Botão com classes específicas do VTEX (informadas pelo usuário)
            "//button[contains(@class, 'vtex-button') and contains(@class, 'bg-action-primary') and contains(@class, 't-action--small')]",
            "//button[contains(@class, 'vtex-button') and contains(@class, 'bg-action-primary')]",
            "//button[contains(@class, 'vtex-button') and contains(@class, 't-action--small')]",
            
            # Texto exato "Mostrar mais" que foi encontrado
            "//button[contains(text(), 'Mostrar mais')]",
            "//div[contains(text(), 'Mostrar mais')]",
            "//span[contains(text(), 'Mostrar mais')]",
            "//*[contains(text(), 'Mostrar mais')]",
            
            # Botão com classe vtex-button (mais genérico)
            "//button[contains(@class, 'vtex-button')]",
            
            # Classes específicas do VTEX (uma por vez)
            "//button[contains(@class, 'bg-action-primary')]",
            "//button[contains(@class, 't-action--small')]",
            "//button[contains(@class, 'min-h-small')]",
            
            # Outras variações de texto
            "//button[contains(text(), 'Ver mais produtos +')]",
            "//button[contains(text(), 'Ver mais produtos')]",
            "//a[contains(text(), 'Ver mais produtos')]",
            "//div[contains(text(), 'Ver mais produtos')]",
            
            # Texto com variações
            "//*[contains(text(), 'Ver mais')]",
            "//*[contains(text(), 'mais produtos')]",
            "//*[contains(text(), 'Carregar mais')]",
            
            # Classes comuns
            "//a[contains(@class, 'load-more')]",
            "//button[contains(@class, 'load-more')]",
            "//a[contains(@class, 'ver-mais')]",
            "//button[contains(@class, 'ver-mais')]",
            "//a[contains(@class, 'show-more')]",
            "//button[contains(@class, 'show-more')]",
            
            # IDs comuns
            "//*[@id='load-more']",
            "//*[@id='ver-mais']",
            "//*[@id='show-more']",
            
            # Atributos específicos
            "//a[contains(@href, 'load-more')]",
            "//a[contains(@onclick, 'load')]",
            "//button[contains(@onclick, 'load')]",
        ]
        
        for i, selector in enumerate(selectors):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"🎯 Botão encontrado usando seletor {i+1}: {selector}")
                        logging.info(f"Botão encontrado usando seletor {i+1}: {selector}")
                        return element
            except Exception as e:
                continue
        
        return None
    
    def collect_all_urls(self):
        """
        Coleta todas as URLs dos produtos clicando no botão "Ver mais produtos"
        """
        if not self.driver:
            self.setup_driver()
        
        print(f"🌐 Acessando página: {self.products_url}")
        logging.info(f"Acessando página: {self.products_url}")
        
        self.driver.get(self.products_url)
        
        # Aguardar carregamento inicial
        print("⏳ Aguardando carregamento inicial da página...")
        time.sleep(3)
        
        # Ajustar zoom para 75% para ver o botão "Ver mais produtos"
        print("🔍 Ajustando zoom para 75% para visualizar o botão...")
        self.driver.execute_script("document.body.style.zoom='75%'")
        time.sleep(2)
        
        # Coletar URLs iniciais
        initial_urls = self.extract_current_urls()
        print(f"📦 URLs iniciais coletadas: {len(initial_urls)}")
        
        # Configurações para cliques
        max_clicks = 10  # Aumentei para 10 cliques
        clicks_realizados = 0
        
        print(f"🔄 Iniciando processo de carregamento: máximo {max_clicks} cliques")
        
        for tentativa in range(max_clicks):
            print(f"\n--- Tentativa {tentativa + 1}/{max_clicks} ---")
            
            # Rolar até o final da página
            self.scroll_to_bottom()
            
            # Procurar botão "Ver mais produtos"
            load_more_button = self.find_load_more_button()
            
            if not load_more_button:
                print("❌ Botão 'Ver mais produtos' não encontrado")
                logging.info(f"Botão não encontrado na tentativa {tentativa + 1}")
                if tentativa == 0:
                    print("⚠️  Pode ser que todos os produtos já estejam carregados")
                break
            
            # Scroll até o botão
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_button)
                time.sleep(2)
                
                # Tentar clicar
                clicked = False
                try:
                    load_more_button.click()
                    clicked = True
                    print(f"✅ Clique {tentativa + 1} realizado com sucesso")
                    logging.info(f"Clique {tentativa + 1} realizado com sucesso")
                except ElementClickInterceptedException:
                    # Tentar com JavaScript
                    try:
                        self.driver.execute_script("arguments[0].click();", load_more_button)
                        clicked = True
                        print(f"✅ Clique {tentativa + 1} realizado via JavaScript")
                        logging.info(f"Clique {tentativa + 1} realizado via JavaScript")
                    except Exception as e:
                        print(f"❌ Erro ao clicar: {e}")
                        logging.error(f"Erro ao clicar: {e}")
                
                if clicked:
                    clicks_realizados += 1
                    print("⏳ Aguardando carregamento de novos produtos...")
                    time.sleep(5)  # Aguardar carregamento
                    
                    # Verificar se novas URLs foram carregadas
                    current_urls = self.extract_current_urls()
                    print(f"📦 Total de URLs após clique: {len(current_urls)}")
                    
                    if len(current_urls) == len(self.collected_urls):
                        print("⚠️  Nenhuma nova URL foi carregada - pode ter chegado ao fim")
                        break
                    
                    self.collected_urls = current_urls
                else:
                    print("❌ Falha ao clicar no botão")
                    break
                    
            except Exception as e:
                print(f"❌ Erro na tentativa {tentativa + 1}: {e}")
                logging.error(f"Erro na tentativa {tentativa + 1}: {e}")
                break
        
        print(f"\n🎯 Processo concluído!")
        print(f"📊 Cliques realizados: {clicks_realizados}")
        print(f"🔗 Total de URLs coletadas: {len(self.collected_urls)}")
        
        return self.collected_urls
    
    def extract_current_urls(self):
        """
        Extrai URLs dos produtos da página atual
        """
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        product_urls = []
        
        # Estratégias para encontrar links dos produtos
        strategies = [
            # Links diretos para produtos
            lambda s: [link.get('href') for link in s.find_all('a', href=True) 
                      if link.get('href') and any(pattern in link.get('href', '').lower() 
                      for pattern in ['produto', 'product', '/p/', 'whey', 'creatina', 'barra'])],
            
            # Links em containers de produto
            lambda s: [link.get('href') for container in s.find_all(['div', 'article'], 
                      class_=re.compile(r'product|item|card', re.I)) 
                      for link in container.find_all('a', href=True)],
            
            # Links com texto que indica produto
            lambda s: [link.get('href') for link in s.find_all('a', href=True)
                      if link.get('href') and link.get_text(strip=True) and 
                      len(link.get_text(strip=True)) > 5]
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                urls = strategy(soup)
                for url in urls:
                    if url and url.startswith(('/', 'http')):
                        full_url = urljoin(self.base_url, url)
                        # Filtrar apenas URLs que realmente são de produtos (terminam com /p)
                        if (full_url not in product_urls and 
                            self.base_url in full_url and 
                            full_url.endswith('/p') and
                            not any(exclude in full_url.lower() for exclude in 
                                   ['categoria', 'blog', 'conta', 'carrinho', 'checkout', 'login'])):
                            product_urls.append(full_url)
                            
            except Exception as e:
                logging.error(f"Erro na estratégia {i+1}: {e}")
                continue
        
        return product_urls
    
    def save_urls_to_file(self, urls, filename=None):
        """
        Salva as URLs coletadas em um arquivo
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"urls_produtos_{timestamp}.txt"
        
        filepath = os.path.join(dados_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(f"{url}\n")
        
        print(f"💾 URLs salvas em: {filepath}")
        logging.info(f"URLs salvas em: {filepath}")
        
        return filepath
    
    def run(self):
        """
        Executa o processo completo de coleta de URLs
        """
        try:
            print("🚀 Iniciando coleta de URLs dos produtos...")
            
            # Coletar URLs
            urls = self.collect_all_urls()
            
            if urls:
                # Salvar URLs
                filepath = self.save_urls_to_file(urls)
                
                print(f"\n📋 Resumo da coleta:")
                print(f"   🔗 Total de URLs: {len(urls)}")
                print(f"   📁 Arquivo salvo: {filepath}")
                
                # Mostrar algumas URLs como exemplo
                print(f"\n🔍 Primeiras 5 URLs coletadas:")
                for i, url in enumerate(urls[:5]):
                    print(f"   {i+1}. {url}")
                
                if len(urls) > 5:
                    print(f"   ... e mais {len(urls) - 5} URLs")
                
                return urls
            else:
                print("❌ Nenhuma URL foi coletada")
                return []
                
        except Exception as e:
            print(f"❌ Erro durante a coleta: {e}")
            logging.error(f"Erro durante a coleta: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 WebDriver fechado")

def main():
    """
    Função principal
    """
    print("=" * 60)
    print("🔍 COLETOR DE URLs - INTEGRAL MÉDICA")
    print("=" * 60)
    
    collector = URLCollector(headless=False)  # Modo visual para debug
    urls = collector.run()
    
    print("\n" + "=" * 60)
    print("✅ COLETA FINALIZADA!")
    print("=" * 60)
    
    return urls

if __name__ == "__main__":
    main()