#!/usr/bin/env python3
"""
Scraper completo para dados nutricionais da Integralmedica
Inclui Selenium para carregar todos os produtos clicando em 'Ver mais produtos'
Configurado para 8 cliques máximos com 5 segundos entre cliques
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
from typing import List, Dict, Optional
import logging
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import os
import platform

# Configuração do logging (arquivo salvo na pasta logs/)
dados_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(dados_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, 'scraper_completo.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Importar webdriver-manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logging.warning("⚠️ webdriver-manager não encontrado. Usando ChromeDriver padrão.")

class CompleteNutritionalScraper:
    """
    Scraper completo para dados nutricionais da Integralmedica
    """
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://www.integralmedica.com.br"
        self.products_url = f"{self.base_url}/todos-os-produtos"
        self.headless = headless
        
        # Configurar requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Campos nutricionais que queremos extrair
        self.nutritional_fields = [
            'URL',
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
        
        self.driver = None
        
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
    
    def load_all_products(self) -> BeautifulSoup:
        """
        Carrega todos os produtos clicando no botão 'Ver mais produtos'
        Faz até 8 cliques com 5 segundos de espera entre cada clique
        """
        if not self.driver:
            self.setup_driver()
        
        logging.info(f"Acessando página: {self.products_url}")
        self.driver.get(self.products_url)
        
        # Aguardar carregamento inicial
        logging.info("Aguardando carregamento inicial da página...")
        time.sleep(5)
        
        # Configurações para cliques no botão "Ver mais produtos"
        max_clicks = 8  # Máximo de 8 cliques
        wait_between_clicks = 5  # 5 segundos entre cliques
        load_more_clicked = 0
        
        logging.info(f"Iniciando processo de carregamento: máximo {max_clicks} cliques, {wait_between_clicks}s entre cliques")
        
        for click_attempt in range(max_clicks):
            try:
                # Procurar pelo botão "Ver mais produtos"
                load_more_selectors = [
                    "//button[contains(text(), 'Ver mais produtos')]",
                    "//a[contains(text(), 'Ver mais produtos')]",
                    "//div[contains(text(), 'Ver mais produtos')]",
                    "//*[contains(text(), 'Ver mais produtos')]",
                    "//button[contains(@class, 'load-more')]",
                    "//button[contains(@class, 'ver-mais')]",
                    "//a[contains(@class, 'load-more')]"
                ]
                
                load_more_button = None
                for selector in load_more_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                load_more_button = element
                                break
                        if load_more_button:
                            break
                    except Exception:
                        continue
                
                if not load_more_button:
                    logging.info(f"Botão 'Ver mais produtos' não encontrado na tentativa {click_attempt + 1}")
                    if click_attempt == 0:
                        logging.warning("Botão não encontrado na primeira tentativa - pode ser que todos os produtos já estejam carregados")
                    break
                
                # Scroll até o botão para garantir que está visível
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_button)
                time.sleep(2)
                
                # Tentar clicar no botão
                clicked = False
                try:
                    load_more_button.click()
                    clicked = True
                    logging.info(f"✅ Clique {click_attempt + 1}/{max_clicks} realizado com sucesso")
                except ElementClickInterceptedException:
                    # Tentar clique com JavaScript se o clique normal falhar
                    try:
                        self.driver.execute_script("arguments[0].click();", load_more_button)
                        clicked = True
                        logging.info(f"✅ Clique {click_attempt + 1}/{max_clicks} realizado via JavaScript")
                    except Exception as e:
                        logging.warning(f"❌ Não foi possível clicar no botão na tentativa {click_attempt + 1}: {e}")
                
                if clicked:
                    load_more_clicked += 1
                    
                    # Aguardar carregamento dos novos produtos
                    logging.info(f"Aguardando {wait_between_clicks}s para carregamento dos novos produtos...")
                    time.sleep(wait_between_clicks)
                else:
                    logging.warning(f"Falha ao clicar na tentativa {click_attempt + 1}")
                    break
                
            except NoSuchElementException:
                logging.info(f"Botão 'Ver mais produtos' não encontrado na tentativa {click_attempt + 1}")
                break
            except Exception as e:
                logging.error(f"Erro inesperado na tentativa {click_attempt + 1}: {e}")
                break
        
        logging.info(f"🎯 Processo de carregamento concluído: {load_more_clicked} cliques realizados de {max_clicks} máximos")
        
        # Aguardar carregamento final
        logging.info("Aguardando carregamento final da página...")
        time.sleep(3)
        
        # Contar produtos carregados
        try:
            product_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'produto') or contains(@href, 'product')]")
            logging.info(f"📦 Total de elementos de produto encontrados: {len(product_elements)}")
        except Exception as e:
            logging.warning(f"Não foi possível contar produtos: {e}")
        
        # Obter HTML final da página
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        return soup
    
    def extract_product_urls(self, soup: BeautifulSoup) -> List[str]:
        """
        Extrai URLs dos produtos da página
        """
        product_urls = []
        
        # Estratégias para encontrar links dos produtos
        strategies = [
            # Estratégia 1: Links em containers com classe product
            lambda s: [link.get('href') for container in s.find_all(['div', 'article'], class_=re.compile(r'product', re.I)) 
                      for link in container.find_all('a', href=True)],
            
            # Estratégia 2: Links diretos para produtos
            lambda s: [link.get('href') for link in s.find_all('a', href=True) 
                      if link.get('href') and any(pattern in link.get('href', '').lower() for pattern in ['produto', 'product', '/p/'])],
            
            # Estratégia 3: Links em containers com item
            lambda s: [link.get('href') for container in s.find_all(['div', 'li'], class_=re.compile(r'item', re.I))
                      for link in container.find_all('a', href=True) if link.get('href')],
            
            # Estratégia 4: Links com texto de produto
            lambda s: [link.get('href') for link in s.find_all('a', href=True)
                      if link.get('href') and link.get_text(strip=True)]
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                urls = strategy(soup)
                valid_urls = []
                
                for url in urls:
                    if url:
                        # Filtrar apenas URLs que parecem ser de produtos
                        if any(pattern in url.lower() for pattern in ['produto', 'product', '/p/']):
                            full_url = urljoin(self.base_url, url)
                            if full_url not in valid_urls:
                                valid_urls.append(full_url)
                
                if valid_urls:
                    logging.info(f"Estratégia {i+1} encontrou {len(valid_urls)} URLs de produtos")
                    product_urls.extend(valid_urls)
                    
            except Exception as e:
                logging.error(f"Erro na estratégia {i+1}: {e}")
                continue
        
        # Remover duplicatas mantendo a ordem
        seen = set()
        unique_urls = []
        for url in product_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logging.info(f"🔗 Total de URLs únicas encontradas: {len(unique_urls)}")
        return unique_urls
    
    def get_page_content(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Obtém conteúdo HTML de uma página
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
                
            except requests.RequestException as e:
                logging.error(f"Erro na requisição para {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logging.error(f"Falhou após {max_retries} tentativas para {url}")
                    return None
    
    def extract_nutritional_data(self, soup: BeautifulSoup, product_url: str) -> Dict[str, str]:
        """
        Extrai dados nutricionais de uma página de produto
        """
        # Inicializar dados com valores padrão
        nutritional_data = {
            'URL': product_url,
            'PORÇÃO (g)': '0',
            'CALORIAS (kcal)': '0',
            'CARBOIDRATOS (g)': '0',
            'PROTEÍNAS (g)': '0',
            'GORDURAS_TOTAIS (g)': '0',
            'GORDURAS_SATURADAS (g)': '0',
            'FIBRAS (g)': '0',
            'AÇÚCARES (g)': '0',
            'SÓDIO (mg)': '0'
        }
        
        # Procurar tabela nutricional
        nutrition_selectors = [
            'table[class*="nutri"]',
            'table[class*="nutrition"]',
            'div[class*="nutri"]',
            'div[class*="nutrition"]',
            '.nutrition-table',
            '.tabela-nutricional',
            '.informacao-nutricional'
        ]
        
        nutrition_container = None
        for selector in nutrition_selectors:
            container = soup.select_one(selector)
            if container:
                nutrition_container = container
                break
        
        # Se não encontrou por seletores específicos, procurar por texto
        if not nutrition_container:
            text_indicators = ['informação nutricional', 'tabela nutricional', 'nutrition', 'nutricional']
            for indicator in text_indicators:
                elements = soup.find_all(text=re.compile(indicator, re.I))
                for element in elements:
                    parent = element.parent
                    for _ in range(5):  # Máximo 5 níveis acima
                        if parent and parent.name in ['table', 'div']:
                            nutrition_container = parent
                            break
                        parent = parent.parent if parent else None
                    if nutrition_container:
                        break
                if nutrition_container:
                    break
        
        if nutrition_container:
            self._parse_nutrition_table(nutrition_container, nutritional_data)
        else:
            logging.warning(f"Tabela nutricional não encontrada em {product_url}")
        
        return nutritional_data
    
    def _parse_nutrition_table(self, container: BeautifulSoup, data: Dict[str, str]):
        """
        Faz parsing da tabela nutricional
        """
        # Mapeamento de termos para campos
        field_mapping = {
            'porção': 'PORÇÃO (g)',
            'calorias': 'CALORIAS (kcal)',
            'valor energético': 'CALORIAS (kcal)',
            'carboidratos': 'CARBOIDRATOS (g)',
            'proteínas': 'PROTEÍNAS (g)',
            'gorduras totais': 'GORDURAS_TOTAIS (g)',
            'gorduras saturadas': 'GORDURAS_SATURADAS (g)',
            'fibras': 'FIBRAS (g)',
            'açúcares': 'AÇÚCARES (g)',
            'sódio': 'SÓDIO (mg)'
        }
        
        # Extrair todo o texto do container
        text = container.get_text()
        
        # Procurar por padrões de dados nutricionais
        for search_term, field_name in field_mapping.items():
            patterns = [
                rf'{re.escape(search_term)}[:\s]*(\d+(?:[,\.]\d+)?)',
                rf'{re.escape(search_term)}.*?(\d+(?:[,\.]\d+)?)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '.')
                    try:
                        float(value)
                        data[field_name] = value
                        logging.debug(f"Encontrado {field_name}: {value}")
                        break
                    except ValueError:
                        continue
        
        # Procurar especificamente por tabelas HTML
        if container.name == 'table':
            rows = container.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    for search_term, field_name in field_mapping.items():
                        if search_term in label:
                            number_match = re.search(r'(\d+(?:[,\.]\d+)?)', value)
                            if number_match:
                                number_value = number_match.group(1).replace(',', '.')
                                try:
                                    float(number_value)
                                    data[field_name] = number_value
                                    logging.debug(f"Encontrado {field_name}: {number_value}")
                                    break
                                except ValueError:
                                    continue
    
    def scrape_all_products(self) -> List[Dict[str, str]]:
        """
        Faz scraping de todos os produtos
        """
        logging.info("=== Iniciando coleta completa de produtos ===")
        
        try:
            # Carregar todos os produtos usando Selenium
            soup = self.load_all_products()
            
            # Extrair URLs dos produtos
            product_urls = self.extract_product_urls(soup)
            
            if not product_urls:
                logging.error("Nenhuma URL de produto encontrada")
                return []
            
            logging.info(f"📋 Processando {len(product_urls)} produtos encontrados")
            
            # Coletar dados nutricionais de cada produto
            all_nutritional_data = []
            
            for i, url in enumerate(product_urls, 1):
                logging.info(f"🔍 Produto {i}/{len(product_urls)}: {url}")
                
                # Delay entre requisições para ser respeitoso
                if i > 1:
                    time.sleep(2)
                
                product_soup = self.get_page_content(url)
                if product_soup:
                    nutritional_data = self.extract_nutritional_data(product_soup, url)
                    all_nutritional_data.append(nutritional_data)
                    
                    # Log do progresso
                    non_zero_fields = sum(1 for field in self.nutritional_fields[1:] if nutritional_data[field] != '0')
                    logging.info(f"📊 Produto {i} - {non_zero_fields}/{len(self.nutritional_fields)-1} campos nutricionais encontrados")
                else:
                    logging.error(f"❌ Não foi possível carregar produto {i}: {url}")
                    # Adicionar entrada vazia para manter consistência
                    empty_data = {field: '0' for field in self.nutritional_fields}
                    empty_data['URL'] = url
                    all_nutritional_data.append(empty_data)
            
            return all_nutritional_data
            
        finally:
            # Fechar driver
            if self.driver:
                self.driver.quit()
                logging.info("🔒 WebDriver fechado")
    
    def save_data(self, data: List[Dict[str, str]], base_filename: str = 'produtos_nutricional_completo'):
        """
        Salva dados em CSV e Excel usando pandas
        """
        if not data:
            logging.error("Nenhum dado para salvar")
            return
        
        # Criar DataFrame pandas
        try:
            df = pd.DataFrame(data)
            
            # Garantir que as colunas estejam na ordem correta
            df = df[self.nutritional_fields]
            
            # Converter campos numéricos para float (exceto URL)
            numeric_fields = [field for field in self.nutritional_fields if field != 'URL']
            for field in numeric_fields:
                df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
            
            # Adicionar timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{base_filename}_{timestamp}.csv"
            excel_filename = f"{base_filename}_{timestamp}.xlsx"
            
            # Salvar CSV
            self._save_to_csv(df, csv_filename)
            
            # Salvar Excel
            self._save_to_excel(df, excel_filename)
            
            # Estatísticas
            products_with_nutrition = len(df[df[numeric_fields].sum(axis=1) > 0])
            logging.info(f"📊 Total de produtos: {len(df)}")
            logging.info(f"📈 Produtos com dados nutricionais: {products_with_nutrition}/{len(df)}")
            
        except Exception as e:
            logging.error(f"Erro ao processar dados: {e}")
    
    def _save_to_csv(self, df: pd.DataFrame, filename: str):
        """
        Salva DataFrame em CSV na pasta dados/csv/
        """
        try:
            # Garantir que a pasta existe
            csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'csv')
            os.makedirs(csv_dir, exist_ok=True)
            filepath = os.path.join(csv_dir, filename)
            
            # Salvar CSV
            df.to_csv(filepath, index=False, encoding='utf-8')
            logging.info(f"💾 CSV salvo em: {filepath}")
            
        except Exception as e:
            logging.error(f"Erro ao salvar CSV: {e}")
    
    def _save_to_excel(self, df: pd.DataFrame, filename: str):
        """
        Salva DataFrame em Excel na pasta dados/excel/
        """
        try:
            # Garantir que a pasta existe
            excel_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'excel')
            os.makedirs(excel_dir, exist_ok=True)
            filepath = os.path.join(excel_dir, filename)
            
            # Salvar Excel com formatação
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Dados Nutricionais', index=False)
                
                # Obter worksheet para formatação
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
                
                # Formatação do cabeçalho
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    cell.fill = cell.fill.copy(start_color="CCCCCC")
            
            logging.info(f"📊 Excel salvo em: {filepath}")
            
        except Exception as e:
            logging.error(f"Erro ao salvar Excel: {e}")
    
    def run(self):
        """
        Executa o scraping completo
        """
        logging.info("=== 🚀 Iniciando Scraper Completo da Integralmedica ===")
        
        nutritional_data = self.scrape_all_products()
        
        if nutritional_data:
            self.save_data(nutritional_data)
            
            print(f"\n✅ Scraping concluído com sucesso!")
            print(f"📦 {len(nutritional_data)} produtos processados")
            print(f"💾 Dados salvos em:")
            print(f"   📄 CSV: dados/csv/")
            print(f"   📊 Excel: dados/excel/")
            
            # Estatísticas
            products_with_data = sum(1 for product in nutritional_data if any(product[field] != '0' for field in self.nutritional_fields[1:]))
            print(f"📈 {products_with_data} produtos com dados nutricionais")
            
            return nutritional_data
        else:
            print("\n❌ Nenhum dado foi coletado. Verifique os logs para mais detalhes.")
            return []

def main():
    """
    Função principal
    """
    # Configurações
    headless = True  # Mude para False se quiser ver o navegador funcionando
    
    print("🔧 Configurando scraper...")
    print("⚙️  Máximo de 8 cliques no botão 'Ver mais produtos'")
    print("⏱️  5 segundos de espera entre cliques")
    print("🤖 Modo headless:", "Sim" if headless else "Não")
    
    scraper = CompleteNutritionalScraper(headless=headless)
    results = scraper.run()
    
    if results:
        print("\n📋 Exemplo dos primeiros 3 produtos:")
        for i, product in enumerate(results[:3]):
            print(f"\n{i+1}. {product['URL']}")
            for field in scraper.nutritional_fields[1:]:
                if product[field] != '0':
                    print(f"   {field}: {product[field]}")

if __name__ == "__main__":
    main() 