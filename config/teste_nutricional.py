#!/usr/bin/env python3
"""
Script de teste para coleta de dados nutricionais de produtos individuais
URL de teste: https://www.integralmedica.com.br/whey-protein-concentrado-pouch-900g/p
"""

import requests
from bs4 import BeautifulSoup, Tag
import re
import json
from typing import Dict, Optional

class NutritionalDataExtractor:
    """
    Extrator de dados nutricionais de produtos individuais
    """
    
    def __init__(self):
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
        self.target_fields = {
            'URL': '',
            'NOME_PRODUTO': '',
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
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Obtém conteúdo da página
        """
        try:
            print(f"🔍 Acessando: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"✅ Página carregada com sucesso")
            return soup
            
        except requests.RequestException as e:
            print(f"❌ Erro ao acessar página: {e}")
            return None
    
    def extract_product_name(self, soup: BeautifulSoup) -> str:
        """
        Extrai o nome do produto
        """
        print("🔍 Procurando nome do produto...")
        
        # Estratégias para encontrar o nome do produto
        name_selectors = [
            'h1',  # Título principal
            'h2',  # Subtítulo
            '.product-name',
            '.product-title',
            '.nome-produto',
            '[class*="product"][class*="name"]',
            '[class*="product"][class*="title"]',
            'h1[class*="product"]',
            'h2[class*="product"]'
        ]
        
        for selector in name_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    if name and len(name) > 3:  # Nome válido
                        print(f"✅ Nome encontrado: {name}")
                        return name
            except Exception as e:
                print(f"⚠️  Erro no seletor {selector}: {e}")
                continue
        
        # Se não encontrou pelos seletores, procurar no título da página
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remover texto comum do título
            title = re.sub(r'\s*\|\s*.*$', '', title)  # Remove "| Integral Médica"
            if title and len(title) > 3:
                print(f"✅ Nome encontrado no título: {title}")
                return title
        
        print("❌ Nome do produto não encontrado")
        return "Produto não identificado"
    
    def extract_nutritional_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extrai dados nutricionais da tabela
        """
        print("🔍 Procurando tabela nutricional...")
        
        # Procurar seção da tabela nutricional
        nutrition_section = self.find_nutrition_section(soup)
        
        if not nutrition_section:
            print("❌ Seção nutricional não encontrada")
            return {}
        
        print("✅ Seção nutricional encontrada")
        
        # Extrair dados
        nutrition_data = {}
        
        # Procurar por tabela HTML
        table = nutrition_section.find('table')
        if table and isinstance(table, Tag):
            print("✅ Tabela HTML encontrada")
            nutrition_data = self.parse_html_table(table)
        else:
            print("⚠️  Tabela HTML não encontrada, tentando parsing de texto")
            nutrition_data = self.parse_nutrition_text(nutrition_section)
        
        return nutrition_data
    
    def find_nutrition_section(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """
        Encontra a seção da tabela nutricional
        """
        # Procurar por texto indicativo
        text_indicators = [
            'tabela nutricional',
            'informação nutricional',
            'nutrition',
            'nutricional'
        ]
        
        for indicator in text_indicators:
            # Procurar por elementos que contenham o texto
            elements = soup.find_all(string=re.compile(indicator, re.I))
            for element in elements:
                # Subir na árvore para encontrar o container
                parent = element.parent
                for _ in range(8):  # Até 8 níveis acima
                    if parent:
                        # Verificar se é uma seção relevante
                        if parent.name in ['div', 'section', 'article', 'table']:
                            # Verificar se contém dados nutricionais
                            text_content = parent.get_text().lower()
                            if any(term in text_content for term in ['calorias', 'proteínas', 'carboidratos', 'kcal']):
                                return parent
                        parent = parent.parent
                    else:
                        break
        
        return None
    
    def parse_html_table(self, table: Tag) -> Dict[str, str]:
        """
        Faz parsing de uma tabela HTML
        """
        data = {}
        
        # Mapeamento de termos para nossos campos (ordem importa - mais específico primeiro)
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
            'açúcares totais': 'AÇÚCARES (g)',  # Priorizar "açúcares totais" sobre "açúcares"
            'sódio': 'SÓDIO (mg)'
        }
        
        # Procurar por linhas da tabela
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Primeira coluna: nome do nutriente
                label = cells[0].get_text(strip=True).lower()
                # Segunda coluna: valor
                value = cells[1].get_text(strip=True)
                
                # Verificar se encontramos um campo que queremos
                for search_term, field_name in field_mapping.items():
                    if search_term in label:
                        # Extrair número
                        number = self.extract_number(value)
                        if number:
                            data[field_name] = number
                            print(f"✅ Encontrado {field_name}: {number}")
                            break
        
        return data
    
    def parse_nutrition_text(self, section: BeautifulSoup) -> Dict[str, str]:
        """
        Faz parsing do texto da seção nutricional
        """
        data = {}
        text = section.get_text()
        
        # Padrões para encontrar dados
        patterns = {
            'PORÇÃO (g)': [
                r'porção[:\s]*(\d+(?:[,\.]\d+)?)\s*g',
                r'(\d+(?:[,\.]\d+)?)\s*g.*(?:dosador|porção)'
            ],
            'CALORIAS (kcal)': [
                r'(?:valor energético|calorias)[:\s]*(\d+(?:[,\.]\d+)?)',
                r'(\d+(?:[,\.]\d+)?)\s*kcal'
            ],
            'CARBOIDRATOS (g)': [
                r'carboidratos[:\s]*(\d+(?:[,\.]\d+)?)',
            ],
            'PROTEÍNAS (g)': [
                r'proteínas[:\s]*(\d+(?:[,\.]\d+)?)',
            ],
            'GORDURAS_TOTAIS (g)': [
                r'gorduras totais[:\s]*(\d+(?:[,\.]\d+)?)',
            ],
            'GORDURAS_SATURADAS (g)': [
                r'gorduras saturadas[:\s]*(\d+(?:[,\.]\d+)?)',
            ],
            'FIBRAS (g)': [
                r'fibras[:\s]*(\d+(?:[,\.]\d+)?)',
            ],
            'AÇÚCARES (g)': [
                r'açúcares[:\s]*(\d+(?:[,\.]\d+)?)',
            ],
            'SÓDIO (mg)': [
                r'sódio[:\s]*(\d+(?:[,\.]\d+)?)',
            ]
        }
        
        for field_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '.')
                    data[field_name] = value
                    print(f"✅ Encontrado {field_name}: {value}")
                    break
        
        return data
    
    def extract_number(self, text: str) -> Optional[str]:
        """
        Extrai número de um texto
        """
        # Procurar por número (pode ter vírgula ou ponto decimal)
        match = re.search(r'(\d+(?:[,\.]\d+)?)', text)
        if match:
            return match.group(1).replace(',', '.')
        return None
    
    def extract_all_data(self, url: str) -> Dict[str, str]:
        """
        Extrai todos os dados de um produto
        """
        # Inicializar dados
        product_data = self.target_fields.copy()
        product_data['URL'] = url
        
        # Obter conteúdo da página
        soup = self.get_page_content(url)
        if not soup:
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
    
    def print_results(self, data: Dict[str, str]):
        """
        Imprime resultados formatados
        """
        print("\n" + "="*80)
        print("📊 DADOS COLETADOS")
        print("="*80)
        
        for field, value in data.items():
            if field == 'URL':
                print(f"🔗 {field}: {value}")
            elif field == 'NOME_PRODUTO':
                print(f"📦 {field}: {value}")
            else:
                print(f"📋 {field}: {value}")
        
        print("="*80)
        
        # Estatísticas
        non_zero_fields = sum(1 for field, value in data.items() 
                             if field not in ['URL', 'NOME_PRODUTO'] and value != '0')
        total_nutrition_fields = len(data) - 2  # Excluir URL e NOME_PRODUTO
        
        print(f"📈 Campos nutricionais encontrados: {non_zero_fields}/{total_nutrition_fields}")
        print(f"🎯 Taxa de sucesso: {(non_zero_fields/total_nutrition_fields)*100:.1f}%")
        print("="*80)

def main():
    """
    Função principal para teste
    """
    # URL de teste
    test_url = "https://www.integralmedica.com.br/whey-protein-concentrado-pouch-900g/p"
    
    print("🚀 TESTE DE COLETA DE DADOS NUTRICIONAIS")
    print("="*80)
    print(f"📋 URL de teste: {test_url}")
    print("="*80)
    
    # Criar extrator
    extractor = NutritionalDataExtractor()
    
    # Extrair dados
    product_data = extractor.extract_all_data(test_url)
    
    # Mostrar resultados
    extractor.print_results(product_data)
    
    # Salvar em JSON para análise
    with open('teste_produto.json', 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Dados salvos em: teste_produto.json")

if __name__ == "__main__":
    main() 