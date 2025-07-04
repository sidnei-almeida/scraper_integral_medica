#!/usr/bin/env python3
"""
Scraper específico para coletar dados nutricionais dos produtos da Integralmedica
Coleta apenas: URL, PORÇÃO, CALORIAS, CARBOIDRATOS, PROTEÍNAS, GORDURAS_TOTAIS, 
GORDURAS_SATURADAS, FIBRAS, AÇÚCARES, SÓDIO
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_nutricional.log'),
        logging.StreamHandler()
    ]
)

class NutritionalScraper:
    """
    Scraper específico para dados nutricionais da Integralmedica
    """
    
    def __init__(self):
        self.base_url = "https://www.integralmedica.com.br"
        self.products_url = f"{self.base_url}/todos-os-produtos"
        self.session = requests.Session()
        
        # Headers para simular um navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Campos que queremos extrair da tabela nutricional
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
        
    def get_page_content(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Obtém o conteúdo HTML de uma página
        """
        for attempt in range(max_retries):
            try:
                logging.info(f"Fazendo requisição para: {url} (Tentativa {attempt + 1})")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
                
            except requests.RequestException as e:
                logging.error(f"Erro na requisição para {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                else:
                    logging.error(f"Falhou após {max_retries} tentativas para {url}")
                    return None
    
    def extract_product_urls(self, soup: BeautifulSoup) -> List[str]:
        """
        Extrai URLs dos produtos da página de listagem
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
                      for link in container.find_all('a', href=True) if link.get('href')]
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
        
        logging.info(f"Total de URLs únicas encontradas: {len(unique_urls)}")
        return unique_urls
    
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
        
        # Estratégias para encontrar tabela nutricional
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
            # Procurar por texto que indica tabela nutricional
            text_indicators = ['informação nutricional', 'tabela nutricional', 'nutrition', 'nutricional']
            for indicator in text_indicators:
                elements = soup.find_all(text=re.compile(indicator, re.I))
                for element in elements:
                    parent = element.parent
                    # Subir na árvore até encontrar uma tabela ou container
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
            # Extrair dados da tabela nutricional
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
            # Padrões regex para encontrar valores
            patterns = [
                rf'{re.escape(search_term)}[:\s]*(\d+(?:[,\.]\d+)?)\s*[gk]?cal?',
                rf'{re.escape(search_term)}[:\s]*(\d+(?:[,\.]\d+)?)',
                rf'{re.escape(search_term)}.*?(\d+(?:[,\.]\d+)?)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '.')
                    try:
                        # Verificar se é um número válido
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
                            # Extrair número do valor
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
        Faz scraping de todos os produtos e extrai dados nutricionais
        """
        logging.info("Iniciando coleta de URLs dos produtos...")
        
        # Obter página principal
        soup = self.get_page_content(self.products_url)
        if not soup:
            logging.error("Não foi possível carregar a página principal")
            return []
        
        # Extrair URLs dos produtos
        product_urls = self.extract_product_urls(soup)
        
        if not product_urls:
            logging.error("Nenhuma URL de produto encontrada")
            return []
        
        logging.info(f"Encontradas {len(product_urls)} URLs de produtos")
        
        # Coletar dados nutricionais de cada produto
        all_nutritional_data = []
        
        for i, url in enumerate(product_urls, 1):
            logging.info(f"Processando produto {i}/{len(product_urls)}: {url}")
            
            # Delay entre requisições para ser respeitoso
            if i > 1:
                time.sleep(2)
            
            product_soup = self.get_page_content(url)
            if product_soup:
                nutritional_data = self.extract_nutritional_data(product_soup, url)
                all_nutritional_data.append(nutritional_data)
                
                # Log do progresso
                non_zero_fields = sum(1 for field in self.nutritional_fields[1:] if nutritional_data[field] != '0')
                logging.info(f"Produto {i} - {non_zero_fields}/{len(self.nutritional_fields)-1} campos nutricionais encontrados")
            else:
                logging.error(f"Não foi possível carregar produto {i}: {url}")
                # Adicionar entrada vazia para manter consistência
                empty_data = {field: '0' for field in self.nutritional_fields}
                empty_data['URL'] = url
                all_nutritional_data.append(empty_data)
        
        return all_nutritional_data
    
    def save_to_csv(self, data: List[Dict[str, str]], filename: str = 'produtos_nutricional.csv'):
        """
        Salva dados nutricionais em arquivo CSV
        """
        if not data:
            logging.error("Nenhum dado para salvar")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.nutritional_fields)
                writer.writeheader()
                writer.writerows(data)
            
            logging.info(f"Dados salvos em {filename}")
            logging.info(f"Total de produtos: {len(data)}")
            
            # Estatísticas
            products_with_nutrition = sum(1 for product in data if any(product[field] != '0' for field in self.nutritional_fields[1:]))
            logging.info(f"Produtos com dados nutricionais: {products_with_nutrition}/{len(data)}")
            
        except Exception as e:
            logging.error(f"Erro ao salvar CSV: {e}")
    
    def run(self):
        """
        Executa o scraping completo
        """
        logging.info("=== Iniciando Scraper Nutricional da Integralmedica ===")
        
        # Fazer scraping de todos os produtos
        nutritional_data = self.scrape_all_products()
        
        if nutritional_data:
            # Salvar em CSV
            self.save_to_csv(nutritional_data)
            
            print(f"\n✅ Scraping concluído com sucesso!")
            print(f"📦 {len(nutritional_data)} produtos processados")
            print(f"💾 Dados salvos em 'produtos_nutricional.csv'")
            
            # Mostrar estatísticas
            products_with_data = sum(1 for product in nutritional_data if any(product[field] != '0' for field in self.nutritional_fields[1:]))
            print(f"📊 {products_with_data} produtos com dados nutricionais")
            
            return nutritional_data
        else:
            print("\n❌ Nenhum dado foi coletado. Verifique os logs para mais detalhes.")
            return []

def main():
    """
    Função principal
    """
    scraper = NutritionalScraper()
    results = scraper.run()
    
    if results:
        print("\n📋 Primeiros 3 produtos como exemplo:")
        for i, product in enumerate(results[:3]):
            print(f"\n{i+1}. URL: {product['URL']}")
            for field in scraper.nutritional_fields[1:]:
                if product[field] != '0':
                    print(f"   {field}: {product[field]}")

if __name__ == "__main__":
    main() 