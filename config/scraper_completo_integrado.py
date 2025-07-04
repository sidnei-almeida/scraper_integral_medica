#!/usr/bin/env python3
"""
Script integrado para coletar URLs e dados nutricionais da Integral Médica
Combina coleta de URLs + extração de dados nutricionais + salvamento em CSV/XLSX
"""

import requests
from bs4 import BeautifulSoup, Tag
import re
import json
import pandas as pd
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from urllib.parse import urljoin
from typing import Dict, List, Optional
import os
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
os.makedirs(os.path.join(dados_dir, 'csv'), exist_ok=True)
os.makedirs(os.path.join(dados_dir, 'excel'), exist_ok=True)

log_file = os.path.join(logs_dir, 'scraper_integrado.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class IntegratedScraper:
    """
    Scraper integrado: coleta URLs + dados nutricionais
    """
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://www.integralmedica.com.br"
        self.products_url = f"{self.base_url}/todos-os-produtos"
        self.headless = headless
        self.driver = None
        
        # Configurar requests session para coleta de dados
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Campos que queremos extrair
        self.target_fields = [
            'URL',
            'NOME_PRODUTO',
            'PORÇÃO (g)',
            'CALORIAS (kcal)',
            'CARBOIDRATOS (g)',
            'PROTEÍNAS (g)',
            'GORDURAS_TOTAIS (g)',
            'GORDURAS_SATURADAS (g)',
            'FIBRAS (g)',
            'AÇÚCARES (g)',
            'SÓDIO (mg)'
        ]
    
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
    

    
    def find_and_click_button(self) -> bool:
        """Procura e clica no botão 'Mostrar mais' usando as estratégias que funcionam"""
        # Estratégias baseadas no coletar_urls.py que funciona
        selectors = [
            # Botão com classes específicas do VTEX (as que funcionam)
            "//button[contains(@class, 'vtex-button') and contains(@class, 'bg-action-primary') and contains(@class, 't-action--small')]",
            "//button[contains(@class, 'vtex-button') and contains(@class, 'bg-action-primary')]",
            "//button[contains(@class, 'vtex-button') and contains(@class, 't-action--small')]",
            
            # Texto exato "Mostrar mais"
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
        ]
        
        for i, selector in enumerate(selectors):
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        logging.info(f"🎯 Botão encontrado usando seletor {i+1}: {selector}")
                        
                        # Scroll até o botão
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(2)
                        
                        try:
                            # Tentar clicar normalmente
                            element.click()
                            return True
                        except ElementClickInterceptedException:
                            # Tentar com JavaScript
                            try:
                                self.driver.execute_script("arguments[0].click();", element)
                                return True
                            except Exception:
                                continue
                                
            except Exception:
                continue
        
        return False
    


    def scroll_to_bottom(self):
        """Rola a página até o final para garantir que o botão apareça (método que funciona)"""
        logging.info("📄 Rolando página até o final para carregar todo o conteúdo...")
        
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
        
        logging.info("✅ Página rolada até o final")

    def collect_urls(self) -> List[str]:
        """Coleta todas as URLs dos produtos usando o método que funciona"""
        logging.info("🔍 Iniciando coleta de URLs...")
        
        if not self.setup_driver():
            return []
        
        try:
            # Acessar página
            logging.info("📱 Acessando página principal...")
            self.driver.get(self.products_url)
            
            # Aguardar carregamento inicial
            logging.info("⏳ Aguardando carregamento inicial da página...")
            time.sleep(3)
            
            # Ajustar zoom para 75% (DEPOIS do carregamento inicial)
            logging.info("🔍 Ajustando zoom para 75%...")
            self.driver.execute_script("document.body.style.zoom='75%'")
            time.sleep(2)
            
            # Coletar URLs iniciais
            initial_urls = self.extract_product_urls(BeautifulSoup(self.driver.page_source, 'html.parser'))
            logging.info(f"📦 URLs iniciais coletadas: {len(initial_urls)}")
            
            # Configurações para cliques (seguindo o padrão que funciona)
            max_clicks = 10
            clicks_realizados = 0
            
            logging.info(f"🔄 Iniciando processo de carregamento: máximo {max_clicks} cliques")
            
            for tentativa in range(max_clicks):
                logging.info(f"--- Tentativa {tentativa + 1}/{max_clicks} ---")
                
                # Rolar até o final da página (método que funciona)
                self.scroll_to_bottom()
                
                # Procurar botão "Mostrar mais"
                button_found = self.find_and_click_button()
                
                if not button_found:
                    logging.info("❌ Botão 'Mostrar mais' não encontrado")
                    if tentativa == 0:
                        logging.info("⚠️ Pode ser que todos os produtos já estejam carregados")
                    break
                
                # Se encontrou e clicou no botão
                clicks_realizados += 1
                logging.info(f"✅ Clique {tentativa + 1} realizado com sucesso")
                
                # Aguardar carregamento (tempo que funciona)
                logging.info("⏳ Aguardando carregamento de novos produtos...")
                time.sleep(5)
                
                # Verificar se novas URLs foram carregadas
                current_urls = self.extract_product_urls(BeautifulSoup(self.driver.page_source, 'html.parser'))
                logging.info(f"📦 Total de URLs após clique: {len(current_urls)}")
                
                if len(current_urls) == len(initial_urls):
                    logging.info("⚠️ Nenhuma nova URL foi carregada - pode ter chegado ao fim")
                    break
                
                initial_urls = current_urls
            
            # Scroll final para garantir que chegamos no fim
            logging.info("📜 Scroll final para garantir carregamento completo...")
            self.scroll_to_bottom()
            time.sleep(3)
            
            # Extrair URLs finais
            logging.info("🔗 Extraindo URLs finais dos produtos...")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            urls = self.extract_product_urls(soup)
            
            logging.info(f"🎯 Processo concluído!")
            logging.info(f"📊 Cliques realizados: {clicks_realizados}")
            logging.info(f"🔗 Total de URLs coletadas: {len(urls)}")
            
            return urls
            
        except Exception as e:
            logging.error(f"❌ Erro na coleta de URLs: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
    
    def extract_product_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extrai URLs dos produtos da página"""
        product_urls = []
        
        # Procurar por todos os links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            if href:
                # Construir URL completa
                full_url = urljoin(self.base_url, href)
                
                # Filtrar apenas URLs de produtos que terminam com /p
                if full_url.endswith('/p'):
                    if full_url not in product_urls:
                        product_urls.append(full_url)
        
        return product_urls
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Obtém conteúdo da página"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"❌ Erro ao acessar {url}: {e}")
            return None
    
    def extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extrai o nome do produto"""
        name_selectors = ['h1', 'h2']
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                if name and len(name) > 3:
                    return name
        
        # Tentar título da página
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            title = re.sub(r'\s*\|\s*.*$', '', title)
            if title and len(title) > 3:
                return title
        
        return "Produto não identificado"
    
    def extract_nutritional_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrai dados nutricionais da tabela"""
        # Procurar por tabela nutricional
        table = soup.find('table')
        if table and isinstance(table, Tag):
            return self.parse_html_table(table)
        return {}
    
    def parse_html_table(self, table: Tag) -> Dict[str, str]:
        """Faz parsing de uma tabela HTML"""
        data = {}
        
        # Mapeamento de termos para nossos campos
        field_mapping = {
            'porção': 'PORÇÃO (g)',
            'valor energético': 'CALORIAS (kcal)',
            'calorias': 'CALORIAS (kcal)',
            'carboidratos': 'CARBOIDRATOS (g)',
            'proteínas': 'PROTEÍNAS (g)',
            'gorduras totais': 'GORDURAS_TOTAIS (g)',
            'gorduras saturadas': 'GORDURAS_SATURADAS (g)',
            'fibras alimentares': 'FIBRAS (g)',
            'fibras': 'FIBRAS (g)',
            'açúcares totais': 'AÇÚCARES (g)',
            'sódio': 'SÓDIO (mg)'
        }
        
        # Procurar por linhas da tabela
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                
                for search_term, field_name in field_mapping.items():
                    if search_term in label:
                        number = self.extract_number(value)
                        if number:
                            data[field_name] = number
                            break
        
        return data
    
    def extract_number(self, text: str) -> Optional[str]:
        """Extrai número de um texto"""
        match = re.search(r'(\d+(?:[,\.]\d+)?)', text)
        if match:
            return match.group(1).replace(',', '.')
        return None
    
    def extract_product_data(self, url: str) -> Dict[str, str]:
        """Extrai todos os dados de um produto"""
        # Inicializar dados
        product_data = {field: '0' if field not in ['URL', 'NOME_PRODUTO'] else '' for field in self.target_fields}
        product_data['URL'] = url
        
        # Obter conteúdo da página
        soup = self.get_page_content(url)
        if not soup:
            product_data['NOME_PRODUTO'] = 'Erro ao carregar página'
            return product_data
        
        # Extrair nome do produto
        product_name = self.extract_product_name(soup)
        product_data['NOME_PRODUTO'] = product_name
        
        # Extrair dados nutricionais
        nutrition_data = self.extract_nutritional_data(soup)
        
        # Atualizar dados com os valores encontrados
        for field, value in nutrition_data.items():
            if field in product_data:
                product_data[field] = value
        
        return product_data
    
    def save_data(self, data: List[Dict[str, str]]):
        """Salva dados em CSV e XLSX"""
        if not data:
            logging.error("❌ Nenhum dado para salvar")
            return
        
        # Criar DataFrame
        df = pd.DataFrame(data)
        
        # Garantir ordem das colunas
        df = df[self.target_fields]
        
        # Converter campos numéricos
        numeric_fields = [field for field in self.target_fields if field not in ['URL', 'NOME_PRODUTO']]
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
        
        # Salvar CSV
        csv_file = os.path.join(dados_dir, 'csv', 'dados.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8')
        logging.info(f"💾 CSV salvo em: {csv_file}")
        
        # Salvar XLSX
        xlsx_file = os.path.join(dados_dir, 'excel', 'dados.xlsx')
        with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados Nutricionais')
            
            # Formatação básica
            worksheet = writer.sheets['Dados Nutricionais']
            
            # Ajustar largura das colunas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logging.info(f"📊 XLSX salvo em: {xlsx_file}")
        
        # Estatísticas
        total_products = len(df)
        products_with_data = len(df[df[numeric_fields].sum(axis=1) > 0])
        
        logging.info(f"📈 Total de produtos: {total_products}")
        logging.info(f"📊 Produtos com dados nutricionais: {products_with_data}")
        logging.info(f"🎯 Taxa de sucesso: {(products_with_data/total_products)*100:.1f}%")
    
    def run(self):
        """Executa o scraper completo"""
        logging.info("🚀 Iniciando Scraper Integrado da Integral Médica")
        logging.info("=" * 60)
        
        # Passo 1: Coletar URLs
        urls = self.collect_urls()
        if not urls:
            logging.error("❌ Nenhuma URL coletada. Abortando.")
            return
        
        logging.info(f"📋 {len(urls)} URLs coletadas. Iniciando extração de dados...")
        
        # Passo 2: Extrair dados de cada produto
        all_data = []
        
        for i, url in enumerate(urls, 1):
            logging.info(f"📦 Processando produto {i}/{len(urls)}: {url}")
            
            product_data = self.extract_product_data(url)
            all_data.append(product_data)
            
            # Log do progresso
            nutrition_fields = [f for f in self.target_fields if f not in ['URL', 'NOME_PRODUTO']]
            found_fields = sum(1 for field in nutrition_fields if product_data[field] != '0')
            
            logging.info(f"   📊 {product_data['NOME_PRODUTO']}")
            logging.info(f"   📈 Dados nutricionais coletados: {found_fields}/{len(nutrition_fields)}")
            
            # Delay entre requisições para ser respeitoso
            if i < len(urls):
                time.sleep(2)
        
        # Passo 3: Salvar dados
        logging.info("💾 Salvando dados...")
        self.save_data(all_data)
        
        logging.info("✅ Scraper integrado concluído com sucesso!")
        logging.info("=" * 60)
        
        return all_data

def main():
    """Função principal"""
    print("🚀 SCRAPER INTEGRADO - INTEGRAL MÉDICA")
    print("=" * 60)
    print("📋 Este script irá:")
    print("   1️⃣ Coletar URLs de todos os produtos")
    print("   2️⃣ Extrair dados nutricionais de cada produto")
    print("   3️⃣ Salvar dados em CSV e XLSX")
    print("=" * 60)
    
    # Perguntar se quer ver o navegador
    print("🖥️  Deseja ver o navegador funcionando? (s/n): ", end="")
    resposta = input().strip().lower()
    headless = resposta not in ['s', 'sim', 'y', 'yes']
    
    if headless:
        print("🤖 Modo headless ativado")
    else:
        print("🖥️  Modo visual ativado")
    
    print("\n🚀 Iniciando scraper...")
    
    # Criar e executar scraper
    scraper = IntegratedScraper(headless=headless)
    results = scraper.run()
    
    if results:
        print(f"\n✅ Sucesso! {len(results)} produtos processados")
        print(f"📁 Arquivos salvos:")
        print(f"   📄 CSV: dados/csv/dados.csv")
        print(f"   📊 XLSX: dados/excel/dados.xlsx")
        print(f"   📋 Log: logs/scraper_integrado.log")
    else:
        print("\n❌ Nenhum dado foi coletado")

if __name__ == "__main__":
    main() 